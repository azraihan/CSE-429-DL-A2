# =============================================================================
# File:     src/doc_agent/serve/__init__.py
# Layer:    Stage 8 - serving package marker
#
# Contains:
#   api.py  FastAPI service - the programmatic interface (/answer, /health)
#   ui.py   Gradio demo over that API - the human interface
#
# Both are thin: they call pipeline.answer() and render contracts.Answer. No
# retrieval or agent logic belongs here, so the demo and the evaluated system
# cannot diverge.
# =============================================================================

