"""
ui_check.py -- Tier-1 deterministic UI defect checker (LLM 0).

Usage:
  python scripts/workflow/ui_check.py --base-url https://shop-demo.n9n.co.kr --slug shop-demo
  python scripts/workflow/ui_check.py --base-url http://localhost:8080 --slug dev-test \
      --manifest out/shop-demo/screen-manifest.json --out docs/intake-inbox/ui-checks/

Integration point (Phase 4 / intake_sync.py):
  After deploy_to_coolify.py exits 0, call:
    subprocess.run(
        [sys.executable, "scripts/workflow/ui_check.py",
         "--base-url", base_url, "--slug", slug,
         "--manifest", manifest_path, "--out", "docs/intake-inbox/ui-checks/"],
        check=False,
    )
  Non-zero rc=2 is a tool error; rc=0 always (even FAIL verdict) -- soft gate.
  Read the written JSON report for verdict field to decide "live-ui-warn" flag.

Graceful degradation:
  If `playwright` is not installed, browser-based checks (screenshot, console errors,
  overflow) are skipped.  HTTP and asset checks still run.  The report includes
  "playwright_available": false and a WARN result noting the skip.

Viewport matrix (Tier-1 MVP):
  desktop: 1366x768
  mobile:  390x844  (iPhone-like)

Screenshot storage:
  apps/intake/data-mirror/ui-shots/<slug>/  (gitignored -- PII-free screenshots only)

Report storage:
  docs/intake-inbox/ui-checks/<slug>.json  (PII-free, committed)

Exit codes:
  0  Normal completion (even when verdict=FAIL -- soft gate)
  2  Tool error (bad args, manifest unreadable, output dir unwritable)
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
import threading
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Playwright optional import
# ---------------------------------------------------------------------------
try:
    from playwright.sync_api import sync_playwright  # type: ignore

    PLAYWRIGHT_AVAILABLE = True
except ImportError:  # noqa: BLE001
    PLAYWRIGHT_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VIEWPORT_MATRIX = [
    {"name": "desktop", "width": 1366, "height": 768},
    {"name": "mobile", "width": 390, "height": 844},
]

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    check: str
    status: str  # "PASS" | "WARN" | "FAIL"
    detail: str
    viewport: Optional[str] = None

    def __post_init__(self) -> None:
        if self.status not in ("PASS", "WARN", "FAIL"):
            raise ValueError(f"Invalid status: {self.status!r}")


# ---------------------------------------------------------------------------
# Path derivation
# ---------------------------------------------------------------------------


def derive_check_paths(manifest: dict, entry_path: str = "/login") -> list[str]:
    """Return de-duped list of URL paths to check.

    Always includes ``entry_path`` (the app's UI landing page; default /login
    for the fullstack demo scaffold, '/' for apps with no login such as intake).
    Adds one path per entity key (ASCII slug, PII-free) from the manifest's
    ``entities`` map.

    Shape assumed:
      manifest["entities"] = {"<entity-key>": {...}, ...}

    Entity paths use the key directly as a slug segment, e.g.
    entity key "sales-order" -> path "/sales-order".
    """
    if not entry_path.startswith("/"):
        entry_path = "/" + entry_path
    paths: list[str] = [entry_path]
    entities: dict = manifest.get("entities", {})
    for key in entities:
        # Guard: entity keys must be ASCII (G-8)
        safe_key = key.encode("ascii", errors="replace").decode("ascii")
        candidate = f"/{safe_key}"
        if candidate not in paths:
            paths.append(candidate)
    return paths


# ---------------------------------------------------------------------------
# HTTP checks (stdlib only)
# ---------------------------------------------------------------------------


# Auth-gated / SPA codes that are EXPECTED on an entity path when the checker is
# unauthenticated: the entity views are served as htmx partials behind login, so a
# top-level GET legitimately returns 401/403 (auth) or 404 (no top-level route).
# These are advisory (WARN), not defects. 5xx (server error) is always a real FAIL.
_AUTH_GATED_CODES = frozenset({401, 403, 404})


def check_http(
    base_url: str, paths: list[str], entry_path: str = "/login"
) -> list[CheckResult]:
    """GET each path. Entry path is strict (4xx/5xx FAIL). Entity paths treat
    401/403/404 as WARN (auth-gated/htmx-partial route — expected unauthenticated)
    and only 5xx as FAIL. 2xx/3xx is always PASS."""
    if not entry_path.startswith("/"):
        entry_path = "/" + entry_path
    results: list[CheckResult] = []
    base = base_url.rstrip("/")
    for path in paths:
        url = base + path
        is_entry = path == entry_path
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                code = resp.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception as exc:  # noqa: BLE001
            results.append(
                CheckResult(
                    check=f"http:{path}",
                    status="FAIL",
                    detail=f"Connection error: {exc}",
                )
            )
            continue

        if 200 <= code < 400:
            results.append(
                CheckResult(check=f"http:{path}", status="PASS", detail=f"HTTP {code}")
            )
        elif not is_entry and code in _AUTH_GATED_CODES:
            results.append(
                CheckResult(
                    check=f"http:{path}",
                    status="WARN",
                    detail=f"HTTP {code} (auth-gated/htmx-partial entity route — "
                    f"expected for an unauthenticated check)",
                )
            )
        else:
            results.append(
                CheckResult(check=f"http:{path}", status="FAIL", detail=f"HTTP {code}")
            )
    return results


# ---------------------------------------------------------------------------
# Screenshot + console error + overflow checks (Playwright)
# ---------------------------------------------------------------------------


def screenshot_and_check(
    base_url: str,
    paths: list[str],
    viewports: list[dict],
    out_dir: Path,
    entry_path: str = "/login",
) -> list[CheckResult]:
    """Browser-based checks via Playwright sync API.

    For each (path, viewport):
    - Capture console error-level messages -> FAIL (entry path) / WARN (entity path)
    - Check document.scrollWidth > viewport.width + 1 -> FAIL (horizontal overflow)
    - Save screenshot PNG to out_dir

    Console errors on an entity path are advisory: the unauthenticated checker hits
    a login redirect / 404 shell, so its console noise is not a defect of the
    delivered app. The entry path stays strict.

    Returns empty list (with a WARN noting unavailability) if Playwright not installed.
    """
    if not entry_path.startswith("/"):
        entry_path = "/" + entry_path
    if not PLAYWRIGHT_AVAILABLE:
        return [
            CheckResult(
                check="browser:playwright",
                status="WARN",
                detail="playwright package not installed; browser checks skipped. "
                "Run: pip install playwright && playwright install chromium",
            )
        ]

    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[CheckResult] = []
    base = base_url.rstrip("/")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for vp in viewports:
                vp_name = vp["name"]
                vp_w = vp["width"]
                vp_h = vp["height"]
                context = browser.new_context(
                    viewport={"width": vp_w, "height": vp_h}
                )
                try:
                    for path in paths:
                        url = base + path
                        is_entry = path == entry_path
                        page = context.new_page()
                        console_errors: list[str] = []

                        def _on_console(msg: object, _path: str = path) -> None:  # noqa: ANN001
                            if getattr(msg, "type", "") == "error":
                                console_errors.append(str(getattr(msg, "text", msg)))

                        page.on("console", _on_console)
                        try:
                            page.goto(url, wait_until="networkidle", timeout=20_000)
                        except Exception as exc:  # noqa: BLE001
                            results.append(
                                CheckResult(
                                    check=f"browser:load:{path}",
                                    status="FAIL",
                                    detail=f"Page load error: {exc}",
                                    viewport=vp_name,
                                )
                            )
                            page.close()
                            continue

                        # Console error check — strict on entry, advisory on entity paths
                        if console_errors:
                            results.append(
                                CheckResult(
                                    check=f"browser:console:{path}",
                                    status="FAIL" if is_entry else "WARN",
                                    detail=(
                                        f"Console errors: {console_errors[:3]}"
                                        if is_entry
                                        else f"Console errors on auth-gated/htmx-partial "
                                        f"entity route (advisory): {console_errors[:3]}"
                                    ),
                                    viewport=vp_name,
                                )
                            )
                        else:
                            results.append(
                                CheckResult(
                                    check=f"browser:console:{path}",
                                    status="PASS",
                                    detail="No console errors",
                                    viewport=vp_name,
                                )
                            )

                        # Horizontal overflow check
                        scroll_w: int = page.evaluate("document.documentElement.scrollWidth")
                        if scroll_w > vp_w + 1:
                            results.append(
                                CheckResult(
                                    check=f"browser:overflow:{path}",
                                    status="FAIL",
                                    detail=f"scrollWidth {scroll_w} > viewport {vp_w}",
                                    viewport=vp_name,
                                )
                            )
                        else:
                            results.append(
                                CheckResult(
                                    check=f"browser:overflow:{path}",
                                    status="PASS",
                                    detail=f"scrollWidth {scroll_w} <= viewport {vp_w}",
                                    viewport=vp_name,
                                )
                            )

                        # Screenshot
                        safe_path = path.strip("/") or "root"
                        shot_name = f"{vp_name}_{safe_path.replace('/', '_')}.png"
                        shot_path = out_dir / shot_name
                        page.screenshot(path=str(shot_path), full_page=False)
                        page.close()
                finally:
                    context.close()
        finally:
            browser.close()

    return results


# ---------------------------------------------------------------------------
# Asset integrity check
# ---------------------------------------------------------------------------


def check_assets(base_url: str, path: str = "/login") -> list[CheckResult]:
    """Parse page HTML for <img>/<link>/<script> src/href; HEAD each; FAIL on 4xx."""
    import html.parser

    base = base_url.rstrip("/")
    url = base + path
    results: list[CheckResult] = []

    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            html_bytes = resp.read()
    except Exception as exc:  # noqa: BLE001
        return [
            CheckResult(
                check="assets:fetch-page",
                status="FAIL",
                detail=f"Could not fetch {path}: {exc}",
            )
        ]

    html_text = html_bytes.decode("utf-8", errors="replace")

    class _AssetParser(html.parser.HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.assets: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            attr_map = dict(attrs)
            if tag == "img":
                src = attr_map.get("src")
            elif tag == "link":
                src = attr_map.get("href")
            elif tag == "script":
                src = attr_map.get("src")
            else:
                src = None
            if src and src.startswith(("http://", "https://", "/")):
                self.assets.append(src)

    parser = _AssetParser()
    parser.feed(html_text)

    for asset in parser.assets:
        asset_url = asset if asset.startswith("http") else base + asset
        try:
            req = urllib.request.Request(asset_url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                code = resp.status
        except urllib.error.HTTPError as exc:
            code = exc.code
        except Exception as exc:  # noqa: BLE001
            results.append(
                CheckResult(
                    check=f"asset:{asset}",
                    status="FAIL",
                    detail=f"Connection error: {exc}",
                )
            )
            continue

        if code >= 400:
            results.append(
                CheckResult(check=f"asset:{asset}", status="FAIL", detail=f"HTTP {code}")
            )
        else:
            results.append(
                CheckResult(check=f"asset:{asset}", status="PASS", detail=f"HTTP {code}")
            )

    if not parser.assets:
        results.append(
            CheckResult(
                check="assets:scan",
                status="WARN",
                detail=f"No external assets found on {path}",
            )
        )

    return results


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------


def write_report(results: list[CheckResult], slug: str, out_path: Path) -> dict:
    """Write PII-free JSON report to out_path.

    Report shape:
      {slug, generated_at, playwright_available, viewport_matrix, results:[...], verdict}

    verdict: FAIL if any FAIL, else WARN if any WARN, else PASS.
    Returns the report dict.
    """
    statuses = {r.status for r in results}
    if "FAIL" in statuses:
        verdict = "FAIL"
    elif "WARN" in statuses:
        verdict = "WARN"
    else:
        verdict = "PASS"

    report = {
        "slug": slug,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "viewport_matrix": [
            f"{vp['name']}:{vp['width']}x{vp['height']}" for vp in VIEWPORT_MATRIX
        ],
        "results": [asdict(r) for r in results],
        "verdict": verdict,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


# ---------------------------------------------------------------------------
# Vision-review request emitter (--full-vision, LLM 0)
# ---------------------------------------------------------------------------

_RUBRIC_REPO_PATH = "design/vision-qa-rubric.yaml"
_VISION_REQUEST_SUFFIX = "-vision-request.json"


def _emit_vision_review_request(
    slug: str,
    shot_dir: Path,
    out_dir: Path,
) -> Path:
    """Collect captured screenshots and emit a vision-review-request.json.

    No LLM calls are made here.  The file is a handoff artefact for CDO/QA
    who will open each screenshot in zai-mcp analyze_image and score against
    the rubric.

    Output: docs/intake-inbox/ui-checks/<slug>-vision-request.json
    Schema (PII-free):
      {
        "slug": "<slug>",
        "generated_by": "ui_check --full-vision",
        "generated_at": "<ISO-8601 UTC>",
        "screenshots": [
          {"page": "<path>", "viewport": "<desktop|mobile>", "path": "<abs-path>"}
        ],
        "rubric": "design/vision-qa-rubric.yaml",
        "reference_shots_dir": "design/references/<slug>/"  (omitted when absent),
        "instructions": "CDO/QA: open each screenshot with zai-mcp analyze_image, score rubric criteria, write verdict to docs/intake-inbox/ui-checks/<slug>-vision-verdict.json"
      }

    When no screenshots exist the list is empty and a WARNING is printed.
    """
    screenshots: list[dict] = []

    if shot_dir.exists():
        # Collect PNG files grouped by viewport inferred from filename prefix.
        for png in sorted(shot_dir.glob("*.png")):
            name = png.name  # e.g. desktop_login.png, mobile_root.png
            if name.startswith("desktop_"):
                viewport = "desktop"
                page_slug = name[len("desktop_"):][:-4].replace("_", "/")
                page_path = f"/{page_slug}" if page_slug else "/"
            elif name.startswith("mobile_"):
                viewport = "mobile"
                page_slug = name[len("mobile_"):][:-4].replace("_", "/")
                page_path = f"/{page_slug}" if page_slug else "/"
            else:
                viewport = "unknown"
                page_path = f"/{name[:-4]}"
            screenshots.append({
                "page": page_path,
                "viewport": viewport,
                "path": str(png),
            })

    if not screenshots:
        print(
            f"WARNING: --full-vision: no screenshots found in {shot_dir}. "
            "Run ui_check.py without --full-vision first (requires Playwright) "
            "to capture screenshots, then re-run with --full-vision.",
            file=sys.stderr,
        )

    # Optional: reference shots directory for theme diff
    rubric_ref = _REPO_ROOT / "design" / "references" / slug
    request: dict = {
        "slug": slug,
        "generated_by": "ui_check --full-vision",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "screenshots": screenshots,
        "rubric": _RUBRIC_REPO_PATH,
        "instructions": (
            f"CDO/QA: open each screenshot with zai-mcp analyze_image, "
            f"score rubric criteria from {_RUBRIC_REPO_PATH}, "
            f"write verdict to docs/intake-inbox/ui-checks/{slug}-vision-verdict.json"
        ),
    }
    if rubric_ref.exists():
        request["reference_shots_dir"] = str(rubric_ref)

    out_dir.mkdir(parents=True, exist_ok=True)
    request_path = out_dir / f"{slug}{_VISION_REQUEST_SUFFIX}"
    request_path.write_text(
        json.dumps(request, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return request_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Exit codes:
      0  Normal (even when verdict=FAIL -- soft gate)
      2  Tool error (bad args / unreadable manifest / unwritable out dir)
    """
    parser = argparse.ArgumentParser(
        prog="ui_check.py",
        description="Tier-1 deterministic UI defect checker (LLM 0).",
    )
    parser.add_argument("--base-url", required=True, help="Base URL of the deployed preview")
    parser.add_argument("--slug", required=True, help="Customer/profile slug (ASCII, PII-free)")
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to screen-manifest.json (optional; enables entity path derivation)",
    )
    parser.add_argument(
        "--entry-path",
        default="/login",
        help=(
            "App UI entry path (default /login for the fullstack demo scaffold). "
            "Apps with no login page (e.g. the intake app) serve their entry at '/' "
            "— pass --entry-path / to avoid a false-negative 404."
        ),
    )
    parser.add_argument(
        "--out",
        default=str(_REPO_ROOT / "docs" / "intake-inbox" / "ui-checks"),
        help="Output directory for JSON report (default: docs/intake-inbox/ui-checks/)",
    )
    parser.add_argument(
        "--full-vision",
        action="store_true",
        default=False,
        help=(
            "Generate a vision-review-request.json alongside the normal report. "
            "Collects captured screenshots and the rubric path; LLM calls = 0. "
            "CDO/QA reads the request and runs zai-mcp analyze_image to score."
        ),
    )
    args = parser.parse_args(argv)

    # --- Load manifest if provided ---
    manifest: dict = {}
    if args.manifest:
        mpath = Path(args.manifest)
        if not mpath.exists():
            print(f"ERROR: manifest not found: {mpath}", file=sys.stderr)
            return 2
        try:
            manifest = json.loads(mpath.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: cannot parse manifest: {exc}", file=sys.stderr)
            return 2

    # --- Derive paths ---
    paths = derive_check_paths(manifest, entry_path=args.entry_path)

    # --- Screenshot output dir (gitignored) ---
    shot_dir = _REPO_ROOT / "apps" / "intake" / "data-mirror" / "ui-shots" / args.slug

    # --- Run checks ---
    all_results: list[CheckResult] = []

    # 1. HTTP status checks
    all_results.extend(check_http(args.base_url, paths, entry_path=args.entry_path))

    # 2. Asset integrity check
    all_results.extend(check_assets(args.base_url, paths[0]))

    # 3. Browser checks (Playwright; graceful degradation if unavailable)
    all_results.extend(
        screenshot_and_check(
            args.base_url, paths, VIEWPORT_MATRIX, shot_dir, entry_path=args.entry_path
        )
    )

    # --- Write report ---
    out_dir = Path(args.out)
    try:
        report_path = out_dir / f"{args.slug}.json"
        report = write_report(all_results, args.slug, report_path)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: cannot write report: {exc}", file=sys.stderr)
        return 2

    # --- Print summary ---
    verdict = report["verdict"]
    pass_n = sum(1 for r in all_results if r.status == "PASS")
    warn_n = sum(1 for r in all_results if r.status == "WARN")
    fail_n = sum(1 for r in all_results if r.status == "FAIL")
    print(
        f"ui_check [{args.slug}] verdict={verdict} "
        f"PASS={pass_n} WARN={warn_n} FAIL={fail_n}"
    )
    print(f"Report: {report_path}")
    if not PLAYWRIGHT_AVAILABLE:
        print(
            "NOTE: playwright unavailable -- browser checks skipped. "
            "pip install playwright && playwright install chromium"
        )
    if args.full_vision:
        vision_request_path = _emit_vision_review_request(
            slug=args.slug,
            shot_dir=shot_dir,
            out_dir=out_dir,
        )
        print(f"Vision-review request: {vision_request_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
