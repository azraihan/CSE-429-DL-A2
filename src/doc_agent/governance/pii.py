"""Governance — PII detection + redaction (mandatory)

Every paper carries an author block naming living, identifiable researchers, with
affiliations, emails and sometimes ORCIDs; acknowledgements name more. This is public
scholarly attribution, so we do not alter the stored page images — but we keep it out of
the agent's reach: identifiers are redacted from extracted text before indexing, and a
chunk that is mostly personal identifiers is dropped entirely, so questions about people
rather than content retrieve nothing and the agent abstains.

Wired at AFTER_OCR (before indexing), BEFORE_ANSWER (outgoing answer) and ON_LOG.
"""
from __future__ import annotations

import re

from ..contracts import *  # noqa
from ..logging_conf import get_logger

log = get_logger(__name__)

_PATTERNS: list[tuple[str, "re.Pattern[str]"]] = [
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("ORCID", re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dXx]\b")),
    ("URL_USER", re.compile(r"\b(?:https?://)?(?:github|linkedin)\.com/[\w./-]+", re.I)),
    ("PHONE", re.compile(r"(?<!\d)(?:\+\d{1,3}[ -]?)?(?:\(\d{2,4}\)[ -]?)?\d{3,4}[ -]\d{4}(?!\d)")),
]

# "Corresponding author: Jane Q. Doe", "Acknowledgements. We thank John Smith ..."
_NAMEY = re.compile(
    r"\b(?:corresponding author|e-?mail|contact)\b\s*[:\-]?\s*"
    r"([A-Z][a-z]+(?:\s+[A-Z]\.?)*\s+[A-Z][a-z]+)",
    re.I,
)


def detect(text: str) -> list[tuple[int, int, str]]:
    """Return (start, end, type) PII spans."""
    spans: list[tuple[int, int, str]] = []
    for label, pat in _PATTERNS:
        for m in pat.finditer(text):
            spans.append((m.start(), m.end(), label))
    for m in _NAMEY.finditer(text):
        spans.append((m.start(1), m.end(1), "PERSON"))
    return sorted(spans)


def redact(text: str) -> str:
    """Replace every detected span with a typed placeholder."""
    spans = detect(text)
    if not spans:
        return text
    out, last = [], 0
    for start, end, label in spans:
        if start < last:  # overlapping match, keep the first
            continue
        out.append(text[last:start])
        out.append(f"[{label}]")
        last = end
    out.append(text[last:])
    return "".join(out)


def is_mostly_identifiers(text: str) -> bool:
    """An author block is names, affiliations and emails and almost no prose."""
    words = text.split()
    if not words or len(words) > 220:
        return False
    spans = detect(text)
    covered = sum(e - s for s, e, _ in spans)
    if covered / max(1, len(text)) > 0.12:
        return True
    # a run of Capitalised Name-like tokens with barely any lowercase connective prose
    capish = sum(1 for w in words if w[:1].isupper())
    lower = sum(1 for w in words if w.islower() and len(w) > 3)
    return len(words) >= 12 and capish / len(words) > 0.62 and lower / len(words) < 0.12


def register(hooks) -> None:  # type: ignore[no-untyped-def]
    """Wire PII redaction into the pipeline."""

    def _scrub(ctx: dict) -> dict:
        chunks = ctx.get("chunks")
        if isinstance(chunks, list) and chunks and isinstance(chunks[0], Chunk):  # noqa: F405
            kept, dropped = [], 0
            for c in chunks:
                if is_mostly_identifiers(c.text):
                    dropped += 1
                    continue
                c.text = redact(c.text)
                kept.append(c)
            if dropped:
                log.info("pii: dropped %d identifier-dominated chunks", dropped)
            # pipeline.py discards hooks.run()'s return value and passes the SAME list
            # on to Stage 4, so the drop has to be an in-place edit to take effect.
            chunks[:] = kept
            ctx["chunks"] = kept

        ans = ctx.get("answer")
        if isinstance(ans, Answer):  # noqa: F405
            ans.text = redact(ans.text)

        msg = ctx.get("msg")
        if isinstance(msg, str):
            ctx["msg"] = redact(msg)
        return ctx

    hooks.register(hooks.AFTER_OCR, _scrub)       # scrub extracted text before indexing
    hooks.register(hooks.BEFORE_ANSWER, _scrub)   # scrub the outgoing answer
    hooks.register(hooks.ON_LOG, _scrub)          # scrub logs
