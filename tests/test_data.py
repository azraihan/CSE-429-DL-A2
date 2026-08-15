# =============================================================================
# File:     tests/test_data.py
# Layer:    Tests - data validation unit tests
# Status:   SKIPPED placeholder - implement alongside data/validate.py
#
# What belongs here:
#   - validate() raises when a doc_id appears in more than one split. This is the
#     most important assertion in the file: A1 identified cross-split leakage as
#     the project's most likely failure, it inflates every reported number, and
#     it is invisible in the metrics themselves
#   - validate() raises below MIN_PAGES / MIN_WORDS
#   - validate() raises on a missing page image, a page absent from PAGE_META, or
#     a duplicate page id
#   - validate() reports ALL problems in one message rather than the first
#   - a clean corpus passes silently
#   - versioning.snapshot() is stable for unchanged inputs and CHANGES when the
#     manifest, qa or splits file changes - a version id that does not move when
#     the corpus does is worse than none
#
# All testable from small temporary fixture files; no real corpus needed.
# =============================================================================

"""Unit test home for data validation. IMPLEMENT — CI runs these."""
import pytest

@pytest.mark.skip(reason="students: implement data validation unit tests")
def test_data_placeholder():
    assert True
