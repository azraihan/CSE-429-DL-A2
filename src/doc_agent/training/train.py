# =============================================================================
# File:     src/doc_agent/training/train.py
# Layer:    Training - unified entry point
# Status:   STUB - main() raises NotImplementedError
#
# Purpose:
#   One command trains any component: main(component, cfg) selects the
#   LightningModule, builds the DocDataModule, and runs a SEEDED Lightning
#   Trainer with a W&B logger.
#
# Why unified rather than one script per component:
#   Seeding, checkpoint naming, split handling, logging and the eventual
#   registry entry are identical concerns for the enhancer, the OCR reader and
#   the retriever. Three separate scripts means three places for those to drift,
#   and drift here is what makes a reported result impossible to reproduce.
#
# main(component, cfg) should:
#   - seed everything from cfg["seed"] (scripts/set_seed.py sets the global,
#     deterministic-algorithm state)
#   - build the datamodule and the LitComponent for `component`
#   - init the W&B run through mlops/tracking.init_run(cfg, tags=[component])
#   - train, checkpoint on the val metric
#   - register the checkpoint and its metrics via mlops/registry.register(), so
#     every number in the report points to a recoverable artifact
# =============================================================================

"""Training — unified entrypoint"""
from __future__ import annotations
from ..contracts import *  # noqa

def main(component: str, cfg: dict) -> None:
    """Train one component with a seeded Lightning Trainer + W&B logger. IMPLEMENT."""
    raise NotImplementedError("Training: main")

