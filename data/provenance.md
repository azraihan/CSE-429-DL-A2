# Corpus provenance (PaperScholar — G19)

All figures below are **measured** by `scripts/get_data.sh` and reproduced in
`notebooks/eda.ipynb`. Nothing here is estimated.

## Source

- **Corpus:** SciEGQA-Bench — scientific document QA with semantic evidence grounding
- **Source (URL):** https://huggingface.co/datasets/Yuwh07/SciEGQA-Bench
- **Pinned revision:** `9bdca77be633cc3259d7e3739d35b38ab00bf5d9`
- **Retrieved:** 2026-08-15
- **Upstream paper:** arXiv:2511.15090
- **Related split (not used in A2):** `Yuwh07/SciEGQA-Train`, revision
  `4ffb867c88e3264161920b4b2446d5ac6352269e` — 30,780 QA rows over 3,494 documents,
  77.1 GB. Excluded deliberately: every one of its 30,780 rows carries
  `subimg_type == "image"`, so the text/table/figure distinction our primary NFR is
  defined on **cannot be constructed from it**. Only the Bench split labels evidence
  by type.

## Licence / usage rights

**Link-only. We redistribute no page images and no extracted text.**

The HuggingFace dataset card sets **no `license` field**, and the underlying pages are
renders of arXiv PDFs whose licences vary per submission — from CC-BY to arXiv's
default non-exclusive distribution licence, which does not grant redistribution rights
over derivatives. We therefore treat the corpus as link-only:

- `scripts/get_data.sh` fetches `PDF.tar` + `SciEGQA_Bench.jsonl` from the pinned
  revision at build time and re-renders every page locally.
- `data/raw/` is gitignored; no page image is committed.
- The only images in the repository are the 18 pages under
  `grading_kit/heldout_pages/`, committed as required grading evidence.
- Every page traces to its arXiv id via `doc_id`, so any individual licence can be
  audited back to its source.

## Size

| Measure | Value |
|---|---|
| Documents | **80** arXiv papers (10 in each of 8 categories) |
| Pages | **1,823** — floor is 300 ✓ |
| Words (PDF text layer) | **788,265** — floor is 60,000 ✓ |
| Mean / median words per page | 432 / 419 |
| Rendered size on disk | **0.58 GB** (300 DPI, 8-bit greyscale PNG) |
| Download size | 132 MB (`PDF.tar`) + 0.7 MB (`SciEGQA_Bench.jsonl`) |
| QA pairs | **1,623** with annotated evidence regions |
| Distinct evidence pages | 837 |

We fetch `PDF.tar` (132 MB) and render pages ourselves rather than pulling the
supplied `Images.tar` (1.13 GB). Verified equivalent: the dataset's boxes satisfy
`bbox == rel_bbox / 1000 × page_pixels` (e.g. `281 == 110.196/1000 × 2550`), so the
annotations were authored against pages rendered at **300 DPI at native page size**.
Re-rendering at 300 DPI reproduces that coordinate system exactly while cutting the
download by 8.5× and giving us the PDF text layer for ground truth.

## Scan / script difficulty notes

These are **born-digital renders, not degraded scans** — there is no speckle, skew, or
fading, and therefore no restoration stage (`enhance.enabled: false`). The difficulty is
**layout**, which is what our data speciality claims:

- **42.5%** of pages (774/1,823) are multi-column, where reading order ≠ visual order.
- **56.1%** of QA pairs have their evidence inside a **figure or table region**, not in
  running prose (stratum S3 below). This is the single most important property of the
  corpus and the reason Stage 2 Layout is load-bearing rather than incidental.
- Mixed page geometry: 1,308 US-Letter (612×792 pt), 397 A4 (595×842 pt), 69 at
  486×720 pt, plus 5 landscape pages. Absolute pixel boxes are therefore **not**
  portable across pages; all coordinate handling uses the normalised `rel_bbox`.
- Dense mathematics: displayed equations and multi-row tables with spanning cells.
- Only 0.7% of pages (13/1,823) carry fewer than 20 words.

## Evidence strata (the primary NFR is defined on these)

Derived in `get_data.sh` from the corpus's own `subimg_type` annotation plus a
column-detection pass over the PDF text blocks:

| Stratum | Definition | QA pairs | Share |
|---|---|---|---|
| S1 | evidence in running text, single-column page | 336 | 20.7% |
| S2 | evidence in running text, multi-column page | 376 | 23.2% |
| S3 | evidence inside a figure, table, or displayed equation | 911 | 56.1% |

## Split policy (by document)

Split **by `doc_id`, never by page**, stratified by category, seeded (`seed: 42`) and
reproducible from `scripts/get_data.sh`. Written to `data/raw/splits.json`.

| Split | Documents | Pages | QA pairs |
|---|---|---|---|
| train | 56 | 1,375 | 1,122 |
| val | 16 | 331 | 337 |
| test | 8 | 117 | 164 |

**Leakage check.** The single most likely leak is the same paper appearing in two
splits. Because a split is assigned to a `doc_id` and every page and QA row inherits it,
that leak is structurally impossible rather than merely absent. It is asserted in
`src/doc_agent/data/validate.py`, which fails the build if any `doc_id` resolves to more
than one split, and if the corpus falls below 300 pages or 60,000 words.

## Correction to A1

A1 reported corpus statistics that we have since measured and found wrong; the A1
numbers were estimates presented as measurements. Corrected here and in
`notebooks/eda.ipynb`. **The three A1 choices — domain, data speciality, and the
robustness NFR with its `F1(S1) − F1(S3) ≤ 8` target — are unchanged, as is the
`pooled answer-F1 ≥ 0.70` success metric.**

| A1 stated | Measured |
|---|---|
| 51.8k pages, ~60 GB | 1,823 pages, 0.58 GB rendered (Bench split) |
| ~150 words per page | 432 mean, 419 median |
| cs ≈ 61% of documents | exactly 12.5% per category (10 docs × 8) |
| ~18,400 QA pairs | 1,623 (Bench) / 30,780 (Train) |
| S1 45% / S2 34% / S3 21% | S1 20.7% / S2 23.2% / **S3 56.1%** |
| ~12% of pages near-zero text | 0.7% (13 pages) |
| Licence "MIT" (§2) | link-only, as A1 §4 itself already argued |

Two of these strengthen the project rather than weakening it: the corpus is **perfectly
balanced across categories**, so A1's stated worry about a cs skew biasing our headline
F1 does not arise; and evidence sits in figure/table regions in **56% of questions
rather than 21%**, making the layout speciality the dominant property of the corpus
instead of a minority case.
