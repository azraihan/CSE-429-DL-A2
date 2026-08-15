# =============================================================================
# File:     src/doc_agent/retrieval/retriever.py
# Stage:    5 - dense retrieval
# Status:   IMPLEMENTED
#
# Purpose:
#   Question -> the k most relevant chunks, and - just as importantly - a NUMBER
#   saying how good that evidence is. The second half is what makes the agent
#   agentic.
#
# class Retriever:
#   __init__(cfg)  keeps cfg["retrieve"] and the full cfg (embedding needs it);
#                  the index is NOT loaded here.
#   _load()        lazy, once: store.load() brings in the FAISS index, the chunk
#                  list and the build metadata. Lazy so constructing a Retriever
#                  is free in tests and so a missing index fails at first use
#                  with a clear message.
#   retrieve(q, k) encodes the query with is_query=True (BGE prefix - see
#                  embed.py), searches, and returns list[Chunk] with .score set.
#                  Each result is a COPY of the stored chunk, so a cached chunk
#                  never carries a stale score from an earlier query - a subtle
#                  bug that would make is_weak() read the wrong number.
#                  k is clamped to the corpus size; negative FAISS ids (padding
#                  when k exceeds available vectors) are skipped.
#
# Evidence-strength policy - read by agent.decide():
#   top_score(chunks)   best chunk score, 0.0 for an empty result
#   is_weak(chunks,cfg) True when the best score is below
#                       cfg["retrieve"]["weak_threshold"]
#   next_k(k, cfg)      k + k_step, or None once that would exceed k_max
#
#   These three encode the MANDATORY agentic behaviour graded in A3:
#     retrieve at k -> if weak, widen to next_k and retrieve AGAIN -> if still
#     weak at k_max, ABSTAIN ("insufficient evidence"). The policy is fail-closed
#     - running out of widening room produces an abstention, never a guess - and
#     it is deliberately kept here rather than inside the agent so the numeric
#     rule can be unit-tested without an LLM.
#
# Config  : cfg["retrieve"] -> k, weak_threshold, k_step, k_max, rerank
# =============================================================================

"""Stage 5 — dense retrieval"""

from __future__ import annotations

from ..contracts import *  # noqa
from ..contracts import Chunk  # explicit: keeps the star import from hiding the name
from ..index import embed, store
from ..logging_conf import get_logger

log = get_logger(__name__)


class Retriever:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg["retrieve"]
        self._full = cfg
        self._index = None
        self._chunks: list[Chunk] = []  # noqa: F405
        self.meta: dict = {}

    def _load(self) -> None:
        if self._index is None:
            self._index, self._chunks, self.meta = store.load(self._full)
            log.info("retriever: %d chunks loaded", len(self._chunks))

    def retrieve(self, query: str, k: int | None = None) -> list[Chunk]:
        """Top-k dense retrieval. Sets chunk.score on every result so decide() can judge
        whether the evidence is weak."""
        self._load()
        assert self._index is not None
        k = int(k or self.cfg.get("k", 10))
        qv = embed.encode_texts([query], self._full, is_query=True)
        scores, ids = self._index.search(qv, min(k, len(self._chunks)))

        out: list[Chunk] = []  # noqa: F405
        for score, idx in zip(scores[0], ids[0], strict=False):
            if idx < 0:
                continue
            src = self._chunks[int(idx)]
            # copy, so a cached chunk never carries a stale score from an earlier query
            out.append(
                Chunk(  # noqa: F405
                    id=src.id,
                    doc_id=src.doc_id,
                    text=src.text,
                    page_ids=list(src.page_ids),
                    score=float(score),
                )
            )
        return out


# --- evidence-strength policy: read by agent.decide() for evidence-gated re-search ---
def top_score(chunks: list[Chunk]) -> float:
    """Strength of the current evidence = best chunk score (0.0 if empty)."""
    return max((c.score for c in chunks), default=0.0)


def is_weak(chunks: list[Chunk], cfg: dict) -> bool:
    """Weak evidence = best score below cfg.retrieve.weak_threshold."""
    return top_score(chunks) < cfg["retrieve"]["weak_threshold"]


def next_k(k: int, cfg: dict) -> int | None:
    """Widen the net: k + k_step, or None once it would exceed k_max (signal to ABSTAIN)."""
    nk = k + cfg["retrieve"]["k_step"]
    return nk if nk <= cfg["retrieve"]["k_max"] else None
