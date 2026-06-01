# tests/adapters/_shared/ — Shared Backend Compliance Suite

Canonical location of `test_compliance.py` — the adapter-agnostic black-box HTTP
compliance gate for all backend adapters (swappable-layers §6, Growth-11 QA decision).

## What lives here

- `test_compliance.py` — 23 tests across 4 dimensions (DIM-1~DIM-4). Single source.
- `conftest.py` is NOT here — the parent `tests/adapters/conftest.py` provides the
  `adapter_base_url` fixture (reads ADAPTER_BASE_URL env var).

## Gate invocation

```bash
# Any backend adapter, already running:
ADAPTER_BASE_URL=http://localhost:8080 pytest tests/adapters/_shared/ -v   # springboot-jakarta
ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/_shared/ -v   # fastapi

# Adapter-specific gate with auto-launch (see each adapter dir's conftest.py):
pytest tests/adapters/springboot-jakarta/ -v   # gradlew auto-launch if not running
pytest tests/adapters/fastapi/ -v              # uvicorn auto-launch if not running
```

## Single-source guarantee

`tests/adapters/springboot-jakarta/test_compliance.py` is a 1-line import-star shim:

```python
from tests.adapters._shared.test_compliance import *  # noqa: F401,F403
```

There is exactly ONE copy of the 23 assertions (this file). The shim makes
`pytest tests/adapters/springboot-jakarta/ -v` collect the tests under the springboot
path so the gradle auto-launch conftest applies. No sync risk.

## Adding a new backend adapter gate

1. Create `tests/adapters/<kind>/conftest.py` (auto-launch fixture — mirror fastapi conftest).
2. Gate command: `ADAPTER_BASE_URL=http://localhost:<port> pytest tests/adapters/_shared/ -v`
3. All 23 tests must pass (0 FAIL, 0 ERROR). Any failure = BLOCK (QA authority).
4. Update `backend/adapters/INDEX.md` row for the new adapter.
