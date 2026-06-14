"""pipeline_dashboard.py -- Localhost-only HTML dashboard for the customer-intake pipeline.

Serves a self-contained HTML page (no external CSS/JS/CDN) on 127.0.0.1 that
mirrors the same PII-free data as the CLI pipeline_status.py, rendered as
coloured chips, health cards, and alert rows.

stdlib only. LLM 0. No PII accessed or rendered.

CLI:
  python scripts/workflow/pipeline_dashboard.py [--host 127.0.0.1] [--port 8787]
      [--cases-dir DIR] [--once]
"""
from __future__ import annotations

import argparse
import http.server
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path setup (mirrors pipeline_status.py)
# ---------------------------------------------------------------------------

_WORKFLOW_DIR = Path(__file__).resolve().parent
if str(_WORKFLOW_DIR) not in sys.path:
    sys.path.insert(0, str(_WORKFLOW_DIR))

from pipeline_monitor import (  # noqa: E402
    NodeState,
    PipelineHealth,
    load_cases,
    project_node_states,
    aggregate_health,
    _load_processed,
)

# ---------------------------------------------------------------------------
# Repo paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_CASES_DIR = _REPO_ROOT / "infra" / "registry" / "cases"
_DEFAULT_PROCESSED = _REPO_ROOT / "apps" / "intake" / "data-mirror" / "processed.jsonl"
_DEFAULT_MIRROR_DIR = _REPO_ROOT / "apps" / "intake" / "data-mirror"
_DEFAULT_EVIDENCE_DIR = _REPO_ROOT / "docs" / "intake-inbox" / "evidence"

# ---------------------------------------------------------------------------
# Node order constants
# ---------------------------------------------------------------------------

#: Qualify-path node order for the horizontal chip row.
QUALIFY_NODE_ORDER: list[str] = [
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

#: Branch nodes -- rendered only if entered.
BRANCH_NODES: list[str] = ["CALL_QUEUE", "GAP_RECORDED", "PM_TRIAGE"]

# ---------------------------------------------------------------------------
# PII-safe field whitelist (only these keys may appear in rendered HTML)
# ---------------------------------------------------------------------------

_SAFE_CASE_KEYS: frozenset[str] = frozenset({
    "client_id", "slug", "triage_status", "score",
    "pipeline_events",  # iterated, not dumped verbatim
})

# ---------------------------------------------------------------------------
# Duration helper (same logic as pipeline_status.py)
# ---------------------------------------------------------------------------

def _format_duration(seconds: float) -> str:
    """Human-readable duration: '45s', '2m', '2h 34m'."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.0f}m"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


# ---------------------------------------------------------------------------
# PII filter
# ---------------------------------------------------------------------------

def _pii_safe_case(case: dict) -> dict:
    """Return a copy of case containing only known PII-free keys."""
    return {k: v for k, v in case.items() if k in _SAFE_CASE_KEYS}


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _h(text: str) -> str:
    """HTML-escape a plain string."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _chip_color(status: str) -> str:
    return {
        "complete":    "#2e7d32",   # green
        "in_progress": "#1565c0",   # blue
        "stalled":     "#e65100",   # amber
        "failed":      "#b71c1c",   # red
        "skipped":     "#757575",   # grey
    }.get(status, "#757575")


def _alert_bg(severity: str) -> str:
    return {
        "warn":     "#fff8e1",
        "error":    "#ffebee",
        "critical": "#4a0000",
    }.get(severity, "#fff8e1")


def _alert_fg(severity: str) -> str:
    return "#ffffff" if severity == "critical" else "#212121"


# ---------------------------------------------------------------------------
# Evidence lookup
# ---------------------------------------------------------------------------

def _find_evidence(node_id: str, slug: str, evidence_dir: Path) -> str | None:
    """Return path string of latest evidence file for node+slug, or None."""
    if not evidence_dir.exists():
        return None
    matches = sorted(evidence_dir.glob(f"{node_id}-{slug}-*.txt"))
    return str(matches[-1]) if matches else None


# ---------------------------------------------------------------------------
# HTML renderer (pure function, unit-testable)
# ---------------------------------------------------------------------------

def render_dashboard_html(
    cases: list[dict],
    health: PipelineHealth,
    now: datetime,
    *,
    evidence_dir: Path,
    mirror_dir: Path | None,
) -> str:
    """Return the full HTML string for the pipeline dashboard.

    Parameters are PII-free by contract (cases have passed through _pii_safe_case).
    """
    ts_str = _h(health.generated_at)

    # Mirror freshness
    if mirror_dir is not None and mirror_dir.exists():
        mtime = mirror_dir.stat().st_mtime
        mtime_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        age_seconds = (now - mtime_dt).total_seconds()
        mtime_str = _h(mtime_dt.strftime("%Y-%m-%d %H:%M:%S UTC"))
        if age_seconds > 7200:
            mirror_line = (
                f'Mirror last synced: {mtime_str} '
                f'<span style="background:#f57f17;color:#fff;padding:2px 6px;border-radius:3px;">'
                f'WARN: mirror stale (&gt;2h)</span>'
            )
        else:
            mirror_line = f"Mirror last synced: {mtime_str}"
    else:
        mirror_line = "<em>(no local mirror synced yet)</em>"

    # Health card rows
    def _card(label: str, count: int, warn_color: str | None = None) -> str:
        bg = warn_color if (warn_color and count > 0) else "#f5f5f5"
        fg = "#fff" if (warn_color and count > 0) else "#212121"
        return (
            f'<div style="display:inline-block;min-width:90px;padding:12px 16px;'
            f'margin:4px;border-radius:6px;background:{bg};color:{fg};'
            f'text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.2);">'
            f'<div style="font-size:1.8em;font-weight:bold;">{count}</div>'
            f'<div style="font-size:.8em;margin-top:4px;">{label}</div></div>'
        )

    cards_html = (
        _card("Total", health.total_cases)
        + _card("Active", health.active_cases)
        + _card("Stalled", health.stalled_cases, "#e65100")
        + _card("Failed", health.failed_cases, "#b71c1c")
        + _card("Closed", health.closed_cases)
    )

    # Alerts section
    if health.alerts:
        alert_rows = []
        for a in health.alerts:
            bg = _alert_bg(a.severity)
            fg = _alert_fg(a.severity)
            alert_rows.append(
                f'<div style="padding:8px 12px;margin:3px 0;border-radius:4px;'
                f'background:{bg};color:{fg};font-family:monospace;font-size:.85em;">'
                f'[{_h(a.severity.upper())}] {_h(a.slug)} / {_h(a.node_id)} '
                f'-- {_h(a.error_class or "?")} -- {_h(a.message)}'
                f"</div>"
            )
        alerts_html = "\n".join(alert_rows)
    else:
        alerts_html = '<p style="color:#555;">No active alerts.</p>'

    # Per-case pipeline chips
    if not cases:
        cases_html = (
            '<div style="padding:24px;background:#e8f5e9;border-radius:8px;'
            'text-align:center;color:#2e7d32;font-size:1.1em;">'
            "No cases yet -- pipeline idle.</div>"
        )
    else:
        case_blocks = []
        for raw_case in cases:
            case = _pii_safe_case(raw_case)
            slug = _h(str(case.get("slug") or case.get("client_id", "?")))
            triage = _h(str(case.get("triage_status") or "-"))

            states = project_node_states(raw_case, now)
            state_map: dict[str, NodeState] = {s.node_id: s for s in states}

            # Qualify-path chip row
            chips = []
            has_issue = False
            for nid in QUALIFY_NODE_ORDER:
                st = state_map.get(nid)
                status = st.status if st else "skipped"
                color = _chip_color(status)
                chips.append(
                    f'<span style="display:inline-block;padding:4px 8px;margin:2px;'
                    f'border-radius:4px;background:{color};color:#fff;'
                    f'font-size:.75em;font-family:monospace;" title="{_h(nid)}">'
                    f"{_h(nid[:8])}</span>"
                )
                if status in ("failed", "stalled"):
                    has_issue = True

            chip_row = "".join(chips)

            # Branch nodes (only if entered)
            branch_chips = []
            for nid in BRANCH_NODES:
                st = state_map.get(nid)
                if st:
                    color = _chip_color(st.status)
                    branch_chips.append(
                        f'<span style="display:inline-block;padding:4px 8px;margin:2px;'
                        f'border-radius:4px;background:{color};color:#fff;'
                        f'font-size:.75em;font-family:monospace;">{_h(nid)}</span>'
                    )
            branch_row = ""
            if branch_chips:
                branch_row = (
                    '<div style="margin-top:4px;">'
                    '<span style="font-size:.8em;color:#555;">Branch: </span>'
                    + "".join(branch_chips)
                    + "</div>"
                )

            # Drill-in for failed/stalled nodes
            drillin_html = ""
            if has_issue:
                drillin_rows = []
                for nid in QUALIFY_NODE_ORDER:
                    st = state_map.get(nid)
                    if st and st.status in ("failed", "stalled"):
                        ev_path = _find_evidence(nid, st.slug or "", evidence_dir)
                        ev_str = _h(ev_path) if ev_path else "(none)"
                        drillin_rows.append(
                            f'<tr>'
                            f'<td style="padding:4px 8px;color:#b71c1c;font-weight:bold;">'
                            f'{_h(st.status.upper())}</td>'
                            f'<td style="padding:4px 8px;font-family:monospace;">'
                            f'{_h(nid)}</td>'
                            f'<td style="padding:4px 8px;">'
                            f'{_h(st.error_class or "-")}</td>'
                            f'<td style="padding:4px 8px;">'
                            f'{_h(_format_duration(st.dwell_seconds))}</td>'
                            f'<td style="padding:4px 8px;font-size:.8em;color:#555;">'
                            f'{_h(st.entered_at or "-")}</td>'
                            f'<td style="padding:4px 8px;font-size:.75em;color:#555;">'
                            f'{ev_str}</td>'
                            f'</tr>'
                        )
                if drillin_rows:
                    drillin_html = (
                        '<div style="margin-top:8px;overflow-x:auto;">'
                        '<table style="border-collapse:collapse;font-size:.82em;'
                        'width:100%;border:1px solid #e0e0e0;">'
                        '<thead><tr style="background:#fafafa;">'
                        '<th style="padding:4px 8px;text-align:left;">Status</th>'
                        '<th style="padding:4px 8px;text-align:left;">Node</th>'
                        '<th style="padding:4px 8px;text-align:left;">Error class</th>'
                        '<th style="padding:4px 8px;text-align:left;">Dwell</th>'
                        '<th style="padding:4px 8px;text-align:left;">Entered</th>'
                        '<th style="padding:4px 8px;text-align:left;">Evidence</th>'
                        "</tr></thead><tbody>"
                        + "".join(drillin_rows)
                        + "</tbody></table></div>"
                    )

            case_blocks.append(
                f'<div style="margin-bottom:16px;padding:12px 16px;border:1px solid #e0e0e0;'
                f'border-radius:6px;background:#fafafa;">'
                f'<div style="font-weight:bold;margin-bottom:6px;">'
                f'{slug} <span style="font-weight:normal;color:#555;font-size:.9em;">'
                f'({triage})</span></div>'
                f'<div>{chip_row}</div>'
                f'{branch_row}'
                f'{drillin_html}'
                f"</div>"
            )
        cases_html = "\n".join(case_blocks)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="15">
<title>Pipeline Monitor</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0; padding: 16px 24px; background: #fff; color: #212121;
  }}
  h1 {{ font-size: 1.3em; margin-bottom: 4px; }}
  h2 {{ font-size: 1em; margin: 20px 0 8px; border-bottom: 1px solid #e0e0e0;
        padding-bottom: 4px; }}
  .meta {{ color: #555; font-size: .85em; margin-bottom: 8px; }}
  .cards {{ margin-bottom: 8px; }}
</style>
</head>
<body>
<h1>Pipeline Monitor <span style="font-weight:normal;font-size:.7em;color:#555;">(PII-free, local)</span></h1>
<div class="meta">Generated: {ts_str}</div>
<div class="meta">{mirror_line}</div>

<h2>Health Summary</h2>
<div class="cards">{cards_html}</div>

<h2>Alerts</h2>
{alerts_html}

<h2>Cases</h2>
{cases_html}
</body>
</html>"""
    return html


# ---------------------------------------------------------------------------
# HTTP request handler
# ---------------------------------------------------------------------------

class _DashboardHandler(http.server.BaseHTTPRequestHandler):
    """Serves the dashboard HTML on GET /, 404 for everything else."""

    # Injected by serve()
    cases_dir: Path
    processed_path: Path | None
    evidence_dir: Path
    mirror_dir: Path | None

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Suppress per-request server log noise."""

    def do_GET(self) -> None:  # noqa: N802
        if self.path not in ("/", ""):
            self.send_response(404)
            self.end_headers()
            return

        now = datetime.now(timezone.utc)
        try:
            cases = load_cases(self.cases_dir)
            processed = None
            if self.processed_path is not None:
                processed = _load_processed(self.processed_path)
            health = aggregate_health(cases, now, processed=processed)
            html = render_dashboard_html(
                cases, health, now,
                evidence_dir=self.evidence_dir,
                mirror_dir=self.mirror_dir,
            )
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:  # noqa: BLE001
            err = f"<pre>Error: {exc}</pre>".encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)


# ---------------------------------------------------------------------------
# Server factory
# ---------------------------------------------------------------------------

def serve(
    host: str,
    port: int,
    cases_dir: Path,
    *,
    processed_path: Path | None = None,
    evidence_dir: Path | None = None,
    mirror_dir: Path | None = None,
) -> None:
    """Start a ThreadingHTTPServer on host:port and block until Ctrl+C."""
    _ev_dir = evidence_dir or _DEFAULT_EVIDENCE_DIR

    # Build handler class with injected config via class attributes
    handler = type(
        "_ConfiguredHandler",
        (_DashboardHandler,),
        {
            "cases_dir": cases_dir,
            "processed_path": processed_path,
            "evidence_dir": _ev_dir,
            "mirror_dir": mirror_dir,
        },
    )

    server = http.server.ThreadingHTTPServer((host, port), handler)
    print(f"Pipeline dashboard at http://{host}:{port}/  (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_LOOPBACK = {"127.0.0.1", "localhost", "::1"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline HTML dashboard (PII-free, localhost-only)."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8787, help="Bind port (default: 8787)")
    parser.add_argument(
        "--cases-dir",
        default=str(_DEFAULT_CASES_DIR),
        help=f"Path to infra/registry/cases/ (default: {_DEFAULT_CASES_DIR})",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Print HTML to stdout and exit (no server started). Used by tests.",
    )
    args = parser.parse_args(argv)

    if args.host not in _LOOPBACK:
        print(
            f"WARNING: --host {args.host!r} is not a loopback address. "
            "External exposure is a TODO and is not hardened.",
            file=sys.stderr,
            flush=True,
        )

    cases_dir = Path(args.cases_dir)
    processed_path = _DEFAULT_PROCESSED if _DEFAULT_PROCESSED.exists() else None
    mirror_dir = _DEFAULT_MIRROR_DIR if _DEFAULT_MIRROR_DIR.exists() else None

    if args.once:
        now = datetime.now(timezone.utc)
        cases = load_cases(cases_dir)
        processed = _load_processed(processed_path) if processed_path else None
        health = aggregate_health(cases, now, processed=processed)
        html = render_dashboard_html(
            cases, health, now,
            evidence_dir=_DEFAULT_EVIDENCE_DIR,
            mirror_dir=mirror_dir,
        )
        sys.stdout.buffer.write(html.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
        return 0

    serve(
        args.host, args.port, cases_dir,
        processed_path=processed_path,
        evidence_dir=_DEFAULT_EVIDENCE_DIR,
        mirror_dir=mirror_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
