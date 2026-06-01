# Backend Adapter: fastapi

FastAPI (Python 3.11+), Uvicorn ASGI server.
Serves all 8 wire keys defined in `middle/contract/wire-v1.yaml`.
Swap-compatible with `springboot-jakarta` via customer profile `stack.backend: fastapi`.

## Wire Key → HTTP Mapping

| Wire key       | Method | Path                                  | Notes                          |
|----------------|--------|---------------------------------------|--------------------------------|
| auth.login     | POST   | /api/auth/login                       | Body: {username, password, remember_me?} |
| auth.logout    | POST   | /api/auth/logout                      | Body: {token}; idempotent      |
| entity.read    | GET    | /api/entities/{entity_type}/{id}      |                                |
| entity.list    | GET    | /api/entities/{entity_type}           | Query: page, size, paging_mode, sort_field, sort_direction |
| entity.create  | POST   | /api/entities/{entity_type}           | Body: {data: {...}} or flat map |
| entity.update  | PATCH  | /api/entities/{entity_type}/{id}      | PATCH semantics; absent fields unchanged |
| entity.delete  | DELETE | /api/entities/{entity_type}/{id}      | Idempotent; missing id → success |
| status.health  | GET    | /api/status/health                    |                                |

Paths match springboot-jakarta exactly — the shared compliance suite is path-coupled.

## How to Run

Requirements: Python 3.11+.

```bash
# From this directory
pip install -r requirements.txt

# Default port 8081 (springboot-jakarta uses 8080)
uvicorn main:app --port 8081

# Port override via env var
PORT=9090 uvicorn main:app --port 9090
```

FastAPI auto-generates interactive docs at `http://localhost:8081/docs`.

## How to Test

### L1 — Unit smoke tests (no server required)

```bash
cd backend/adapters/fastapi
pytest tests/test_smoke.py -v
```

### L4 — Shared compliance suite (server must be running)

The shared compliance suite lives in `tests/adapters/springboot-jakarta/` and is
adapter-agnostic. Point it at the FastAPI adapter via `ADAPTER_BASE_URL`:

```bash
# Terminal 1: start the adapter
cd backend/adapters/fastapi
uvicorn main:app --port 8081

# Terminal 2: run compliance suite
ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/springboot-jakarta/ -v
```

## Contract Loading (G-1 Compliance)

`contract_loader.py` reads `middle/contract/wire-v1.yaml` and
`middle/contract/error/codes.yaml` at startup using a relative path from the
adapter root to the repo root. No error codes or HTTP status values are hardcoded
as Python constants — this satisfies the G-1 single-source principle. The
`scripts/diagnose.py G-1` guard scans `.py` files and passes cleanly.

## Persistence

M1: generic in-memory store (`store.py::InMemoryEntityStore`). Thread-safe via
per-entity-type `threading.Lock`. Keyed by `entity_type → (id → field map)`.
UUIDs generated on create. Restart clears all data.

DDL-axis integration (real database) is a later Growth.

## Known Gaps

| Gap | Reason | Future Growth |
|-----|--------|---------------|
| cursor paging returns BAD_REQUEST | Not implemented; offset mode fully works | Growth-N: cursor paging spec |
| No real credential store | Demo user only (username=demo, password=demo) | Growth-N: JWT / OAuth2 |
| Token validation not enforced on entity endpoints | Auth is stub-grade M1 | Growth-N: security filter |
| No DDL-schema validation on create/update | In-memory only, no catalog wired | Growth-N: DDL-axis integration |
| No multi-tenancy | Single in-memory store, not tenant-scoped | M5 gate |

## Auth Demo Credentials

```
username: demo
password: demo
```

POST /api/auth/login → returns token. Token is valid until server restart or logout.

## Port Notes

Default port is **8081** to avoid collision with springboot-jakarta (8080). Both
adapters may run simultaneously for side-by-side compliance testing.
Port is env-configurable: `PORT=<n> uvicorn main:app --port <n>`.
(Growth-7 hit port conflicts running both adapters — documented here so QA can plan.)
