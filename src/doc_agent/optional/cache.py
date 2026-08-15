# =============================================================================
# File:     src/doc_agent/optional/cache.py
# Layer:    OPTIONAL - embedding / retrieval / answer cache
# Status:   STUB, off by default. Activate for a low-latency NFR; CI does not
#           require an implementation.
#
# Purpose:
#   get(key) / put(key, val) over a keyed store, to skip repeated work at serving
#   time - re-embedding an identical query, re-running retrieval for it, or
#   re-generating an answer already produced.
#
# Note on what is already cached elsewhere:
#   The expensive caching this project actually needed is already implemented
#   where it belonged - vision/ocr.py writes every transcription to
#   data/interim/ocr_cache.jsonl so a killed GPU run resumes, and index/embed.py
#   holds the embedding model in a module global so it loads once. This module is
#   the serving-time layer on top of those, which the current demo-scale
#   deployment does not need.
#
# If implemented: key on (query, k, index version) - a cache that survives a
# corpus rebuild and serves answers from a stale index is worse than no cache.
# =============================================================================

"""OPTIONAL — embedding/retrieval/answer cache
Activate only if your data speciality or NFR requires it (e.g. a low-latency NFR). Off by default; CI does not require impl."""
from __future__ import annotations

def get(key: str): raise NotImplementedError("optional: cache get")
def put(key: str, val) -> None: raise NotImplementedError("optional: cache put")

