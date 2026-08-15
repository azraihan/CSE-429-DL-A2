# =============================================================================
# File:     tests/test_ocr.py
# Layer:    Tests - Stage 3 OCR unit tests
# Status:   SKIPPED placeholder - implement alongside vision/ocr.py
#
# What belongs here - all of it testable WITHOUT loading Nougat, by testing the
# pure functions and stubbing Reader._run_batch:
#   - _repetition_cut() detects a loop that starts near the TOP of the page, not
#     just at the end. This is a regression test for a real fix: an earlier
#     version inspected only the last 400 characters and missed exactly that case
#   - _repetition_cut() returns None on healthy text, and on text too short to
#     judge
#   - _guarded() keeps the healthy prefix and discards the loop, rather than
#     dropping the whole page
#   - _load_cache() re-applies the guard on READ (the self-healing property) and
#     skips half-written lines from a killed run
#   - transcribe() serves cached keys without calling the model, and emits
#     "<page>#prose" chunks plus "[figure]"/"[table]"-prefixed region chunks with
#     ids numbered by REGION_META order
#   - the OOM path falls back to one image at a time instead of failing the run
#
# Also worth covering: vision/layout.py's _gutter() on a synthetic two-column
# image, since reading order is this project's data speciality.
# =============================================================================

"""Unit test home for OCR. IMPLEMENT — CI runs these."""
import pytest

@pytest.mark.skip(reason="students: implement OCR unit tests")
def test_ocr_placeholder():
    assert True
