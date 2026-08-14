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
