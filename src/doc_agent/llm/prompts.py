# =============================================================================
# File:     src/doc_agent/llm/prompts.py
# Layer:    LLM - prompt template registry
# Status:   STUB - all three templates are placeholder strings
#
# Purpose:
#   FIXED home for every prompt in the system. Prompts are behaviour: scattering
#   them through agent.py, judge.py and postprocess.py would mean the system's
#   actual instructions could not be reviewed, diffed or version-controlled as a
#   unit. One file, one place to audit.
#
# Templates:
#   DECIDE     - tool selection. Given the query, the observations so far and the
#                available tools, choose the next action. Must be able to emit
#                "stop", and must present retrieved text as DATA, clearly
#                delimited from instructions (the injection defence in
#                guardrails.py depends on this framing holding).
#   SYNTHESIZE - the grounded-answer prompt. Must force inline citations to
#                chunk ids and must make abstention an explicit, allowed output
#                ("insufficient evidence"), because postprocess.py's gate can
#                only pass what the prompt permits the model to say.
#   JUDGE      - the LLM-as-judge rubric for non-verifiable, open-ended answers
#                (causal / summary / intent), used by eval/judge.py.
#
# Note: tests/test_structure.py requires SYNTHESIZE to exist by name.
# =============================================================================

"""LLM — FIXED prompt template registry (all prompts live here)"""
from __future__ import annotations
from ..contracts import *  # noqa

# Fill the template bodies; do NOT scatter prompt strings elsewhere.
DECIDE = "IMPLEMENT: tool-selection prompt"
SYNTHESIZE = "IMPLEMENT: grounded-answer prompt (must force citations + abstention)"
JUDGE = "IMPLEMENT: LLM-as-judge prompt for open-ended inference"

