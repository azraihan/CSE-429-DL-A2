# =============================================================================
# File:     src/doc_agent/llm/__init__.py
# Layer:    LLM package marker
#
# Contains:
#   client.py       the single wrapper every model call goes through
#   prompts.py      the prompt template registry (no prompt strings elsewhere)
#   postprocess.py  answer formatting, citation enforcement and the grounding /
#                   abstention gate wired at BEFORE_ANSWER
#
# The three-way split exists so that "what we ask the model", "how we call it"
# and "what we accept back" can each be changed and reviewed independently.
# =============================================================================

