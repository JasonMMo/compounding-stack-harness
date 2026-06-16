# Prism Theme

**Tone**: Precise clarity
**Target**: API platform SaaS, developer tools, gateway analytics, observability tooling, platform engineering teams

## Aesthetic

Pure white canvas (`#FFFFFF`) with a single committed deep-azure accent (`#1B4FA8`).
Built for A7 archetype (API Platform / Developer Tool): the visual language of a clean
request log, not a marketing brochure. Neutral ground lets the bento-grid product
cluster do the work; azure is the single signal color.

## Accent

`#1B4FA8` — deep azure (OKLCH H≈228, C≈0.185). The hue of high-trust developer
tooling (Stripe docs, Linear API, Postman). Saturated but non-neon: no glow, no
gradient on the CTA, no box-shadow with color.

## Typography

- **Display**: IBM Plex Sans 700 — precision-instrument grotesque. Open terminals,
  rational proportions, authority without aggression.
- **Body**: DM Sans — humanist geometry optimized for data-dense reading at 14-16px.
- **Mono** (bento stat numerals only): DM Mono — monospace rhythm signals "real data".

Loaded via Google Fonts `@import url(...)` in `global.css` (no npm fontsource package,
matching the existing pattern for nova/flux/meridian themes).

## Key Tokens

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#1B4FA8` | CTA button, links, focus ring |
| `--color-surface-2` | `#F2F5FA` | Section-alt bg, bento card bg |
| `--color-bento-card-bg` | `#F2F5FA` | Bento cluster card background |
| `--color-bento-card-border` | `#E2E8F2` | Bento card fine rule |
| `--color-bento-status-ok` | `#16A34A` | System healthy indicator |
| `--radius-bento-card` | `12px` | Bento card corner radius |

## Composition (A7 archetype)

```
hero/bento-grid         Light canvas; stat+proof bento cluster right (7-5 grid)
logos/horizontal-scroll Company name wordmarks, grayscale
features/bento-mosaic   5 capability cards, irregular grid
stats/ticker-band       Quantitative band, surface-2 bg
testimonial/pull-quote-wall  3 typographic pull-quotes, asymmetric
pricing/three-tier      Standard decision point, middle tier highlighted
faq/single-col          Focused objection handling
cta/left-aligned        Surface-2 band, azure CTA
footer/full-links
```
