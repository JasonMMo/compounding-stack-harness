"""
deploy_static_site.py -- Deploy a static site (nginx / dockercompose) to Coolify.

Generalized from deploy_demo_portal.py. Used for the marketing-site preview lane:
landing demos and landing portals are static (no backend/db), so they cannot use
the business-system deploy_to_coolify.py path (screen-manifest + SECRET_KEY + /login).

Idempotent: reuses an existing project/app with the same --slug.

Usage:
  python scripts/workflow/deploy_static_site.py \
      --slug gtm-landing \
      --domain https://gtm-landing.n9n.co.kr \
      --compose /deploy/preview/gtm-landing.compose.yml \
      --service web

  python scripts/workflow/deploy_static_site.py \
      --slug landing-portal \
      --domain https://landing.n9n.co.kr \
      --compose /deploy/preview/landing-portal.compose.yml \
      --service portal

  add --dry-run to print the create payload without calling the API.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
API_BASE = "http://localhost:8000/api/v1"

# Reusable fixed assets (preview-deploy.md runbook — never regenerate)
SERVER_UUID = "n12vdydjpwp81hu5i15n1gsb"
PRIVATE_KEY_UUID = "s127pafarr46wlu1r2mre2te"
GIT_REPO = "git@github.com:JasonMMo/compounding-stack-harness.git"
GIT_BRANCH = "master"


def _load_token() -> str:
    token_file = REPO_ROOT / "infra" / "secrets" / "coolify_api_token"
    raw = token_file.read_bytes().replace(b"\r", b"").replace(b"\n", b"").strip()
    token = raw.decode("ascii")
    print(f"[deploy] token loaded (len={len(token)}).")
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
        print(f"[deploy] HTTP {e.code} on {method} {url}: {err}")
        return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deploy a static dockercompose site to Coolify.")
    parser.add_argument("--slug", required=True, help="Coolify project/app name (ASCII).")
    parser.add_argument("--domain", required=True, help="https://<sub>.n9n.co.kr")
    parser.add_argument("--compose", required=True,
                        help="Absolute (repo-rooted) docker_compose_location, e.g. /deploy/preview/<slug>.compose.yml")
    parser.add_argument("--service", required=True,
                        help="Compose service name that receives the domain (e.g. web / portal).")
    parser.add_argument("--description", default="", help="Project description.")
    parser.add_argument("--dry-run", action="store_true", help="Print create payload; no API calls.")
    args = parser.parse_args(argv)

    slug = args.slug
    payload = {
        "type": "public",
        "name": slug,
        "server_uuid": SERVER_UUID,
        "environment_name": "production",
        "git_repository": GIT_REPO,
        "git_branch": GIT_BRANCH,
        "build_pack": "dockercompose",
        "docker_compose_location": args.compose,
        "private_key_uuid": PRIVATE_KEY_UUID,
        "instant_deploy": False,
    }
    if args.dry_run:
        print(f"[deploy] DRY-RUN slug={slug} domain={args.domain} service={args.service}")
        print(json.dumps(payload, indent=2))
        return 0

    token = _load_token()

    # 1. Tunnel check
    try:
        urllib.request.urlopen(f"{API_BASE}/version", timeout=5)
    except urllib.error.HTTPError:
        pass  # 401 fine
    except Exception as e:
        print(f"[deploy] tunnel check failed: {e}")
        return 1
    print("[deploy] tunnel: alive.")

    # 2. Find or create project
    proj_uuid = ""
    projects = _api("GET", "/projects", token)
    for p in (projects if isinstance(projects, list) else []):
        if p.get("name") == slug:
            proj_uuid = p["uuid"]
            print(f"[deploy] project reused: {proj_uuid}.")
            break
    if not proj_uuid:
        proj = _api("POST", "/projects", token,
                    {"name": slug, "description": args.description or f"{slug} static site"})
        proj_uuid = proj.get("uuid", "")
    if not proj_uuid:
        print("[deploy] ERROR: could not create/find project.")
        return 1
    print(f"[deploy] project: {proj_uuid}.")

    # 3. Find or create application
    app_uuid = ""
    apps = _api("GET", "/applications", token)
    app_list = apps if isinstance(apps, list) else apps.get("data", [])
    for a in app_list:
        if a.get("name") == slug:
            app_uuid = a["uuid"]
            print(f"[deploy] app reused: {app_uuid}.")
            break
    if not app_uuid:
        payload["project_uuid"] = proj_uuid
        app = _api("POST", "/applications/private-deploy-key", token, payload)
        app_uuid = app.get("uuid", "")
    if not app_uuid:
        print("[deploy] ERROR: could not create/find app.")
        return 1
    print(f"[deploy] app: {app_uuid}.")

    # 4. Wait for compose raw, then patch domain (docker_compose_domains; fqdn PATCH = 422)
    for attempt in range(1, 25):
        time.sleep(5)
        check = _api("GET", f"/applications/{app_uuid}", token)
        if check.get("docker_compose_raw"):
            break
        print(f"[deploy] waiting for compose raw... (attempt={attempt})")

    patch = _api("PATCH", f"/applications/{app_uuid}", token,
                 {"docker_compose_domains": [{"name": args.service, "domain": args.domain}],
                  "force_domain_override": True})
    if patch:
        print(f"[deploy] domain patched: {args.domain} -> {args.service}.")

    time.sleep(3)

    # 5. Deploy (GET /start)
    deploy = _api("GET", f"/applications/{app_uuid}/start", token, body=None)
    dep_uuid = deploy.get("deployment_uuid") or deploy.get("uuid", "")
    if not dep_uuid:
        print("[deploy] ERROR: deploy did not return deployment_uuid.")
        return 1
    print(f"[deploy] deploy queued: {dep_uuid}.")

    # 6. Poll (static image builds can take a few minutes for the node+astro stage)
    for _ in range(90):
        time.sleep(5)
        status_resp = _api("GET", f"/deployments/{dep_uuid}", token)
        status = status_resp.get("status", "unknown")
        print(f"[deploy]   status={status}")
        if status == "finished":
            break
        if status in ("failed", "cancelled", "error"):
            print("[deploy] build FAILED — check Coolify deployment logs.")
            return 1

    print(f"[deploy] DONE. app={app_uuid} project={proj_uuid} url={args.domain}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
