# =============================================================================
# File:     src/doc_agent/ingest/enhance.py
# Stage:    1 - ENHANCEMENT (generative restoration of degraded scans)
# Status:   STUB - Enhancer.train() and Enhancer.apply() raise NotImplementedError
#
# Purpose:
#   The generative-model slot in the pipeline: a VAE or diffusion model that
#   denoises / super-resolves a degraded page image before it reaches layout
#   detection and OCR, so a poor scan does not silently cap end-to-end accuracy.
#
# Structure:
#   Enhancer(cfg)   reads cfg["enhance"]; train() fits on the corpus, apply()
#                   maps list[Page] -> list[Page] of restored pages.
#   run(pages, cfg) the pipeline-facing wrapper. Returns pages unchanged when
#                   cfg["enhance"]["enabled"] is false, which is the default -
#                   this corpus is born-digital, so there is nothing to restore
#                   unless preprocess ran with degrade=True.
#
# Where it earns its place:
#   Paired with cfg.ingest.degrade, this is the measurable arm of the robustness
#   story: degrade a clean page, restore it, and compare OCR CER/WER against the
#   clean original (eval/metrics.py, eval/robustness.py).
#
# TODO:
#   Implement train() and apply(); keep the enabled flag so the clean-corpus
#   path stays a no-op and the pipeline cost does not change by default.
# =============================================================================

"""Stage 1 — ENHANCEMENT (VAE / diffusion) — generative denoise / super-resolution of degraded scans"""
from __future__ import annotations
from ..contracts import *  # noqa

class Enhancer:
    """Model set by cfg['enhance']. IMPLEMENT train() and apply()."""
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg["enhance"]
    def train(self, pages: list[Page]) -> None:
        raise NotImplementedError("Stage 1: train VAE/diffusion enhancer")
    def apply(self, pages: list[Page]) -> list[Page]:
        raise NotImplementedError("Stage 1: apply enhancer")

def run(pages: list[Page], cfg: dict) -> list[Page]:
    if not cfg["enhance"]["enabled"]:
        return pages
    return Enhancer(cfg).apply(pages)

