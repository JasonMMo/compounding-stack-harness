# Pipeline Monitor Runbook

> Single source of truth: DevOps persona owns operations; QA persona owns gate verdicts.
> Update this file on any operational change + record in `docs/learn-logs/devops.md`.

[Back to runbooks index](preview-deploy.md)

## Overview

The pipeline monitor tracks every customer case through the automated intake lifecycle from `SUBMITTED` to `CLOSED`. It detects stalls (SLA breach), node failures, and retry-exhausted conditions — all deterministically (LLM 0, PII-free).

Two scripts:

| Script | Purpose |
|---|---|
| `scripts/workflow/pipeline_status.py` | Human-readable status table + per-case node graph |
| `scripts/workflow/pipeline_monitor.py` | Health aggregator + alert emitter |

Data source: `infra/registry/cases/*.yaml` (PII-free, committed). Mirror freshness: `apps/intake/data-mirror/` (gitignored, synced by `intake_sync.py`).

## Quick Start

```bash
# All cases — status table
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_status.py

# All cases — with node graphs
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_status.py --graph

# Drill into a specific case (failed/stalled detail + evidence path)
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_status.py --case <case_id>

# Health summary
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_monitor.py

# Health summary as JSON
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_monitor.py --json

# Append new alerts to docs/intake-inbox/alerts.md (called by intake_sync.py)
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_monitor.py --alert
```

## SLA Table

| Node | Gate | SLA |
|---|---|---|
| SUBMITTED | AUTO | 6 min |
| TRIAGED | AUTO | 1 h |
| CALL_QUEUE | HUMAN | 24 h |
| GAP_RECORDED | AUTO | 1 h |
| PM_TRIAGE | HUMAN | 48 h |
| DRAFT_PROMOTED | AUTO | 2 h |
| SCAFFOLDED | AUTO | 2 h |
| DEPLOYED | AUTO | 10 h |
| UI_CHECKED | AUTO | 1 h |
| NEEDS_FIT | AUTO | 2 h |
| PROFILE_CONFIRMED | HUMAN | 48 h |
| DELIVERED | HUMAN | 72 h |
| FEEDBACK | AUTO | 7 days |
| CLOSED | AUTO | 24 h |

HUMAN-gate nodes generate a `warn` alert at 80% of SLA and a `stall` alert at 100%.

## Node Graph Glyphs

The `--graph` flag renders a horizontal pipe for each case:

```
[OK]SUBMIT -> [>>]TRIAGED -> [..] -> [XX]DEPLOY -> [..]...
```

| Glyph | Meaning |
|---|---|
| `[OK]` | Node completed successfully |
| `[>>]` | Node in progress (within SLA) |
| `[!>]` | Stalled (past SLA, no exit event) |
| `[XX]` | Failed (NODE_FAIL event received) |
| `[..]` | Node not yet entered (skipped/future) |

Only the qualify-path nodes appear in the main graph. Branch nodes (CALL_QUEUE, GAP_RECORDED, PM_TRIAGE) appear on a separate "Branch:" line if entered.

## Drilling into a Stalled or Failed Case

```bash
# Identify the case_id from the status table (leftmost column = slug, use client_id for --case)
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_status.py --case <case_id>
```

Output includes:

- `error_class`: taxonomy label from `DEFECT_TAXONOMY` (e.g. `deploy-fail`, `human-gate-stall`)
- `evidence_path`: path to a PII-free evidence text file under `docs/intake-inbox/evidence/`
- `dwell`: time spent in the node
- `entered_at`: when the node was entered

Read the evidence file for returncode, truncated stderr, and report path:

```bash
cat docs/intake-inbox/evidence/<node>-<slug>-<ts>.txt
```

## Defect Taxonomy

| Class | Meaning | Typical action |
|---|---|---|
| `deploy-fail` | Coolify deploy error | Check Coolify logs; re-run `deploy_to_coolify.py` |
| `scaffold-unknown-entity` | catalog.yaml entity missing | Add entity to catalog; re-scaffold |
| `ui-check-fail` | Playwright smoke failure | Check `docs/intake-inbox/` report; fix adapter |
| `needs-fit-BLOCK` | Needs-fit codex found GAP | CTO: add entity/AC; PM: update criteria |
| `conversion-error` | `intake_to_profile.py` failed | Check qualification_policy.yaml; fix answers |
| `sync-ssh-fail` | SSH rsync error | Check VPS connectivity; retry `intake_sync.py` |
| `human-gate-stall` | Human gate past SLA | CEO/PM: action required |
| `retry-exhausted` | Same node failed 3+ times | CTO escalation; architecture review |
| `audit-chain-broken` | Hash-chain integrity violation | CISO review; do not merge |
| `unknown` | Unclassified | Inspect evidence file manually |

## Alerts File

`docs/intake-inbox/alerts.md` is append-only (PII-free). `intake_sync.py` calls `pipeline_monitor.py --alert` at the end of each sync run. Alerts are deduplicated by `case_id|node_id|alert_type|entered_at`.

To manually flush alerts:

```bash
PYTHONIOENCODING=utf-8 python scripts/workflow/pipeline_monitor.py --alert
```

## Ownership

- **DevOps**: infra failures (`deploy-fail`, `sync-ssh-fail`), SLA monitoring, runbook updates.
- **QA**: gate verdict failures (`ui-check-fail`, `needs-fit-BLOCK`), retry-exhausted escalation.
- **CTO**: `retry-exhausted`, `audit-chain-broken`, architecture defects.
- **CEO**: `human-gate-stall` at `PROFILE_CONFIRMED` and `DELIVERED` nodes.

## G-14 Guard

`python scripts/diagnose.py G-14` checks for qualify-tier cases with NODE_FAIL or SLA-breached NODE_ENTER events. Returns SPEC when no cases exist; FAIL when an active stall or failure is detected.

```bash
python scripts/diagnose.py G-14
python scripts/diagnose.py --list   # confirm G-14 appears
```
