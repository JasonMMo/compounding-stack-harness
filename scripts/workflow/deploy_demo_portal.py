"""
deploy_demo_portal.py -- Deploy demo-portal static site to Coolify.

Target: demo.n9n.co.kr (nginx static HTML)
Compose: deploy/preview/demo-portal.compose.yml

Usage:
  python scripts/workflow/deploy_demo_portal.py
"""
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
API_BASE = "http://localhost:8000/api/v1"
SLUG = "demo-portal"
DOMAIN = "https://demo.n9n.co.kr"
GIT_REPO = "git@github.com:JasonMMo/compounding-stack-harness.git"
GIT_BRANCH = "master"
COMPOSE_LOCATION = "/deploy/preview/demo-portal.compose.yml"
PRIVATE_KEY_UUID = "s127pafarr46wlu1r2mre2te"


def _load_token() -> str:
    token_file = REPO_ROOT / "infra" / "secrets" / "coolify_api_token"
    raw = token_file.read_bytes().replace(b"\r", b"").replace(b"\n", b"").strip()
    token = raw.decode("ascii")
    print(f"[demo-portal] token loaded (len={len(token)}).")
    return token


def _api(method: str, path: str, token: str, body: dict | None = None) -> dict:
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        try:
            err = json.loads(body_bytes)
        except Exception:
            err = body_bytes.decode(errors="replace")
        print(f"[demo-portal] HTTP {e.code} on {method} {url}: {err}")
        return {}


def main() -> int:
    token = _load_token()

    # 1. Check tunnel
    try:
        urllib.request.urlopen(f"{API_BASE}/version", timeout=5)
    except urllib.error.HTTPError:
        pass  # 401 is fine
    except Exception as e:
        print(f"[demo-portal] tunnel check failed: {e}")
        return 1
    print("[demo-portal] tunnel: alive.")

    # 2. Create project
    proj = _api("POST", "/projects", token, {
        "name": SLUG,
        "description": "Demo portal landing page",
    })
    proj_uuid = proj.get("uuid", "")
    if not proj_uuid:
        # Try to find existing
        projects = _api("GET", "/projects", token)
        for p in (projects if isinstance(projects, list) else []):
            if p.get("name") == SLUG:
                proj_uuid = p["uuid"]
                break
    if not proj_uuid:
        print("[demo-portal] ERROR: could not create/find project.")
        return 1
    print(f"[demo-portal] project uuid={proj_uuid}.")

    # 3. Create application
    payload = {
        "type": "public",
        "name": SLUG,
        "project_uuid": proj_uuid,
        "server_uuid": "mwgsocco840cws8wssocg4w4",
        "environment_name": "production",
        "git_repository": GIT_REPO,
        "git_branch": GIT_BRANCH,
        "build_pack": "dockercompose",
        "docker_compose_location": COMPOSE_LOCATION,
        "private_key_uuid": PRIVATE_KEY_UUID,
        "instant_deploy": False,
    }
    app = _api("POST", "/applications/private-deploy-key", token, payload)
    app_uuid = app.get("uuid", "")
    if not app_uuid:
        # Already exists?
        apps = _api("GET", "/applications", token)
        app_list = apps if isinstance(apps, list) else apps.get("data", [])
        for a in app_list:
            if a.get("name") == SLUG:
                app_uuid = a["uuid"]
                break
    if not app_uuid:
        print("[demo-portal] ERROR: could not create/find app.")
        return 1
    print(f"[demo-portal] app uuid={app_uuid}.")

    # 4. Wait for compose raw then patch domain
    for attempt in range(1, 25):
        time.sleep(5)
        check = _api("GET", f"/applications/{app_uuid}", token)
        if check.get("docker_compose_raw"):
            break
        print(f"[demo-portal] waiting for compose raw... (attempt={attempt})")

    domain_payload = [{"name": "portal", "domain": DOMAIN}]
    patch = _api("PATCH", f"/applications/{app_uuid}", token,
                 {"docker_compose_domains": json.dumps(domain_payload)})
    if patch:
        print(f"[demo-portal] domain patched: {DOMAIN} -> portal.")

    # 5. Deploy
    deploy = _api("POST", f"/applications/{app_uuid}/deploy", token,
                  {"force": False})
    dep_uuid = deploy.get("deployment_uuid", "")
    if not dep_uuid:
        print("[demo-portal] ERROR: deploy did not return deployment_uuid.")
        return 1
    print(f"[demo-portal] deploy queued: {dep_uuid}.")

    # 6. Poll
    for _ in range(60):
        time.sleep(5)
        status_resp = _api("GET", f"/deployments/{dep_uuid}", token)
        status = status_resp.get("status", "unknown")
        print(f"[demo-portal]   status={status}")
        if status == "finished":
            break
        if status in ("failed", "cancelled", "error"):
            print("[demo-portal] build FAILED.")
            return 1

    print(f"[demo-portal] DONE. Preview: {DOMAIN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
