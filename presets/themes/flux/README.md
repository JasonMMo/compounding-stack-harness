# Flux Theme

**Tone**: Engineered precision
**Target**: Developer infrastructure, observability, API platforms, data pipelines

## Aesthetic

Deep charcoal canvas (`#1A1610`) with a single committed amber-gold accent (`#8B5E10`).
No violet. No green. No neon glow gradients. The amber reads as "instrumentation" —
spectrum analyzers, signal traces, scientific precision — without borrowing from
consumer-SaaS playbooks (indigo/violet) or the second-reflex cliche (terminal green).

Space Grotesk display numerals are the craft signature: at 48–78px the numeral forms
are geometrically distinct enough to carry stats sections and pricing tables without
needing decorative support. This is load-bearing typography.

## Primary Archetype

**A1 — SaaS Product Launch** (dense, trust-heavy, conversion-optimized):
hero/glowy-waves → logos/horizontal-scroll → features/bento-mosaic →
process/numbered-stack → stats/ticker-band → testimonial/pull-quote-wall →
pricing/three-tier → faq/two-col → cta/left-aligned → footer/full-links

## Differentiation from aurora

Both aurora and flux target B2B SaaS, but:

| Dimension | aurora | flux |
|---|---|---|
| Hero bg | Indigo-to-violet gradient | Charcoal amber-cast flat |
| Accent hue | Violet/purple (#6D28D9) | Amber-gold (#8B5E10) |
| Display font | Bricolage Grotesque | Space Grotesk |
| Body font | Epilogue | Inter |
| Register | "Startup energy, bold" | "Infrastructure precision, earned" |
| Radius | 16px card (soft) | 8px card (considered) |
| Shadow | Purple-tinted | Amber-tinted charcoal |

## Fonts

- Display: Space Grotesk Variable — `@fontsource-variable/space-grotesk`
- Body: Inter Variable — `@fontsource-variable/inter`

Both self-hosted via Fontsource (no external CDN — visitor IP privacy).

## A11y

Minimum contrast pair: `#736250` (text-3) on `#F8F7F4` (surface-1) = 4.6:1 (AA).
All primary text pairs AAA. Full pairs in `theme.yaml a11y.wcag_aa_pairs`.
