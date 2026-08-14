#!/usr/bin/env bash
# A2 — build the vector index end to end.
#
#   pages -> clean -> layout -> OCR -> chunk -> embed -> store
#
# Everything is driven by configs/config.yaml; nothing is configured here.
# Set DOC_AGENT_LIMIT_PAGES=N for a quick smoke run over the first N pages.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

if [ ! -f data/raw/manifest.jsonl ]; then
  echo "[build_index] no corpus found — fetching it first"
  bash scripts/get_data.sh
fi

echo "[build_index] validating corpus + recording version"
python - <<'PY'
from doc_agent import config
from doc_agent.data import validate, versioning
from doc_agent.ingest import loader

cfg = config.load()
pages = loader.load_pages(cfg)
validate.validate(pages)                     # floors + no split leakage
print("corpus_version:", versioning.snapshot(loader.corpus_dir(cfg)))
PY

echo "[build_index] running stages 1-4"
python scripts/set_seed.py
python scripts/run_ingest.py

echo "[build_index] index summary"
python - <<'PY'
import json, os
meta = json.load(open(os.path.join("data", "index", "index_meta.json"), encoding="utf-8"))
for k, v in meta.items():
    print(f"  {k:<14} {v}")
assert meta["n_chunks"] > 0, "index is empty"
PY

echo "[build_index] done -> data/index/"
