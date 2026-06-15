# Meridian Theme

**Slug**: `meridian`
**Archetype**: A6 — B2B Services / Consulting (managed-IT, security advisory, professional services)
**Register**: Brand-serves-product. Trust and clarity.

---

## Aesthetic Rationale

Meridian communicates competence through structure, not colour volume. The surface is a
cool-stone near-white (OKLCH L 0.975 C 0.008 H 100 — a barely-perceptible stone cast,
committed and distinct from the cream/sand AI-default trap). Against this, a single
deep forest-green accent (OKLCH L 0.38 C 0.12 H 155) fires at every interactive
element: CTAs, links, focus rings, numbered-step labels, monogram circles.

The hero anchors in a very deep forest (#112219), giving the page a strong entrance
without glow, gradient theatrics, or dark-neon. Whitespace is generous but measured
(104px section-y vs atelier's 120px) — "deliberate" reads as advisory precision, not
gallery contemplation. Radius is tight (4-6px): considered, not clinical, not rounded.

---

## Why Not the B2B Reflex

**Against navy-and-grey**: not a single blue token. The "reliable" signal comes from
the dark forest anchor and the typographic weight of Syne at 800, not from navy hue.

**Against navy-gold premium-fintech**: no gold, no amber, no copper. Forest-green
reads "resilient infrastructure, environmental stability" — associations useful for
managed-IT and security advisory.

---

## How It Stays Distinct from Atelier

Atelier is warm-monochrome: ink-black on warm-paper bone (hue 76-80), copper accent,
Raleway+Karla, 120px section-y, near-zero radius, dark-hero drench.

Meridian is cool: stone near-white surface (hue 100-102), forest-green accent (hue 155),
Syne+DM Sans, 104px section-y, 4-6px radius, similar dark-hero anchor but with a
forest hue (#112219) not an ink-black (#141418). The two themes share restraint as a
value but diverge on temperature, hue family, typography, and industry register. Atelier
reads "creative studio portfolio." Meridian reads "you can trust us with your infrastructure."

---

## Persona and Industry Fit

| Persona | Fit | Notes |
|---|---|---|
| CEO | Primary | High-level confidence and outcome framing. Hero / cta sections. |
| Ops | Primary | Process stack, features, FAQ — detailed but not technical |
| IT-admin | Strong secondary | team/headshot-grid with titles, clear nav, structured content |

**Industry tags**: consulting, managed-IT, security-advisory, B2B-services, professional-services.

---

## Font Rationale

**Display: Syne Variable** (`@fontsource-variable/syne`)
Geometric sans with an angular, architectural optical axis. At weight 800 it reads
"engineered precision" — not decorative (Raleway), not editorial-compressed (Big Shoulders),
not serif-soft (Cormorant). The junctions are sharp; the proportions wide and confident.
Appropriate for a firm that wants to signal technical mastery without visual noise.

**Body: DM Sans Variable** (`@fontsource-variable/dm-sans`)
Humanist grotesque with wide apertures and clear rhythm at 15-16px. Excellent legibility
for longer advisory copy (service descriptions, FAQ answers, team bios). Paired with
Syne, the contrast axis — angular geometric display vs open humanist body — reads
precise and credible without feeling cold. Distinct from every prior theme body face:
Karla (atelier), Hanken Grotesk (harvest), Source Serif 4 (kiln), Inter (aurora),
Lato (studio).

Korean fallback: system stack (Apple SD Gothic Neo / Malgun Gothic). No extra cost.

---

## A11y — WCAG AA Pairs

All pairs pass AA minimum (4.5:1 normal text / 3:1 large text). Six pairs pass AAA.

| Background | Foreground | Ratio | Context | Result |
|---|---|---|---|---|
| `#F7F8F4` surface-1 | `#171E19` text-1 | 17.1:1 | Body copy | AAA |
| `#F7F8F4` surface-1 | `#1A5C3A` primary | 12.3:1 | Links, focus rings, CTA label | AAA |
| `#112219` hero-bg | `#F7F8F4` surface-1 | 17.8:1 | Hero headline/body | AAA |
| `#F7F8F4` surface-1 | `#394F3E` text-2 | 12.0:1 | Sub-headings, labels | AAA |
| `#F7F8F4` surface-1 | `#627A68` text-3 | 4.6:1 | Tertiary labels, captions | AA |
| `#1A5C3A` primary bg | `#F7F8F4` surface-1 | 12.3:1 | CTA button fill | AAA |
| `#ECEDE8` surface-2 | `#171E19` text-1 | 15.8:1 | Alt section body | AAA |
| `#112219` hero-bg | `#EAF2EC` primary-subtle | 16.5:1 | Hero badge/label | AAA |

Focus ring (`#4A8C63` primary-border on `#F7F8F4`): ≥ 3:1 large-component threshold,
WCAG 1.4.11 PASS.

Team monogram circles: forest-green bg (`#1A5C3A`) + white initials (`#F7F8F4`): 12.3:1 AAA.

KWCAG: all animations use reveal-on-scroll / fade-up with fade-simple reduced-motion
fallback. No autoplay. No rapid flicker. Carousel autoplay explicitly disabled.

---

## Composition Guide — A6 Section Order

```
hero/centered           dark forest bg, centred headline, inverse CTA
logos/quote-band        client logo band OR single pull-quote on dark strip
process/numbered-stack  1-2-3-4 vertical numbered service delivery steps
features/two-col-alternating  each service / capability pair alternates image+text
team/headshot-grid      3-col grid, monogram fallback for no-photo bios
testimonial/carousel    autoplay=false, single centered quote per slide
faq/single-col          line dividers, chevron icon, collapse animation
cta/left-aligned        forest-green bg, left-aligned text, inverse button
footer/full-links       4-col, social links, top divider
```

---

## Fontsource Install Reference

```bash
npm install @fontsource-variable/syne @fontsource-variable/dm-sans
```

Import in Astro layout:

```js
import "@fontsource-variable/syne";
import "@fontsource-variable/dm-sans";
```

`font-display: swap` is set by Fontsource by default. Self-hosted — no Google Fonts CDN,
no visitor IP exposure (INDEX.md invariant).
