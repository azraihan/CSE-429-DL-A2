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
