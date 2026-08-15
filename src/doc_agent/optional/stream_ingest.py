# =============================================================================
# File:     src/doc_agent/optional/stream_ingest.py
# Layer:    OPTIONAL - batch / streaming ingestion for very large corpora
# Status:   STUB, off by default. CI does not require an implementation.
#
# Purpose:
#   stream(cfg) yields pages incrementally instead of materialising the whole
#   corpus in memory, for a corpus too large to load at once or one that arrives
#   continuously.
#
# Why it is not needed here:
#   ingest/loader.py loads the manifest eagerly, which is comfortable at this
#   corpus's scale (~1.8k pages, 0.58 GB of images) because only PATHS are held -
#   images are opened one at a time by preprocess and ocr. The stage that could
#   not be redone cheaply is OCR, and that is already incremental for a different
#   reason: it streams results to a resume cache so an interrupted run continues.
#
# If a future corpus outgrows this, the change is contained: load_pages() becomes
# a generator and the same stage sequence consumes it, since no stage after
# ingest needs the full page list at once.
# =============================================================================

"""OPTIONAL — batch/streaming ingestion for very large corpora
Activate only if your data speciality or NFR requires it (e.g. a huge-corpus / scalable project). Off by default; CI does not require impl."""
from __future__ import annotations

def stream(cfg: dict):
    raise NotImplementedError("optional: stream ingest")

