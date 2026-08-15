# =============================================================================
# File:     src/doc_agent/rl/policy.py
# Stage:    7 - policy network
# Status:   STUB - Policy.act() raises NotImplementedError
#
# Purpose:
#   The learned replacement for the hand-written branch in agent.decide().
#   Policy.act(state) -> the same action dict the agent loop already consumes
#   ({"tool": ..., ...}), so the rule-based baseline and the learned policy are
#   interchangeable at the call site and can be compared directly in the
#   ablation harness.
#
# Structure:
#   Policy(cfg) reads cfg["rl"] (algorithm, network shape, checkpoint path).
#
# Implementation notes:
#   - The action space is small and the state is low-dimensional (query features,
#     top_score, k, step count, budget left), so a small MLP is appropriate; the
#     interesting behaviour is in the reward design, not the architecture.
#   - Mask actions the guardrails would reject rather than letting the policy
#     learn to avoid them the slow way.
#   - act() must remain deterministic at evaluation time for the reproducibility
#     gate.
# =============================================================================

"""Stage 7 — policy network"""
from __future__ import annotations
from ..contracts import *  # noqa

class Policy:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg["rl"]
    def act(self, state) -> dict:
        raise NotImplementedError("Stage 7: policy.act")

