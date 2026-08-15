# =============================================================================
# File:     tests/test_ingest.py
# Layer:    Tests - Stage 1 ingest unit tests
# Status:   SKIPPED placeholder - implement alongside ingest/loader.py and
#           ingest/preprocess.py
#
# What belongs here:
#   - load_pages() populates PAGE_META for every returned page, and CLEARS stale
#     entries on a second call - it is module-level state that later stages index
#     into, so a leftover row is a real bug
#   - cfg.ingest.limit_pages and cfg.ingest.splits filter as documented; the
#     splits filter is what keeps train/test isolation honest
#   - a missing manifest raises the message naming scripts/get_data.sh
#   - preprocess.run() raises on a missing image file
#   - preprocess.run() raises when image geometry disagrees with the manifest -
#     the check that stops a corpus/manifest mismatch surfacing later as an
#     unexplained OCR failure
#   - greyscale conversion happens when configured, and pages pass through
#     unchanged when degrade is off
#   - with degrade on, output paths point into data/interim/ and data/raw/ is
#     untouched
#
# Use a handful of tiny generated PNGs plus a fixture manifest.
# =============================================================================

"""Unit test home for ingest. IMPLEMENT — CI runs these."""
import pytest

@pytest.mark.skip(reason="students: implement ingest unit tests")
def test_ingest_placeholder():
    assert True
