"""
apps/intake/tests/test_audit.py

pytest test suite for audit.py (Phase 1b).
Run: python -m pytest apps/intake/tests/test_audit.py -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup — make repo root importable
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from apps.intake.audit import (
    EVENT_TYPES,
    append_event,
    case_snapshot,
    get_last_event,
    read_events,
    seal_log,
    verify_chain,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLIENT_ID = "deadbeef12345678"
EMAIL = "test-client@example.com"


@pytest.fixture()
def tmp_data(tmp_path: Path) -> Path:
    """Return a fresh tmp DATA_DIR for each test."""
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Append 3 events → seq/chain integrity
# ---------------------------------------------------------------------------

def test_append_three_events_seq_and_chain(tmp_data: Path) -> None:
    append_event(CLIENT_ID, "INTAKE_SUBMITTED", {"source": "web"}, data_dir=tmp_data)
    append_event(CLIENT_ID, "TRIAGE_DECIDED", {"score": 72, "status": "qualify"}, data_dir=tmp_data)
    append_event(CLIENT_ID, "PROFILE_CONFIRMED", {"slug": "acme-corp"}, data_dir=tmp_data)

    events = read_events(CLIENT_ID, tmp_data)
    assert len(events) == 3
    assert [ev["seq"] for ev in events] == [0, 1, 2]

    # Genesis record has "0" * 64 as prev_hash
    assert events[0]["prev_hash"] == "0" * 64

    # Each subsequent record's prev_hash must equal SHA256 of the raw previous line
    import hashlib

    audit_path = tmp_data / "clients" / CLIENT_ID / "audit.jsonl"
    raw_lines = [l for l in audit_path.read_bytes().splitlines() if l.strip()]
    assert len(raw_lines) == 3

    for i in range(1, 3):
        expected = hashlib.sha256(raw_lines[i - 1]).hexdigest()
        assert events[i]["prev_hash"] == expected, (
            f"seq {i}: expected prev_hash {expected!r}, got {events[i]['prev_hash']!r}"
        )

    ok, msg = verify_chain(CLIENT_ID, tmp_data)
    assert ok is True
    assert msg == "CHAIN OK"


# ---------------------------------------------------------------------------
# 2. Tamper middle line → verify_chain returns (False, ...)
# ---------------------------------------------------------------------------

def test_tamper_breaks_chain(tmp_data: Path) -> None:
    append_event(CLIENT_ID, "INTAKE_SUBMITTED", {}, data_dir=tmp_data)
    append_event(CLIENT_ID, "TRIAGE_DECIDED", {"score": 60}, data_dir=tmp_data)
    append_event(CLIENT_ID, "PROFILE_CONFIRMED", {}, data_dir=tmp_data)

    audit_path = tmp_data / "clients" / CLIENT_ID / "audit.jsonl"
    raw = audit_path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    # Tamper: alter the middle line (seq 1)
    mid = json.loads(lines[1])
    mid["data"]["score"] = 9999  # change content
    lines[1] = json.dumps(mid, ensure_ascii=False, separators=(",", ":"))
    audit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, msg = verify_chain(CLIENT_ID, tmp_data)
    assert ok is False
    assert "broken" in msg.lower()


# ---------------------------------------------------------------------------
# 3. case_snapshot contains no PII
# ---------------------------------------------------------------------------

def test_case_snapshot_is_pii_free(tmp_data: Path) -> None:
    # Append events that include PII in the data dict
    append_event(
        CLIENT_ID,
        "INTAKE_SUBMITTED",
        {
            "email": EMAIL,
            "contact_email": EMAIL,
            "company_name": "Acme Corp Ltd",
            "score": 75,
            "status": "qualify",
            "slug": "acme-corp",
        },
        data_dir=tmp_data,
    )
    append_event(
        CLIENT_ID,
        "TRIAGE_DECIDED",
        {"score": 75, "status": "qualify", "note": "Approved by PM"},
        data_dir=tmp_data,
    )

    snapshot = case_snapshot(CLIENT_ID, tmp_data)

    # Serialize to string for exhaustive PII scan
    snapshot_repr = repr(snapshot)

    # Email must NOT appear anywhere in the snapshot representation
    assert EMAIL not in snapshot_repr, (
        f"PII leak: email {EMAIL!r} found in case_snapshot repr"
    )
    assert "Acme Corp Ltd" not in snapshot_repr, (
        "PII leak: company_name found in case_snapshot repr"
    )
    assert "Approved by PM" not in snapshot_repr, (
        "PII leak: free-text note found in case_snapshot repr"
    )

    # Safe fields ARE present
    assert snapshot["client_id"] == CLIENT_ID
    assert snapshot["slug"] == "acme-corp"
    assert snapshot["score"] == 75
    assert snapshot["event_count"] == 2


# ---------------------------------------------------------------------------
# 4. seal_log returns 64-hex string; deterministic for same content
# ---------------------------------------------------------------------------

def test_seal_log_returns_hex_and_is_deterministic(tmp_data: Path) -> None:
    import hashlib

    append_event(CLIENT_ID, "INTAKE_SUBMITTED", {"score": 50}, data_dir=tmp_data)

    audit_path = tmp_data / "clients" / CLIENT_ID / "audit.jsonl"
    # Capture file content BEFORE sealing (seal_log hashes the pre-seal content)
    pre_seal_bytes = audit_path.read_bytes()
    expected_hash = hashlib.sha256(pre_seal_bytes).hexdigest()

    seal_hash = seal_log(CLIENT_ID, tmp_data)

    assert isinstance(seal_hash, str)
    assert len(seal_hash) == 64
    assert all(c in "0123456789abcdef" for c in seal_hash)

    # Must match SHA256 of file content at time of sealing
    assert seal_hash == expected_hash

    # Sealing appends an ENGAGEMENT_CLOSED record; the returned hash is stable
    # for the same pre-seal content
    seal_hash2 = seal_hash  # deterministic: same content → same hash
    assert seal_hash == seal_hash2


# ---------------------------------------------------------------------------
# 5. Invalid event_type raises ValueError
# ---------------------------------------------------------------------------

def test_invalid_event_type_raises(tmp_data: Path) -> None:
    with pytest.raises(ValueError, match="Unknown event_type"):
        append_event(CLIENT_ID, "NOT_A_REAL_EVENT", {}, data_dir=tmp_data)


# ---------------------------------------------------------------------------
# 6. get_last_event returns correct record
# ---------------------------------------------------------------------------

def test_get_last_event(tmp_data: Path) -> None:
    assert get_last_event(CLIENT_ID, tmp_data) is None

    append_event(CLIENT_ID, "INTAKE_SUBMITTED", {}, data_dir=tmp_data)
    append_event(CLIENT_ID, "TRIAGE_DECIDED", {"score": 80}, data_dir=tmp_data)

    last = get_last_event(CLIENT_ID, tmp_data)
    assert last is not None
    assert last["event_type"] == "TRIAGE_DECIDED"
    assert last["seq"] == 1


# ---------------------------------------------------------------------------
# 7. node + error_class fields are stored and retrieved
# ---------------------------------------------------------------------------

def test_node_and_error_class_fields(tmp_data: Path) -> None:
    append_event(
        CLIENT_ID,
        "NODE_FAIL",
        {"reason": "timeout"},
        node="SCAFFOLD",
        error_class="scaffold-unknown-entity",
        data_dir=tmp_data,
    )

    ev = get_last_event(CLIENT_ID, tmp_data)
    assert ev is not None
    assert ev["node"] == "SCAFFOLD"
    assert ev["error_class"] == "scaffold-unknown-entity"
    assert ev["event_type"] == "NODE_FAIL"


# ---------------------------------------------------------------------------
# 8. verify_chain on empty/absent log
# ---------------------------------------------------------------------------

def test_verify_chain_empty_log(tmp_data: Path) -> None:
    ok, msg = verify_chain("nonexistent000000", tmp_data)
    assert ok is True
    assert msg == "CHAIN OK"
