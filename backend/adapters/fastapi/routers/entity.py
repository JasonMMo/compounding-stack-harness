"""
routers/entity.py — entity domain router.

Wire key → HTTP mapping:
  entity.read   → GET    /api/entities/{entity_type}/{id}
  entity.list   → GET    /api/entities/{entity_type}
  entity.create → POST   /api/entities/{entity_type}
  entity.update → PATCH  /api/entities/{entity_type}/{id}   (PATCH semantics)
  entity.delete → DELETE /api/entities/{entity_type}/{id}   (idempotent)

Critical compliance points (mirroring EntityController.java):
- Flat-underscore paging params: paging_mode, page, size (NOT dot-notation).
  Also accepts paging.mode as legacy fallback (BUG-2 pattern from springboot).
- Cursor mode → BAD_REQUEST (not implemented, same as springboot adapter).
- Offset last-page: correct partial slice — no off-by-one.
- Idempotent delete: missing id → success (not NOT_FOUND).
- PATCH: only supplied fields merged; 'id' not overwritable; absent fields unchanged.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

import wire_response
from store import entity_store

router = APIRouter(prefix="/api/entities", tags=["entity"])

# Query params that are reserved for paging/sort (not passed to filter)
_RESERVED_KEYS = frozenset(
    {
        "page",
        "size",
        "paging_mode",
        "paging.mode",
        "cursor",
        "paging_cursor",
        "sort_field",
        "sort.field",
        "sort_direction",
        "sort.direction",
    }
)


def _parse_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _matches_filter(record: dict[str, Any], filter_: dict[str, str]) -> bool:
    for k, v in filter_.items():
        val = record.get(k)
        if val is None or str(val) != v:
            return False
    return True


def _compare_field(a: dict[str, Any], b: dict[str, Any], field: str, desc: bool) -> int:
    va = a.get(field)
    vb = b.get(field)
    if va is None and vb is None:
        return 0
    if va is None:
        return 1 if desc else -1
    if vb is None:
        return -1 if desc else 1
    try:
        cmp = (va > vb) - (va < vb)
    except TypeError:
        cmp = (str(va) > str(vb)) - (str(va) < str(vb))
    return -cmp if desc else cmp


# ── entity.read ───────────────────────────────────────────────────────────────

@router.get("/{entity_type}/{id}")
async def read(entity_type: str, id: str) -> JSONResponse:
    record = entity_store.find_by_id(entity_type, id)
    if record is None:
        return wire_response.error("NOT_FOUND")
    return wire_response.ok({"entity_type": entity_type, "id": id, "data": record})


# ── entity.list ───────────────────────────────────────────────────────────────

@router.get("/{entity_type}")
async def list_entities(entity_type: str, request: Request) -> JSONResponse:
    params: dict[str, str] = dict(request.query_params)

    # BUG-2 pattern: accept paging_mode (dot-free, preferred) OR paging.mode (legacy)
    paging_mode = params.get("paging_mode") or params.get("paging.mode") or "offset"

    if paging_mode == "cursor":
        return wire_response.error(
            "BAD_REQUEST",
            {"reason": "cursor paging not yet implemented; use paging_mode=offset"},
        )

    page = max(1, _parse_int(params.get("page"), 1))
    size = max(1, _parse_int(params.get("size"), 20))

    sort_field = params.get("sort_field") or params.get("sort.field")
    sort_direction = params.get("sort_direction") or params.get("sort.direction") or "asc"

    # Filter: all params not in reserved set
    filter_: dict[str, str] = {k: v for k, v in params.items() if k not in _RESERVED_KEYS}

    all_records = entity_store.find_all(entity_type)

    # Apply filter
    filtered = [r for r in all_records if _matches_filter(r, filter_)]

    # Apply sort
    if sort_field:
        import functools

        def _cmp(a: dict, b: dict) -> int:
            return _compare_field(a, b, sort_field, desc=(sort_direction == "desc"))

        filtered.sort(key=functools.cmp_to_key(_cmp))

    # Offset paging slice — 1-based page
    total = len(filtered)
    from_idx = min((page - 1) * size, total)
    to_idx = min(from_idx + size, total)
    page_items = filtered[from_idx:to_idx]

    return wire_response.ok(
        {"entity_type": entity_type, "items": page_items, "total": total}
    )


# ── entity.create ─────────────────────────────────────────────────────────────

@router.post("/{entity_type}", status_code=201)
async def create(entity_type: str, body: dict[str, Any] | None = None) -> JSONResponse:
    if body is None:
        return wire_response.error("BAD_REQUEST", {"reason": "request body with 'data' field is required"})

    data = body.get("data") if "data" in body else body
    if not data:
        return wire_response.error("BAD_REQUEST", {"reason": "'data' field is required"})

    created = entity_store.create(entity_type, data)

    return JSONResponse(
        content={
            "entity_type": entity_type,
            "id": created["id"],
            "data": created,
        },
        status_code=201,
    )


# ── entity.update (PATCH) ─────────────────────────────────────────────────────

@router.patch("/{entity_type}/{id}")
async def update(entity_type: str, id: str, body: dict[str, Any] | None = None) -> JSONResponse:
    if body is None:
        return wire_response.error("BAD_REQUEST", {"reason": "PATCH body with fields to update is required"})

    patch_data = body.get("data") if "data" in body else body
    if not patch_data:
        return wire_response.error(
            "BAD_REQUEST",
            {"reason": "'data' field with at least one field to update is required"},
        )

    updated = entity_store.patch(entity_type, id, patch_data)
    if updated is None:
        return wire_response.error("NOT_FOUND")

    return wire_response.ok({"entity_type": entity_type, "id": id, "data": updated})


# ── entity.delete (idempotent) ────────────────────────────────────────────────

@router.delete("/{entity_type}/{id}")
async def delete(entity_type: str, id: str) -> JSONResponse:
    # Idempotent per wire-v1.yaml Growth-5d: missing id → success, not NOT_FOUND
    entity_store.delete(entity_type, id)
    return wire_response.ok({"success": True})
