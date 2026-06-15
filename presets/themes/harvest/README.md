# Harvest Theme

**Slug**: `harvest`
**Version**: 1.0.0
**Tone**: Warm drenched craft

## Aesthetic Concept

The inverse of aurora. Where aurora is cold indigo glow and SaaS precision,
harvest is a drenched roasted-malt amber surface with hop-green accent and
foam-cool highlight. Think a beer label printed on kraft paper under warm tap
lighting — not a timid cream background, but a committed amber-copper surface
that makes you feel the malt.

The three sensations the palette must deliver:
1. **Roasted malt** — deep amber-copper surface (oklch ~42-52% chroma 0.13-0.14 hue 50-55)
2. **Fresh hops** — hop-green secondary accent (oklch ~40% chroma 0.14 hue 145)
3. **Crisp finish** — foam/effervescence cool-light highlight (#BBEBC8)

## Palette Strategy

**Drenched** — the amber surface is the brand. Not a near-white page with a
colored button. The hero is gradient amber-to-deep-malt; body sections use
a deliberate warm-bone surface (#F8F5F0, oklch 97% 0.006 70) that is tinted
toward amber specifically (not generic AI warm cream). `section-alt-bg` deepens
to `#EDE3D4` for rhythm.

## Typography

- **Display**: Big Shoulders Display Variable — bold condensed grotesque.
  Beer-label energy. Off impeccable reflex list. Heavy uppercase weight at
  weight-900 reads as craft print, not SaaS or editorial.
- **Body**: Hanken Grotesk Variable — clean humanist sans. Off reflex list
  (not Inter, DM Sans, Outfit, or Plus Jakarta Sans). Warm stroke angles,
  excellent legibility at body sizes.
- **Korean fallback**: Apple SD Gothic Neo / Malgun Gothic (system).

## Texture & Motion

The signature texture distinguishing harvest from aurora's glowy canvas:

1. **Grain/noise overlay** — inline SVG `feTurbulence` fractalNoise at 3%
   opacity in the hero. Adds tactile craft quality; zero JS; purely decorative.
2. **Effervescence bubbles** — CSS `@keyframes` rising-bubble animation.
   Small circles float upward with staggered delays. `prefers-reduced-motion`
   collapses to static positioned dots.
3. **Soft radial** — restrained warm-amber radial gradient glow at ~15% opacity
   at the top of the hero. Not a glowy wave canvas. No JS canvas required.

All of these are implemented in the `HeroBrewBubbles` section component
(`frontend/adapters/landing-astro/src/sections/HeroBrewBubbles.astro`).

## Fonts Self-Hosting

Requires npm packages (installed in landing-astro):
- `@fontsource-variable/big-shoulders-display`
- `@fontsource-variable/hanken-grotesk`

Imported in `global.css` with conditional block guarded by theme slug comment.

## Industry Fit

- Craft brewery / taproom launch
- Artisan food & beverage CPG
- Premium spirits, coffee, tea brands
- Farm-to-table restaurant launch
- Any brand where warmth must come from material, not from UI chrome

## A11y Notes

All text contrast pairs exceed WCAG AA. Gradient hero tested at both ends of
the gradient span. Effervescence animation uses long duration (8s) with no
rapid flicker — safe for KWCAG 2.3. Grain overlay is aria-hidden decoration.
See `theme.yaml a11y.wcag_aa_pairs` for full contrast table.
