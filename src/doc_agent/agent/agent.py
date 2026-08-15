# =============================================================================
# File:     src/doc_agent/agent/agent.py
# Stage:    6 - the agent loop
# Status:   PARTIAL - run() is FIXED and complete; decide(), act() and
#           synthesize() are STUBS to implement.
#
# Purpose:
#   The control loop that turns retrieval into an agent: perceive -> decide ->
#   act -> observe, bounded by cfg["agent"]["max_steps"], with every
#   cross-cutting concern entering through a hook seam rather than inline code.
#
# run(query_text) - FIXED, do not restructure:
#   for each step (bounded):
#       hooks.run(ON_STEP)        -> tracing
#       action = self.decide()    -> IMPLEMENT: the policy
#       stop?                     -> leave the loop
#       hooks.run(ON_TOOL_CALL)   -> guardrails: budget, autonomy, injection
#       result = self.act()       -> dispatch through tools.REGISTRY
#       record into state["obs"] and Memory
#   hooks.run(BEFORE_ANSWER)      -> grounding gate + PII redaction
#   ans = self.synthesize()       -> IMPLEMENT: grounded, cited answer
#   hooks.run(AFTER_ANSWER)       -> trace + metrics
#
#   Security, grounding, privacy and tracing are deliberately NOT written here.
#   Inlining them would scatter each concern across the codebase and break the
#   audit story that wiring.py exists to tell.
#
# decide(state) - THE MANDATORY AGENTIC BEHAVIOUR (A3 gate, fail-closed):
#   Reads the last observation (top_score, k) and branches on the NUMBER, using
#   the helpers in retrieval/retriever.py:
#     1. retrieve at k = cfg.retrieve.k
#     2. if is_weak(chunks, cfg):  k2 = next_k(k, cfg)
#          k2 is not None -> retrieve AGAIN at the wider k2, then re-check
#          k2 is None (k_max reached, still weak) -> ABSTAIN
#     3. else -> synthesize a grounded, cited answer
#   Every step must emit obs {"top_score": ..., "k": ...} so traces/run.jsonl
#   shows the path depending on observations. A fixed retrieve->answer path is
#   NOT agentic and caps the grade. May be rule-based (baseline) or the RL
#   policy from Stage 7.
#
# act(action)      - IMPLEMENT: look the tool up in tools.REGISTRY by name and
#                    call it with the action's arguments, returning a ToolResult.
# synthesize(state)- IMPLEMENT: a grounded, cited Answer built only from the
#                    observed evidence; abstain when unsupported. Prompt text
#                    belongs in llm/prompts.py, not here.
#
# Collaborators: retrieval.Retriever, agent.memory.Memory, agent.tools.REGISTRY,
#                hooks (four seams), llm.postprocess.format_answer
# =============================================================================

"""Stage 6 - FIXED loop - perceive -> decide -> act -> observe, with cross-cutting seams.
Implement decide() and synthesize() only. Security, grounding, PII, and tracing run via hooks at the
marked seams - do NOT inline them here."""
from __future__ import annotations
from ..contracts import *  # noqa
from .. import hooks
from .memory import Memory

class Agent:
    """FIXED loop. Implement decide() (the policy) and synthesize() only."""
    def __init__(self, cfg: dict, retriever) -> None:
        self.cfg = cfg["agent"]; self.retriever = retriever; self.mem = Memory()

    def run(self, query_text: str) -> Answer:
        state = {"query": query_text, "obs": []}
        for _ in range(self.cfg["max_steps"]):
            hooks.run(hooks.ON_STEP, {"state": state})
            action = self.decide(state)                      # IMPLEMENT (policy)
            if action["tool"] == "stop":
                break
            hooks.run(hooks.ON_TOOL_CALL, {"action": action})   # guardrails/injection/trace
            result = self.act(action)                        # runs the tool via REGISTRY
            state["obs"].append(result); self.mem.add(result)
        hooks.run(hooks.BEFORE_ANSWER, {"state": state})     # grounding gate / PII redact
        ans = self.synthesize(state)                         # IMPLEMENT (grounded answer)
        hooks.run(hooks.AFTER_ANSWER, {"answer": ans})       # trace / metrics
        return ans

    def decide(self, state: dict) -> dict:
        """Evidence-gated re-search — the MANDATORY agentic behaviour (A3 gate, fail-closed).
        Read the last observation (top_score, k) and branch on the NUMBER, using retrieval.retriever:
          1. retrieve at k = cfg.retrieve.k
          2. if is_weak(chunks, cfg):  k2 = next_k(k, cfg)
               - k2 is not None -> retrieve AGAIN at the wider k2 (widen the net), then re-check
               - k2 is None (hit k_max) and still weak -> ABSTAIN ("insufficient evidence")
          3. else -> synthesize a grounded, cited answer
        Emit obs {"top_score": ..., "k": ...} on each step. A fixed retrieve->answer path is NOT agentic
        and caps the grade. Rule-based (baseline) or RL policy (Stage 7)."""
        raise NotImplementedError("Stage 6: agent policy")

    def act(self, action: dict) -> ToolResult:
        raise NotImplementedError("Stage 6: dispatch tool from tools.REGISTRY")

    def synthesize(self, state: dict) -> Answer:
        """Grounded, cited answer; abstain if unsupported (no-hallucination)."""
        raise NotImplementedError("Stage 6: synthesize grounded answer")
