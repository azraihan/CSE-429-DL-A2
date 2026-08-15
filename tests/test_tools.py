# =============================================================================
# File:     tests/test_tools.py
# Layer:    Tests - agent tool registry
# Status:   ACTIVE - runs in CI and currently passes
#
# Purpose:
#   Asserts every entry in tools.REGISTRY is a Tool subclass with a string name.
#   That is what lets Agent.act() dispatch generically: the loop looks a tool up
#   by name and calls it without knowing what it does, and a registry entry that
#   is not a Tool would break that at runtime, inside an agent loop, where it is
#   far harder to diagnose.
#
# Complements tests/test_structure.py::test_tool_names_locked, which pins the
# exact set of nine names - this pins their type and shape.
#
# Worth adding once the tools are implemented: that each __call__ returns a
# contracts.ToolResult (not a bare dict), and that Retrieve's payload contains
# chunk_ids, top_score and k - agent.decide() branches on top_score, so a tool
# that omits it silently disables the evidence-gated re-search that A3 grades.
# =============================================================================

from doc_agent.agent import tools

def test_registry_is_tool_subclasses():
    for t in tools.REGISTRY:
        assert issubclass(t, tools.Tool) and isinstance(t.name, str)
