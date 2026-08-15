# =============================================================================
# File:     src/doc_agent/ingest/__init__.py
# Layer:    Stage 1 - ingest package marker
#
# Contains:
#   loader.py      data/raw/manifest.jsonl -> list[Page] (+ PAGE_META sidecar)
#   preprocess.py  contract enforcement (greyscale, geometry) and the optional
#                  synthetic degradation used for robustness testing
#   enhance.py     optional generative restoration (VAE / diffusion), off by
#                  default because this corpus is born-digital
#
# Intentionally empty: the package exposes nothing itself, so importers name the
# module they need (from ..ingest.loader import PAGE_META) and the dependency is
# visible at the import line.
# =============================================================================

