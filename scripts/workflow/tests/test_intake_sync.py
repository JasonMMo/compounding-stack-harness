"""test_intake_sync.py -- Phase 4 sync bridge unit tests.

All tests use tmp dirs + --no-ssh.  No real SSH, no real subprocesses for
deploy / scaffold beyond monkeypatching.

Run:
  PYTHONIOENCODING=utf-8 python -m pytest scripts/workflow/tests/test_intake_sync.py -q

Covered:
  1. is_processed / record_processed -- idempotency (same ts not processed twice).
  2. route_entry status=prefer_call -- writes pm-inbox CALL block, sets
     triage_status, records processed; NO profiles/ file created.
  3. route_entry status=gap_only -- appends gap-registry.jsonl; no build.
  4. route_entry status=qualify with --skip-deploy --skip-ui-check and a
     fixture mirror draft.yaml -- promote_draft writes profiles/<slug>.yaml with
     non-null stack (defaults injected when source null); emits DRAFT_PROMOTED +
     SCAFFOLDED node events into a tmp cases yaml.
     Scaffold subprocess is monkeypatched to return rc=0.
  5. promote_draft null-stack default injection unit test.
  6. rsync_inbox rsync/scp fallback -- shutil.which determines which tool is used.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup: make workflow dir importable
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_DIR = REPO_ROOT / "scripts" / "workflow"

if str(WORKFLOW_DIR) not in sys.path:
    sys.path.insert(0, str(WORKFLOW_DIR))

import intake_sync as _intake_sync_mod
from intake_sync import (  # noqa: E402
    is_processed,
    load_inbox,
    promote_draft,
    record_processed,
    route_entry,
    rsync_client_artifacts,
    rsync_inbox,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FAKE_TS = "2026-06-14T00:00:00Z"
_FAKE_SLUG = "acme-test"
_FAKE_CLIENT = "client-abc123"


def _make_entry(
    status: str = "qualify",
    prefer_call: str = "no",
    score: int = 70,
    slug: str = _FAKE_SLUG,
    client_id: str = _FAKE_CLIENT,
    ts: str = _FAKE_TS,
    gap_category: str = "",
    todo_axis: str = "",
) -> dict:
    return {
        "ts": ts,
        "client_id": client_id,
        "slug": slug,
        "score": score,
        "status": status,
        "prefer_call": prefer_call,
        "qualifies": status == "qualify",
        "gap_category": gap_category,
        "todo_axis": todo_axis,
    }


def _make_draft_yaml(tmp_path: Path, slug: str = _FAKE_SLUG, null_stack: bool = False) -> Path:
    """Write a minimal draft.yaml to mirror_dir/clients/<client_id>/."""
    client_dir = tmp_path / "clients" / _FAKE_CLIENT
    client_dir.mkdir(parents=True, exist_ok=True)
    draft_path = client_dir / "draft.yaml"
    if null_stack:
        draft_content = (
            "schema_version: '1'\n"
            f"slug: {slug}\n"
            "status: draft\n"
            "stack:\n"
            "  frontend: null\n"
            "  backend: null\n"
            "  dialect: null\n"
            "domains: []\n"
        )
    else:
        draft_content = (
            "schema_version: '1'\n"
            f"slug: {slug}\n"
            "status: draft\n"
            "stack:\n"
            "  frontend: react\n"
            "  backend: fastapi\n"
            "  dialect: postgres\n"
            "domains: [invoice, customer]\n"
        )
    draft_path.write_text(draft_content, encoding="utf-8")
    return draft_path


def _fake_subprocess_ok(*args, **kwargs):
    """Monkeypatch target: returns rc=0 with empty output.  Accepts **kwargs
    so the encoding kwargs added by BUG-1 fix do not cause TypeError."""
    result = types.SimpleNamespace(
        returncode=0, stdout="VERDICT: PASS\n", stderr=""
    )
    return result


# ---------------------------------------------------------------------------
# 1. is_processed / record_processed idempotency
# ---------------------------------------------------------------------------


def test_is_processed_false_when_file_absent(tmp_path):
    processed = tmp_path / "processed.jsonl"
    assert not is_processed(_FAKE_TS, processed)


def test_record_then_is_processed(tmp_path):
    processed = tmp_path / "processed.jsonl"
    entry = _make_entry()
    record_processed(entry, processed, status="built")
    assert is_processed(_FAKE_TS, processed)


def test_record_processed_does_not_duplicate(tmp_path):
    """Same ts may be recorded twice by caller (shouldn't happen normally) --
    is_processed still returns True after first record."""
    processed = tmp_path / "processed.jsonl"
    entry = _make_entry()
    record_processed(entry, processed, status="built")
    record_processed(entry, processed, status="built")  # second write (caller bug)
    # is_processed should still be True
    assert is_processed(_FAKE_TS, processed)
    # And the file should have two lines (record_processed itself doesn't dedup;
    # idempotency is guaranteed by the caller (main loop) checking is_processed first).
    lines = [l for l in processed.read_text().splitlines() if l.strip()]
    assert len(lines) == 2


def test_different_ts_not_matched(tmp_path):
    processed = tmp_path / "processed.jsonl"
    entry = _make_entry(ts="2026-01-01T00:00:00Z")
    record_processed(entry, processed, status="built")
    assert not is_processed("2026-06-14T00:00:00Z", processed)


def test_record_processed_pii_free(tmp_path):
    """processed.jsonl must not contain email or free-text (PII-free contract)."""
    processed = tmp_path / "processed.jsonl"
    entry = _make_entry()
    # Inject a fake email that should NOT appear
    entry["email"] = "secret@example.com"
    entry["company_free_text"] = "ACME Corp secret"
    record_processed(entry, processed, status="built")
    content = processed.read_text(encoding="utf-8")
    assert "secret@example.com" not in content
    assert "ACME Corp secret" not in content
    assert "acme-test" in content  # slug is OK


# ---------------------------------------------------------------------------
# 2. route_entry prefer_call path
# ---------------------------------------------------------------------------


def test_route_prefer_call_writes_pm_inbox(tmp_path):
    """prefer_call=yes -> pm-inbox CALL block written; no profiles file created."""
    entry = _make_entry(status="qualify", prefer_call="yes")
    processed = tmp_path / "processed.jsonl"
    cases_dir = tmp_path / "cases"
    pm_inbox = tmp_path / "pm-inbox.md"
    profiles_dir = tmp_path / "profiles"

    result = route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=tmp_path / "mirror",
        processed_path=processed,
        profiles_dir=profiles_dir,
        cases_dir=cases_dir,
        pm_inbox_path=pm_inbox,
        gap_registry_path=tmp_path / "gap.jsonl",
    )

    assert result["routed_to"] == "call_queue"
    # pm-inbox written
    assert pm_inbox.exists()
    content = pm_inbox.read_text(encoding="utf-8")
    assert "CALL REQUEST" in content
    assert _FAKE_SLUG in content
    # NO PII
    assert "secret@example.com" not in content
    # processed
    assert is_processed(_FAKE_TS, processed)
    processed_line = json.loads(processed.read_text().strip())
    assert processed_line["status"] == "call_queue"
    # No profiles file
    assert not (profiles_dir / f"{_FAKE_SLUG}.yaml").exists()


def test_route_prefer_call_sets_triage_status(tmp_path):
    entry = _make_entry(status="qualify", prefer_call="yes")
    processed = tmp_path / "processed.jsonl"
    cases_dir = tmp_path / "cases"

    route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=tmp_path / "mirror",
        processed_path=processed,
        profiles_dir=tmp_path / "profiles",
        cases_dir=cases_dir,
        pm_inbox_path=tmp_path / "pm.md",
        gap_registry_path=tmp_path / "gap.jsonl",
    )

    # Check case yaml has triage_status=prefer_call
    case_yaml = cases_dir / f"{_FAKE_CLIENT}.yaml"
    assert case_yaml.exists()
    import yaml
    data = yaml.safe_load(case_yaml.read_text())
    assert data["triage_status"] == "prefer_call"


# ---------------------------------------------------------------------------
# 3. route_entry gap_only path
# ---------------------------------------------------------------------------


def test_route_gap_only_writes_gap_registry(tmp_path):
    entry = _make_entry(
        status="gap_only",
        score=30,
        gap_category="db_dialect_mssql",
        todo_axis="ddl",
    )
    processed = tmp_path / "processed.jsonl"
    gap_registry = tmp_path / "gap-registry.jsonl"
    cases_dir = tmp_path / "cases"
    pm_inbox = tmp_path / "pm-inbox.md"

    result = route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=tmp_path / "mirror",
        processed_path=processed,
        profiles_dir=tmp_path / "profiles",
        cases_dir=cases_dir,
        pm_inbox_path=pm_inbox,
        gap_registry_path=gap_registry,
    )

    assert result["routed_to"] == "gap_registry"
    # gap-registry.jsonl has a line
    assert gap_registry.exists()
    gap_line = json.loads(gap_registry.read_text().strip())
    assert gap_line["slug"] == _FAKE_SLUG
    assert gap_line["gap_category"] == "db_dialect_mssql"
    assert gap_line["todo_axis"] == "ddl"
    # No email/PII in gap record
    assert "email" not in gap_line
    # pm-inbox triage block
    assert pm_inbox.exists()
    assert "TRIAGE" in pm_inbox.read_text()
    # processed
    assert is_processed(_FAKE_TS, processed)


def test_route_defer_appends_gap_registry(tmp_path):
    entry = _make_entry(status="defer", score=48, gap_category="auth_sso", todo_axis="creater")
    processed = tmp_path / "processed.jsonl"
    gap_registry = tmp_path / "gap-registry.jsonl"

    route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=tmp_path / "mirror",
        processed_path=processed,
        profiles_dir=tmp_path / "profiles",
        cases_dir=tmp_path / "cases",
        pm_inbox_path=tmp_path / "pm.md",
        gap_registry_path=gap_registry,
    )

    assert gap_registry.exists()
    line = json.loads(gap_registry.read_text().strip())
    assert line.get("slug") == _FAKE_SLUG


def test_route_gap_only_no_build(tmp_path):
    """gap_only must not create any profiles file."""
    entry = _make_entry(status="gap_only")
    profiles_dir = tmp_path / "profiles"

    route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=tmp_path / "mirror",
        processed_path=tmp_path / "proc.jsonl",
        profiles_dir=profiles_dir,
        cases_dir=tmp_path / "cases",
        pm_inbox_path=tmp_path / "pm.md",
        gap_registry_path=tmp_path / "gap.jsonl",
    )

    assert not (profiles_dir / f"{_FAKE_SLUG}.yaml").exists()


# ---------------------------------------------------------------------------
# 4. route_entry qualify path (monkeypatched scaffold)
# ---------------------------------------------------------------------------


def test_route_qualify_creates_profile_and_case_events(tmp_path, monkeypatch):
    """qualify -> promote_draft -> scaffold(stubbed) -> profile written, case events."""
    mirror_dir = tmp_path / "mirror"
    _make_draft_yaml(mirror_dir, null_stack=False)

    entry = _make_entry(status="qualify", score=72)
    processed = tmp_path / "processed.jsonl"
    cases_dir = tmp_path / "cases"
    profiles_dir = tmp_path / "profiles"

    # Monkeypatch subprocess.run: scaffold rc=0, needs_fit prints PASS
    monkeypatch.setattr("intake_sync.subprocess.run", _fake_subprocess_ok)

    result = route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=mirror_dir,
        processed_path=processed,
        profiles_dir=profiles_dir,
        cases_dir=cases_dir,
        pm_inbox_path=tmp_path / "pm.md",
        gap_registry_path=tmp_path / "gap.jsonl",
        subprocess_run=_fake_subprocess_ok,
    )

    # profiles/<slug>.yaml must exist
    profile_path = profiles_dir / f"{_FAKE_SLUG}.yaml"
    assert profile_path.exists(), f"profile not written: {profile_path}"

    # Case yaml must have pipeline_events with DRAFT_PROMOTED and SCAFFOLDED
    case_yaml = cases_dir / f"{_FAKE_CLIENT}.yaml"
    assert case_yaml.exists(), f"case yaml not written: {case_yaml}"

    import yaml
    data = yaml.safe_load(case_yaml.read_text())
    events = data.get("pipeline_events", [])
    node_ids = [e["node_id"] for e in events]
    assert "DRAFT_PROMOTED" in node_ids, f"DRAFT_PROMOTED not in {node_ids}"
    assert "SCAFFOLDED" in node_ids, f"SCAFFOLDED not in {node_ids}"

    # processed entry written with a 'built*' status
    assert is_processed(_FAKE_TS, processed)
    proc_line = json.loads(processed.read_text().strip())
    assert proc_line["status"].startswith("built")


def test_route_qualify_scaffold_fail_records_failed(tmp_path, monkeypatch):
    """If scaffold returns rc=1, record_processed with status=failed."""
    mirror_dir = tmp_path / "mirror"
    _make_draft_yaml(mirror_dir, null_stack=False)
    entry = _make_entry(status="qualify")

    def _fake_fail(*a, **kw):  # **kw absorbs encoding kwargs
        return types.SimpleNamespace(returncode=1, stdout="", stderr="entity not found")

    result = route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=mirror_dir,
        processed_path=tmp_path / "proc.jsonl",
        profiles_dir=tmp_path / "profiles",
        cases_dir=tmp_path / "cases",
        evidence_dir=tmp_path / "evidence",  # keep node-fail evidence out of the repo dir
        pm_inbox_path=tmp_path / "pm.md",
        gap_registry_path=tmp_path / "gap.jsonl",
        subprocess_run=_fake_fail,
    )

    assert result["final_status"] == "failed"
    assert is_processed(_FAKE_TS, tmp_path / "proc.jsonl")
    line = json.loads((tmp_path / "proc.jsonl").read_text().strip())
    assert line["status"] == "failed"


# ---------------------------------------------------------------------------
# 5. promote_draft null-stack default injection
# ---------------------------------------------------------------------------


def test_promote_draft_null_stack_gets_defaults(tmp_path):
    """When draft.yaml has null frontend/backend/dialect, defaults are injected."""
    mirror_dir = tmp_path / "mirror"
    _make_draft_yaml(mirror_dir, null_stack=True)
    profiles_dir = tmp_path / "profiles"

    dest = promote_draft(_FAKE_SLUG, _FAKE_CLIENT, mirror_dir, profiles_dir=profiles_dir)

    assert dest.exists()
    import yaml
    data = yaml.safe_load(dest.read_text(encoding="utf-8"))
    stack = data.get("stack", {})
    assert stack.get("frontend") == "vanilla-htmx", f"frontend was {stack.get('frontend')}"
    assert stack.get("backend") == "fastapi", f"backend was {stack.get('backend')}"
    assert stack.get("dialect") == "postgres", f"dialect was {stack.get('dialect')}"


def test_promote_draft_existing_stack_preserved(tmp_path):
    """When draft.yaml has explicit stack values, they are NOT overwritten."""
    mirror_dir = tmp_path / "mirror"
    _make_draft_yaml(mirror_dir, null_stack=False)  # react / fastapi / postgres
    profiles_dir = tmp_path / "profiles"

    dest = promote_draft(_FAKE_SLUG, _FAKE_CLIENT, mirror_dir, profiles_dir=profiles_dir)
    import yaml
    data = yaml.safe_load(dest.read_text(encoding="utf-8"))
    stack = data.get("stack", {})
    assert stack.get("frontend") == "react"


def test_promote_draft_missing_draft_raises(tmp_path):
    """promote_draft raises FileNotFoundError when draft.yaml absent."""
    mirror_dir = tmp_path / "mirror"
    (mirror_dir / "clients" / _FAKE_CLIENT).mkdir(parents=True, exist_ok=True)
    profiles_dir = tmp_path / "profiles"
    with pytest.raises(FileNotFoundError):
        promote_draft(_FAKE_SLUG, _FAKE_CLIENT, mirror_dir, profiles_dir=profiles_dir)


# ---------------------------------------------------------------------------
# 5b. promote_draft PII scrub (security fix)
# ---------------------------------------------------------------------------


def test_promote_draft_strips_contact_email(tmp_path):
    """promote_draft replaces customer.contact email with intake-ref:<client_id>."""
    mirror_dir = tmp_path / "mirror"
    client_dir = mirror_dir / "clients" / _FAKE_CLIENT
    client_dir.mkdir(parents=True, exist_ok=True)
    # Draft as produced by intake_to_profile._render_profile: contact = real email
    draft_content = (
        "schema_version: '1'\n"
        f"slug: {_FAKE_SLUG}\n"
        "status: draft\n"
        "customer:\n"
        "  slug: acme-test\n"
        "  display: Acme Corp\n"
        "  contact: ceo@acme.com\n"
        "  industry: manufacturing\n"
        "stack:\n"
        "  frontend: react\n"
        "  backend: fastapi\n"
        "  dialect: postgres\n"
        "domains: []\n"
    )
    (client_dir / "draft.yaml").write_text(draft_content, encoding="utf-8")

    profiles_dir = tmp_path / "profiles"
    dest = promote_draft(_FAKE_SLUG, _FAKE_CLIENT, mirror_dir, profiles_dir=profiles_dir)
    content = dest.read_text(encoding="utf-8")

    # Must contain NO '@' anywhere in the promoted profile
    assert "@" not in content, (
        f"Email character '@' found in promoted profile -- PII leak:\n{content}"
    )
    # contact replaced with the PII-free sentinel
    assert f"intake-ref:{_FAKE_CLIENT}" in content, (
        f"intake-ref sentinel not found in promoted profile:\n{content}"
    )
    # Non-PII fields preserved
    assert _FAKE_SLUG in content
    assert "Acme Corp" in content


def test_promote_draft_contact_phone_stripped(tmp_path):
    """customer.contact containing a phone number is also replaced."""
    mirror_dir = tmp_path / "mirror"
    client_dir = mirror_dir / "clients" / _FAKE_CLIENT
    client_dir.mkdir(parents=True, exist_ok=True)
    draft_content = (
        "schema_version: '1'\n"
        f"slug: {_FAKE_SLUG}\n"
        "status: draft\n"
        "customer:\n"
        "  slug: acme-test\n"
        "  display: Acme Corp\n"
        "  contact: '010-1234-5678'\n"
        "  industry: retail\n"
        "stack:\n"
        "  frontend: null\n"
        "  backend: null\n"
        "  dialect: null\n"
        "domains: []\n"
    )
    (client_dir / "draft.yaml").write_text(draft_content, encoding="utf-8")

    profiles_dir = tmp_path / "profiles"
    dest = promote_draft(_FAKE_SLUG, _FAKE_CLIENT, mirror_dir, profiles_dir=profiles_dir)
    content = dest.read_text(encoding="utf-8")

    assert "010-1234-5678" not in content
    assert f"intake-ref:{_FAKE_CLIENT}" in content


def test_promote_draft_email_in_other_field_raises(tmp_path):
    """Email in a non-contact field triggers the belt-and-suspenders scan -> ValueError."""
    mirror_dir = tmp_path / "mirror"
    client_dir = mirror_dir / "clients" / _FAKE_CLIENT
    client_dir.mkdir(parents=True, exist_ok=True)
    # Email injected into display (shouldn't happen, but tests the full-YAML scan)
    draft_content = (
        "schema_version: '1'\n"
        f"slug: {_FAKE_SLUG}\n"
        "status: draft\n"
        "customer:\n"
        "  slug: acme-test\n"
        "  display: acme-ceo@acme.com\n"
        "  contact: null\n"
        "  industry: generic\n"
        "stack:\n"
        "  frontend: react\n"
        "  backend: fastapi\n"
        "  dialect: postgres\n"
        "domains: []\n"
    )
    (client_dir / "draft.yaml").write_text(draft_content, encoding="utf-8")

    profiles_dir = tmp_path / "profiles"
    with pytest.raises(ValueError, match="PII detected"):
        promote_draft(_FAKE_SLUG, _FAKE_CLIENT, mirror_dir, profiles_dir=profiles_dir)

    # Profile file must NOT have been written (write is aborted before the raise)
    assert not (profiles_dir / f"{_FAKE_SLUG}.yaml").exists()


def test_promote_draft_no_contact_field_ok(tmp_path):
    """Draft without customer.contact passes through without error."""
    mirror_dir = tmp_path / "mirror"
    client_dir = mirror_dir / "clients" / _FAKE_CLIENT
    client_dir.mkdir(parents=True, exist_ok=True)
    draft_content = (
        "schema_version: '1'\n"
        f"slug: {_FAKE_SLUG}\n"
        "status: draft\n"
        "customer:\n"
        "  slug: acme-test\n"
        "  display: Acme Corp\n"
        "  industry: logistics\n"
        "stack:\n"
        "  frontend: vue\n"
        "  backend: springboot\n"
        "  dialect: mysql\n"
        "domains: []\n"
    )
    (client_dir / "draft.yaml").write_text(draft_content, encoding="utf-8")

    profiles_dir = tmp_path / "profiles"
    dest = promote_draft(_FAKE_SLUG, _FAKE_CLIENT, mirror_dir, profiles_dir=profiles_dir)
    assert dest.exists()
    assert "@" not in dest.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 6. load_inbox / rsync_inbox with --no-ssh
# ---------------------------------------------------------------------------


def test_load_inbox_empty_when_no_file(tmp_path):
    entries = load_inbox(tmp_path / "empty-mirror")
    assert entries == []


def test_load_inbox_sorts_by_ts(tmp_path):
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    inbox = mirror / "inbox.jsonl"
    inbox.write_text(
        json.dumps({"ts": "2026-06-14T12:00:00Z", "slug": "b", "status": "qualify"}) + "\n"
        + json.dumps({"ts": "2026-06-14T08:00:00Z", "slug": "a", "status": "qualify"}) + "\n",
        encoding="utf-8",
    )
    entries = load_inbox(mirror)
    assert entries[0]["slug"] == "a"
    assert entries[1]["slug"] == "b"


def test_rsync_inbox_no_ssh_returns_path(tmp_path):
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    result = rsync_inbox(no_ssh=True, mirror_dir=mirror)
    assert result == mirror / "inbox.jsonl"


def test_load_inbox_skips_bad_json_lines(tmp_path):
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    inbox = mirror / "inbox.jsonl"
    inbox.write_text(
        "{bad json line}\n"
        + json.dumps({"ts": "2026-06-14T00:00:00Z", "slug": "ok"}) + "\n",
        encoding="utf-8",
    )
    entries = load_inbox(mirror)
    assert len(entries) == 1
    assert entries[0]["slug"] == "ok"


# ---------------------------------------------------------------------------
# 7. dry-run does not mutate
# ---------------------------------------------------------------------------


def test_route_prefer_call_dry_run_no_mutation(tmp_path):
    entry = _make_entry(status="qualify", prefer_call="yes")
    processed = tmp_path / "processed.jsonl"
    pm_inbox = tmp_path / "pm-inbox.md"

    route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=tmp_path / "mirror",
        processed_path=processed,
        profiles_dir=tmp_path / "profiles",
        cases_dir=tmp_path / "cases",
        pm_inbox_path=pm_inbox,
        gap_registry_path=tmp_path / "gap.jsonl",
        dry_run=True,
    )

    # Nothing should be written
    assert not processed.exists()
    assert not pm_inbox.exists()


def test_route_qualify_dry_run_no_mutation(tmp_path, monkeypatch):
    mirror_dir = tmp_path / "mirror"
    _make_draft_yaml(mirror_dir, null_stack=False)
    entry = _make_entry(status="qualify")
    processed = tmp_path / "processed.jsonl"
    profiles_dir = tmp_path / "profiles"

    monkeypatch.setattr("intake_sync.subprocess.run", _fake_subprocess_ok)

    route_entry(
        entry,
        no_ssh=True,
        skip_deploy=True,
        skip_ui_check=True,
        mirror_dir=mirror_dir,
        processed_path=processed,
        profiles_dir=profiles_dir,
        cases_dir=tmp_path / "cases",
        pm_inbox_path=tmp_path / "pm.md",
        gap_registry_path=tmp_path / "gap.jsonl",
        subprocess_run=_fake_subprocess_ok,
        dry_run=True,
    )

    assert not processed.exists(), "processed.jsonl should not be written in dry-run"
    assert not (profiles_dir / f"{_FAKE_SLUG}.yaml").exists(), (
        "profiles file should not be written in dry-run"
    )


# ---------------------------------------------------------------------------
# 8. rsync / scp fallback (BUG-2 fix)
# ---------------------------------------------------------------------------


def test_rsync_inbox_uses_rsync_when_available(tmp_path, monkeypatch):
    """When shutil.which('rsync') returns a path, subprocess is called with rsync."""
    mirror = tmp_path / "mirror"
    mirror.mkdir()

    captured: list[list[str]] = []

    def _fake_run(argv, *args, **kwargs):
        captured.append(list(argv))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("intake_sync.shutil.which", lambda name: "/usr/bin/rsync" if name == "rsync" else None)
    monkeypatch.setattr("intake_sync.subprocess.run", _fake_run)

    rsync_inbox(no_ssh=False, mirror_dir=mirror)

    assert len(captured) == 1, f"Expected 1 subprocess call, got {len(captured)}"
    assert captured[0][0] == "rsync", f"Expected rsync command, got {captured[0][0]!r}"


def test_rsync_inbox_falls_back_to_scp_when_rsync_absent(tmp_path, monkeypatch):
    """When shutil.which('rsync') returns None, subprocess is called with scp."""
    mirror = tmp_path / "mirror"
    mirror.mkdir()

    captured: list[list[str]] = []

    def _fake_run(argv, *args, **kwargs):
        captured.append(list(argv))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("intake_sync.shutil.which", lambda name: None)
    monkeypatch.setattr("intake_sync.subprocess.run", _fake_run)

    rsync_inbox(no_ssh=False, mirror_dir=mirror)

    assert len(captured) == 1, f"Expected 1 subprocess call, got {len(captured)}"
    argv = captured[0]
    assert argv[0] == "scp", f"Expected scp command, got {argv[0]!r}"
    # Must include the inbox.jsonl remote path
    assert any("inbox.jsonl" in arg for arg in argv), (
        f"inbox.jsonl not found in scp argv: {argv}"
    )
    # Must include the local mirror path
    local_inbox = str(mirror / "inbox.jsonl")
    assert local_inbox in argv, f"local inbox path {local_inbox!r} not in argv: {argv}"


def test_rsync_client_artifacts_uses_rsync_when_available(tmp_path, monkeypatch):
    """When shutil.which('rsync') returns a path, rsync is used for client pull."""
    mirror = tmp_path / "mirror"
    mirror.mkdir()

    captured: list[list[str]] = []

    def _fake_run(argv, *args, **kwargs):
        captured.append(list(argv))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("intake_sync.shutil.which", lambda name: "/usr/bin/rsync" if name == "rsync" else None)
    monkeypatch.setattr("intake_sync.subprocess.run", _fake_run)

    rsync_client_artifacts(_FAKE_CLIENT, no_ssh=False, mirror_dir=mirror)

    assert len(captured) == 1
    assert captured[0][0] == "rsync"


def test_rsync_client_artifacts_falls_back_to_scp_when_rsync_absent(tmp_path, monkeypatch):
    """When shutil.which('rsync') returns None, scp -r is used for client pull."""
    mirror = tmp_path / "mirror"
    mirror.mkdir()

    captured: list[list[str]] = []

    def _fake_run(argv, *args, **kwargs):
        captured.append(list(argv))
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("intake_sync.shutil.which", lambda name: None)
    monkeypatch.setattr("intake_sync.subprocess.run", _fake_run)

    rsync_client_artifacts(_FAKE_CLIENT, no_ssh=False, mirror_dir=mirror)

    assert len(captured) == 1
    argv = captured[0]
    assert argv[0] == "scp", f"Expected scp, got {argv[0]!r}"
    # Must be a recursive copy (-r flag)
    assert "-r" in argv, f"-r flag not in scp argv: {argv}"
    # Must reference the client_id in the remote path
    assert any(_FAKE_CLIENT in arg for arg in argv), (
        f"client_id {_FAKE_CLIENT!r} not in scp argv: {argv}"
    )
