"""
store.py — Generic in-memory entity store.

Structure: entity_type → (id → field map).
Thread-safe via threading.Lock per entity_type bucket.

Mirrors InMemoryEntityStore.java behavior:
- create: UUID id, adds created_at/updated_at epoch ms
- findById: returns copy or None
- findAll: returns list of copies (no filter/sort — done in router)
- patch: merges only supplied fields; 'id' field not overwritable; NOT_FOUND → None
- delete: idempotent — missing id returns True (not an error)

Seed file (optional):
  Set env SEED_FILE=/path/to/seed-data.json to pre-populate the store at
  module import time. If the file does not exist or is unset, the store
  starts empty (backward-compatible). Duplicate ids within the same
  entity_type are skipped (last writer wins — stable because seed is
  deterministic). Loaded record count is logged once to stdout.
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from typing import Any


class InMemoryEntityStore:
    def __init__(self) -> None:
        # outer dict keyed by entity_type (str)
        # inner dict keyed by id (str) → field map (dict)
        self._store: dict[str, dict[str, dict[str, Any]]] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._meta_lock = threading.Lock()  # guards creation of new type buckets

    def _get_or_create_bucket(
        self, entity_type: str
    ) -> tuple[dict[str, dict[str, Any]], threading.Lock]:
        with self._meta_lock:
            if entity_type not in self._store:
                self._store[entity_type] = {}
                self._locks[entity_type] = threading.Lock()
            return self._store[entity_type], self._locks[entity_type]

    # ── create ────────────────────────────────────────────────────────────────

    def create(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new record. Returns persisted record including generated id."""
        new_id = str(uuid.uuid4())
        now = int(time.time() * 1000)

        record: dict[str, Any] = dict(data)
        record["id"] = new_id
        record.setdefault("created_at", now)
        record["updated_at"] = now

        bucket, lock = self._get_or_create_bucket(entity_type)
        with lock:
            bucket[new_id] = record

        return dict(record)

    # ── read ──────────────────────────────────────────────────────────────────

    def find_by_id(self, entity_type: str, id_: str) -> dict[str, Any] | None:
        bucket, lock = self._get_or_create_bucket(entity_type)
        with lock:
            record = bucket.get(id_)
            return dict(record) if record is not None else None

    # ── list ──────────────────────────────────────────────────────────────────

    def find_all(self, entity_type: str) -> list[dict[str, Any]]:
        """Return all records for the entity_type. No filter/sort applied here."""
        bucket, lock = self._get_or_create_bucket(entity_type)
        with lock:
            return [dict(r) for r in bucket.values()]

    # ── update (PATCH semantics) ───────────────────────────────────────────────

    def patch(
        self, entity_type: str, id_: str, patch_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Partial update: only supplied fields replaced; absent fields unchanged.
        'id' field is not overwritable.
        Returns updated record or None if id does not exist.
        """
        bucket, lock = self._get_or_create_bucket(entity_type)
        with lock:
            existing = bucket.get(id_)
            if existing is None:
                return None

            updated = dict(existing)
            for k, v in patch_data.items():
                if k != "id":  # guard: id is not overwritable
                    updated[k] = v
            updated["updated_at"] = int(time.time() * 1000)
            bucket[id_] = updated
            return dict(updated)

    # ── delete (idempotent) ────────────────────────────────────────────────────

    def delete(self, entity_type: str, id_: str) -> bool:
        """
        Remove a record. Idempotent per wire-v1.yaml Growth-5d:
        missing id → True (not an error).
        """
        bucket, lock = self._get_or_create_bucket(entity_type)
        with lock:
            bucket.pop(id_, None)  # pop with default: no-op if absent
        return True

    # ── test helper ───────────────────────────────────────────────────────────

    def clear_all(self) -> None:
        with self._meta_lock:
            self._store.clear()
            self._locks.clear()


# ---------------------------------------------------------------------------
# Seed loader — reads SEED_FILE env at import time (optional)
# ---------------------------------------------------------------------------

def _load_seed_file(store: "InMemoryEntityStore") -> None:
    """Load seed-data.json into store if SEED_FILE env is set and file exists.

    Format: { "<entity_type>": [ {id, field...}, ... ], ... }
    Each record must have an "id" field; records without "id" are skipped.
    Duplicate ids within an entity_type are silently overwritten (last wins —
    seed is deterministic so this is safe).
    Logs one summary line per entity_type to stdout.
    """
    seed_path = os.environ.get("SEED_FILE", "").strip()
    if not seed_path:
        return  # env unset — backward-compatible empty store

    import pathlib
    p = pathlib.Path(seed_path)
    if not p.exists():
        print(
            f"[store] WARN: SEED_FILE={seed_path} not found — starting with empty store.",
            flush=True,
        )
        return

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[store] WARN: SEED_FILE parse error ({exc}) — starting with empty store.", flush=True)
        return

    if not isinstance(data, dict):
        print("[store] WARN: SEED_FILE root must be a JSON object — starting with empty store.", flush=True)
        return

    total = 0
    for entity_type, records in data.items():
        if not isinstance(records, list):
            continue
        bucket, lock = store._get_or_create_bucket(entity_type)
        loaded = 0
        with lock:
            for rec in records:
                if not isinstance(rec, dict):
                    continue
                rid = rec.get("id")
                if not rid:
                    continue
                bucket[str(rid)] = dict(rec)
                loaded += 1
        print(f"[store] seed loaded: {entity_type} → {loaded} records", flush=True)
        total += loaded

    print(f"[store] seed total: {total} records from {seed_path}", flush=True)


# Module-level singleton shared across all routers
entity_store = InMemoryEntityStore()
_load_seed_file(entity_store)
