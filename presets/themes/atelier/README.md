# Atelier Theme

**Slug**: `atelier`
**Tone**: Ink-pressed, deliberate, sparse

## Aesthetic

A confident near-black hero surface (ink, not pure black — oklch 12% with a cool-blue undertone)
stands against warm-paper bone (#F5F2EC — enough amber chroma to read as intentional, not as
AI-default cream). One restrained copper accent (#9A5B32) fires at gallery hover states, CTA buttons,
and focus rings. Everywhere else: ink and paper.

The register: architectural practice business card. Design consultancy studio letterhead. The kind of
site where the portfolio images are the loudest thing on the page, and the type knows to be quiet
but not timid.

**NOT**: editorial-magazine (no display serif, no Fraunces, no italic drop caps). NOT SaaS. NOT artisan-warm.

## Fonts

- **Display**: Raleway Variable — geometric sans with art-deco lineage. Heavy weight (800) reads as
  architectural signage, not as SaaS marketing. NOT on the reflex-reject list. Sharp optical axis,
  compressed at heavy weights. The `headline-only` hero variant puts it at 7xl with tight tracking.
- **Body**: Karla Variable — humanist grotesque, warm stroke angles. Distinct from Epilogue (aurora)
  and Hanken Grotesk (harvest). Clean at 16px+ body text.
- **Korean fallback**: Apple SD Gothic Neo / Malgun Gothic (system).

## Palette

| Token | Hex | OKLCH | Usage |
|---|---|---|---|
| `hero-bg-from` | `#141418` | oklch(12% 0.02 250) | Hero surface anchor |
| `surface-1` | `#F5F2EC` | oklch(96% 0.012 80) | Body background |
| `surface-2` | `#E8E2D8` | oklch(91% 0.014 76) | Alternating sections |
| `primary` | `#9A5B32` | oklch(55% 0.12 42) | Copper accent (≤15% coverage) |
| `text-1` | `#201F27` | oklch(18% 0.025 250) | Body copy |

## Page Archetype

Designed for **A2 — Creative Agency / Portfolio** (see `docs/architecture/landing-pattern-matrix.md §3`):

```
hero / headline-only  →  gallery / masonry-3col  →  story / founder-split
→  features / single-col-list  →  testimonial / single-card
→  cta / with-image  →  footer / minimal
```

## A11y

- WCAG AA minimum met on all text/bg pairs (checked in `theme.yaml a11y.wcag_aa_pairs`)
- Ink-black hero with warm-paper text: 15.1:1 (AAA)
- Copper CTA on warm-paper: 4.55:1 (AA)
- Copper CTA button (paper label on copper bg): 4.82:1 (AA)
- All animations reduced-motion safe (fade-simple fallback)
