# =============================================================================
# File:     src/doc_agent/serve/ui.py
# Stage:    8 - Gradio demo
# Status:   STUB - launch() raises NotImplementedError
#
# Purpose:
#   The human-facing demo over /answer. For a grounded document agent the UI is
#   not decoration: the claim being demonstrated is "this answer is supported by
#   this evidence", and that is only checkable if the interface SHOWS the
#   evidence.
#
# What launch(cfg) should surface:
#   - the answer text, with its confidence
#   - the citations, resolved back to page images with the cited region
#     highlighted (REGION_META in vision/layout.py holds the box geometry)
#   - the abstention case shown honestly as "insufficient evidence" rather than
#     as an empty answer
#   - optionally the trace from traces/run.jsonl, so the re-search branch is
#     visible - it is the most direct demonstration of the agentic behaviour
#   - the HITL review queue from agent/hitl.py, where a human resolves escalated
#     items
#
# Keep it a thin client over pipeline.answer()/the API, so the demo and the
# evaluated system stay the same system.
# =============================================================================

"""Stage 8 — Gradio demo"""
from __future__ import annotations
from ..contracts import *  # noqa

def launch(cfg: dict) -> None:
    """Gradio UI over /answer. IMPLEMENT."""
    raise NotImplementedError("Stage 8: Gradio UI")

