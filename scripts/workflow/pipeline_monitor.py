"""pipeline_monitor.py — deterministic pipeline health detector.

Reads infra/registry/cases/*.yaml (PII-free) and projects node states,
detects stalls, classifies defects, and emits alerts.

stdlib + PyYAML. LLM 0. No PII accessed. 'now' injected via datetime.now(timezone.utc).

CLI:
  python scripts/workflow/pipeline_monitor.py [--cases-dir DIR] [--processed FILE]
         [--json] [--alert]
  --alert : appends new alerts to docs/intake-inbox/alerts.md (deduplicated).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml as _yaml  # type: ignore[import]
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Repo paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_CASES_DIR = _REPO_ROOT / "infra" / "registry" / "cases"
_DEFAULT_ALERTS_PATH = _REPO_ROOT / "docs" / "intake-inbox" / "alerts.md"
_DEFAULT_DATA_MIRROR = _REPO_ROOT / "apps" / "intake" / "data-mirror"

# ---------------------------------------------------------------------------
# Canonical node graph
# ---------------------------------------------------------------------------

#: Per-node metadata: enter_event, exit_event, gate, sla_seconds, description.
NODES: dict[str, dict[str, Any]] = {
    "SUBMITTED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 360,
        "description": "Form submitted, awaiting in-process conversion",
    },
    "TRIAGED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 3600,
        "description": "Qualification + triage decision",
    },
    "CALL_QUEUE": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "HUMAN",
        "sla_seconds": 86400,
        "description": "Prefer-call path: awaiting human callback",
    },
    "GAP_RECORDED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 3600,
        "description": "Gap registered in gap-registry.jsonl",
    },
    "PM_TRIAGE": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "HUMAN",
        "sla_seconds": 172800,
        "description": "PM manual triage (defer/gap_only cases)",
    },
    "DRAFT_PROMOTED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 7200,
        "description": "Draft profile promoted from intake answers",
    },
    "SCAFFOLDED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 7200,
        "description": "scaffold.py generated screen manifest + DDL",
    },
    "DEPLOYED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 36000,
        "description": "Preview deployed to Coolify",
    },
    "UI_CHECKED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 3600,
        "description": "UI check (Playwright smoke, overflow, console errors)",
    },
    "NEEDS_FIT": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 7200,
        "description": "Needs-fit codex audit gate",
    },
    "PROFILE_CONFIRMED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "HUMAN",
        "sla_seconds": 172800,
        "description": "CEO gate: profile + needs-fit review confirmed",
    },
    "DELIVERED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "HUMAN",
        "sla_seconds": 259200,
        "description": "CEO gate: delivery to customer",
    },
    "FEEDBACK": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 604800,
        "description": "Awaiting customer feedback",
    },
    "CLOSED": {
        "enter_event": "NODE_ENTER",
        "exit_event": "NODE_EXIT_OK",
        "gate": "AUTO",
        "sla_seconds": 86400,
        "description": "Engagement closed and sealed",
    },
}

#: Defect taxonomy — canonical class labels.
DEFECT_TAXONOMY: frozenset[str] = frozenset({
    "deploy-fail",
    "scaffold-unknown-entity",
    "ui-check-fail",
    "needs-fit-BLOCK",
    "conversion-error",
    "sync-ssh-fail",
    "human-gate-stall",
    "retry-exhausted",
    "audit-chain-broken",
    "unknown",
})

#: Triage statuses that belong to the qualify path (monitored for stall/fail).
_QUALIFY_STATUSES: frozenset[str] = frozenset({"qualify"})

#: Nodes that are only relevant for non-qualify paths (excluded from qualify metrics).
_NON_QUALIFY_NODES: frozenset[str] = frozenset({"CALL_QUEUE", "GAP_RECORDED", "PM_TRIAGE"})

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class NodeState:
    node_id: str
    case_id: str
    slug: str
    entered_at: str | None          # ISO-8601 string or None
    exited_at: str | None           # ISO-8601 string or None
    status: str                     # in_progress | complete | stalled | failed | skipped
    dwell_seconds: float            # seconds since enter (or 0 if not entered)
    error_class: str | None         # from NODE_FAIL event
    detail: str | None              # free note (non-PII)


@dataclasses.dataclass
class Alert:
    alert_type: str                 # stall | defect | retry-exhausted
    case_id: str
    slug: str
    node_id: str
    error_class: str | None
    message: str
    entered_at: str | None
    dwell_seconds: float
    sla_seconds: int
    severity: str                   # warn | error | critical


@dataclasses.dataclass
class PipelineHealth:
    generated_at: str               # ISO-8601
    total_cases: int
    active_cases: int
    stalled_cases: int
    failed_cases: int
    closed_cases: int
    alerts: list[Alert]
    node_summary: dict[str, dict]   # node_id -> {in_progress, complete, stalled, failed}

# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

def _load_yaml_file(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        if _HAS_YAML:
            data = _yaml.safe_load(text)
            return data if isinstance(data, dict) else {}
        return {}
    except Exception:
        return {}


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        # Handle 'Z' suffix (Python <3.11 fromisoformat doesn't accept Z)
        clean = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except (ValueError, AttributeError):
        return None

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def load_cases(cases_dir: Path) -> list[dict]:
    """Load all case YAML files from cases_dir (skips README, .gitkeep, dirs)."""
    cases_dir = Path(cases_dir)
    if not cases_dir.exists():
        return []
    result = []
    for p in sorted(cases_dir.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".yaml", ".yml"}:
            continue
        if p.name.lower() in {"readme.md", ".gitkeep", "readme.yaml", "_readme.yaml"}:
            continue
        if p.name.startswith("_") or p.name.startswith("."):
            continue
        data = _load_yaml_file(p)
        if data:
            # Ensure client_id is present (fall back to stem)
            if "client_id" not in data:
                data["client_id"] = p.stem
            result.append(data)
    return result


def project_node_states(case: dict, now: datetime) -> list[NodeState]:
    """Project pipeline_events list into per-node NodeState objects.

    For each node that has at least one event, determines:
    - entered_at (first NODE_ENTER ts)
    - exited_at (first NODE_EXIT_OK ts after enter)
    - failed_at / error_class (NODE_FAIL)
    - status: in_progress | complete | stalled | failed | skipped

    Nodes with no events at all are omitted (not 'skipped' — just absent).
    """
    case_id = case.get("client_id", "")
    slug = case.get("slug", "") or ""
    events: list[dict] = case.get("pipeline_events", []) or []

    # Index events per node
    by_node: dict[str, list[dict]] = {}
    for ev in events:
        nid = ev.get("node_id")
        if nid and nid in NODES:
            by_node.setdefault(nid, []).append(ev)

    states: list[NodeState] = []
    for node_id, node_evs in by_node.items():
        node_meta = NODES[node_id]
        sla_seconds = node_meta["sla_seconds"]

        # Find enter, exit, fail events (chronological)
        enters = [e for e in node_evs if e.get("event") == "NODE_ENTER"]
        exits  = [e for e in node_evs if e.get("event") == "NODE_EXIT_OK"]
        fails  = [e for e in node_evs if e.get("event") == "NODE_FAIL"]

        entered_at_str: str | None = enters[0].get("ts") if enters else None

        # Latest-terminal-wins: a NODE_EXIT_OK or NODE_FAIL emitted later
        # supersedes an earlier terminal event for the same node. This makes a
        # retry (transient fail then success) and a re-judgment (codex Step 4b
        # upgrading a conservative deterministic NEEDS_FIT BLOCK to PASS, or
        # vice-versa) resolve to the current truth instead of latching on the
        # first failure. The full event history stays in the case YAML for audit.
        terminals = sorted(exits + fails, key=lambda e: e.get("ts") or "")
        latest_terminal = terminals[-1] if terminals else None

        exited_at_str: str | None = None
        error_class: str | None = None
        if latest_terminal is not None and latest_terminal.get("event") == "NODE_EXIT_OK":
            exited_at_str = latest_terminal.get("ts")

        entered_at_dt = _parse_iso(entered_at_str)
        exited_at_dt  = _parse_iso(exited_at_str)

        # Compute dwell
        dwell = 0.0
        if entered_at_dt:
            end = exited_at_dt if exited_at_dt else now
            dwell = max(0.0, (end - entered_at_dt).total_seconds())

        # Determine status from the latest terminal event
        if latest_terminal is not None:
            if latest_terminal.get("event") == "NODE_FAIL":
                status = "failed"
                error_class = latest_terminal.get("error_class")
            else:
                status = "complete"
        elif enters:
            # in_progress: check for stall
            if entered_at_dt and dwell > sla_seconds:
                status = "stalled"
            else:
                status = "in_progress"
        else:
            status = "skipped"

        states.append(NodeState(
            node_id=node_id,
            case_id=case_id,
            slug=slug,
            entered_at=entered_at_str,
            exited_at=exited_at_str,
            status=status,
            dwell_seconds=dwell,
            error_class=error_class,
            detail=None,
        ))

    return states


def classify_defect(state: NodeState, processed_detail: str | None = None) -> str:
    """Map a NodeState (failed or stalled) to a DEFECT_TAXONOMY class.

    Uses state.error_class if already set; falls back to node_id heuristics
    and processed_detail if available.
    """
    ec = state.error_class or ""
    if ec in DEFECT_TAXONOMY:
        return ec

    # Node-id heuristics
    if state.node_id == "DEPLOYED":
        if processed_detail and "ssh" in processed_detail.lower():
            return "sync-ssh-fail"
        return "deploy-fail"
    if state.node_id == "SCAFFOLDED":
        return "scaffold-unknown-entity"
    if state.node_id == "UI_CHECKED":
        return "ui-check-fail"
    if state.node_id == "NEEDS_FIT":
        return "needs-fit-BLOCK"
    if state.node_id == "SUBMITTED":
        return "conversion-error"

    # Human-gate nodes
    if NODES.get(state.node_id, {}).get("gate") == "HUMAN" and state.status in ("stalled", "in_progress"):
        return "human-gate-stall"

    # Processed detail keyword fallback
    if processed_detail:
        pd = processed_detail.lower()
        if "retry" in pd:
            return "retry-exhausted"
        if "ssh" in pd:
            return "sync-ssh-fail"
        if "chain" in pd or "hash" in pd:
            return "audit-chain-broken"

    if state.status == "stalled" and NODES.get(state.node_id, {}).get("gate") == "HUMAN":
        return "human-gate-stall"

    return "unknown"


def detect_stalls(
    states: list[NodeState],
    now: datetime,
    *,
    processed: list[dict] | None = None,
) -> list[Alert]:
    """Generate Alert objects for stalled, failed, or retry-exhausted nodes.

    Parameters
    ----------
    states:
        NodeState list from project_node_states() for a single case.
    now:
        Current UTC datetime (injected by caller).
    processed:
        Optional list of processed.jsonl records for the same case_id.
        Used to detect retry-exhausted and disambiguate DEPLOYED defects.

    Notes
    -----
    Only qualify-tier cases contribute to stall/fail alerts.
    Non-qualify nodes (CALL_QUEUE, GAP_RECORDED, PM_TRIAGE) are skipped.
    """
    alerts: list[Alert] = []
    processed = processed or []

    for state in states:
        if state.node_id in _NON_QUALIFY_NODES:
            continue

        node_meta = NODES.get(state.node_id, {})
        sla_seconds = node_meta.get("sla_seconds", 0)
        is_human_gate = node_meta.get("gate") == "HUMAN"

        if state.status == "stalled":
            defect = classify_defect(state)
            # Human-gate stall gets its own alert_type distinction
            if is_human_gate:
                defect = "human-gate-stall"
                severity = "warn"
                atype = "stall"
            else:
                severity = "error"
                atype = "stall"

            alerts.append(Alert(
                alert_type=atype,
                case_id=state.case_id,
                slug=state.slug,
                node_id=state.node_id,
                error_class=defect,
                message=(
                    f"{state.node_id} stalled for {state.dwell_seconds:.0f}s "
                    f"(SLA {sla_seconds}s)"
                ),
                entered_at=state.entered_at,
                dwell_seconds=state.dwell_seconds,
                sla_seconds=sla_seconds,
                severity=severity,
            ))

        elif state.status == "failed":
            defect = classify_defect(state)
            # Check for retry-exhausted in processed records
            retry_count = sum(
                1 for p in processed
                if p.get("slug") == state.slug and p.get("status") == "failed"
            )
            if retry_count >= 3:
                atype = "retry-exhausted"
                severity = "critical"
                defect = "retry-exhausted"
            else:
                atype = "defect"
                severity = "error"

            alerts.append(Alert(
                alert_type=atype,
                case_id=state.case_id,
                slug=state.slug,
                node_id=state.node_id,
                error_class=defect,
                message=(
                    f"{state.node_id} FAILED: {defect} "
                    f"(dwell {state.dwell_seconds:.0f}s)"
                ),
                entered_at=state.entered_at,
                dwell_seconds=state.dwell_seconds,
                sla_seconds=sla_seconds,
                severity=severity,
            ))

        elif state.status == "in_progress" and is_human_gate:
            # Human gate approaching SLA — warn early
            if state.dwell_seconds > sla_seconds * 0.8:
                alerts.append(Alert(
                    alert_type="stall",
                    case_id=state.case_id,
                    slug=state.slug,
                    node_id=state.node_id,
                    error_class="human-gate-stall",
                    message=(
                        f"{state.node_id} human gate at "
                        f"{state.dwell_seconds:.0f}s (SLA {sla_seconds}s, 80% threshold)"
                    ),
                    entered_at=state.entered_at,
                    dwell_seconds=state.dwell_seconds,
                    sla_seconds=sla_seconds,
                    severity="warn",
                ))

    return alerts


def _load_processed(processed_path: Path | None) -> list[dict]:
    """Load processed.jsonl records (list of JSON dicts, one per line)."""
    if processed_path is None:
        return []
    p = Path(processed_path)
    if not p.exists():
        return []
    records = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return records


def aggregate_health(
    cases: list[dict],
    now: datetime,
    *,
    processed: list[dict] | None = None,
) -> PipelineHealth:
    """Compute overall pipeline health from loaded case dicts.

    Only qualify-tier cases count toward active/stalled/failed metrics.
    """
    processed = processed or []

    total = len(cases)
    active = 0
    stalled = 0
    failed = 0
    closed = 0
    all_alerts: list[Alert] = []

    # Node summary: {node_id: {in_progress, complete, stalled, failed, skipped}}
    node_summary: dict[str, dict] = {
        nid: {"in_progress": 0, "complete": 0, "stalled": 0, "failed": 0, "skipped": 0}
        for nid in NODES
    }

    for case in cases:
        ts = case.get("triage_status")
        case_id = case.get("client_id", "")
        states = project_node_states(case, now)

        # Per-node summary (all cases)
        for st in states:
            if st.node_id in node_summary:
                bucket = st.status if st.status in node_summary[st.node_id] else "skipped"
                node_summary[st.node_id][bucket] += 1

        # Only qualify cases contribute to stall/fail metrics
        if ts in _QUALIFY_STATUSES:
            case_status_set = {st.status for st in states}

            if "closed" in {case.get("triage_status")} or ts == "closed":
                closed += 1
            elif "failed" in case_status_set:
                failed += 1
            elif "stalled" in case_status_set:
                stalled += 1
            else:
                active += 1

            # Processed records for this case (for retry-exhausted detection)
            case_processed = [p for p in processed if p.get("case_id") == case_id or p.get("slug") == case.get("slug")]
            alerts = detect_stalls(states, now, processed=case_processed)
            all_alerts.extend(alerts)

    if ts == "closed":
        closed += 1
        active = max(0, active)

    return PipelineHealth(
        generated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        total_cases=total,
        active_cases=active,
        stalled_cases=stalled,
        failed_cases=failed,
        closed_cases=closed,
        alerts=all_alerts,
        node_summary=node_summary,
    )


def render_summary(health: PipelineHealth, output: str = "text") -> str:
    """Render a PipelineHealth summary as text or JSON."""
    if output == "json":
        return json.dumps(dataclasses.asdict(health), indent=2, ensure_ascii=False)

    lines = [
        f"Pipeline Health — {health.generated_at}",
        f"  Total cases : {health.total_cases}",
        f"  Active      : {health.active_cases}",
        f"  Stalled     : {health.stalled_cases}",
        f"  Failed      : {health.failed_cases}",
        f"  Closed      : {health.closed_cases}",
    ]
    if health.alerts:
        lines.append(f"\nAlerts ({len(health.alerts)}):")
        for a in health.alerts:
            lines.append(
                f"  [{a.severity.upper()}] {a.alert_type} | {a.slug} | "
                f"{a.node_id} | {a.error_class} | {a.message}"
            )
    else:
        lines.append("\nNo alerts.")

    lines.append("\nNode summary:")
    for nid, counts in health.node_summary.items():
        total_n = sum(counts.values())
        if total_n == 0:
            continue
        parts = ", ".join(f"{k}={v}" for k, v in counts.items() if v > 0)
        lines.append(f"  {nid}: {parts}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Alerts deduplication & append
# ---------------------------------------------------------------------------

def _alert_dedup_key(a: Alert) -> str:
    """Unique key for deduplication: case+node+alert_type+entered_at."""
    return f"{a.case_id}|{a.node_id}|{a.alert_type}|{a.entered_at}"


def _load_existing_alert_keys(alerts_path: Path) -> set[str]:
    """Parse existing alerts.md to extract dedup keys from structured lines."""
    if not alerts_path.exists():
        return set()
    keys: set[str] = set()
    for line in alerts_path.read_text(encoding="utf-8").splitlines():
        # Lines written by us look like:
        # | <ts> | <case_id> | <slug> | <node_id> | <type> | ... | <entered_at> |
        # We use a simple heuristic: split on | and reassemble the dedup key.
        parts = [p.strip() for p in line.split("|") if p.strip()]
        # Expected layout (after filtering blanks): ts, case_id, slug, node_id, type, ..., entered_at
        if len(parts) >= 7:
            try:
                # case_id=parts[1], node_id=parts[3], type=parts[4], entered_at=parts[-1]
                key = f"{parts[1]}|{parts[3]}|{parts[4]}|{parts[-1]}"
                keys.add(key)
            except IndexError:
                pass
    return keys


def append_alerts(alerts: list[Alert], alerts_path: Path) -> int:
    """Append new alerts (deduplicated) to alerts_path.

    Returns number of new alerts written.
    """
    if not alerts:
        return 0

    alerts_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialise file with header if absent
    if not alerts_path.exists():
        alerts_path.write_text(
            "<!-- append-only pipeline alerts (PII-free), written by pipeline_monitor.py --alert -->\n"
            "| ts | case_id | slug | node_id | alert_type | error_class | severity | dwell_s | sla_s | entered_at |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )

    existing_keys = _load_existing_alert_keys(alerts_path)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    written = 0
    with open(alerts_path, "a", encoding="utf-8") as fh:
        for a in alerts:
            key = _alert_dedup_key(a)
            if key in existing_keys:
                continue
            row = (
                f"| {now_str} | {a.case_id} | {a.slug} | {a.node_id} | "
                f"{a.alert_type} | {a.error_class or '-'} | {a.severity} | "
                f"{a.dwell_seconds:.0f} | {a.sla_seconds} | {a.entered_at or '-'} |\n"
            )
            fh.write(row)
            existing_keys.add(key)
            written += 1
    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic pipeline health monitor (LLM 0, PII-free)."
    )
    parser.add_argument(
        "--cases-dir",
        default=str(_DEFAULT_CASES_DIR),
        help=f"Path to infra/registry/cases/ (default: {_DEFAULT_CASES_DIR})",
    )
    parser.add_argument(
        "--processed",
        default=None,
        help="Path to processed.jsonl (optional, for retry-exhausted detection).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit JSON output instead of text.",
    )
    parser.add_argument(
        "--alert",
        action="store_true",
        help="Append new alerts to docs/intake-inbox/alerts.md.",
    )
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    cases_dir = Path(args.cases_dir)
    cases = load_cases(cases_dir)
    processed = _load_processed(Path(args.processed) if args.processed else None)

    health = aggregate_health(cases, now, processed=processed)

    # Mirror staleness note
    mirror_dir = _DEFAULT_DATA_MIRROR
    stale_note = ""
    if mirror_dir.exists():
        mirror_files = sorted(mirror_dir.rglob("inbox.jsonl"))
        if mirror_files:
            newest_mtime = max(p.stat().st_mtime for p in mirror_files)
            age_seconds = (now.timestamp() - newest_mtime)
            if age_seconds > 7200:
                stale_note = (
                    f"\nWARN: data-mirror may be stale "
                    f"(newest inbox.jsonl is {age_seconds/3600:.1f}h old — run intake_sync.py)."
                )

    output_str = render_summary(health, output="json" if args.as_json else "text")
    print(output_str)
    if stale_note:
        print(stale_note)

    if args.alert and health.alerts:
        n_written = append_alerts(health.alerts, _DEFAULT_ALERTS_PATH)
        print(f"\n[alert] {n_written} new alert(s) written to {_DEFAULT_ALERTS_PATH}.")

    # Exit 1 if any qualify-tier cases are stalled or failed
    if health.failed_cases > 0 or health.stalled_cases > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
