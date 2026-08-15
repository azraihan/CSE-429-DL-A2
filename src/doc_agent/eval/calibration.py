# =============================================================================
# File:     src/doc_agent/eval/calibration.py
# Layer:    Stage 9 - confidence calibration (calibrated-confidence NFR)
# Status:   STUB - temperature_scale() and ece() raise NotImplementedError
#
# Purpose:
#   contracts.Answer carries a `confidence` field, and that number is only worth
#   having if it is honest: answers reported at 0.9 should be right about 90% of
#   the time. Calibration is what makes downstream thresholds - the abstention
#   gate in llm/postprocess.py and the escalation trigger in agent/hitl.py -
#   meaningful rather than arbitrary.
#
# API:
#   temperature_scale(logits, labels)  Fit a single temperature on the VALIDATION
#                                      split and return a scaler. One parameter,
#                                      fitted post-hoc; it cannot change any
#                                      ranking or accuracy, only the confidence
#                                      spread. Fitting on test would leak.
#   ece(confidences, correct)          Expected calibration error: bin by
#                                      confidence, take the weighted mean gap
#                                      between mean confidence and mean accuracy
#                                      per bin. Report the bin count - ECE is
#                                      sensitive to it.
#
# Note: eval/metrics.py declares a matching ece() stub; implement once and have
#       the other delegate, so two numbers under the same name cannot diverge.
# =============================================================================

"""Stage 9 — confidence calibration (calibrated-confidence NFR)"""
from __future__ import annotations
from ..contracts import *  # noqa

def temperature_scale(logits, labels):
    """Fit temperature on val; return scaler. IMPLEMENT."""
    raise NotImplementedError("Calibration: temperature scaling")
def ece(confidences, correct) -> float:
    raise NotImplementedError("Calibration: ECE")

