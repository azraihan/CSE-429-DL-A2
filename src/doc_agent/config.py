# =============================================================================
# File:     src/doc_agent/config.py
# Layer:    Configuration
# Status:   FIXED (provided scaffold)
#
# Purpose:
#   The only place YAML is read. Every stage takes a plain `cfg: dict` argument
#   rather than reaching for a global, so a test can hand any stage a small
#   hand-built dict and no stage has hidden configuration state.
#
# Functions:
#   load(path="configs/config.yaml")  -> the run config: seed, device, and the
#       per-stage blocks (ingest, layout, ocr, embed, index, retrieve, agent,
#       enhance, rl) that each stage indexes by name.
#   load_task(path="configs/task.yaml") -> the task/problem definition used by
#       the eval harness.
#
# Contract note:
#   Keys are read with cfg["stage"]["key"] at the point of use, so a missing
#   key raises a KeyError naming the stage rather than silently defaulting.
#   Secrets are deliberately NOT here - they live in settings.py, read from the
#   environment, so configs/ can be committed safely.
# =============================================================================

"""FIXED config loader."""
from __future__ import annotations
import yaml
from pathlib import Path

def load(path: str | Path = "configs/config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def load_task(path: str | Path = "configs/task.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
