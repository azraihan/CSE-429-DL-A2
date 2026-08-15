# =============================================================================
# File:     src/doc_agent/settings.py
# Layer:    Configuration - secrets
# Status:   FIXED (provided scaffold)
#
# Purpose:
#   Typed, validated access to every secret the system needs, loaded from the
#   environment or a local .env file by pydantic-settings. This is the ONLY
#   module allowed to read secret material; no other file should touch
#   os.environ for keys.
#
# Fields:
#   llm_api_key    - credential for the LLM used by llm/client.py and eval/judge.py
#   wandb_api_key  - credential for experiment tracking in mlops/tracking.py
#   Both default to "" so import never fails on a machine without credentials;
#   the failure surfaces at call time, where it can be reported meaningfully.
#
# Usage:
#   from ..settings import settings   ->  settings.llm_api_key
#
# Why it matters:
#   .env is gitignored and .env.example is committed in its place, so a key can
#   never be captured in git history - the auditable/secure NFR depends on this
#   separation holding everywhere.
# =============================================================================

"""FIXED — typed settings from environment (secrets live here, never in code/config)."""
from __future__ import annotations
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_api_key: str = ""
    wandb_api_key: str = ""
    class Config:
        env_file = ".env"

settings = Settings()  # import this; do not read os.environ elsewhere
