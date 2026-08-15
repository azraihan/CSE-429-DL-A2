# =============================================================================
# File:     src/doc_agent/data/validate.py
# Layer:    Data - schema and quality validation at ingest
# Status:   IMPLEMENTED
#
# Purpose:
#   Fails the run early and loudly when the corpus is not what the rest of the
#   system assumes. Every check here corresponds to a failure that would
#   otherwise appear much later as an unexplained metric.
#
# validate(pages) collects ALL problems before raising, so one run reports every
# fault rather than one per attempt:
#   1. Corpus floors  - >= 300 pages and >= 60,000 words (MIN_PAGES / MIN_WORDS),
#                       the assignment's minimum scale.
#   2. Missing images - a manifest row whose PNG is absent.
#   3. Manifest gaps  - a Page with no PAGE_META row; every downstream stage
#                       looks up geometry there, so this would fail later.
#   4. SPLIT LEAKAGE  - the check that matters most. A1 named "the same paper in
#                       train and test" as the single most likely leak. Splits
#                       are assigned per doc_id and inherited by every page, so
#                       the leak should be structurally impossible - this
#                       ASSERTS that rather than assuming it, because a leak here
#                       inflates every reported number and is invisible in the
#                       metrics themselves.
#   5. Duplicate page ids.
#
# Inputs  : list[Page], PAGE_META (from ingest/loader.py)
# Raises  : ValueError listing every problem found
# =============================================================================

"""Data — data schema/quality validation at ingest"""

from __future__ import annotations

import os
from collections import defaultdict

from ..contracts import *  # noqa
from ..ingest.loader import PAGE_META
from ..logging_conf import get_logger

log = get_logger(__name__)

MIN_PAGES = 300
MIN_WORDS = 60_000


def validate(pages: list[Page]) -> None:  # noqa: F405
    """Assert min pages/words, format, and no leakage across splits.

    A1 named "the same paper in train and test" as the single most likely leak. Splits
    are assigned per doc_id and inherited by every page, so the leak should be
    structurally impossible — this asserts it rather than assuming it.
    """
    problems: list[str] = []

    if len(pages) < MIN_PAGES:
        problems.append(f"corpus floor: {len(pages)} pages < {MIN_PAGES}")

    words = sum(PAGE_META.get(p.id, {}).get("n_words", 0) for p in pages)
    if words < MIN_WORDS:
        problems.append(f"corpus floor: {words} words < {MIN_WORDS}")

    missing = [p.id for p in pages if not os.path.exists(p.image_path)]
    if missing:
        problems.append(f"{len(missing)} page images missing, e.g. {missing[:3]}")

    unknown = [p.id for p in pages if p.id not in PAGE_META]
    if unknown:
        problems.append(f"{len(unknown)} pages absent from the manifest, e.g. {unknown[:3]}")

    splits_by_doc: dict[str, set[str]] = defaultdict(set)
    for p in pages:
        split = PAGE_META.get(p.id, {}).get("split")
        if split:
            splits_by_doc[p.doc_id].add(split)
    leaked = {d: s for d, s in splits_by_doc.items() if len(s) > 1}
    if leaked:
        problems.append(
            f"LEAKAGE: {len(leaked)} documents span multiple splits: {list(leaked)[:3]}"
        )

    dupes = len(pages) - len({p.id for p in pages})
    if dupes:
        problems.append(f"{dupes} duplicate page ids")

    if problems:
        raise ValueError("corpus validation failed:\n  - " + "\n  - ".join(problems))

    log.info(
        "validate: OK — %d pages, %d words, %d documents, no split leakage",
        len(pages),
        words,
        len({p.doc_id for p in pages}),
    )
