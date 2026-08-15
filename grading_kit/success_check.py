# =============================================================================
# File:     grading_kit/success_check.py
# Layer:    Evaluation - per-task verifier
# Status:   STUB - check() raises NotImplementedError. The SIGNATURE IS FIXED.
#
# Purpose:
#   The single definition of "did the system get this task right", used by
#   scripts/run_eval.py and by the graders. Keeping it in one function with a
#   fixed signature is what makes results comparable across groups - a project
#   that scores itself with its own bespoke matcher is not measuring the same
#   thing as anyone else.
#
# check(task, answer) -> bool
#   Routes on the task type, mirroring contracts.Query:
#     verifiable -> exact match after normalisation (see
#                   eval.metrics.normalize_text and rl/rlvr.py, which must agree
#                   with this - a training reward that disagrees with the
#                   evaluation criterion optimises the wrong target)
#     judged     -> eval/judge.py, thresholded
#
# Implementation cautions:
#   - Normalise both sides identically (case, whitespace, units, LaTeX vs
#     Unicode), then compare EXACTLY. Fuzzy matching here quietly inflates the
#     verifiable subset, which is the objective anchor of the whole evaluation.
#   - An abstention on an answerable task is a failure; an abstention on an
#     unanswerable one should count as a success, or the metric rewards guessing.
# =============================================================================

"""Per-task verifier. FIXED signature."""
from __future__ import annotations

def check(task: dict, answer: dict) -> bool:
    """Return True if `answer` satisfies `task` (exact for fact tasks; judge for open). IMPLEMENT."""
    raise NotImplementedError("verify a task result")
