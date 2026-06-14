"""
scripts/workflow/audit_export.py — dispute-evidence exporter (operator-only).

Reads audit.jsonl (PII tier) + revisions/*.json, verifies the hash chain,
and renders a chronological markdown evidence report.

This tool is meant to be run LOCALLY by an operator with explicit intent.
It DOES read PII (email, free-text answers from revision JSONs) for evidence
purposes — that is acceptable. NEVER commit its output; default out-path is
apps/intake/data-mirror/evidence-export/ (gitignored).

stdlib + PyYAML. LLM 0.

Usage:
    python scripts/workflow/audit_export.py --client-id <id> --data-dir <path> [--out <path>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo root on sys.path so audit.py is importable
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from apps.intake.audit import read_events, verify_chain  # noqa: E402

# ---------------------------------------------------------------------------
# Default output dir (gitignored)
# ---------------------------------------------------------------------------

_DEFAULT_OUT_BASE = REPO_ROOT / "apps" / "intake" / "data-mirror" / "evidence-export"


# ---------------------------------------------------------------------------
# Core export
# ---------------------------------------------------------------------------

def _load_revisions(client_id: str, data_dir: Path) -> list[dict]:
    """Load all revision JSONs for this client. Returns list sorted by ts."""
    rev_dir = data_dir / "clients" / client_id / "revisions"
    if not rev_dir.exists():
        return []
    revisions = []
    for p in sorted(rev_dir.glob("*.json")):
        try:
            with open(p, encoding="utf-8") as fh:
                answers = json.load(fh)
            revisions.append({"ts": p.stem, "answers": answers, "path": str(p)})
        except Exception as exc:
            revisions.append({"ts": p.stem, "answers": {}, "path": str(p), "load_error": str(exc)})
    return revisions


def _render_markdown(
    client_id: str,
    events: list[dict],
    revisions: list[dict],
    chain_ok: bool,
    chain_msg: str,
    exported_at: str,
) -> str:
    lines: list[str] = []
    lines.append(f"# Evidence Report — client_id: {client_id}")
    lines.append("")
    lines.append(f"**Exported at**: {exported_at}  ")
    chain_label = "CHAIN OK" if chain_ok else f"CHAIN BROKEN — {chain_msg}"
    lines.append(f"**Chain verification**: {chain_label}  ")
    lines.append(f"**Total events**: {len(events)}  ")
    lines.append(f"**Total revisions**: {len(revisions)}  ")
    lines.append("")

    # Audit event timeline
    lines.append("## Audit Event Timeline")
    lines.append("")
    if not events:
        lines.append("_No audit events found._")
    else:
        lines.append("| seq | ts | event_type | node | error_class | prev_hash (prefix) |")
        lines.append("|-----|----|-----------:|------|-------------|-------------------|")
        for ev in events:
            seq = ev.get("seq", "")
            ts = ev.get("ts", "")
            et = ev.get("event_type", "")
            node = ev.get("node") or ""
            ec = ev.get("error_class") or ""
            ph = (ev.get("prev_hash") or "")[:12] + "..."
            lines.append(f"| {seq} | {ts} | {et} | {node} | {ec} | {ph} |")
        lines.append("")

        # data fields per event (may include PII)
        lines.append("### Event Data Details")
        lines.append("")
        for ev in events:
            lines.append(f"**seq {ev.get('seq')} — {ev.get('event_type')} @ {ev.get('ts')}**")
            data = ev.get("data", {})
            if data:
                for k, v in data.items():
                    lines.append(f"- `{k}`: {v!r}")
            else:
                lines.append("- _(no data)_")
            lines.append("")

    # Revision timeline (PII context for evidence)
    lines.append("## Answer Revisions")
    lines.append("")
    if not revisions:
        lines.append("_No revisions found._")
    else:
        for rev in revisions:
            lines.append(f"### Revision @ {rev['ts']}")
            err = rev.get("load_error")
            if err:
                lines.append(f"**Load error**: {err}")
            else:
                answers = rev.get("answers", {})
                if answers:
                    for k, v in answers.items():
                        lines.append(f"- `{k}`: {v!r}")
                else:
                    lines.append("- _(empty)_")
            lines.append("")

    # Chain verification detail
    lines.append("## Chain Verification")
    lines.append("")
    lines.append(f"Result: **{chain_label}**")
    lines.append("")

    return "\n".join(lines)


def export_case(
    client_id: str,
    data_dir: str | os.PathLike,
    out_path: Path,
) -> dict:
    """Read audit.jsonl, verify chain, join with revisions, render markdown evidence report.

    Returns dict: {chain_ok: bool, event_count: int, out_path: str}
    """
    data_dir_path = Path(data_dir)
    events = read_events(client_id, data_dir_path)
    chain_ok, chain_msg = verify_chain(client_id, data_dir_path)
    revisions = _load_revisions(client_id, data_dir_path)

    exported_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    md = _render_markdown(
        client_id=client_id,
        events=events,
        revisions=revisions,
        chain_ok=chain_ok,
        chain_msg=chain_msg,
        exported_at=exported_at,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")

    return {
        "chain_ok": chain_ok,
        "event_count": len(events),
        "out_path": str(out_path),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Dispute-evidence exporter. Reads PII audit.jsonl + revisions "
            "for a client, verifies hash chain, and renders a markdown evidence report. "
            "Operator-only tool — never commit its output."
        )
    )
    parser.add_argument(
        "--client-id",
        required=True,
        help="16-hex client_id (sha256 prefix of email)",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="DATA_DIR path (default: DATA_DIR env var or apps/intake/data)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help=(
            "Output .md path (default: "
            "apps/intake/data-mirror/evidence-export/<client_id>-<ts>.md)"
        ),
    )
    args = parser.parse_args(argv)

    # Resolve data_dir
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        env = os.environ.get("DATA_DIR")
        data_dir = Path(env) if env else REPO_ROOT / "apps" / "intake" / "data"

    # Resolve out_path
    if args.out:
        out_path = Path(args.out)
    else:
        ts_label = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = _DEFAULT_OUT_BASE / f"{args.client_id}-{ts_label}.md"

    result = export_case(
        client_id=args.client_id,
        data_dir=data_dir,
        out_path=out_path,
    )

    status_label = "CHAIN OK" if result["chain_ok"] else "CHAIN BROKEN"
    print(f"{status_label} | events={result['event_count']} | out={result['out_path']}")

    return 0 if result["chain_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
