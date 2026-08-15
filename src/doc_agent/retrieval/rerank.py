# =============================================================================
# File:     src/doc_agent/retrieval/rerank.py
# Stage:    5 - reranking
# Status:   STUB - rerank() raises NotImplementedError
#
# Purpose:
#   Second-stage precision. The bi-encoder in embed.py scores query and chunk
#   independently, which is what makes indexing the whole corpus affordable but
#   also what limits its precision. A cross-encoder reads the query and the
#   candidate TOGETHER and reorders a short list, typically recovering several
#   points of top-1 accuracy for the cost of one forward pass per candidate.
#
# Intended contract:
#   rerank(query, candidates, cfg) -> list[Chunk] reordered by cross-encoder
#   score, gated on cfg["retrieve"]["rerank"]. Returning Chunks with .score
#   overwritten by the new score matters: agent.decide() reads top_score(), so a
#   reranked score must be on the same scale as weak_threshold, or the
#   re-search gate will misfire.
#
# Where it fits:
#   Retriever.retrieve() widens k, this narrows it again - retrieve k=50, rerank,
#   keep 10. It is also the natural implementation of the `rerank` tool in
#   agent/tools.py.
# =============================================================================

"""Stage 5 — reranking"""
from __future__ import annotations
from ..contracts import *  # noqa

def rerank(query: str, candidates: list[Chunk], cfg: dict) -> list[Chunk]:
    """Cross-encoder rerank if cfg['retrieve']['rerank']. IMPLEMENT."""
    raise NotImplementedError("Stage 5: rerank")

