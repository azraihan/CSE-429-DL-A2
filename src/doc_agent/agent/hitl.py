# =============================================================================
# File:     src/doc_agent/agent/hitl.py
# Layer:    Human-in-the-loop - escalation entry point
# Status:   STUB - escalate() and review_queue() raise NotImplementedError
#
# Purpose:
#   The system's answer to "what happens when the agent should not decide alone".
#   Reached two ways: the agent calls the escalate_to_human tool deliberately
#   (low confidence, conflicting evidence, an action above its autonomy level),
#   or guardrails.check() diverts a blocked action here instead of executing it.
#
# API:
#   escalate(reason, context) -> ToolResult
#       Queue the item for human review and BLOCK the action until a reviewer
#       approves. Blocking is the point - an escalation that files a ticket and
#       proceeds anyway provides oversight in name only.
#   review_queue() -> pending items for the reviewer UI (serve/ui.py).
#
# Split of responsibility:
#   This module is the policy - when to escalate and what blocking means.
#   Persistence lives in hitl_store.py, so a pending review survives a restart.
# =============================================================================

"""HITL — human-in-the-loop review queue"""
from __future__ import annotations
from ..contracts import *  # noqa

def escalate(reason: str, context: dict) -> ToolResult:
    """Queue for human review; block action until approved. IMPLEMENT."""
    raise NotImplementedError("HITL: escalate_to_human")

def review_queue():
    """Return pending items for the reviewer UI. IMPLEMENT."""
    raise NotImplementedError("HITL: review queue")

