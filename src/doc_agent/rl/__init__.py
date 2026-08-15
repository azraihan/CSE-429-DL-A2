# =============================================================================
# File:     src/doc_agent/rl/__init__.py
# Layer:    Stage 7 - reinforcement learning package marker
#
# Contains:
#   env.py       Gymnasium environment wrapping the agent loop
#   policy.py    the learned tool-selection policy
#   rlvr.py      RLVR - verifiable reward on extraction accuracy
#   train_rl.py  the training entry point
#
# What this stage is for: agent.decide() can be a hand-written rule (the
# baseline) or a LEARNED policy. This package is the learned arm - it optimises
# which tool to call and when to stop, under a step/cost budget.
# =============================================================================

