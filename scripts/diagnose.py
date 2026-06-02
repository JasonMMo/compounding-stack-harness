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

    Detection: load codes.yaml code→http_status pairs (single source).
    Scan backend/adapters and frontend/adapters source files.
    FLAG when a single line contains BOTH a code key string AND its
    http_status integer — that is the "code→status re-declaration" drift
    pattern (e.g. `NOT_FOUND(404)` or `if code == "NOT_FOUND": status = 404`).

    ALLOW: lines that carry a code string alone (reference/forwarding pattern)
    or an HTTP status alone. The springboot-jakarta adapter calls
    WireResponse.error(loader, "NOT_FOUND") — code string with no hardcoded
    status — so it passes cleanly.

    Adapter directories with zero contract references emit a WARN note
    (potential silent re-declaration), but do NOT raise a FAIL by themselves
    to avoid false-positives on adapters that are pure pass-through shims.
    """
    # ── 1. load contract (single source) ──────────────────────────────────────
    codes_yaml = REPO_ROOT / "middle" / "contract" / "error" / "codes.yaml"
    if not codes_yaml.exists():
        return GuardResult(
            "G-1", "wire-protocol single source", "Lesson 1",
            status="SPEC",
            notes="middle/contract/error/codes.yaml not found — detection activates once contract lands.",
        )

    # Minimal inline YAML parse — only need the flat `codes:` map.
    # We deliberately avoid importing pyyaml at module level so diagnose.py
    # has zero mandatory dependencies beyond stdlib.
    try:
        import yaml as _yaml  # type: ignore[import]
        _raw = _yaml.safe_load(codes_yaml.read_text(encoding="utf-8"))
        _codes_map: dict = _raw.get("codes", {}) if isinstance(_raw, dict) else {}
    except Exception:
        # pyyaml unavailable — fall back to a simple regex parse good enough
        # for the flat codes.yaml structure.
        _codes_map = {}
        _code_key_re = re.compile(r"^([A-Z][A-Z0-9_]+):\s*$", re.MULTILINE)
        _http_re = re.compile(r"^\s+http_status:\s*(\d+)", re.MULTILINE)
        _text = codes_yaml.read_text(encoding="utf-8")
        for _m in _code_key_re.finditer(_text):
            _key = _m.group(1)
            _after = _text[_m.end():]
            _hm = _http_re.search(_after.split("\n\n")[0])
            if _hm:
                _codes_map[_key] = int(_hm.group(1))

    if not _codes_map:
        return GuardResult(
            "G-1", "wire-protocol single source", "Lesson 1",
            status="SPEC",
            notes="codes.yaml parsed but 'codes' map is empty — cannot detect violations.",
        )

    # Build lookup: code_string -> http_status int
    # Only include entries that actually have an http_status (non-HTTP adapters
    # that omit it should not produce false-positives).
    code_to_status: dict[str, int] = {}
    for code_key, entry in _codes_map.items():
        if isinstance(entry, dict) and "http_status" in entry:
            code_to_status[code_key] = int(entry["http_status"])

    if not code_to_status:
        return GuardResult(
            "G-1", "wire-protocol single source", "Lesson 1",
            status="SPEC",
            notes="No code→http_status pairs found in codes.yaml.",
        )

    # ── 2. locate adapter directories ─────────────────────────────────────────
    adapter_roots = [
        REPO_ROOT / "backend"  / "adapters",
        REPO_ROOT / "frontend" / "adapters",
    ]
    existing_adapter_roots = [r for r in adapter_roots if r.exists()]

    if not existing_adapter_roots:
        return GuardResult(
            "G-1", "wire-protocol single source", "Lesson 1",
            status="SPEC",
            notes="No adapter directories found yet (backend/adapters, frontend/adapters).",
        )

    # Build per-adapter directory list (one level down from adapter root)
    adapter_dirs: list[Path] = []
    for root in existing_adapter_roots:
        for child in root.iterdir():
            if child.is_dir():
                adapter_dirs.append(child)

    # Excluded directories inside adapter trees (build artefacts) — shared constant.
    _SKIP_DIR_PARTS = _GENERATED_DIR_PARTS

    # Source file extensions to scan
    _SOURCE_EXTS = {".java", ".kt", ".py", ".ts", ".tsx", ".js", ".go", ".cs"}

    # Files to exclude from scanning (this guard file itself, and codes.yaml)
    _self_path = Path(__file__).resolve()
    _codes_path = codes_yaml.resolve()

    # ── 3. scan ───────────────────────────────────────────────────────────────
    violations: list[str] = []
    scanned_files = 0
    adapter_ref_counts: dict[str, int] = {}  # adapter_name -> contract reference count

    # Strings that indicate the adapter IS loading the contract at runtime.
    _contract_ref_tokens = ("ContractLoader", "wire-v1", "codes.yaml", "contract/error")

    for adapter_dir in adapter_dirs:
        adapter_name = adapter_dir.name
        ref_count = 0

        for src_file in adapter_dir.rglob("*"):
            if not src_file.is_file():
                continue
            # Skip build artefact directories
            if any(part in _SKIP_DIR_PARTS for part in src_file.relative_to(adapter_dir).parts):
                continue
            if src_file.suffix not in _SOURCE_EXTS:
                continue
            if src_file.resolve() in (_self_path, _codes_path):
                continue

            scanned_files += 1
            try:
                lines = src_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue

            # Count contract references (positive-evidence tracking)
            file_text_joined = " ".join(lines)
            if any(tok in file_text_joined for tok in _contract_ref_tokens):
                ref_count += 1

            # Per-line FLAG check: code key AND its http_status on same line.
            # We want to catch re-declaration patterns like:
            #   NOT_FOUND(404)          ← enum constant with hardcoded status
            #   "NOT_FOUND" -> 404      ← Map/switch mapping
            #   if code == "NOT_FOUND": return 404   ← branch mapping
            #
            # We must NOT flag:
            #   comments / doc strings
            #   @DisplayName / @Test annotation strings (human-readable description)
            #   assertion/expectation lines (.value(404), andExpect, assertEquals)
            #   description fields, message text, or log strings
            #   import / package lines

            # Tokens that identify a line as test-assertion / doc / comment context:
            _SAFE_TOKENS = (
                "@DisplayName", "andExpect", ".value(", "assertEquals",
                "assertThat", "contains(", "description", "message",
                "\"returns ", "\"with ", "// ", "# ", " * ", "/*",
                "import ", "package ", "@Test", "log.", "logger.",
                "println", "print(", ".info(", ".warn(", ".error(",
                "notes=", "note:", "README", "description:",
            )

            for lineno, line in enumerate(lines, start=1):
                stripped = line.strip()

                # Skip blank lines
                if not stripped:
                    continue

                # Skip comment-only lines
                if (stripped.startswith("//")
                        or stripped.startswith("#")
                        or stripped.startswith("*")
                        or stripped.startswith("/*")):
                    continue

                # Skip lines that are clearly in a safe (non-mapping) context
                if any(tok in line for tok in _SAFE_TOKENS):
                    continue

                for code_key, http_status in code_to_status.items():
                    status_str = str(http_status)
                    if code_key in line and status_str in line:
                        rel = src_file.relative_to(REPO_ROOT)
                        violations.append(
                            f"{rel}:{lineno} — '{code_key}' + '{status_str}' "
                            f"on same line (code→status re-declaration drift)"
                        )

        adapter_ref_counts[adapter_name] = ref_count

    # ── 4. no-reference WARN note (not a FAIL) ────────────────────────────────
    no_ref_adapters = [name for name, count in adapter_ref_counts.items() if count == 0]
    note_parts = [
        f"Scanned {len(adapter_dirs)} adapter(s), {scanned_files} source file(s). "
        f"Contract: {len(code_to_status)} code→status pairs from codes.yaml."
    ]
    if no_ref_adapters:
        note_parts.append(
            f"WARN: adapter(s) with zero contract references "
            f"(potential silent re-declaration): {', '.join(no_ref_adapters)}."
        )

    return GuardResult(
        "G-1", "wire-protocol single source", "Lesson 1",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=" ".join(note_parts),
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
        ("skill",        REPO_ROOT / "presets" / "skills",     "**/*.seed.md"),
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


# Directories that are generated/gitignored artefacts — excluded from ALL source
# scans (G-1 already used this set; G-6 and G-8 now share it for consistency).
# Guards scan SOURCE, not build output.
_GENERATED_DIR_PARTS = frozenset({
    "build", ".gradle", "node_modules", "__pycache__", "target",
    ".venv", "venv", "out", "dist", ".pytest_cache",
    ".git", ".codegraph", ".context",
})

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
            # Skip generated/build artefact directories (same set as G-1).
            if any(part in _GENERATED_DIR_PARTS for part in path.relative_to(root).parts):
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
# Alternation order matters: longer Korean tokens first so e.g. "1주일" matches
# "주일" rather than greedy-matching "주" and leaving "일" without a boundary.
_TIME_PAT = re.compile(
    r"\b\d+\s*(주일|시간|개월|분|일|주|년|min|hour|hr|day|week)s?\b",
    re.IGNORECASE,
)


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
    # Real milestone headings are "M{n} — <title>" (number immediately followed
    # by an em-dash). This deliberately excludes prose sections like
    # "## M1 Maturity Threshold — …", which are gating *definitions*, not
    # persona-acceptance triples and so are not subject to the persona+time rule.
    milestone_blocks = [b for b in blocks if re.match(r"^#{2,4}\s+M\d+\s+—", b)]
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
# _PATH_IGNORE_PARTS uses the shared _GENERATED_DIR_PARTS set (defined above G-6)
# so G-8 skips the same build/artefact directories as G-1 and G-6.
_PATH_IGNORE_PREFIX = ("docs/scaffolds",)


def g8_ascii_slug() -> GuardResult:
    """G-8 / CLAUDE.md §10 — all repo paths use ASCII slugs only.

    Detection: walk the repo, flag any file or directory whose name contains
    non-ASCII characters or characters outside [A-Za-z0-9._-].
    Generated/build directories are excluded (same set as G-1/G-6).
    """
    violations: list[str] = []
    checked = 0
    for path in REPO_ROOT.rglob("*"):
        rel_parts = path.relative_to(REPO_ROOT).parts
        if any(part in _GENERATED_DIR_PARTS for part in rel_parts):
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


_LEARNLOG = REPO_ROOT / "learn-log.md"
_SLIM_DIVIDER = "**Growth-4 부터 1줄 + pointer 포맷**"
_SLIM_ENTRY_MAX_BODY_LINES = 10
_SLIM_SECTION_MAX_LINES = 200


def g9_main_log_slim() -> GuardResult:
    """G-9 / learn-log.md §6 slim format — post-divider Growth entries are thin.

    Per Growth-4 charter: main §6 keeps 1-line rollup + pointer per Growth entry;
    detail lives in `docs/learn-logs/<role>.md`. This guard enforces:
      (a) every `### Growth-N` heading after the slim divider has at most
          {max_body} non-blank body lines (heading line itself excluded).
      (b) the slim section as a whole stays under {max_section} non-blank lines.

    Drift here means main context bloats again — defeats Growth-4's reason.
    """
    if not _LEARNLOG.exists():
        return GuardResult(
            "G-9", "main learn-log §6 slim", "Growth-4 charter",
            status="SKIP",
            notes="learn-log.md not found.",
        )
    text = _LEARNLOG.read_text(encoding="utf-8")
    lines = text.splitlines()
    divider_idx: int | None = None
    for i, line in enumerate(lines):
        if _SLIM_DIVIDER in line:
            divider_idx = i
            break
    if divider_idx is None:
        return GuardResult(
            "G-9", "main learn-log §6 slim", "Growth-4 charter",
            status="SKIP",
            notes=f"Slim divider marker not found yet: {_SLIM_DIVIDER!r}.",
        )

    post = lines[divider_idx + 1:]
    violations: list[str] = []

    # Mark lines inside fenced code blocks so they are excluded from both
    # entry detection and non-blank counts (spec templates live in fences).
    in_fence = False
    fence_mask: list[bool] = []
    for ln in post:
        if ln.lstrip().startswith("```"):
            fence_mask.append(True)  # the fence line itself is excluded
            in_fence = not in_fence
            continue
        fence_mask.append(in_fence)

    def is_active(i: int) -> bool:
        return not fence_mask[i]

    # (b) aggregate cap (ignore fenced lines)
    non_blank_total = sum(1 for i, ln in enumerate(post) if is_active(i) and ln.strip())
    if non_blank_total > _SLIM_SECTION_MAX_LINES:
        violations.append(
            f"slim §6 has {non_blank_total} non-blank lines (cap {_SLIM_SECTION_MAX_LINES})"
        )

    # (a) per-entry cap — walk Growth headings outside code fences
    entry_starts: list[tuple[int, str]] = []
    for i, ln in enumerate(post):
        if not is_active(i):
            continue
        stripped = ln.lstrip()
        if stripped.startswith("### Growth-"):
            title = stripped[4:].strip()
            entry_starts.append((i, title))

    for idx, (start, title) in enumerate(entry_starts):
        end = entry_starts[idx + 1][0] if idx + 1 < len(entry_starts) else len(post)
        body_non_blank = sum(
            1 for j in range(start + 1, end) if is_active(j) and post[j].strip()
        )
        if body_non_blank > _SLIM_ENTRY_MAX_BODY_LINES:
            violations.append(
                f"{title}: {body_non_blank} non-blank body lines (cap {_SLIM_ENTRY_MAX_BODY_LINES})"
            )

    notes = (
        f"Scanned {len(entry_starts)} slim entries, {non_blank_total} non-blank §6 lines."
    )
    return GuardResult(
        "G-9", "main learn-log §6 slim", "Growth-4 charter",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# G-10 DDL catalog integrity
# ---------------------------------------------------------------------------

_CATALOG_PATH = REPO_ROOT / "presets" / "ddl" / "catalog.yaml"
_SEEDS_DIR = REPO_ROOT / "presets" / "skills" / "generic"

# Closed set of neutral types from _catalog-format.md §2.
_NEUTRAL_TYPES = frozenset([
    "uuid", "string", "text", "integer", "decimal",
    "boolean", "date", "timestamp", "enum",
])


def _parse_seed_entities(seed_path: Path) -> list[str]:
    """Extract entity slugs from a seed file's YAML frontmatter `entities:` list."""
    text = seed_path.read_text(encoding="utf-8")
    # Frontmatter is between the first and second '---' lines.
    lines = text.splitlines()
    in_front = False
    front_lines: list[str] = []
    found_open = False
    for line in lines:
        if line.strip() == "---":
            if not found_open:
                found_open = True
                in_front = True
                continue
            else:
                break  # closing ---
        if in_front:
            front_lines.append(line)

    # Find `entities:` block — collect indented list items.
    entities: list[str] = []
    in_entities = False
    for line in front_lines:
        stripped = line.strip()
        if stripped == "entities:":
            in_entities = True
            continue
        if in_entities:
            if stripped.startswith("-"):
                entities.append(stripped.lstrip("- ").strip())
            elif stripped and not stripped.startswith("-"):
                break  # next key
    return entities


def g10_ddl_catalog_integrity() -> GuardResult:
    """G-10 / Growth-10 — DDL catalog integrity: seed coverage, FK validity, type closure.

    Three checks (per _catalog-format.md §7):
      (a) seed entities subset of catalog — every entity declared in a *.seed.md
          frontmatter must have a matching key in catalog.yaml.
      (b) no dangling FKs — every fk.entity reference in catalog.yaml must point
          to a real catalog entity key.
      (c) type closure — every column `type` in catalog.yaml must be in the 8-type
          neutral vocabulary (uuid/string/text/integer/decimal/boolean/date/timestamp/enum).
    """
    if not _CATALOG_PATH.exists():
        return GuardResult(
            "G-10", "DDL catalog integrity", "Growth-10",
            status="SPEC",
            notes="presets/ddl/catalog.yaml not found — guard activates once ddl axis lands.",
        )

    # Load catalog with PyYAML (already a dependency used by G-1).
    try:
        import yaml as _yaml  # type: ignore[import]
        _raw = _yaml.safe_load(_CATALOG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        return GuardResult(
            "G-10", "DDL catalog integrity", "Growth-10",
            status="FAIL",
            violations=[f"catalog.yaml failed to parse: {exc}"],
        )

    if not isinstance(_raw, dict) or "entities" not in _raw:
        return GuardResult(
            "G-10", "DDL catalog integrity", "Growth-10",
            status="FAIL",
            violations=["catalog.yaml missing top-level 'entities' key."],
        )

    catalog_entities: dict = _raw["entities"]
    catalog_keys: set[str] = set(catalog_entities.keys())

    violations: list[str] = []

    # ── (a) seed entities ⊆ catalog entities ─────────────────────────────────
    seed_files = sorted(_SEEDS_DIR.glob("*.seed.md"))
    seed_entity_count = 0
    for seed_path in seed_files:
        try:
            seed_ents = _parse_seed_entities(seed_path)
        except Exception as exc:
            violations.append(f"Failed to parse seed {seed_path.name}: {exc}")
            continue
        for ent in seed_ents:
            seed_entity_count += 1
            if ent not in catalog_keys:
                violations.append(
                    f"(a) seed '{seed_path.stem}' declares entity '{ent}' "
                    f"but it is missing from catalog.yaml."
                )

    # ── (b) no dangling FK references ────────────────────────────────────────
    for entity_key, ent_def in catalog_entities.items():
        if not isinstance(ent_def, dict):
            continue
        columns = ent_def.get("columns") or {}
        for col_key, col_def in columns.items():
            if not isinstance(col_def, dict):
                continue
            fk = col_def.get("fk")
            if not fk or not isinstance(fk, dict):
                continue
            target = fk.get("entity")
            if target and target not in catalog_keys:
                violations.append(
                    f"(b) {entity_key}.{col_key}: fk.entity '{target}' "
                    f"not found in catalog (dangling FK)."
                )

    # ── (c) type closure (8-type neutral vocabulary) ──────────────────────────
    for entity_key, ent_def in catalog_entities.items():
        if not isinstance(ent_def, dict):
            continue
        columns = ent_def.get("columns") or {}
        for col_key, col_def in columns.items():
            if not isinstance(col_def, dict):
                continue
            col_type = col_def.get("type")
            if col_type and col_type not in _NEUTRAL_TYPES:
                violations.append(
                    f"(c) {entity_key}.{col_key}: type '{col_type}' is not in "
                    f"the 8-type neutral vocabulary."
                )

    notes = (
        f"Catalog: {len(catalog_keys)} entities. "
        f"Seed files: {len(seed_files)}, seed entity refs: {seed_entity_count}."
    )
    return GuardResult(
        "G-10", "DDL catalog integrity", "Growth-10",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# G-11 Creater single-source catalog loader
# ---------------------------------------------------------------------------

_WORKFLOW_DIR = REPO_ROOT / "scripts" / "workflow"

# Pattern: direct yaml.safe_load( ... ) call that opens catalog.yaml inline.
# Matches lines like: yaml.safe_load(open("...catalog.yaml"))
#                     yaml.safe_load(Path("...catalog.yaml").read_text())
_INLINE_CATALOG_LOAD_RE = re.compile(
    r"""yaml\s*\.\s*safe_load\s*\(""",   # yaml.safe_load( anywhere
)

# Pattern: a local function definition named load_catalog.
# Matches: def load_catalog(  (any args)
_LOCAL_LOAD_CATALOG_DEF_RE = re.compile(
    r"""\bdef\s+load_catalog\s*\(""",
)


def g11_creater_catalog_single_source() -> GuardResult:
    """G-11 / Growth-14 — creater scripts must not reimplement catalog loading.

    scripts/workflow/*.py MUST import load_catalog from render.py (single-source,
    presets/ddl/render.py). Violations are:
      (a) a local `def load_catalog(` definition in any workflow script, OR
      (b) a direct `yaml.safe_load(` call that opens catalog.yaml inline.

    PASS when scaffold.py and manifest.py only import the loader from render.py
    (current state as of Growth-14). This guard enshrines the invariant so
    future workflow scripts cannot silently redeclare catalog parsing logic.
    """
    if not _WORKFLOW_DIR.exists():
        return GuardResult(
            "G-11", "creater catalog single-source", "Growth-14",
            status="SKIP",
            notes="scripts/workflow/ not found — guard activates once creater axis lands.",
        )

    py_files = sorted(_WORKFLOW_DIR.glob("*.py"))
    if not py_files:
        return GuardResult(
            "G-11", "creater catalog single-source", "Growth-14",
            status="SKIP",
            notes="No .py files in scripts/workflow/ yet.",
        )

    violations: list[str] = []
    scanned = 0

    for src in py_files:
        try:
            lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        scanned += 1
        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Skip comment lines
            if stripped.startswith("#"):
                continue

            rel = src.relative_to(REPO_ROOT)

            # (a) local load_catalog definition
            if _LOCAL_LOAD_CATALOG_DEF_RE.search(line):
                violations.append(
                    f"{rel}:{lineno} — local `def load_catalog(` "
                    f"re-declares catalog loader (must import from render.py)."
                )

            # (b) inline yaml.safe_load — only flag if catalog.yaml also appears
            # on the same line or within 3 lines (the open/read pattern).
            if _INLINE_CATALOG_LOAD_RE.search(line):
                # Check the surrounding context window [lineno-1 .. lineno+2]
                ctx_start = max(0, lineno - 2)
                ctx_end = min(len(lines), lineno + 2)
                ctx_text = "\n".join(lines[ctx_start:ctx_end])
                if "catalog.yaml" in ctx_text:
                    violations.append(
                        f"{rel}:{lineno} — inline `yaml.safe_load(` near 'catalog.yaml' "
                        f"re-declares catalog parsing (must import load_catalog from render.py)."
                    )

    return GuardResult(
        "G-11", "creater catalog single-source", "Growth-14",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=(
            f"Scanned {scanned} script(s) in scripts/workflow/. "
            f"Invariant: import load_catalog from render.py; no local redeclaration."
        ),
    )


# ---------------------------------------------------------------------------
# G-12 Catalog FK hygiene
# ---------------------------------------------------------------------------

# Regex: column name ends with _id (but not just "id" alone).
_ID_COL_NAME_RE = re.compile(r"^\s{6,}([a-z][a-z0-9_]*_id)\s*:")

# Marker token that whitelists an intentional fk-less _id column.
_FK_EXEMPT_TOKEN = "fk-exempt:"


def g12_catalog_fk_hygiene() -> GuardResult:
    """G-12 / Growth-15 — every *_id column (non-PK) has fk: or fk-exempt: marker.

    For each column whose name matches *_id (not the bare 'id' primary key),
    one of the following must hold:
      (a) the column definition contains 'fk:' (a real FK block), OR
      (b) the column line itself OR the immediately preceding line contains
          'fk-exempt:' (intentional / backlog marker).

    FAIL names every entity.column that satisfies neither condition.
    PASS after Part A annotations in Growth-15.
    """
    if not _CATALOG_PATH.exists():
        return GuardResult(
            "G-12", "catalog FK hygiene", "Growth-15",
            status="SPEC",
            notes="presets/ddl/catalog.yaml not found — guard activates once ddl axis lands.",
        )

    try:
        raw_lines = _CATALOG_PATH.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return GuardResult(
            "G-12", "catalog FK hygiene", "Growth-15",
            status="FAIL",
            violations=[f"Could not read catalog.yaml: {exc}"],
        )

    # Walk lines; track current entity key for error messages.
    violations: list[str] = []
    current_entity: str = ""
    _entity_key_re = re.compile(r"^  ([a-z][a-z0-9_-]+):\s*$")
    checked = 0

    for lineno, line in enumerate(raw_lines):
        # Track entity headings (2-space indent, ends with colon, no leading spaces
        # beyond 2, and the name uses slug chars).
        entity_m = _entity_key_re.match(line)
        if entity_m:
            current_entity = entity_m.group(1)
            continue

        # Check for *_id columns (6+ spaces indent to avoid matching entity keys).
        col_m = _ID_COL_NAME_RE.match(line)
        if not col_m:
            continue

        col_name = col_m.group(1)
        checked += 1

        # The catalog uses two FK formats:
        #   (inline)     col_id: { type: uuid, ..., fk: { entity: foo, ... } }
        #   (multi-line) col_id: { type: uuid, ...,
        #                          fk: { entity: foo, ... } }
        # So we must check the column line AND the immediately following line for
        # "fk:" — the continuation line is always more deeply indented and is the
        # only next-line that could contain fk: for this column.
        next_line = raw_lines[lineno + 1] if lineno + 1 < len(raw_lines) else ""

        # (a) Does this column line or its immediate continuation contain fk:?
        if "fk:" in line or "fk:" in next_line:
            continue

        # (b) Does this line or the immediately preceding line contain fk-exempt:?
        prev_line = raw_lines[lineno - 1] if lineno > 0 else ""
        if _FK_EXEMPT_TOKEN in line or _FK_EXEMPT_TOKEN in prev_line:
            continue

        violations.append(
            f"{current_entity}.{col_name}: no fk: block and no fk-exempt: marker"
        )

    return GuardResult(
        "G-12", "catalog FK hygiene", "Growth-15",
        status="FAIL" if violations else ("PASS" if checked else "SKIP"),
        violations=violations,
        notes=f"Scanned {checked} *_id column(s) across all entities.",
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
    "G-9": g9_main_log_slim,
    "G-10": g10_ddl_catalog_integrity,
    "G-11": g11_creater_catalog_single_source,
    "G-12": g12_catalog_fk_hygiene,
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
