"""Stage 4 — chunk text"""

from __future__ import annotations

import re
import unicodedata

from ..contracts import *  # noqa
from ..logging_conf import get_logger

log = get_logger(__name__)

_MATH_FIXES = {
    "−": "-",
    "–": "-",
    "—": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "×": "x",
    " ": " ",
}


def _normalize(text: str) -> str:
    """NFKC plus the maths punctuation that would otherwise split a token in two."""
    text = unicodedata.normalize("NFKC", text)
    for bad, good in _MATH_FIXES.items():
        text = text.replace(bad, good)
    return re.sub(r"[ \t]+", " ", text).strip()


def _sections(text: str) -> list[str]:
    """Split page prose on Markdown headings — Nougat emits them, so they are free
    semantic boundaries and a far better cut point than a fixed window."""
    parts: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        if re.match(r"^\s{0,3}#{1,6}\s+\S", line) and cur:
            parts.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)
    if cur:
        parts.append("\n".join(cur).strip())
    return [p for p in parts if p]


def _window(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    if len(words) <= size:
        return [text] if words else []
    step = max(1, size - overlap)
    out = []
    for i in range(0, len(words), step):
        piece = words[i : i + size]
        if not piece:
            break
        out.append(" ".join(piece))
        if i + size >= len(words):
            break
    return out


def split(chunks: list[Chunk], cfg: dict) -> list[Chunk]:  # noqa: F405
    """Re-chunk to cfg['index'] size/overlap — REGION-AWARE.

    A chunk never spans two layout regions. Fixed-size windows over a flattened page
    would re-mix the columns and glue table cells onto neighbouring prose, undoing the
    reading order Stage 2 just established; keeping the region boundary is what makes a
    retrieved chunk citable back to one box on one page.
    """
    idx = cfg["index"]
    size = int(idx.get("chunk_tokens", 256))
    overlap = int(idx.get("overlap", 32))
    region_aware = bool(idx.get("region_aware", True))

    out: list[Chunk] = []  # noqa: F405
    for parent in chunks:
        text = _normalize(parent.text)
        if not text:
            continue
        # a figure/table transcription is one indivisible piece of evidence
        is_region = parent.id.split("#")[-1].startswith("r") or text.startswith("[")
        pieces = (
            [text]
            if (is_region and region_aware and len(text.split()) <= size * 2)
            else [w for sec in _sections(text) for w in _window(sec, size, overlap)]
        )
        for i, piece in enumerate(pieces):
            out.append(
                Chunk(  # noqa: F405
                    id=f"{parent.id}/c{i:03d}",
                    doc_id=parent.doc_id,
                    text=piece,
                    page_ids=list(parent.page_ids),
                )
            )

    lens = [len(c.text.split()) for c in out] or [0]
    log.info(
        "chunk: %d -> %d chunks (size=%d overlap=%d, mean %d words)",
        len(chunks),
        len(out),
        size,
        overlap,
        sum(lens) // max(1, len(lens)),
    )
    return out
