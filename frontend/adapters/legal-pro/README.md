# Frontend Adapter: legal-pro

React 18 + Vite + TypeScript SPA for the unified legal product (법무 vertical, M3 flagship).
Bakes the `legal-pro` theme (navy `#0F1729` header / `#1A2744` primary + restrained gold `#B8960C` precedent badge).

Visually distinct from the vanilla-htmx adapter and the generic `react` adapter by design —
this is the premium B2B product face, not a generic harness demo.

## Stack

| Concern | Choice |
|---|---|
| UI framework | React 18 + react-router-dom v6 |
| Build tool | Vite 5 |
| Language | TypeScript 5 (strict) |
| Theme | `presets/themes/legal-pro/` (navy+gold) baked at build time |
| Backend | `services/legal-rag` FastAPI (self-host, no external CDN) |
| Auth | Email + JWT, sessionStorage (clears on tab close) |

## Directory Structure

```
legal-pro/
  index.html               — SPA shell (lang="ko", no CDN links)
  package.json
  vite.config.ts           — proxies /auth, /search, /health, /documents, /cases → backend
  tsconfig.json
  scripts/
    codegen.mjs            — emits src/contract/contract.gen.ts (legal-rag endpoints + error codes)
    build-tokens.mjs       — concatenates legal-pro theme CSS → src/tokens/tokens.gen.css
  src/
    main.tsx               — React root, imports tokens.gen.css
    App.tsx                — shell: navy header + routes (Login → PrecedentSearch)
    contract/
      contract.gen.ts      — GENERATED (gitignored) — legal-rag endpoints + error codes
    tokens/
      tokens.gen.css       — GENERATED (gitignored) — legal-pro baked theme CSS
    api/
      wire.ts              — typed fetch layer for legal-rag backend
      manifest.ts          — stub (Phase B: case-management forms)
    components/
      ErrorBanner.tsx      — F-3 error envelope renderer (code-branched, messageKo)
      TypedField.tsx        — typed form field (Phase B: case-management; unused in Phase A)
    screens/
      LoginScreen.tsx      — email+password auth, legal-pro card design
      PrecedentSearchScreen.tsx — precedent search (Phase A core)
```

## Phase Status

### Phase A — DONE

- Scaffold mirrors `frontend/adapters/react/` structure (package.json / vite.config.ts / tsconfig.json / codegen.mjs / build-tokens.mjs / contract layer / component stubs).
- legal-pro theme baked: `presets/themes/legal-pro/tokens.css` + `services/legal-rag/web/styles/app.css` bundled into `src/tokens/tokens.gen.css`.
- `PrecedentSearchScreen.tsx`: full port of `services/legal-rag/web/app.js` search behavior:
  - POST `/search` with `{ query, top_k, match_mode, case_id? }`
  - `CitationOut.relevance` → "관련도 N%" badge (not raw `rrf_score`)
  - Citation cards: 1:1 chunk binding (`chunk_id`), zero-hallucination rendering
  - Korean lexical match badges (`fts_rank != null` → "키워드 일치")
  - Word-match badge ("단어 N/M 일치") — excerpt-based
  - Search highlight: XSS-safe React `<mark>` insertion (no innerHTML)
  - AND/OR match mode segment toggle
  - Skeleton loading cards
  - Empty-query / no-results / error / 503 sidecar-down / 429 states
  - Health polling (30s interval → health banner)
- `LoginScreen.tsx`: email+password auth, legal-pro navy card with gold strip.
- `App.tsx`: Login → PrecedentSearch routing with auth guard.
- L3 build gate: `npm run build` passes (tsc + vite).

### Phase B — DEFERRED

Blocked on the following open gaps and questions. Do NOT implement until CTO resolves:

| ID | Blocker | Detail |
|---|---|---|
| G-1 | `/cases` endpoint | GET /cases not implemented in services/legal-rag |
| G-2 | `/cases/:id` endpoint | GET /cases/:id not implemented |
| G-3 | `/cases` mutation endpoints | POST/PATCH/DELETE /cases missing |
| G-4 | `CaseOut` schema | Not yet stabilised — Phase B schema changes risk adapter churn |
| G-5 | Role-based mutations | Policy for case create/edit by role (partner/associate) TBD |
| G-6 | RLS end-to-end for case-scoped search | `/search?case_id=` RLS isolation not end-to-end tested |
| Q-1 | Architecture question | Should Phase B case screens be in this SPA or a separate micro-frontend? |

Phase B TODO markers are present in `App.tsx` and `PrecedentSearchScreen.tsx`.

## How to Build and Run

Requirements: Node v20+, npm 10+.

```bash
# From this directory
npm install

# Build-time generation (contract.gen.ts + tokens.gen.css)
npm run codegen
npm run build:tokens

# Verify (L3 build gate — must succeed before deploy)
npm run build

# Development server (runs codegen + build:tokens via prebuild)
npm run dev
```

Default dev port: `5174` (distinct from generic react adapter on `5173`).
Override: `FRONTEND_PORT=<port>`.

Backend default: `http://localhost:8000` (legal-rag FastAPI service).
Override: `BACKEND_BASE_URL=http://<host>:<port>`.

### Self-Host Deployment (Coolify / static)

```bash
npm run build   # produces dist/

# Option A: serve dist/ from the legal-rag service's StaticFiles mount
# Option B: serve dist/ via Nginx/Coolify static site

# No CDN dependencies — all fonts are system font stack, all assets are local.
```

The vite build proxies are only for development. In production, static files
should be served from the same origin as the API (or via a configured reverse proxy
that routes `/auth`, `/search`, `/health`, `/documents`, `/cases` to the FastAPI backend).

## Theme: legal-pro

| Token | Value | Use |
|---|---|---|
| `--lr-navy-900` | `#0F1729` | Header background |
| `--lr-navy-800` | `#1A2744` | Primary buttons, links, focus rings |
| `--lr-navy-700` | `#243659` | Hover state |
| `--lr-gold-500` | `#B8960C` | Precedent badge, authority strip |
| `--lr-gold-100` | `#FDF8E7` | Precedent badge background |

All component styles (`citation-card`, `ingest-badge`, `health-banner`, etc.)
are sourced from `services/legal-rag/web/styles/app.css` (the proven live service CSS),
bundled at build time. Changing the live service CSS automatically affects this adapter
on the next `npm run build`.

## Auth Demo Credentials

Matches `services/legal-rag` seed:

```
email: park@lawfirm.example   (associate — sees own cases only)
email: lee@lawfirm.example    (partner  — sees all cases)
password: demo (both)
```
