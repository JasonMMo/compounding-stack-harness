# deploy/templates/

Reusable Traefik label blocks for `deploy/preview/<slug>.compose.yml` (Growth-144,
P2-3). Purpose: stop copy-pasting the same 15-18 line label block into every new
preview service compose file.

**How Coolify consumes this**: Coolify reads the compose file at
`docker_compose_location` as raw YAML and passes it straight to `docker compose`.
There is no templating step at deploy time — the placeholder substitution here
is **build-time**, done by hand (or by an agent) when a new service compose
file is written, before it is committed. `deploy/templates/*.tpl.yml` files are
never referenced by Coolify directly; they exist only as a copy source.

## When you need this

Only when a service needs Traefik routing behavior beyond what Coolify's
`docker_compose_domains` API auto-generates: a rate-limited sub-path, or
joining another stack's docker network by service name. If neither applies,
use **Variant 0** below (no labels at all).

## Variant table

| Variant | When | Example (existing) | What it adds |
|---|---|---|---|
| **0 — no labels** | Simple static/landing service, single port, no path-specific rules. Domain is set via Coolify API `PATCH docker_compose_domains`, not in the compose file. | `hopwell.compose.yml`, `gtm-landing.compose.yml`, `demo-portal.compose.yml`, `taskflow-demo.compose.yml`, `lawfirm-demo.compose.yml` (~20 landing/business-system composes) | Nothing — just `ports: - "80"` (or the app's port) and let Coolify's proxy auto-route. |
| **A — main router only** | Service is self-contained, does not need another stack's containers, no path-specific rate-limit. | (no current instance uses A without the ratelimit sub-router; legal-rag's base block is A + ratelimit) | `traefik.http.routers.{{SLUG}}.*` + `traefik.http.services.{{SLUG}}.*` |
| **A + ratelimit sub-router** | Self-contained service, but one path (login, public write API) needs throttling. | `legal-rag.compose.yml` (`/auth/login`) | Variant A + `{{SLUG}}-ratelimit` middleware + `{{SLUG}}-limited` priority router |
| **B — external network** | Service must resolve another stack's containers by name (shared db/embed), or convention requires joining the shared preview network. | `hanbang-rag.compose.yml` (reuses legal-rag's `db`/`embed`), `noshow-demo.compose.yml` (`/api` ratelimit + shared network) | `traefik.docker.network={{COOLIFY_NETWORK}}` label + `networks: coolifynet: external: true` (service-level `networks: - coolifynet` too) |

Variant B is additive — it stacks on top of A (with or without the ratelimit
sub-router). Read `traefik-labels.tpl.yml` top-to-bottom; it is laid out in
that order.

## Placeholders

| Placeholder | Meaning | Example |
|---|---|---|
| `{{SLUG}}` | Router/service/middleware name. **Must be unique across the whole Coolify VPS** — Traefik's router/service/middleware namespace is global, not per-stack. | `legal-rag`, `hanbang-rag`, `noshow-demo` |
| `{{DOMAIN}}` | Full external domain (wildcard `*.n9n.co.kr` already resolves to the VPS) | `legal-rag.n9n.co.kr` |
| `{{PORT}}` | Container's internal listen port | `8000` |
| `{{RATELIMIT_PATH}}` | Path prefix to throttle | `/auth/login`, `/api` |
| `{{RATELIMIT_AVERAGE}}` | Steady-state requests per period | `5` (login), `10` (public API) |
| `{{RATELIMIT_BURST}}` | Burst allowance | `10`, `20` |
| `{{RATELIMIT_PERIOD}}` | Window | `1m` |
| `{{COOLIFY_NETWORK}}` | External network name — the shared coolify-proxy network | `gwpba3e8j8upf9v0swf96wkt` |

## Usage

1. Decide the variant from the table above.
2. Copy the matching block(s) from `traefik-labels.tpl.yml` into the new
   service's `labels:` list in `deploy/preview/<new-slug>.compose.yml`.
3. Replace every `{{PLACEHOLDER}}` with the concrete value.
4. If Variant B: add `networks: - coolifynet` to the service and the
   top-level `networks:` block to the compose file.
5. Do not touch the three existing instances (`legal-rag.compose.yml`,
   `hanbang-rag.compose.yml`, `noshow-demo.compose.yml`) to "backfill" the
   template — they are live services; this template applies going forward,
   starting with the next (4th) service that needs Variant A/B routing.

## Non-goals

- This is not a Helm/Kustomize-style templating engine. No render step, no
  CI validation of substituted output. Keep it a copy-paste-and-replace aid;
  if the number of Variant B services grows large enough to warrant an actual
  render script, that is a future DevOps task, not this one.
- Variant 0 services (the ~20 static/landing composes) are intentionally left
  alone — they do not need Traefik labels and adding them would be scope
  creep, not simplification.
