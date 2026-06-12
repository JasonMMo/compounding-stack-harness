"""
server.py — vanilla-htmx frontend adapter thin server.

Architecture B (frontend-adapter-contract.md §1):
  Browser → [this server] → (reverse proxy /api/*) → BACKEND_BASE_URL

Responsibilities:
  1. Serve HTML + htmx pages for all 6 screens (list / detail+edit / create /
     delete confirm / login / health).
  2. Reverse-proxy /api/* requests to the backend adapter at BACKEND_BASE_URL.
  3. Read wire-v1.yaml + codes.yaml at startup via contract_loader.py (G-1).
  4. Render wire responses including error envelopes (F-3: branch on error.code,
     display message_ko).
  5. Serialize paging/sort as flat-underscore in proxy requests (F-1).
  6. Support offset + cursor paging (F-2).
  7. Treat 404 on entity.delete as success (F-4 — idempotent delete).

Stack: Python 3.11+ stdlib + Flask (lightweight WSGI, no heavy deps).
Flask was chosen over stdlib http.server because:
  - Jinja2 templating is already bundled with Flask (zero extra deps).
  - URL routing and request parsing are trivial to write correctly.
  - Single pip install (flask), no build tool needed.
  - Consistent with pytest harness (Python-first repo).

Environment variables:
  BACKEND_BASE_URL   — where to reverse-proxy /api/* (default: http://localhost:8080)
  FRONTEND_PORT      — port to listen on (default: 5000)
  CONTRACT_DIR       — path to middle/contract/ (optional, auto-detected)
  SECRET_KEY         — Flask session secret (default: dev-insecure-change-me)
"""

import json
import logging
import os
import urllib.parse
import urllib.request
import urllib.error
from functools import wraps

from flask import (
    Flask,
    Response,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from contract_loader import get_loader
from manifest_loader import get_manifest_loader

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-insecure-change-me")

BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:8080").rstrip("/")
UI_THEME = os.environ.get("UI_THEME", "saas")  # saas | public-sector
# Comma-separated entity slugs that render in master-detail split layout.
# Example: MASTER_DETAIL_ENTITIES=contact,lead,invoice,document
_MD_ENTITIES: set[str] = {
    e.strip() for e in os.environ.get("MASTER_DETAIL_ENTITIES", "").split(",") if e.strip()
}


# ---------------------------------------------------------------------------
# Template context processor — inject manifest globals into every template
# ---------------------------------------------------------------------------

@app.context_processor
def _inject_manifest_globals() -> dict:
    """Make customer_display, feedback_url, domains and entity_keys available in all templates.

    This lets base.html render the nav brand, sidebar, and footer feedback CTA
    without each route handler passing the values explicitly.
    Routes that also pass these as explicit kwargs will override via the
    normal Jinja2 template variable precedence (explicit wins).

    g_domains  — list of {slug, display, entities[]} for sidebar domain groups.
                 Used by base.html sidebar block. Falls back to g_entity_keys
                 when empty (lawfirm-demo / manifests without domains key).
    g_entity_keys — flat entity key list for no-domains fallback sidebar.

    Security: g_domains and g_entity_keys are suppressed for unauthenticated
    requests so that menu structure (domain labels, entity names) is not
    exposed to anonymous visitors in the HTML response.
    """
    authenticated = bool(session.get("token"))
    if authenticated:
        domains = manifest.domains()
        entity_keys = manifest.entity_keys() if not domains else []
    else:
        domains = []
        entity_keys = []
    return {
        "g_customer_display": manifest.customer_display(),
        "g_feedback_url": manifest.feedback_url(),
        "g_domains": domains,
        "g_entity_keys": entity_keys,
        "g_authenticated": authenticated,
        "ui_theme": UI_THEME,
    }

# Load contract at startup (G-1 — reads wire-v1.yaml + codes.yaml)
loader = get_loader()
log.info("Frontend adapter ready. Wire contract version: %s", loader.wire_version())
log.info("Proxying /api/* to %s", BACKEND_BASE_URL)

# Load screen manifest at startup (Phase 2 — field-aware rendering).
# PROFILE_MANIFEST env var points to out/<profile>/screen-manifest.json.
# If unset or file missing, manifest_loader operates in no-manifest mode and
# the frontend falls back to generic key/value rendering (backward compat).
manifest = get_manifest_loader()
if manifest.is_loaded():
    log.info(
        "ManifestLoader: profile='%s', entities=%s",
        manifest.profile(),
        manifest.entity_keys(),
    )
else:
    log.info("ManifestLoader: no manifest — generic fallback rendering active.")


# ---------------------------------------------------------------------------
# Reverse proxy helper (F-1 / F-4 logic lives here)
# ---------------------------------------------------------------------------

def _proxy_request(
    method: str,
    path: str,
    params: dict | None = None,
    body: dict | None = None,
    token: str | None = None,
) -> tuple[dict, int]:
    """
    Forward a request to BACKEND_BASE_URL and return (parsed_json, status_code).

    F-1: paging/sort fields are already flat-underscore when callers build params
         (e.g. paging_mode, paging_page, sort_field). This function passes them
         through unchanged — the flat-underscore contract is enforced by callers.

    F-4: on entity.delete paths, a 404 from the backend is mapped to a synthetic
         success response here before returning to the caller.
    """
    url = f"{BACKEND_BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(
            {k: v for k, v in params.items() if v is not None and v != ""}
        )

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
    except urllib.error.URLError as exc:
        log.error("Proxy connection failed to %s: %s", BACKEND_BASE_URL, exc.reason)
        return {
            "error": {
                "code": "UNAVAILABLE",
                "message": loader.message_en("UNAVAILABLE"),
            }
        }, 503

    try:
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        payload = {"error": {"code": "INTERNAL", "message": "Invalid JSON from backend"}}

    # F-4: idempotent delete — treat 404 as success
    if status == 404 and method == "DELETE":
        log.info("F-4: entity.delete returned 404 — mapping to success (idempotent)")
        return {"success": True}, 200

    return payload, status


def _entity_path(entity_type: str, entity_id: str | None = None) -> str:
    if entity_id:
        return f"/api/entities/{entity_type}/{entity_id}"
    return f"/api/entities/{entity_type}"


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def _current_token() -> str | None:
    return session.get("token")


def _require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _current_token():
            return redirect(url_for("login_get"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Error rendering helper
# ---------------------------------------------------------------------------

def _render_error(payload: dict, status: int, entity_type: str = "") -> str | Response:
    """
    F-3: branch on error.code (never on message text).
    Render message_ko from codes.yaml.
    """
    err = payload.get("error") or {}
    code = err.get("code", "INTERNAL")
    message_ko = loader.message_ko(code)
    retriable = loader.is_retriable(code)
    details = err.get("details")

    # Auth errors redirect to login
    if code in ("AUTH_REQUIRED", "AUTH_EXPIRED"):
        session.clear()
        return redirect(url_for("login_get"))

    return render_template(
        "error.html",
        code=code,
        message_ko=message_ko,
        retriable=retriable,
        details=details,
        entity_type=entity_type,
        wire_version=loader.wire_version(),
    ), status


# ---------------------------------------------------------------------------
# Static assets
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if not _current_token():
        return redirect(url_for("login_get"))
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Home screen — personalised landing after login
# ---------------------------------------------------------------------------

@app.get("/home")
@_require_login
def home():
    """Render the post-login landing page.

    Shows customer.display heading + domain cards (with entity links).
    Falls back gracefully when no manifest is loaded (generic heading).
    """
    return render_template(
        "home.html",
        customer_display=manifest.customer_display(),
        domains=manifest.domains(),
        feedback_url=manifest.feedback_url(),
        wire_version=loader.wire_version(),
    )


# ---------------------------------------------------------------------------
# Login / Logout  (auth.login / auth.logout)
# ---------------------------------------------------------------------------

@app.get("/login")
def login_get():
    return render_template("login.html", wire_version=loader.wire_version())


@app.post("/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    remember_me = bool(request.form.get("remember_me"))

    payload, status = _proxy_request(
        "POST",
        "/api/auth/login",
        body={"username": username, "password": password, "remember_me": remember_me},
    )

    if payload.get("error"):
        err = payload["error"]
        code = err.get("code", "AUTH_FAILED")
        return render_template(
            "login.html",
            error=loader.message_ko(code),
            wire_version=loader.wire_version(),
        ), 401

    session["token"] = payload.get("token", "")
    session["user_id"] = payload.get("user_id", "")
    session["expires_at"] = payload.get("expires_at", "")
    return redirect(url_for("home"))


@app.post("/logout")
def logout():
    token = _current_token()
    if token:
        _proxy_request("POST", "/api/auth/logout", body={"token": token}, token=token)
    session.clear()
    return redirect(url_for("login_get"))


# ---------------------------------------------------------------------------
# Entity list  (entity.list — offset paging default, F-1/F-2)
# ---------------------------------------------------------------------------

@app.get("/entities/<entity_type>")
@_require_login
def entity_list(entity_type: str):
    # F-1: flat-underscore serialization for paging/sort
    paging_mode = request.args.get("paging_mode", "offset")
    paging_page = request.args.get("paging_page", "1")
    paging_size = request.args.get("paging_size", "20")
    paging_cursor = request.args.get("paging_cursor", "")
    sort_field = request.args.get("sort_field", "")
    sort_direction = request.args.get("sort_direction", "asc")
    search = request.args.get("search", "")

    # Build flat-underscore query params (F-1).
    # entity_type is part of the URL path, NOT a query param — sending it as a
    # query key makes the backend treat it as a record filter (entity.list
    # filters on any non-reserved key) and returns 0 rows. Paging keys must be
    # the contract's flat-underscore page/size/cursor (see _shared compliance
    # suite: page=, size=, paging_mode=, cursor=), not paging_page/paging_size.
    params: dict = {"paging_mode": paging_mode}
    if paging_mode == "offset":
        params["page"] = paging_page
        params["size"] = paging_size
    elif paging_mode == "cursor" and paging_cursor:
        params["cursor"] = paging_cursor
        params["size"] = paging_size

    if sort_field:
        params["sort_field"] = sort_field
        params["sort_direction"] = sort_direction
    if search:
        params["search"] = search

    payload, status = _proxy_request(
        "GET",
        _entity_path(entity_type),
        params=params,
        token=_current_token(),
    )

    if payload.get("error"):
        return _render_error(payload, status, entity_type)

    items = payload.get("items", [])
    total = payload.get("total", len(items))
    next_cursor = payload.get("next_cursor")  # F-2: cursor mode next page

    # Derive column names from first item (generic — entity_type drives shape)
    columns = list(items[0].keys()) if items else []

    # Pagination math (offset mode)
    page_int = int(paging_page) if paging_page.isdigit() else 1
    size_int = int(paging_size) if paging_size.isdigit() else 20
    total_pages = max(1, (total + size_int - 1) // size_int) if total else 1

    _tpl = "list-master-detail.html" if entity_type in _MD_ENTITIES else "list.html"
    return render_template(
        _tpl,
        entity_type=entity_type,
        items=items,
        columns=columns,
        total=total,
        paging_mode=paging_mode,
        paging_page=page_int,
        paging_size=size_int,
        total_pages=total_pages,
        next_cursor=next_cursor,
        sort_field=sort_field,
        sort_direction=sort_direction,
        search=search,
        entity_label=manifest.label(entity_type) or entity_type,
        wire_version=loader.wire_version(),
    )


# ---------------------------------------------------------------------------
# Entity detail / edit  (entity.read + entity.update)
# ---------------------------------------------------------------------------

@app.get("/entities/<entity_type>/<entity_id>")
@_require_login
def entity_detail(entity_type: str, entity_id: str):
    payload, status = _proxy_request(
        "GET",
        _entity_path(entity_type, entity_id),
        token=_current_token(),
    )
    if payload.get("error"):
        return _render_error(payload, status, entity_type)

    manifest_fields = manifest.entity_fields(entity_type)
    return render_template(
        "detail.html",
        entity_type=entity_type,
        entity_id=entity_id,
        data=payload.get("data", {}),
        manifest_fields=manifest_fields,
        hidden_fields=manifest.hidden_fields(entity_type),
        entity_label=manifest.label(entity_type) or entity_type,
        wire_version=loader.wire_version(),
    )


@app.post("/entities/<entity_type>/<entity_id>/edit")
@_require_login
def entity_update(entity_type: str, entity_id: str):
    # Collect all non-empty form fields as the patch data (skip hidden/system fields)
    hidden = set(manifest.hidden_fields(entity_type))
    data = {
        k: v
        for k, v in request.form.items()
        if k != "_method" and v != "" and k not in hidden
    }
    payload, status = _proxy_request(
        "PATCH",
        _entity_path(entity_type, entity_id),
        body={"entity_type": entity_type, "id": entity_id, "data": data},
        token=_current_token(),
    )
    if payload.get("error"):
        err = payload["error"]
        code = err.get("code", "INTERNAL")
        # Re-render detail form with error
        read_payload, _ = _proxy_request(
            "GET",
            _entity_path(entity_type, entity_id),
            token=_current_token(),
        )
        manifest_fields = manifest.entity_fields(entity_type)
        return render_template(
            "detail.html",
            entity_type=entity_type,
            entity_id=entity_id,
            data=read_payload.get("data", data),
            manifest_fields=manifest_fields,
            hidden_fields=manifest.hidden_fields(entity_type),
            entity_label=manifest.label(entity_type) or entity_type,
            error=loader.message_ko(code),
            error_details=err.get("details"),
            wire_version=loader.wire_version(),
        ), status

    return redirect(url_for("entity_detail", entity_type=entity_type, entity_id=entity_id))


# ---------------------------------------------------------------------------
# Entity create  (entity.create)
# ---------------------------------------------------------------------------

@app.get("/entities/<entity_type>/new")
@_require_login
def entity_create_form(entity_type: str):
    manifest_fields = manifest.entity_fields(entity_type)
    return render_template(
        "create.html",
        entity_type=entity_type,
        manifest_fields=manifest_fields,
        entity_label=manifest.label(entity_type) or entity_type,
        wire_version=loader.wire_version(),
    )


@app.post("/entities/<entity_type>/new")
@_require_login
def entity_create_post(entity_type: str):
    # hidden_fields are excluded from create POST (they are system-generated)
    hidden = set(manifest.hidden_fields(entity_type))
    data = {
        k: v
        for k, v in request.form.items()
        if v != "" and k not in hidden
    }
    payload, status = _proxy_request(
        "POST",
        _entity_path(entity_type),
        body={"entity_type": entity_type, "data": data},
        token=_current_token(),
    )
    if payload.get("error"):
        err = payload["error"]
        code = err.get("code", "INTERNAL")
        manifest_fields = manifest.entity_fields(entity_type)
        return render_template(
            "create.html",
            entity_type=entity_type,
            manifest_fields=manifest_fields,
            entity_label=manifest.label(entity_type) or entity_type,
            form_data=data,
            error=loader.message_ko(code),
            error_details=err.get("details"),
            wire_version=loader.wire_version(),
        ), status

    new_id = payload.get("id", "")
    return redirect(url_for("entity_detail", entity_type=entity_type, entity_id=new_id))


# ---------------------------------------------------------------------------
# Entity delete  (entity.delete — F-4 idempotent)
# ---------------------------------------------------------------------------

@app.get("/entities/<entity_type>/<entity_id>/delete")
@_require_login
def entity_delete_confirm(entity_type: str, entity_id: str):
    """Two-step confirm screen (button.md a11y: require confirmation before destructive action)."""
    # Read current data for the confirmation display
    payload, status = _proxy_request(
        "GET",
        _entity_path(entity_type, entity_id),
        token=_current_token(),
    )
    # If already gone, treat as success (F-4)
    if payload.get("error"):
        err_code = payload["error"].get("code", "")
        if err_code == "NOT_FOUND":
            return render_template(
                "delete_success.html",
                entity_type=entity_type,
                entity_id=entity_id,
                already_deleted=True,
                wire_version=loader.wire_version(),
            )
        return _render_error(payload, status, entity_type)

    return render_template(
        "delete_confirm.html",
        entity_type=entity_type,
        entity_id=entity_id,
        data=payload.get("data", {}),
        wire_version=loader.wire_version(),
    )


@app.post("/entities/<entity_type>/<entity_id>/delete")
@_require_login
def entity_delete_post(entity_type: str, entity_id: str):
    """
    Dispatch entity.delete.
    F-4: 404 from backend is already mapped to success in _proxy_request.
    """
    payload, status = _proxy_request(
        "DELETE",
        _entity_path(entity_type, entity_id),
        token=_current_token(),
    )

    if payload.get("error"):
        err = payload["error"]
        code = err.get("code", "INTERNAL")
        return render_template(
            "error.html",
            code=code,
            message_ko=loader.message_ko(code),
            retriable=loader.is_retriable(code),
            entity_type=entity_type,
            wire_version=loader.wire_version(),
        ), status

    # Success (including idempotent second-call success via F-4 mapping)
    return render_template(
        "delete_success.html",
        entity_type=entity_type,
        entity_id=entity_id,
        already_deleted=False,
        wire_version=loader.wire_version(),
    )


# ---------------------------------------------------------------------------
# Legal precedent search  (law-firm vertical — A안)
# ---------------------------------------------------------------------------

@app.get("/legal/search")
@_require_login
def legal_search():
    """
    Render the precedent full-text search screen.
    The actual search is done client-side via htmx → /api/legal/precedents/search.
    """
    return render_template(
        "legal_precedent_search.html",
        wire_version=loader.wire_version(),
    )


# ---------------------------------------------------------------------------
# Health  (status.health)
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    payload, status = _proxy_request(
        "GET",
        "/api/status/health",
        token=_current_token(),
    )
    return render_template(
        "health.html",
        health=payload,
        wire_version=loader.wire_version(),
    ), status


# ---------------------------------------------------------------------------
# Reverse proxy pass-through for raw /api/* calls from htmx
# ---------------------------------------------------------------------------

@app.route("/api/<path:subpath>", methods=["GET", "POST", "PATCH", "DELETE", "PUT"])
def api_proxy(subpath: str):
    """
    Pass-through proxy for htmx requests that go directly to /api/*.
    Injects the session token as Authorization header.
    F-1/F-4 rules apply: callers must already use flat-underscore params;
    DELETE 404 is mapped to success before returning.
    """
    target_url = f"{BACKEND_BASE_URL}/api/{subpath}"
    qs = request.query_string.decode("utf-8")
    if qs:
        target_url += "?" + qs

    headers = dict(request.headers)
    headers.pop("Host", None)
    token = _current_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = request.get_data() or None
    req = urllib.request.Request(
        target_url, data=data, headers=headers, method=request.method
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            status = resp.status
            content_type = resp.headers.get("Content-Type", "application/json")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        status = exc.code
        content_type = exc.headers.get("Content-Type", "application/json")
        # F-4: DELETE + 404 → synthetic success
        if request.method == "DELETE" and status == 404:
            log.info("F-4 proxy: DELETE 404 mapped to success")
            return Response(
                json.dumps({"success": True}),
                status=200,
                content_type="application/json",
            )
    except urllib.error.URLError as exc:
        error_body = json.dumps({
            "error": {"code": "UNAVAILABLE", "message": str(exc.reason)}
        })
        return Response(error_body, status=503, content_type="application/json")

    return Response(raw, status=status, content_type=content_type)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("FRONTEND_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    log.info("Starting vanilla-htmx frontend adapter on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
