# =============================================================================
# File:     src/doc_agent/optional/retrain_trigger.py
# Layer:    OPTIONAL - automated retraining on drift / SLA breach
# Status:   STUB, off by default. Activate for a closed-loop MLOps profile; CI
#           does not require an implementation.
#
# Purpose:
#   maybe_retrain(metrics, cfg) -> bool. The decision half of the loop that
#   mlops/monitor.py opens: given observed drift or an SLO breach, should the
#   system retrain, roll back to a previous mlops/registry.py entry, or just
#   alert a human?
#
# Design cautions if implemented:
#   - Require sustained breach, not a single noisy window; an automated retrain
#     on transient noise is a way to make a system worse on a schedule.
#   - Never promote automatically on unlabelled proxies alone. Gate promotion on
#     the held-out evaluation, and keep the previous registry version available
#     for rollback.
#   - Log the trigger decision and its inputs - an automated action that cannot
#     be explained after the fact is not auditable.
#
# Not activated: this project has no live traffic, so the loop has nothing to
# close.
# =============================================================================

"""OPTIONAL — automated retrain on drift/SLA breach
Activate only if your data speciality or NFR requires it (MLOps closed-loop). Off by default; CI does not require impl."""
from __future__ import annotations

def maybe_retrain(metrics: dict, cfg: dict) -> bool:
    raise NotImplementedError("optional: retrain trigger")

