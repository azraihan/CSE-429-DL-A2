# =============================================================================
# File:     tests/test_contracts.py
# Layer:    Tests - data contracts
# Status:   ACTIVE - runs in CI and currently passes
#
# Purpose:
#   Constructs a fully populated contracts.Answer with a Citation and asserts the
#   fields round-trip. Small, but it pins the shape every other stage is written
#   against: pydantic would accept a silently changed field type, and the failure
#   would otherwise appear far downstream in synthesis or scoring.
#
# Worth extending as the stages land:
#   - Answer(grounded=False) with citations=[] is a valid ABSTENTION, and the
#     abstention path should be exercised as explicitly as the success path
#   - Citation.span ordering and bounds against the cited chunk's text
#   - Query.verifiable / Query.judged being mutually exclusive in the task set,
#     since scripts/run_eval.py routes scoring on exactly that distinction
# =============================================================================

from doc_agent.contracts import Answer, Citation

def test_answer_contract():
    a = Answer(text="x", citations=[Citation(chunk_id="c1", span=(0, 1))],
               grounded=True, confidence=0.9)
    assert a.grounded and a.citations[0].chunk_id == "c1"
