#!/usr/bin/env bash
# A1 — fetch or recreate the scanned corpus into data/raw/
#
# Corpus: SciEGQA-Bench (80 arXiv papers, 1823 pages) at a PINNED revision.
# We redistribute nothing: this script rebuilds every page image locally from the
# source PDFs. See data/provenance.md for licence reasoning.
#
# Pages are rendered at 300 DPI at each page's NATIVE size, which reproduces the
# coordinate system the dataset's bbox annotations were authored against
# (verified: bbox == rel_bbox/1000 * page_px, e.g. 281 == 110.196/1000 * 2550).
#
# Idempotent: re-running skips work that is already done.
set -euo pipefail

REPO="Yuwh07/SciEGQA-Bench"
REV="9bdca77be633cc3259d7e3739d35b38ab00bf5d9"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW="$ROOT/data/raw"
DPI=300
SEED=42

export HF_HUB_DISABLE_SYMLINKS_WARNING=1
mkdir -p "$RAW"

echo "[get_data] corpus=$REPO revision=$REV dpi=$DPI"

python - "$REPO" "$REV" "$RAW" "$DPI" "$SEED" <<'PY'
import json, os, random, re, sys, tarfile, collections
from huggingface_hub import hf_hub_download

repo, rev, raw, dpi, seed = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
pdf_dir   = os.path.join(raw, "pdf")
pages_dir = os.path.join(raw, "pages")

# ---------------------------------------------------------------- 1. fetch
print("[1/5] downloading pinned files")
qa_path  = hf_hub_download(repo, "SciEGQA_Bench.jsonl", repo_type="dataset", revision=rev)
tar_path = hf_hub_download(repo, "PDF.tar",             repo_type="dataset", revision=rev)

# ---------------------------------------------------------------- 2. extract
if not os.path.isdir(pdf_dir):
    print("[2/5] extracting PDF.tar")
    os.makedirs(pdf_dir, exist_ok=True)
    with tarfile.open(tar_path) as t:
        t.extractall(pdf_dir)
else:
    print("[2/5] PDFs already extracted, skipping")

# PDFs are named "<arxiv_id>_<Title>.pdf" but qa.doc_name is the bare arXiv id,
# so key on the id and keep the title only as metadata.
pdfs = {}
for dirpath, _, names in os.walk(pdf_dir):
    for n in names:
        if n.lower().endswith(".pdf"):
            stem = os.path.splitext(n)[0]
            doc_id = stem.split("_", 1)[0]
            title = stem.split("_", 1)[1].replace("_", " ") if "_" in stem else ""
            pdfs[doc_id] = (os.path.join(dirpath, n), title)
print(f"      {len(pdfs)} PDFs")

# ---------------------------------------------------------------- 3. render
import pymupdf

def is_multicolumn(page) -> bool:
    """Two text bands separated by a gutter -> multi-column page."""
    W = page.rect.width
    blocks = [b for b in page.get_text("blocks") if b[4].strip()]
    narrow = [b for b in blocks if (b[2] - b[0]) < 0.6 * W]
    if len(narrow) < 6:
        return False
    left  = [b for b in narrow if (b[0] + b[2]) / 2 < 0.5 * W]
    right = [b for b in narrow if (b[0] + b[2]) / 2 >= 0.5 * W]
    return min(len(left), len(right)) >= 3 and min(len(left), len(right)) >= 0.25 * len(narrow)

print(f"[3/5] rendering pages at {dpi} DPI")
zoom = dpi / 72.0
manifest, done, rendered = [], 0, 0
for doc_id, (path, title) in sorted(pdfs.items()):
    category = os.path.basename(os.path.dirname(path))
    out_dir  = os.path.join(pages_dir, category, doc_id)
    os.makedirs(out_dir, exist_ok=True)
    d = pymupdf.open(path)
    for i, page in enumerate(d, start=1):
        png = os.path.join(out_dir, f"{doc_id}_p{i:03d}.png")
        if not os.path.exists(png):
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csGRAY)
            pix.save(png)
            rendered += 1
        text = page.get_text("text")
        manifest.append({
            "page_id":   f"{category}/{doc_id}/p{i:03d}",
            "doc_id":    doc_id,
            "doc_title": title,
            "category":  category,
            "page_no":   i,
            "n_pages_doc": d.page_count,
            "image_path": os.path.relpath(png, raw).replace("\\", "/"),
            "width":     int(page.rect.width  * zoom),
            "height":    int(page.rect.height * zoom),
            "n_words":   len(re.findall(r"\S+", text)),
            "multicolumn": is_multicolumn(page),
        })
    d.close()
    done += 1
    if done % 10 == 0:
        print(f"      {done}/{len(pdfs)} docs, {len(manifest)} pages")
print(f"      {rendered} newly rendered, {len(manifest)} pages total")

# ---------------------------------------------------------------- 4. QA + strata
print("[4/5] building qa.jsonl with S1/S2/S3 strata")
mc = {m["page_id"]: m["multicolumn"] for m in manifest}
by_doc_page = {(m["doc_id"], m["page_no"]): m["page_id"] for m in manifest}

def flatten(x):
    if isinstance(x, list):
        for i in x:
            yield from flatten(i)
    else:
        yield x

qa, missing = [], 0
for line in open(qa_path, encoding="utf-8"):
    r = json.loads(line)
    doc = r["doc_name"]
    pids = []
    for pg in flatten([r["evidence_page"]]):
        pid = by_doc_page.get((doc, int(pg)))
        if pid:
            pids.append(pid)
    if not pids:
        missing += 1
        continue
    types = set(flatten([r.get("subimg_type", [])]))
    if types & {"image", "table"}:
        stratum = "S3"                                    # evidence inside a figure/table/equation
    elif any(mc.get(p, False) for p in pids):
        stratum = "S2"                                    # running text, multi-column page
    else:
        stratum = "S1"                                    # running text, single-column page
    qa.append({
        "query": r["query"], "answer": r["answer"], "doc_id": doc,
        "category": r.get("category"), "page_ids": pids,
        "bbox": r.get("bbox"), "rel_bbox": r.get("rel_bbox"),
        "subimg_type": sorted(types), "stratum": stratum,
    })
print(f"      {len(qa)} QA items ({missing} dropped: evidence page not in corpus)")
print("      strata:", dict(collections.Counter(q['stratum'] for q in qa)))

# ---------------------------------------------------------------- 5. split by DOCUMENT
print("[5/5] splitting 70/15/15 by document, stratified by category")
rng = random.Random(seed)
bycat = collections.defaultdict(list)
for m in manifest:
    bycat[m["category"]].append(m["doc_id"])
splits = {}
for cat, docs in sorted(bycat.items()):
    uniq = sorted(set(docs)); rng.shuffle(uniq)
    n = len(uniq); n_tr = round(0.70 * n); n_va = round(0.15 * n)
    for d in uniq[:n_tr]:            splits[d] = "train"
    for d in uniq[n_tr:n_tr + n_va]: splits[d] = "val"
    for d in uniq[n_tr + n_va:]:     splits[d] = "test"
for m in manifest:
    m["split"] = splits[m["doc_id"]]
for q in qa:
    q["split"] = splits.get(q["doc_id"], "train")
print("      docs:", dict(collections.Counter(splits.values())))
print("      pages:", dict(collections.Counter(m["split"] for m in manifest)))

for name, rows in (("manifest.jsonl", manifest), ("qa.jsonl", qa)):
    with open(os.path.join(raw, name), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(os.path.join(raw, "splits.json"), "w", encoding="utf-8") as f:
    json.dump(splits, f, indent=2, sort_keys=True)

words = sum(m["n_words"] for m in manifest)
print(f"\n[get_data] DONE  pages={len(manifest)}  words={words}  docs={len(pdfs)}")
assert len(manifest) >= 300,  "corpus floor: >=300 pages"
assert words        >= 60000, "corpus floor: >=60000 words"
PY

echo "[get_data] corpus ready under data/raw/"
