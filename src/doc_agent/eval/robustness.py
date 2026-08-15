# =============================================================================
# File:     src/doc_agent/eval/robustness.py
# Layer:    Stage 9 - OOD / scan-quality stress
# Status:   STUB - stress() raises NotImplementedError
#
# Purpose:
#   Measures how far accuracy falls when the input stops being ideal. The corpus
#   is born-digital and clean, so a headline number measured on it is an
#   optimistic ceiling; this module is what turns that ceiling into a curve.
#
# The intended experiment (already supported by the ingest stage):
#   Set cfg.ingest.degrade to have preprocess._degrade() manufacture blurred,
#   noisy copies of KNOWN-CLEAN pages, re-run OCR and retrieval over them, and
#   report the metric delta against the clean reference. Because the clean
#   original is available, the degradation level is a controlled variable rather
#   than a confound - the honest use of a degradation library on clean data.
#
# Dimensions worth sweeping:
#   blur / noise level, JPEG-style compression, resolution reduction, rotation,
#   and out-of-domain pages (a different venue or template).
#
# Report: metric vs degradation level per stage, so it is visible WHERE the
#         system breaks first - OCR, retrieval, or the agent's abstention
#         behaviour. Ideally the abstention rate rises as quality drops; an
#         agent that keeps answering confidently on degraded input is the
#         failure this measurement exists to catch.
# =============================================================================

"""Stage 9 — OOD / scan-quality stress"""
from __future__ import annotations
from ..contracts import *  # noqa

def stress(cfg: dict) -> dict:
    raise NotImplementedError("Stage 9: robustness/OOD")

