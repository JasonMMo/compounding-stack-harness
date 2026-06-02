# Demo Filming Runbook — smallmfg-demo (vanilla-htmx + FastAPI)

[← demo-video-scenario.md](demo-video-scenario.md)

> Bring the `smallmfg-demo` profile up locally with realistic Korean demo data
> for recording the GTM video. Maps each step to its scene.
> Verified working 2026-06-02 on Windows 11 (Python 3.x + Node v24; fastapi live, DIM 37 PASS).

**All sample data is fictional** (`profiles/seed/smallmfg-demo.seed.yaml`) — invented
names/serials for demo only. Honest-marketing constraint: every screen shown is a real
running adapter, never a mockup.

---

## What runs where

| Tier | Process | Port | Source |
|---|---|---|---|
| Backend | FastAPI adapter (in-memory store) | `8081` | `backend/adapters/fastapi/` |
| Frontend | vanilla-htmx Flask thin server | `5000` | `frontend/adapters/vanilla-htmx/` |
| Data | seed loaded via wire `entity.create` | — | `profiles/seed/smallmfg-demo.seed.yaml` |

> The FastAPI store is **in-memory**: data lives only while the process runs.
> Restarting the backend wipes it — re-run the seed loader (step 4) after every
> fresh backend launch. This is intentional for M1 (no DB dependency to film).

---

## Prerequisites (once)

```bash
# from repo root
pip install -r backend/adapters/fastapi/requirements.txt
pip install -r frontend/adapters/vanilla-htmx/requirements.txt
pip install pyyaml
```

---

## Demo up — copy-paste sequence

Run from the repo root: `D:\AI\workspace\compounding-stack-harness`.
Use a fresh backend so screens show only the 4 demo employees (a long-lived
instance may carry leftover compliance-test rows).

### Step 1 — Scaffold (Scene 2: the `scaffold.py` terminal shot)

```bash
python scripts/workflow/scaffold.py --profile smallmfg-demo
```

Expected (film this verbatim — Scene 2):

```
scaffold complete — profile: smallmfg-demo
  entities scaffolded : 11 (employee, department, position, leave-request, ...)
  DDL output          : .../out/smallmfg-demo/ddl/postgres.sql
  manifest output     : .../out/smallmfg-demo/screen-manifest.json
```

The printed manifest path is needed in step 3 (frontend reads it via `PROFILE_MANIFEST`).

### Step 2 — Launch the FastAPI backend (terminal A)

```bash
cd backend/adapters/fastapi
PYTHONPATH=. python -m uvicorn main:app --host 127.0.0.1 --port 8081
```

PowerShell equivalent:

```powershell
cd backend\adapters\fastapi
$env:PYTHONPATH="."; python -m uvicorn main:app --host 127.0.0.1 --port 8081
```

Wait for `Application startup complete.` Health check (separate shell):

```bash
curl http://127.0.0.1:8081/api/status/health
# {"status":"ok","version":"1.0.0","checks":[{"name":"store",...},{"name":"contract",...}]}
```

### Step 3 — Launch the vanilla-htmx frontend (terminal B)

```bash
cd frontend/adapters/vanilla-htmx
python build_tokens.py        # emits static/css/tokens.css (L3 build step)
BACKEND_BASE_URL=http://127.0.0.1:8081 \
  FRONTEND_PORT=5000 \
  PROFILE_MANIFEST="$(pwd)/../../../out/smallmfg-demo/screen-manifest.json" \
  python server.py
```

PowerShell equivalent (run from repo root after `python build_tokens.py`):

```powershell
cd frontend\adapters\vanilla-htmx
python build_tokens.py
$env:BACKEND_BASE_URL="http://127.0.0.1:8081"
$env:FRONTEND_PORT="5000"
$env:PROFILE_MANIFEST="$(Resolve-Path ..\..\..\out\smallmfg-demo\screen-manifest.json)"
python server.py
```

`PROFILE_MANIFEST` makes the frontend render typed forms (field labels/controls)
instead of generic key/value rows — this is what Scene 3B's labeled leave form needs.

### Step 4 — Load the demo seed (terminal C — backend must be up)

```bash
python scripts/workflow/seed_loader.py --slug smallmfg-demo --base-url http://127.0.0.1:8081
```

Expected tail:

```
seed load complete — 18 records created via entity.create.
```

Dry-run (validate ordering without POSTing): add `--dry-run`.

### Step 5 — Open the browser (Scene 3)

1. `http://localhost:5000/login` → login `demo` / `demo`.
2. **Scene 3A — employee list**: `http://localhost:5000/entities/employee`
   - Shows 김민준 (active), 박서연 (on-leave / 휴가중), 이도윤 (active), 정지우 (active).
3. **Scene 3B — leave request form**: `http://localhost:5000/entities/leave-request/new`
   - Typed form: `leave_type` (연차/병가/무급 등), `start_date`, `end_date`, `reason`.
   - Fill one live and submit; list at `/entities/leave-request` updates.
4. **Scene 3C — asset + maintenance**: `http://localhost:5000/entities/asset`
   - Shows `CNC-001` (CNC 밀링머신 1호기) and `AIR-002`.
   - `http://localhost:5000/entities/maintenance-record` →
     the inspection record for CNC-001 with `next_due_date 2026-06-15`.

---

## Scene → command map (quick reference)

| Scene | What to film | Command / URL |
|---|---|---|
| 2 | scaffold terminal output | `python scripts/workflow/scaffold.py --profile smallmfg-demo` |
| 2 | manifest JSON zoom | open `out/smallmfg-demo/screen-manifest.json` |
| 3A | employee list, status badges | `localhost:5000/entities/employee` |
| 3B | leave request typed form | `localhost:5000/entities/leave-request/new` |
| 3C | asset list + CNC-001 maintenance | `localhost:5000/entities/asset`, `.../maintenance-record` |
| 4 | stack-swap (vanilla-htmx/fastapi → react/springboot) | edit `profiles/smallmfg-demo.yaml` `stack:` + re-scaffold; see scenario §Scene 4 |

---

## Verification (2026-06-02, this machine)

- Guards: `python scripts/diagnose.py` → 0 real FAIL (G-2/G-3 SPEC only, allowed).
- Seed loader dry-run: 18 records resolve in dependency order.
- Seed loader live: 18 records created via `entity.create`; all FKs resolved
  (backend `_check_fk` would reject any dangling reference).
- Wire-API read-back: employee total includes the 4 demo rows
  (김민준 active / 박서연 on-leave / 이도윤 active / 정지우 active);
  leave-request `annual`/`approved`; assets `CNC-001` + `AIR-002`;
  maintenance-record `inspection` with `next_due_date 2026-06-15`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `error while attempting to bind ... 8081` | a backend is already running on 8081 | reuse it, or kill it and relaunch for a clean store |
| employee list shows extra `Test Employee` rows | leftover compliance-test rows in a long-lived store | relaunch backend fresh, re-run step 4 |
| forms show raw key/value, no labels | `PROFILE_MANIFEST` not set / wrong path | re-run step 3 with the manifest path from step 1 |
| `backend unreachable` from seed loader | backend not up yet | wait for `Application startup complete.`, retry step 4 |
| login fails | wrong creds | use `demo` / `demo` (M1 stub) |
