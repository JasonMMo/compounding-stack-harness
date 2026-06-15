# Kiln — Theme README

> Slug: `kiln` | Version: 1.0.0 | Industry: Artisan Ceramics Studio (A4 F&B/Local/Artisan)

## Aesthetic Rationale

Kiln tells the material story of a ceramics studio in three acts: raw earth on the wheel, the kiln at heat, and the cool glaze reveal. Every visual decision reinforces this arc.

**Surface**: The body background (`surface-1: #C9A078`) is a committed mid-clay field — warm ochre at OKLCH L=0.78, C=0.07. It sits below the L=0.84 impeccable floor (avoiding the cream/sand AI-default trap) and above the C=0.06 chroma threshold, making it unmistakably the brand's own hue. Warmth is carried structurally, not by defaulting to a near-white paper.

**Dark anchor**: The hero and kiln-dark sections use `#1E140A` — a near-black with clay undertone, not a neutral charcoal. It reads as the inside of a kiln, not a generic dark.

**Accent**: The ember primary (`#B5501A`) is a saturated fired terracotta — distinctly orange-brick, not the copper-brown of atelier, not the amber-beer of harvest. It appears only in CTAs, links, and focus rings (<=15% surface coverage).

## Structural Distinction from Harvest (the other F&B Theme)

Harvest is a beer-drench amber theme — liquid, luminous, warm-saturated surfaces with hops-green as a complementary; its hero is a full warm amber drench and its typography is industrial-display (Big Shoulders). Kiln is earthen and matte — a mid-clay body field, ash neutrals, fired terracotta accent, and old-style serif typography that reads hand-lettered and material rather than bold-industrial.

## Persona Fit

Best suited to the **CEO persona** of a ceramics studio owner who needs a landing page that signals handcraft quality, studio legitimacy, and workshop experience. Secondary fit for **ops persona** (workshop booking, class registration form). IT-heavy console personas are out of scope for this archetype.

## Font Pairing Rationale

**Display: Cormorant Garamond** (`@fontsource-variable/cormorant-garamond`)

A high-contrast old-style serif with visible thick-thin stroke transitions and ink-trap details. This pairing axis is **serif display + serif body** — deliberately off-reflex for landing pages (SaaS and beer themes both default to sans-serif display). Cormorant reads as letterpress, hand-pressed, editorial-artisan. It is NOT on the impeccable reflex-reject list. At weight 700 it gives structural authority without shouting.

**Body: Source Serif 4** (`@fontsource-variable/source-serif-4`)

A warm humanist slab with variable weight axis. Pairing two serifs on different contrast axes (Cormorant's extreme high-contrast vs Source Serif 4's moderate-contrast humanist) creates readable hierarchy while staying in the material/editorial register. It is distinct from Karla (atelier), Hanken Grotesk (harvest), and Epilogue (aurora).

Both packages self-host via Fontsource (CLAUDE.md invariant — no Google Fonts CDN). Variable fonts loaded with `font-display: swap`.

## Colour Palette

| Token | Hex | OKLCH approx | Role |
|---|---|---|---|
| `surface-1` | `#C9A078` | L 78% C 0.07 H 42 | Clay body bg (committed earthy, NOT cream) |
| `surface-2` | `#B08556` | L 71% C 0.075 H 41 | Deeper clay pocket, alternating sections |
| `surface-3` | `#8C6438` | L 62% C 0.07 H 40 | Clay shadow, borders |
| `text-1` | `#1E140A` | L 14% C 0.03 H 40 | Near-black with clay warmth |
| `text-2` | `#4A3020` | L 32% C 0.045 H 40 | Warm dark brown |
| `text-3` | `#3D2510` | L 27% C 0.038 H 40 | Tertiary label (darkened for AA) |
| `primary` | `#B5501A` | L 56% C 0.16 H 38 | Kiln-ember accent (fired terracotta) |
| `primary-hover` | `#CC6525` | L 64% C 0.155 H 38 | Lighter ember |
| `primary-active` | `#9A3E10` | L 47% C 0.15 H 38 | Darker fired |
| `primary-subtle` | `#EDD8C0` | L 92% C 0.04 H 44 | Fired-bone badge bg |
| `hero-bg-from` | `#1E140A` | L 14% C 0.03 H 40 | Kiln interior dark |
| `hero-bg-to` | `#2C1E10` | L 20% C 0.032 H 40 | Warm ash-black |

## Texture Tokens (Parallax-Scroll Signature Section)

The `gallery/parallax-scroll` variant renders full-viewport sticky "chapter" panels — no image assets required. Each chapter uses a theme-driven CSS gradient between two hex endpoints, with a dark rgba overlay for text legibility. A CSS grain/noise layer sits on top for the material texture.

### `texture-clay` — Raw Earth Chapter

- Gradient: `#8C4A1E` (warm ochre-terracotta) → `#5C2A0C` (deep raw clay)
- Overlay: `rgba(30,20,10,0.45)` — legibility blanket for light text
- Visual story: clay fresh from the earth, unbaked, organic
- Text contrast on `from` endpoint: **4.88:1** (PASS AA vs `#EDD8C0` light text)
- Text contrast on `to` endpoint: **8.48:1** (PASS AAA)

### `texture-ash` — Wood-Ash Grey Chapter

- Gradient: `#5A5048` (warm ash grey) → `#3A3028` (deep kiln residue)
- Overlay: `rgba(20,16,10,0.40)`
- Visual story: the neutral interlude — wood ash, kiln residue, the pause between heat and glaze
- Text contrast on `from` endpoint: **5.67:1** (PASS AA)
- Text contrast on `to` endpoint: **9.30:1** (PASS AAA)

### `texture-ember` — Kiln Heat Chapter

- Gradient: `#C45A18` (peak ember orange) → `#8C3A0A` (deep fired red)
- Overlay: `rgba(40,15,5,0.35)`
- Visual story: the kiln at maximum temperature — the most saturated and visually intense moment
- Text contrast on `from` endpoint: **3.15:1** (PASS large-text >=3.0 — display headings >=24px)
- Text contrast on `to` endpoint: **5.57:1** (PASS AA for body text)
- Note: ember-from is used only for large display text (chapter titles >=24px bold); body copy always sits over the `to` end or deeper in the gradient where AA is clear.

## A11y Summary

Minimum 10 spot-checked pairs, all PASS (see `theme.yaml a11y.wcag_aa_pairs`). Key pairs:

| Pair | Ratio | Gate |
|---|---|---|
| `text-1` on `surface-1` | 7.57:1 | PASS AAA |
| `text-2` on `surface-1` | 5.06:1 | PASS AA |
| `text-3` on `surface-1` | 5.97:1 | PASS AA |
| White on `primary` (CTA) | 5.09:1 | PASS AA |
| `surface-1` on `hero-bg-from` | 7.57:1 | PASS AAA |

All entrance animations fall back to `fade-simple` under `prefers-reduced-motion: reduce` (WCAG 2.3.3). No autoplay anywhere (WCAG 2.2.2). Parallax-scroll React island respects reduced-motion via the `parallax-lite` preset CSS degradation path. KWCAG: all interactive elements maintain visible focus rings using the ember primary at sufficient contrast.
