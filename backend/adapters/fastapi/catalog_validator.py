"""
catalog_validator.py — Runtime DDL catalog-driven input validator.

G-1 compliant: reads presets/ddl/catalog.yaml from the repo root at startup.
No schema data is hardcoded; the catalog is the single source of truth.

Contract (validation-contract.md §2, §3, §4):
    entity_type ∈ catalog  →  enforce schema (required/type/enum/length/unique)
    entity_type ∉ catalog  →  schema-less pass-through (backward-compat, returns [])

validate(entity_type, data, partial, current_id=None) → list[FieldError]
    partial=False (create): required + type + enum + length + unique
    partial=True  (update): type + enum + length + unique only (no required check)

Server-populated columns never required from client: id, created_at, updated_at.

FieldError.kind:
    "INVALID" → caller maps to VALIDATION_ERROR — type/enum/length/required violations
    "UNIQUE"  → caller maps to CONFLICT         — unique constraint collision

Callers collect ALL errors before responding (not fail-fast, per UX contract).

Type vocabulary (catalog neutral 8-type system):
    uuid      → any str  (format not enforced — FK UUIDs come as strings)
    string    → str
    text      → str
    integer   → int, not bool, no fractional float
    decimal   → int or float, not bool
    boolean   → bool (strict — not 0/1 or "true"/"false" strings)
    date      → str parseable as YYYY-MM-DD via datetime.date.fromisoformat
    timestamp → str parseable as ISO-8601 (datetime.datetime.fromisoformat or date fallback)
    enum      → str, value must be in catalog values[]

Mirrors CatalogValidator.java behavior exactly.
"""

from __future__ import annotations

import logging
import pathlib
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import yaml

_log = logging.getLogger(__name__)

# Resolve presets/ddl/catalog.yaml relative to this file's position.
# This file: backend/adapters/fastapi/catalog_validator.py
# Repo root: three parents up → backend/adapters/fastapi → backend/adapters → backend → repo root
_ADAPTER_DIR = pathlib.Path(__file__).resolve().parent
_REPO_ROOT = _ADAPTER_DIR.parents[2]
_CATALOG_PATH = _REPO_ROOT / "presets" / "ddl" / "catalog.yaml"

# Server-populated columns — never required from client, never checked for presence.
_SERVER_COLUMNS = frozenset({"id", "created_at", "updated_at"})


# ── FieldError ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FieldError:
    """A single field-level validation violation."""
    field:  str
    reason: str
    kind:   str  # "INVALID" | "UNIQUE"

    @classmethod
    def invalid(cls, field: str, reason: str) -> "FieldError":
        return cls(field=field, reason=reason, kind="INVALID")

    @classmethod
    def unique(cls, field: str, reason: str) -> "FieldError":
        return cls(field=field, reason=reason, kind="UNIQUE")

    def __repr__(self) -> str:
        return f"{self.kind}[{self.field}]: {self.reason}"


# ── CatalogValidator ──────────────────────────────────────────────────────────

class CatalogValidator:
    """
    Loads catalog.yaml at startup and validates entity data against the schema.
    Mirrors CatalogValidator.java API exactly.
    """

    def __init__(self) -> None:
        self._entities: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        try:
            with _CATALOG_PATH.open(encoding="utf-8") as f:
                doc = yaml.safe_load(f) or {}
        except Exception as exc:
            raise RuntimeError(
                f"CatalogValidator: failed to load {_CATALOG_PATH} — {exc}"
            ) from exc

        entities = doc.get("entities")
        if not entities:
            _log.warning(
                "CatalogValidator: catalog.yaml loaded but 'entities' map is empty. "
                "Checked path: %s", _CATALOG_PATH
            )
            self._entities = {}
        else:
            self._entities = dict(entities)
            _log.info(
                "CatalogValidator: loaded %d catalog entities from catalog.yaml",
                len(self._entities),
            )

    # ── public API ────────────────────────────────────────────────────────────

    def validate(
        self,
        entity_type: str,
        data: dict[str, Any],
        partial: bool,
        current_id: str | None = None,
        store: Any = None,
    ) -> list[FieldError]:
        """
        Validate data against the catalog schema for entity_type.

        Args:
            entity_type: e.g. "employee"
            data:        client-supplied field map
            partial:     True = PATCH (skip required); False = create (full)
            current_id:  id being updated — excluded from unique collision scan
            store:       InMemoryEntityStore instance for unique checks

        Returns:
            List of FieldError; empty = pass.
        """
        entity_def = self._entities.get(entity_type)
        if entity_def is None:
            # Not in catalog → schema-less pass-through (backward-compat).
            return []

        columns: dict[str, Any] = entity_def.get("columns") or {}
        errors: list[FieldError] = []

        for col_name, col_def in columns.items():
            if col_name in _SERVER_COLUMNS:
                continue
            if not isinstance(col_def, dict):
                continue

            col_type: str = col_def.get("type") or ""
            nullable: bool = col_def.get("nullable", True)
            present: bool = col_name in data
            value: Any = data.get(col_name)

            # ── required check (create only) ─────────────────────────────────
            if not partial and not nullable and (not present or value is None):
                errors.append(FieldError.invalid(col_name, "required field is missing or null"))
                continue  # no further checks if value absent

            # Skip if value absent (PATCH) or null+nullable
            if not present or value is None:
                continue

            # ── type check ───────────────────────────────────────────────────
            type_err = self._check_type(col_name, col_type, value)
            if type_err is not None:
                errors.append(FieldError.invalid(col_name, type_err))
                continue  # skip enum/length if type is wrong

            # ── enum check ───────────────────────────────────────────────────
            if col_type == "enum":
                allowed: list = col_def.get("values") or []
                if allowed and str(value) not in [str(v) for v in allowed]:
                    errors.append(FieldError.invalid(
                        col_name, f"must be one of {allowed}"
                    ))
                continue  # enum: no length check

            # ── length check (string/text only) ──────────────────────────────
            if col_type in ("string", "text") and isinstance(value, str):
                max_len = col_def.get("length")
                if max_len is not None and len(value) > int(max_len):
                    errors.append(FieldError.invalid(
                        col_name, f"exceeds maximum length of {max_len}"
                    ))

        # ── unique checks (run after all field-level checks) ─────────────────
        # Collect even when INVALID errors already exist (collect-all contract).
        if store is not None:
            unique_errors = self._check_unique(entity_type, columns, data, current_id, store)
            errors.extend(unique_errors)

        return errors

    # ── helpers ───────────────────────────────────────────────────────────────

    def _check_type(self, col_name: str, col_type: str, value: Any) -> str | None:
        """
        Returns a human-readable error string if the value fails the neutral type check,
        or None if it passes.

        Design choices (documented per spec requirement):
        - integer: rejects bool (isinstance(True, int) is True in Python — explicit guard
          needed). Rejects float with fractional part.
        - decimal: rejects bool. Accepts int and float.
        - boolean: strict — only Python bool accepted; "true"/"false" strings and 0/1 are
          not coerced (JSON deserialiser already produces True/False for JSON booleans).
        - date: str parseable by datetime.date.fromisoformat (YYYY-MM-DD).
        - timestamp: str parseable by datetime.datetime.fromisoformat; falls back to
          datetime.date.fromisoformat. Covers "2024-01-15T10:30:00Z" (after stripping Z).
        - uuid/string/text: any str.
        - enum: just requires str here; allowed-values check is separate.
        """
        if col_type in ("uuid", "string", "text"):
            if not isinstance(value, str):
                return "must be a string"

        elif col_type == "integer":
            if isinstance(value, bool):
                return "must be an integer (boolean is not accepted)"
            if not isinstance(value, (int, float)):
                return "must be an integer"
            if isinstance(value, float) and value != int(value):
                return "must be an integer (fractional number is not accepted)"

        elif col_type == "decimal":
            if isinstance(value, bool):
                return "must be a number (boolean is not accepted)"
            if not isinstance(value, (int, float)):
                return "must be a number (decimal)"

        elif col_type == "boolean":
            if not isinstance(value, bool):
                return "must be a boolean (true or false)"

        elif col_type == "date":
            if not isinstance(value, str):
                return "must be a date string in YYYY-MM-DD format"
            try:
                date.fromisoformat(value)
            except (ValueError, TypeError):
                return "must be a valid date in YYYY-MM-DD format"

        elif col_type == "timestamp":
            if not isinstance(value, str):
                return "must be a timestamp string in ISO-8601 format"
            ok = False
            try:
                # Normalize trailing Z → +00:00 for Python 3.10 compat
                ts = value.replace("Z", "+00:00")
                datetime.fromisoformat(ts)
                ok = True
            except (ValueError, TypeError):
                pass
            if not ok:
                try:
                    date.fromisoformat(value)
                    ok = True
                except (ValueError, TypeError):
                    pass
            if not ok:
                return "must be a valid ISO-8601 timestamp"

        elif col_type == "enum":
            if not isinstance(value, str):
                return "must be a string (enum value)"

        # Unknown type: pass through (forward-compat)
        return None

    def _check_unique(
        self,
        entity_type: str,
        columns: dict[str, Any],
        data: dict[str, Any],
        current_id: str | None,
        store: Any,
    ) -> list[FieldError]:
        """Scan unique columns against existing store records. Returns UNIQUE-kind errors."""
        errors: list[FieldError] = []

        for col_name, col_def in columns.items():
            if col_name in _SERVER_COLUMNS:
                continue
            if not isinstance(col_def, dict):
                continue
            if not col_def.get("unique"):
                continue

            new_val = data.get(col_name)
            if new_val is None:
                continue

            new_val_str = str(new_val)
            all_records: list[dict] = store.find_all(entity_type)
            for record in all_records:
                # Exclude the record being updated from collision check.
                if current_id is not None and str(record.get("id")) == current_id:
                    continue
                existing = record.get(col_name)
                if existing is not None and str(existing) == new_val_str:
                    errors.append(FieldError.unique(col_name, "must be unique"))
                    break  # one collision per column is enough

        return errors


# ── module-level singleton ────────────────────────────────────────────────────
# Loaded once at import time — mirrors @PostConstruct pattern in Java.
catalog_validator = CatalogValidator()
