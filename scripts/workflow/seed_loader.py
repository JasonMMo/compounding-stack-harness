"""seed_loader.py — load a declarative demo/test seed into a running backend adapter.

Loads profiles/seed/<slug>.seed.yaml by POSTing each record through the
wire-v1 entity.create key (POST /api/entities/<entity_type>). It does NOT touch
the adapter's store directly — data enters only through the contract (G-1).

Why a loader (design note):
  The in-memory store assigns server-side UUID ids on create; clients cannot set
  `id`, and FK columns are validated against the store. So the seed cannot bake
  static FK UUIDs — it declares records in dependency order with symbolic
  `ref:` names, and FK fields use {"$ref": "<name>"}. This loader resolves each
  $ref to the id the store returned for that ref. Result: a declarative,
  reusable, contract-honest fixture.

Adapter-agnostic: any backend exposing wire-v1 auth.login + entity.create can be
  targeted (fastapi today, springboot tomorrow) via --base-url.

Usage:
  # backend running on :8081 (fastapi default)
  python scripts/workflow/seed_loader.py --slug smallmfg-demo --base-url http://localhost:8081

  # dry-run: resolve refs + validate ordering without POSTing
  python scripts/workflow/seed_loader.py --slug smallmfg-demo --dry-run

Exit codes:
  0 — all records created (or dry-run resolved cleanly)
  1 — load error (auth failed, HTTP error, unresolved $ref, backend down)
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Seed file loader
# ---------------------------------------------------------------------------

def load_seed(slug: str) -> dict[str, Any]:
    """Read profiles/seed/<slug>.seed.yaml (read-only)."""
    path = REPO_ROOT / "profiles" / "seed" / f"{slug}.seed.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or "records" not in data:
        raise ValueError(f"Seed {slug}.seed.yaml missing top-level 'records' list.")
    return data


# ---------------------------------------------------------------------------
# $ref resolution
# ---------------------------------------------------------------------------

def resolve_refs(value: Any, ref_ids: dict[str, str]) -> Any:
    """Recursively replace {"$ref": "<name>"} with the resolved id string.

    Raises KeyError if a $ref names a ref that has not yet been created.
    """
    if isinstance(value, dict):
        if "$ref" in value and len(value) == 1:
            name = value["$ref"]
            if name not in ref_ids:
                raise KeyError(name)
            return ref_ids[name]
        return {k: resolve_refs(v, ref_ids) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_refs(v, ref_ids) for v in value]
    return value


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only — mirrors compliance test request style)
# ---------------------------------------------------------------------------

def _request(
    base_url: str, method: str, path: str, body: dict | None = None, token: str | None = None
) -> tuple[int, dict]:
    url = base_url.rstrip("/") + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        status = exc.code
    except urllib.error.URLError as exc:
        raise ConnectionError(f"backend unreachable at {base_url}: {exc.reason}") from exc
    try:
        parsed = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        parsed = {"_raw": raw}
    return status, parsed


def login(base_url: str, username: str, password: str) -> str:
    status, body = _request(
        base_url, "POST", "/api/auth/login",
        body={"username": username, "password": password},
    )
    if status != 200 or "token" not in body:
        raise RuntimeError(f"auth.login failed (status={status}): {body}")
    return body["token"]


# ---------------------------------------------------------------------------
# Core load
# ---------------------------------------------------------------------------

def load(slug: str, base_url: str, dry_run: bool = False) -> int:
    seed = load_seed(slug)
    records: list[dict] = seed.get("records", [])
    if not records:
        print("ERROR: seed has no records.", file=sys.stderr)
        return 1

    print(f"seed_loader — slug: {slug}  records: {len(records)}  dry_run: {dry_run}")

    token: str | None = None
    if not dry_run:
        auth = seed.get("auth", {})
        try:
            token = login(base_url, auth.get("username", "demo"), auth.get("password", "demo"))
        except (RuntimeError, ConnectionError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print(f"  authenticated (token acquired) against {base_url}")

    ref_ids: dict[str, str] = {}
    created = 0

    for idx, rec in enumerate(records):
        entity = rec.get("entity")
        ref = rec.get("ref")
        raw_data = rec.get("data", {})
        if not entity:
            print(f"ERROR: record #{idx} missing 'entity'.", file=sys.stderr)
            return 1

        # Resolve $ref placeholders against ids created so far (dependency order).
        try:
            data = resolve_refs(raw_data, ref_ids)
        except KeyError as missing:
            print(
                f"ERROR: record #{idx} (entity={entity}, ref={ref}) references "
                f"unresolved $ref {missing} — check dependency ordering.",
                file=sys.stderr,
            )
            return 1

        if dry_run:
            print(f"  [{idx:02d}] {entity:<20} ref={ref}  data-keys={list(data.keys())}")
            if ref:
                ref_ids[ref] = f"<dry-{ref}>"
            continue

        status, body = _request(
            base_url, "POST", f"/api/entities/{entity}",
            body={"entity_type": entity, "data": data}, token=token,
        )
        if status != 201 or "id" not in body:
            print(
                f"ERROR: entity.create failed for record #{idx} (entity={entity}, ref={ref}) "
                f"status={status}: {json.dumps(body, ensure_ascii=False)}",
                file=sys.stderr,
            )
            return 1

        new_id = body["id"]
        if ref:
            ref_ids[ref] = new_id
        created += 1
        print(f"  [{idx:02d}] {entity:<20} ref={ref:<18} -> id={new_id}")

    if dry_run:
        print(f"dry-run OK — {len(ref_ids)} refs resolvable in order, no records POSTed.")
    else:
        print(f"seed load complete — {created} records created via entity.create.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Load profiles/seed/<slug>.seed.yaml into a running backend via the wire contract."
    )
    parser.add_argument("--slug", required=True, help="Seed slug (e.g. smallmfg-demo).")
    parser.add_argument(
        "--base-url", default="http://localhost:8081",
        help="Backend adapter base URL. Default: http://localhost:8081 (fastapi).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Resolve refs + validate ordering without POSTing or authenticating.",
    )
    args = parser.parse_args(argv)

    try:
        return load(args.slug, args.base_url, dry_run=args.dry_run)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
