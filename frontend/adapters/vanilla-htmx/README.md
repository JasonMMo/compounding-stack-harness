# Frontend Adapter: vanilla-htmx

Python/Flask thin server + htmx UI. Serves all 6 screens defined in
`docs/architecture/frontend-adapter-contract.md`, reverse-proxies `/api/*`
to any backend adapter, consumes design tokens from `design/tokens/`.

## Wire Key → Screen Mapping

| Wire key        | Screen route                               | Notes                                      |
|-----------------|--------------------------------------------|--------------------------------------------|
| auth.login      | GET/POST `/login`                          | Stores token in Flask session              |
| auth.logout     | POST `/logout`                             | Clears session, proxies logout to backend  |
| entity.list     | GET `/entities/<entity_type>`              | Offset paging default; cursor mode toggle (F-2) |
| entity.read     | GET `/entities/<entity_type>/<id>`         | Detail/edit form                           |
| entity.update   | POST `/entities/<entity_type>/<id>/edit`   | PATCH to backend; re-renders form on error |
| entity.create   | GET/POST `/entities/<entity_type>/new`     | Generic field form                         |
| entity.delete   | GET `/entities/<entity_type>/<id>/delete`  | Two-step confirm screen                    |
| entity.delete   | POST `/entities/<entity_type>/<id>/delete` | Dispatches DELETE; F-4 idempotent          |
| status.health   | GET `/health`                              | Optional; shows backend health             |

## How to Run

Requirements: Python 3.11+, pip.

```bash
# From this directory
pip install -r requirements.txt

# Build CSS tokens first (L3 build step)
python build_tokens.py

# Launch the thin server
python server.py
```

Default port: `5000`. Override with the `FRONTEND_PORT` env var.

Backend must be running at `http://localhost:8080` (default).
Override with the `BACKEND_BASE_URL` env var.

Single-command launch example:

```bash
BACKEND_BASE_URL=http://localhost:8080 FRONTEND_PORT=5000 python server.py
```

## How to Test

```bash
# L1 unit tests (contract_loader + CSS generator)
pytest tests/ -v

# L3 build check (generate tokens.css, exit 0 on success)
python build_tokens.py
```

For L4 live compliance (F-1~F-4), start both adapters and point QA suite at them:

```
FRONTEND_BASE_URL=http://localhost:5000
BACKEND_BASE_URL=http://localhost:8080
```

## Contract Loading (G-1 Compliance)

`contract_loader.py` reads `middle/contract/wire-v1.yaml` and
`middle/contract/error/codes.yaml` at server startup.

Resolution order for the contract directory:

1. `CONTRACT_DIR` env var (absolute path to `middle/contract/`)
2. Auto-detection: walks upward from `contract_loader.py` looking for
   `middle/contract/` — works when run from any directory inside the repo.

No endpoint paths, error code strings, or HTTP status integers are
hardcoded in adapter Python source — this satisfies the G-1 single-source
principle, mirroring `ContractLoader.java` in the backend adapter.

## CSS Token Generation (Design Token Consumption)

`token_css_generator.py` reads `design/tokens/raw.json`,
`design/tokens/semantic.json`, and `design/tokens/persona/*.json` and
emits `static/css/tokens.css`.

Generator rules (per `design/tokens/README.md`):

| Rule | Implementation |
|------|----------------|
| raw.json → `--raw-*` variables | `_flatten_raw()` walker |
| `{dot.path}` references resolved against raw.json | `_resolve_ref()` |
| semantic.json → `--*` variables (no prefix) | `_flatten_semantic()` |
| persona overrides → `[data-persona="<name>"]` scoped block | `_flatten_persona()` |
| Strip `_meta`, `_density`, `note`, `_*` keys | `_STRIP_KEYS` + `key.startswith("_")` |
| Font shorthand keys skipped (doc hints only) | `_FONT_SHORTHAND_KEYS` guard |

`app.css` consumes only `var(--*)` tokens — zero raw hex values.
`build_tokens.py` is the L3 build step.

## Compliance Points (F-1 ~ F-4)

| # | Point | Implementation |
|---|-------|----------------|
| **F-1** | Flat-underscore query params | `entity_list` route builds `paging_mode`, `paging_page`, `paging_size`, `paging_cursor`, `sort_field`, `sort_direction` as flat keys in the `params` dict passed to `_proxy_request`. |
| **F-2** | Offset + cursor paging | `entity_list` reads `paging_mode` from query string; renders offset pagination bar or cursor "Load more" button. `next_cursor` from response is forwarded as `paging_cursor` in the next request URL. |
| **F-3** | Error envelope rendering | `_render_error()` branches on `error.code` (never on message text). Calls `loader.message_ko(code)` to get the Korean message from `codes.yaml`. `retriable` codes render a retry hint. Auth codes redirect to login. |
| **F-4** | Idempotent delete | `_proxy_request()` maps HTTP 404 on DELETE method to `{"success": True, status: 200}`. The delete success template renders the same "삭제 완료" page for both first-call and second-call. |

## Known Gaps

| Gap | Reason | Future Growth |
|-----|--------|---------------|
| htmx inline partial updates not used for list refresh | Full page reload on htmx nav is simpler for M1 demo; htmx partials add complexity without a partial-response backend contract | Growth-N: partial rendering once wire supports `HX-Request` headers |
| No CSRF protection on POST forms | Flask dev mode only; production must add `flask-wtf` or custom CSRF token | Growth-N: security hardening |
| Session stored in cookie (client-side) | Flask default; sufficient for M1 demo auth | Growth-N: server-side session store |
| Persona persisted only in JS (localStorage not used) | `data-persona` set on `<html>` via select widget; page reload resets to default `ops` | Growth-N: persist persona in session or localStorage |
| No real DDL schema for create form fields | Generic key/value row form; backend accepts any field map | Growth-N: DDL-axis integration |
| cursor paging "Load more" appends to same page | Does not accumulate rows in DOM (redirects to new URL with cursor) | Growth-N: htmx hx-swap="beforeend" for true infinite scroll |

## Auth Demo Credentials

Matches backend adapter defaults:

```
username: demo
password: demo
```

POST to `/login` → session token stored → all entity routes accessible.
