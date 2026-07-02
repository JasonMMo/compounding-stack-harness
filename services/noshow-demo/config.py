"""
config.py — environment-driven configuration for noshow-demo service.

No secrets required (SQLite in-container, no auth, no LLM calls, no external
DB). Everything has a sane default so the service boots with zero env setup.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _optional(var: str, default: str) -> str:
    return os.environ.get(var, default).strip() or default


@dataclass(frozen=True)
class Settings:
    db_path: str
    """Absolute path to the SQLite file. Lives inside the container only —
    no volume mount. Losing it on redeploy/restart is intentional (demo
    data is meant to reset)."""

    env: str
    """Deployment environment: 'dev' (default) | 'prod'.
    In prod mode FastAPI auto-docs (/docs, /redoc, /openapi.json) are disabled."""

    reset_interval_seconds: int
    """Background reseed interval (default 6h). See docs/business/noshow-demo-spec.md §3:
    public demo data resets periodically to avoid pollution."""


def load() -> Settings:
    """Load settings from environment. Call once at startup."""
    return Settings(
        db_path=_optional("NOSHOW_DB_PATH", "/data/noshow.db"),
        env=_optional("NOSHOW_ENV", "dev").lower(),
        reset_interval_seconds=int(
            _optional("NOSHOW_RESET_INTERVAL_SECONDS", str(6 * 3600))
        ),
    )
