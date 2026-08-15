# =============================================================================
# File:     src/doc_agent/training/adapt.py
# Layer:    Training - affordable adaptation (LoRA / quantization)
# Status:   STUB - apply_lora() and quantize() raise NotImplementedError
#
# Purpose:
#   Makes adapting a foundation model feasible on the hardware actually
#   available. Nougat (vision/ocr.py) is far too large to full-finetune on a
#   student GPU budget; these two techniques are what turn "we could not adapt
#   the model" into "we adapted it for a few hours on one card".
#
# apply_lora(model, cfg)
#   Freezes the base weights and trains small low-rank adapters, cutting
#   trainable parameters by orders of magnitude and shrinking the checkpoint from
#   gigabytes to megabytes - which also makes per-experiment checkpoints cheap
#   enough to keep in the model registry. Rank, alpha, dropout and target modules
#   come from cfg.
#
# quantize(model, cfg)
#   Post-training quantization (int8/4-bit) to cut memory and speed up inference.
#   Serves the latency/cost NFR at serving time; report the accuracy cost
#   alongside the speedup, since a quantized model that loses accuracy on
#   figure-heavy pages is a real regression for this corpus.
#
# Interaction: both apply to the components trained via training/train.py, and
# quantization is typically applied AFTER LoRA merging.
# =============================================================================

"""Stage 8 — affordable adaptation — LoRA / quantization"""
from __future__ import annotations
from ..contracts import *  # noqa

def apply_lora(model, cfg: dict):
    """Wrap a component with LoRA per cfg. IMPLEMENT."""
    raise NotImplementedError("Adapt: LoRA")
def quantize(model, cfg: dict):
    """Post-training quantization per cfg. IMPLEMENT."""
    raise NotImplementedError("Adapt: quantize")

