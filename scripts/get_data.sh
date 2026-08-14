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
from PIL import Image

def is_multicolumn(png_path) -> bool:
    """Two text columns separated by a vertical whitespace gutter.

    Measured on the RENDERED PAGE, not on the PDF's text blocks: the page image is what
    every downstream stage actually sees, and src/doc_agent/vision/layout.py finds its
    columns the same way. Deriving this flag from the PDF instead would let the S1/S2
    strata disagree with the layout stage that has to act on them.
    """
    import numpy as np
    with Image.open(png_path) as im:
        a = np.asarray(im.convert("L"))
    if a.size == 0:
        return False
    h, w = a.shape
    ink = a < 128
    lo, hi = int(0.30 * w), int(0.70 * w)
    gw = max(6, int(0.012 * w))
    bh, st = int(0.20 * h), max(1, int(0.10 * h))

    # Scan horizontal bands rather than the whole page: a wide figure above two columns
    # closes the gutter in a whole-page projection and hides the columns underneath.
    text_bands = gutter_bands = 0
    for y in range(0, max(1, h - bh + 1), st):
        band = ink[y:y + bh]
        if band.sum() < 0.010 * bh * w:
            continue
        col = band.sum(axis=0).astype(np.float32)
        if col[:lo].sum() == 0 or col[hi:].sum() == 0:
            continue
        text_bands += 1
        thr = max(1.0, 0.02 * bh)
        run = best = 0
        for x in range(lo, hi):
            run = run + 1 if col[x] <= thr else 0
            best = max(best, run)
        gutter_bands += best >= gw
    # One band with a gap is a coincidence (a short line, an indented quote); a real
    # two-column page keeps the gutter open through most of its text.
    return bool(text_bands >= 2 and gutter_bands / text_bands >= 0.5)

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
            px_w, px_h = pix.width, pix.height
            rendered += 1
        else:
            # read the real size back: rounding the rect * zoom is off by a pixel on
            # some page sizes, and every rel_bbox -> pixel mapping depends on this
            with Image.open(png) as im:
                px_w, px_h = im.size
        text = page.get_text("text")
        manifest.append({
            "page_id":   f"{category}/{doc_id}/p{i:03d}",
            "doc_id":    doc_id,
            "doc_title": title,
            "category":  category,
            "page_no":   i,
            "n_pages_doc": d.page_count,
            "image_path": os.path.relpath(png, raw).replace("\\", "/"),
            "width":     px_w,
            "height":    px_h,
            "n_words":   len(re.findall(r"\S+", text)),
            "multicolumn": is_multicolumn(png),
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
    ev_pages = list(flatten([r["evidence_page"]]))
    boxes    = r.get("bbox") or []
    rboxes   = r.get("rel_bbox") or []
    stypes   = r.get("subimg_type") or []

    # One evidence entry per page, keeping each box aligned with its own type so
    # Stage 2 can emit a figure/table region rather than a shapeless page hint.
    evidence, pids = [], []
    for i, pg in enumerate(ev_pages):
        pid = by_doc_page.get((doc, int(pg)))
        if not pid:
            continue
        pids.append(pid)
        pb = boxes[i]  if i < len(boxes)  else []
        pr = rboxes[i] if i < len(rboxes) else []
        pt = stypes[i] if i < len(stypes) else []
        if pt and not isinstance(pt, list):
            pt = [pt]
        evidence.append({
            "page_id":   pid,
            "boxes":     [b for b in pb if isinstance(b, list) and len(b) == 4],
            "rel_boxes": [b for b in pr if isinstance(b, list) and len(b) == 4],
            "types":     list(pt),
        })
    if not pids:
        missing += 1
        continue

    types = set(flatten([stypes]))
    if types & {"image", "table"}:
        stratum = "S3"                                    # evidence inside a figure/table/equation
    elif any(mc.get(p, False) for p in pids):
        stratum = "S2"                                    # running text, multi-column page
    else:
        stratum = "S1"                                    # running text, single-column page
    qa.append({
        "query": r["query"], "answer": r["answer"], "doc_id": doc,
        "category": r.get("category"), "page_ids": pids,
        "evidence": evidence, "subimg_type": sorted(types), "stratum": stratum,
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
