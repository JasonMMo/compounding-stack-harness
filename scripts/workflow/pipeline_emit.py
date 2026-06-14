"""pipeline_emit.py — local-side node-event emitter for pipeline tracking.

Writes PII-free pipeline_events into infra/registry/cases/<client_id>.yaml.
Evidence artifacts go to docs/intake-inbox/evidence/<node>-<slug>-<ts>.txt.

stdlib + PyYAML. LLM 0. No PII (email, free-text, company name) ever written.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml  # type: ignore[import]
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Canonical node constants
# ---------------------------------------------------------------------------

#: All valid pipeline node IDs.
VALID_NODES: frozenset[str] = frozenset({
    "SUBMITTED",
    "TRIAGED",
    "CALL_QUEUE",
    "GAP_RECORDED",
    "PM_TRIAGE",
    "DRAFT_PROMOTED",
    "SCAFFOLDED",
    "DEPLOYED",
    "UI_CHECKED",
    "NEEDS_FIT",
    "PROFILE_CONFIRMED",
    "DELIVERED",
    "FEEDBACK",
    "CLOSED",
})

#: Valid pipeline event labels (matches audit.py EVENT_TYPES subset).
VALID_EVENTS: frozenset[str] = frozenset({
    "NODE_ENTER",
    "NODE_EXIT_OK",
    "NODE_FAIL",
})

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_CASES_DIR = _REPO_ROOT / "infra" / "registry" / "cases"
_DEFAULT_EVIDENCE_DIR = _REPO_ROOT / "docs" / "intake-inbox" / "evidence"


def _cases_dir() -> Path:
    env = os.environ.get("PIPELINE_CASES_DIR")
    return Path(env) if env else _DEFAULT_CASES_DIR


def _evidence_dir() -> Path:
    env = os.environ.get("PIPELINE_EVIDENCE_DIR")
    return Path(env) if env else _DEFAULT_EVIDENCE_DIR

# ---------------------------------------------------------------------------
# YAML helpers (no catalog.yaml dependency — standalone)
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    """Load a YAML file; return {} if absent or unparseable."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if _HAS_YAML:
        data = _yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    # Minimal fallback: not needed for normal operation, return {}
    return {}


def _dump_yaml(data: dict, path: Path) -> None:
    """Write dict to YAML file; creates parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if _HAS_YAML:
        path.write_text(
            _yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    else:
        # Minimal fallback stringification (sufficient for smoke tests without pyyaml)
        import json as _json
        path.write_text(_json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def emit_node_event(
    case_yaml_path: Path,
    node_id: str,
    event: str,
    *,
    slug: str,
    score: int | float | None = None,
    error_class: str | None = None,
    evidence_path: str | None = None,
    ts: str | None = None,
) -> dict:
    """Append a pipeline node event to the case YAML.

    Creates the case file with a minimal skeleton if absent.
    Never writes email, free-text, or any PII.

    Parameters
    ----------
    case_yaml_path:
        Path to infra/registry/cases/<client_id>.yaml (absolute or relative).
    node_id:
        One of VALID_NODES (e.g. "SUBMITTED", "DEPLOYED").
    event:
        "NODE_ENTER", "NODE_EXIT_OK", or "NODE_FAIL".
    slug:
        ASCII slug identifying the customer profile (G-8 compliant).
    score:
        Optional integer qualification score (PII-free numeric).
    error_class:
        Optional defect taxonomy class (e.g. "deploy-fail").
    evidence_path:
        Optional str path to a PII-free evidence file.
    ts:
        Optional ISO-8601 timestamp string; defaults to UTC now.

    Returns
    -------
    dict
        The event record that was appended.

    Raises
    ------
    ValueError
        If node_id or event is not in the allowed sets.
    """
    if node_id not in VALID_NODES:
        raise ValueError(
            f"Unknown node_id {node_id!r}. Must be one of: {sorted(VALID_NODES)}"
        )
    if event not in VALID_EVENTS:
        raise ValueError(
            f"Unknown event {event!r}. Must be one of: {sorted(VALID_EVENTS)}"
        )

    case_yaml_path = Path(case_yaml_path)
    # Derive client_id from filename stem (no extension)
    client_id = case_yaml_path.stem

    # Load existing data or initialise skeleton (PII-free)
    data = _load_yaml(case_yaml_path)
    if not data:
        data = {
            "client_id": client_id,
            "slug": slug,
            "score": score,
            "triage_status": None,
            "pipeline_events": [],
        }

    # Ensure pipeline_events list exists
    if "pipeline_events" not in data or not isinstance(data["pipeline_events"], list):
        data["pipeline_events"] = []

    # Update top-level score if provided
    if score is not None:
        data["score"] = int(score)

    # Update slug (in case of first write)
    if slug:
        data["slug"] = slug

    # Build event record (PII-free: no email/free-text/company)
    if ts is None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    record: dict[str, Any] = {
        "ts": ts,
        "node_id": node_id,
        "event": event,
        "error_class": error_class,
        "evidence_path": str(evidence_path) if evidence_path else None,
    }

    data["pipeline_events"].append(record)
    _dump_yaml(data, case_yaml_path)
    return record


def capture_evidence(
    node_id: str,
    slug: str,
    *,
    returncode: int | None = None,
    stderr_tail: str = "",
    report_path: str | None = None,
    out_dir: Path | None = None,
) -> Path:
    """Write a PII-free evidence text file for a node failure/outcome.

    Content: returncode, stderr tail (truncated to 500 chars), report path.
    Never includes email, free-text answers, or PII.

    Parameters
    ----------
    node_id:
        Pipeline node (e.g. "DEPLOYED").
    slug:
        ASCII customer slug.
    returncode:
        Process exit code, if applicable.
    stderr_tail:
        Last N characters of stderr output (truncated to 500 chars here).
    report_path:
        Path to a machine-generated report file (not the content, just the path).
    out_dir:
        Directory to write evidence file; defaults to docs/intake-inbox/evidence/.

    Returns
    -------
    Path
        Absolute path to the written evidence file.
    """
    if out_dir is None:
        out_dir = _evidence_dir()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ts_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{node_id}-{slug}-{ts_str}.txt"
    evidence_path = out_dir / filename

    # Truncate stderr to 500 chars to avoid accidental PII bleed
    stderr_safe = (stderr_tail or "")[:500]

    lines = [
        f"node: {node_id}",
        f"slug: {slug}",
        f"ts: {ts_str}",
        f"returncode: {returncode!r}",
        f"stderr_tail (truncated to 500 chars):",
        stderr_safe,
        f"report_path: {report_path!r}",
    ]
    evidence_path.write_text("\n".join(lines), encoding="utf-8")
    return evidence_path


def set_triage_status(case_yaml_path: Path, status: str) -> None:
    """Set the triage_status field in the case YAML.

    Parameters
    ----------
    case_yaml_path:
        Path to infra/registry/cases/<client_id>.yaml.
    status:
        One of: qualify | defer | gap_only | prefer_call | closed.

    Raises
    ------
    ValueError
        If status is not a recognised value.
    """
    _VALID_STATUSES = {"qualify", "defer", "gap_only", "prefer_call", "closed"}
    if status not in _VALID_STATUSES:
        raise ValueError(
            f"Unknown triage_status {status!r}. Must be one of: {sorted(_VALID_STATUSES)}"
        )

    case_yaml_path = Path(case_yaml_path)
    data = _load_yaml(case_yaml_path)
    if not data:
        # Initialise a minimal skeleton if the file does not exist yet
        client_id = case_yaml_path.stem
        data = {
            "client_id": client_id,
            "slug": None,
            "score": None,
            "triage_status": None,
            "pipeline_events": [],
        }
    data["triage_status"] = status
    _dump_yaml(data, case_yaml_path)
