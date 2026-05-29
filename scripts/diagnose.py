#!/usr/bin/env python3
"""diagnose.py — compounding-stack-harness guard runner.

G-1 ~ G-7 : 7 inherited meta-lessons (docs/inherited-wisdom/README.md).
G-8       : ASCII-slug convention (CLAUDE.md §10).

Each guard returns a GuardResult(status, violations, notes).
status in {PASS, FAIL, SKIP, SPEC}:
  PASS  — guard ran and found no violations.
  FAIL  — guard ran and found violations.
  SKIP  — guard's target (axis directory, asset) does not yet exist at this milestone.
  SPEC  — guard is specified but detection is deferred until the relevant axis lands.

CLI:
  python scripts/diagnose.py                # run all guards
  python scripts/diagnose.py G-1,G-4,G-8    # run a subset
  python scripts/diagnose.py --list         # list all guards
  python scripts/diagnose.py --json         # machine-readable output

Exit code: 0 if no FAIL, 1 otherwise. SKIP/SPEC do not fail the run.
"""
from __future__ import annotations

import argparse
import dataclasses
import io
import json
import re
import sys
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class GuardResult:
    guard_id: str
    title: str
    lesson_ref: str
    status: str  # PASS | FAIL | SKIP | SPEC
    violations: list[str] = dataclasses.field(default_factory=list)
    notes: str = ""


GuardFn = Callable[[], GuardResult]


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def g1_wire_protocol_single_source() -> GuardResult:
    """G-1 / Lesson 1 — wire-protocol single source of truth.

    Detection: enumerate top-level keys declared in middle/contract/, then grep
    frontend/adapters and backend/adapters for files that *redeclare* those
    keys (not merely reference them). At M0 the contract directory is empty.
    """
    contract_dir = REPO_ROOT / "middle" / "contract"
    if not contract_dir.exists() or not any(contract_dir.iterdir()):
        return GuardResult(
            "G-1",
            "wire-protocol single source",
            "Lesson 1",
            status="SPEC",
            notes="middle/contract/ not yet populated — detection activates in M1.",
        )

    # M1+: extract keys from yaml/json contracts, grep adapter trees.
    return GuardResult(
        "G-1", "wire-protocol single source", "Lesson 1",
        status="SPEC",
        notes="Implementation pending: yaml-key extractor + adapter grep.",
    )


def g2_context_path_consistency() -> GuardResult:
    """G-2 / Lesson 2 — context-path string lives in one place.

    Detection: read context paths declared in customer profile + middle
    contract; grep entire repo for the same literal in files that are *not*
    the declaring file.
    """
    profiles_dir = REPO_ROOT / "profiles"
    if not (profiles_dir.exists() and list(profiles_dir.glob("*.yaml"))):
        return GuardResult(
            "G-2", "context-path consistency", "Lesson 2",
            status="SPEC",
            notes="No customer profile yet — detection activates once a profile lands.",
        )
    return GuardResult(
        "G-2", "context-path consistency", "Lesson 2",
        status="SPEC",
        notes="Implementation pending: profile path extractor + repo grep.",
    )


def g3_single_source_delegation() -> GuardResult:
    """G-3 / Lesson 3 — new entry points delegate, never reimplement.

    Detection heuristic: every file under `entrypoints/` (or any future
    web/IDE/API surface) must either `import` the CLI module or invoke it via
    subprocess. Pure inline codegen is the violation pattern.
    """
    entrypoints = REPO_ROOT / "entrypoints"
    if not entrypoints.exists():
        return GuardResult(
            "G-3", "single-source delegation", "Lesson 3",
            status="SPEC",
            notes="No alternative entry points exist — CLI is single surface today.",
        )
    return GuardResult(
        "G-3", "single-source delegation", "Lesson 3",
        status="SPEC",
        notes="Implementation pending: entrypoint AST scan for delegation pattern.",
    )


_ENV_VAR_RE = re.compile(r"\$\{[A-Z_][A-Z0-9_]*\}")


def g4_envvar_round_trip() -> GuardResult:
    """G-4 / Lesson 4 — ${ENV_VAR} placeholders survive profile round-trip.

    Detection: for each profiles/*.yaml, read the raw text, collect every
    ${VAR} match. If a round-trip helper exists, dump and re-read; assert no
    placeholder is lost or quoted. At M0 there are no profile files yet, so
    the guard records what it *would* enforce.
    """
    profiles_dir = REPO_ROOT / "profiles"
    profile_files = sorted(profiles_dir.glob("*.yaml")) if profiles_dir.exists() else []
    if not profile_files:
        return GuardResult(
            "G-4", "${ENV_VAR} round-trip", "Lesson 4",
            status="SKIP",
            notes="No profile YAMLs yet. Schema in profiles/_README.md mandates round-trip preservation.",
        )

    violations: list[str] = []
    for path in profile_files:
        text = path.read_text(encoding="utf-8")
        placeholders = _ENV_VAR_RE.findall(text)
        if not placeholders:
            continue
        # Round-trip check requires the helper module. Until it lands, flag
        # any direct PyYAML import as a risk and pass otherwise.
        if "yaml.safe_load" in text or "yaml.load" in text:
            violations.append(
                f"{path.relative_to(REPO_ROOT)} contains placeholders and references "
                f"pyyaml directly — must route through round-trip helper."
            )

    return GuardResult(
        "G-4", "${ENV_VAR} round-trip", "Lesson 4",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Scanned {len(profile_files)} profile file(s).",
    )


_ASSET_THRESHOLD = 2  # manifest required once an axis carries 2+ assets.


def g5_asset_exposure_harness() -> GuardResult:
    """G-5 / Lesson 5 — every axis exposes its assets through a manifest.

    Detection: each axis is described by (directory, glob, manifest-locations).
    Once the axis carries _ASSET_THRESHOLD or more matching assets, at least
    one manifest path must exist. A /status page must enumerate counts per
    axis once the portal exists (M1+).
    """
    axes: list[tuple[str, Path, str]] = [
        ("skill",        REPO_ROOT / "presets" / "skills",     "*.seed.md"),
        ("ddl",          REPO_ROOT / "presets" / "ddl",        "*.yaml"),
        ("middle",       REPO_ROOT / "middle" / "contract",    "*"),
        ("frontend",     REPO_ROOT / "frontend" / "adapters",  "*"),
        ("backend",      REPO_ROOT / "backend" / "adapters",   "*"),
        ("customer",     REPO_ROOT / "profiles",               "*.yaml"),
        ("expert-agent", REPO_ROOT / ".claude" / "agents",     "domain-expert-*.md"),
    ]
    violations: list[str] = []
    checked = 0
    for axis, axis_dir, glob in axes:
        if not axis_dir.exists():
            continue
        assets = [p for p in axis_dir.glob(glob) if not p.name.startswith(".")]
        if len(assets) < _ASSET_THRESHOLD:
            continue
        checked += 1
        manifest_candidates = [
            axis_dir / "INDEX.md",
            axis_dir / "_README.md",
            axis_dir / "README.md",
        ]
        if not any(p.exists() for p in manifest_candidates):
            violations.append(
                f"axis '{axis}' has {len(assets)} assets in "
                f"{axis_dir.relative_to(REPO_ROOT)} but no manifest "
                f"(INDEX.md / _README.md / README.md)."
            )

    return GuardResult(
        "G-5", "asset-exposure manifest", "Lesson 5",
        status="FAIL" if violations else ("PASS" if checked else "SKIP"),
        violations=violations,
        notes=f"Checked {checked} axes at/above threshold ({_ASSET_THRESHOLD}). "
              f"/status page lands in M1.",
    )


_SAAS_HINTS = (
    "tenant_id",
    "tenant-id",
    "TenantId",
    "multi_tenant",
    "MultiTenant",
)


def g6_self_host_single_mode() -> GuardResult:
    """G-6 / Lesson 6 — SaaS / multi-tenant patterns forbidden until M5 gate.

    Detection: grep middle/, backend/, frontend/, scripts/ for SaaS hints.
    The gate file `.m5-saas-gate-open` (placed only after AND-conditions in
    revenue-roadmap §M5) suppresses the guard.
    """
    if (REPO_ROOT / ".m5-saas-gate-open").exists():
        return GuardResult(
            "G-6", "self-host single mode", "Lesson 6",
            status="SKIP",
            notes="M5 SaaS gate file present — multi-tenant code permitted.",
        )

    search_roots = [
        REPO_ROOT / "middle",
        REPO_ROOT / "backend",
        REPO_ROOT / "frontend",
        REPO_ROOT / "scripts",
    ]
    # Exclude this file: it declares the hints as its own detection vocabulary.
    self_path = Path(__file__).resolve()
    violations: list[str] = []
    scanned = 0
    for root in search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".ts", ".tsx", ".js", ".java", ".kt", ".go", ".yaml", ".yml"}:
                continue
            if path.resolve() == self_path:
                continue
            scanned += 1
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for hint in _SAAS_HINTS:
                if hint in text:
                    violations.append(
                        f"{path.relative_to(REPO_ROOT)} contains SaaS hint '{hint}'."
                    )
                    break

    return GuardResult(
        "G-6", "self-host single mode", "Lesson 6",
        status="FAIL" if violations else ("PASS" if scanned else "SKIP"),
        violations=violations,
        notes=f"Scanned {scanned} source files for SaaS hints.",
    )


_PERSONA_PAT = re.compile(r"\b(CEO|업무담당자|IT-?담당자)\b")
_TIME_PAT = re.compile(r"\b\d+\s*(분|시간|일|주|min|hour|hr|day|week)s?\b", re.IGNORECASE)


def g7_persona_driven_gating() -> GuardResult:
    """G-7 / Lesson 7 — every milestone acceptance criterion names a persona.

    Detection: parse docs/business/revenue-roadmap.md; each milestone block
    (heading ## M\\d) must mention at least one of the 3 personas AND a
    duration unit somewhere inside the block.
    """
    roadmap = REPO_ROOT / "docs" / "business" / "revenue-roadmap.md"
    if not roadmap.exists():
        return GuardResult(
            "G-7", "persona-driven gating", "Lesson 7",
            status="SKIP",
            notes="revenue-roadmap.md not found.",
        )
    text = roadmap.read_text(encoding="utf-8")
    blocks = re.split(r"(?=^#{2,4}\s+M\d+)", text, flags=re.MULTILINE)
    milestone_blocks = [b for b in blocks if re.match(r"^#{2,4}\s+M\d+", b)]
    violations: list[str] = []
    for block in milestone_blocks:
        head_match = re.match(r"^#{2,4}\s+(M\d+)[^\n]*", block)
        head = head_match.group(1) if head_match else "M?"
        has_persona = bool(_PERSONA_PAT.search(block))
        has_time = bool(_TIME_PAT.search(block))
        if not (has_persona and has_time):
            missing = []
            if not has_persona:
                missing.append("persona")
            if not has_time:
                missing.append("time")
            violations.append(
                f"milestone {head} missing: {', '.join(missing)}."
            )
    return GuardResult(
        "G-7", "persona-driven gating", "Lesson 7",
        status="FAIL" if violations else ("PASS" if milestone_blocks else "SKIP"),
        violations=violations,
        notes=f"Inspected {len(milestone_blocks)} milestone block(s).",
    )


_ASCII_SAFE = re.compile(r"^[A-Za-z0-9._\-/]+$")
_PATH_IGNORE_PARTS = {".git", "node_modules", "out", "target", "__pycache__", ".venv", "venv"}
_PATH_IGNORE_PREFIX = ("docs/scaffolds",)


def g8_ascii_slug() -> GuardResult:
    """G-8 / CLAUDE.md §10 — all repo paths use ASCII slugs only.

    Detection: walk the repo, flag any file or directory whose name contains
    non-ASCII characters or characters outside [A-Za-z0-9._-].
    """
    violations: list[str] = []
    checked = 0
    for path in REPO_ROOT.rglob("*"):
        rel_parts = path.relative_to(REPO_ROOT).parts
        if any(part in _PATH_IGNORE_PARTS for part in rel_parts):
            continue
        rel_str = "/".join(rel_parts)
        if any(rel_str.startswith(prefix) for prefix in _PATH_IGNORE_PREFIX):
            continue
        checked += 1
        name = path.name
        if not _ASCII_SAFE.match(name):
            violations.append(f"non-ASCII or unsafe path component: {rel_str}")
    return GuardResult(
        "G-8", "ASCII-slug paths", "CLAUDE.md §10",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Scanned {checked} repo entries.",
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

GUARDS: dict[str, GuardFn] = {
    "G-1": g1_wire_protocol_single_source,
    "G-2": g2_context_path_consistency,
    "G-3": g3_single_source_delegation,
    "G-4": g4_envvar_round_trip,
    "G-5": g5_asset_exposure_harness,
    "G-6": g6_self_host_single_mode,
    "G-7": g7_persona_driven_gating,
    "G-8": g8_ascii_slug,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def render_text(results: list[GuardResult]) -> str:
    buf = io.StringIO()
    width = max(len(r.title) for r in results) + 2
    buf.write(f"{'ID':5} {'STATUS':6} {'TITLE'.ljust(width)} LESSON\n")
    buf.write("-" * (5 + 1 + 6 + 1 + width + 1 + 12) + "\n")
    for r in results:
        buf.write(f"{r.guard_id:5} {r.status:6} {r.title.ljust(width)} {r.lesson_ref}\n")
        if r.notes:
            buf.write(f"      └ note: {r.notes}\n")
        for v in r.violations:
            buf.write(f"      ✗ {v}\n")
    return buf.getvalue()


def render_json(results: list[GuardResult]) -> str:
    return json.dumps([dataclasses.asdict(r) for r in results], indent=2, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="compounding-stack-harness guard runner")
    parser.add_argument("guards", nargs="?", default="",
                        help="comma-separated guard ids (e.g. G-1,G-7). default: all.")
    parser.add_argument("--list", action="store_true", help="list guards and exit.")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text.")
    args = parser.parse_args(argv)

    if args.list:
        for gid, fn in GUARDS.items():
            doc = (fn.__doc__ or "").strip().splitlines()[0]
            print(f"{gid}  {doc}")
        return 0

    selected = list(GUARDS.keys())
    if args.guards:
        selected = [g.strip() for g in args.guards.split(",") if g.strip()]
        unknown = [g for g in selected if g not in GUARDS]
        if unknown:
            print(f"unknown guard ids: {', '.join(unknown)}", file=sys.stderr)
            return 2

    results = [GUARDS[gid]() for gid in selected]
    output = render_json(results) if args.json else render_text(results)
    print(output)

    return 1 if any(r.status == "FAIL" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
