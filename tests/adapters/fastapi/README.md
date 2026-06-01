# tests/adapters/fastapi/ — FastAPI Adapter Gate

Adapter-specific test gate for `backend/adapters/fastapi/`.

## Contents

- `conftest.py` — provides `adapter_base_url` fixture with uvicorn auto-launch
  (overrides parent `tests/adapters/conftest.py` base fixture).
- No test files here — compliance tests live in `tests/adapters/_shared/`.

## Gate invocation

```bash
# With auto-launch (uvicorn started/stopped by pytest):
pytest tests/adapters/fastapi/ -v          # 0 tests (conftest only, no test files here)

# Correct invocation for the fastapi compliance gate:
ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/_shared/ -v

# Or start uvicorn manually first, then:
# cd backend/adapters/fastapi && uvicorn main:app --port 8081
# ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/_shared/ -v
```

## Growth-11 result

23/23 PASSED (DIM-1~DIM-4). RC=0. First Python adapter to pass the shared suite.
Verdict: PASS. Adapter-agnostic claim HELD.
