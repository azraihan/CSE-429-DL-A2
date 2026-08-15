# =============================================================================
# File:     src/doc_agent/governance/__init__.py
# Layer:    Governance package marker
#
# Contains:
#   pii.py  PII detection, redaction and identifier-block dropping, wired into
#           three seams (AFTER_OCR, BEFORE_ANSWER, ON_LOG)
#
# Governance is a MANDATORY cross-cutting feature for this project: the corpus is
# academic papers, and every paper carries an author block naming real people.
# =============================================================================

