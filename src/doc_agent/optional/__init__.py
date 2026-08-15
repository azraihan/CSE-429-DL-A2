# =============================================================================
# File:     src/doc_agent/optional/__init__.py
# Layer:    Optional features package marker
# Status:   All modules here are OFF by default and NOT required by the CI
#           structure gate.
#
# What "optional" means:
#   These are capabilities a project activates only if its data speciality or
#   NFR profile actually requires them. Implementing all of them would be
#   scope-padding, not engineering - the point of the directory is to make the
#   deliberate NOT-doing visible and reversible, rather than leaving the option
#   undocumented.
#
# Contains: api_security, cache, config_snapshot, dp, query_expansion,
#           retrain_trigger, stream_ingest, synthetic_data
# =============================================================================

"""OPTIONAL features. Profile-gated; OFF by default; not required by CI structure gate."""
