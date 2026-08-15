# =============================================================================
# File:     tests/test_crosscutting.py
# Layer:    Tests - cross-cutting behaviour
# Status:   ALL SKIPPED - un-skip each alongside the feature it covers
#
# Purpose:
#   The premise stated at the top of the file: cross-cutting features must work
#   END TO END, not merely exist in a file. tests/test_structure.py proves each
#   feature has a register() function; these prove the registration actually
#   changes what the system does.
#
# The five claims, each mapping to one wired feature:
#   grounding  an answer with no supporting evidence ABSTAINS rather than
#              fabricating                            -> llm/postprocess.py
#   security   a document containing "ignore your instructions" does not change
#              agent behaviour - retrieved text is data, never instructions
#                                                     -> agent/guardrails.py
#   privacy    PII in the corpus never reaches an answer or a log
#                                                     -> governance/pii.py
#   audit      every agent step and tool call appears in the trail
#                                                     -> logging_conf.register
#   repro      a seeded re-run reproduces reported metrics within tolerance
#                                                     -> scripts/set_seed.py
#
# These are the NFR claims the project is graded on. Each is written as a
# property an adversary would try to violate, which is why they are behavioural
# tests rather than assertions that a function exists.
# =============================================================================

"""Cross-cutting features must work END TO END, not just exist in one file.
Un-skip and implement alongside the feature. CI runs these."""
import pytest

@pytest.mark.skip(reason="implement with grounding")
def test_grounding_unsupported_query_abstains():
    """An answer with no supporting evidence must abstain, not fabricate."""
    assert True

@pytest.mark.skip(reason="implement with security")
def test_injection_in_document_does_not_hijack():
    """A document containing 'ignore your instructions' must not change agent behaviour."""
    assert True

@pytest.mark.skip(reason="implement with PII")
def test_pii_never_leaks_to_answer_or_log():
    """PII in the corpus must not appear in answers or logs."""
    assert True

@pytest.mark.skip(reason="implement with tracing")
def test_trace_covers_every_step():
    """Every agent step and tool call must appear in the audit trail."""
    assert True

@pytest.mark.skip(reason="implement with reproducibility")
def test_rerun_reproduces_metrics():
    """A seeded re-run reproduces reported metrics within tolerance."""
    assert True
