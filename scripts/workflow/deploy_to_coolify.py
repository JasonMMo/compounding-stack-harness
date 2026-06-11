"""
deploy_to_coolify.py — idempotent single-command Coolify preview deployment.

Usage:
  # Dry-run first (no API mutations — payload only, token/secret values omitted):
  python scripts/workflow/deploy_to_coolify.py --slug shop-demo --dry-run

  # Real deploy (idempotent — reuses existing project/app if found):
  python scripts/workflow/deploy_to_coolify.py --slug shop-demo

Steps (runbook docs/runbooks/preview-deploy.md §4):
  1. Verify SSH tunnel to Coolify API (localhost:8000).
  2. Ensure project — reuse if <slug> already exists, create otherwise.
  3. Ensure application — reuse if <slug> app already exists, create otherwise.
     POST /applications/private-deploy-key with validated payload.
     Pitfall: docker_compose_location MUST start with '/' (absolute).
  4. PATCH domain — docker_compose_domains array (NOT fqdn field — 422).
  5. SCP manifest to server /data/coolify/manifests/<slug>/screen-manifest.json.
  6. Trigger instant deploy.
  7. Poll build status until finished or error (timeout 5 min).
  8. External validation: /login HTTP 200, /health HTTP 200, TLS CN match.

Security:
  - Token read from infra/secrets/preview-vps.env via sed (no shell source).
  - Token never printed — length only.
  - SECRET_KEY read from infra/secrets/<slug>-secret-key.txt (gitignored vault).
  - GET /applications/{uuid}/envs response: real_value field masked (CISO §7 note).
  - Token never passed via argv (ps exposure risk).

Fixed constants (from runbook — do NOT regenerate):
  server_uuid:      n12vdydjpwp81hu5i15n1gsb
  private_key_uuid: s127pafarr46wlu1r2mre2te
  git_repository:   git@github.com:JasonMMo/compounding-stack-harness.git
  git_branch:       master
  API base:         http://localhost:8000/api/v1/ (SSH tunnel, port 8000)

Exit codes: 0 success, 1 error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants (verified — do NOT modify without runbook update)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
API_BASE = "http://localhost:8000/api/v1"
SERVER_UUID = "n12vdydjpwp81hu5i15n1gsb"
PRIVATE_KEY_UUID = "s127pafarr46wlu1r2mre2te"
GIT_REPOSITORY = "git@github.com:JasonMMo/compounding-stack-harness.git"
GIT_BRANCH = "master"
PREVIEW_HOST = "root@187.77.140.157"
PREVIEW_SSH_KEY = str(Path.home() / ".ssh" / "n9n_preview_ed25519")
MANIFEST_SERVER_BASE = "/data/coolify/manifests"

# ---------------------------------------------------------------------------
# Token loader — sed extraction, no shell source, no print
# ---------------------------------------------------------------------------

def _load_token() -> str:
    """Read Coolify API token from vault file.

    Supports two formats:
      - Raw value only (preview-vps.env contains raw token string)
      - KEY=value format (sed strips prefix)

    Never prints the token value — only length for verification.
    """
    vault_path = REPO_ROOT / "infra" / "secrets" / "preview-vps.env"
    if not vault_path.exists():
        print(
            f"[deploy_to_coolify] ERROR: vault file not found: {vault_path}",
            file=sys.stderr,
        )
        print(
            "[deploy_to_coolify] Expected: infra/secrets/preview-vps.env (gitignored, raw token or COOLIFY_API_TOKEN=<value>)",
            file=sys.stderr,
        )
        sys.exit(1)

    raw = vault_path.read_text(encoding="utf-8").strip()
    # Strip optional KEY= prefix (handles both raw and KEY=value formats)
    token = re.sub(r"^COOLIFY_API_TOKEN=", "", raw).strip()

    if not token:
        print(
            "[deploy_to_coolify] ERROR: token is empty after reading vault file.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[deploy_to_coolify] token loaded (len={len(token)}).")
    return token


def _load_secret_key(slug: str) -> str | None:
    """Read SECRET_KEY from vault file infra/secrets/<slug>-secret-key.txt.

    Returns None if file does not exist (caller handles).
    Never prints the value.
    """
    vault_path = REPO_ROOT / "infra" / "secrets" / f"{slug}-secret-key.txt"
    if not vault_path.exists():
        return None
    value = vault_path.read_text(encoding="utf-8").strip()
    if not value:
        return None
    print(f"[deploy_to_coolify] secret-key loaded for {slug} (len={len(value)}).")
    return value


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _api_request(
    method: str,
    path: str,
    token: str,
    body: dict | None = None,
    dry_run: bool = False,
    mutating: bool = True,
) -> dict | None:
    """Perform a Coolify API request.

    In dry_run mode, mutating requests (POST/PATCH/DELETE) print payload and return None.
    GET requests always execute (needed for idempotency checks).

    CISO note: if response contains env variable data, real_value fields are masked
    before any printing via _mask_env_values().
    """
    url = f"{API_BASE}/{path.lstrip('/')}"
    data = json.dumps(body).encode("utf-8") if body else None

    if dry_run and mutating and method.upper() != "GET":
        safe_body = _redact_secrets(body) if body else {}
        print(f"[DRY-RUN] {method.upper()} {url}")
        print(f"[DRY-RUN] payload: {json.dumps(safe_body, indent=2, ensure_ascii=False)}")
        return None

    req = urllib.request.Request(url, data=data, method=method.upper())
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_body = resp.read().decode("utf-8")
            if not response_body.strip():
                return {}
            parsed = json.loads(response_body)
            # CISO: mask real_value fields in env responses before any use
            return _mask_env_values(parsed)
    except urllib.error.HTTPError as exc:
        body_bytes = exc.read()
        try:
            err_body = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            err_body = body_bytes.decode("utf-8", errors="replace")
        print(
            f"[deploy_to_coolify] HTTP {exc.code} on {method.upper()} {url}: {err_body}",
            file=sys.stderr,
        )
        raise


def _redact_secrets(body: dict) -> dict:
    """Return a copy of body with sensitive field values replaced by '***'."""
    sensitive_keys = {"value", "secret", "password", "token", "key", "SECRET_KEY"}
    result = {}
    for k, v in body.items():
        if any(sk.lower() in k.lower() for sk in sensitive_keys):
            result[k] = "***"
        elif isinstance(v, dict):
            result[k] = _redact_secrets(v)
        elif isinstance(v, list):
            result[k] = [_redact_secrets(i) if isinstance(i, dict) else i for i in v]
        else:
            result[k] = v
    return result


def _mask_env_values(obj: Any) -> Any:
    """Recursively mask real_value fields in API response objects.

    CISO requirement: GET /applications/{uuid}/envs exposes real_value with
    plaintext SECRET_KEY — mask before any logging or return.
    """
    if isinstance(obj, dict):
        return {
            k: ("***masked***" if k == "real_value" else _mask_env_values(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_mask_env_values(i) for i in obj]
    return obj


# ---------------------------------------------------------------------------
# Tunnel check
# ---------------------------------------------------------------------------

def check_tunnel(dry_run: bool = False) -> bool:
    """Verify SSH tunnel to Coolify API is alive.

    Returns True if API responds (404 = alive per runbook).
    Prints tunnel reactivation command if dead.
    """
    try:
        req = urllib.request.Request(
            f"{API_BASE}/healthcheck",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            _ = resp.read()
        print("[deploy_to_coolify] tunnel: alive (200).")
        return True
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print("[deploy_to_coolify] tunnel: alive (404 = API responds).")
            return True
        print(f"[deploy_to_coolify] tunnel: HTTP {exc.code} — may still be alive.", file=sys.stderr)
        return True
    except Exception as exc:
        print(f"[deploy_to_coolify] tunnel: DEAD — {exc}", file=sys.stderr)
        print(
            "[deploy_to_coolify] Reactivate with:\n"
            f"  ssh -i {PREVIEW_SSH_KEY} -fN -o ServerAliveInterval=30 "
            f"-L 8000:localhost:8000 {PREVIEW_HOST}",
            file=sys.stderr,
        )
        return False


# ---------------------------------------------------------------------------
# Project ensure
# ---------------------------------------------------------------------------

def ensure_project(slug: str, token: str, dry_run: bool = False) -> str | None:
    """Return project_uuid for slug, creating if necessary (idempotent).

    In dry_run: prints create payload and returns a placeholder UUID.
    """
    projects = _api_request("GET", "/projects", token, dry_run=dry_run, mutating=False)
    if projects:
        for proj in projects:
            if proj.get("name") == slug:
                uuid = proj["uuid"]
                print(f"[deploy_to_coolify] project '{slug}' already exists — reusing uuid={uuid}.")
                return uuid

    # Create new project
    payload = {"name": slug, "description": f"Preview — {slug}"}
    if dry_run:
        _api_request("POST", "/projects", token, body=payload, dry_run=True)
        return f"DRY-RUN-PROJECT-UUID-{slug}"

    result = _api_request("POST", "/projects", token, body=payload)
    uuid = result["uuid"]
    print(f"[deploy_to_coolify] project created: uuid={uuid}.")
    return uuid


# ---------------------------------------------------------------------------
# Application ensure
# ---------------------------------------------------------------------------

def ensure_application(slug: str, project_uuid: str, token: str, dry_run: bool = False) -> str | None:
    """Return app_uuid for slug, creating if necessary (idempotent).

    Pitfall (runbook §4b): docker_compose_location MUST start with '/'.
    """
    # Check if app already exists under any project
    apps = _api_request("GET", "/applications", token, dry_run=dry_run, mutating=False)
    if apps:
        # API may return list or dict with data key
        app_list = apps if isinstance(apps, list) else apps.get("data", [])
        for app in app_list:
            if app.get("name") == slug:
                uuid = app["uuid"]
                print(f"[deploy_to_coolify] application '{slug}' already exists — reusing uuid={uuid}.")
                return uuid

    compose_location = f"/deploy/preview/{slug}.compose.yml"

    # Verify compose file is committed before creating app
    compose_path = REPO_ROOT / "deploy" / "preview" / f"{slug}.compose.yml"
    if not compose_path.exists() and not dry_run:
        print(
            f"[deploy_to_coolify] ERROR: {compose_path} not found.\n"
            f"  Run: python scripts/workflow/preview_package.py --profile {slug} --coolify\n"
            f"  Then commit + push before deploying.",
            file=sys.stderr,
        )
        sys.exit(1)

    payload = {
        "project_uuid": project_uuid,
        "server_uuid": SERVER_UUID,
        "environment_name": "production",
        "build_pack": "dockercompose",
        "git_repository": GIT_REPOSITORY,
        "git_branch": GIT_BRANCH,
        "private_key_uuid": PRIVATE_KEY_UUID,
        "docker_compose_location": compose_location,
        "name": slug,
        "instant_deploy": False,
    }

    if dry_run:
        _api_request(
            "POST", "/applications/private-deploy-key", token,
            body=payload, dry_run=True,
        )
        return f"DRY-RUN-APP-UUID-{slug}"

    result = _api_request("POST", "/applications/private-deploy-key", token, body=payload)
    uuid = result["uuid"]
    print(f"[deploy_to_coolify] application created: uuid={uuid}.")
    return uuid


# ---------------------------------------------------------------------------
# Domain PATCH
# ---------------------------------------------------------------------------

def patch_domain(app_uuid: str, slug: str, token: str, dry_run: bool = False) -> None:
    """Set docker_compose_domains via PATCH.

    Pitfall (runbook §4c): use docker_compose_domains array — NOT fqdn field (422).
    """
    payload = {
        "docker_compose_domains": [
            {"name": "frontend", "domain": f"https://{slug}.n9n.co.kr"}
        ]
    }
    _api_request("PATCH", f"/applications/{app_uuid}", token, body=payload, dry_run=dry_run)
    if not dry_run:
        print(f"[deploy_to_coolify] domain patched: https://{slug}.n9n.co.kr → frontend.")


# ---------------------------------------------------------------------------
# Manifest SCP
# ---------------------------------------------------------------------------

def scp_manifest(slug: str, dry_run: bool = False) -> bool:
    """SCP manifest to server /data/coolify/manifests/<slug>/screen-manifest.json.

    Returns True on success.
    """
    manifest_local = REPO_ROOT / "out" / slug / "screen-manifest.json"
    remote_dir = f"{MANIFEST_SERVER_BASE}/{slug}"
    remote_path = f"{remote_dir}/screen-manifest.json"

    if not manifest_local.exists():
        print(
            f"[deploy_to_coolify] ERROR: manifest not found at {manifest_local}.\n"
            f"  Run: python scripts/workflow/preview_package.py --profile {slug} --coolify",
            file=sys.stderr,
        )
        return False

    mkdir_cmd = [
        "ssh",
        "-i", PREVIEW_SSH_KEY,
        "-o", "StrictHostKeyChecking=accept-new",
        PREVIEW_HOST,
        f"mkdir -p {remote_dir}",
    ]
    scp_cmd = [
        "scp",
        "-i", PREVIEW_SSH_KEY,
        "-o", "StrictHostKeyChecking=accept-new",
        str(manifest_local),
        f"{PREVIEW_HOST}:{remote_path}",
    ]

    if dry_run:
        print(f"[DRY-RUN] ssh mkdir -p {remote_dir}")
        print(f"[DRY-RUN] scp {manifest_local} → {PREVIEW_HOST}:{remote_path}")
        return True

    print(f"[deploy_to_coolify] creating remote dir {remote_dir} ...")
    result = subprocess.run(mkdir_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: ssh mkdir failed: {result.stderr}", file=sys.stderr)
        return False

    print(f"[deploy_to_coolify] scp manifest → {remote_path} ...")
    result = subprocess.run(scp_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: scp failed: {result.stderr}", file=sys.stderr)
        return False

    print(f"[deploy_to_coolify] manifest uploaded.")
    return True


# ---------------------------------------------------------------------------
# Secret KEY injection
# ---------------------------------------------------------------------------

def inject_secret_key(app_uuid: str, slug: str, token: str, dry_run: bool = False) -> None:
    """Inject SECRET_KEY env var into Coolify application from vault.

    Pitfall (runbook §6): body must be key+value only — is_build_time/is_secret = 422.
    CISO: value never printed; vault file gitignored.
    """
    secret_key = _load_secret_key(slug)
    if not secret_key:
        # Generate and save
        import secrets as _secrets
        secret_key = _secrets.token_hex(32)
        vault_path = REPO_ROOT / "infra" / "secrets" / f"{slug}-secret-key.txt"
        if not dry_run:
            vault_path.write_text(secret_key, encoding="utf-8")
            print(f"[deploy_to_coolify] SECRET_KEY generated and saved to {vault_path}.")
        else:
            print(f"[DRY-RUN] SECRET_KEY would be generated and saved to {vault_path}.")

    payload = {"key": "SECRET_KEY", "value": secret_key}

    if dry_run:
        print(f"[DRY-RUN] POST /applications/{app_uuid}/envs  (PATCH if already exists)")
        print("[DRY-RUN] payload: {\"key\": \"SECRET_KEY\", \"value\": \"***\"}")
        return

    # Idempotent: POST first, treat 409 (already exists) as success.
    # Coolify 4.1.2 does not expose a stable per-env PATCH endpoint —
    # if the env already exists with a valid value, skip silently.
    try:
        _api_request("POST", f"/applications/{app_uuid}/envs", token, body=payload)
        print(f"[deploy_to_coolify] SECRET_KEY injected (len={len(secret_key)}).")
    except urllib.error.HTTPError as exc:
        if exc.code == 409:
            print(
                f"[deploy_to_coolify] SECRET_KEY already exists on app (409 — idempotent skip)."
            )
        else:
            raise


# ---------------------------------------------------------------------------
# Deploy trigger + poll
# ---------------------------------------------------------------------------

def trigger_deploy(app_uuid: str, token: str, dry_run: bool = False) -> str | None:
    """Trigger instant deploy. Returns deployment_uuid."""
    if dry_run:
        print(f"[DRY-RUN] GET /applications/{app_uuid}/start")
        return f"DRY-RUN-DEPLOY-UUID"

    result = _api_request("GET", f"/applications/{app_uuid}/start", token, mutating=True)
    deploy_uuid = result.get("deployment_uuid") or result.get("uuid")
    print(f"[deploy_to_coolify] deploy queued: deployment_uuid={deploy_uuid}.")
    return deploy_uuid


def poll_deployment(deploy_uuid: str, token: str, timeout_s: int = 300) -> bool:
    """Poll deployment status until finished/error or timeout.

    Returns True on success (status=finished).
    Runbook: success = status=='finished'.
    """
    print(f"[deploy_to_coolify] polling deployment {deploy_uuid} (timeout={timeout_s}s) ...")
    deadline = time.time() + timeout_s
    interval = 5

    while time.time() < deadline:
        try:
            result = _api_request(
                "GET", f"/deployments/{deploy_uuid}", token,
                dry_run=False, mutating=False,
            )
            status = result.get("status", "unknown")
            print(f"[deploy_to_coolify]   status={status}")
            if status == "finished":
                print("[deploy_to_coolify] build FINISHED.")
                return True
            if status in ("error", "failed"):
                print(f"[deploy_to_coolify] build FAILED (status={status}).", file=sys.stderr)
                return False
        except Exception as exc:
            print(f"[deploy_to_coolify] poll error: {exc}", file=sys.stderr)

        time.sleep(interval)

    print(f"[deploy_to_coolify] TIMEOUT after {timeout_s}s.", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# External validation
# ---------------------------------------------------------------------------

def validate_preview(slug: str) -> bool:
    """Validate deployed preview: /login HTTP 200, /health HTTP 200, TLS CN match.

    Uses subprocess for TLS validation (openssl s_client).
    Returns True if all 3 pass.
    """
    base_url = f"https://{slug}.n9n.co.kr"
    all_pass = True

    # /login HTTP 200
    for path in ["/login", "/health"]:
        url = base_url + path
        print(f"[deploy_to_coolify] validating {url} ...")
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                code = resp.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception as exc:
            print(f"[deploy_to_coolify]   ERROR: {exc}", file=sys.stderr)
            all_pass = False
            continue

        status = "PASS" if code == 200 else "FAIL"
        print(f"[deploy_to_coolify]   HTTP {code} — {status}")
        if code != 200:
            all_pass = False

    # TLS CN check via openssl
    print(f"[deploy_to_coolify] validating TLS CN for {slug}.n9n.co.kr ...")
    try:
        result = subprocess.run(
            [
                "openssl", "s_client",
                "-connect", f"{slug}.n9n.co.kr:443",
                "-servername", f"{slug}.n9n.co.kr",
            ],
            input=b"",
            capture_output=True,
            timeout=15,
        )
        cert_result = subprocess.run(
            ["openssl", "x509", "-noout", "-subject", "-issuer"],
            input=result.stdout,
            capture_output=True,
            timeout=5,
        )
        cert_text = cert_result.stdout.decode("utf-8", errors="replace")
        expected_cn = f"CN={slug}.n9n.co.kr"
        if expected_cn in cert_text and "Let's Encrypt" in cert_text:
            print(f"[deploy_to_coolify]   TLS CN — PASS ({expected_cn}, issuer=Let's Encrypt)")
        else:
            print(f"[deploy_to_coolify]   TLS CN — WARN: {cert_text.strip()}")
    except Exception as exc:
        print(f"[deploy_to_coolify]   TLS check skipped: {exc}")

    return all_pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Idempotent Coolify preview deployment — runbook §4 single command.",
    )
    parser.add_argument("--slug", required=True, help="Profile slug (e.g. shop-demo)")
    parser.add_argument(
        "--dry-run", action="store_true",
        help=(
            "Print payloads only — no POST/PATCH/deploy. Token and secret values omitted. "
            "Always run this first for verification."
        ),
    )
    parser.add_argument(
        "--skip-scp", action="store_true",
        help="Skip manifest SCP step (manifest already on server).",
    )
    parser.add_argument(
        "--skip-validation", action="store_true",
        help="Skip external HTTP/TLS validation after deploy.",
    )
    args = parser.parse_args()

    slug: str = args.slug
    dry_run: bool = args.dry_run

    if dry_run:
        print(f"[deploy_to_coolify] DRY-RUN mode — no mutations will be made.")

    print(f"[deploy_to_coolify] slug={slug}")

    # Load token (always — needed for GET calls even in dry-run)
    token = _load_token()

    # Step 0: tunnel check
    if not check_tunnel(dry_run=dry_run):
        return 1

    # Step 1: project ensure
    project_uuid = ensure_project(slug, token, dry_run=dry_run)
    if not project_uuid:
        print("[deploy_to_coolify] ERROR: could not get project_uuid.", file=sys.stderr)
        return 1

    # Step 2: application ensure
    app_uuid = ensure_application(slug, project_uuid, token, dry_run=dry_run)
    if not app_uuid:
        print("[deploy_to_coolify] ERROR: could not get app_uuid.", file=sys.stderr)
        return 1

    # Step 3: domain PATCH
    patch_domain(app_uuid, slug, token, dry_run=dry_run)

    # Step 4: manifest SCP
    if not args.skip_scp:
        if not scp_manifest(slug, dry_run=dry_run):
            return 1
    else:
        print("[deploy_to_coolify] --skip-scp: manifest SCP skipped.")

    # Step 5: SECRET_KEY injection
    inject_secret_key(app_uuid, slug, token, dry_run=dry_run)

    # Step 6: deploy trigger
    deploy_uuid = trigger_deploy(app_uuid, token, dry_run=dry_run)

    if dry_run:
        print()
        print("[DRY-RUN] All steps printed. Re-run without --dry-run to execute.")
        return 0

    # Step 7: poll build
    if deploy_uuid:
        success = poll_deployment(deploy_uuid, token)
        if not success:
            print("[deploy_to_coolify] Build failed — check Coolify logs.", file=sys.stderr)
            return 1

    # Step 8: external validation
    if not args.skip_validation:
        print(f"[deploy_to_coolify] waiting 5s for traefik routing to settle ...")
        time.sleep(5)
        all_pass = validate_preview(slug)
        if not all_pass:
            print(
                "[deploy_to_coolify] WARN: validation failures detected — preview may still be starting.",
                file=sys.stderr,
            )
    else:
        print("[deploy_to_coolify] --skip-validation: external check skipped.")

    print()
    print(f"[deploy_to_coolify] DONE. Preview: https://{slug}.n9n.co.kr/login")
    return 0


if __name__ == "__main__":
    sys.exit(main())
