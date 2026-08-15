# =============================================================================
# File:     src/doc_agent/llm/postprocess.py
# Layer:    LLM - answer formatting and the grounding gate
# Status:   STUB - format_answer() and the _ground handler both raise
#           NotImplementedError
#
# Purpose:
#   The last check between the model and the user, and the module that owns the
#   no-hallucination NFR.
#
#   format_answer(raw, citations) -> Answer
#       Turns raw model text into a contracts.Answer: attaches citations, sets
#       `grounded`, sets `confidence` (calibrated - see eval/calibration.py) and
#       enforces abstention when the evidence does not support the claim.
#
#   register(hooks) -> _ground at BEFORE_ANSWER
#       Runs on every answer regardless of which path produced it. The gate must
#       verify each claim is supported by a retrieved chunk and downgrade the
#       answer to an abstention when it is not. Wiring it as a hook rather than a
#       call inside synthesize() means a future second answer path cannot bypass
#       it by forgetting to call it.
#
# Ordering:
#   wiring.py registers pii.register before postprocess.register, so PII
#   redaction runs first and the gate judges the exact text that will be
#   returned.
#
# Blocking note:
#   Because _ground is registered unconditionally, ANY pipeline run that reaches
#   BEFORE_ANSWER raises until this is implemented.
#
# Verified by: tests/test_crosscutting.py::test_grounding_unsupported_query_abstains
# =============================================================================

"""LLM — answer post-process / format / abstention"""
from __future__ import annotations
from ..contracts import *  # noqa

def format_answer(raw: str, citations: list) -> Answer:
    """Attach citations, set grounded/confidence, enforce abstention. IMPLEMENT."""
    raise NotImplementedError("LLM: format_answer")



def register(hooks) -> None:
    """Wire the grounding / abstention gate. IMPLEMENT (abstain if answer unsupported by evidence)."""
    def _ground(ctx: dict) -> dict:
        raise NotImplementedError("Grounding: abstain if unsupported; enforce citations")
    hooks.register(hooks.BEFORE_ANSWER, _ground)
