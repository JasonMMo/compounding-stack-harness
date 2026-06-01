"""
contract_loader.py — Runtime loader for middle/contract/ YAML files.

G-1 compliance: reads codes.yaml and wire-v1.yaml at startup.
No error code → http_status mappings are hardcoded here.
Mirrors ContractLoader.java behavior exactly.
"""

import pathlib
from typing import Any

import yaml

# Resolve middle/contract/ relative to this file's location.
# This file lives at backend/adapters/fastapi/contract_loader.py
# middle/contract/ is three levels up, then down into middle/contract/
_ADAPTER_DIR = pathlib.Path(__file__).resolve().parent
_REPO_ROOT = _ADAPTER_DIR.parents[2]  # up from fastapi/ → adapters/ → backend/ → repo root
_CONTRACT_DIR = _REPO_ROOT / "middle" / "contract"

_CODES_PATH = _CONTRACT_DIR / "error" / "codes.yaml"
_WIRE_PATH = _CONTRACT_DIR / "wire-v1.yaml"


class ContractLoader:
    """
    Loads middle/contract/ YAML files at startup.
    Provides http_status and message lookups for error codes.
    Provides wire contract version for status.health responses.
    """

    def __init__(self) -> None:
        self._codes_doc: dict[str, Any] = {}
        self._wire_doc: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        with _CODES_PATH.open(encoding="utf-8") as f:
            self._codes_doc = yaml.safe_load(f) or {}
        with _WIRE_PATH.open(encoding="utf-8") as f:
            self._wire_doc = yaml.safe_load(f) or {}

        codes = self._codes_doc.get("codes", {})
        if not codes:
            raise RuntimeError(
                f"ContractLoader: codes.yaml loaded but 'codes' map is empty. "
                f"Checked path: {_CODES_PATH}"
            )

        import logging
        logging.getLogger(__name__).info(
            "ContractLoader: loaded %d error codes from codes.yaml; "
            "wire version = %s",
            len(codes),
            self._wire_doc.get("version", "unknown"),
        )

    # ── public API (mirrors ContractLoader.java) ──────────────────────────────

    def http_status_for(self, code: str) -> int:
        """Return the HTTP status integer for a given error code from codes.yaml."""
        codes: dict = self._codes_doc.get("codes", {})
        entry: dict = codes.get(code, {})
        status = entry.get("http_status")
        if isinstance(status, int):
            return status
        if isinstance(status, float):
            return int(status)
        return 500  # defensive fallback — should not happen for valid codes

    def message_for(self, code: str) -> str:
        """Return the English message for a given error code from codes.yaml."""
        codes: dict = self._codes_doc.get("codes", {})
        entry: dict = codes.get(code, {})
        msg = entry.get("message")
        if msg:
            return str(msg)
        return f"An error occurred ({code})."

    def wire_version(self) -> str:
        """Return the contract version string from wire-v1.yaml."""
        v = self._wire_doc.get("version")
        return str(v) if v else "unknown"


# Module-level singleton — loaded once at import time (mirrors @PostConstruct)
contract = ContractLoader()
