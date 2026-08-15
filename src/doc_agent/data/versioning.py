# =============================================================================
# File:     src/doc_agent/data/versioning.py
# Layer:    Data - corpus versioning
# Status:   IMPLEMENTED
#
# Purpose:
#   Answers "which corpus produced this number?". Without a corpus version id, a
#   metric in the report cannot be tied to the data it came from, and a
#   re-rendered or extended corpus silently invalidates every previously reported
#   result. Complements DVC (.dvc/) with a value that can be embedded in run
#   records and read without the DVC toolchain.
#
# snapshot(corpus_dir) -> 16-hex-character version id
#   Hashes manifest.jsonl, qa.jsonl and splits.json with SHA-256 (streamed in 1 MB
#   blocks), NOT the page images. Those three files already name every page, its
#   geometry and its split assignment, so any change to the corpus changes them -
#   while hashing 0.58 GB of PNGs on every run would cost minutes and buy no more
#   certainty. Missing files are skipped and recorded, so the id stays meaningful
#   on a partially built corpus.
#   Writes data/corpus_version.json: {corpus_version, hashed, corpus_dir, created}.
#
# Used by: MLOps run records and the eval reports, to stamp results with the
#          corpus they were measured on.
# =============================================================================

"""Data — corpus versioning (which corpus version -> which result)"""

from __future__ import annotations

import hashlib
import json
import os
import time

from ..contracts import *  # noqa
from ..logging_conf import get_logger

log = get_logger(__name__)


def snapshot(corpus_dir: str) -> str:
    """Hash + record a corpus version id.

    Hashes the manifest and split assignment rather than every page image: those two
    files already name every page, its size and its split, so any change to the corpus
    changes them, and hashing 0.58 GB of PNGs on every run would not buy more certainty.
    """
    h = hashlib.sha256()
    parts: list[str] = []
    for name in ("manifest.jsonl", "qa.jsonl", "splits.json"):
        path = os.path.join(corpus_dir, name)
        if not os.path.exists(path):
            continue
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        parts.append(name)

    version = h.hexdigest()[:16]
    record = {
        "corpus_version": version,
        "hashed": parts,
        "corpus_dir": os.path.relpath(corpus_dir, os.path.dirname(corpus_dir)),
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out = os.path.join(corpus_dir, "..", "corpus_version.json")
    with open(os.path.abspath(out), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)

    log.info("corpus version %s (from %s)", version, ", ".join(parts) or "nothing")
    return version
