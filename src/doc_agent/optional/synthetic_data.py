# =============================================================================
# File:     src/doc_agent/optional/synthetic_data.py
# Layer:    OPTIONAL - synthetic text-line generation for tiny-label training
# Status:   STUB, off by default. Activate for a data-efficient / tiny-label
#           project; CI does not require an implementation.
#
# Purpose:
#   generate(cfg) renders synthetic text lines with known ground truth - varied
#   fonts, spacing and degradation - to train or fine-tune a recogniser when
#   real transcriptions are scarce. The appeal is that labels are free and exact
#   by construction.
#
# Why it is not needed here:
#   This project's OCR baseline is Nougat, already pretrained on arXiv page
#   images, and the corpus ships with a PDF text layer that serves as ground
#   truth for measuring CER/WER (eval/metrics.py). There is no label scarcity to
#   solve, and synthetic lines would not reproduce the property that actually
#   matters on this data - two-column layout and figure/table structure, which is
#   a PAGE-level phenomenon, not a line-level one.
#
# The closer analogue that IS used: preprocess._degrade(), which manufactures
# degraded copies of real pages for robustness measurement.
# =============================================================================

"""OPTIONAL — generate synthetic text-lines for tiny-label training
Activate only if your data speciality or NFR requires it (e.g. a tiny-label / data-efficient project). Off by default; CI does not require impl."""
from __future__ import annotations

def generate(cfg: dict) -> list:
    raise NotImplementedError("optional: synthetic data")

