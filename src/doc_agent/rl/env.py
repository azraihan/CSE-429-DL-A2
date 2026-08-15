# =============================================================================
# File:     src/doc_agent/rl/env.py
# Stage:    7 - Gymnasium environment for tool / retrieval selection
# Status:   STUB - reset() and step() raise NotImplementedError
#
# Purpose:
#   Wraps the agent loop as a standard RL environment so any off-the-shelf
#   algorithm can train the policy without knowing anything about documents.
#
# The MDP:
#   State   - the agent context: the query, observations so far (crucially
#             top_score and the current k), steps taken and budget remaining.
#             The state must contain the evidence-strength numbers, or the policy
#             cannot learn the re-search behaviour that is the point of the
#             exercise.
#   Action  - a choice from tools.REGISTRY, plus "stop".
#   Reward  - task success UNDER BUDGET. Verifiable tasks score via
#             rl/rlvr.verifiable_reward; every step should carry a small negative
#             cost so a policy that retrieves indefinitely is penalised, and a
#             confident wrong answer should score below an abstention - otherwise
#             the policy learns to guess.
#   Episode - one question, ending at "stop", at max_steps, or at a guardrail
#             violation.
#
# Note: keep the environment seeded from cfg["seed"] so training runs are
#       reproducible, and reuse the real Retriever so the learned policy is
#       trained against the same distribution it will be deployed on.
# =============================================================================

"""Stage 7 — Gymnasium env for tool/retrieval selection"""
from __future__ import annotations
from ..contracts import *  # noqa

import gymnasium as gym

class ToolSelectionEnv(gym.Env):
    """State=agent context, Action=tool choice, Reward=task success under budget. IMPLEMENT."""
    def reset(self, *, seed=None, options=None):
        raise NotImplementedError("Stage 7: env.reset")
    def step(self, action):
        raise NotImplementedError("Stage 7: env.step")

