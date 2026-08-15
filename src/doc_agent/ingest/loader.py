# =============================================================================
# File:     src/doc_agent/ingest/loader.py
# Stage:    1 - load scanned page images
# Status:   IMPLEMENTED
#
# Purpose:
#   Turns the on-disk corpus produced by scripts/get_data.sh into the list[Page]
#   the rest of the pipeline consumes, and caches everything else known about
#   each page in a sidecar dictionary.
#
# Key objects:
#   PAGE_META : dict[page_id -> row]
#       contracts.Page is FIXED at (id, image_path, doc_id), so page number,
#       width/height, split, word count and the absolute image path live here
#       instead. Populated by load_pages() and read by preprocess, layout, ocr,
#       validate and the eval code. It is module-level state: load_pages() must
#       run before any consumer touches it, and it is cleared on every call so a
#       second load never inherits stale rows.
#   repo_root()   - absolute repo path, derived from __file__ (../../..), so
#                   scripts and notebooks work from any working directory.
#   corpus_dir()  - data/raw/, where the rendered corpus lives.
#   load_qa()     - the benchmark's own questions, evidence page ids, normalised
#                   boxes and strata; returns [] when absent so the layout stage
#                   degrades to pure heuristics rather than crashing.
#   load_pages()  - reads manifest.jsonl, honours cfg.ingest.limit_pages (fast
#                   smoke runs) and cfg.ingest.splits (train/val/test isolation),
#                   and raises a message naming get_data.sh when the manifest is
#                   missing.
#
# Inputs  : data/raw/manifest.jsonl, data/raw/qa.jsonl, cfg["ingest"]
# Outputs : list[Page], populated PAGE_META
# =============================================================================

"""Stage 1 — load scanned page-images"""

from __future__ import annotations

import json
import os

from ..contracts import *  # noqa
from ..contracts import Page  # explicit: keeps the star import from hiding the name
from ..logging_conf import get_logger

log = get_logger(__name__)

# contracts.Page carries only (id, image_path, doc_id) and is FIXED, so everything else
# the pipeline needs about a page — page number, geometry, split, word count, whether the
# page is multi-column — lives in this sidecar, keyed by page id. It is populated by
# load_pages() and read by the layout, index and eval stages.
PAGE_META: dict[str, dict] = {}


def repo_root() -> str:
    """Absolute path of the repository root (src/doc_agent/ingest/ -> ../../..)."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def corpus_dir(cfg: dict) -> str:
    """Where scripts/get_data.sh put the rendered corpus."""
    return os.path.join(repo_root(), "data", "raw")


def load_qa(cfg: dict) -> list[dict]:
    """The benchmark's own questions, evidence pages, boxes and strata."""
    path = os.path.join(corpus_dir(cfg), "qa.jsonl")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def load_pages(cfg: dict) -> list[Page]:
    """Read data/raw/ -> list[Page], and cache per-page metadata in PAGE_META."""
    root = corpus_dir(cfg)
    manifest = os.path.join(root, "manifest.jsonl")
    if not os.path.exists(manifest):
        raise FileNotFoundError(
            f"{manifest} missing — run `bash scripts/get_data.sh` to build the corpus first."
        )

    limit = int(cfg.get("ingest", {}).get("limit_pages", 0) or 0)
    splits = cfg.get("ingest", {}).get("splits")

    pages: list[Page] = []
    PAGE_META.clear()
    with open(manifest, encoding="utf-8") as fh:
        for line in fh:
            row = json.loads(line)
            if splits and row.get("split") not in splits:
                continue
            row["abs_path"] = os.path.join(root, row["image_path"])
            PAGE_META[row["page_id"]] = row
            pages.append(
                Page(  # noqa: F405
                    id=row["page_id"],
                    image_path=row["abs_path"],
                    doc_id=row["doc_id"],
                )
            )
            if limit and len(pages) >= limit:
                break

    log.info(
        "loaded %d pages from %d documents (%d words)",
        len(pages),
        len({p.doc_id for p in pages}),
        sum(PAGE_META[p.id]["n_words"] for p in pages),
    )
    return pages
