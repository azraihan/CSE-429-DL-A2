# =============================================================================
# File:     src/doc_agent/eval/judge.py
# Layer:    Stage 9 - LLM-as-judge
# Status:   STUB - judge() raises NotImplementedError
#
# Purpose:
#   Scores the half of the benchmark that exact match cannot. contracts.Query
#   carries `verifiable` and `judged` precisely to split these: a verifiable
#   question ("what is the reported F1?") is graded by string match in
#   grading_kit/success_check.py, while a judged one (causal, summary, intent)
#   has many correct phrasings and needs a rubric.
#
# judge(query, answer) -> float
#   Applies the JUDGE template from llm/prompts.py through llm/client.py.
#
# Implementation cautions:
#   - Judge the answer against the RETRIEVED EVIDENCE, not the judge model's own
#     knowledge, or the score measures the judge's priors instead of the system.
#   - Use deterministic decoding and record the judge model and prompt version
#     with the scores; an undocumented judge change silently moves every number.
#   - Verifiable questions should never be routed here - keeping the objective
#     subset objective is what anchors the whole evaluation (and RLVR).
# =============================================================================

"""Stage 9 — LLM-as-judge for non-verifiable inference"""
from __future__ import annotations
from ..contracts import *  # noqa

def judge(query: Query, answer: Answer) -> float:
    """Score open-ended answers (causal/summary/intent). IMPLEMENT."""
    raise NotImplementedError("Stage 9: LLM-as-judge")

