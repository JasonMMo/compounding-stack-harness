"""
scripts/workflow/gap_registry_report.py

Reads docs/intake-inbox/gap-registry.jsonl, tallies gap frequencies,
and renders docs/intake-inbox/gap-summary.md.

NO LLM, NO network. stdlib + PyYAML only.

Usage:
    python scripts/workflow/gap_registry_report.py
    python scripts/workflow/gap_registry_report.py --registry path/to/gap-registry.jsonl \\
        --policy path/to/qualification_policy.yaml --out path/to/gap-summary.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Default paths (relative to repo root, resolved from this file)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REGISTRY = _REPO_ROOT / "docs" / "intake-inbox" / "gap-registry.jsonl"
_DEFAULT_POLICY = _REPO_ROOT / "apps" / "intake" / "qualification_policy.yaml"
_DEFAULT_OUT = _REPO_ROOT / "docs" / "intake-inbox" / "gap-summary.md"


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def load_registry(path: Path) -> list[dict]:
    """
    Load gap-registry.jsonl. Returns list of dicts.
    Each line is a JSON object: {ts, slug, score, gap_category, todo_axis, ...}
    Empty file or missing file returns [].
    """
    if not path.exists():
        return []
    records: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                # Log bad line but continue — registry must remain readable
                print(
                    f"[gap_registry_report] WARN: line {lineno} parse error: {exc}",
                    file=sys.stderr,
                )
    return records


def tally_gaps(records: list[dict]) -> dict[str, dict]:
    """
    Tally records by gap_category.

    Returns:
        dict: gap_category -> {
            count: int,
            todo_axis: str,
            first_ts: str | None,
            last_ts: str | None,
            slugs: list[str],   # unique slugs that triggered this gap
        }
    """
    tallied: dict[str, dict] = {}
    for rec in records:
        cat = rec.get("gap_category", "unknown")
        ts = rec.get("ts", "")
        slug = rec.get("slug", "")
        axis = rec.get("todo_axis", "unknown")

        if cat not in tallied:
            tallied[cat] = {
                "count": 0,
                "todo_axis": axis,
                "first_ts": ts,
                "last_ts": ts,
                "slugs": [],
            }

        entry = tallied[cat]
        entry["count"] += 1
        entry["todo_axis"] = axis  # last seen axis wins (should be stable per category)

        # Track first/last timestamps (lexicographic ISO-8601 sort)
        if ts:
            if not entry["first_ts"] or ts < entry["first_ts"]:
                entry["first_ts"] = ts
            if not entry["last_ts"] or ts > entry["last_ts"]:
                entry["last_ts"] = ts

        if slug and slug not in entry["slugs"]:
            entry["slugs"].append(slug)

    return tallied


def render_summary(tallied: dict[str, dict], policy: dict, out_path: Path) -> None:
    """
    Write gap-summary.md to out_path.

    Sections:
      1. Top Growth Signals (by frequency) — with PROMOTE flag when count >= threshold
      2. Scope Rejects (excluded from growth signals)
      3. Recently Closed Gaps (already_served:true in policy)
    """
    promotion_threshold = int(policy.get("promotion_threshold", 3))
    gap_defs = policy.get("gap_definitions", {})
    scope_defs = policy.get("scope_mismatch", {})

    # Collect scope reject categories
    scope_categories: set[str] = set()
    for _, defn in scope_defs.items():
        if defn.get("disqualifies", False):
            scope_categories.add(defn.get("gap_category", ""))

    # Collect already_served categories (closed gaps)
    closed_gaps: list[dict] = []
    for _group, entries in gap_defs.items():
        for _key, defn in entries.items():
            if isinstance(defn, dict) and defn.get("already_served", False):
                closed_gaps.append({
                    "gap_category": defn.get("gap_category", ""),
                    "todo_axis": defn.get("todo_axis", ""),
                    "expansion_note": defn.get("expansion_note", "").strip(),
                })

    # Split tallied into growth signals vs scope rejects
    growth_signals: list[tuple[str, dict]] = []
    scope_tallied: list[tuple[str, dict]] = []

    for cat, entry in tallied.items():
        if cat in scope_categories:
            scope_tallied.append((cat, entry))
        else:
            growth_signals.append((cat, entry))

    # Sort growth signals by count desc
    growth_signals.sort(key=lambda x: x[1]["count"], reverse=True)
    scope_tallied.sort(key=lambda x: x[1]["count"], reverse=True)

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = [
        f"# Gap Growth Signals — intake-inbox",
        f"",
        f"> Auto-generated by `gap_registry_report.py` at {now_str}.",
        f"> Source: `docs/intake-inbox/gap-registry.jsonl`.",
        f"> PROMOTE = count >= {promotion_threshold}. Each gap is an expansion ToDo, NOT a permanent reject.",
        f"",
    ]

    # ── Section 1: Top Growth Signals ──
    lines.append("## Top Growth Signals (by frequency)")
    lines.append("")
    if not growth_signals:
        lines.append("_No growth signals recorded yet._")
        lines.append("")
    else:
        lines.append("| gap_category | todo_axis | count | first_seen | last_seen | promote |")
        lines.append("|---|---|---|---|---|---|")
        for cat, entry in growth_signals:
            count = entry["count"]
            promote = "**PROMOTE**" if count >= promotion_threshold else ""
            first_ts = entry.get("first_ts", "") or ""
            last_ts = entry.get("last_ts", "") or ""
            # Truncate to date portion if ISO timestamp
            first_date = first_ts[:10] if len(first_ts) >= 10 else first_ts
            last_date = last_ts[:10] if len(last_ts) >= 10 else last_ts
            lines.append(
                f"| {cat} | {entry['todo_axis']} | {count} | {first_date} | {last_date} | {promote} |"
            )
        lines.append("")

        # Detail blocks for PROMOTE candidates
        promote_cats = [(cat, e) for cat, e in growth_signals if e["count"] >= promotion_threshold]
        if promote_cats:
            lines.append("### PROMOTE Candidates")
            lines.append("")
            lines.append(
                f"> These gap categories have reached count >= {promotion_threshold}. "
                f"Recommend CTO review for Growth-N axis expansion."
            )
            lines.append("")
            for cat, entry in promote_cats:
                lines.append(f"**{cat}** (axis: `{entry['todo_axis']}`, count: {entry['count']})")
                # Find expansion_note from policy
                note = _find_expansion_note(cat, gap_defs)
                if note:
                    lines.append(f"  - {note[:200]}")
                lines.append("")

    # ── Section 2: Scope Rejects ──
    lines.append("## Scope Rejects (excluded from growth signals)")
    lines.append("")
    if not scope_tallied:
        lines.append("_No scope rejects recorded._")
        lines.append("")
    else:
        lines.append("| gap_category | count | first_seen | last_seen |")
        lines.append("|---|---|---|---|")
        for cat, entry in scope_tallied:
            first_date = (entry.get("first_ts", "") or "")[:10]
            last_date = (entry.get("last_ts", "") or "")[:10]
            lines.append(f"| {cat} | {entry['count']} | {first_date} | {last_date} |")
        lines.append("")
        lines.append(
            "> Scope rejects are hard disqualifies (consumer apps, personal projects). "
            "They do NOT represent capability gaps and are excluded from the growth signal table."
        )
        lines.append("")

    # ── Section 3: Recently Closed Gaps ──
    lines.append("## Recently Closed Gaps")
    lines.append("")
    lines.append(
        "> These gaps are marked `already_served:true` in `qualification_policy.yaml`. "
        "Future leads in these categories are no longer flagged."
    )
    lines.append("")
    if not closed_gaps:
        lines.append("_No closed gaps yet._")
        lines.append("")
    else:
        lines.append("| gap_category | todo_axis | note |")
        lines.append("|---|---|---|")
        for gap in closed_gaps:
            note_short = gap["expansion_note"][:100].replace("|", "/").replace("\n", " ")
            lines.append(f"| {gap['gap_category']} | {gap['todo_axis']} | {note_short} |")
        lines.append("")

    # Write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[gap_registry_report] wrote: {out_path}")


def _find_expansion_note(gap_category: str, gap_defs: dict) -> str:
    """Scan gap_defs for a matching gap_category and return expansion_note."""
    for _group, entries in gap_defs.items():
        for _key, defn in entries.items():
            if isinstance(defn, dict) and defn.get("gap_category") == gap_category:
                return defn.get("expansion_note", "").strip()
    return ""


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tally gap-registry.jsonl and render gap-summary.md.",
    )
    parser.add_argument(
        "--registry",
        default=str(_DEFAULT_REGISTRY),
        help=f"Path to gap-registry.jsonl (default: {_DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--policy",
        default=str(_DEFAULT_POLICY),
        help=f"Path to qualification_policy.yaml (default: {_DEFAULT_POLICY})",
    )
    parser.add_argument(
        "--out",
        default=str(_DEFAULT_OUT),
        help=f"Output path for gap-summary.md (default: {_DEFAULT_OUT})",
    )
    args = parser.parse_args(argv)

    registry_path = Path(args.registry)
    policy_path = Path(args.policy)
    out_path = Path(args.out)

    # Load policy
    if not policy_path.exists():
        print(f"[gap_registry_report] ERROR: policy not found: {policy_path}", file=sys.stderr)
        return 1

    with open(policy_path, encoding="utf-8") as fh:
        policy = yaml.safe_load(fh)

    # Load and tally
    records = load_registry(registry_path)
    tallied = tally_gaps(records)

    # Render
    render_summary(tallied, policy, out_path)

    print(
        f"[gap_registry_report] tallied {len(records)} records, "
        f"{len(tallied)} unique gap categories."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
