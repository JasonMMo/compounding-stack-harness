# Bridge — Theme README

> Trust-conversion. SMB lead-gen + AI instant-answer landing pages.

## Aesthetic

Crisp white canvas. Single committed deep warm-navy accent (H~212, OKLCH-derived —
distinct from prism's azure H228 and aurora's indigo H280). Plus Jakarta Sans display
paired with Inter Variable body: approachable authority that reads "established local
business" without looking like a generic corporate blue template.

No gradient on the CTA button. No glow. No dark neon. Trust is carried by clarity and
contrast — the visitor submits the lead form because the page is honest, not because
an animation distracted them.

## Primary Purpose

This theme is the visual anchor for the `ai-guide` section — the catalog's first
interactive section. The ai-guide split-hero places the AI answer widget above the fold,
flanked by a dark navy trust panel. The rest of the page (logos, features, faq, cta)
builds the case for submission.

## Composition (recommended section order)

```
ai-guide / split-hero        <- primary hero + AI widget (above fold)
logos    / horizontal-scroll <- social proof strip
features / three-col-icon    <- value props
testimonial / grid           <- customer voices
faq      / single-col        <- objection handling
cta      / centered          <- closing conversion band
footer   / minimal           <- legal + brand
```

## Industry Fit

- Telecom dealers (LG U+, KT, SKT resellers): 요금제 즉답 + 상담신청
- SMB insurance agents: 보험 상품 즉답 + 리드 수집
- Local finance services: 대출/적금 안내 + 상담 예약
- Any SMB business with a knowledge base and a lead-gen goal

## Token Highlights

- `primary`: `#13508C` (warm-navy, OKLCH H212 — unclaimed hue band as of 2026-06-18)
- `surface-1`: `#FFFFFF` (pure white — maximum clarity for the ai-guide input surface)
- `hero-bg-from`: `#111E30` (deep navy for the split-hero trust panel)
- `ai-guide-panel` radius: `12px` (slightly softer than cards — signals interactive tool)

## Fontsource packages required

- `@fontsource-variable/plus-jakarta-sans`
- `@fontsource-variable/inter`

Both self-hosted via Fontsource npm (no external CDN per CLAUDE.md invariant).

## Engineer TODO (functional wiring, out of CDO scope)

The `ai-guide` section type has visual tokens and copy slots defined. Functional
behavior requires adapter-layer implementation:

1. **Embedding inference**: integrate `ai_config.embedding_model` (e.g. `all-MiniLM-L6-v2`
   via sentence-transformers) as a sidecar or server action in `landing-astro`.
2. **Knowledge base loader**: parse `ai_config.knowledge_source` path (YAML/JSON KB)
   and build the vector index at build time (static) or server start (dynamic).
3. **Answer API**: a lightweight endpoint (SSR island or API route) that accepts a query
   string, runs embedding similarity, returns top-K answer objects + recommendation rules.
4. **Lead submission**: POST handler writing to `ai_config.lead_destination`
   (DB table, webhook, or CRM API). Fields from `ai_config.lead_fields`.
5. **Privacy mode**: `privacy_mode: strict` → no query logging, no IP storage.
   `privacy_mode: analytics` → aggregate query counts only (no PII).
6. **SSR fallback (G-69)**: the input and answer area must render as a static FAQ list
   when JS is disabled — full content visible, just no live query capability.

See `presets/site-sections/catalog.yaml` `ai-guide` entry for full `ai_config` schema
documentation (commented).
