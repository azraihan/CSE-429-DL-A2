# =============================================================================
# File:     tests/test_retrieval.py
# Layer:    Tests - Stage 5 retrieval unit tests
# Status:   SKIPPED placeholder - implement alongside retrieval/retriever.py
#
# What belongs here:
#   - retrieve() sets .score on every returned chunk, and returns COPIES - the
#     same chunk retrieved by two different queries must not share a score. This
#     is the subtle bug the copy in retriever.py exists to prevent, and it would
#     make is_weak() read a stale number
#   - k is clamped to the corpus size, and negative FAISS ids are skipped
#   - the query is encoded with is_query=True, so the BGE instruction prefix is
#     applied on the query side only
#   - top_score() returns 0.0 for an empty result rather than raising
#   - is_weak() at, just below, and just above weak_threshold - boundary
#     behaviour matters because this single comparison decides whether the agent
#     re-searches
#   - next_k() widens by k_step and returns None exactly once k_max is exceeded,
#     which is the ABSTAIN signal
#
# The three policy helpers need no index or model at all - they are pure
# functions over scores, and they encode the graded agentic behaviour, so they
# should be tested exhaustively.
# =============================================================================

"""Unit test home for retrieval. IMPLEMENT — CI runs these."""
import pytest

@pytest.mark.skip(reason="students: implement retrieval unit tests")
def test_retrieval_placeholder():
    assert True
