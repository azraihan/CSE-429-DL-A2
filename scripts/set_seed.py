# =============================================================================
# File:     scripts/set_seed.py
# Layer:    Entry point script - reproducibility gate
#
# Purpose:
#   Sets every source of randomness that affects a run from the single value in
#   configs/config.yaml: Python's `random`, NumPy, and PyTorch. It then calls
#   torch.use_deterministic_algorithms(True), which is the step that matters
#   most - without it, CUDA kernels remain free to choose non-deterministic
#   implementations and two runs of the same seed can still disagree.
#
# Usage:   python scripts/set_seed.py, or import and call main() before training
#          or evaluation.
#
# Caveats worth knowing:
#   - Deterministic algorithms can be slower, and PyTorch raises rather than
#     silently falling back when an operation has no deterministic
#     implementation. That is the desired behaviour here: an unreproducible run
#     should fail loudly, not quietly.
#   - Some CUDA kernels additionally need CUBLAS_WORKSPACE_CONFIG set in the
#     environment.
#
# Verified by: tests/test_crosscutting.py::test_rerun_reproduces_metrics
# =============================================================================

"""Deterministic seeds (reproducibility gate)."""
import random, numpy as np, torch
from doc_agent import config

def main() -> None:
    s = config.load()["seed"]
    random.seed(s); np.random.seed(s); torch.manual_seed(s)
    torch.use_deterministic_algorithms(True)

if __name__ == "__main__":
    main()
