# =============================================================================
# File:     src/doc_agent/hooks.py
# Layer:    Cross-cutting seam registry
# Status:   FIXED - seam names are locked; tests/test_structure.py asserts the
#           exact set, and no seam may be added, removed or renamed.
#
# Purpose:
#   The mechanism that keeps horizontal concerns (privacy, security, grounding,
#   tracing) out of the vertical stages. A stage calls hooks.run(SEAM, ctx) at a
#   fixed point; features attach handlers to that seam via their own register().
#   Result: PII redaction is not sprinkled through ocr.py, and guardrails are
#   not inlined in agent.py - each lives in one module and is wired in one place
#   (wiring.py).
#
# The nine seams and who fires them:
#   AFTER_INGEST    pipeline, after pages are loaded/preprocessed/enhanced
#   AFTER_OCR       pipeline, on extracted text BEFORE indexing  (PII scrub)
#   BEFORE_INDEX    pipeline, on the final chunk list
#   AFTER_RETRIEVE  retrieval, on the candidate set
#   ON_STEP         agent loop, once per iteration               (trace)
#   ON_TOOL_CALL    agent loop, before every tool dispatch       (guardrails, trace)
#   BEFORE_ANSWER   agent loop, before synthesis                 (grounding, PII)
#   AFTER_ANSWER    agent loop, on the finished Answer           (trace, metrics)
#   ON_LOG          logging path                                 (PII scrub)
#
# API:
#   register(seam, handler) - attach; asserts the seam name is real
#   run(seam, ctx)          - run every handler in registration order, threading
#                             ctx through; a handler returning None keeps the
#                             previous ctx
#   clear()                 - drop all handlers (called by wiring.register_all
#                             so repeated wiring is idempotent, and by tests)
#
# Gotcha:
#   pipeline.py discards run()'s return value, so a handler that needs to change
#   a list the pipeline still holds must mutate it in place - see the
#   `chunks[:] = kept` line in governance/pii.py.
# =============================================================================

"""FIXED — cross-cutting seam. Horizontal features register handlers here; the pipeline and agent
call run() at fixed seams. Do NOT add/remove seams or the hooks.run() calls that use them."""
from __future__ import annotations
from collections import defaultdict
from typing import Callable

# The only points where cross-cutting code runs.
AFTER_INGEST = "after_ingest"
AFTER_OCR = "after_ocr"
BEFORE_INDEX = "before_index"
AFTER_RETRIEVE = "after_retrieve"
ON_STEP = "on_step"
ON_TOOL_CALL = "on_tool_call"
BEFORE_ANSWER = "before_answer"
AFTER_ANSWER = "after_answer"
ON_LOG = "on_log"
SEAMS = [AFTER_INGEST, AFTER_OCR, BEFORE_INDEX, AFTER_RETRIEVE, ON_STEP,
         ON_TOOL_CALL, BEFORE_ANSWER, AFTER_ANSWER, ON_LOG]

_handlers: dict[str, list[Callable]] = defaultdict(list)

def register(seam: str, handler: Callable) -> None:
    """Attach a handler to a seam. Called by each feature's register() via wiring.py."""
    assert seam in SEAMS, f"unknown seam {seam}"
    _handlers[seam].append(handler)

def run(seam: str, ctx: dict) -> dict:
    """Run every handler registered at `seam`, threading ctx through. Called at fixed points only."""
    for h in _handlers[seam]:
        ctx = h(ctx) or ctx
    return ctx

def clear() -> None:
    _handlers.clear()
