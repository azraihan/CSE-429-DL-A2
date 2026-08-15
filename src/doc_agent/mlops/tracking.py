# =============================================================================
# File:     src/doc_agent/mlops/tracking.py
# Layer:    MLOps - experiment tracking (Weights & Biases)
# Status:   STUB - init_run() and log() raise NotImplementedError
#           (tests/test_structure.py requires init_run to exist by name)
#
# Purpose:
#   Records every run so results are comparable rather than anecdotal. Without
#   it, "the retriever improved" is a claim about two numbers someone remembers;
#   with it, it is a diff between two logged configurations.
#
# API:
#   init_run(cfg, tags)  start a run and log the FULL config, so a result can be
#                        traced back to the exact settings that produced it. Log
#                        alongside it the corpus version from
#                        data/versioning.snapshot() and the git commit - config
#                        alone does not identify a run.
#   log(metrics)         stream metrics during training and evaluation.
#
# Credentials: settings.settings.wandb_api_key, never a literal key in code or
#              in configs/.
#
# Practical note: keep an offline/disabled mode so CI and graders can run the
# pipeline without a W&B account - a hard dependency on a network service turns
# a missing credential into a broken pipeline.
# =============================================================================

"""MLOps — experiment tracking (W&B)"""
from __future__ import annotations
from ..contracts import *  # noqa

def init_run(cfg: dict, tags: list[str]):
    """Start a W&B run; log config. IMPLEMENT."""
    raise NotImplementedError("MLOps: init_run")
def log(metrics: dict) -> None:
    raise NotImplementedError("MLOps: log")

