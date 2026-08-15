# =============================================================================
# File:     src/doc_agent/optional/config_snapshot.py
# Layer:    OPTIONAL - exact run-config snapshot
# Status:   STUB, off by default. Activate for a reproducibility+ profile; CI
#           does not require an implementation.
#
# Purpose:
#   snapshot(cfg, out) writes the FULLY RESOLVED config for a run - after
#   defaults, environment overrides and any programmatic edits - so the run can
#   be reconstructed from the artifact rather than from configs/ as it happens to
#   look today. configs/config.yaml is a moving file; a snapshot is not.
#
# Pairs with:
#   data/versioning.snapshot()   which corpus
#   mlops/registry.register()    which checkpoint
#   the git commit               which code
#   Those four together are what makes a reported number reproducible.
#
# Not activated: mlops/tracking.init_run() is specified to log the full config
# with each run, which covers the same need for this project without a second
# artifact to keep in sync.
# =============================================================================

"""OPTIONAL — snapshot exact run config for reproducibility+
Activate only if your data speciality or NFR requires it (repro+). Off by default; CI does not require impl."""
from __future__ import annotations

def snapshot(cfg: dict, out: str) -> None:
    raise NotImplementedError("optional: config snapshot")

