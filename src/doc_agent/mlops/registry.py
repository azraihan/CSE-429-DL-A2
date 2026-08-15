# =============================================================================
# File:     src/doc_agent/mlops/registry.py
# Layer:    MLOps - model registry
# Status:   STUB - register() raises NotImplementedError
#
# Purpose:
#   Binds a checkpoint to the metrics it achieved, so "the OCR model scores
#   0.94 F1" names a specific, recoverable file rather than a model that existed
#   on someone's machine at some point.
#
# register(component, path, metrics) -> version id
#   Should also capture the corpus version (data/versioning.snapshot()), the git
#   commit, and the config hash - a checkpoint without the data and code that
#   produced it is not reproducible, only retrievable.
#
# Why it is a separate module from tracking.py:
#   Tracking answers "what did we try and what happened"; the registry answers
#   "what do we ship and where is it". A registry entry is the promotion
#   decision, and it is what mlops/monitor.py rolls back to when drift is
#   detected.
#
# Called by: training/train.py and rl/train_rl.py after a successful run.
# =============================================================================

"""MLOps — model registry"""
from __future__ import annotations
from ..contracts import *  # noqa

def register(component: str, path: str, metrics: dict) -> str:
    """Version a checkpoint + its metrics. IMPLEMENT."""
    raise NotImplementedError("MLOps: register")

