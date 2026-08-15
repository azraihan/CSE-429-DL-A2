# =============================================================================
# File:     src/doc_agent/__init__.py
# Layer:    Package root
# Status:   FIXED (provided scaffold)
#
# Purpose:
#   Marks `doc_agent` as an importable package and advertises the three modules
#   that make up the public surface of the system: `contracts` (the frozen data
#   models), `config` (YAML loading) and `pipeline` (the end-to-end entry points).
#
# Notes:
#   `__all__` here only affects `from doc_agent import *`; every internal module
#   is still imported by its full dotted path (e.g. doc_agent.vision.layout).
#   The package is installed in editable mode via pyproject.toml, so `src/` is
#   on sys.path and `import doc_agent` works from anywhere in the repo.
# =============================================================================

__all__ = ["contracts", "config", "pipeline"]
