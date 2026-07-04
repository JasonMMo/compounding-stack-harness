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
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent

# Windows 기본 콘솔(cp949)에서 가드 마크(✓/✗) 출력이 UnicodeEncodeError 로
# 죽지 않도록 stdout/stderr 를 UTF-8 로 강제 (PYTHONIOENCODING 불필요).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


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

# Astro dynamic route naming: [...slug].astro, [page].astro, [...page].astro.
# Brackets are Astro's mandatory file-based routing convention (not non-ASCII).
# Exemption applies only inside frontend/adapters/landing-astro/src/pages/.
_ASTRO_ROUTE_NAME = re.compile(r"^\[[\w.]+\]\.astro$|^\[\.\.\.[\w.]+\]\.astro$")
_ASTRO_PAGES_PATH = "frontend/adapters/landing-astro/src/pages"

# Apple asset-catalog retina-scale naming, e.g. AppIcon-512@2x.png, icon@3x~ipad.png.
# The '@Nx' scale suffix is a REQUIRED Apple convention inside *.xcassets bundles
# (Capacitor iOS adapter generates these). Renaming would break the iOS build, so
# G-8 exempts the '@Nx' token — but ONLY inside an *.xcassets ancestor, so a truly
# bad non-ASCII name elsewhere (or a non-Apple file in the bundle) is still caught.
_APPLE_ASSET_NAME = re.compile(r"^[A-Za-z0-9._\-]+@[123]x(~[a-z]+)?\.[A-Za-z0-9]+$")


def g8_ascii_slug() -> GuardResult:
    """G-8 / CLAUDE.md §10 — all repo paths use ASCII slugs only.

    Detection: walk the repo, flag any file or directory whose name contains
    non-ASCII characters or characters outside [A-Za-z0-9._-].
    Generated/build directories are excluded (same set as G-1/G-6).
    Exemption: Apple '@Nx' retina assets inside *.xcassets bundles (see
    _APPLE_ASSET_NAME) — the '@' is a required Apple naming convention.
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
            # Apple retina-asset exemption: '@Nx' token inside an *.xcassets bundle.
            if _APPLE_ASSET_NAME.match(name) and any(
                part.endswith(".xcassets") for part in rel_parts
            ):
                continue
            # Astro dynamic route exemption: [...slug].astro inside Astro pages dir.
            # Brackets are mandatory Astro file-based routing convention (ASCII chars).
            if _ASTRO_ROUTE_NAME.match(name) and rel_str.startswith(_ASTRO_PAGES_PATH):
                continue
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
      (d) no duplicate entity keys — two entities sharing a key (e.g. a legal `invoice`
          colliding with the finance `invoice`) is silently deduped by safe_load, which
          DROPS one entity and can mis-point FKs. compose() sees pre-dedup nodes. (Growth-128)
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

    # ── (d) no duplicate entity keys (safe_load silently dedups — compose sees all) ──
    # YAML mappings with a repeated key keep only the LAST value after load, so a
    # colliding entity silently overwrites another (and any FK to it mis-points).
    # compose() yields the un-deduped node tree, exposing every key node. (Growth-128)
    try:
        _root_node = _yaml.compose(_CATALOG_PATH.read_text(encoding="utf-8"))
        _ent_node = None
        if _root_node is not None and hasattr(_root_node, "value"):
            for _k, _v in _root_node.value:
                if getattr(_k, "value", None) == "entities":
                    _ent_node = _v
                    break
        if _ent_node is not None and hasattr(_ent_node, "value"):
            _seen: set[str] = set()
            _dups: list[str] = []
            for _k, _v in _ent_node.value:
                _key = getattr(_k, "value", None)
                if _key is None:
                    continue
                if _key in _seen and _key not in _dups:
                    _dups.append(_key)
                _seen.add(_key)
            for _d in _dups:
                violations.append(
                    f"(d) duplicate entity key '{_d}' in catalog.yaml — YAML keeps "
                    f"only the last; one entity is silently dropped. Rename one "
                    f"(use a domain prefix, e.g. 'case-invoice')."
                )
    except Exception as exc:  # pragma: no cover - compose failure is itself a defect
        violations.append(f"(d) duplicate-key scan failed: {exc}")

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


_OUTPUT_PROTOCOL_REF = "subagent-output-protocol"

# ---------------------------------------------------------------------------
# G-14 Intake pipeline health
# ---------------------------------------------------------------------------

_DEFAULT_CASES_DIR_FOR_G14 = REPO_ROOT / "infra" / "registry" / "cases"


def g14_intake_pipeline_health(
    cases_dir: Path | None = None,
) -> GuardResult:
    """G-14 / Phase 8 — intake pipeline health: qualify cases must not be stalled/failed.

    Reads infra/registry/cases/*.yaml (PII-free).
    Flags any triage_status=qualify case that has a NODE_FAIL event OR a
    NODE_ENTER with no matching NODE_EXIT_OK where now - enter > SLA.

    Returns SPEC if cases dir is absent or has no case files yet.
    Returns FAIL on any detected stall or failure in a qualify-tier case.

    The optional `cases_dir` parameter allows tests to inject a temporary
    directory instead of the repo default.
    """
    from datetime import datetime as _datetime, timezone as _tz
    import json as _json

    _cases_dir: Path = cases_dir if cases_dir is not None else _DEFAULT_CASES_DIR_FOR_G14

    if not _cases_dir.exists():
        # Use relative_to only when the path is inside the repo root
        try:
            _dir_label = str(_cases_dir.relative_to(REPO_ROOT))
        except ValueError:
            _dir_label = str(_cases_dir)
        return GuardResult(
            "G-14", "intake pipeline health", "Phase 8",
            status="SPEC",
            notes=f"Cases directory not found ({_dir_label}) — "
                  "guard activates once infra/registry/cases/ has entries.",
        )

    # Collect case YAML files (skip README, .gitkeep, hidden)
    try:
        import yaml as _yaml  # type: ignore[import]
        _has_yaml = True
    except ImportError:
        _has_yaml = False

    def _load_case(path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            text = path.read_text(encoding="utf-8")
            if _has_yaml:
                data = _yaml.safe_load(text)
                return data if isinstance(data, dict) else {}
            # Fallback: return empty (cannot parse without pyyaml)
            return {}
        except Exception:
            return {}

    case_files = [
        p for p in sorted(_cases_dir.iterdir())
        if p.is_file()
        and p.suffix.lower() in {".yaml", ".yml"}
        and not p.name.startswith(".")
        and not p.name.startswith("_")
        and p.name.lower() not in {"readme.yaml", "readme.yml"}
    ]

    if not case_files:
        return GuardResult(
            "G-14", "intake pipeline health", "Phase 8",
            status="SPEC",
            notes="No case files in infra/registry/cases/ yet — "
                  "guard activates once a case is registered.",
        )

    # SLA table (seconds) — matches pipeline_monitor.NODES
    _SLA: dict[str, int] = {
        "SUBMITTED": 360,
        "TRIAGED": 3600,
        "CALL_QUEUE": 86400,
        "GAP_RECORDED": 3600,
        "PM_TRIAGE": 172800,
        "DRAFT_PROMOTED": 7200,
        "SCAFFOLDED": 7200,
        "DEPLOYED": 36000,
        "UI_CHECKED": 3600,
        "NEEDS_FIT": 7200,
        "PROFILE_CONFIRMED": 172800,
        "DELIVERED": 259200,
        "FEEDBACK": 604800,
        "CLOSED": 86400,
    }

    _NON_QUALIFY_NODES: frozenset[str] = frozenset({"CALL_QUEUE", "GAP_RECORDED", "PM_TRIAGE"})

    def _parse_ts(ts_str: str | None) -> "_datetime | None":
        if not ts_str:
            return None
        try:
            clean = ts_str.replace("Z", "+00:00")
            return _datetime.fromisoformat(clean)
        except (ValueError, AttributeError):
            return None

    now = _datetime.now(_tz.utc)
    violations: list[str] = []
    qualify_count = 0

    for cf in case_files:
        case = _load_case(cf)
        if not case:
            continue

        triage_status = case.get("triage_status")
        if triage_status != "qualify":
            continue

        qualify_count += 1
        slug = case.get("slug") or cf.stem
        events: list[dict] = case.get("pipeline_events", []) or []

        # Per-node: collect enter/exit/fail events
        by_node: dict[str, dict] = {}
        for ev in events:
            nid = ev.get("node_id")
            if not nid or nid in _NON_QUALIFY_NODES:
                continue
            if nid not in by_node:
                by_node[nid] = {"enters": [], "exits": [], "fails": []}
            evt = ev.get("event", "")
            if evt == "NODE_ENTER":
                by_node[nid]["enters"].append(ev)
            elif evt == "NODE_EXIT_OK":
                by_node[nid]["exits"].append(ev)
            elif evt == "NODE_FAIL":
                by_node[nid]["fails"].append(ev)

        for nid, evs in by_node.items():
            # Latest-terminal-wins (matches pipeline_monitor.project_node_states):
            # a NODE_EXIT_OK emitted after a NODE_FAIL supersedes it. This lets a
            # codex Step 4b re-judgment clear a conservative deterministic
            # NEEDS_FIT BLOCK (and lets a successful retry clear a transient fail)
            # without the guard latching on the first failure. Full history is
            # retained in the case YAML for audit.
            terminals = sorted(
                evs["exits"] + evs["fails"], key=lambda e: e.get("ts") or ""
            )
            latest_terminal = terminals[-1] if terminals else None
            if latest_terminal is not None:
                if latest_terminal.get("event") == "NODE_FAIL":
                    ec = latest_terminal.get("error_class", "unknown")
                    violations.append(
                        f"{slug}:{nid} NODE_FAIL (error_class={ec!r})"
                    )
                # NODE_EXIT_OK latest → node resolved, no violation
            elif evs["enters"]:
                # Entered, never reached a terminal event — check for SLA breach
                enter_ts = _parse_ts(evs["enters"][0].get("ts"))
                if enter_ts:
                    sla = _SLA.get(nid, 0)
                    dwell = (now - enter_ts).total_seconds()
                    if dwell > sla:
                        violations.append(
                            f"{slug}:{nid} stalled {dwell:.0f}s (SLA {sla}s)"
                        )

    notes = (
        f"Scanned {len(case_files)} case file(s); {qualify_count} qualify-tier case(s). "
        "Non-qualify triage statuses (call/gap/defer/closed) excluded from stall accounting."
    )

    if qualify_count == 0:
        return GuardResult(
            "G-14", "intake pipeline health", "Phase 8",
            status="SPEC",
            notes=notes + " No qualify cases yet.",
        )

    return GuardResult(
        "G-14", "intake pipeline health", "Phase 8",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=notes,
    )


def g87_embed_caller_split() -> GuardResult:
    """G-87 / Growth-93 — legal-rag embed caller split: asymmetric e5 prefix invariant.

    The legal-rag embed sidecar uses Microsoft e5 asymmetric prefixes:
      - Single embed  (.embed)       → "query: "   prefix  — search queries only.
      - Batch embed   (.embed_batch) → "passage: " prefix  — ingest passages only.

    Callers MUST stay one-directional:
      - api.py  (/search path)  : ONLY calls .embed()      — NEVER .embed_batch()
      - ingest.py               : ONLY calls .embed_batch() — NEVER a bare .embed()

    Failure mode is SILENT: wrong prefix produces no error, only degraded retrieval,
    and the damage is irreversible after ingest. QA mandated this machine guard
    (Growth-93) so the constraint is machine-enforced, not just convention.

    Scope: services/legal-rag/ source files only (NOT tests).
    Returns SKIP if services/legal-rag/ does not exist (safe in repos without this vertical).

    Rules implemented:
      (a) FAIL if api.py contains a .embed_batch( call (search path must never batch).
      (b) FAIL if ingest.py contains a bare .embed( call that is NOT .embed_batch(
          (ingest must never single-embed). Regex carefully avoids matching
          .embed_batch( as a hit for .embed( and ignores imports/class definitions.
    """
    legal_rag_dir = REPO_ROOT / "services" / "legal-rag"
    if not legal_rag_dir.exists():
        return GuardResult(
            "G-87", "embed caller split (e5 asymmetric prefix)", "Growth-93",
            status="SKIP",
            notes="services/legal-rag/ not found — guard activates once legal-rag vertical lands.",
        )

    violations: list[str] = []

    # ── (a) api.py must NOT call .embed_batch( ────────────────────────────────
    api_path = legal_rag_dir / "api.py"
    if api_path.exists():
        api_lines = api_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        # Pattern: .embed_batch( as a method call on any object.
        # Must not appear in api.py (search path).
        _batch_call_re = re.compile(r"\.\s*embed_batch\s*\(")
        for lineno, line in enumerate(api_lines, start=1):
            stripped = line.strip()
            # Skip comment lines
            if stripped.startswith("#"):
                continue
            if _batch_call_re.search(line):
                rel = api_path.relative_to(REPO_ROOT)
                violations.append(
                    f"{rel}:{lineno} — .embed_batch( call found in search path "
                    f"(api.py must only use .embed() with 'query:' prefix, never batch)."
                )
    else:
        violations.append("services/legal-rag/api.py not found (expected source file).")

    # ── (b) ingest.py must NOT call bare .embed( (only .embed_batch( allowed) ─
    ingest_path = legal_rag_dir / "ingest.py"
    if ingest_path.exists():
        ingest_lines = ingest_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        # Neutralize .embed_batch( first, then any remaining .embed( is a bare
        # single-embed violation. Robust against whitespace variants.
        _batch_embed_re = re.compile(r"\.\s*embed_batch\s*\(")

        for lineno, line in enumerate(ingest_lines, start=1):
            stripped = line.strip()
            # Skip comment lines
            if stripped.startswith("#"):
                continue
            # Skip import statements and class/function definitions
            if stripped.startswith(("import ", "from ", "class ", "def ")):
                continue
            # Check for a method call form: <object>.embed(  but not .embed_batch(
            # Strategy: look for .embed( that is NOT part of .embed_batch(
            # Replace all .embed_batch( occurrences to neutralize them, then
            # check for remaining .embed( patterns.
            neutralized = _batch_embed_re.sub(".EMBED_BATCH_SAFE(", line)
            # Now look for .embed( in the neutralized line (method call form only)
            if re.search(r"\.\s*embed\s*\(", neutralized):
                rel = ingest_path.relative_to(REPO_ROOT)
                violations.append(
                    f"{rel}:{lineno} — bare .embed( call found in ingest path "
                    f"(ingest.py must only use .embed_batch() with 'passage:' prefix, never single-embed)."
                )
    else:
        violations.append("services/legal-rag/ingest.py not found (expected source file).")

    return GuardResult(
        "G-87", "embed caller split (e5 asymmetric prefix)", "Growth-93",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=(
            "Invariant: api.py (search) → .embed() only; ingest.py → .embed_batch() only. "
            "Wrong prefix = silent retrieval degradation + irreversible ingest corruption. "
            "Scope: services/legal-rag/api.py + ingest.py source only (tests excluded)."
        ),
    )


def g15_marketing_site_visual_gate(
    cases_dir: Path | None = None,
    ui_checks_dir: Path | None = None,
) -> GuardResult:
    """G-15 / Growth-65 — marketing-site deliverable must pass vision-QA before DELIVERED.

    Reads infra/registry/cases/*.yaml.  For each case whose deliverable_kind is
    'marketing-site', checks that a vision-QA verdict file exists at
    docs/intake-inbox/ui-checks/<slug>-vision-verdict.json AND contains
    verdict=="PASS".

    Returns SPEC when:
      - infra/registry/cases/ does not exist, OR
      - no case files are present, OR
      - no case with deliverable_kind==marketing-site exists.

    Returns FAIL when a marketing-site case has triage_status=="delivered" (or
    "DELIVERED") but no verdict file or a non-PASS verdict.

    Note: the agency-demo profile is a fixture/fixture, not a case file —
    it is excluded by this guard's scope (cases only, not profiles/).

    The optional `cases_dir` / `ui_checks_dir` parameters allow tests to inject
    temporary directories instead of the repo defaults (same pattern as G-14).
    """
    _cases_dir: Path = cases_dir if cases_dir is not None else REPO_ROOT / "infra" / "registry" / "cases"
    _ui_checks_dir: Path = ui_checks_dir if ui_checks_dir is not None else REPO_ROOT / "docs" / "intake-inbox" / "ui-checks"

    if not _cases_dir.exists():
        return GuardResult(
            "G-15", "marketing-site visual gate", "Growth-65",
            status="SPEC",
            notes=(
                "infra/registry/cases/ not found — "
                "guard activates once a marketing-site case is registered."
            ),
        )

    try:
        import yaml as _yaml  # type: ignore[import]
        _has_yaml = True
    except ImportError:
        _has_yaml = False

    def _load_case(path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            text = path.read_text(encoding="utf-8")
            if _has_yaml:
                data = _yaml.safe_load(text)
                return data if isinstance(data, dict) else {}
            return {}
        except Exception:
            return {}

    case_files = [
        p for p in sorted(_cases_dir.iterdir())
        if p.is_file()
        and p.suffix.lower() in {".yaml", ".yml"}
        and not p.name.startswith(".")
        and not p.name.startswith("_")
        and p.name.lower() not in {"readme.yaml", "readme.yml"}
    ]

    if not case_files:
        return GuardResult(
            "G-15", "marketing-site visual gate", "Growth-65",
            status="SPEC",
            notes=(
                "No case files in infra/registry/cases/ yet — "
                "guard activates once a marketing-site case is registered."
            ),
        )

    marketing_cases: list[dict] = []
    for cf in case_files:
        case = _load_case(cf)
        if not case:
            continue
        kind = case.get("deliverable_kind") or (
            case.get("stack", {}).get("deliverable_kind") if isinstance(case.get("stack"), dict) else None
        )
        if kind == "marketing-site":
            marketing_cases.append({"slug": case.get("slug") or cf.stem, "case": case})

    if not marketing_cases:
        return GuardResult(
            "G-15", "marketing-site visual gate", "Growth-65",
            status="SPEC",
            notes=(
                f"Scanned {len(case_files)} case file(s); no marketing-site deliverable found — "
                "guard activates once a marketing-site case is registered."
            ),
        )

    violations: list[str] = []
    for entry in marketing_cases:
        slug = entry["slug"]
        case = entry["case"]
        triage_status = (case.get("triage_status") or "").lower()

        # Only check cases that are in the DELIVERED pipeline state.
        if triage_status != "delivered":
            continue

        # Check for a vision-verdict file.
        verdict_path = _ui_checks_dir / f"{slug}-vision-verdict.json"
        if not verdict_path.exists():
            try:
                _verdict_label = str(verdict_path.relative_to(REPO_ROOT))
            except ValueError:
                _verdict_label = str(verdict_path)
            violations.append(
                f"{slug}: triage_status=delivered but no vision-verdict file "
                f"({_verdict_label}) — "
                "run ui_check --full-vision and complete CDO/QA scoring."
            )
            continue

        try:
            import json as _json
            verdict_data = _json.loads(verdict_path.read_text(encoding="utf-8"))
        except Exception as exc:
            violations.append(f"{slug}: vision-verdict file unreadable: {exc}")
            continue

        verdict = verdict_data.get("verdict", "")
        if verdict.upper() != "PASS":
            violations.append(
                f"{slug}: vision-verdict is {verdict!r} (need PASS) — "
                "complete CDO/QA rubric scoring before delivery."
            )

    marketing_count = len(marketing_cases)
    notes = (
        f"Scanned {len(case_files)} case file(s); "
        f"{marketing_count} marketing-site case(s). "
        "Vision-verdict PASS required before triage_status=delivered."
    )

    return GuardResult(
        "G-15", "marketing-site visual gate", "Growth-65",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=notes,
    )


def g13_subagent_output_protocol_wired() -> GuardResult:
    """G-13 / Growth-34 — every persona loop SKILL wires the subagent output protocol.

    Hardens the Growth-33 output protocol; implemented in the Growth-34 dogfood.

    Detection: each .claude/skills/<role>-loop/SKILL.md must link to
    subagent-output-protocol.md (the file-then-envelope return discipline).
    Heading wording varies across loops ('## 출력 규약' vs '**반환 규약**'), so the
    check is on the protocol link, not the heading. This keeps the return
    boundary from silently dropping out of a loop when it is edited — the
    protocol's drift failure mode. Envelope size itself is a runtime property
    and cannot be checked statically; this guard protects the mechanism that
    makes the 8-persona agents comply by default.
    """
    skills_dir = REPO_ROOT / ".claude" / "skills"
    if not skills_dir.exists():
        return GuardResult(
            "G-13", "subagent output protocol wired", "Growth-34",
            status="SKIP", notes="No .claude/skills directory.",
        )
    violations: list[str] = []
    checked = 0
    for skill in sorted(skills_dir.glob("*-loop/SKILL.md")):
        checked += 1
        rel = skill.relative_to(REPO_ROOT).as_posix()
        if _OUTPUT_PROTOCOL_REF not in skill.read_text(encoding="utf-8"):
            violations.append(f"{rel}: no link to subagent-output-protocol.md")
    return GuardResult(
        "G-13", "subagent output protocol wired", "Growth-34",
        status="FAIL" if violations else ("PASS" if checked else "SKIP"),
        violations=violations,
        notes=f"Scanned {checked} *-loop SKILL(s).",
    )


# ---------------------------------------------------------------------------
# G-16 ~ G-20 — Design-Cloud Bridge guards (Growth-130, WP-2)
#   claude.ai/design 클라우드 워크벤치 경계의 안전망. claude-design 비의존.
#   설계: docs/architecture/design-cloud-bridge-execution-plan.md §3 (CI 가드 5종),
#         docs/architecture/design-cloud-bridge.md §5.
# ---------------------------------------------------------------------------

# 클라우드(claude.ai/design)로 절대 올라가면 안 되는 PII/시크릿의 흔적 (G-16).
_PII_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "email"),
    (re.compile(r"\b\d{6}-\d{7}\b"), "RRN(주민등록번호)"),
    (re.compile(r"\b01[016-9]-?\d{3,4}-?\d{4}\b"), "휴대폰번호"),
    (re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"), "Anthropic API key"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "Google API key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
]
# 주: RRN 의 하이픈 없는 13자리 형식(\d{13})은 epoch-ms 타임스탬프와 충돌 → 거짓양성
#     위험으로 의도적 제외. 하이픈 형식만 고신호로 탐지 (QA WP-2 게이트 합의, 후속 재검토).
# 시크릿/의뢰인 PII 보관 경로 — 업로드 컴포넌트가 이걸 참조하면 스코프 위반 (G-16).
_FORBIDDEN_PATH_REFS = (
    "apps/intake/data", "infra/secrets", "infra/cloudflared/config.yml",
)
# 인도물(복제본·landing 산출물)에 남으면 안 되는 클라우드 결합 흔적 (G-17).
_CLOUD_COUPLING_TOKENS = (
    "claude.ai/design", "claude.ai", "DesignSync", "/design-sync",
)
# 정규화 게이트를 우회한 raw synced 컴포넌트의 provenance 마커 (G-20).
#   normalize.py / staging 컨벤션이 synced 원본에 이 토큰을 남긴다. production
#   경로(frontend/presets)에서 발견되면 = 정규화 미경유 직붙임 = axis-8 붕괴.
_STAGING_PROVENANCE_MARKER = "design-sync:staging"

_BRIDGE_STAGING_DIR = REPO_ROOT / "staging" / "design-sync"
_BRIDGE_REPLICA_ROOT = REPO_ROOT / "out" / "replicas"
_BRIDGE_DELIVERY_ROOTS = (
    REPO_ROOT / "frontend" / "adapters" / "landing-astro" / "src",
    REPO_ROOT / "presets" / "themes",
    REPO_ROOT / "presets" / "site-sections",
)
_BRIDGE_PRODUCTION_ROOTS = (
    REPO_ROOT / "frontend" / "adapters",
    REPO_ROOT / "presets" / "themes",
    REPO_ROOT / "presets" / "site-sections",
)
_CODE_SUFFIXES = {".html", ".htm", ".css", ".js", ".mjs", ".ts", ".astro", ".json", ".svg"}
_TEXTY_SUFFIXES = _CODE_SUFFIXES | {".yaml", ".yml", ".md", ".txt"}


def _iter_files(root: Path, suffixes: set[str]):
    """root 아래 주어진 확장자의 파일을 정렬 순회 (root 부재 시 빈 순회)."""
    if not root.exists():
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in suffixes:
            yield p


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def g16_design_upload_scope(staging_dir: Path | None = None) -> GuardResult:
    """G-16 / Growth-130 — claude.ai/design 업로드 스코프: 무명 컴포넌트만.

    staging/design-sync/ (cloud 업로드 후보 영역)의 텍스트에서 PII/시크릿/금지경로
    참조를 탐지한다. Claude Design 은 BAA 적용 제외 + 기본 학습 허용이므로 의뢰인
    PII·기밀은 절대 업로드 금지 — 무명(無名) 디자인 컴포넌트만 경계를 넘는다.

    SPEC: staging/design-sync/ 부재 또는 (README 외) 내용물 없음.
    FAIL: 이메일/주민번호/전화/시크릿키/금지경로참조 발견.

    테스트는 staging_dir 주입으로 임시 디렉터리 검사 (G-14/G-15 패턴).
    """
    sdir = staging_dir if staging_dir is not None else _BRIDGE_STAGING_DIR
    if not sdir.exists():
        return GuardResult(
            "G-16", "design upload scope", "Growth-130",
            status="SPEC",
            notes="staging/design-sync/ not found — guard activates once components are synced.",
        )
    files = [
        p for p in _iter_files(sdir, _TEXTY_SUFFIXES)
        if p.name.lower() != "readme.md"
    ]
    if not files:
        return GuardResult(
            "G-16", "design upload scope", "Growth-130",
            status="SPEC",
            notes="No synced components in staging/design-sync/ (README only) — nothing to scope.",
        )
    violations: list[str] = []
    for p in files:
        text = p.read_text(encoding="utf-8", errors="replace")
        for pat, label in _PII_PATTERNS:
            if pat.search(text):
                violations.append(f"{_rel(p)}: contains {label} — PII must not reach claude.ai/design.")
        for ref in _FORBIDDEN_PATH_REFS:
            if ref in text:
                violations.append(f"{_rel(p)}: references secret/PII path '{ref}' — strip before upload.")
    return GuardResult(
        "G-16", "design upload scope", "Growth-130",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Scanned {len(files)} staged file(s) for PII/secret leakage.",
    )


def g17_cloud_coupling_leak(scan_roots: tuple[Path, ...] | None = None) -> GuardResult:
    """G-17 / Growth-130 — 인도물에 클라우드 결합 흔적 0.

    고객에게 인도되는 산출물(복제본 번들, landing-astro 소스, 테마)에 claude.ai/design
    클라우드 도구 참조가 남으면 vendor lock-in + 의도치 않은 외부 의존. 정적 검사로
    'claude.ai', 'DesignSync', '/design-sync' 토큰을 0 으로 강제한다.

    PASS: delivery 루트에 결합 토큰 없음 (clean repo 기본값).
    FAIL: 발견 시 (어느 파일·토큰인지 보고).

    스캔 대상 .md/.yaml 제외 — 문서/주석의 정당한 언급과 인도물을 구분.
    """
    roots = scan_roots if scan_roots is not None else (
        _BRIDGE_REPLICA_ROOT, *_BRIDGE_DELIVERY_ROOTS,
    )
    present = [r for r in roots if r.exists()]
    if not present:
        return GuardResult(
            "G-17", "cloud-coupling leak", "Growth-130",
            status="SPEC",
            notes="No delivery artifact roots present yet — guard activates once they land.",
        )
    violations: list[str] = []
    scanned = 0
    for root in present:
        for p in _iter_files(root, _CODE_SUFFIXES):
            scanned += 1
            text_lc = p.read_text(encoding="utf-8", errors="replace").lower()
            for tok in _CLOUD_COUPLING_TOKENS:
                if tok.lower() in text_lc:  # 대소문자 변형(CLAUDE.AI 등)도 차단
                    violations.append(f"{_rel(p)}: cloud-coupling token '{tok}' must be stripped from delivered artifact.")
    return GuardResult(
        "G-17", "cloud-coupling leak", "Growth-130",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Scanned {scanned} delivery file(s) across {len(present)} root(s) for cloud coupling.",
    )


def g18_cross_tenant_leak(
    replica_root: Path | None = None,
    profiles_dir: Path | None = None,
    cases_dir: Path | None = None,
) -> GuardResult:
    """G-18 / Growth-130 — 고객 복제본 번들에 타 테넌트 식별자 0.

    out/replicas/<slug>/ 의 각 고객 번들은 자기 slug 외 다른 고객의 slug/식별자를
    포함하면 안 된다 (데이터 격리). 알려진 slug 집합은 profiles/*.yaml +
    infra/registry/cases/*.yaml stem 에서 수집.

    SPEC: out/replicas/ 부재 (복제본 빌드 WP-3 전) 또는 번들 없음.
    FAIL: 번들 <slug> 안에서 다른 고객 slug 가 토큰 단위로 발견.
    """
    rroot = replica_root if replica_root is not None else _BRIDGE_REPLICA_ROOT
    pdir = profiles_dir if profiles_dir is not None else REPO_ROOT / "profiles"
    cdir = cases_dir if cases_dir is not None else REPO_ROOT / "infra" / "registry" / "cases"
    if not rroot.exists():
        return GuardResult(
            "G-18", "cross-tenant leak", "Growth-130",
            status="SPEC",
            notes="out/replicas/ not found — guard activates once replica builds land (WP-3).",
        )
    bundles = [d for d in sorted(rroot.iterdir()) if d.is_dir() and not d.name.startswith(("_", "."))]
    if not bundles:
        return GuardResult(
            "G-18", "cross-tenant leak", "Growth-130",
            status="SPEC", notes="No replica bundles in out/replicas/ yet.",
        )
    known: set[str] = set()
    for d in (pdir, cdir):
        for p in _iter_files(d, {".yaml", ".yml"}):
            stem = p.stem
            if not stem.startswith("_") and stem.lower() != "readme":
                known.add(stem)
    known |= {b.name for b in bundles}
    # 토큰 경계 매칭: slug 가 단어 경계로 나타날 때만 (부분문자열 오탐 방지).
    violations: list[str] = []
    for bundle in bundles:
        own = bundle.name
        foreign = sorted(s for s in known if s != own and len(s) >= 3)
        if not foreign:
            continue
        pats = {s: re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(s)}(?![A-Za-z0-9_-])") for s in foreign}
        for p in _iter_files(bundle, _TEXTY_SUFFIXES):
            text = p.read_text(encoding="utf-8", errors="replace")
            for s, pat in pats.items():
                if pat.search(text):
                    violations.append(f"{_rel(p)}: replica '{own}' leaks foreign tenant slug '{s}'.")
    return GuardResult(
        "G-18", "cross-tenant leak", "Growth-130",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Checked {len(bundles)} replica bundle(s) against {len(known)} known slug(s).",
    )


def g19_dtcg_schema(staging_dir: Path | None = None) -> GuardResult:
    """G-19 / Growth-130 — 경계를 넘는 토큰 override 가 DTCG semantic 화이트리스트 준수.

    cloud→repo 단일 교환 포맷은 DTCG 토큰 JSON. staging/design-sync/**/*.tokens.json
    의 각 override 가 design/tokens/semantic.json 키 화이트리스트(+landing extras)
    안인지 scripts/design/dtcg_schema.py 로 검증한다.

    SPEC: semantic.json 부재(검증 불가) 또는 token override 파일 없음.
    FAIL: 화이트리스트 밖 키 발견.

    주의: DTCG 는 W3C Community Group draft(v2025.10)로 완전한 Recommendation 아님.
    """
    sdir = staging_dir if staging_dir is not None else _BRIDGE_STAGING_DIR
    design_dir = REPO_ROOT / "scripts" / "design"
    if str(design_dir) not in sys.path:
        sys.path.insert(0, str(design_dir))
    try:
        import dtcg_schema  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - import guard
        return GuardResult(
            "G-19", "DTCG token schema", "Growth-130",
            status="SPEC", notes=f"scripts/design/dtcg_schema.py not importable: {exc}",
        )
    if not dtcg_schema.load_semantic_keys():
        return GuardResult(
            "G-19", "DTCG token schema", "Growth-130",
            status="SPEC",
            notes="design/tokens/semantic.json not found — cannot validate token boundary yet.",
        )
    if not sdir.exists():
        return GuardResult(
            "G-19", "DTCG token schema", "Growth-130",
            status="SPEC", notes="staging/design-sync/ not found — no token overrides to validate.",
        )
    token_files = [p for p in _iter_files(sdir, {".json"}) if p.name.endswith(".tokens.json")]
    if not token_files:
        return GuardResult(
            "G-19", "DTCG token schema", "Growth-130",
            status="SPEC", notes="No *.tokens.json overrides staged yet.",
        )
    violations: list[str] = []
    for p in token_files:
        try:
            overrides = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            violations.append(f"{_rel(p)}: invalid JSON ({exc}).")
            continue
        if not isinstance(overrides, dict):
            violations.append(f"{_rel(p)}: token override must be a JSON object.")
            continue
        for bad in dtcg_schema.validate_token_overrides(overrides):
            violations.append(f"{_rel(p)}: key '{bad}' outside semantic whitelist.")
    return GuardResult(
        "G-19", "DTCG token schema", "Growth-130",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Validated {len(token_files)} token-override file(s) against semantic whitelist.",
    )


def g20_normalization_gate(production_roots: tuple[Path, ...] | None = None) -> GuardResult:
    """G-20 / Growth-130 — synced 컴포넌트 raw HTML 의 production 직붙임 차단.

    정규화 게이트(normalize.py)는 비협상이다. cloud 에서 내려온 컴포넌트는 토큰
    override + variant 로 분해되어야 production(frontend/adapters, presets/themes,
    presets/site-sections)에 들어간다. 이 가드는 production 경로에서 staging
    provenance 마커('design-sync:staging')를 탐지 — 발견 = 정규화 미경유 직붙임.

    PASS: production 경로에 마커 없음 (clean repo 기본값).
    FAIL: 마커 발견 (어느 파일인지 보고).
    """
    roots = production_roots if production_roots is not None else _BRIDGE_PRODUCTION_ROOTS
    present = [r for r in roots if r.exists()]
    if not present:
        return GuardResult(
            "G-20", "normalization gate", "Growth-130",
            status="SPEC", notes="No production frontend/preset roots present.",
        )
    violations: list[str] = []
    scanned = 0
    for root in present:
        for p in _iter_files(root, _TEXTY_SUFFIXES):
            scanned += 1
            if _STAGING_PROVENANCE_MARKER in p.read_text(encoding="utf-8", errors="replace"):
                violations.append(
                    f"{_rel(p)}: carries staging marker '{_STAGING_PROVENANCE_MARKER}' — "
                    "raw synced component bypassed the normalization gate."
                )
    return GuardResult(
        "G-20", "normalization gate", "Growth-130",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Scanned {scanned} production file(s) for normalization-gate bypass.",
    )


# G-21 — Shell 컴포넌트 conformance (구조적 도메인-프리, v2 WP-C)
#   격리 sibling 레포(harness-design-system)의 셸 템플릿이 도메인 텍스트를 담지
#   못하게 강제한다. 가시 텍스트노드 / aria-label·placeholder·title·alt 는 단일
#   {{마커}} 이거나 _structural-allowlist.txt(UI chrome 닫힌 집합)여야 한다.
#   denylist(FORBIDDEN_PATTERNS)와의 결정적 차이: allowlist = fail-safe(누락 시 BLOCK),
#   미래 도메인 용어 누락으로 인한 누출(Growth-130 사고 클래스) 원천 불가능.
#   설계: docs/architecture/design-cloud-bridge-v2-structural.md, sibling components/CONTRACT.md.
# ---------------------------------------------------------------------------

_SIBLING_ROOT = REPO_ROOT.parent / "harness-design-system"
_SIBLING_COMPONENTS = _SIBLING_ROOT / "components"
_SHELL_ALLOWLIST_FILE = _SIBLING_COMPONENTS / "_structural-allowlist.txt"

# conformance 스캔 시 서브트리째 무시할 태그(콘텐츠 아님) / 클래스(데모 scaffolding).
_SHELL_SKIP_TAGS = {"head", "title", "script", "style", "svg"}
_SHELL_SKIP_CLASSES = {"demo-heading", "demo-desc"}
_SHELL_VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img",
                    "input", "link", "meta", "param", "source", "track", "wbr"}
_SHELL_CHECK_ATTRS = ("aria-label", "placeholder", "title", "alt")
_SHELL_MARKER_RE = re.compile(r"\{\{\s*[\w.]+\s*\}\}")
_SHELL_MARKER_ONLY_RE = re.compile(r"^(?:\{\{\s*[\w.]+\s*\}\}\s*)+$")
_HANGUL_RE = re.compile(r"[가-힣]")
_LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")


def _shell_text_ok(raw: str, allow: set[str]) -> bool:
    """텍스트노드/속성값이 conformance 통과면 True.

    통과: (a) 마커만으로 구성, (b) 마커 제거 후 Hangul/3+자 라틴단어 없음(순수 chrome 기호),
          (c) 원문(trim)이 allowlist 에 정확히 존재.
    """
    s = raw.strip()
    if not s:
        return True
    if _SHELL_MARKER_ONLY_RE.match(s):
        return True
    residue = _SHELL_MARKER_RE.sub(" ", s)
    if not _HANGUL_RE.search(residue) and not _LATIN_WORD_RE.search(residue):
        return True
    return s in allow


class _ShellConformanceParser(HTMLParser):
    """셸 템플릿에서 conformance 위반 텍스트/속성을 수집 (stdlib만 사용)."""

    def __init__(self, allow: set[str]) -> None:
        super().__init__(convert_charrefs=True)
        self._allow = allow
        self._skip_stack: list[bool] = []
        self.violations: list[str] = []

    def _class_skip(self, attrs: list[tuple[str, str | None]]) -> bool:
        for k, v in attrs:
            if k == "class" and v:
                if set(v.split()) & _SHELL_SKIP_CLASSES:
                    return True
        return False

    def _parent_skip(self) -> bool:
        return self._skip_stack[-1] if self._skip_stack else False

    def _check_attrs(self, attrs: list[tuple[str, str | None]]) -> None:
        for k, v in attrs:
            if k in _SHELL_CHECK_ATTRS and v and not _shell_text_ok(v, self._allow):
                self.violations.append(f"@{k}=\"{v.strip()}\"")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        skip = self._parent_skip() or tag in _SHELL_SKIP_TAGS or self._class_skip(attrs)
        if not skip:
            self._check_attrs(attrs)
        if tag not in _SHELL_VOID_TAGS:
            self._skip_stack.append(skip)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if not (self._parent_skip() or tag in _SHELL_SKIP_TAGS or self._class_skip(attrs)):
            self._check_attrs(attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag not in _SHELL_VOID_TAGS and self._skip_stack:
            self._skip_stack.pop()

    def handle_data(self, data: str) -> None:
        if self._parent_skip():
            return
        if not _shell_text_ok(data, self._allow):
            self.violations.append(f"text \"{data.strip()}\"")


def _load_shell_allowlist() -> set[str]:
    allow: set[str] = set()
    if _SHELL_ALLOWLIST_FILE.exists():
        for line in _SHELL_ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                allow.add(line)
    return allow


def g21_shell_conformance(components_dir: Path | None = None) -> GuardResult:
    """G-21 / Growth-130 — Shell 템플릿 구조적 도메인-프리 conformance.

    SPEC: sibling components/ 부재 (sibling 레포 미체크아웃) 또는 index.html 없음.
    FAIL: 마커도 allowlist도 아닌 Hangul/단어 텍스트노드·속성 발견 (= 도메인 텍스트 잔존).
    PASS: 모든 셸이 {{마커}} + chrome 만 포함.
    """
    cdir = components_dir if components_dir is not None else _SIBLING_COMPONENTS
    if not cdir.exists():
        return GuardResult(
            "G-21", "shell conformance", "Growth-130",
            status="SPEC",
            notes=f"sibling components/ not found ({_rel(cdir)}) — guard activates once design-system repo is checked out alongside.",
        )
    # 스캔 대상 = 컴포넌트 셸 템플릿 + cloud-노출(committed) 갤러리 HTML.
    #   reference/showcase.html 류도 cloud(GitHub 연결)에 노출되므로 같은 conformance 적용.
    #   단 reference/rendered/ (gitignored 렌더 산출물 = corpus 충전본)는 제외.
    targets = sorted(cdir.glob("*/index.html"))
    ref_dir = cdir.parent / "reference"
    if ref_dir.is_dir():
        targets += sorted(
            p for p in ref_dir.glob("*.html")
            if "rendered" not in p.relative_to(ref_dir).parts
        )
    if not targets:
        return GuardResult(
            "G-21", "shell conformance", "Growth-130",
            status="SPEC", notes="No shell/reference HTML templates found.",
        )
    allow = _load_shell_allowlist()
    sib_root = cdir.parent
    violations: list[str] = []
    for tgt in targets:
        parser = _ShellConformanceParser(allow)
        parser.feed(tgt.read_text(encoding="utf-8", errors="replace"))
        try:
            label = str(tgt.relative_to(sib_root)).replace("\\", "/")
        except ValueError:
            label = tgt.name
        for v in parser.violations:
            violations.append(
                f"{label}: {v} — not a {{{{slot}}}} marker nor in _structural-allowlist.txt (domain text must move to fixtures/manifest)."
            )
    return GuardResult(
        "G-21", "shell conformance", "Growth-130",
        status="FAIL" if violations else "PASS",
        violations=violations,
        notes=f"Scanned {len(targets)} shell/gallery template(s) against {len(allow)} chrome allowlist entr(ies).",
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
    "G-13": g13_subagent_output_protocol_wired,
    "G-14": g14_intake_pipeline_health,
    "G-15": g15_marketing_site_visual_gate,
    "G-16": g16_design_upload_scope,
    "G-17": g17_cloud_coupling_leak,
    "G-18": g18_cross_tenant_leak,
    "G-19": g19_dtcg_schema,
    "G-20": g20_normalization_gate,
    "G-21": g21_shell_conformance,
    "G-87": g87_embed_caller_split,
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
