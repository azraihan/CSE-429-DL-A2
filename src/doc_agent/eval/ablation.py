# =============================================================================
# File:     src/doc_agent/eval/ablation.py
# Layer:    Stage 9 - ablation harness
# Status:   STUB - run() raises NotImplementedError
#
# Purpose:
#   Attributes the headline number to the parts that earned it. Every stage in
#   this pipeline was a design decision; an ablation is the evidence that each
#   one pays for itself, and it is what distinguishes a justified architecture
#   from an accumulated one.
#
# run(cfg) -> {variant: {metric: delta}}
#   Toggle one stage off at a time, re-run evaluation, report the change.
#
# The ablations that matter most here, each tied to a decision defended
# elsewhere in the codebase:
#   region_aware chunking off   (index/chunk.py)      - does keeping region
#                               boundaries actually help, or would flat windows do
#   figure/table region passes off (vision/ocr.py)    - the 56.1% figure-evidence
#                               claim stands or falls on this
#   use_dataset_bboxes off      (vision/layout.py)    - heuristics alone vs
#                               annotations + heuristics
#   evidence-gated re-search off (agent/agent.py)     - fixed retrieve->answer
#                               vs the agentic branch; this is the A3 claim
#   rerank off                  (retrieval/rerank.py)
#   BGE query prefix off        (index/embed.py)      - the recall cost quantified
#
# Implementation note: vary ONE key of cfg per run, keep the seed fixed, and
# stamp each result with the corpus version from data/versioning.py.
# =============================================================================

"""Stage 9 — ablation harness"""
from __future__ import annotations
from ..contracts import *  # noqa

def run(cfg: dict) -> dict:
    """Toggle each stage off; report metric deltas. IMPLEMENT."""
    raise NotImplementedError("Stage 9: ablation")

