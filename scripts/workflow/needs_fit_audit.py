"""
scripts/workflow/needs_fit_audit.py — Needs-Fit Audit Gate deterministic pre-pass.

Phase 5 (pm-delivery-loop Step 4b) helper.

Two responsibilities:
  1. Deterministic pre-pass (LLM 0): parse needs, load manifest entities, load AC,
     build coverage matrix by keyword/slug overlap, write a draft review skeleton.
  2. Build the codex prompt (from needs-fit-prompt-template.md) for the Claude session
     to spawn a codex agent that refines the verdict with judgment.

Usage:
  python scripts/workflow/needs_fit_audit.py \\
      --slug <slug> \\
      --needs-note <path/to/needs-note.md> \\
      --manifest <path/to/screen-manifest.json> \\
      --profile <path/to/profile.yaml> \\
      [--acceptance-criteria <path/to/acceptance-criteria.md>] \\
      [--out <docs/delivery/<slug>>]

Stdout: deterministic envelope + codex prompt (for the Claude session to use).

Constraints:
  - LLM 0 (no external API calls)
  - stdlib + PyYAML only
  - PII never written to docs/
  - ASCII filenames (G-8)
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Repo root
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "pm-delivery-loop"
    / "needs-fit-prompt-template.md"
)

# ---------------------------------------------------------------------------
# PII patterns
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
_PHONE_RE = re.compile(r"(?:0\d{9,10}|\d{2,4}-\d{3,4}-\d{4})")
# The 의뢰인 기본 block: from the heading to the next ## heading (or end of string)
_PII_BLOCK_RE = re.compile(
    r"##\s*의뢰인\s*기본.*?(?=##|\Z)", re.DOTALL | re.UNICODE
)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class NeedItem:
    id: str
    who: str
    what: str
    why: str
    source_section: str


@dataclass
class CoverageRow:
    need_id: str
    need_summary: str
    entity_evidence: list[str] = field(default_factory=list)
    ac_evidence: list[str] = field(default_factory=list)
    verdict: str = "GAP"  # "COVERED" | "PARTIAL" | "GAP"


# ---------------------------------------------------------------------------
# PII stripping
# ---------------------------------------------------------------------------


def strip_pii(text: str) -> str:
    """Remove email/phone patterns and the 의뢰인 기본 block from text."""
    text = _PII_BLOCK_RE.sub("", text)
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _PHONE_RE.sub("[PHONE]", text)
    return text


# ---------------------------------------------------------------------------
# Needs-note parsing
# ---------------------------------------------------------------------------

# Sections to extract needs from (in order of relevance)
_NEED_SECTIONS = {
    "누가": "who",
    "무엇을": "what",
    "왜": "why",
}

# Sections to skip entirely (PII or irrelevant)
_SKIP_SECTIONS = {"의뢰인 기본", "현재", "빈도", "비용·리스크", "IT 기술 메모", "추가 시그널"}


def _section_key(heading: str) -> Optional[str]:
    """Return the canonical section key if the heading matches a known section."""
    h = heading.strip()
    for name in _SKIP_SECTIONS:
        if name in h:
            return None  # skip
    for name, key in _NEED_SECTIONS.items():
        if name in h:
            return key
    return None


def parse_needs(needs_note_md: str) -> list[NeedItem]:
    """Parse a needs-note markdown string into atomic NeedItem list.

    Rules:
    - Ignores the '의뢰인 기본' (PII) section entirely.
    - Extracts bullet-point content from '누가', '무엇을', '왜' sections.
    - Sub-headings (###) within a section are treated as continuation of that section.
    - Each non-empty bullet line becomes a candidate need fragment.
    - Fragments are grouped by section and combined into NeedItem records.
    - PII (email/phone) is never stored in any NeedItem field.
    """
    # Strip the PII block first, before any processing
    safe_md = _PII_BLOCK_RE.sub("", needs_note_md)

    # Split into sections by ## headings
    section_blocks: dict[str, list[str]] = {}
    current_section_key: Optional[str] = None

    for line in safe_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:]
            current_section_key = _section_key(heading)
            if current_section_key and current_section_key not in section_blocks:
                section_blocks[current_section_key] = []
        elif stripped.startswith("### "):
            # sub-heading: keep in current section if active
            pass
        elif current_section_key is not None:
            section_blocks.setdefault(current_section_key, []).append(line)

    # Extract bullet items per section
    def _bullets(lines: list[str]) -> list[str]:
        items = []
        for ln in lines:
            s = ln.strip()
            if s.startswith("- ") or s.startswith("* "):
                content = s[2:].strip()
                # Strip PII patterns from content
                content = _EMAIL_RE.sub("[EMAIL]", content)
                content = _PHONE_RE.sub("[PHONE]", content)
                if content and content != "—":
                    items.append(content)
            elif s and not s.startswith("#") and not s.startswith(">"):
                # Free text paragraphs (pain point blocks etc.)
                content = _EMAIL_RE.sub("[EMAIL]", s)
                content = _PHONE_RE.sub("[PHONE]", content)
                if content and content != "—":
                    items.append(content)
        return items

    who_items = _bullets(section_blocks.get("who", []))
    what_items = _bullets(section_blocks.get("what", []))
    why_items = _bullets(section_blocks.get("why", []))

    # Build NeedItems: zip what+why as primary axes, who as context
    who_str = "; ".join(who_items) if who_items else ""
    needs: list[NeedItem] = []

    # Cross-product: each what × each why → one NeedItem
    # If one list is empty, treat as single empty string
    what_list = what_items if what_items else ["(unspecified)"]
    why_list = why_items if why_items else ["(unspecified)"]

    n = 1
    for what_val in what_list:
        for why_val in why_list:
            needs.append(
                NeedItem(
                    id=f"N-{n}",
                    who=who_str,
                    what=what_val,
                    why=why_val,
                    source_section="무엇을/왜",
                )
            )
            n += 1

    return needs


# ---------------------------------------------------------------------------
# Manifest entity loading
# ---------------------------------------------------------------------------


def load_manifest_entities(manifest_path: Path) -> list[str]:
    """Load entity keys and their domain slugs from a screen-manifest.json.

    Returns a flat list of strings of the form 'entity-key (domain: <domain>)'
    so that keyword matching can cover both the entity key and its domain.
    PII-free by design (manifest contains no PII).
    """
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    entities = data.get("entities", {})
    results: list[str] = []
    for key, info in entities.items():
        domain = info.get("domain", "") if isinstance(info, dict) else ""
        results.append(f"{key} (domain: {domain})")
    return results


# ---------------------------------------------------------------------------
# Acceptance-criteria parsing
# ---------------------------------------------------------------------------


def parse_acceptance_criteria(ac_path: Path) -> list[str]:
    """Parse AC IDs and 기준 text from an acceptance-criteria markdown file.

    Returns list of strings of the form 'AC-N: <criteria text>'.
    Returns [] if the file does not exist.
    """
    if not ac_path or not ac_path.exists():
        return []

    lines = ac_path.read_text(encoding="utf-8").splitlines()
    results: list[str] = []

    # Look for table rows: | AC-N | <criteria> | ... |
    # Also handle plain text lines like "AC-1: ..."
    _ac_table_re = re.compile(r"\|\s*(AC-\d+)\s*\|([^|]+)\|")
    _ac_text_re = re.compile(r"(AC-\d+)[:\s]+(.+)")

    for line in lines:
        m = _ac_table_re.search(line)
        if m:
            ac_id = m.group(1).strip()
            criteria = m.group(2).strip()
            results.append(f"{ac_id}: {criteria}")
            continue
        m = _ac_text_re.search(line)
        if m:
            ac_id = m.group(1).strip()
            criteria = m.group(2).strip()
            results.append(f"{ac_id}: {criteria}")

    return results


# ---------------------------------------------------------------------------
# Coverage matrix builder
# ---------------------------------------------------------------------------


def _keywords(text: str) -> set[str]:
    """Extract lowercase keywords (3+ chars, alphanumeric+hyphen) from text."""
    tokens = re.findall(r"[a-zA-Z가-힣\-_]{2,}", text)
    result: set[str] = set()
    for t in tokens:
        low = t.lower().replace("_", "-")
        if len(low) >= 2:
            result.add(low)
    return result


def _overlaps(need_text: str, candidate: str) -> bool:
    """True if any keyword from need_text appears in candidate (case-insensitive)."""
    need_kw = _keywords(need_text)
    cand_lower = candidate.lower()
    for kw in need_kw:
        if kw in cand_lower:
            return True
    return False


def build_coverage_matrix(
    needs: list[NeedItem],
    entities: list[str],
    acs: list[str],
) -> list[CoverageRow]:
    """Build coverage matrix rows using keyword/slug overlap heuristic.

    Verdict logic:
    - COVERED: entity_evidence non-empty AND ac_evidence non-empty
    - PARTIAL: exactly one of entity_evidence or ac_evidence is non-empty
    - GAP: both empty
    """
    rows: list[CoverageRow] = []

    for need in needs:
        search_text = f"{need.what} {need.who}"

        entity_ev = [e for e in entities if _overlaps(search_text, e)]
        ac_ev = [a for a in acs if _overlaps(f"{need.what} {need.why}", a)]

        if entity_ev and ac_ev:
            verdict = "COVERED"
        elif entity_ev or ac_ev:
            verdict = "PARTIAL"
        else:
            verdict = "GAP"

        rows.append(
            CoverageRow(
                need_id=need.id,
                need_summary=f"{need.what[:60]}",
                entity_evidence=entity_ev,
                ac_evidence=ac_ev,
                verdict=verdict,
            )
        )

    return rows


# ---------------------------------------------------------------------------
# Aggregate verdict
# ---------------------------------------------------------------------------


def aggregate_verdict(rows: list[CoverageRow]) -> str:
    """PASS / PASS-WITH-CAVEAT / BLOCK."""
    has_gap = any(r.verdict == "GAP" for r in rows)
    has_partial = any(r.verdict == "PARTIAL" for r in rows)

    if has_gap:
        return "BLOCK"
    if has_partial:
        return "PASS-WITH-CAVEAT"
    return "PASS"


# ---------------------------------------------------------------------------
# Report renderer (PII-stripped)
# ---------------------------------------------------------------------------


def render_review(
    slug: str,
    rows: list[CoverageRow],
    verdict: str,
    out_path: Path,
) -> None:
    """Write docs/delivery/<slug>/needs-fit-review.md (PII-stripped, deterministic pre-pass).

    The file is safe to commit: no PII (email/phone/contact details).
    """
    today = datetime.date.today().isoformat()

    gap_rows = [r for r in rows if r.verdict == "GAP"]
    partial_rows = [r for r in rows if r.verdict == "PARTIAL"]
    covered_rows = [r for r in rows if r.verdict == "COVERED"]

    lines: list[str] = [
        f"# Needs-Fit Review — {slug}",
        f"",
        f"> Audit date: {today}  ",
        f"> **Aggregate verdict: {verdict}**  ",
        f"> Source: deterministic pre-pass (`needs_fit_audit.py`); codex refinement pending.",
        f"",
        f"## Coverage Matrix",
        f"",
        f"| Need ID | What (summary) | Entity Evidence | AC Evidence | Verdict |",
        f"|---------|----------------|-----------------|-------------|---------|",
    ]

    for row in rows:
        ent_str = ", ".join(row.entity_evidence) if row.entity_evidence else "—"
        ac_str = ", ".join(row.ac_evidence) if row.ac_evidence else "—"
        safe_summary = strip_pii(row.need_summary)
        lines.append(
            f"| {row.need_id} | {safe_summary} | {ent_str} | {ac_str} | {row.verdict} |"
        )

    lines += [
        f"",
        f"## Summary",
        f"",
        f"- COVERED: {len(covered_rows)}",
        f"- PARTIAL: {len(partial_rows)}",
        f"- GAP: {len(gap_rows)}",
        f"- **Total needs: {len(rows)}**",
        f"",
    ]

    if gap_rows:
        lines += [
            f"## GAP Items",
            f"",
            f"> Each GAP requires action before delivery (Step 5 / BLOCK).",
            f"",
        ]
        for row in gap_rows:
            lines.append(f"- **{row.need_id}**: {strip_pii(row.need_summary)}")
            lines.append(
                f"  - Recommended: entity absent → CTO backlog; AC absent → PM adds criteria"
            )
        lines.append("")

    if partial_rows:
        lines += [
            f"## CAVEAT Items",
            f"",
            f"> PARTIALs covered by either entity OR AC — verify completeness.",
            f"",
        ]
        for row in partial_rows:
            missing = "AC" if row.entity_evidence and not row.ac_evidence else "entity"
            lines.append(f"- **{row.need_id}**: {strip_pii(row.need_summary)}")
            lines.append(f"  - Missing: {missing} evidence — consider adding before delivery")
        lines.append("")

    lines += [
        f"---",
        f"",
        f"> Note: This is the **deterministic pre-pass** output (LLM 0, keyword/slug heuristic).",
        f"> Codex refinement pass is required for final verdict — run via `Agent(subagent_type='codex:codex-rescue', ...)`",
        f"> after `build_codex_prompt()` in `needs_fit_audit.py`.",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Codex prompt builder
# ---------------------------------------------------------------------------


def build_codex_prompt(slug: str, paths: dict[str, str]) -> str:
    """Fill needs-fit-prompt-template.md placeholders and return the prompt string.

    paths keys: needs_note_path, manifest_path, profile_path, acceptance_criteria_path
    """
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    replacements = {
        "{slug}": slug,
        "{needs_note_path}": paths.get("needs_note_path", ""),
        "{manifest_path}": paths.get("manifest_path", ""),
        "{profile_path}": paths.get("profile_path", ""),
        "{acceptance_criteria_path}": paths.get("acceptance_criteria_path", ""),
    }
    result = template
    for token, value in replacements.items():
        result = result.replace(token, value)
    return result


# ---------------------------------------------------------------------------
# CLI main
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Needs-Fit Audit Gate — deterministic pre-pass + codex prompt builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Full run (writes review skeleton, prints codex prompt to stdout):\n"
            "  python scripts/workflow/needs_fit_audit.py \\\n"
            "      --slug lawfirm-demo \\\n"
            "      --needs-note apps/intake/data-mirror/lawfirm-demo-needs-note.md \\\n"
            "      --manifest out/lawfirm-demo/screen-manifest.json \\\n"
            "      --profile profiles/lawfirm-demo.yaml \\\n"
            "      --acceptance-criteria docs/delivery/lawfirm-demo/acceptance-criteria.md\n"
            "\n"
            "  # Without AC file (PARTIAL/GAP expected):\n"
            "  python scripts/workflow/needs_fit_audit.py \\\n"
            "      --slug acme \\\n"
            "      --needs-note /path/to/needs-note.md \\\n"
            "      --manifest /path/to/screen-manifest.json \\\n"
            "      --profile /path/to/acme.yaml\n"
        ),
    )
    parser.add_argument("--slug", required=True, help="Customer slug (ASCII, G-8)")
    parser.add_argument(
        "--needs-note", required=True, help="Path to needs-note.md (may contain PII)"
    )
    parser.add_argument(
        "--manifest", required=True, help="Path to screen-manifest.json"
    )
    parser.add_argument("--profile", required=True, help="Path to profile.yaml")
    parser.add_argument(
        "--acceptance-criteria",
        default=None,
        help="Path to acceptance-criteria.md (optional)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help=(
            "Output directory for review (default: docs/delivery/<slug>). "
            "Review written to <out>/needs-fit-review.md"
        ),
    )
    args = parser.parse_args(argv)

    needs_note_path = Path(args.needs_note)
    manifest_path = Path(args.manifest)
    profile_path = Path(args.profile)
    ac_path = Path(args.acceptance_criteria) if args.acceptance_criteria else None
    slug = args.slug

    # Validate required inputs
    if not needs_note_path.exists():
        print(
            f"[needs_fit_audit] ERROR: needs-note not found: {needs_note_path}",
            file=sys.stderr,
        )
        return 1

    # Determine output directory
    if args.out:
        out_dir = Path(args.out)
    else:
        out_dir = REPO_ROOT / "docs" / "delivery" / slug
    review_path = out_dir / "needs-fit-review.md"

    # --- Pre-pass ---
    needs_note_md = needs_note_path.read_text(encoding="utf-8")
    needs = parse_needs(needs_note_md)
    entities = load_manifest_entities(manifest_path)
    acs = parse_acceptance_criteria(ac_path) if ac_path else []
    rows = build_coverage_matrix(needs, entities, acs)
    verdict = aggregate_verdict(rows)
    render_review(slug, rows, verdict, review_path)

    # --- Deterministic envelope (stdout) ---
    gap_rows = [r for r in rows if r.verdict == "GAP"]
    partial_rows = [r for r in rows if r.verdict == "PARTIAL"]
    covered_rows = [r for r in rows if r.verdict == "COVERED"]

    print("=== NEEDS-FIT DETERMINISTIC PRE-PASS ENVELOPE ===")
    print(f"VERDICT:  {verdict}")
    print(f"REPORT:   {review_path}")
    print(f"COVERED:  {len(covered_rows)}")
    print(f"PARTIAL:  {len(partial_rows)}")
    print(f"GAP:      {len(gap_rows)}")
    for row in gap_rows[:5]:
        print(f"BLOCK-ITEM: {row.need_id} — {row.need_summary}")
    for row in partial_rows[:5]:
        print(f"CAVEAT-ITEM: {row.need_id} — {row.need_summary}")
    print("=================================================")
    print()

    # --- Codex prompt (stdout, for Claude session to use) ---
    paths_dict = {
        "needs_note_path": str(needs_note_path),
        "manifest_path": str(manifest_path),
        "profile_path": str(profile_path),
        "acceptance_criteria_path": str(ac_path) if ac_path else "(not provided)",
    }

    if TEMPLATE_PATH.exists():
        print("=== CODEX PROMPT (paste to Agent(subagent_type='codex:codex-rescue')) ===")
        print(build_codex_prompt(slug, paths_dict))
        print("==========================================================================")
    else:
        print(
            f"[needs_fit_audit] WARN: prompt template not found at {TEMPLATE_PATH}",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
