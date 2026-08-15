# =============================================================================
# File:     src/doc_agent/eval/metrics.py
# Layer:    Stage 9 - metric definitions
# Status:   PARTIAL - the OCR metrics are IMPLEMENTED; the retrieval, grounding,
#           citation, calibration and fairness metrics are STUBS.
#
# normalize_text(s) - the most consequential function here.
#   Shared normalisation so OCR scoring measures READING, not ENCODING. The
#   reader emits LaTeX ("\(n\)", "\mathcal{C}") where the PDF text layer emits
#   font-mapped Unicode, so control sequences are stripped and both sides are
#   compared as text. Steps: NFKC fold, lowercase, unify dash variants, drop
#   LaTeX control sequences and math delimiters, drop glyph classes the two sides
#   encode differently, collapse whitespace.
#   Math VARIABLES are deliberately still scored: the oracle repairs the PDF's
#   truncated codepoints and NFKC folds mathematical-italic n to "n", while
#   "\(n\)" reduces to "n" here, so the two sides agree. Greek letters and math
#   operators stay EXCLUDED because LaTeX spells them as words ("\alpha") and the
#   PDF as glyphs (α) - scoring those would measure notation, not accuracy. The
#   remaining excluded ranges (CJK, Hangul, Private Use) are defensive, for pages
#   whose font mapping is broken in a way the oracle did not repair.
#
# Implemented metrics:
#   ocr_f1(pred, gold)  token-level F1 as a multiset intersection, so a repeated
#                       word must be repeated the right number of times
#   cer / wer           edit distance over characters / words, normalised by gold
#                       length - the standard OCR numbers
#   _edit_distance      uses the C `Levenshtein` implementation when installed
#                       (already a dependency via Nougat post-processing) and
#                       falls back to pure Python, so the metric never depends on
#                       an optional package. Pure Python costs seconds per
#                       2,500-character page, which made the evidence notebook
#                       slow to re-run.
#
# Still to implement:
#   recall_at_k(retrieved, gold, k)  retrieval quality  -> recall NFR
#   groundedness(answer)             fraction of claims backed by evidence
#                                    -> no-hallucination NFR
#   citation_accuracy(answer)        do the citations point at the right spans
#   ece(confidences, correct)        expected calibration error
#   subgroup_gap(scores_by_group)    worst-group disparity -> fairness NFR
# =============================================================================

"""Stage 9 — metrics"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any

from ..contracts import *  # noqa
from ..contracts import Answer  # explicit: keeps the star import from hiding the name

# The reader emits LaTeX ("\(n\)", "\mathcal{C}") where the PDF text layer emits font
# mapped Unicode, so the control sequences are stripped and both sides compared as text.
# Math VARIABLES are scored: the oracle recovers them (the PDF's truncated codepoints are
# repaired and NFKC folds a math italic n to "n"), and "\(n\)" reduces to "n" here, so the
# two now agree. Greek letters and math operators stay excluded because LaTeX spells them
# as words ("\alpha") and the PDF as glyphs ("α"); the remaining classes are defensive,
# for any page whose font mapping is broken in a way the oracle did not repair.
_MATH_GLYPHS = re.compile(
    "["
    "\u1d400-\u1d7ff"  # Mathematical Alphanumeric Symbols
    "\uac00-\ud7af"  # Hangul Syllables (mis-decoded math italics)
    "\u3400-\u4dbf"  # CJK Ext A
    "\u4e00-\u9fff"  # CJK Unified
    "\ue000-\uf8ff"  # Private Use (unmapped font glyphs)
    "\u0370-\u03ff"  # Greek (LaTeX writes \alpha, the PDF writes the glyph)
    "\u2200-\u22ff"  # Mathematical Operators
    "]"
)
_LATEX = re.compile(r"\\[a-zA-Z]+\s*|\\[()\[\]]|[${}^_~]")


def normalize_text(s: str) -> str:
    """Shared normalisation so OCR scoring measures reading, not encoding."""
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[‐-―]", "-", s)
    s = _LATEX.sub(" ", s)  # drop LaTeX control sequences and math delimiters
    s = _MATH_GLYPHS.sub(" ", s)  # drop symbols the two sides encode differently
    s = re.sub(r"[^\w\s.,;:%()\[\]/+=<>-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def ocr_f1(pred: str, gold: str) -> float:
    """Token-level F1 between a transcription and its ground truth (bag of tokens with
    multiplicity, so repeated words still have to be repeated correctly)."""
    p, g = Counter(normalize_text(pred).split()), Counter(normalize_text(gold).split())
    if not p and not g:
        return 1.0
    if not p or not g:
        return 0.0
    overlap = sum((p & g).values())
    if overlap == 0:
        return 0.0
    precision, recall = overlap / sum(p.values()), overlap / sum(g.values())
    return 2 * precision * recall / (precision + recall)


def _edit_distance(a: Any, b: Any) -> int:
    """Levenshtein distance, using the C implementation when it is installed.

    Pure Python is O(len(a) x len(b)) interpreted, which on 2,500-character pages costs
    seconds per comparison and makes the evidence notebook slow to re-run. The C library
    is already a dependency (Nougat's post-processing needs it), so use it when present
    and keep the fallback so the metric never depends on an optional package.
    """
    try:
        import Levenshtein

        return int(Levenshtein.distance(a, b))
    except ImportError:
        pass
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(pred: str, gold: str) -> float:
    """Character error rate = edit distance / len(gold), the standard OCR number."""
    a, b = normalize_text(pred), normalize_text(gold)
    if not b:
        return 0.0 if not a else 1.0
    return _edit_distance(a, b) / len(b)


def wer(pred: str, gold: str) -> float:
    """Word error rate — same edit distance, over tokens instead of characters."""
    a, b = normalize_text(pred).split(), normalize_text(gold).split()
    if not b:
        return 0.0 if not a else 1.0
    return _edit_distance(a, b) / len(b)


def recall_at_k(retrieved: list, gold: list, k: int) -> float:
    raise NotImplementedError


def groundedness(answer: Answer) -> float:
    raise NotImplementedError  # no-hallucination


def citation_accuracy(answer: Answer) -> float:
    raise NotImplementedError


def ece(confidences: Any, correct: Any) -> float:
    raise NotImplementedError  # calibration


def subgroup_gap(scores_by_group: dict) -> float:
    raise NotImplementedError  # fairness
