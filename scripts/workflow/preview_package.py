"""
preview_package.py — generates compose files for local or Coolify preview.

Usage:
  python scripts/workflow/preview_package.py --profile lawfirm-demo
  python scripts/workflow/preview_package.py --profile shop-demo --out out/
  python scripts/workflow/preview_package.py --profile new-client --coolify

Modes:
  LOCAL (default): generates out/<slug>/docker-compose.yml
    - Absolute Windows paths for build context and manifest volume.
    - Frontend exposed on host port (default :8090).
    - No Coolify labels.

  COOLIFY (--coolify flag): generates deploy/preview/<slug>.compose.yml
    - Repo-root relative build context (Coolify clones full repo).
    - Manifest bind-mount from /data/coolify/manifests/<slug>/screen-manifest.json.
    - Domain comment only — set via API PATCH docker_compose_domains.
    - SECRET_KEY injected via Coolify env API (not in compose file).

Steps:
  1. Run scaffold.py to produce out/<slug>/ artifacts (DDL + manifest).
     If out/<slug>/screen-manifest.json already exists, scaffold is skipped
     unless --force-scaffold is passed.
  2. Write compose file(s).

Exit codes: 0 success, 1 error.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Repo root: this file is at scripts/workflow/preview_package.py
REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Docker-compose template
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Coolify compose template
# ---------------------------------------------------------------------------

_COOLIFY_COMPOSE_TEMPLATE_NO_SEED = """\
# deploy/preview/{slug}.compose.yml
# Coolify dockercompose preview — profile: {slug}
# Build context: repo root (Coolify clones whole repo, build context = clone root)
#
# Domain: set via Coolify API PATCH docker_compose_domains (not SERVICE_FQDN_* env)
# Manifest: server-side persistent file mounted read-only into frontend
#
# Coolify deployment:
#   build_pack: dockercompose
#   docker_compose_location: /deploy/preview/{slug}.compose.yml
#   git_repository: git@github.com:JasonMMo/compounding-stack-harness.git
#   git_branch: master
#   private_key_uuid: s127pafarr46wlu1r2mre2te

services:

  backend:
    build:
      context: .
      dockerfile: backend/adapters/fastapi/Dockerfile
    environment:
      PORT: "8081"
      PYTHONIOENCODING: "utf-8"
    # No custom network — Coolify attaches containers to its uuid network only.
    # Traefik can only reach uuid-net IPs; declaring preview-net caused bistable 504.
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: frontend/adapters/vanilla-htmx/Dockerfile
    environment:
      # Domain routing: set via Coolify API PATCH docker_compose_domains
      # [{{"name":"frontend","domain":"https://{slug}.n9n.co.kr"}}]
      # Do NOT use SERVICE_FQDN_* env here — set via API, not compose file.
      FRONTEND_PORT: "5000"
      BACKEND_BASE_URL: "http://backend:8081"
      CONTRACT_DIR: "/app/middle/contract"
      PROFILE_MANIFEST: "/data/manifest/screen-manifest.json"
      PYTHONIOENCODING: "utf-8"
      # SECRET_KEY injected via Coolify environment variables (not in compose file)
    volumes:
      # Persistent manifest file — scp'd to server before deploy
      # Path: /data/coolify/manifests/{slug}/screen-manifest.json
      - type: bind
        source: /data/coolify/manifests/{slug}/screen-manifest.json
        target: /data/manifest/screen-manifest.json
        read_only: true
    ports:
      - "5000"
    depends_on:
      - backend
    restart: unless-stopped
"""

_COOLIFY_COMPOSE_TEMPLATE_WITH_SEED = """\
# deploy/preview/{slug}.compose.yml
# Coolify dockercompose preview — profile: {slug}
# Build context: repo root (Coolify clones whole repo, build context = clone root)
#
# Domain: set via Coolify API PATCH docker_compose_domains (not SERVICE_FQDN_* env)
# Manifest: server-side persistent file mounted read-only into frontend
# Seed: server-side seed-data.json mounted read-only into backend (SEED_FILE)
#
# Coolify deployment:
#   build_pack: dockercompose
#   docker_compose_location: /deploy/preview/{slug}.compose.yml
#   git_repository: git@github.com:JasonMMo/compounding-stack-harness.git
#   git_branch: master
#   private_key_uuid: s127pafarr46wlu1r2mre2te

services:

  backend:
    build:
      context: .
      dockerfile: backend/adapters/fastapi/Dockerfile
    environment:
      PORT: "8081"
      PYTHONIOENCODING: "utf-8"
      SEED_FILE: "/data/seed/seed-data.json"
    volumes:
      # Seed data file — scp'd to server before deploy
      # Path: /data/coolify/manifests/{slug}/seed-data.json
      - type: bind
        source: /data/coolify/manifests/{slug}/seed-data.json
        target: /data/seed/seed-data.json
        read_only: true
    # No custom network — Coolify attaches containers to its uuid network only.
    # Traefik can only reach uuid-net IPs; declaring preview-net caused bistable 504.
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: frontend/adapters/vanilla-htmx/Dockerfile
    environment:
      # Domain routing: set via Coolify API PATCH docker_compose_domains
      # [{{"name":"frontend","domain":"https://{slug}.n9n.co.kr"}}]
      # Do NOT use SERVICE_FQDN_* env here — set via API, not compose file.
      FRONTEND_PORT: "5000"
      BACKEND_BASE_URL: "http://backend:8081"
      CONTRACT_DIR: "/app/middle/contract"
      PROFILE_MANIFEST: "/data/manifest/screen-manifest.json"
      PYTHONIOENCODING: "utf-8"
      # SECRET_KEY injected via Coolify environment variables (not in compose file)
    volumes:
      # Persistent manifest file — scp'd to server before deploy
      # Path: /data/coolify/manifests/{slug}/screen-manifest.json
      - type: bind
        source: /data/coolify/manifests/{slug}/screen-manifest.json
        target: /data/manifest/screen-manifest.json
        read_only: true
    ports:
      - "5000"
    depends_on:
      - backend
    restart: unless-stopped
"""

# Backward-compat alias: templates without seed use the no-seed template as default
_COOLIFY_COMPOSE_TEMPLATE = _COOLIFY_COMPOSE_TEMPLATE_NO_SEED

_COMPOSE_TEMPLATE = """\
# docker-compose.yml — local preview for profile: {slug}
# Generated by: scripts/workflow/preview_package.py
#
# Usage:
#   docker compose -f out/{slug}/docker-compose.yml up -d --build
#   docker compose -f out/{slug}/docker-compose.yml logs -f
#   docker compose -f out/{slug}/docker-compose.yml down -v
#
# NOTE: Build context is the REPO ROOT, not this file's directory.
# Run docker compose from the repo root or use --project-directory.
#
# Ports:
#   frontend → host :{frontend_port}  (browser: http://localhost:{frontend_port}/login)
#   backend  → NOT exposed to host (internal only via compose network)

services:

  backend:
    build:
      context: {repo_root_posix}
      dockerfile: backend/adapters/fastapi/Dockerfile
    image: compounding-backend-{slug}:local
    environment:
      PORT: "8081"
      PYTHONIOENCODING: "utf-8"
    # No host port binding — frontend reaches backend inside compose network
    networks:
      - preview-net
    restart: unless-stopped

  frontend:
    build:
      context: {repo_root_posix}
      dockerfile: frontend/adapters/vanilla-htmx/Dockerfile
    image: compounding-frontend-{slug}:local
    environment:
      FRONTEND_PORT: "5000"
      BACKEND_BASE_URL: "http://backend:8081"
      CONTRACT_DIR: "/app/middle/contract"
      PROFILE_MANIFEST: "/data/manifest/screen-manifest.json"
      # SECRET_KEY: "change-me-in-production"  # set via env or secrets manager
      PYTHONIOENCODING: "utf-8"
    ports:
      - "{frontend_port}:5000"
    volumes:
      # Mount the generated manifest read-only into the container.
      # Re-run preview_package.py after scaffold changes to refresh.
      - type: bind
        source: {manifest_host_posix}
        target: /data/manifest/screen-manifest.json
        read_only: true
    depends_on:
      - backend
    networks:
      - preview-net
    restart: unless-stopped

networks:
  preview-net:
    driver: bridge
"""

# ---------------------------------------------------------------------------
# Scaffold helper
# ---------------------------------------------------------------------------

def run_scaffold(slug: str, out_root: Path) -> int:
    """Invoke scaffold.py as a subprocess. Returns exit code."""
    scaffold_script = REPO_ROOT / "scripts" / "workflow" / "scaffold.py"
    cmd = [
        sys.executable,
        str(scaffold_script),
        "--profile", slug,
        "--out", str(out_root),
    ]
    result = subprocess.run(cmd, env=_utf8_env())
    return result.returncode


def _utf8_env() -> dict:
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


# ---------------------------------------------------------------------------
# Compose writer
# ---------------------------------------------------------------------------

def write_coolify_compose(slug: str, out_root: Path | None = None) -> Path:
    """Write deploy/preview/<slug>.compose.yml for Coolify deployment.

    If out/<slug>/seed-data.json exists, uses the seed-aware template which adds:
      - backend SEED_FILE env var pointing to /data/seed/seed-data.json
      - backend bind-mount: /data/coolify/manifests/<slug>/seed-data.json (ro)
    Otherwise uses the no-seed template (backward-compatible — lawfirm/shop unaffected).
    """
    deploy_dir = REPO_ROOT / "deploy" / "preview"
    deploy_dir.mkdir(parents=True, exist_ok=True)

    # Detect seed file existence to select template
    _out = out_root if out_root is not None else (REPO_ROOT / "out")
    seed_path = _out / slug / "seed-data.json"
    has_seed = seed_path.exists()

    if has_seed:
        template = _COOLIFY_COMPOSE_TEMPLATE_WITH_SEED
        print(f"[preview_package] seed file detected at {seed_path} — using seed-aware template.")
    else:
        template = _COOLIFY_COMPOSE_TEMPLATE_NO_SEED

    compose_content = template.format(slug=slug)

    compose_path = deploy_dir / f"{slug}.compose.yml"
    compose_path.write_text(compose_content, encoding="utf-8")
    return compose_path


def write_compose(slug: str, out_root: Path, frontend_port: int) -> Path:
    out_dir = out_root / slug
    manifest_host = (out_dir / "screen-manifest.json").resolve()

    compose_content = _COMPOSE_TEMPLATE.format(
        slug=slug,
        repo_root_posix=REPO_ROOT.as_posix(),
        manifest_host_posix=manifest_host.as_posix(),
        frontend_port=frontend_port,
    )

    compose_path = out_dir / "docker-compose.yml"
    compose_path.write_text(compose_content, encoding="utf-8")
    return compose_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _verify_coolify_compose_structure(slug: str, compose_path: Path) -> bool:
    """Verify generated Coolify compose matches reference templates structurally.

    Diffs generated file against shop-demo reference (slug substituted out).
    Returns True if structurally identical (slug differences only), OR if the
    only differences are seed-specific additions (SEED_FILE env + volumes block).
    Seed-aware composes are expected to differ from shop-demo — logged as INFO,
    not WARN.
    """
    import difflib

    reference_path = REPO_ROOT / "deploy" / "preview" / "shop-demo.compose.yml"
    if not reference_path.exists():
        print("[preview_package] WARN: reference shop-demo.compose.yml not found — skipping diff.")
        return True

    generated = compose_path.read_text(encoding="utf-8")
    reference = reference_path.read_text(encoding="utf-8")

    # Normalize: replace slug in generated with reference slug for comparison
    generated_normalized = generated.replace(slug, "shop-demo")

    if generated_normalized == reference:
        print("[preview_package] structural diff vs shop-demo: PASS (slug differences only).")
        return True

    # Check if differences are only seed-related lines
    seed_markers = {"SEED_FILE", "seed-data.json", "/data/seed/", "# Seed:", "Seed:"}
    diff_lines = list(difflib.unified_diff(
        reference.splitlines(keepends=True),
        generated_normalized.splitlines(keepends=True),
        fromfile="shop-demo.compose.yml (reference)",
        tofile=f"{slug}.compose.yml (generated, slug normalized)",
        n=0,
    ))
    non_seed_diffs = [
        ln for ln in diff_lines
        if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))
        and not any(m in ln for m in seed_markers)
    ]
    if not non_seed_diffs:
        print("[preview_package] structural diff vs shop-demo: PASS (seed additions only — expected).")
        return True

    # Show diff for diagnosis
    diff = list(difflib.unified_diff(
        reference.splitlines(keepends=True),
        generated_normalized.splitlines(keepends=True),
        fromfile="shop-demo.compose.yml (reference)",
        tofile=f"{slug}.compose.yml (generated, slug normalized)",
        n=3,
    ))
    if diff:
        print("[preview_package] WARN: structural diff detected (non-slug, non-seed differences):")
        for line in diff:
            print("  " + line.rstrip())
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate docker-compose.yml for local or Coolify customer preview.",
    )
    parser.add_argument("--profile", required=True, help="Profile slug (e.g. lawfirm-demo)")
    parser.add_argument("--out", default=str(REPO_ROOT / "out"), help="Output root directory")
    parser.add_argument(
        "--frontend-port", type=int, default=8090,
        help="Host port for frontend — LOCAL mode only (default: 8090)",
    )
    parser.add_argument(
        "--force-scaffold", action="store_true",
        help="Re-run scaffold.py even if out/<slug>/screen-manifest.json already exists.",
    )
    parser.add_argument(
        "--coolify", action="store_true",
        help=(
            "Generate deploy/preview/<slug>.compose.yml for Coolify deployment "
            "instead of out/<slug>/docker-compose.yml for local use."
        ),
    )
    args = parser.parse_args()

    slug: str = args.profile
    out_root = Path(args.out).resolve()
    manifest_path = out_root / slug / "screen-manifest.json"

    # Step 1: scaffold (both modes)
    if manifest_path.exists() and not args.force_scaffold:
        print(f"[preview_package] scaffold artifacts found at {out_root / slug} — skipping scaffold.")
        print(f"[preview_package] (pass --force-scaffold to regenerate)")
    else:
        print(f"[preview_package] running scaffold for profile={slug} ...")
        rc = run_scaffold(slug, out_root)
        if rc != 0:
            print("[preview_package] ERROR: scaffold.py failed — aborting.", file=sys.stderr)
            return 1
        if not manifest_path.exists():
            print(
                f"[preview_package] ERROR: scaffold succeeded but manifest not found at {manifest_path}",
                file=sys.stderr,
            )
            return 1
        print(f"[preview_package] scaffold complete. manifest → {manifest_path}")

    if args.coolify:
        # Step 2 (Coolify mode): write deploy/preview/<slug>.compose.yml
        compose_path = write_coolify_compose(slug, out_root=out_root)
        print(f"[preview_package] Coolify compose written → {compose_path}")

        # Structural diff verification against reference.
        # Skip when seed file is present: seed-aware template intentionally adds
        # backend volumes/SEED_FILE block not present in shop-demo reference.
        seed_file_exists = (out_root / slug / "seed-data.json").exists()
        if seed_file_exists:
            print("[preview_package] structural diff skipped (seed-aware compose — expected additions).")
        else:
            _verify_coolify_compose_structure(slug, compose_path)

        print()
        print("Coolify next steps:")
        print(f"  1. git add {compose_path.relative_to(REPO_ROOT).as_posix()}")
        print(f"  2. git commit + push to master")
        print(f"  3. scp out/{slug}/screen-manifest.json → root@187.77.140.157:/data/coolify/manifests/{slug}/")
        print(f"  4. python scripts/workflow/deploy_to_coolify.py --slug {slug} --dry-run")
        print(f"  5. python scripts/workflow/deploy_to_coolify.py --slug {slug}")
    else:
        # Step 2 (local mode): write out/<slug>/docker-compose.yml
        compose_path = write_compose(slug, out_root, args.frontend_port)
        print(f"[preview_package] compose written → {compose_path}")
        print()
        print("Next steps:")
        print(f"  docker compose -f \"{compose_path}\" up -d --build")
        print(f"  # then open http://localhost:{args.frontend_port}/login")
        print(f"  docker compose -f \"{compose_path}\" down -v  # cleanup")

    return 0


if __name__ == "__main__":
    sys.exit(main())
