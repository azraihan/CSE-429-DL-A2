# =============================================================================
# File:     src/doc_agent/training/datamodule.py
# Layer:    Training - Lightning DataModule
# Status:   STUB - setup() raises NotImplementedError
#
# Purpose:
#   Owns everything about data loading for training: which examples are in which
#   split, how they are batched, and what transforms apply.
#
# The one rule that must not be broken - SPLIT BY DOCUMENT:
#   Pages from the same paper are near-duplicates of one another (shared
#   template, shared notation, repeated phrasing). Splitting by PAGE puts pages
#   of one paper in both train and test and inflates every reported number. A1
#   named this as the single most likely leak in the project. Splits are assigned
#   per doc_id and inherited by every page, and data/validate.py asserts the
#   property holds - setup() must read those existing assignments (PAGE_META
#   "split") rather than re-deriving its own.
#
# setup(stage) should build train/val/test datasets from the manifest, apply
# augmentation on the train split only, and keep the val split fixed so
# model selection and calibration (eval/calibration.py) are comparable across
# runs.
# =============================================================================

"""Training — Lightning datamodule"""
from __future__ import annotations
from ..contracts import *  # noqa

import lightning as L

class DocDataModule(L.LightningDataModule):
    def setup(self, stage: str | None = None) -> None:
        raise NotImplementedError("Training: datamodule.setup (split by document)")

