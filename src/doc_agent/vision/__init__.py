# =============================================================================
# File:     src/doc_agent/vision/__init__.py
# Layer:    Stages 2-3 - vision package marker
#
# Contains:
#   layout.py  Stage 2 - region detection and, critically, READING ORDER
#              (multi-column resolution + figure/table boxes). Owns REGION_META.
#   ocr.py     Stage 3 - Nougat transcription of full pages and of figure/table
#              crops, with a repetition guard and a disk resume cache.
#
# These two carry the project's data speciality: this corpus is 42.5% two-column
# and 56.1% of its questions have evidence inside a figure or table, so getting
# order and region isolation right here is what makes retrieval possible later.
# =============================================================================

