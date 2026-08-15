# =============================================================================
# File:     src/doc_agent/rl/train_rl.py
# Stage:    7 - RL / RLVR training loop
# Status:   STUB - train() raises NotImplementedError
#
# Purpose:
#   The entry point that ties Stage 7 together: build ToolSelectionEnv over the
#   TRAIN split, optimise rl/policy.Policy with the algorithm named in
#   cfg["rl"]["algo"], using rl/rlvr.verifiable_reward on the fact tasks.
#
# train(cfg) responsibilities:
#   - seed everything from cfg["seed"] (see scripts/set_seed.py)
#   - train on the train split ONLY; select on val; never touch test. Split
#     isolation is enforced upstream by cfg.ingest.splits and asserted by
#     data/validate.py
#   - log to W&B via mlops/tracking.py and register the resulting checkpoint with
#     its metrics via mlops/registry.py, so the policy that produced a reported
#     number can be recovered
#   - report against the rule-based baseline; a learned policy that does not beat
#     the hand-written branch in agent.decide() is a finding worth stating, not
#     one to bury
# =============================================================================

"""Stage 7 — RL/RLVR training loop"""
from __future__ import annotations
from ..contracts import *  # noqa

def train(cfg: dict) -> None:
    """Train the tool-selection policy (cfg['rl']['algo']); RLVR on fact tasks. IMPLEMENT."""
    raise NotImplementedError("Stage 7: RL training")

