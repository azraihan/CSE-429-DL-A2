# =============================================================================
# File:     src/doc_agent/index/embed.py
# Stage:    4 - embed chunks
# Status:   IMPLEMENTED
#
# Purpose:
#   Maps text to the dense vectors the FAISS index stores and searches. Used on
#   BOTH sides: once offline over every chunk, and once per query at retrieval
#   time - which is why the query/passage asymmetry below lives here rather than
#   in the retriever.
#
# Functions:
#   get_model(cfg)   Loads the SentenceTransformer named in cfg["embed"]["model"]
#                    ONCE and caches it in a module global, re-loading only if
#                    the configured name changes. Loading is seconds of startup
#                    cost that would otherwise be paid on every single query.
#   encode_texts(texts, cfg, is_query)
#                    The real worker. Applies the BGE instruction prefix
#                    ("Represent this sentence for searching relevant
#                    passages: ") to the QUERY side only - that prefix is part of
#                    how BGE was trained and omitting it costs real recall, while
#                    applying it to passages would be wrong. Returns a correctly
#                    shaped empty array for empty input so callers never
#                    special-case it. Embeddings are L2-normalised by default so
#                    FAISS inner product is cosine similarity.
#   encode(chunks, cfg)
#                    Passage-side entry point. Asserts the produced dimension
#                    matches cfg["embed"]["dim"] and raises a message naming both
#                    numbers if not - a silent dimension mismatch would build an
#                    index that fails much later, at search time.
#
# Config  : cfg["embed"] -> model, dim, batch_size, normalize; cfg["device"]
# Outputs : float32 numpy array, shape (n_texts, dim)
# =============================================================================

"""Stage 4 — embed chunks"""

from __future__ import annotations

from typing import Any

from ..contracts import *  # noqa
from ..logging_conf import get_logger

log = get_logger(__name__)

_MODEL: Any = None
_MODEL_NAME: str | None = None


def get_model(cfg: dict) -> Any:
    """Load (once) the sentence-embedding model named in cfg['embed']['model']."""
    global _MODEL, _MODEL_NAME
    name = cfg["embed"]["model"]
    if _MODEL is None or _MODEL_NAME != name:
        from sentence_transformers import SentenceTransformer

        log.info("loading embedder %s on %s", name, cfg.get("device", "cpu"))
        _MODEL = SentenceTransformer(name, device=cfg.get("device", "cpu"))
        _MODEL_NAME = name
    return _MODEL


def encode_texts(texts: list[str], cfg: dict, is_query: bool = False) -> Any:
    """Encode raw strings. BGE wants an instruction prefix on the QUERY side only."""
    import numpy as np

    if not texts:
        return np.zeros((0, int(cfg["embed"].get("dim", 768))), dtype="float32")

    model = get_model(cfg)
    name = cfg["embed"]["model"].lower()
    if is_query and "bge" in name:
        # the prefix is part of how BGE was trained; omitting it costs real recall
        texts = ["Represent this sentence for searching relevant passages: " + t for t in texts]

    vecs = model.encode(
        texts,
        batch_size=int(cfg["embed"].get("batch_size", 16)),
        convert_to_numpy=True,
        normalize_embeddings=bool(cfg["embed"].get("normalize", True)),
        show_progress_bar=False,
    )
    return vecs.astype("float32")


def encode(chunks: list[Chunk], cfg: dict) -> Any:  # noqa: F405
    """Embed with cfg['embed']['model']."""
    vecs = encode_texts([c.text for c in chunks], cfg, is_query=False)
    expected = int(cfg["embed"].get("dim", 0) or 0)
    if expected and vecs.shape[1] != expected:
        raise ValueError(
            f"configs/config.yaml says embed.dim={expected} but {cfg['embed']['model']} "
            f"produces {vecs.shape[1]} — fix the config, the index depends on it."
        )
    log.info("embed: %d chunks -> %s", len(chunks), tuple(vecs.shape))
    return vecs
