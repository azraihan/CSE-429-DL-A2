# =============================================================================
# File:     src/doc_agent/eval/__init__.py
# Layer:    Stage 9 - evaluation package marker
#
# Contains:
#   metrics.py      OCR (CER/WER/F1), retrieval, groundedness, citation, ECE,
#                   fairness gap - the numeric definitions
#   judge.py        LLM-as-judge for non-verifiable, open-ended answers
#   calibration.py  temperature scaling + ECE (calibrated-confidence NFR)
#   fairness.py     subgroup audit
#   robustness.py   OOD / scan-quality stress
#   ablation.py     stage-by-stage contribution deltas
#   interpret.py    explainability - why retrieved, where looked
#
# Split by question, not by convenience: "how accurate", "how honest", "how
# fair", "how robust", "which part earned it" and "why" are separate questions
# and each gets its own module.
# =============================================================================

