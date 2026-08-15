# Per-stage design choices — PaperScholar (G19)

Stages 0–4 are built and filled here (A2). Stages 5–9 are declared at A3/A4.
Every number cited is measured; see `notebooks/eda.ipynb` and `notebooks/kb_demo.ipynb`.

| Stage | Problem statement | Data | Model | Methods | Design | Development | Deployment | MLOps |
|---|---|---|---|---|---|---|---|---|
| **0 Frame** | Answer a question from a scanned scientific page, grounded in that page. Pooled answer-F1 ≥ 0.70; robustness gate F1(S1)−F1(S3) ≤ 8 | SciEGQA-Bench, 80 docs / 1823 pages / 788k words | none | Three axes fixed in `task.yaml`; strata S1/S2/S3 derived from corpus annotations | `task.yaml` + `manifest.yaml` are the single source of the axes | axes asserted identical across task/manifest/form | n/a | corpus pinned to revision `9bdca77b` |
| **1 Ingest** | Turn 80 PDFs into 300-DPI pages whose coordinates still match the corpus's boxes | `PDF.tar` (132 MB) at pinned rev; splits 70/15/15 **by document** | none — deterministic ops only | Render 300 DPI native size, greyscale, NFKC + math punctuation; **no deskew/denoise/binarize** | `get_data.sh` emits `manifest/qa/splits`; `load_pages()` is the only reader | geometry assertion per page; floors + leakage in `validate.py` | offline batch, once per corpus revision | `snapshot()` hashes manifest+qa+splits → corpus version id |
| **2 Layout ▲E2** | Recover reading order and locate figure/table evidence | corpus `rel_bbox` + `subimg_type` as region labels | none learned — projection + morphology | Band-scan gutter detection → bands → left column, then right; annotated boxes spliced into the same order | `detect()` returns regions **in reading order**; that order is the contract | 8/8 agreement with eye-checked pages; overlays rendered | CPU, ~0.2 s/page | region provenance recorded in `REGION_META` |
| **3 OCR** | Read prose and figure/table regions into text | rendered pages + region crops (8 px padding) | **`facebook/nougat-base`** — reproduced published method (Blecher et al. 2023) | Full-page pass for prose; separate pass per figure/table crop; fp16; batch auto-sized to VRAM; repetition guard | Two paths for the two evidence kinds; `Chunk.id` encodes page + region | per-page resume cache; batched output verified identical to batch-1 | GPU batch; **4.5 h on a Kaggle T4 at batch 2** for 2,444 passes (1,823 pages + 621 region crops) | `ocr_cache.jsonl` keyed by page/region, 2,444 entries |
| **4 Index** | Make regions searchable without losing which box they came from | chunks from Stage 3, PII-scrubbed | `BAAI/bge-base-en-v1.5` (768-d) | Region-aware chunking, split on Nougat's Markdown headings, 256 tokens / 32 overlap; normalised vectors | FAISS `IndexFlatIP` + `chunks.jsonl` + `index_meta.json` in `data/index/` | `embed.dim` asserted against the model's real output | offline batch; index ships in the repo so the demo runs without a GPU | index tagged with model, chunk params, corpus counts |
| 5 Retrieval | A3 | | | | | | | |
| 6 Agent | A3 | | | | | | | |
| 7 RL/RLVR | bonus | | | | | | | |
| 8 Serving | A4 | | | | | | | |
| 9 Eval | A3/A4 | | | | | | | |

---

## Stage 0 — Frame

**Choice.** Domain: scientific literature triage. Data speciality: dense multi-column
layout. Primary NFR: robustness as a worst-stratum gap, `F1(S1) − F1(S3) ≤ 8`.

**Why it fits our corpus.** Measured, not assumed: 56.1% of the 1,623 QA pairs have
evidence annotated inside a figure or table, and 16.8% of pages are two-column. A
researcher cannot know in advance whether their question lands on prose or inside a
table, so a good average built from 0.85 on prose and 0.45 on figures fails them exactly
where the tool is meant to help.

**Cost.** Reporting per stratum means we cannot hide a weak stratum behind a good mean,
and the gate is falsifiable — shipping at 9 means we missed.

**What would change it.** If S3 had turned out to be the ~21% A1 estimated rather than
56%, the layout speciality would be a minority case and a pooled metric would be
defensible. It is the majority case, so it is not.

## Stage 1 — Ingest

**Choice.** Render each page at 300 DPI at its native size from the source PDFs; verify
rather than repair. Enhancement is **off**.

**Why it fits our corpus.** These are born-digital renders: 0.7% of pages have under 20
words, there is no skew, speckle or fading. Classical restoration on clean glyphs only
destroys them, and a VAE/diffusion enhancer would have nothing to learn from. We
verified the coordinate system rather than trusting it — the corpus's boxes satisfy
`bbox == rel_bbox/1000 × page_pixels` (281 == 110.196/1000 × 2550), which is why
rendering at 300 DPI reproduces the annotation frame exactly while downloading 132 MB
instead of the supplied 1.13 GB of images.

**Cost.** One extra validation pass, and a hard failure when a page's geometry disagrees
with the manifest. That assertion has already earned itself: it caught a one-pixel
truncation bug in our own manifest on A4-sized pages.

**What would change it.** A corpus of real scans rather than renders would flip
enhancement on and make `ingest/enhance.py` a graded gated stage instead of dead code.

## Stage 2 — Layout · data-speciality enhancement (E2)

**Choice.** Detect the column gutter by scanning horizontal bands, cut the page into
spanning and column bands, then order left column before right. Use the corpus's own
figure/table boxes as region labels and splice them into the same ordering.

**Why it fits our corpus.** Reading order is the speciality, so an unordered pile of
boxes would be useless. Two design decisions were forced by measurement:

- *Projection, not morphology, for the gutter.* The column gap is ~12 px at working
  resolution — narrower than the morphological kernel needed to join words into lines.
  Any purely morphological pass bridges the gutter and welds the two columns into one
  block, which is precisely the failure this stage exists to prevent.
- *Bands, not a whole-page projection.* A wide figure above two columns closes the
  gutter in a full-page projection and hides the columns underneath. Scanning bands
  finds them; requiring the gutter to persist across most text bands stops an indented
  block quote from faking one.

**Cost.** Two full passes over every page image (~0.2 s/page, CPU) and a heuristic we
must defend rather than a citation we can point at.

**What would change it.** A learned detector (DocLayout-YOLO, PP-DocLayout) if pages
without annotations turned out to need better recall than the morphological pass gives —
we would then be comparing against a measured baseline rather than adopting on faith.

**Honest limit.** Validated by eye on 8 pages (8/8 agreement between the manifest flag
and the layout stage). That is a small sample; it is a sanity check, not an evaluation.

## Stage 3 — OCR · reproduced published method

**Choice.** `facebook/nougat-base` (Blecher et al., 2023, arXiv:2308.13418) via HF
`transformers`, **not** the unmaintained `nougat-ocr` package. Pretrained, not
fine-tuned.

**Why it fits our corpus.** Nougat was trained on arXiv page images, which is literally
what this corpus is. It emits Markdown with LaTeX for mathematics and resolves
multi-column reading order internally — the two properties our speciality turns on. A
line-level recogniser like TrOCR would need Stage 2 to feed it correctly ordered lines
and would still lose every displayed equation; Tesseract would lose both.

**Cost.** It is a generative decoder, so it is slow (~95 s/page unbatched on CPU) and it
can fall into repetition loops on dense tables — a documented failure mode we guard
explicitly and count rather than hide. We do not fine-tune: with no page-level
transcription labels beyond our own 18-page oracle, fine-tuning would overfit the
oracle we score against.

**What would change it.** Enough labelled pages to fine-tune honestly (a separate
training split, not the held-out set), or a corpus whose notation Nougat was not
trained on.

## Stage 4 — Index

**Choice.** Region-aware chunks split on Nougat's Markdown headings, 256 tokens with 32
overlap, embedded with `BAAI/bge-base-en-v1.5` (768-d, normalised) into a FAISS
`IndexFlatIP`.

**Why it fits our corpus.** A chunk never spans two layout regions: fixed-size windows
over a flattened page would re-mix the columns Stage 2 just separated and glue table
cells onto neighbouring prose. Keeping the region boundary is what lets a retrieved
chunk be traced back to one box on one page, which A3's grounding gate needs. Nougat
emits headings, so section boundaries are free and strictly better cut points than a
blind window. **Flat, not HNSW**: at this corpus size an approximate index trades recall
for a speedup we do not need, and recall is what the NFR is about — flat is exact.

**Cost.** bge-**base** rather than the bge-large named in A1: 4× smaller and faster, at
a small retrieval cost we accept because the index must ship inside the repo so the demo
notebook runs for a grader without a GPU. Flat search is O(n) per query, which is fine
at ~10⁴ vectors and would not be at 10⁷.

**What would change it.** A corpus one or two orders of magnitude larger would force
HNSW or IVF-PQ and make `optional/stream_ingest.py` real; a multilingual corpus would
force a multilingual embedder.

---

## The cross-cutting decision: PII

Wired at `hooks.AFTER_OCR`, between reading and indexing — the last point where text
exists but is not yet searchable. Author blocks, emails and ORCIDs are redacted, and a
chunk that is mostly personal identifiers is dropped before embedding, so questions
about people rather than content retrieve nothing and the agent abstains. We do not
alter the stored page images: this is public scholarly attribution, and the goal is to
keep it out of the agent's reach, not to erase it.

**Known limit.** A title line that carries the author's name alongside the title is
kept, because dropping titles would cost real retrieval quality. Identifier redaction
still applies to it.

---

## What the build actually produced (A2 results)

Measured in `notebooks/kb_demo.ipynb`; every figure in the A2 form comes from there.

| | |
|---|---|
| Corpus | 80 documents · 1,823 pages · 788,265 words |
| OCR | 2,444 Nougat passes (1,823 pages + 621 region crops), 4.5 h on a Kaggle T4 |
| Index | **5,240 chunks** (644 of them figure/table transcriptions) · 768-d · FAISS flat · 15.4 MB |
| Coverage | 1,818 / 1,823 pages (99.7%), all 80 documents |
| OCR quality | **token-F1 0.866**, CER 0.300 on 18 held-out pages — S1 0.763 · S2 0.892 · S3 0.943 |
| Retrieval | R@1 0.353 · R@5 0.600 · R@10 0.667 over 150 sampled queries |

Three results worth carrying into A3, none of them predicted in A1:

**The region path is what answers figure questions.** On a 5-question S3 spot check every
single top hit was a `#r*:figure` or `#r*:table` chunk, not page prose. Stage 2 → Stage 3's
crop-and-reread path is doing the work our data speciality said it would.

**Reading is hardest on mathematics, not on columns.** S3 reads *best* (0.943) and S1
worst (0.763) — the opposite of A1's expectation. The S1 figure is dragged down almost
entirely by one page where Nougat fell into a repetition loop; the difficulty is dense
notation, not column count. Multi-column reading order is effectively solved by Nougat.

**`weak_threshold` is mis-calibrated and would break the A3 gate.** Across 150 queries the
top-1 similarity ranged 0.494–0.812 (mean 0.664); *none* fell below the configured 0.35, so
evidence-gated re-search would never fire. And failed retrievals (0.494–0.741, median
0.623) overlap the successful ones almost completely, so no absolute cut separates them.
A3 must use a relative criterion — top-1 vs top-k margin, or the post-rerank score.

## Known limits, stated rather than buried

- The OCR oracle is **machine-extracted from the PDF text layer and human-reviewed**, not
  hand-typed. Strong for prose; the maths required repairing truncated codepoints, and
  table *structure* is not represented, so we score table content and not table layout.
- Greek letters and math operators are excluded from the character metric because LaTeX
  spells them as words and the PDF as glyphs. Math *variables* are scored.
- The PII gate removed 5 pages (0.27%) from the index, costing 4 papers' titles.
- The shipped index was built with the tail-based repetition guard; the stronger
  whole-page guard landed afterwards and applies on cache reload, so any rebuild picks
  it up. About 1% of pages triggered the guard during the build.
