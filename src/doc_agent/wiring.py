# =============================================================================
# File:     src/doc_agent/wiring.py
# Layer:    Cross-cutting - the wiring manifest
# Status:   FIXED (provided scaffold)
#
# Purpose:
#   One auditable page that answers "which horizontal features are active, and
#   where do they run?". If a feature is not listed in register_all(), it is not
#   wired anywhere in the system - there is no second place to look.
#
# register_all(cfg) attaches, in this order:
#   logging_conf.register(hooks)      tracing/audit -> ON_STEP, ON_TOOL_CALL,
#                                                       AFTER_ANSWER
#   pii.register(hooks)               privacy       -> AFTER_OCR, BEFORE_ANSWER,
#                                                       ON_LOG
#   guardrails.register(hooks, cfg)   security      -> ON_TOOL_CALL
#   postprocess.register(hooks)       grounding     -> BEFORE_ANSWER
#
#   It begins with hooks.clear(), so calling it twice (build_knowledge_base and
#   answer both call it) re-wires cleanly instead of stacking duplicate handlers.
#
# Ordering matters:
#   Registration order is execution order within a seam. At BEFORE_ANSWER, PII
#   redaction runs before the grounding gate, so the gate judges the text that
#   will actually be returned.
#
# Current caveat:
#   logging_conf.register and postprocess.register install handlers that still
#   raise NotImplementedError, so any pipeline run that fires their seams will
#   fail until Stage 6 tracing and the grounding gate are implemented.
# =============================================================================

"""FIXED — the single auditable manifest of cross-cutting features and where they attach.
register_all() wires every horizontal feature into the hook seams. If a feature is not listed here,
it is not wired anywhere. Implement each feature's register() in its owning module."""
from __future__ import annotations
from . import hooks, logging_conf
from .governance import pii
from .agent import guardrails
from .llm import postprocess

def register_all(cfg: dict) -> None:
    hooks.clear()
    logging_conf.register(hooks)        # tracing/audit  -> ON_STEP, ON_TOOL_CALL, AFTER_ANSWER
    pii.register(hooks)                 # privacy        -> AFTER_OCR, BEFORE_ANSWER, ON_LOG
    guardrails.register(hooks, cfg)     # security       -> ON_TOOL_CALL
    postprocess.register(hooks)         # grounding      -> BEFORE_ANSWER
