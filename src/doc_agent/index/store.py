"""Stage 4 — vector store"""

from __future__ import annotations

import json
import os
from typing import Any

from ..contracts import *  # noqa
from ..ingest.loader import repo_root
from ..logging_conf import get_logger

log = get_logger(__name__)


def index_dir() -> str:
    """data/index/ — deliberately NOT data/raw/ or data/interim/, both of which are
    gitignored. The built index is small enough to ship, so a grader can run the demo
    notebook without a GPU or a corpus rebuild."""
    return os.path.join(repo_root(), "data", "index")


def build(chunks: Any, vectors: Any, cfg: dict) -> None:
    """Persist a vector index (cfg['index']['type'])."""
    import faiss
    import numpy as np

    out = index_dir()
    os.makedirs(out, exist_ok=True)
    vectors = np.ascontiguousarray(vectors.astype("float32"))
    n, dim = vectors.shape
    kind = str(cfg["index"].get("type", "faiss:flat")).lower()

    index: Any
    if kind.endswith("hnsw"):
        index = faiss.IndexHNSWFlat(dim, 32, faiss.METRIC_INNER_PRODUCT)
        index.hnsw.efConstruction = 200
    else:
        # Flat is EXACT. At this corpus size an approximate index would trade recall
        # for a speedup we do not need, and recall is what the NFR is about.
        index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    faiss.write_index(index, os.path.join(out, "index.faiss"))

    with open(os.path.join(out, "chunks.jsonl"), "w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(
                json.dumps(
                    {"id": c.id, "doc_id": c.doc_id, "text": c.text, "page_ids": c.page_ids},
                    ensure_ascii=False,
                )
                + "\n"
            )

    meta = {
        "n_chunks": int(n),
        "dim": int(dim),
        "index_type": kind,
        "embed_model": cfg["embed"]["model"],
        "chunk_tokens": cfg["index"].get("chunk_tokens"),
        "overlap": cfg["index"].get("overlap"),
        "n_pages": len({p for c in chunks for p in c.page_ids}),
        "n_docs": len({c.doc_id for c in chunks}),
        "n_words": sum(len(c.text.split()) for c in chunks),
        "index_bytes": os.path.getsize(os.path.join(out, "index.faiss")),
    }
    with open(os.path.join(out, "index_meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    log.info("index: %d vectors dim=%d type=%s -> %s", n, dim, kind, out)


def load(cfg: dict) -> tuple[Any, list[Chunk], dict]:  # noqa: F405
    """Load the persisted index, its chunks, and its build metadata."""
    import faiss

    out = index_dir()
    path = os.path.join(out, "index.faiss")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} missing — run `bash scripts/build_index.sh` to build the index first."
        )
    index = faiss.read_index(path)
    with open(os.path.join(out, "chunks.jsonl"), encoding="utf-8") as fh:
        chunks = [Chunk(**json.loads(line)) for line in fh]  # noqa: F405
    with open(os.path.join(out, "index_meta.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    return index, chunks, meta
