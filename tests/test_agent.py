# =============================================================================
# File:     tests/test_agent.py
# Layer:    Tests - Stage 6 agent unit tests
# Status:   SKIPPED placeholder - implement alongside agent/agent.py
#
# What belongs here (the highest-value tests in the suite, since this is where
# the A3 agentic claim is made):
#   - decide() with a STRONG last observation answers immediately - one retrieval,
#     no widening
#   - decide() with a WEAK observation re-retrieves at next_k rather than
#     answering, and the second call really does use the wider k
#   - decide() at k_max with still-weak evidence ABSTAINS - the fail-closed path,
#     which must be tested explicitly because it is the branch that never fires on
#     easy questions
#   - the loop respects cfg["agent"]["max_steps"]
#   - act() dispatches by name through tools.REGISTRY and returns a ToolResult
#   - synthesize() emits citations for every claim, and an unsupported claim
#     produces an abstention
#
# All of these can run against a FAKE retriever returning fixed scores - no
# index, no GPU and no LLM required, which is what keeps them in CI.
# =============================================================================

"""Unit test home for agent. IMPLEMENT — CI runs these."""
import pytest

@pytest.mark.skip(reason="students: implement agent unit tests")
def test_agent_placeholder():
    assert True
