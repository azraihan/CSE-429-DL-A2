# =============================================================================
# File:     src/doc_agent/optional/dp.py
# Layer:    OPTIONAL - differential privacy (DP-SGD)
# Status:   STUB, off by default. Activate for a PII-sensitive corpus or a
#           private-training NFR; CI does not require an implementation.
#
# Purpose:
#   make_private(optimizer, cfg) wraps a training optimizer with gradient
#   clipping and calibrated noise, bounding how much any single training example
#   can influence the resulting weights - the defence against a shared model
#   memorising and later regurgitating its training data.
#
# Why it is not activated here:
#   This corpus is PUBLISHED academic papers. The privacy concern is real but
#   different in kind - it is about the author identifiers inside public
#   documents, not about confidential records - and it is addressed at the right
#   layer by governance/pii.py, which redacts identifiers before indexing and
#   drops author blocks entirely. DP-SGD would impose a real accuracy cost to
#   protect data that is already public.
#
# If a future corpus contains genuinely private documents, this is the module to
# turn on, and the accuracy/epsilon trade-off should be reported explicitly.
# =============================================================================

"""OPTIONAL — differential privacy (DP-SGD) for shared models
Activate only if your data speciality or NFR requires it (e.g. a PII-sensitive corpus / private NFR). Off by default; CI does not require impl."""
from __future__ import annotations

def make_private(optimizer, cfg: dict):
    raise NotImplementedError("optional: DP-SGD")

