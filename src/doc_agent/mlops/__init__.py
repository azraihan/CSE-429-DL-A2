# =============================================================================
# File:     src/doc_agent/mlops/__init__.py
# Layer:    MLOps package marker
#
# Contains:
#   tracking.py  experiment tracking (W&B) - what was run and what it scored
#   registry.py  model registry - which checkpoint produced that score
#   monitor.py   drift and latency monitoring - is it still working in production
#
# Together with data/versioning.py (which corpus) these answer the four
# questions a reported metric has to survive: which data, which code, which
# checkpoint, and is it still true today.
# =============================================================================

