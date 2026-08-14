"""Stage 9 — metrics"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any

from ..contracts import *  # noqa
from ..contracts import Answer  # explicit: keeps the star import from hiding the name


def normalize_text(s: str) -> str:
    """Shared normalisation so OCR scoring is not measuring punctuation style."""
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[‐-―]", "-", s)
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


def cer(pred: str, gold: str) -> float:
    """Character error rate = edit distance / len(gold), the standard OCR number."""
    a, b = normalize_text(pred), normalize_text(gold)
    if not b:
        return 0.0 if not a else 1.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1] / len(b)


def wer(pred: str, gold: str) -> float:
    """Word error rate — same edit distance, over tokens instead of characters."""
    a, b = normalize_text(pred).split(), normalize_text(gold).split()
    if not b:
        return 0.0 if not a else 1.0
    prev = list(range(len(b) + 1))
    for i, wa in enumerate(a, 1):
        cur = [i]
        for j, wb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (wa != wb)))
        prev = cur
    return prev[-1] / len(b)


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
