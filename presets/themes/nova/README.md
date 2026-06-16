# Nova Theme

**Tone**: Friendly vivid consumer
**Target**: Consumer mobile apps, SaaS with mobile product, utility tools, productivity apps, health/wellness, edtech

## Aesthetic

Pure white canvas (`#FFFFFF`) with a single committed vivid-violet accent (`#8B2BE2`).
The color system is built for download conversion: visitor sees hero phone mockup,
reads one headline, and hits the App Store / Google Play button pair. White ground
keeps phone screenshots honest — portrait mockups need a neutral backdrop, not a
competing hue. Friendly rounded geometry everywhere (24px button, 16px card) reinforces
the consumer-safe, approachable register.

Vivid violet is not "AI purple glow" and not "electric neon". At OKLCH C≈0.240 H≈305
it reads "category leader app icon" — the register of Figma, Notion, Headspace,
Linear. Chroma is vivid enough to punch on white without a shadow halo or glow filter.
The impeccable DON'T (purple/cyan gradient + glow) is enforced by design: no gradient
on the primary color, no accent-glow (set to 0.00 opacity), no colored shadow.

## Typography

Plus Jakarta Sans 800 is the craft signature. Rounded geometric grotesque at display
scale (48–72px) carries the "app brand name" headline with the weight of a product
launch — think app store feature banner. Paired with Nunito (rounded humanist sans) in
body copy: both fonts share rounded terminals, creating a warm+contemporary system
that no existing theme in the library uses.

| Dimension | Value |
|---|---|
| Display | Plus Jakarta Sans 800 |
| Body | Nunito 400 / 700 |
| Display size range | 48–72px |
| Letter-spacing display | -0.02em |
| Letter-spacing body | 0.00em |

Both fonts require new Fontsource packages — see New Packages section.

Self-hosted via Fontsource (no external CDN — visitor IP privacy).

## Primary Archetype

**A5 — Mobile App / Consumer SaaS**:
hero/split-right → logos/marquee-3d → features/carousel
→ gallery/grid-2x2 → stats/four-up → testimonial/grid
→ cta/centered → footer/minimal

## Hue Differentiation from All 7 Existing Themes

| Dimension | nova | nearest neighbor |
|---|---|---|
| Accent hue | Vivid violet #8B2BE2 (OKLCH H≈305) | aurora (H≈280, blue-violet indigo) — 25 degrees away |
| Canvas ground | Pure white #FFFFFF | studio (near-white, cooler), meridian (stone white, cooler) |
| Display font | Plus Jakarta Sans | No rounded geometric in library |
| Body font | Nunito | No rounded humanist in library |
| Register | "Friendly vivid consumer" / app-store | No mobile-app register in library |
| Radius | 24px button / 16px card | Aurora (16px card, 12px button) — nova is rounder |
| Shadow | Violet-undertone light | No violet-tinted shadow in library |

**Why H≈305 is clear:**
- aurora H≈280 is blue-dominant indigo (cooler, more "enterprise platform")
- nova H≈305 is red-dominant violet-magenta (warmer, more "consumer app")
- Side-by-side: aurora reads blue-adjacent; nova reads purple/fuchsia-adjacent
- 25 hue degrees is perceptually distinct at the vivid chroma level (C≈0.240)

## Hero Architecture

`split-right` on pure white — phone mockup LEFT, text+CTA RIGHT.

- Left 50%: Portrait phone mockup with `border-radius: var(--radius-hero-media)` (20px),
  `box-shadow: var(--shadow-hero-media)`. No dark panel. No gradient wash.
- Right 50%: App name in Plus Jakarta Sans 800, one-line value proposition, two-button
  CTA pair: primary-lg (violet) = App Store, secondary-lg (outlined) = Google Play.

Light hero is a deliberate choice: consumer apps convert better on clean white
(trust, editorial clarity). The phone mockup is the hero — not a background image.

## Gallery grid-2x2 — Phone Screenshot Treatment

Current Gallery.astro `grid-2x2` uses `h-64 object-cover` which crops portrait
phone screenshots (9:19.5 ≈ 1:2.17 ratio) catastrophically. The CDO spec for
the A5 archetype is:

- `aspect-ratio: 9 / 19.5` per frame cell (width from grid; height derived)
- `object-fit: contain` (no cropping; screenshot shows in full)
- Device-frame chrome: `6px solid var(--color-phone-frame)` + `border-radius: var(--radius-gallery-phone-frame)`
- Letterbox background: `var(--color-surface-3)` (makes depth, not artifact)
- Caption: below frame, `var(--color-text-3)`, 13px, centered
- Grid: `grid-cols-2` always (App Store screenshot row idiom — no mobile stacking)
- Section wrapper: `background: var(--color-surface-2)` (violet whisper frames the set)

Full token-spec in `theme.yaml gallery_engineer_spec`.

## Stats Band

`four-up` on full vivid-violet background (`#8B2BE2`): white numerals at 48px+.
Contrast: 5.9:1 (AA; display size ≥48px bold meets AA large text comfortably).
Typical content: "10M+ Downloads" / "4.9 Stars" / "180 Countries" / "50M Users".
This is the emotional proof peak — numbers in white on violet read "category leader".

## New Fontsource Packages Required

Engineer must install and import in `global.css`:

```
@fontsource-variable/plus-jakarta-sans
@fontsource-variable/nunito
```

Imports to add (after ignite block in global.css):

```css
/* Nova theme: Plus Jakarta Sans (display) + Nunito (body)
   Variable fonts — single file covers all weights. font-display: swap. */
@import "@fontsource-variable/plus-jakarta-sans";
@import "@fontsource-variable/nunito";
```

Both are variable fonts — single import covers the full weight range (200–800 for
Plus Jakarta Sans, 200–900 for Nunito). No separate weight CSS files needed.

## A11y

Minimum contrast pair: `#7A6A92` (text-3) on `#FFFFFF` (surface-1) = 4.6:1 (AA).
All primary text pairs AAA. CTA button (violet bg / white): 5.9:1 (AA).
Focus rings use `var(--color-primary)` directly (5.9:1, exceeds 3:1 non-text threshold).
`primary-border` (#B57EE8) is decorative only — not used for focus rings.
Full pairs in `theme.yaml a11y.wcag_aa_pairs`.
