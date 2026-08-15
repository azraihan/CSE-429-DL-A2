# =============================================================================
# File:     scripts/run_index.py
# Layer:    Entry point script
#
# Purpose:
#   Rebuilds the index. Indexing happens inside build_knowledge_base(), so this
#   currently calls the same function as scripts/run_ingest.py; it is kept as a
#   separate entry point for staged runs, where earlier stages are served
#   entirely from the OCR cache.
#
# Usage:   python scripts/run_index.py
# Writes:  data/index/{index.faiss, chunks.jsonl, index_meta.json}
#
# In practice: after the first full run, re-running this is cheap for everything
# except embedding, because vision/ocr.py serves every transcription from
# data/interim/ocr_cache.jsonl. That makes it the right entry point for
# re-chunking or re-embedding experiments - changing chunk_tokens, overlap or the
# embedding model in configs/config.yaml and rebuilding without touching the GPU
# OCR pass.
# =============================================================================

# index is built inside build_knowledge_base; kept for staged runs
from doc_agent import config, pipeline
pipeline.build_knowledge_base(config.load())
