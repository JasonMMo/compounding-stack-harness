"""
apps/intake/audit.py — append-only, hash-chained per-client audit log.

2-tier architecture (Phase 1b):
  VPS/PII tier : DATA_DIR/clients/<client_id>/audit.jsonl
                 Each line is a JSON record; prev_hash = SHA256(previous raw line bytes).
                 Genesis record uses prev_hash = "0" * 64.
                 data dict MAY contain PII (email, free-text) — VPS only, gitignored.

  Repo tier    : infra/registry/cases/<client_id>.yaml
                 Written by the LOCAL bridge (Phase 4) via case_snapshot().
                 PII-free: slug, score, event_type list, timestamps only.

stdlib + PyYAML. LLM 0. No external dependencies beyond standard library.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EVENT_TYPES: frozenset[str] = frozenset({
    "INTAKE_SUBMITTED",
    "TRIAGE_DECIDED",
    "PROFILE_CONFIRMED",
    "PREVIEW_BUILT",
    "UI_CHECKED",
    "NEEDS_FIT_VERDICT",
    "DELIVERED",
    "FEEDBACK",
    "ENGAGEMENT_CLOSED",
    "NODE_ENTER",
    "NODE_EXIT_OK",
    "NODE_FAIL",
})

# PII keys that must NEVER appear in case_snapshot output
_PII_KEYS: frozenset[str] = frozenset({
    "email",
    "contact_email",
    "phone",
    "name",
    "company_name",
    "free_text",
    "note",
    "description",
    "message",
    "address",
    "contact",
})

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _resolve_data_dir(data_dir: str | os.PathLike | None) -> Path:
    """Resolve DATA_DIR with same fallback logic as app.py _data_dir()."""
    if data_dir is not None:
        return Path(data_dir)
    env = os.environ.get("DATA_DIR")
    if env:
        return Path(env)
    # Default: apps/intake/data (relative to this file)
    return Path(__file__).resolve().parent / "data"


def _audit_path(client_id: str, data_dir: str | os.PathLike | None = None) -> Path:
    base = _resolve_data_dir(data_dir)
    return base / "clients" / client_id / "audit.jsonl"

# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------

_GENESIS_HASH = "0" * 64


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def append_event(
    client_id: str,
    event_type: str,
    data: dict[str, Any] | None = None,
    *,
    node: str | None = None,
    error_class: str | None = None,
    data_dir: str | os.PathLike | None = None,
) -> dict:
    """Append one event to the client's audit.jsonl.

    Validates event_type; computes prev_hash from last raw line bytes;
    writes atomically (open 'a'); returns the written record dict.

    Raises ValueError for unknown event_type.
    """
    if event_type not in EVENT_TYPES:
        raise ValueError(
            f"Unknown event_type {event_type!r}. "
            f"Must be one of: {sorted(EVENT_TYPES)}"
        )

    path = _audit_path(client_id, data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing content once; derive both seq and prev_hash from it.
    # Use .splitlines() so hash computation is consistent across OS line endings.
    existing_lines: list[bytes] = []
    if path.exists():
        raw_bytes = path.read_bytes()
        if raw_bytes:
            existing_lines = [l for l in raw_bytes.splitlines() if l.strip()]

    seq = len(existing_lines)
    prev_hash = _sha256_bytes(existing_lines[-1]) if existing_lines else _GENESIS_HASH

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    record: dict[str, Any] = {
        "seq": seq,
        "ts": ts,
        "event_type": event_type,
        "node": node,
        "error_class": error_class,
        "prev_hash": prev_hash,
        "data": data or {},
    }

    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))

    # Append — atomic enough for single-writer VPS usage.
    # Open in binary mode to guarantee \n-only line endings on all platforms
    # (avoids \r\n on Windows, keeping hash-chain stable across OS boundaries).
    with open(path, "ab") as fh:
        fh.write((line + "\n").encode("utf-8"))

    return record


def read_events(
    client_id: str,
    data_dir: str | os.PathLike | None = None,
) -> list[dict]:
    """Return all events for client_id in seq order (empty list if no log)."""
    path = _audit_path(client_id, data_dir)
    if not path.exists():
        return []
    events = []
    for raw_line in path.read_bytes().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        events.append(json.loads(line.decode("utf-8")))
    return events


def get_last_event(
    client_id: str,
    data_dir: str | os.PathLike | None = None,
) -> dict | None:
    """Return the last event record, or None if the log is empty/absent."""
    events = read_events(client_id, data_dir)
    return events[-1] if events else None


def verify_chain(
    client_id: str,
    data_dir: str | os.PathLike | None = None,
) -> tuple[bool, str]:
    """Recompute prev_hash chain.

    Returns (True, "CHAIN OK") if all links are valid.
    Returns (False, "broken at seq N") on the first bad link.
    """
    path = _audit_path(client_id, data_dir)
    if not path.exists():
        return True, "CHAIN OK"

    raw_lines = [l for l in path.read_bytes().splitlines() if l.strip()]
    if not raw_lines:
        return True, "CHAIN OK"

    # Genesis: first record must have prev_hash == "0"*64
    first_record = json.loads(raw_lines[0].decode("utf-8"))
    if first_record.get("prev_hash") != _GENESIS_HASH:
        return False, "broken at seq 0 (genesis prev_hash mismatch)"

    for i in range(1, len(raw_lines)):
        expected_prev = _sha256_bytes(raw_lines[i - 1])
        record = json.loads(raw_lines[i].decode("utf-8"))
        actual_prev = record.get("prev_hash", "")
        if actual_prev != expected_prev:
            seq = record.get("seq", i)
            return False, f"broken at seq {seq}"

    return True, "CHAIN OK"


def seal_log(
    client_id: str,
    data_dir: str | os.PathLike | None = None,
) -> str:
    """Compute SEAL_HASH = SHA256(full file bytes).

    Appends an ENGAGEMENT_CLOSED seal record to mark the log as sealed
    and returns the hex hash of the file content AT THE TIME OF SEALING
    (before the seal record itself is appended — this is the evidence hash).

    If the log does not exist, returns SHA256 of empty bytes.
    """
    path = _audit_path(client_id, data_dir)

    if not path.exists():
        return _sha256_bytes(b"")

    seal_hash = _sha256_file(path)

    # Append a seal record (ENGAGEMENT_CLOSED companion)
    append_event(
        client_id,
        "ENGAGEMENT_CLOSED",
        data={"seal_hash": seal_hash, "sealed": True},
        node="SEAL",
        data_dir=data_dir,
    )

    return seal_hash


def case_snapshot(
    client_id: str,
    data_dir: str | os.PathLike | None = None,
) -> dict:
    """Return a PII-free projection suitable for infra/registry/cases/<id>.yaml.

    Fields included: client_id (hash prefix, not email), events list
    (event_type, ts, node, error_class only), last_event_type, event_count.
    NO email, free-text, company name, or any PII key from data dicts.
    """
    events = read_events(client_id, data_dir)

    pii_free_events = []
    for ev in events:
        pii_free_events.append({
            "seq": ev.get("seq"),
            "ts": ev.get("ts"),
            "event_type": ev.get("event_type"),
            "node": ev.get("node"),
            "error_class": ev.get("error_class"),
        })

    # Extract safe scalar fields from data dicts (score, status, slug — never free-text)
    score: int | None = None
    status: str | None = None
    slug: str | None = None
    for ev in events:
        d = ev.get("data", {})
        if "score" in d and isinstance(d["score"], (int, float)):
            score = int(d["score"])
        if "status" in d and isinstance(d["status"], str):
            # Only accept known safe enum-like status values
            cand = str(d["status"])
            if cand in {"qualify", "defer", "gap_only", "closed", "live", "retired"}:
                status = cand
        if "slug" in d and isinstance(d["slug"], str):
            # slug is ASCII safe by G-8
            s = str(d["slug"])
            if s.isascii() and all(c.isalnum() or c in "-_" for c in s):
                slug = s

    last_event_type: str | None = (
        events[-1].get("event_type") if events else None
    )

    return {
        "client_id": client_id,
        "slug": slug,
        "score": score,
        "status": status,
        "last_event_type": last_event_type,
        "event_count": len(events),
        "events": pii_free_events,
    }
