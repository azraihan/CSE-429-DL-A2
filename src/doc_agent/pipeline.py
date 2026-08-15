# =============================================================================
# File:     src/doc_agent/pipeline.py
# Layer:    Orchestration - the end-to-end entry points
# Status:   FIXED - stage order and the hooks.run()/register_all() calls must
#           not be reordered or removed.
#
# Purpose:
#   Composes the vertical stages into the two things the system actually does:
#   build a knowledge base offline, and answer a question online.
#
# build_knowledge_base(cfg)  - offline, run once per corpus version:
#   wiring.register_all(cfg)              wire cross-cutting features
#   loader.load_pages(cfg)                Stage 1  data/raw -> list[Page]
#   preprocess.run(...)                   Stage 1  contract checks / greyscale
#   enhance.run(...)                      Stage 1  optional VAE/diffusion restore
#   hooks.run(AFTER_INGEST, ...)
#   layout.detect(...)                    Stage 2  -> list[Region], READING ORDER
#   ocr.transcribe(...)                   Stage 3  -> list[Chunk] (Nougat)
#   hooks.run(AFTER_OCR, ...)                      PII scrubbed BEFORE indexing
#   chunk.split(...)                      Stage 4  region-aware re-chunking
#   hooks.run(BEFORE_INDEX, ...)
#   embed.encode(...)                     Stage 4  -> float32 matrix
#   store.build(...)                      Stage 4  -> data/index/{faiss,jsonl,meta}
#
# answer(query_text, cfg)    - online, per question:
#   wiring.register_all(cfg) -> Retriever (Stage 5) -> Agent.run() (Stage 6).
#   All security, grounding, PII and tracing happen at the seams inside the
#   agent loop, not here.
#
# Why the seam placement is deliberate:
#   AFTER_OCR sits before chunking and embedding, so identifiers are removed
#   from the text that gets indexed - redacting only at answer time would still
#   leave PII searchable in the vector store.
# =============================================================================

"""FIXED end-to-end order (Stages 0-9) + cross-cutting seams.
Do not reorder stages or remove hooks.run()/register_all() calls."""
from __future__ import annotations
from . import config, hooks, wiring  # noqa: F401
from .ingest import loader, preprocess, enhance
from .vision import layout, ocr
from .index import chunk, embed, store
from .retrieval import retriever
from .agent import agent

def build_knowledge_base(cfg: dict) -> None:
    wiring.register_all(cfg)                        # wire cross-cutting features
    pages = loader.load_pages(cfg)
    pages = preprocess.run(pages, cfg)
    pages = enhance.run(pages, cfg)                 # Stage 1 - enhancement (VAE/diffusion)
    hooks.run(hooks.AFTER_INGEST, {"pages": pages})
    regions = layout.detect(pages, cfg)             # Stage 2
    text = ocr.transcribe(regions, cfg)             # Stage 3
    hooks.run(hooks.AFTER_OCR, {"chunks": text})    # e.g. PII redaction on extracted text
    chunks = chunk.split(text, cfg)                 # Stage 4
    hooks.run(hooks.BEFORE_INDEX, {"chunks": chunks})
    vectors = embed.encode(chunks, cfg)
    store.build(chunks, vectors, cfg)

def answer(query_text: str, cfg: dict):
    wiring.register_all(cfg)
    r = retriever.Retriever(cfg)                    # Stage 5
    return agent.Agent(cfg, r).run(query_text)      # Stage 6 (seams run inside the loop)
