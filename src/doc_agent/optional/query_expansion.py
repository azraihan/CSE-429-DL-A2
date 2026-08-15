# =============================================================================
# File:     src/doc_agent/optional/query_expansion.py
# Layer:    OPTIONAL - query embedding and expansion
# Status:   STUB, off by default. CI does not require an implementation.
#
# Purpose:
#   expand(query, cfg) -> several reformulations of one question (synonyms,
#   expanded acronyms, a hypothetical answer document / HyDE), each retrieved
#   separately and the results fused. It targets vocabulary mismatch: the paper
#   says "we ablate the attention head" and the question asks "what happens if
#   you remove attention".
#
# Relationship to the agent:
#   agent.decide() already REFORMULATES the query when the evidence is weak -
#   that is the mandatory evidence-gated re-search behaviour. This module is the
#   unconditional, up-front version of the same idea. It is left off partly so
#   the two do not confound each other: if every query is expanded before the
#   first retrieval, the weak-evidence branch fires less often and the agentic
#   behaviour becomes harder to demonstrate and measure.
#
# If activated, treat it as an ablation arm in eval/ablation.py rather than a
# silent default.
# =============================================================================

"""OPTIONAL — query embedding + expansion
Activate only if your data speciality or NFR requires it (profiles 18, 27). Off by default; CI does not require impl."""
from __future__ import annotations

def expand(query: str, cfg: dict) -> list[str]:
    raise NotImplementedError("optional: query expansion")

