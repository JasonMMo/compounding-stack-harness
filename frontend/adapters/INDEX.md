# Frontend Adapters — Index

Pluggable frontend adapters for the compounding-stack-harness.
All adapters implement the contract in `docs/architecture/frontend-adapter-contract.md`.

## Registered Adapters

| Adapter | Stack | Port | Status |
|---------|-------|------|--------|
| [vanilla-htmx](vanilla-htmx/) | Python/Flask + htmx | 5000 | M1 baseline |
| [react](react/) | Vite + React 18 + TypeScript | 5173 | M1 2nd adapter |
| [capacitor](capacitor/) | Capacitor 6 native shell (wraps vanilla-htmx PWA) | — | scaffold — Growth-49 |

## Pluggability

Customer profile key: `stack.frontend: <adapter-name>`

All adapters share the same wire-protocol contract (`middle/contract/wire-v1.yaml`)
and design tokens (`design/tokens/`). Swapping adapters requires only changing the
profile key and starting the corresponding adapter process.

## Compliance Gate (per adapter)

New adapters must pass before merge:
- F-1 flat-underscore query params
- F-2 offset + cursor paging
- F-3 error envelope rendering (branch on `code`, display `message_ko`)
- F-4 idempotent delete (404 → success)
- L1 unit tests
- L3 build (exit 0, bundle produced)
- L4 live (both adapters + backend running)
- `python scripts/diagnose.py` 0 real FAIL

See `docs/architecture/frontend-adapter-contract.md §4` for the full gate.
