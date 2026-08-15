# =============================================================================
# File:     scripts/run_eval.py
# Layer:    Entry point script
# Status:   STUB - only the imports are present
#
# Purpose:
#   The evaluation harness: read the task set, run each question through the
#   agent, score the results, and write a report.
#
# To implement:
#   1. load tasks.jsonl (contracts.Query - note `verifiable` and `judged`)
#   2. for each task: pipeline.answer(query.text, cfg)
#   3. score by route - verifiable tasks through grading_kit/success_check.py
#      (exact match), judged tasks through eval/judge.py; retrieval and OCR
#      metrics from eval/metrics.py
#   4. aggregate OVERALL and PER SUBGROUP (eval/fairness.py) - the mean alone
#      hides the figure/table stratum, which is 56.1% of this corpus's questions
#   5. write results stamped with the corpus version (data/versioning.snapshot())
#      and the config, so the numbers stay attributable
#
# Should also record the abstention rate: on this system a lower score with
# honest abstentions is a better outcome than a higher score with confident
# fabrications, and only this harness can show the difference.
# =============================================================================

"""Run tasks.jsonl through the agent and score."""
from doc_agent import config, pipeline
# IMPLEMENT: load tasks, call pipeline.answer, score with eval.metrics + grading_kit/success_check.py
