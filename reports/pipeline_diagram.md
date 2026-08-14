# Knowledge-base pipeline — PaperScholar (G19)

Stages 1–4, as built for A2. Stage order is fixed by `src/doc_agent/pipeline.py`; the
labels on the arrows are the `contracts.py` types that cross each boundary.

```mermaid
flowchart TB
    subgraph S0["Stage 0 · Frame"]
        A0["configs/task.yaml<br/>domain · multi-column · robust<br/>F1(S1) − F1(S3) ≤ 8"]
    end

    subgraph S1["Stage 1 · Ingest"]
        A["scripts/get_data.sh<br/>SciEGQA-Bench @ pinned rev<br/>PDF.tar → render 300 DPI"]
        B["ingest/loader.py<br/>load_pages()"]
        C["ingest/preprocess.py<br/>run() — verify contract<br/>no deskew/denoise"]
    end

    subgraph S2["Stage 2 · Layout ▲ E2"]
        D["vision/layout.py · detect()<br/>gutter → bands → reading order<br/>+ corpus figure/table boxes"]
    end

    subgraph S3["Stage 3 · OCR"]
        E["vision/ocr.py · transcribe()<br/>Nougat full page (prose)<br/>Nougat on crop (figure/table)"]
    end

    subgraph S4["Stage 4 · Index"]
        G["index/chunk.py · split()<br/>region-aware, heading-split"]
        H["index/embed.py · encode()<br/>bge-base-en-v1.5, 768-d"]
        I["index/store.py · build()<br/>FAISS IndexFlatIP"]
    end

    A -->|"manifest.jsonl<br/>qa.jsonl · splits.json"| B
    B -->|"list[Page]"| C
    C -->|"list[Page]"| D
    D -->|"list[Region] IN READING ORDER"| E
    E -->|"list[Chunk]"| F{{"hooks.AFTER_OCR<br/>governance/pii.py<br/>redact + drop author blocks"}}
    F -->|"list[Chunk]"| G
    G -->|"list[Chunk]"| H
    H -->|"float32[n, 768]"| I
    I -->|"data/index/"| J["retrieval/retriever.py<br/>retrieve() → Chunk.score"]

    A0 -.->|"drives every choice"| S1
    E -.->|"ocr_cache.jsonl<br/>resume on crash"| E

    classDef gated fill:#fde2e2,stroke:#c0392b,stroke-width:2px
    classDef seam fill:#fff3cd,stroke:#b8860b,stroke-width:2px
    class D gated
    class F seam
```

## Why the shape is what it is

**Stage 2 is the load-bearing stage, not Stage 3.** 56.1% of this corpus's questions have
their evidence annotated inside a figure or table, and 16.8% of pages are two-column
where reading order is not visual order. So `detect()` returns regions **in reading
order** and that list order is the contract Stage 3 consumes. Everything else follows
from getting that right.

**The two OCR paths exist for the two evidence kinds.** Page prose gets one full-page
Nougat pass, because Nougat resolves multi-column order internally and emits LaTeX for
mathematics. A figure or table gets its own pass over the padded crop, so evidence
living inside a region becomes its own retrievable, citable chunk rather than being
flattened into the surrounding prose.

**The PII seam sits between OCR and indexing** because that is the last point where text
exists but is not yet searchable — redacting later would leave identifiers in the index,
redacting earlier would mean re-reading pages.

**Chunks never span regions.** Fixed-size windows over a flattened page would re-mix the
columns Stage 2 just separated and glue table cells onto neighbouring prose. The region
boundary is what lets a retrieved chunk be traced back to one box on one page — which is
what A3's grounding gate will need.

## Data contracts crossing each boundary

| Boundary | Type | Carries |
|---|---|---|
| loader → preprocess → layout | `Page` | `id`, `image_path`, `doc_id` |
| layout → ocr | `list[Region]` | `page_id`, `bbox`, `kind`, **ordered** |
| ocr → pii → chunk → embed | `Chunk` | `id`, `doc_id`, `text`, `page_ids`, `score` |
| store → retriever | FAISS + `chunks.jsonl` | vectors + chunk payloads |

`contracts.py` is fixed and cannot gain fields, so per-page metadata (page number,
geometry, split, multi-column flag) lives in `ingest.loader.PAGE_META`, and per-region
reading-order index and provenance live in `vision.layout.REGION_META`, both keyed by id.

## Reproducing it

```bash
bash scripts/get_data.sh      # corpus @ pinned revision 9bdca77b
bash scripts/build_index.sh   # validate → stages 1-4 → data/index/
```

`build_index.sh` asserts the corpus floors (≥300 pages, ≥60k words) and that no document
appears in two splits before any model runs.
