# =============================================================================
# File:     src/doc_agent/agent/guardrails.py
# Stage:    6 - SECURITY (autonomy, budgets, prompt-injection defence)
# Status:   PARTIAL - register() and the seam wiring are done; Guardrails.check()
#           is a STUB.
#
# Purpose:
#   The security boundary around tool use. register() attaches _check to the
#   ON_TOOL_CALL seam, so EVERY tool call in agent.run() passes through
#   Guardrails.check() before dispatch - there is no code path that reaches a
#   tool without being checked, which is exactly why this is a hook rather than
#   an `if` inside the agent.
#
# check(action) must enforce three things:
#   1. BUDGET      - step and cost ceilings from cfg["agent"]. An agent that can
#                    loop is an agent that can burn an unbounded amount of money
#                    and time; self.steps / self.spent are tracked by reset().
#   2. AUTONOMY    - is this tool permitted at the configured autonomy level?
#                    Low-autonomy runs should route consequential actions to
#                    escalate_to_human instead of executing them.
#   3. INJECTION   - instruction/content isolation. Retrieved document text is
#                    DATA, never instructions. A page containing "ignore your
#                    previous instructions" must not change the agent's
#                    behaviour; this is the property
#                    tests/test_crosscutting.py::test_injection_in_document_does_not_hijack
#                    is written to prove.
#   Violations raise, failing closed - a guardrail that logs and continues is
#   not a guardrail.
#
# TODO: implement check(); note reset() defines self.spent/self.steps, so check()
#       should increment them as well as test them.
# =============================================================================

"""Stage 6 — SECURITY — autonomy, budgets, prompt-injection defense"""
from __future__ import annotations
from ..contracts import *  # noqa

class Guardrails:
    """Enforce autonomy level, step/cost budget, and instruction/content isolation."""
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg["agent"]
    def reset(self) -> None:
        self.spent = 0.0; self.steps = 0
    def check(self, action: dict) -> None:
        """Raise if over budget / disallowed autonomy / injection detected. IMPLEMENT."""
        raise NotImplementedError("Stage 6: guardrails")



def register(hooks, cfg: dict) -> None:
    """Wire guardrails into every tool call. IMPLEMENT (call Guardrails.check)."""
    g = Guardrails(cfg); g.reset()
    def _check(ctx: dict) -> dict:
        g.check(ctx["action"])                    # budgets / autonomy / injection
        return ctx
    hooks.register(hooks.ON_TOOL_CALL, _check)
