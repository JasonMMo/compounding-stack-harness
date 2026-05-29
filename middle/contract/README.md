# Middle Contract — Asset Manifest

> The wire-protocol contract is the **single stable layer** of the 3-tier
> architecture (CLAUDE.md §4). Frontend and Backend adapters READ these files
> only — they never redeclare the definitions (G-1 single-source).

## Assets

| File | Purpose | Since |
|---|---|---|
| [`wire-v1.yaml`](wire-v1.yaml) | Wire-protocol request/response schemas. 8 keys across `auth` / `entity` / `status` domains. Error fields reference the envelope below. | Growth-5d |
| [`error/codes.yaml`](error/codes.yaml) | Standard error-code catalog (11 codes). Closed set the `error` envelope `code` field draws from. http_status + retriable + i18n baseline. | Growth-7 |

## Contract conventions

- **Key namespace**: `<domain>.<verb>` (two-segment dotted path). New domains are added as `presets/skills/<industry>` warrant.
- **Error envelope**: every error response is `{ "error": { "code", "message", "details"? } }`. `code` is the only stable, non-localized token — clients branch on `code`, never message text.
- **Idempotency / standards** (Growth-5d): `entity.delete` is idempotent (404→success); `entity.update` is PATCH semantics (partial). Adapters MUST honor these.
- **Versioning**: each file carries a SemVer `version`. Adapters declare the range they support. OpenAPI 3.1 migration is the long-term target (swappable-layers.md §8), gated to the first adapter (now landed — Growth-7).

## Consumers (adapters reading this contract)

| Adapter | Layer | Status |
|---|---|---|
| [`backend/adapters/springboot-jakarta`](../../backend/adapters/springboot-jakarta) | Backend | Growth-7 (in-memory store, offset paging) |

> New adapters: read this directory at build/runtime, map keys to your framework, and pass the adapter compliance gate (swappable-layers.md §6). Do not redeclare schemas or error codes.
