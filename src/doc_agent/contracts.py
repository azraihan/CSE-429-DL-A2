# =============================================================================
# File:     src/doc_agent/contracts.py
# Layer:    Cross-stage data contracts
# Status:   FIXED — fields and types are locked; CI (tests/test_structure.py)
#           fails if any model or field is renamed, removed or retyped.
#
# Purpose:
#   The single vocabulary every stage speaks. Stage N hands Stage N+1 one of
#   these pydantic models and nothing else, which is what lets the stages be
#   developed, tested and swapped independently.
#
# The models, in pipeline order:
#   Page       (id, image_path, doc_id)          - Stage 1 ingest output
#   Region     (page_id, bbox, kind)             - Stage 2 layout output
#   Chunk      (id, doc_id, text, page_ids,      - Stage 3/4 text unit; `score`
#               score)                             is filled by Stage 5 retrieval
#   Query      (text, verifiable, judged)        - an eval task; `verifiable`
#                                                  anchors exact-match scoring
#                                                  and RLVR, `judged` routes to
#                                                  the LLM judge
#   Citation   (chunk_id, span)                  - a pointer back into evidence
#   Answer     (text, citations, grounded,       - Stage 6 output; `grounded`
#               confidence)                        and `confidence` carry the
#                                                  no-hallucination and
#                                                  calibration NFRs
#   ToolResult (ok, payload)                     - uniform tool return type
#   TraceStep  (step, tool, args, obs)           - one line of traces/run.jsonl
#
# Why the sidecars exist:
#   Because these models are frozen, per-page and per-region extras live in
#   module-level sidecar dicts keyed by id - PAGE_META in ingest/loader.py and
#   REGION_META in vision/layout.py - rather than as new fields here.
#
# Mandatory agentic behaviour (graded in A3):
#   Chunk.score is the hinge. agent.decide() reads the top score, and when the
#   evidence is weak it re-retrieves at a wider k instead of answering. That
#   runtime branch on an observed number is what makes this an agent rather
#   than a fixed retrieve-then-answer chain.
# =============================================================================

"""FIXED data contracts. Do not change fields or types."""
from __future__ import annotations
from pydantic import BaseModel

class Page(BaseModel):
    id: str
    image_path: str
    doc_id: str

class Region(BaseModel):
    page_id: str
    bbox: tuple[int, int, int, int]
    kind: str  # text | table | figure | heading

class Chunk(BaseModel):
    id: str
    doc_id: str
    text: str
    page_ids: list[str]
    score: float = 0.0        # relevance score set by retrieval; decide() reads the top score to judge weak evidence

class Query(BaseModel):
    text: str
    verifiable: bool          # True = checkable by exact match (anchors objective grading + RLVR)
    judged: bool              # True = scored by LLM-judge / human (non-verifiable inference)

class Citation(BaseModel):
    chunk_id: str
    span: tuple[int, int]

class Answer(BaseModel):
    text: str
    citations: list[Citation]
    grounded: bool
    confidence: float

class ToolResult(BaseModel):
    ok: bool
    payload: dict


class TraceStep(BaseModel):
    """One agent step, emitted to traces/run.jsonl so the A3 agentic-feature check can read the path."""
    step: int
    tool: str                 # tool name, or "decide" / "answer"
    args: dict                # e.g. {"query": "..."} — for retrieve, the query actually used
    obs: dict                 # what decide() saw, e.g. {"top_score": 0.31, "n": 10}

# MANDATORY agentic behaviour (graded in A3): evidence-gated re-search — decide() must re-retrieve with a
# reformulated query when the top evidence is weak. That runtime branch is what makes the system an agent.
# (multi-hop -> recall NFR, verify-and-correct -> precision NFR, tool-routing -> bonus; see the codebase guide.)

