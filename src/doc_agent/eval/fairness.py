# =============================================================================
# File:     src/doc_agent/eval/fairness.py
# Layer:    Stage 9 - subgroup audit
# Status:   STUB - audit() raises NotImplementedError
#
# Purpose:
#   A single average hides who the system fails. audit(cfg) should recompute the
#   headline metrics per subgroup and report the WORST group and the gap, not
#   just the mean, because the mean is dominated by the largest stratum.
#
# Meaningful subgroups for this corpus (all available in PAGE_META / qa.jsonl):
#   - page layout      single-column vs two-column (42.5% two-column)
#   - evidence type    prose vs figure vs table (56.1% of questions are
#                      figure/table evidence, and that is the arm most likely to
#                      lag)
#   - question type    verifiable vs judged
#   - document / venue so no single source dominates the score
#   - scan quality     clean vs degraded, shared with eval/robustness.py
#
# Output: per-group metrics plus the disparity, using
#         eval.metrics.subgroup_gap(). Report group SIZES alongside - a gap over
#         a handful of examples is noise, and presenting it as a finding is worse
#         than not measuring.
# =============================================================================

"""Stage 9 — subgroup audit"""
from __future__ import annotations
from ..contracts import *  # noqa

def audit(cfg: dict) -> dict:
    raise NotImplementedError("Stage 9: fairness audit")

