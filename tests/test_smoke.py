# =============================================================================
# File:     tests/test_smoke.py
# Layer:    Tests - end-to-end
# Status:   SKIPPED - enable once the Stage 6 agent is implemented
#
# Purpose:
#   The one test that exercises the whole system: pipeline.answer() over a real
#   config, asserting the result is grounded and carries at least one citation.
#   Every other test checks a part; this checks that the parts compose.
#
# What it will catch that unit tests cannot:
#   the wiring. register_all() attaches four features to the seams, and a
#   handler that raises, mutates the wrong object, or is registered in the wrong
#   order only fails when the full path runs. The known in-place mutation
#   requirement in governance/pii.py is exactly that class of bug.
#
# Prerequisites to un-skip: a built data/index/ (scripts/run_index.py), plus
# implementations of agent.decide/act/synthesize, logging_conf.register and
# llm.postprocess.register.
# =============================================================================

"""End-to-end tiny run. Passes once students implement the stages."""
import pytest
from doc_agent import config, pipeline

@pytest.mark.skip(reason="enable after implementing stages")
def test_answer_is_grounded_and_cited():
    ans = pipeline.answer("sample question", config.load())
    assert ans.grounded and len(ans.citations) >= 1
