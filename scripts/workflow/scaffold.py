"""scaffold.py — creater axis orchestrator (Phase 1).

Ties together: profile load → catalog validate → DDL emit → manifest emit.

Usage:
  python scripts/workflow/scaffold.py --profile shop-demo
  python scripts/workflow/scaffold.py --profile shop-demo --dialect postgres --out out/

Exit codes:
  0 — success
  1 — validation error (missing entity keys) or I/O error
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Repo root: scaffold.py lives at scripts/workflow/scaffold.py
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Profile loader — G-4 safe (read-only, no re-dump)
# ---------------------------------------------------------------------------

def load_profile(slug: str) -> dict[str, Any]:
    """Load a customer profile YAML by slug.

    G-4 contract: loaded read-only via yaml.safe_load (no re-dump).
    ${ENV_VAR} placeholders in the raw file are never touched by this call.
    scaffold.py only reads profile data; it never writes back to the profile file.
    """
    profiles_dir = REPO_ROOT / "profiles"
    path = profiles_dir / f"{slug}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Profile {slug}.yaml is not a YAML mapping.")
    return data


# ---------------------------------------------------------------------------
# Entity key collection from profile domains
# ---------------------------------------------------------------------------

def collect_entity_keys(profile: dict[str, Any]) -> list[str]:
    """Return all entity keys from profile.domains[], preserving order."""
    keys: list[str] = []
    seen: set[str] = set()
    for domain_block in profile.get("domains", []):
        for key in domain_block.get("entities", []):
            if key not in seen:
                keys.append(key)
                seen.add(key)
    return keys


# ---------------------------------------------------------------------------
# Catalog validation
# ---------------------------------------------------------------------------

def validate_entities(
    entity_keys: list[str],
    catalog: dict[str, Any],
    profile: dict[str, Any],
) -> list[str]:
    """Return list of error messages for any entity key missing from catalog.

    Each error names the missing key and which profile domain block it came from.
    """
    all_catalog_entities: dict[str, Any] = catalog.get("entities", {})
    # Build reverse map: entity key → domain slug in profile
    key_to_domain: dict[str, str] = {}
    for domain_block in profile.get("domains", []):
        domain_slug = domain_block.get("slug", "?")
        for key in domain_block.get("entities", []):
            key_to_domain[key] = domain_slug

    errors: list[str] = []
    for key in entity_keys:
        if key not in all_catalog_entities:
            domain_slug = key_to_domain.get(key, "?")
            errors.append(
                f"  entity '{key}' (domain: '{domain_slug}') not found in catalog"
            )
    return errors


# ---------------------------------------------------------------------------
# DDL emission — delegates to render.py CLI (single-source)
# ---------------------------------------------------------------------------

def emit_ddl(
    entity_keys: list[str],
    dialect: str,
    out_dir: Path,
) -> Path:
    """Call render.py once with --entities for the full entity set → out_dir/ddl/<dialect>.sql.

    Passes all entity keys in a single subprocess call so render.py can compute
    the correct cross-entity topological order and deferred FK (ALTER TABLE) placement.
    Returns the path to the written SQL file.
    """
    render_script = REPO_ROOT / "presets" / "ddl" / "render.py"

    ddl_out_dir = out_dir / "ddl"
    ddl_out_dir.mkdir(parents=True, exist_ok=True)
    sql_path = ddl_out_dir / f"{dialect}.sql"

    # Single call — render.py receives all keys at once and applies topological sort
    # across the full subset, ensuring FK targets precede referrers.
    entities_arg = ",".join(entity_keys)
    result = subprocess.run(
        [sys.executable, str(render_script), "--dialect", dialect, "--entities", entities_arg],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"render.py error: {result.stderr.strip()}", file=sys.stderr)
        raise RuntimeError(f"DDL render failed: {result.stderr.strip()}")

    # Replace render.py header with a scaffold-level header that lists the
    # profile-requested entity keys (in profile order, before topo reorder).
    body_lines = [l for l in result.stdout.splitlines() if not l.startswith("-- ")]
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    header = (
        f"-- DDL generated by scaffold.py (via render.py)\n"
        f"-- dialect : {dialect}\n"
        f"-- entities: {', '.join(entity_keys)}\n"
    )
    sql_path.write_text(header + "\n" + "\n".join(body_lines), encoding="utf-8")
    return sql_path


# ---------------------------------------------------------------------------
# Manifest emission — delegates to manifest.py (single-source)
# ---------------------------------------------------------------------------

def emit_manifest(
    profile_slug: str,
    entity_keys: list[str],
    catalog: dict[str, Any],
    out_dir: Path,
    profile: dict[str, Any] | None = None,
) -> Path:
    """Call build_manifest() and write out_dir/screen-manifest.json."""
    workflow_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(workflow_dir))
    from manifest import build_manifest  # type: ignore[import]

    manifest = build_manifest(profile_slug, entity_keys, catalog, profile=profile)

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "screen-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return manifest_path


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_scaffold(
    profile_slug: str,
    dialect: str = "postgres",
    out_root: Path | None = None,
) -> int:
    """Full scaffold pipeline. Returns exit code (0 = success, 1 = error)."""
    if out_root is None:
        out_root = REPO_ROOT / "out"

    out_dir = out_root / profile_slug

    # Step 1: Load profile (G-4 safe)
    try:
        profile = load_profile(profile_slug)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Step 2: Collect entity keys
    entity_keys = collect_entity_keys(profile)
    if not entity_keys:
        print("ERROR: Profile has no entities in domains[].", file=sys.stderr)
        return 1

    # Step 3: Load catalog (single-source via render.py)
    render_dir = REPO_ROOT / "presets" / "ddl"
    sys.path.insert(0, str(render_dir))
    try:
        from render import load_catalog  # type: ignore[import]
    except ImportError as e:
        print(f"Cannot import render.py: {e}", file=sys.stderr)
        return 1

    catalog = load_catalog()

    # Step 4: Validate every entity exists in catalog (build-time FAIL guard)
    errors = validate_entities(entity_keys, catalog, profile)
    if errors:
        print("ERROR: Profile references entity keys not found in catalog:", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        return 1

    # Step 5: Emit DDL
    try:
        sql_path = emit_ddl(entity_keys, dialect, out_dir)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Step 6: Emit manifest (pass profile for customer_display / domains / feedback_url)
    manifest_path = emit_manifest(profile_slug, entity_keys, catalog, out_dir, profile=profile)

    # Step 7: Print summary
    manifest_abs = manifest_path.resolve()
    print(f"scaffold complete — profile: {profile_slug}")
    print(f"  entities scaffolded : {len(entity_keys)} ({', '.join(entity_keys)})")
    print(f"  DDL output          : {sql_path.resolve()}")
    print(f"  manifest output     : {manifest_abs}")
    print(f"")
    print(f"  Phase 2 frontend run command:")
    print(f"    PROFILE_MANIFEST={manifest_abs} python server.py")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold DDL + screen manifest from a customer profile."
    )
    parser.add_argument(
        "--profile", required=True,
        help="Customer profile slug (e.g. shop-demo).",
    )
    parser.add_argument(
        "--dialect", default="postgres",
        help="DDL dialect (postgres | hsqldb | mysql | oracle). Default: postgres.",
    )
    parser.add_argument(
        "--out", default=None,
        help="Output root directory. Default: out/ (repo root).",
    )
    args = parser.parse_args(argv)

    out_root = Path(args.out).resolve() if args.out else None
    return run_scaffold(args.profile, args.dialect, out_root)


if __name__ == "__main__":
    raise SystemExit(main())
