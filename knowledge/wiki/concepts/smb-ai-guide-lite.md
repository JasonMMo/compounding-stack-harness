# SMB AI Guide — Lite Tier

> Type: `[SYNTHESIZED]` — CDO design session + product charter (2026-06-18).
> Relates to: `ai-guide` section type (`presets/site-sections/catalog.yaml`),
>   `bridge` theme (`presets/themes/bridge/`),
>   `telecom-leadgen-demo.yaml` profile.

## What it is

A **local-embedding instant-answer widget** that matches a visitor's free-text question
against a curated knowledge base and returns the best-matching answer cards plus
rule-based recommendation cards — without calling any generative LLM and without
sending any data to a third party.

This is the Lite tier of the "self-host AI 즉답 가이드 + 시맨틱검색 + 리드폼" product.

## Core mechanism

```
Visitor question (text)
    ↓
Local embedding model (multilingual-e5-base, 768-dim, sentence-transformers — Korean+English)
    ↓  cosine similarity
Knowledge base (YAML/JSON, embedded at build or server start)
    ↓  top-K results
Answer cards + recommendation rules
    ↓
Lead capture form (name / phone / opt-in)
    ↓
Lead destination (DB / webhook / CRM)
```

No generative LLM in this path. No per-query API cost. No data leaves the server.

## Why this matters (product differentiation)

| Dimension | Lite tier (this) | Typical chatbot SaaS |
|---|---|---|
| LLM API cost | 0 (local embedding only) | per-query billing |
| Data sovereignty | 100% on-server | visitor data sent to 3rd party |
| Answer accuracy | bounded by KB (no hallucination) | generative — can fabricate |
| Setup complexity | KB YAML + deploy | API key + prompt engineering + safety filters |
| SMB trust signal | "your data stays here" | unclear |

## SMB verticals where this pattern applies directly

- Telecom dealers (요금제 즉답 + 상담 연결)
- Insurance agents (상품 비교 + 상담 예약)
- Local finance services (대출/적금 안내 + 상담 접수)
- Any SMB with a bounded FAQ/product knowledge base and a lead-gen goal

## Section type: `ai-guide`

The catalog entry (`presets/site-sections/catalog.yaml`) defines the static content
shell (CDO-owned: `copy_slots`, `variants`) and documents the functional config as
comments (`ai_config{}` — engineer-owned, not validated by `site_manifest.py`).

**Variants:**
- `split-hero` — primary placement; dark trust panel left, widget right (above fold)
- `centered-panel` — full-width single-purpose landing
- `inline-compact` — embeddable mid-page bar driving to anchor #contact

## Theme: `bridge`

`presets/themes/bridge/` is the visual anchor for this section type.
Warm-navy (H~212) accent, Plus Jakarta Sans display / Inter Variable body.
All ai-guide-specific tokens are declared: `ai-guide-bg`, `ai-guide-border`,
`ai-guide-answer-bg`, `ai-guide-answer-border`, `ai-guide-panel` radius, shadow.

## SSR / G-69 invariant

The ai-guide input and answer area must render as a **static FAQ list** when JS is
disabled — full content visible, no live query. Progressive enhancement only.

## Engineer follow-up (not yet wired)

The functional `ai_config` block is documented in the catalog as comments and in
`presets/themes/bridge/README.md`. Wiring tasks:

1. Embedding sidecar or server action in `landing-astro`
2. Knowledge base loader (build-time vector index)
3. Answer API endpoint (SSR island or API route)
4. Lead submission POST handler
5. Privacy mode enforcement (`strict` = no query log)

See `presets/themes/bridge/README.md` for full task list.

## Reference files

- Section catalog entry: `presets/site-sections/catalog.yaml` → `ai-guide`
- Theme: `presets/themes/bridge/theme.yaml`
- Demo profile: `profiles/telecom-leadgen-demo.yaml`
- Domain seed: `presets/skills/telecom/leadgen.seed.md`
