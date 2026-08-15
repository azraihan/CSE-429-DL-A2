# =============================================================================
# File:     src/doc_agent/llm/client.py
# Layer:    LLM - the single call wrapper
# Status:   STUB - LLM.complete() raises NotImplementedError
#
# Purpose:
#   Every model call in the system goes through this one class. That constraint
#   is what makes it possible to add retries, timeouts, token accounting, cost
#   tracking, caching and request logging in ONE place - and it is what lets
#   guardrails enforce a cost budget at all, since there is a single point where
#   spend is observable.
#
# Structure:
#   LLM(cfg)              model and decoding parameters from cfg["agent"];
#                         credentials from settings.settings, never from
#                         os.environ here and never from configs/.
#   complete(prompt, **kw) -> str
#
# Callers: agent.decide/synthesize (via llm/prompts.py), eval/judge.py.
#
# Implementation notes:
#   - Keep prompts out of this file; they belong in prompts.py.
#   - Report failures rather than returning empty text: a silent "" would flow
#     into synthesize() and be indistinguishable from a genuine abstention.
#   - Deterministic decoding (temperature 0) for anything the reproducibility
#     gate re-runs.
# =============================================================================

"""LLM — the single LLM call wrapper (all model calls go through here)"""
from __future__ import annotations
from ..contracts import *  # noqa

class LLM:
    """Model set by cfg['agent']. Key from settings. IMPLEMENT complete()."""
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
    def complete(self, prompt: str, **kw) -> str:
        raise NotImplementedError("LLM: complete")

