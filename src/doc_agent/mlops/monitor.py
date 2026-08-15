# =============================================================================
# File:     src/doc_agent/mlops/monitor.py
# Layer:    MLOps - drift and latency monitoring
# Status:   STUB - check_drift() raises NotImplementedError
#
# Purpose:
#   Closes the loop. Everything else in this repo measures the system at build
#   time; this watches it after deployment, where the input distribution moves
#   and no label arrives to tell you accuracy has fallen.
#
# check_drift(cfg) should watch:
#   - INPUT drift    scan-quality and layout statistics of incoming pages
#                    against the training distribution (ink density, resolution,
#                    column count). This corpus is clean and born-digital, so
#                    genuinely scanned input is a large, detectable shift and
#                    exactly the case where accuracy would silently degrade.
#   - OUTPUT drift   abstention rate, mean confidence and mean top_score. These
#                    are the best unlabelled proxies available: a rising
#                    abstention rate is the system reporting its own degradation
#                    before any human notices.
#   - LATENCY SLO    p50/p95 per stage, since OCR generation dominates cost.
#
# On breach: raise an alert and hand off to optional/retrain_trigger.py, which
# decides whether to retrain or roll back to a previous mlops/registry.py entry.
# =============================================================================

"""MLOps — drift / latency monitoring"""
from __future__ import annotations
from ..contracts import *  # noqa

def check_drift(cfg: dict) -> dict:
    """Detect input drift (scan quality) + latency SLO breach; trigger retrain. IMPLEMENT."""
    raise NotImplementedError("MLOps: monitor")

