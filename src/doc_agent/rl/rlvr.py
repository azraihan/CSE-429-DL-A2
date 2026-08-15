# =============================================================================
# File:     src/doc_agent/rl/rlvr.py
# Stage:    7 - RLVR (reinforcement learning from verifiable rewards)
# Status:   STUB - verifiable_reward() raises NotImplementedError
#
# Purpose:
#   The reward signal that needs no human and no judge model. For the subset of
#   the benchmark where contracts.Query.verifiable is True, correctness is
#   decidable by exact match against the gold extraction: +1 if the prediction
#   matches, 0 otherwise. That objectivity is the whole point - it removes reward
#   hacking against a learned reward model and gives GRPO/PPO a signal that
#   cannot drift.
#
# verifiable_reward(prediction, gold) -> float
#
# Implementation notes:
#   - Normalise both sides before comparing (case, whitespace, unit formatting) -
#     eval/metrics.normalize_text is the obvious shared basis - but keep the
#     comparison EXACT after normalisation. A fuzzy "verifiable" reward is no
#     longer verifiable.
#   - Judged (non-verifiable) questions must not be routed here; they belong to
#     eval/judge.py. Mixing them reintroduces exactly the subjectivity RLVR
#     avoids.
#   - Pairs naturally with the `extract` tool in agent/tools.py, which produces
#     the field values this scores.
# =============================================================================

"""Stage 7 — RLVR — verifiable reward on extraction accuracy"""
from __future__ import annotations
from ..contracts import *  # noqa

def verifiable_reward(prediction, gold) -> float:
    """+1 if extraction exactly matches gold, else 0. Drives RLVR/GRPO. IMPLEMENT."""
    raise NotImplementedError("Stage 7: verifiable reward")

