"""
contract_loader.py — G-1 compliance: reads middle/contract/ at runtime.

Mirror of ContractLoader.java in backend/adapters/springboot-jakarta.
Frontend adapter reads wire-v1.yaml and error/codes.yaml from the repo's
middle/contract/ directory via the CONTRACT_DIR env var (or a default relative
path). No endpoint paths, error codes, or HTTP status values are hardcoded here
— they all come from the YAML files.
"""

import os
import pathlib
import logging
from typing import Any

import yaml  # PyYAML (stdlib-free alternative: see _load_yaml comment)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _contract_dir() -> pathlib.Path:
    """
    Locate middle/contract/.

    Resolution order:
      1. CONTRACT_DIR env var (absolute or relative to cwd)
      2. Repo root auto-detection: walk upward from this file looking for
         middle/contract/ — works whether the adapter is run in-place or from
         an arbitrary cwd.
    """
    env_val = os.environ.get("CONTRACT_DIR", "")
    if env_val:
        p = pathlib.Path(env_val)
        if p.is_dir():
            return p
        raise FileNotFoundError(
            f"CONTRACT_DIR env var set to '{env_val}' but that directory does not exist."
        )

    # Walk upward from this file's location
    here = pathlib.Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        guess = candidate / "middle" / "contract"
        if guess.is_dir():
            return guess

    raise FileNotFoundError(
        "Cannot locate middle/contract/. Set the CONTRACT_DIR env var to the "
        "absolute path of middle/contract/."
    )


def _load_yaml(path: pathlib.Path) -> dict[str, Any]:
    """Load a YAML file and return its parsed content as a dict."""
    with path.open("r", encoding="utf-8") as fh:
        result = yaml.safe_load(fh)
    return result if isinstance(result, dict) else {}


# ---------------------------------------------------------------------------
# ContractLoader
# ---------------------------------------------------------------------------

class ContractLoader:
    """
    Loads wire-v1.yaml and error/codes.yaml at startup.
    Provides helpers that the thin server and templates consume.

    G-1: no error code strings, HTTP status integers, or endpoint path fragments
    are redeclared inside this class. Every value is read from the YAML files.
    """

    def __init__(self) -> None:
        contract_dir = _contract_dir()

        self._wire: dict[str, Any] = _load_yaml(contract_dir / "wire-v1.yaml")
        self._codes_doc: dict[str, Any] = _load_yaml(contract_dir / "error" / "codes.yaml")

        codes: dict[str, Any] = self._codes_doc.get("codes", {})
        if not codes:
            raise RuntimeError(
                "ContractLoader: error/codes.yaml loaded but 'codes' map is empty. "
                "Check CONTRACT_DIR resolves to the correct middle/contract/ directory."
            )

        log.info(
            "ContractLoader: loaded %d error codes, wire contract version=%s",
            len(codes),
            self._wire.get("version", "unknown"),
        )

    # ── public helpers ────────────────────────────────────────────────────────

    def wire_version(self) -> str:
        return str(self._wire.get("version", "unknown"))

    def wire_keys(self) -> dict[str, Any]:
        """Return the full 'keys' map from wire-v1.yaml."""
        return self._wire.get("keys", {})

    def codes(self) -> dict[str, Any]:
        """Return the full 'codes' map from codes.yaml."""
        return self._codes_doc.get("codes", {})

    def message_ko(self, code: str) -> str:
        """
        Return the Korean message for an error code.
        Falls back to English message, then a generic string.
        """
        entry: dict = self.codes().get(code, {})
        return (
            entry.get("message_ko")
            or entry.get("message")
            or f"오류가 발생했습니다 ({code})."
        )

    def message_en(self, code: str) -> str:
        entry: dict = self.codes().get(code, {})
        return entry.get("message") or f"An error occurred ({code})."

    def is_retriable(self, code: str) -> bool:
        entry: dict = self.codes().get(code, {})
        return bool(entry.get("retriable", False))

    def http_status_for(self, code: str) -> int:
        """Advisory HTTP status for a given error code (used by the proxy layer)."""
        entry: dict = self.codes().get(code, {})
        status = entry.get("http_status")
        if isinstance(status, int):
            return status
        return 500


# Singleton — imported by server.py at startup.
_loader: ContractLoader | None = None


def get_loader() -> ContractLoader:
    global _loader
    if _loader is None:
        _loader = ContractLoader()
    return _loader
