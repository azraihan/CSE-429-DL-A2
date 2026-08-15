# =============================================================================
# File:     src/doc_agent/agent/__init__.py
# Layer:    Stage 6 - agent package marker
#
# Contains:
#   agent.py       the FIXED perceive->decide->act->observe loop
#   tools.py       the locked tool interface and REGISTRY
#   memory.py      working / episodic memory across steps
#   guardrails.py  autonomy, budget and prompt-injection enforcement (ON_TOOL_CALL)
#   hitl.py        human-in-the-loop escalation
#   hitl_store.py  the persistent review queue behind it
# =============================================================================

