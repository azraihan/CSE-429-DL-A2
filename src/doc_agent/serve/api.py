# =============================================================================
# File:     src/doc_agent/serve/api.py
# Stage:    8 - FastAPI service
# Status:   PARTIAL - the app object and /health exist; /answer is a STUB.
#           tests/test_structure.py requires `app` to exist by name.
#
# Purpose:
#   The system's programmatic surface. Config is loaded once at import
#   (`_cfg = config.load()`) rather than per request, so a served process is not
#   re-reading YAML on every call.
#
# Endpoints:
#   POST /answer  -> IMPLEMENT: call pipeline.answer(q, _cfg) and return the
#                    contracts.Answer as JSON - text, citations, grounded and
#                    confidence. Return all four: an API that returns only the
#                    text discards exactly the fields the no-hallucination and
#                    calibration NFRs are carried in, and callers lose the
#                    ability to distinguish an answer from an abstention.
#   GET  /health  -> liveness probe, already implemented.
#
# Things to add with the endpoint:
#   - a request/response log through logging_conf (the ON_LOG seam already
#     scrubs PII from log messages)
#   - a warm start: pipeline.answer() constructs a Retriever per call, which
#     lazily loads the FAISS index and the embedding model - fine for a demo,
#     worth hoisting for a real service
#   - auth and rate limiting from optional/api_security.py if the deployment
#     profile calls for it
# =============================================================================

"""Stage 8 — FastAPI service"""
from __future__ import annotations
from ..contracts import *  # noqa

from fastapi import FastAPI
from .. import config, pipeline

app = FastAPI(title="doc-agent")
_cfg = config.load()

@app.post("/answer")
def answer(q: str) -> dict:
    """Return grounded, cited answer. IMPLEMENT (calls pipeline.answer)."""
    raise NotImplementedError("Stage 8: /answer endpoint")

@app.get("/health")
def health() -> dict:
    return {"ok": True}

