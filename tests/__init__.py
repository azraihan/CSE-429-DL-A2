# =============================================================================
# File:     tests/__init__.py
# Layer:    Test package marker
#
# Present so `tests` is a package and the modules inside it can share fixtures
# and be imported unambiguously by pytest.
#
# The suite splits into three kinds:
#   structural  test_structure.py, test_contracts.py, test_tools.py - run today
#               and enforce the frozen skeleton
#   unit        test_ingest / test_ocr / test_retrieval / test_agent / test_data
#               / test_eval - per-stage homes, currently skipped placeholders
#   end to end  test_smoke.py, test_crosscutting.py - the behavioural claims
# =============================================================================

