# =============================================================================
# File:     src/doc_agent/logging_conf.py
# Layer:    Cross-cutting - observability (auditable NFR)
# Status:   PARTIAL - get_logger() is FIXED and working; register() is a STUB.
#
# Purpose:
#   Two related jobs.
#
#   1. get_logger(name) - the project-wide structured logger. Emits one JSON
#      object per line ({ts, lvl, mod, msg}) to stdout so a run's logs can be
#      parsed and audited mechanically instead of eyeballed. Every module does
#      `log = get_logger(__name__)` at import; print() is banned project-wide.
#      Handlers are attached only once per logger name, so repeated imports do
#      not produce duplicated lines.
#
#   2. register(hooks) - wires tracing into the ON_STEP, ON_TOOL_CALL and
#      AFTER_ANSWER seams and appends a contracts.TraceStep line to
#      traces/run.jsonl for each. That file is what the A3 agentic-feature
#      check reads to confirm the agent's path actually varies with what it
#      observed.
#
# TODO (Stage 6 / A3):
#   register()'s _trace handler currently raises NotImplementedError. Because
#   wiring.register_all() registers it unconditionally, the first hooks.run()
#   in the pipeline will raise until this is implemented - implement it before
#   running build_knowledge_base() or answer() end to end.
# =============================================================================

"""FIXED — structured logging (auditable NFR). Use get_logger(), never print()."""
from __future__ import annotations
import logging, sys

def get_logger(name: str) -> logging.Logger:
    lg = logging.getLogger(name)
    if not lg.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter('{"ts":"%(asctime)s","lvl":"%(levelname)s","mod":"%(name)s","msg":"%(message)s"}'))
        lg.addHandler(h); lg.setLevel(logging.INFO)
    return lg


def register(hooks) -> None:
    """Wire structured tracing at each seam (auditable trail) AND emit traces/run.jsonl.
    Each seam appends a contracts.TraceStep line to traces/run.jsonl so the A3 agentic-feature
    check can read the trajectory (path must depend on observations). IMPLEMENT."""
    def _trace(ctx: dict) -> dict:
        raise NotImplementedError("Tracing: append ctx to the audit trail")
    hooks.register(hooks.ON_STEP, _trace)
    hooks.register(hooks.ON_TOOL_CALL, _trace)
    hooks.register(hooks.AFTER_ANSWER, _trace)
