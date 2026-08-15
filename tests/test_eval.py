# =============================================================================
# File:     tests/test_eval.py
# Layer:    Tests - evaluation unit tests
# Status:   SKIPPED placeholder - implement alongside eval/metrics.py
#
# What belongs here:
#   - normalize_text(): "\(n\)" and the math-italic codepoint for n both reduce to
#     "n"; LaTeX control sequences and math delimiters are stripped; dash variants
#     unify. This function decides what every OCR number MEANS, so it deserves the
#     most tests in the file
#   - ocr_f1 / cer / wer on identical, empty, and disjoint inputs - the boundary
#     cases where a metric silently returns a misleading 0.0 or 1.0
#   - cer's multiset behaviour: a repeated word must be repeated correctly to score
#   - _edit_distance: the C-backed path and the pure-Python fallback agree
#   - recall_at_k on a known ranking, including gold absent entirely
#   - ece() on a perfectly calibrated and a maximally overconfident input
#
# Metric tests are cheap and unusually valuable: a wrong metric does not crash,
# it just reports a number nobody can trust.
# =============================================================================

"""Unit test home for eval. IMPLEMENT — CI runs these."""
import pytest

@pytest.mark.skip(reason="students: implement eval unit tests")
def test_eval_placeholder():
    assert True
