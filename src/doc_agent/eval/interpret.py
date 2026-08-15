# =============================================================================
# File:     src/doc_agent/eval/interpret.py
# Layer:    Stage 9 - EXPLAINABILITY (why retrieved / where looked)
# Status:   STUB - explain() raises NotImplementedError
#
# Purpose:
#   Turns an Answer into an account of how it was reached. Citations say WHICH
#   chunk was used; this says WHY that chunk was retrieved and WHERE on the page
#   the evidence physically sits - the difference between a reference and an
#   explanation.
#
# explain(answer, cfg) -> dict, combining two views:
#   1. Retrieval attribution - per-chunk similarity scores, which query (original
#      or reformulated) surfaced each one, and at which k. Since decide() may
#      re-retrieve at a wider k, the explanation should show that branch, making
#      the agent's reasoning path visible rather than inferred.
#   2. Visual grounding - Grad-CAM (or attention rollout) over the read region,
#      rendered onto the page image so the cited span can be located inside the
#      figure or table it came from. The corpus's own annotation boxes give a
#      reference to check the highlight against.
#
# Inputs: contracts.Answer + Citation spans, REGION_META (vision/layout.py) for
#         box geometry, PAGE_META for the image path, traces/run.jsonl for the
#         retrieval history.
# =============================================================================

"""Stage 9 — EXPLAINABLE — why-retrieved / where-looked"""
from __future__ import annotations
from ..contracts import *  # noqa

def explain(answer: Answer, cfg: dict) -> dict:
    """Grad-CAM on read region + retrieval-score attribution. IMPLEMENT."""
    raise NotImplementedError("Stage 9: interpretability")

