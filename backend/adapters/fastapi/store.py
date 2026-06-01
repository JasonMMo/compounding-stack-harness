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
"""

from __future__ import annotations

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


# Module-level singleton shared across all routers
entity_store = InMemoryEntityStore()
