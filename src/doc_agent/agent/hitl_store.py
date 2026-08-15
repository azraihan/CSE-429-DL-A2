# =============================================================================
# File:     src/doc_agent/agent/hitl_store.py
# Layer:    Human-in-the-loop - persistent review queue
# Status:   STUB - enqueue(), pending() and resolve() raise NotImplementedError
#
# Purpose:
#   Durable storage behind hitl.py. A review queue held in memory loses every
#   pending item when the service restarts, which silently converts "blocked
#   pending human approval" into "never happened" - the failure mode an
#   oversight mechanism cannot afford. SQLite or an append-only JSON file is
#   sufficient at this scale.
#
# API:
#   enqueue(item) -> id     persist a pending review item, return its handle
#   pending()     -> list   everything awaiting a decision (drives serve/ui.py)
#   resolve(id, decision)   record approve/reject and unblock the caller
#
# Suggested record shape:
#   {id, created_at, reason, context, status: pending|approved|rejected,
#    decided_at, decided_by} - enough to reconstruct who approved what and when,
#   which is what the auditable NFR asks for. Note that context may contain
#   corpus text, so PII redaction (governance/pii.py) should be applied on the
#   way in.
# =============================================================================

"""HITL — persistent review queue (survives restarts)"""
from __future__ import annotations
from ..contracts import *  # noqa

def enqueue(item: dict) -> str:
    """Persist a pending review item; return id. IMPLEMENT (sqlite/json)."""
    raise NotImplementedError("HITL store: enqueue")
def pending() -> list[dict]:
    raise NotImplementedError("HITL store: pending")
def resolve(item_id: str, decision: str) -> None:
    raise NotImplementedError("HITL store: resolve")

