"""pipeline_status.py — CLI viewer for pipeline node states.

Renders a status table (all cases) and an optional per-case node graph
with status glyphs. Drill-in for failed/stalled nodes surfaces error_class
and evidence path (PII-free).

stdlib only. LLM 0. No PII accessed.

CLI:
  python scripts/workflow/pipeline_status.py [--cases-dir DIR] [--case CASE_ID] [--graph]
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add workflow dir to path so we can import pipeline_monitor
_WORKFLOW_DIR = Path(__file__).resolve().parent
if str(_WORKFLOW_DIR) not in sys.path:
    sys.path.insert(0, str(_WORKFLOW_DIR))

from pipeline_monitor import (  # noqa: E402
    NODES,
    NodeState,
    load_cases,
    project_node_states,
    detect_stalls,
    action_hint,
)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_CASES_DIR = _REPO_ROOT / "infra" / "registry" / "cases"
_DEFAULT_EVIDENCE_DIR = _REPO_ROOT / "docs" / "intake-inbox" / "evidence"

# ---------------------------------------------------------------------------
# Status glyphs
# ---------------------------------------------------------------------------

_GLYPH = {
    "complete":    "OK",
    "in_progress": "...",
    "stalled":     "WAIT",
    "failed":      "FAIL",
    "skipped":     "skip",
    "unknown":     "?",
}

_ASCII_GLYPH = {
    "complete":    "OK",
    "in_progress": ">>",
    "stalled":     "!>",
    "failed":      "XX",
    "skipped":     "..",
    "unknown":     "??",
}

# Qualify path node order (linear display)
_QUALIFY_NODE_ORDER = [
    "SUBMITTED",
    "TRIAGED",
    "DRAFT_PROMOTED",
    "SCAFFOLDED",
    "DEPLOYED",
    "UI_CHECKED",
    "NEEDS_FIT",
    "PROFILE_CONFIRMED",
    "DELIVERED",
    "FEEDBACK",
    "CLOSED",
]

# ---------------------------------------------------------------------------
# Render helpers
# ---------------------------------------------------------------------------

def _format_duration(seconds: float) -> str:
    """Human-readable duration: e.g. '2h 34m', '45s'."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.0f}m"
    else:
        hours = int(seconds // 3600)
        mins  = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def _current_node(states: list[NodeState]) -> tuple[str, str]:
    """Return (node_id, status) of the most advanced non-complete active node.

    Preference: failed > stalled > in_progress > last complete.
    """
    by_status: dict[str, list[NodeState]] = {"failed": [], "stalled": [], "in_progress": [], "complete": []}
    for st in states:
        if st.status in by_status:
            by_status[st.status].append(st)

    for priority in ("failed", "stalled", "in_progress"):
        if by_status[priority]:
            # Pick latest entered
            ranked = sorted(
                by_status[priority],
                key=lambda s: s.entered_at or "",
                reverse=True,
            )
            return ranked[0].node_id, priority

    # All complete or empty — return last complete
    if by_status["complete"]:
        ranked = sorted(by_status["complete"], key=lambda s: s.exited_at or "", reverse=True)
        return ranked[0].node_id, "complete"

    return "-", "unknown"


def render_status_table(cases: list[dict], now: datetime) -> str:
    """Render a compact table: slug | triage_status | current node | status | time-in-node."""
    if not cases:
        return "No cases found."

    rows: list[tuple[str, str, str, str, str]] = []
    for case in cases:
        slug = case.get("slug") or case.get("client_id", "?")
        triage = case.get("triage_status") or "-"
        states = project_node_states(case, now)

        node_id, status = _current_node(states)

        # Find dwell for current node
        dwell_str = "-"
        for st in states:
            if st.node_id == node_id:
                dwell_str = _format_duration(st.dwell_seconds)
                break

        rows.append((slug, triage, node_id, status, dwell_str))

    # Compute column widths
    header = ("slug", "triage", "current_node", "status", "time_in_node")
    widths = [len(h) for h in header]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(row: tuple[str, ...]) -> str:
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))

    sep = "-+-".join("-" * w for w in widths)
    lines = [fmt_row(header), sep]
    for row in rows:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def render_node_graph(case: dict, now: datetime, width: int = 80) -> str:
    """Render a per-case horizontal node pipeline with ASCII status glyphs.

    Only shows the qualify-path nodes. Non-qualify branch nodes are shown
    as a side note if present.

    Format:
      [OK] SUBMITTED -> [>>] TRIAGED -> [XX] DEPLOYED ...
    """
    slug = case.get("slug") or case.get("client_id", "?")
    triage = case.get("triage_status") or "?"
    states = project_node_states(case, now)
    state_map: dict[str, NodeState] = {st.node_id: st for st in states}

    parts = []
    for nid in _QUALIFY_NODE_ORDER:
        st = state_map.get(nid)
        if st:
            glyph = _ASCII_GLYPH.get(st.status, "??")
        else:
            glyph = ".."
        parts.append(f"[{glyph}]{nid[:6]}")

    header = f"Case: {slug}  (triage: {triage})"
    graph_line = " -> ".join(parts)
    # Wrap if over width
    lines = [header, graph_line]

    # Non-qualify branches
    branch_nodes = ["CALL_QUEUE", "GAP_RECORDED", "PM_TRIAGE"]
    branch_parts = []
    for nid in branch_nodes:
        st = state_map.get(nid)
        if st:
            glyph = _ASCII_GLYPH.get(st.status, "??")
            branch_parts.append(f"[{glyph}]{nid}")
    if branch_parts:
        lines.append("Branch: " + " | ".join(branch_parts))

    return "\n".join(lines)


def build_drillin(
    case_id: str,
    cases_dir: Path,
    *,
    evidence_dir: Path | None = None,
) -> dict:
    """Build a PII-free drill-in bundle for a case's failed/stalled nodes.

    Returns a dict with: case_id, slug, issues (list of node dicts with
    error_class and evidence_path), all PII-free.
    """
    cases_dir = Path(cases_dir)
    evidence_dir = Path(evidence_dir) if evidence_dir else _DEFAULT_EVIDENCE_DIR

    # Find the case file
    case_file = cases_dir / f"{case_id}.yaml"
    if not case_file.exists():
        # Try glob
        matches = list(cases_dir.glob(f"{case_id}*.yaml"))
        if not matches:
            return {"case_id": case_id, "error": "case not found", "issues": []}
        case_file = matches[0]

    from pipeline_monitor import _load_yaml_file  # noqa: E402 (local import)
    case = _load_yaml_file(case_file)
    if not case:
        return {"case_id": case_id, "error": "empty case file", "issues": []}

    now = datetime.now(timezone.utc)
    states = project_node_states(case, now)

    issues = []
    for st in states:
        if st.status not in ("failed", "stalled"):
            continue

        # Find matching evidence files (node + slug prefix)
        slug = st.slug or ""
        ev_files = sorted(evidence_dir.glob(f"{st.node_id}-{slug}-*.txt"))
        ev_path_str = str(ev_files[-1]) if ev_files else None

        issues.append({
            "node_id": st.node_id,
            "status": st.status,
            "error_class": st.error_class,
            "dwell_seconds": st.dwell_seconds,
            "entered_at": st.entered_at,
            "evidence_path": ev_path_str,
        })

    return {
        "case_id": case_id,
        "slug": case.get("slug"),
        "triage_status": case.get("triage_status"),
        "issues": issues,
    }


def render_drillin_text(bundle: dict) -> str:
    """Render a drill-in bundle as human-readable text."""
    lines = [
        f"Drill-in: {bundle.get('case_id')}",
        f"  slug:          {bundle.get('slug') or '-'}",
        f"  triage_status: {bundle.get('triage_status') or '-'}",
    ]
    if bundle.get("error"):
        lines.append(f"  ERROR: {bundle['error']}")
        return "\n".join(lines)

    issues = bundle.get("issues", [])
    if not issues:
        lines.append("  No failed or stalled nodes.")
    else:
        lines.append(f"  Issues ({len(issues)}):")
        for iss in issues:
            lines.append(f"    [{iss['status'].upper()}] {iss['node_id']}")
            lines.append(f"      error_class  : {iss.get('error_class') or '-'}")
            lines.append(f"      dwell        : {_format_duration(iss.get('dwell_seconds', 0))}")
            lines.append(f"      entered_at   : {iss.get('entered_at') or '-'}")
            lines.append(f"      evidence_path: {iss.get('evidence_path') or '(none)'}")
            hint = action_hint(iss.get("error_class") or "unknown")
            lines.append(f"      owner        : {hint['owner']}")
            lines.append(f"      action       : {hint['action']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM analysis stub
# ---------------------------------------------------------------------------

def analyze_node_with_llm(
    node_id: str,
    error_class: str | None,
    evidence_path: str | None,
    slug: str,
) -> str:
    """Return a prompt string for on-demand codex analysis of a failed node.

    This function does NOT call any LLM; it constructs the prompt that a
    Claude session would pass to Agent(subagent_type='codex:codex-rescue', ...).
    The actual LLM invocation is performed by the calling Claude session, NOT here.
    """
    ev_note = f"Evidence file: {evidence_path}" if evidence_path else "No evidence file available."
    return (
        f"Pipeline node failure analysis (PII-free):\n"
        f"  slug: {slug}\n"
        f"  node: {node_id}\n"
        f"  error_class: {error_class or 'unknown'}\n"
        f"  {ev_note}\n\n"
        f"Diagnose the root cause of this {node_id} failure ({error_class}) "
        f"and suggest corrective actions. Do not request or output any PII. "
        f"Focus on infra, code, or config root causes."
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline status viewer (PII-free, LLM 0)."
    )
    parser.add_argument(
        "--cases-dir",
        default=str(_DEFAULT_CASES_DIR),
        help=f"Path to infra/registry/cases/ (default: {_DEFAULT_CASES_DIR})",
    )
    parser.add_argument(
        "--case",
        default=None,
        metavar="CASE_ID",
        help="Case ID for drill-in (shows failed/stalled node detail).",
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Show node graph for each case.",
    )
    args = parser.parse_args(argv)

    now = datetime.now(timezone.utc)
    cases_dir = Path(args.cases_dir)
    cases = load_cases(cases_dir)

    if args.case:
        bundle = build_drillin(args.case, cases_dir)
        print(render_drillin_text(bundle))
        # Also show graph for the specific case
        matched = [c for c in cases if c.get("client_id") == args.case]
        if matched:
            print()
            print(render_node_graph(matched[0], now))
        return 0

    print(render_status_table(cases, now))

    if args.graph:
        for case in cases:
            print()
            print(render_node_graph(case, now))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
