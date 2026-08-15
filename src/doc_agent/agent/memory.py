# =============================================================================
# File:     src/doc_agent/agent/memory.py
# Stage:    6 - working / episodic memory
# Status:   PARTIAL - add() works; recall() is a STUB.
#
# Purpose:
#   What the agent carries across steps within a run. Agent.run() appends every
#   ToolResult here, so step 3 can reason over what steps 1 and 2 observed -
#   without it, each iteration would start blind and multi-hop questions would
#   be impossible.
#
# API:
#   add(item)        append an observation (called by the loop, already working)
#   recall(query)    IMPLEMENT: return the items relevant to `query` rather than
#                    the whole history. This matters once the history exceeds the
#                    context budget: naive concatenation both blows the budget and
#                    buries the useful observation among irrelevant ones. A small
#                    embedding-similarity or recency+overlap ranking over
#                    self.items is enough here.
#
# Scope note:
#   This is WORKING memory - per-run, in-process, discarded when run() returns.
#   Persistent state across runs lives in agent/hitl_store.py (review queue) and
#   data/index/ (the knowledge base).
# =============================================================================

"""Stage 6 — working/episodic memory"""
from __future__ import annotations
from ..contracts import *  # noqa

class Memory:
    def __init__(self) -> None:
        self.items: list = []
    def add(self, item) -> None:
        self.items.append(item)
    def recall(self, query: str) -> list:
        raise NotImplementedError("Stage 6: memory recall")

