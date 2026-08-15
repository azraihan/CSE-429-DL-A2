# =============================================================================
# File:     src/doc_agent/training/lit_modules.py
# Layer:    Training - LightningModules per trainable component
# Status:   STUB - training_step() and configure_optimizers() raise
#           NotImplementedError
#
# Purpose:
#   LitComponent wraps whichever component is being trained - the Stage 1
#   enhancer, the Stage 3 OCR reader, or the retriever's embedding model - behind
#   one Lightning interface. The training loop, checkpointing, mixed precision
#   and distributed handling are then written once in training/train.py rather
#   than reimplemented per component.
#
# To implement:
#   training_step(batch, idx)   the component's loss; log it so the W&B curves in
#                               mlops/tracking.py are comparable across runs
#   configure_optimizers()      optimizer, learning rate and schedule read FROM
#                               cfg, never hard-coded - the reproducibility gate
#                               requires that a run be reconstructable from its
#                               config alone
#   validation_step()           worth adding, reporting the same metric the
#                               eval stage reports, so model selection optimises
#                               the number that is finally published
# =============================================================================

"""Training — Lightning modules per trainable component"""
from __future__ import annotations
from ..contracts import *  # noqa

import lightning as L

class LitComponent(L.LightningModule):
    """Wrap enhancer / OCR / retriever training. IMPLEMENT training_step + configure_optimizers."""
    def training_step(self, batch, idx):
        raise NotImplementedError("Training: training_step")
    def configure_optimizers(self):
        raise NotImplementedError("Training: optimizer + LR schedule (from cfg)")

