# Frontend Adapter: react

Vite + React 18 + TypeScript SPA. Serves all 6 screens defined in
`docs/architecture/frontend-adapter-contract.md`, proxies `/api/*` to any
backend adapter, consumes design tokens from `design/tokens/`.

## Wire Key → Screen Mapping

| Wire key        | Screen route                                  | Notes                                              |
|-----------------|-----------------------------------------------|----------------------------------------------------|
| auth.login      | `/login`                                      | Stores token in sessionStorage                     |
| auth.logout     | navbar logout button                          | Clears sessionStorage, proxies logout to backend   |
| entity.list     | `/entities/:entityType`                       | Offset paging default; cursor mode toggle (F-2)    |
| entity.read     | `/entities/:entityType/:entityId`             | Detail/edit form                                   |
| entity.update   | POST from `/entities/:entityType/:entityId`   | PATCH to backend; re-renders form on error         |
| entity.create   | `/entities/:entityType/new`                   | Typed form from manifest or generic key/value form |
| entity.delete   | `/entities/:entityType/:entityId/delete`      | Two-step confirm screen; F-4 idempotent            |
| status.health   | `/health`                                     | Optional; shows backend health                     |

## How to Run

Requirements: Node v20+, npm 10+.

```bash
# From this directory — first time setup
npm install

# Build-time code generation (must run before build or dev)
npm run codegen        # emits src/contract/contract.gen.ts from wire-v1.yaml + codes.yaml
npm run build:tokens   # emits src/tokens/tokens.gen.css from design/tokens/*.json

# Start development server (runs codegen + build:tokens first via prebuild)
npm run dev

# Or use the combined prebuild then dev
npm run prebuild && npm run dev
```

Default port: `5173`. Override with the `FRONTEND_PORT` env var.

Backend must be running at `http://localhost:8080` (default).
Override with `BACKEND_BASE_URL` env var.

Single-command launch example (fastapi backend):

```bash
# Terminal 1: fastapi backend on port 8081
cd backend/adapters/fastapi && uvicorn main:app --port 8081

# Terminal 2: react adapter
BACKEND_BASE_URL=http://localhost:8081 FRONTEND_PORT=5173 npm run dev
```

## How to Test

```bash
# L1 unit tests (contract codegen + F-1/F-3/F-4 compliance)
# Run from repo root:
cd frontend/adapters/react && npm run codegen && npm test

# L3 build check (codegen + token build + vite build)
npm run build

# L4 live compliance (fastapi backend must be running):
BACKEND_BASE_URL=http://localhost:8081 npm test
```

## Contract Codegen (G-1 Compliance)

`scripts/codegen.mjs` reads `middle/contract/wire-v1.yaml` and
`middle/contract/error/codes.yaml` at **build time** and emits
`src/contract/contract.gen.ts`.

This generated module is the **only** place in the React adapter that
contains endpoint paths, error codes, HTTP status integers, or
flat-underscore paging key names. Components import from it — they never
hardcode contract values.

G-1 guard compliance: the generated file has each code key and its
`httpStatus` on **separate lines** in the emitted object, so
`diagnose.py G-1`'s same-line co-occurrence check does not fire.
`contract.gen.ts` is in `.gitignore` (generated artifact).

Resolution order for the contract directory:
1. `CONTRACT_DIR` env var → absolute or relative path to `middle/contract/`
2. Auto-detection: walks upward from `scripts/codegen.mjs` looking for
   `middle/contract/` — works from any directory inside the repo.

## CSS Token Generation (Design Token Consumption)

`scripts/build-tokens.mjs` reads `design/tokens/raw.json`,
`design/tokens/semantic.json`, and `design/tokens/persona/*.json` and
emits `src/tokens/tokens.gen.css`.

Generator rules (per `design/tokens/README.md`):

| Rule | Implementation |
|------|----------------|
| raw.json → `:root { --raw-* }` variables | `flattenRaw()` walker |
| `{dot.path}` references resolved against raw.json | `resolveRef()` |
| semantic.json → `:root { --* }` variables (no prefix) | `flattenSemantic()` |
| persona overrides → `[data-persona="<name>"]` scoped block | `flattenPersona()` |
| Strip `_meta`, `_density`, `note` keys | `STRIP_KEYS` set + `key.startsWith('_')` guard |
| Font shorthand keys skipped (doc hints only) | `FONT_SHORTHAND_KEYS` guard |

`app.css` consumes only `var(--*)` tokens — zero raw hex values.
`tokens.gen.css` is in `.gitignore` (generated artifact).

## Manifest Typed Forms (Growth-14)

`src/api/manifest.ts` fetches the screen-manifest at runtime from
`VITE_MANIFEST_URL` (default `/manifest.json`). To use:

```bash
# Copy the shop-demo manifest to public/ for the dev server to serve:
cp out/shop-demo/screen-manifest.json public/manifest.json
VITE_MANIFEST_URL=/manifest.json npm run dev
```

When the manifest is loaded, create/edit forms render typed fields
(`text`, `textarea`, `number`, `date`, `datetime`, `select`, `checkbox`,
`fk-text`). When absent, a generic key/value form is shown (backward
compatible, same as vanilla-htmx fallback).

## Compliance Points (F-1 ~ F-4)

| # | Point | Implementation |
|---|-------|----------------|
| **F-1** | Flat-underscore query params | `buildListParams()` in `src/api/wire.ts` constructs `paging_mode`, `paging_page`, `paging_size`, `paging_cursor`, `sort_field`, `sort_direction` as flat keys — key names imported from `contract.gen.ts::PAGING_KEYS / SORT_KEYS`. Never dot-notation in query strings. |
| **F-2** | Offset + cursor paging | `ListScreen` reads `paging_mode` from URL params; renders offset pagination bar or cursor "더 보기" button. `next_cursor` from response forwarded as `paging_cursor` in next request URL. |
| **F-3** | Error envelope rendering | `wireRequest()` branches on `error.code` (never message text). Calls `getMessageKo(code)` from `contract.gen.ts` to get Korean message. Retriable codes render a "다시 시도" button. Auth codes call `clearToken()` and redirect to `/login`. |
| **F-4** | Idempotent delete | `wireRequest()` with `isDelete: true` maps HTTP 404 to `{ success: true }` before returning. `DeleteScreen` also maps `NOT_FOUND` on the confirm GET to the success state. Both call paths render "삭제 완료". |

## Persona Support

Persona is managed via `data-persona` attribute on `<html>`. The navbar
select widget switches between `ops` (default), `ceo`, `it`. CSS token
overrides for each persona are in `tokens.gen.css` (sourced from
`design/tokens/persona/*.json`). M1 implements `ops` fully; `ceo` and
`it` receive CSS token overrides from the design system.

## Known Gaps

| Gap | Reason | Future Growth |
|-----|--------|---------------|
| cursor paging: rows not accumulated in DOM | SPA redirects to new URL with cursor; no infinite-scroll append | Growth-N: React state accumulation |
| No CSRF protection | Vite dev + preview mode only; production needs CSRF header | Growth-N: security hardening |
| Token stored in sessionStorage (not httpOnly cookie) | SPA constraint; sufficient for M1 demo | Growth-N: httpOnly cookie via BFF |
| Persona not persisted across page reload | `data-persona` reset to `ops` on reload | Growth-N: localStorage or server session |
| FK dropdown shows text input with hint | FK dropdown deferred (M1) per manifest note field | Growth-N: FK entity autocomplete |
| No real DDL schema validation | Generic in-memory backend; no catalog wired | Growth-N: DDL-axis integration |

## Auth Demo Credentials

Matches backend adapter defaults:

```
username: demo
password: demo
```

POST to `/login` → token stored in sessionStorage → all entity routes accessible.
