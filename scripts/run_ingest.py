# =============================================================================
# File:     scripts/run_ingest.py
# Layer:    Entry point script
#
# Purpose:
#   Runs the full offline path - ingest, layout, OCR, chunk, embed, index - by
#   calling pipeline.build_knowledge_base(config.load()).
#
# Usage:   python scripts/run_ingest.py
# Reads:   configs/config.yaml, data/raw/
# Writes:  data/interim/ocr_cache.jsonl, data/index/
#
# Prerequisite: bash scripts/get_data.sh must have built data/raw/ first;
# loader.load_pages() raises a message naming that script if the manifest is
# missing.
#
# Note: this is the expensive one. OCR generation dominates the runtime, so this
# wants a GPU - though the resume cache in vision/ocr.py means an interrupted run
# picks up where it stopped rather than starting over.
# =============================================================================

from doc_agent import config, pipeline
pipeline.build_knowledge_base(config.load())
