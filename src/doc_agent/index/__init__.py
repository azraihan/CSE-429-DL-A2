# =============================================================================
# File:     src/doc_agent/index/__init__.py
# Layer:    Stage 4 - indexing package marker
#
# Contains:
#   chunk.py  region-aware re-chunking of OCR output into retrievable units
#   embed.py  sentence-embedding model loading and encoding (query/passage aware)
#   store.py  FAISS index build/load plus the chunk and metadata sidecars
#
# The three run in that order inside pipeline.build_knowledge_base() and their
# combined output is data/index/, the only artifact answer() needs at runtime.
# =============================================================================

