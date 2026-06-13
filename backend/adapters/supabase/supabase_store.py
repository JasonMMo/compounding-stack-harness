"""
supabase_store.py — Supabase PostgREST entity store.

Implements the same 6-method interface as InMemoryEntityStore (store.py in the
fastapi adapter). Injected via sys.modules["store"] in main.py so shared
routers resolve `from store import entity_store` to this module.

Slug → table resolution:
    Reads presets/ddl/catalog.yaml (same _REPO_ROOT logic as catalog_validator.py)
    and builds a slug→table map at import time. If a slug is absent from the
    catalog, falls back to slug.replace("-", "_") (schema-less pass-through,
    matching catalog_validator's tolerance).

PostgREST semantics:
    Base URL: SUPABASE_URL/rest/v1  (from supabase_client)
    Auth: apikey + Authorization Bearer (service_role — bypasses RLS by design
          for the M1 demo tier; RLS can be enforced per-tenant in M5).

Open loops:
    - TODO(scale): filter/sort/paging currently done in Python (entity router).
      For scale, push WHERE/ORDER BY/LIMIT/OFFSET down to PostgREST query params.
    - TODO(auth): Supabase Auth (GoTrue) integration deferred — currently reuses
      demo auth from shared routers/auth.py (in-memory demo/demo). Real multi-
      user auth requires JWT from GoTrue + per-user RLS policies.
"""

from __future__ import annotations

import pathlib
from typing import Any

import yaml

# ── catalog slug→table map ────────────────────────────────────────────────────
# Mirrors catalog_validator.py _REPO_ROOT resolution:
#   this file: backend/adapters/supabase/supabase_store.py
#   parents[0] = backend/adapters/supabase
#   parents[1] = backend/adapters
#   parents[2] = backend
#   parents[3] = repo root
_ADAPTER_DIR = pathlib.Path(__file__).resolve().parent
_REPO_ROOT = _ADAPTER_DIR.parents[2]
_CATALOG_PATH = _REPO_ROOT / "presets" / "ddl" / "catalog.yaml"


def _build_slug_table_map() -> dict[str, str]:
    """
    Load catalog.yaml and return {slug: table_name} mapping.
    Fails gracefully: if catalog is unreadable, logs a warning and returns {}.
    """
    try:
        with _CATALOG_PATH.open(encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
    except Exception as exc:
        print(
            f"[supabase_store] WARN: could not load catalog at {_CATALOG_PATH}: {exc}. "
            "Slug→table resolution will use slug.replace('-','_') fallback.",
            flush=True,
        )
        return {}

    entities: dict[str, Any] = doc.get("entities") or {}
    slug_map: dict[str, str] = {}
    for slug, defn in entities.items():
        if isinstance(defn, dict) and defn.get("table"):
            slug_map[slug] = defn["table"]
        else:
            # No table field → default to slug with - replaced by _
            slug_map[slug] = slug.replace("-", "_")

    print(
        f"[supabase_store] slug→table map loaded: {len(slug_map)} entries",
        flush=True,
    )
    return slug_map


_SLUG_TABLE_MAP: dict[str, str] = _build_slug_table_map()


def _resolve_table(entity_type: str) -> str:
    """
    Map an entity_type slug to a PostgREST table name.
    Catalog hit → catalog table name (e.g. "employee" → "hr_employee").
    Catalog miss → slug.replace("-", "_") (schema-less pass-through).
    """
    return _SLUG_TABLE_MAP.get(entity_type, entity_type.replace("-", "_"))


# ── SupabaseEntityStore ───────────────────────────────────────────────────────

class SupabaseEntityStore:
    """
    PostgREST-backed entity store.

    All methods are synchronous (called from async handlers without await,
    same pattern as InMemoryEntityStore in the fastapi adapter).

    Raises httpx.HTTPStatusError on unexpected non-2xx responses so the
    status.health endpoint can surface degraded state.
    """

    # create ──────────────────────────────────────────────────────────────────

    def create(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        POST /{table} with Prefer: return=representation.
        Postgres populates id (gen_random_uuid()), created_at, updated_at.
        Returns the persisted representation row.
        """
        from supabase_client import _CLIENT

        table = _resolve_table(entity_type)
        resp = _CLIENT.post(
            f"/{table}",
            json=data,
            headers={"Prefer": "return=representation"},
        )
        resp.raise_for_status()
        rows: list[dict[str, Any]] = resp.json()
        # PostgREST returns a JSON array even for single-row inserts
        return rows[0]

    # find_by_id ──────────────────────────────────────────────────────────────

    def find_by_id(self, entity_type: str, id_: str) -> dict[str, Any] | None:
        """
        GET /{table}?id=eq.{id}&limit=1 → first row or None (miss).
        """
        from supabase_client import _CLIENT

        table = _resolve_table(entity_type)
        resp = _CLIENT.get(
            f"/{table}",
            params={"id": f"eq.{id_}", "limit": "1"},
        )
        resp.raise_for_status()
        rows: list[dict[str, Any]] = resp.json()
        return rows[0] if rows else None

    # find_all ────────────────────────────────────────────────────────────────

    def find_all(self, entity_type: str) -> list[dict[str, Any]]:
        """
        GET /{table} → full list.

        Filter/sort/paging is intentionally done in the entity router (Python-
        side), matching the fastapi adapter's contract.

        TODO(scale): push filter/sort/paging down to PostgREST query params
        (PostgREST WHERE clause syntax, order=col.asc, limit/offset) to avoid
        loading entire tables for large datasets.
        """
        from supabase_client import _CLIENT

        table = _resolve_table(entity_type)
        resp = _CLIENT.get(f"/{table}")
        resp.raise_for_status()
        return resp.json()

    # patch ───────────────────────────────────────────────────────────────────

    def patch(
        self, entity_type: str, id_: str, patch_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        PATCH /{table}?id=eq.{id} with Prefer: return=representation.
        'id' is stripped from patch_data (not overwritable — PATCH semantics).
        Returns updated row, or None if no rows matched (missing id).
        """
        from supabase_client import _CLIENT

        table = _resolve_table(entity_type)

        # Guard: id is not overwritable (matches InMemoryEntityStore behaviour)
        safe_patch = {k: v for k, v in patch_data.items() if k != "id"}

        resp = _CLIENT.patch(
            f"/{table}",
            params={"id": f"eq.{id_}"},
            json=safe_patch,
            headers={"Prefer": "return=representation"},
        )
        resp.raise_for_status()
        rows: list[dict[str, Any]] = resp.json()
        # 0 rows = id not found → None (per interface contract)
        return rows[0] if rows else None

    # delete ──────────────────────────────────────────────────────────────────

    def delete(self, entity_type: str, id_: str) -> bool:
        """
        DELETE /{table}?id=eq.{id} with Prefer: return=minimal.
        Idempotent: missing id → True (no error), per wire-v1.yaml Growth-5d.
        Always returns True.
        """
        from supabase_client import _CLIENT

        table = _resolve_table(entity_type)
        resp = _CLIENT.delete(
            f"/{table}",
            params={"id": f"eq.{id_}"},
            headers={"Prefer": "return=minimal"},
        )
        resp.raise_for_status()
        return True

    # clear_all (test helper) ─────────────────────────────────────────────────

    def clear_all(self) -> None:
        """
        Test helper: truncate all known catalog tables.

        WARNING: this is destructive. Only call from test fixtures
        that point at a dedicated test Supabase project.

        Iterates over _SLUG_TABLE_MAP values; tables not in the catalog
        are not touched (no way to enumerate unknown tables safely).
        """
        from supabase_client import _CLIENT

        seen: set[str] = set()
        for table in _SLUG_TABLE_MAP.values():
            if table in seen:
                continue
            seen.add(table)
            try:
                # DELETE without a filter deletes all rows (PostgREST convention)
                resp = _CLIENT.delete(
                    f"/{table}",
                    params={"id": "neq.00000000-0000-0000-0000-000000000000"},
                    headers={"Prefer": "return=minimal"},
                )
                resp.raise_for_status()
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[supabase_store] clear_all: could not clear {table}: {exc}",
                    flush=True,
                )


# ── module-level singleton ────────────────────────────────────────────────────
# Injected into sys.modules["store"] by main.py before shared routers are
# imported. Shared routers resolve `from store import entity_store` here.
entity_store = SupabaseEntityStore()
