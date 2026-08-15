# Held-out pages (PaperScholar — G19)

18 page-images set aside as the OCR oracle. Ground-truth transcriptions are in
`../labels.jsonl`, one JSON object per page keyed by `page_id`.

## How these were chosen

- Drawn **only from `test`-split documents** (`data/raw/splits.json`). Splits are
  assigned per `doc_id`, so no held-out page's document appears in train or val.
- **6 pages per evidence stratum**, so OCR quality can be reported per stratum rather
  than pooled — the same S1/S2/S3 breakdown our primary NFR is defined on:
  - **S1** — evidence in running text, single-column page
  - **S2** — evidence in running text, multi-column page
  - **S3** — evidence inside a figure, table, or displayed equation
- 9 of the 18 are multi-column; 7 documents across 6 arXiv categories are represented.
- These pages are never used to tune or fine-tune the reader.

## How the ground truth was produced

These are born-digital renders, so the source PDF's text layer is authoritative for
characters. Four things were **not** taken on trust:

1. **Reading order.** PyMuPDF's default block order interleaves the two columns of a
   multi-column page — exactly the failure this project exists to fix. Transcriptions
   are extracted column-aware instead: full-width blocks above the columns first, then
   the left column top-to-bottom, then the right.
2. **Figure internals.** A figure's axis labels and legend fragments appear in the text
   layer as scattered tokens. Nougat emits a figure's *caption*, not its internals, so
   scoring against them would penalise the reader for a task it is not performing.
3. **Mathematical notation.** This corpus's LaTeX math fonts map glyphs to Mathematical
   Alphanumeric Symbols (U+1D400–1D7FF), but the PDFs' ToUnicode values are **truncated
   to 16 bits**, dropping every math italic into the Hangul Syllables block — the oracle
   initially appeared to be written in Korean. Verified across all 27 distinct affected
   characters (529 occurrences): each lands exactly on its intended symbol at +0x10000.
   The extractor repairs this, and NFKC then folds a math italic *n* to plain `n`, which
   is directly comparable with the `\(n\)` the reader emits. Without the repair, three
   maths pages scored 0.42–0.79 token-F1 purely as an artefact of the broken oracle.
4. **Table structure.** The raw text layer emits a table's cells as loose blocks with no
   row structure, so a column of numbers can arrive before its row labels. Tables are
   detected and extracted as a grid, then linearised row by row, which matches the order
   both a human and the reader produce. 7 of the 18 pages contain such a table.

Each record therefore carries two transcriptions:

| Field | Contents | Use |
|---|---|---|
| `text` | prose + captions, in true reading order, figure internals removed | **the headline OCR oracle** |
| `text_full` | everything on the page, figure internals included | disclosed alongside, so the exclusion is auditable |

Figure internals are 3.6% of words overall (309 of 8,571), concentrated in 5 pages —
the worst single page is 15%. Both numbers are reported in `notebooks/kb_demo.ipynb`.

Totals: 8,264 words (`text`) / 8,571 words (`text_full`).

Regenerate with the held-out builder documented in `notebooks/kb_demo.ipynb`; the page
images themselves are reproducible from `scripts/get_data.sh` at the pinned revision.
