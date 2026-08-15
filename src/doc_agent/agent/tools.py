# =============================================================================
# File:     src/doc_agent/agent/tools.py
# Stage:    6 - the tool interface
# Status:   FIXED interface / STUB bodies - names and signatures are LOCKED
#           (tests/test_structure.py and tests/test_tools.py assert the exact
#           set of nine names and that each is a Tool subclass).
#
# Purpose:
#   Everything the agent is allowed to do, expressed as one uniform interface.
#   Tool.__call__ always returns a contracts.ToolResult(ok, payload), so the
#   loop in agent.py can dispatch, log, guard and record any tool identically
#   without knowing what it does.
#
# The nine tools:
#   retrieve(query, k)            dense search (Stage 5). MUST return payload
#                                 {"chunk_ids": [...], "top_score": <best score>,
#                                 "k": k} - decide() branches on top_score and
#                                 traces/run.jsonl reads it to prove the
#                                 evidence-gated re-search actually happened.
#   rerank(query, candidates)     cross-encoder reordering (retrieval/rerank.py)
#   read_page(page_id)            fetch a full page's text - the multi-hop move
#   enhance_page(page_id)         re-run restoration on a poor page (Stage 1)
#   extract(field, chunk_id)      pull one structured field from evidence; this
#                                 is the tool RLVR's verifiable reward scores
#   aggregate(op, items)          count / sum / compare across extractions
#   cite(chunk_id, span)          emit a contracts.Citation
#   calculator(expr)              arithmetic, so numeric answers are computed
#                                 rather than generated
#   escalate_to_human(reason,     hand off to the HITL queue (agent/hitl.py)
#                     context)
#
# REGISTRY:
#   The list act() dispatches through. Adding a tool means adding it here AND
#   updating the locked name set in tests/test_structure.py.
#
# TODO: every __call__ currently raises NotImplementedError.
# =============================================================================

"""Stage 6 — FIXED tool interface — the agent's tools"""
from __future__ import annotations
from ..contracts import *  # noqa

from abc import ABC, abstractmethod

class Tool(ABC):
    name: str
    @abstractmethod
    def __call__(self, **kwargs) -> ToolResult: ...

# FIXED tool set — names & signatures locked (test_tools.py checks these).
class Retrieve(Tool):
    name = "retrieve"
    def __call__(self, query: str, k: int = 10) -> ToolResult:
        # IMPLEMENT: run the retriever; return ToolResult(ok=True, payload={"chunk_ids": [...],
        #   "top_score": <best chunk score>, "k": k}) so decide() and traces/run.jsonl can read evidence strength.
        raise NotImplementedError

class Rerank(Tool):
    name = "rerank"
    def __call__(self, query: str, candidates: list) -> ToolResult:
        raise NotImplementedError

class ReadPage(Tool):
    name = "read_page"
    def __call__(self, page_id: str) -> ToolResult:
        raise NotImplementedError

class EnhancePage(Tool):
    name = "enhance_page"
    def __call__(self, page_id: str) -> ToolResult:
        raise NotImplementedError

class Extract(Tool):
    name = "extract"
    def __call__(self, field: str, chunk_id: str) -> ToolResult:
        raise NotImplementedError

class Aggregate(Tool):
    name = "aggregate"
    def __call__(self, op: str, items: list) -> ToolResult:
        raise NotImplementedError

class Cite(Tool):
    name = "cite"
    def __call__(self, chunk_id: str, span: tuple) -> ToolResult:
        raise NotImplementedError

class Calculator(Tool):
    name = "calculator"
    def __call__(self, expr: str) -> ToolResult:
        raise NotImplementedError

class EscalateToHuman(Tool):     # HITL entry
    name = "escalate_to_human"
    def __call__(self, reason: str, context: dict) -> ToolResult:
        raise NotImplementedError

REGISTRY = [Retrieve, Rerank, ReadPage, EnhancePage, Extract,
            Aggregate, Cite, Calculator, EscalateToHuman]

