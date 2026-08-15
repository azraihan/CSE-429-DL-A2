# =============================================================================
# File:     src/doc_agent/optional/api_security.py
# Layer:    OPTIONAL - API authentication and rate limiting
# Status:   STUB, off by default. Activate only for a secure / high-stakes
#           deployment profile; CI does not require an implementation.
#
# Purpose:
#   Protects serve/api.py when it is exposed beyond a local demo.
#   require_auth(token) -> is this caller allowed
#   rate_limit(client)  -> is this caller within its quota
#
# Why it is a real concern rather than boilerplate here:
#   /answer runs an LLM-backed agent loop, so an unauthenticated endpoint is an
#   unauthenticated way to spend the project's LLM budget. Rate limiting is the
#   deployment-side counterpart of the per-run cost budget that
#   agent/guardrails.py enforces internally.
#
# Not activated for this project: the system runs locally and as a graded demo,
# with no public endpoint.
# =============================================================================

"""OPTIONAL — API auth + rate limiting
Activate only if your data speciality or NFR requires it (profiles secure/high-stakes). Off by default; CI does not require impl."""
from __future__ import annotations

def require_auth(token: str) -> bool: raise NotImplementedError("optional: auth")
def rate_limit(client: str) -> bool: raise NotImplementedError("optional: rate limit")

