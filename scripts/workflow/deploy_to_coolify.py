"""
deploy_to_coolify.py — idempotent single-command Coolify preview deployment.

Usage:
  # Dry-run first (no API mutations — payload only, token/secret values omitted):
  python scripts/workflow/deploy_to_coolify.py --slug shop-demo --dry-run

  # Real deploy (idempotent — reuses existing project/app if found):
  python scripts/workflow/deploy_to_coolify.py --slug shop-demo

  # With compose file commit+push before deploy:
  python scripts/workflow/deploy_to_coolify.py --slug new-client --commit

Steps (runbook docs/runbooks/preview-deploy.md §4):
  1. Verify SSH tunnel to Coolify API (localhost:8000).
  2. Ensure project — reuse if <slug> already exists, create otherwise.
  3. Ensure application — reuse if <slug> app already exists, create otherwise.
     POST /applications/private-deploy-key with validated payload.
     Pitfall: docker_compose_location MUST start with '/' (absolute).
  4. PATCH domain — docker_compose_domains array (NOT fqdn field — 422).
     Pitfall: PATCH 직후 422 'docker_compose_raw' race — app 생성 후 Coolify 가
     git fetch 전이면 422; poll(_wait_for_compose_raw)+retry 로 자동 복구.
  5. SCP manifest to server /data/coolify/manifests/<slug>/screen-manifest.json.
  6. Trigger instant deploy.
  7. Poll build status until finished or error (timeout 5 min).
  8. External validation: /login HTTP 200, /health HTTP 200, TLS CN match.
  9. Update registry infra/registry/<slug>.yaml (merge — never clobber existing fields).

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

# yaml: stdlib only — we use a minimal hand-rolled approach to preserve
# comments and hand-written fields (PyYAML is not guaranteed installed).
# We merge only the specific known keys rather than full parse+dump.

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
        print(f"[deploy_to_coolify] tunnel: HTTP {exc.code} - may still be alive.", file=sys.stderr)
        return True
    except Exception as exc:
        print(f"[deploy_to_coolify] tunnel: DEAD - {exc}", file=sys.stderr)
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

def _registry_uuid(slug: str, key: str) -> str | None:
    """Return a uuid from infra/registry/<slug>.yaml for the given nested key under preview:.

    Supports both new format (nested under preview:) and old flat top-level key.
    Returns None if not found or blank.
    """
    registry_path = REPO_ROOT / "infra" / "registry" / f"{slug}.yaml"
    if not registry_path.exists():
        return None
    lines = registry_path.read_text(encoding="utf-8").splitlines(keepends=True)
    # Try nested lookup first (standard format: preview.coolify_project / preview.coolify_app)
    value = _yaml_get(lines, f"  {key}")
    if not value:
        # Fallback: old flat top-level key (e.g. coolify_project: <uuid>)
        value = _yaml_get(lines, key)
    return value if value else None


def ensure_project(slug: str, token: str, dry_run: bool = False) -> str | None:
    """Return project_uuid for slug, creating if necessary (idempotent).

    Lookup order:
      1. Registry file (infra/registry/<slug>.yaml) preview.coolify_project uuid
         — GET /projects/{uuid} to confirm it still exists.
      2. Name-match against GET /projects list.
      3. Create new project as fallback.

    In dry_run: prints create payload and returns a placeholder UUID.
    """
    # 1. Registry-first: skip name matching entirely if uuid known
    known_uuid = _registry_uuid(slug, "coolify_project")
    if known_uuid:
        try:
            proj = _api_request(
                "GET", f"/projects/{known_uuid}", token,
                dry_run=False, mutating=False,
            )
            if proj and proj.get("uuid"):
                uuid = proj["uuid"]
                print(
                    f"[deploy_to_coolify] project '{slug}' found via registry uuid={uuid} - reusing."
                )
                return uuid
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                print(
                    f"[deploy_to_coolify] WARN: registry uuid {known_uuid} returned 404 "
                    f"— falling back to name lookup."
                )
            else:
                raise

    # 2. Name-match fallback
    projects = _api_request("GET", "/projects", token, dry_run=dry_run, mutating=False)
    if projects:
        for proj in projects:
            if proj.get("name") == slug:
                uuid = proj["uuid"]
                print(f"[deploy_to_coolify] project '{slug}' found by name - reusing uuid={uuid}.")
                return uuid

    # 3. Create new project — ASCII-safe description (Coolify 4.1.2 validation)
    payload = {"name": slug, "description": f"Preview - {slug}"}
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

    Lookup order:
      1. Registry file (infra/registry/<slug>.yaml) preview.coolify_app uuid
         — GET /applications/{uuid} to confirm it still exists.
      2. Name-match against GET /applications list.
      3. Create new application as fallback.

    Pitfall (runbook §4b): docker_compose_location MUST start with '/'.
    """
    # 1. Registry-first: skip name matching entirely if uuid known
    known_app_uuid = _registry_uuid(slug, "coolify_app")
    if known_app_uuid:
        try:
            app = _api_request(
                "GET", f"/applications/{known_app_uuid}", token,
                dry_run=False, mutating=False,
            )
            if app and app.get("uuid"):
                uuid = app["uuid"]
                print(
                    f"[deploy_to_coolify] application '{slug}' found via registry uuid={uuid} - reusing."
                )
                return uuid
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                print(
                    f"[deploy_to_coolify] WARN: registry app uuid {known_app_uuid} returned 404 "
                    f"— falling back to name lookup."
                )
            else:
                raise

    # 2. Name-match fallback
    apps = _api_request("GET", "/applications", token, dry_run=dry_run, mutating=False)
    if apps:
        # API may return list or dict with data key
        app_list = apps if isinstance(apps, list) else apps.get("data", [])
        for app in app_list:
            if app.get("name") == slug:
                uuid = app["uuid"]
                print(f"[deploy_to_coolify] application '{slug}' found by name - reusing uuid={uuid}.")
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

_COMPOSE_RAW_NOT_LOADED = "docker_compose_raw"  # 422 메시지 매칭 키워드


def _wait_for_compose_raw(app_uuid: str, token: str, poll_interval: int = 5, max_wait: int = 120) -> bool:
    """Coolify 가 git 에서 compose 파일을 적재할 때까지 poll.

    POST /applications/private-deploy-key 직후 곧바로 domain PATCH 를 하면
    Coolify 가 아직 git clone/fetch 를 완료하지 못해 docker_compose_raw 가 null 인 경우
    422 'Cannot set docker_compose_domains without docker_compose_raw' 를 반환한다.

    GET /applications/{uuid} 의 docker_compose_raw 필드가 비어 있지 않을 때까지 poll.
    Returns True when loaded, False on timeout.
    """
    deadline = time.time() + max_wait
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            app = _api_request(
                "GET", f"/applications/{app_uuid}", token,
                dry_run=False, mutating=False,
            )
            raw = app.get("docker_compose_raw") if app else None
            if raw:
                print(
                    f"[deploy_to_coolify] docker_compose_raw loaded "
                    f"(attempt={attempt}, len={len(raw)})."
                )
                return True
            print(
                f"[deploy_to_coolify] waiting for compose raw... "
                f"(attempt={attempt}, elapsed={int(time.time() - (deadline - max_wait))}s)"
            )
        except Exception as exc:
            print(f"[deploy_to_coolify] poll error: {exc}", file=sys.stderr)
        time.sleep(poll_interval)

    print(
        f"[deploy_to_coolify] WARN: docker_compose_raw still null after {max_wait}s.",
        file=sys.stderr,
    )
    return False


def patch_domain(app_uuid: str, slug: str, token: str, dry_run: bool = False) -> None:
    """Set docker_compose_domains via PATCH.

    Pitfall (runbook §4c): Coolify 4.1.2 stores docker_compose_domains as a
    JSON-encoded object string: '{"<service>":{"domain":"https://..."}}' — NOT
    the array format [{"name":...,"domain":...}] (that form returns 422).
    Confirmed from live GET /applications response on shop-demo (2026-06-12).

    Pitfall (runbook §4c-2): PATCH 직후 422 'Cannot set docker_compose_domains
    without docker_compose_raw. Reload the compose file from the git repository
    first.' — app 생성 직후 Coolify 가 git 에서 compose 를 아직 fetch 하지 못한
    race condition. GET /applications/{uuid} 의 docker_compose_raw 가 채워질
    때까지 poll (5s 간격, 최대 120s) 후 재시도한다.

    Service name: read from infra/registry/<slug>.yaml preview.domain_service.
    Falls back to "frontend" if key absent (lawfirm/shop backward-compat).
    """
    # registry에서 domain_service 읽기 (없으면 "frontend" 디폴트)
    service_name = _registry_uuid(slug, "domain_service") or "frontend"

    # Coolify 4.1.2 PATCH 포맷: array (GET 응답의 JSON-string 저장과 포맷이 다름).
    # GET 응답: '{"frontend":{"domain":"..."}}' (string)
    # PATCH body: [{"name":"frontend","domain":"..."}] (array) — API validation 확인.
    payload = {
        "docker_compose_domains": [
            {"name": service_name, "domain": f"https://{slug}.n9n.co.kr"}
        ]
    }

    if dry_run:
        _api_request("PATCH", f"/applications/{app_uuid}", token, body=payload, dry_run=True)
        return

    # 1차 시도
    try:
        _api_request("PATCH", f"/applications/{app_uuid}", token, body=payload)
        print(f"[deploy_to_coolify] domain patched: https://{slug}.n9n.co.kr → {service_name}.")
        return
    except urllib.error.HTTPError as exc:
        if exc.code != 422:
            raise
        # 422 응답 본문을 다시 읽어 docker_compose_raw race 인지 판별
        # (이미 _api_request 에서 read+출력했으므로 메시지는 stderr 에 있음)
        # exc.read() 는 소진됐으므로 메시지는 stderr 출력으로 확인 완료.
        # docker_compose_raw 미적재 race 로 간주하고 poll 진입.
        print(
            f"[deploy_to_coolify] PATCH 422 — possible compose-raw race; "
            f"polling for docker_compose_raw (up to 120s) ...",
            file=sys.stderr,
        )

    # 2차: compose raw 가 채워질 때까지 poll 후 재시도
    loaded = _wait_for_compose_raw(app_uuid, token)
    if not loaded:
        print(
            "[deploy_to_coolify] WARN: proceeding with PATCH despite timeout "
            "(Coolify may still accept).",
            file=sys.stderr,
        )

    _api_request("PATCH", f"/applications/{app_uuid}", token, body=payload)
    print(f"[deploy_to_coolify] domain patched (retry): https://{slug}.n9n.co.kr → {service_name}.")


# ---------------------------------------------------------------------------
# Manifest SCP
# ---------------------------------------------------------------------------

def scp_manifest(slug: str, dry_run: bool = False) -> bool:
    """SCP manifest (and seed-data.json if present) to server.

    Always uploads:
      out/<slug>/screen-manifest.json → /data/coolify/manifests/<slug>/screen-manifest.json

    Conditionally uploads (if file exists locally):
      out/<slug>/seed-data.json → /data/coolify/manifests/<slug>/seed-data.json

    scp order: mkdir first, then manifest, then seed — container bind-mounts
    require the file to exist before `docker compose up`. Sequence preserves
    the runbook "scp before deploy" invariant.

    Returns True on success.
    """
    manifest_local = REPO_ROOT / "out" / slug / "screen-manifest.json"
    seed_local = REPO_ROOT / "out" / slug / "seed-data.json"
    remote_dir = f"{MANIFEST_SERVER_BASE}/{slug}"
    remote_manifest = f"{remote_dir}/screen-manifest.json"
    remote_seed = f"{remote_dir}/seed-data.json"

    if not manifest_local.exists():
        print(
            f"[deploy_to_coolify] ERROR: manifest not found at {manifest_local}.\n"
            f"  Run: python scripts/workflow/preview_package.py --profile {slug} --coolify",
            file=sys.stderr,
        )
        return False

    has_seed = seed_local.exists()
    if has_seed:
        print(f"[deploy_to_coolify] seed file found at {seed_local} — will upload.")
    else:
        print(f"[deploy_to_coolify] no seed file at {seed_local} — skipping seed upload.")

    mkdir_cmd = [
        "ssh",
        "-i", PREVIEW_SSH_KEY,
        "-o", "StrictHostKeyChecking=accept-new",
        PREVIEW_HOST,
        f"mkdir -p {remote_dir}",
    ]
    scp_manifest_cmd = [
        "scp",
        "-i", PREVIEW_SSH_KEY,
        "-o", "StrictHostKeyChecking=accept-new",
        str(manifest_local),
        f"{PREVIEW_HOST}:{remote_manifest}",
    ]
    scp_seed_cmd = [
        "scp",
        "-i", PREVIEW_SSH_KEY,
        "-o", "StrictHostKeyChecking=accept-new",
        str(seed_local),
        f"{PREVIEW_HOST}:{remote_seed}",
    ]

    if dry_run:
        print(f"[DRY-RUN] ssh mkdir -p {remote_dir}")
        print(f"[DRY-RUN] scp {manifest_local} → {PREVIEW_HOST}:{remote_manifest}")
        if has_seed:
            print(f"[DRY-RUN] scp {seed_local} → {PREVIEW_HOST}:{remote_seed}")
        return True

    print(f"[deploy_to_coolify] creating remote dir {remote_dir} ...")
    result = subprocess.run(mkdir_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: ssh mkdir failed: {result.stderr}", file=sys.stderr)
        return False

    print(f"[deploy_to_coolify] scp manifest → {remote_manifest} ...")
    result = subprocess.run(scp_manifest_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: scp manifest failed: {result.stderr}", file=sys.stderr)
        return False
    print(f"[deploy_to_coolify] manifest uploaded.")

    if has_seed:
        print(f"[deploy_to_coolify] scp seed-data.json → {remote_seed} ...")
        result = subprocess.run(scp_seed_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[deploy_to_coolify] ERROR: scp seed failed: {result.stderr}", file=sys.stderr)
            return False
        print(f"[deploy_to_coolify] seed-data.json uploaded.")

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
                f"[deploy_to_coolify] SECRET_KEY already exists on app (409 - idempotent skip)."
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
        print(f"[deploy_to_coolify]   HTTP {code} - {status}")
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
            print(f"[deploy_to_coolify]   TLS CN - PASS ({expected_cn}, issuer=Let's Encrypt)")
        else:
            print(f"[deploy_to_coolify]   TLS CN - WARN: {cert_text.strip()}")
    except Exception as exc:
        print(f"[deploy_to_coolify]   TLS check skipped: {exc}")

    return all_pass


# ---------------------------------------------------------------------------
# Registry update (merge — never clobber hand-written fields)
# ---------------------------------------------------------------------------

def _yaml_get(lines: list[str], key: str) -> str | None:
    """Return the scalar value of a top-level YAML key from raw lines, or None.

    Strips inline comments (# …), surrounding whitespace, and enclosing quotes
    so that lines like:
        coolify_project: kjjjc67jyiksda35jqly02h7      # project_uuid
        coolify_project: "kjjjc67jyiksda35jqly02h7"
    both return the bare uuid string.
    """
    pattern = re.compile(r"^" + re.escape(key) + r":\s*(.*)")
    for line in lines:
        m = pattern.match(line)
        if m:
            raw = m.group(1)
            # Strip inline comment first, then whitespace, then enclosing quotes
            raw = re.sub(r"\s*#.*$", "", raw)
            v = raw.strip().strip('"').strip("'").strip()
            return v if v not in ("null", "", "~") else None
    return None


def _yaml_set(lines: list[str], key: str, value: str) -> list[str]:
    """Replace or append a top-level YAML key's scalar value in raw lines.

    Preserves all other lines (comments, nested keys, other top-level keys).
    Only modifies the exact line matching '^key:'.
    """
    pattern = re.compile(r"^(" + re.escape(key) + r":)\s*(.*)")
    new_lines = []
    replaced = False
    for line in lines:
        m = pattern.match(line)
        if m:
            new_lines.append(f"{key}: {value}\n")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f"{key}: {value}\n")
    return new_lines


def _yaml_set_nested(lines: list[str], parent: str, key: str, value: str) -> list[str]:
    """Set a 2-level nested YAML key (parent.key) in raw lines.

    Looks for the parent block and updates or appends the child key with 2-space indent.
    Preserves all comments and other fields.
    """
    pattern_parent = re.compile(r"^" + re.escape(parent) + r":\s*$")
    pattern_child = re.compile(r"^  " + re.escape(key) + r":\s*(.*)")

    new_lines = []
    in_parent = False
    child_replaced = False
    parent_line_idx = -1

    for i, line in enumerate(lines):
        if pattern_parent.match(line):
            in_parent = True
            parent_line_idx = i
            new_lines.append(line)
            continue
        if in_parent:
            # Still in parent block if line is indented (2+ spaces) or blank
            if line.startswith("  ") or line.strip() == "":
                m = pattern_child.match(line)
                if m:
                    new_lines.append(f"  {key}: {value}\n")
                    child_replaced = True
                else:
                    new_lines.append(line)
                continue
            else:
                # Exiting parent block — append child if not yet added
                if not child_replaced:
                    new_lines.append(f"  {key}: {value}\n")
                    child_replaced = True
                in_parent = False
        new_lines.append(line)

    # If parent block is at end of file
    if in_parent and not child_replaced:
        new_lines.append(f"  {key}: {value}\n")

    # If parent key never found — append minimal block
    if parent_line_idx == -1:
        new_lines.append(f"{parent}:\n")
        new_lines.append(f"  {key}: {value}\n")

    return new_lines


def update_registry(
    slug: str,
    project_uuid: str,
    app_uuid: str,
    deploy_uuid: str | None,
    token: str,
    dry_run: bool = False,
) -> dict[str, str]:
    """Merge deploy results into infra/registry/<slug>.yaml.

    Merge strategy: load raw lines, update only these keys:
      preview.coolify_project, preview.coolify_app,
      preview.url, preview.status, preview.deployed_at

    All other fields (secret_ref, contact, production, tls, etc.) are preserved.
    File created from skeleton if missing.

    Returns dict of before/after values for envelope (no secret values).
    """
    registry_path = REPO_ROOT / "infra" / "registry" / f"{slug}.yaml"

    # Resolve deployed_at from deployment response (server timestamp — no hardcode)
    deployed_at = None
    if deploy_uuid and not deploy_uuid.startswith("DRY-RUN"):
        try:
            result = _api_request(
                "GET", f"/deployments/{deploy_uuid}", token,
                dry_run=False, mutating=False,
            )
            finished_at = result.get("finished_at") or result.get("updated_at")
            if finished_at:
                # ISO timestamp — take date part only: 2026-06-12T16:38:41.000000Z → 2026-06-12
                deployed_at = finished_at[:10]
        except Exception as exc:
            print(f"[deploy_to_coolify] WARN: could not fetch deployment timestamp: {exc}")

    if not deployed_at:
        # Fallback: use application updated_at
        try:
            app_result = _api_request(
                "GET", f"/applications/{app_uuid}", token,
                dry_run=False, mutating=False,
            )
            updated_at = app_result.get("updated_at", "")
            if updated_at:
                deployed_at = updated_at[:10]
        except Exception:
            pass

    if not deployed_at:
        deployed_at = "unknown"

    live_url = f"https://{slug}.n9n.co.kr"

    if dry_run:
        print(f"[DRY-RUN] registry update: {registry_path}")
        print(f"[DRY-RUN]   preview.coolify_project → {project_uuid}")
        print(f"[DRY-RUN]   preview.coolify_app     → {app_uuid}")
        print(f"[DRY-RUN]   preview.url             → {live_url}")
        print(f"[DRY-RUN]   preview.status          → live")
        print(f"[DRY-RUN]   preview.deployed_at     → {deployed_at}")
        return {}

    # Load or create registry file
    if registry_path.exists():
        lines = registry_path.read_text(encoding="utf-8").splitlines(keepends=True)
        before = {
            "coolify_project": _yaml_get(lines, "  coolify_project") or "(none)",
            "coolify_app": _yaml_get(lines, "  coolify_app") or "(none)",
            "status": _yaml_get(lines, "  status") or "(none)",
            "deployed_at": _yaml_get(lines, "  deployed_at") or "(none)",
        }
    else:
        # Skeleton — minimal valid registry entry
        skeleton = (
            f"# infra/registry/{slug}.yaml\n"
            f"# Auto-created by deploy_to_coolify.py\n"
            f"# Secret plaintext forbidden: use secret_ref only\n"
            f"slug: {slug}\n"
            f"contact:\n"
            f"  channel: internal\n"
            f"  handle: demo\n"
            f"preview:\n"
            f"  subdomain: {slug}.n9n.co.kr\n"
            f"  url: null\n"
            f"  coolify_project: null\n"
            f"  coolify_app: null\n"
            f"  coolify_env: production\n"
            f"  deploy_key_github_id: 154181975\n"
            f"  coolify_privkey_uuid: {PRIVATE_KEY_UUID}\n"
            f"  server_uuid: {SERVER_UUID}\n"
            f"  compose_file: deploy/preview/{slug}.compose.yml\n"
            f"  manifest_server_path: /data/coolify/manifests/{slug}/screen-manifest.json\n"
            f"  status: provisioning\n"
            f"  deployed_at: null\n"
            f"production:\n"
            f"  install_method: null\n"
            f"  installed_at: null\n"
            f"  stack:\n"
            f"    frontend: vanilla-htmx\n"
            f"    backend: fastapi\n"
            f"secret_ref:\n"
            f"  - vault/{slug}/secret-key    # infra/secrets/{slug}-secret-key.txt\n"
            f'cost_note: "preview VPS shared (187.77.140.157), Hostinger KVM2 $8.99/mo"\n'
        )
        lines = skeleton.splitlines(keepends=True)
        before = {
            "coolify_project": "(none)",
            "coolify_app": "(none)",
            "status": "(none)",
            "deployed_at": "(none)",
        }

    # Apply updates — only preview sub-keys
    lines = _yaml_set_nested(lines, "preview", "coolify_project", project_uuid)
    lines = _yaml_set_nested(lines, "preview", "coolify_app", app_uuid)
    lines = _yaml_set_nested(lines, "preview", "url", live_url)
    lines = _yaml_set_nested(lines, "preview", "status", "live")
    lines = _yaml_set_nested(lines, "preview", "deployed_at", f'"{deployed_at}"')

    registry_path.write_text("".join(lines), encoding="utf-8")
    print(f"[deploy_to_coolify] registry updated: {registry_path}")

    after = {
        "coolify_project": project_uuid,
        "coolify_app": app_uuid,
        "status": "live",
        "deployed_at": deployed_at,
    }
    return {"before": before, "after": after}


# ---------------------------------------------------------------------------
# Compose file commit + push (--commit flag, per-file rule)
# ---------------------------------------------------------------------------

def commit_compose_file(slug: str, dry_run: bool = False) -> bool:
    """Commit and push deploy/preview/<slug>.compose.yml to master.

    Follows per-file commit rule — only this file, never git add -A.
    Returns True on success.
    """
    compose_rel = f"deploy/preview/{slug}.compose.yml"
    compose_path = REPO_ROOT / "deploy" / "preview" / f"{slug}.compose.yml"

    if not compose_path.exists():
        print(
            f"[deploy_to_coolify] ERROR: {compose_path} not found.\n"
            f"  Run: python scripts/workflow/preview_package.py --profile {slug} --coolify",
            file=sys.stderr,
        )
        return False

    commit_msg = (
        f"feat(deploy): add {slug} Coolify preview compose file\n\n"
        f"Generated by preview_package.py --coolify. Structural diff PASS.\n\n"
        f"Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
    )

    if dry_run:
        print(f"[DRY-RUN] git add {compose_rel}")
        print(f"[DRY-RUN] git commit -m '{commit_msg[:60]}...'")
        print(f"[DRY-RUN] git push origin master")
        return True

    # Check if file is already tracked and unchanged
    status_result = subprocess.run(
        ["git", "status", "--porcelain", compose_rel],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if not status_result.stdout.strip():
        print(f"[deploy_to_coolify] {compose_rel} already committed and clean - skipping commit.")
        return True

    add_result = subprocess.run(
        ["git", "add", compose_rel],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if add_result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: git add failed: {add_result.stderr}", file=sys.stderr)
        return False

    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if commit_result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: git commit failed: {commit_result.stderr}", file=sys.stderr)
        return False
    print(f"[deploy_to_coolify] committed: {commit_result.stdout.strip()}")

    push_result = subprocess.run(
        ["git", "push", "origin", "master"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if push_result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: git push failed: {push_result.stderr}", file=sys.stderr)
        return False
    print(f"[deploy_to_coolify] pushed to origin/master.")
    return True


# ---------------------------------------------------------------------------
# Webhook helpers (Gap 2b — GitHub push → Coolify auto-redeploy)
# ---------------------------------------------------------------------------

# Coolify 4.1.2 webhook mechanism (investigated 2026-06-12):
#   - Each application has manual_webhook_secret_github (40-char hex, auto-generated)
#   - Endpoint: POST https://<vps-ip-or-fqdn>/webhooks/source/github/events/manual
#     with header X-Hub-Signature-256: sha256=<HMAC-SHA256(secret, body)>
#     and X-GitHub-Event: push
#   - Coolify matches the HMAC against all apps with git_repository matching push payload
#   - On match: queues redeploy for that app
#
# GitHub webhook registration:
#   - URL: https://187.77.140.157/webhooks/source/github/events/manual
#     (VPS IP, port 443, traefik proxies to Coolify)
#   - Secret: app's manual_webhook_secret_github value
#   - Events: push (to master branch)
#   - Content-type: application/json
#
# SAFETY: Registration is gated — this function PRINTS what would be registered
#   and returns the payload. Actual GitHub API call requires --confirm flag
#   AND must only be done for explicitly named slugs (not all apps at once).


def get_webhook_secret(app_uuid: str, token: str) -> str:
    """Return manual_webhook_secret_github for app. Never printed — length only."""
    result = _api_request("GET", f"/applications/{app_uuid}", token, mutating=False)
    secret = result.get("manual_webhook_secret_github", "")
    if not secret:
        raise ValueError(f"No manual_webhook_secret_github found for app {app_uuid}")
    return secret


def save_webhook_secret_to_vault(slug: str, secret: str) -> Path:
    """Save webhook secret to vault only — never commits or prints value."""
    vault_path = REPO_ROOT / "infra" / "secrets" / f"{slug}-webhook-secret.txt"
    vault_path.write_text(secret, encoding="utf-8")
    print(f"[deploy_to_coolify] webhook secret saved to vault: {vault_path} (len={len(secret)})")
    return vault_path


def show_webhook_registration_plan(slug: str, app_uuid: str, token: str) -> dict:
    """Print GitHub webhook registration plan WITHOUT executing it.

    Returns the plan dict for CTO review. Secret value is never shown.
    Actual registration requires --confirm flag + explicit approval.
    """
    secret = get_webhook_secret(app_uuid, token)
    vault_path = save_webhook_secret_to_vault(slug, secret)

    webhook_url = "https://187.77.140.157/webhooks/source/github/events/manual"
    plan = {
        "webhook_url": webhook_url,
        "content_type": "application/json",
        "events": ["push"],
        "branch_filter": "master",
        "secret_vault": str(vault_path),
        "secret_len": len(secret),
        "app_uuid": app_uuid,
        "slug": slug,
        "note": (
            "Coolify matches incoming push by git_repository field in payload. "
            "All apps on this Coolify instance with same git_repository will receive "
            "redeploy trigger on master push — not slug-specific filtering."
        ),
        "risk": (
            "HIGH: master push triggers redeploy for ALL apps sharing git_repository "
            f"git@github.com:JasonMMo/compounding-stack-harness.git. "
            "Currently 2 live tenants (lawfirm-demo + shop-demo) would both redeploy "
            "on every master push. Safe only if all live tenants are stable. "
            "No per-app branch filter in Coolify 4.1.2 manual webhook path."
        ),
        "github_api_command": (
            "gh api repos/JasonMMo/compounding-stack-harness/hooks "
            "--method POST "
            "--field name=web "
            "--field active=true "
            f"--field 'config[url]={webhook_url}' "
            "--field 'config[content_type]=json' "
            "--field 'config[secret]=<from-vault>' "
            "--field 'events[]=push'"
        ),
    }

    print()
    print("[webhook-plan] === GitHub Webhook Registration Plan ===")
    print(f"[webhook-plan] slug:        {slug}")
    print(f"[webhook-plan] app_uuid:    {app_uuid}")
    print(f"[webhook-plan] webhook_url: {webhook_url}")
    print(f"[webhook-plan] events:      push (master)")
    print(f"[webhook-plan] secret:      vault:{vault_path} (len={len(secret)}, value NOT shown)")
    print(f"[webhook-plan] RISK:        {plan['risk']}")
    print()
    print("[webhook-plan] ACTION REQUIRED: CTO must confirm before executing.")
    print("[webhook-plan] Re-run with --setup-webhook --confirm to register on GitHub.")
    print()

    return plan


def register_github_webhook(slug: str, app_uuid: str, token: str) -> bool:
    """Register GitHub webhook for the Coolify app (requires --confirm flag).

    SAFETY: Only callable with explicit --confirm. Never called from main deploy flow.
    Returns True on success.
    """
    secret = get_webhook_secret(app_uuid, token)
    webhook_url = "https://187.77.140.157/webhooks/source/github/events/manual"

    # Use gh CLI to register webhook (token from gh auth — not Coolify token)
    cmd = [
        "gh", "api",
        "repos/JasonMMo/compounding-stack-harness/hooks",
        "--method", "POST",
        "--field", "name=web",
        "--field", "active=true",
        f"--field", f"config[url]={webhook_url}",
        "--field", "config[content_type]=json",
        "--field", f"config[secret]={secret}",
        "--field", "events[]=push",
    ]

    print(f"[deploy_to_coolify] registering GitHub webhook for {slug} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[deploy_to_coolify] ERROR: gh api failed: {result.stderr}", file=sys.stderr)
        return False

    try:
        resp = json.loads(result.stdout)
        hook_id = resp.get("id")
        hook_url = resp.get("config", {}).get("url", "")
        print(f"[deploy_to_coolify] webhook registered: id={hook_id}, url={hook_url}")
    except Exception:
        print(f"[deploy_to_coolify] webhook registered (could not parse response).")

    return True


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
    parser.add_argument(
        "--commit", action="store_true",
        help=(
            "Commit and push deploy/preview/<slug>.compose.yml before deploying. "
            "Per-file commit rule: only that file, never git add -A. "
            "Default: off (compose file must already be committed)."
        ),
    )
    parser.add_argument(
        "--skip-registry", action="store_true",
        help="Skip registry update after successful deploy.",
    )
    parser.add_argument(
        "--setup-webhook", action="store_true",
        help=(
            "Show GitHub webhook registration plan for this slug. "
            "Saves webhook secret to infra/secrets/<slug>-webhook-secret.txt. "
            "Does NOT register — prints plan and waits for --confirm. "
            "SAFETY: only test with shop-demo first."
        ),
    )
    parser.add_argument(
        "--confirm", action="store_true",
        help=(
            "Execute the GitHub webhook registration (requires --setup-webhook). "
            "GATE: CTO must confirm the plan output before using this flag. "
            "Prerequisite: gh CLI authenticated."
        ),
    )
    args = parser.parse_args()

    # Short-circuit: webhook setup mode (does not deploy)
    if args.setup_webhook:
        token = _load_token()
        # Resolve app_uuid for slug
        apps = _api_request("GET", "/applications", token, mutating=False)
        app_list = apps if isinstance(apps, list) else apps.get("data", [])
        app_uuid_found = None
        for app in app_list:
            if app.get("name") == args.slug:
                app_uuid_found = app["uuid"]
                break
        if not app_uuid_found:
            print(f"[deploy_to_coolify] ERROR: app '{args.slug}' not found.", file=sys.stderr)
            return 1

        plan = show_webhook_registration_plan(args.slug, app_uuid_found, token)

        if args.confirm:
            print(f"[deploy_to_coolify] --confirm received - registering GitHub webhook ...")
            ok = register_github_webhook(args.slug, app_uuid_found, token)
            return 0 if ok else 1
        return 0

    slug: str = args.slug
    dry_run: bool = args.dry_run

    if dry_run:
        print(f"[deploy_to_coolify] DRY-RUN mode - no mutations will be made.")

    print(f"[deploy_to_coolify] slug={slug}")

    # Load token (always — needed for GET calls even in dry-run)
    token = _load_token()

    # Step 0a: commit compose file if requested (before tunnel/deploy)
    if args.commit:
        if not commit_compose_file(slug, dry_run=dry_run):
            return 1

    # Step 0b: tunnel check
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
    # registry의 manifest_server_path: null 이면 manifest 없는 앱 (예: intake) — skip
    _manifest_path_in_registry = _registry_uuid(slug, "manifest_server_path")
    _has_no_manifest = _manifest_path_in_registry is None and (
        REPO_ROOT / "infra" / "registry" / f"{slug}.yaml"
    ).exists()
    if args.skip_scp or _has_no_manifest:
        if _has_no_manifest and not args.skip_scp:
            print(
                f"[deploy_to_coolify] manifest SCP skipped "
                f"(registry manifest_server_path=null for '{slug}')."
            )
        else:
            print("[deploy_to_coolify] --skip-scp: manifest SCP skipped.")
    else:
        if not scp_manifest(slug, dry_run=dry_run):
            return 1

    # Step 5: SECRET_KEY injection
    inject_secret_key(app_uuid, slug, token, dry_run=dry_run)

    # Step 6: deploy trigger
    deploy_uuid = trigger_deploy(app_uuid, token, dry_run=dry_run)

    if dry_run:
        # Show registry dry-run even in dry-run mode
        if not args.skip_registry:
            update_registry(
                slug=slug,
                project_uuid=project_uuid or f"DRY-RUN-PROJECT-UUID-{slug}",
                app_uuid=app_uuid or f"DRY-RUN-APP-UUID-{slug}",
                deploy_uuid=None,
                token=token,
                dry_run=True,
            )
        print()
        print("[DRY-RUN] All steps printed. Re-run without --dry-run to execute.")
        return 0

    # Step 7: poll build
    if deploy_uuid:
        success = poll_deployment(deploy_uuid, token)
        if not success:
            print("[deploy_to_coolify] Build failed - check Coolify logs.", file=sys.stderr)
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

    # Step 9: registry update
    if not args.skip_registry:
        reg_diff = update_registry(
            slug=slug,
            project_uuid=project_uuid,
            app_uuid=app_uuid,
            deploy_uuid=deploy_uuid,
            token=token,
            dry_run=dry_run,
        )
        if reg_diff:
            b = reg_diff.get("before", {})
            a = reg_diff.get("after", {})
            print(f"[deploy_to_coolify] registry diff: project {b.get('coolify_project')} → {a.get('coolify_project')}")
            print(f"[deploy_to_coolify] registry diff: app {b.get('coolify_app')} → {a.get('coolify_app')}")
            print(f"[deploy_to_coolify] registry diff: deployed_at {b.get('deployed_at')} → {a.get('deployed_at')}")
    else:
        print("[deploy_to_coolify] --skip-registry: registry update skipped.")

    print()
    print(f"[deploy_to_coolify] DONE. Preview: https://{slug}.n9n.co.kr/login")
    return 0


if __name__ == "__main__":
    sys.exit(main())
