# Ignite Theme

**Tone**: Urgent anticipation
**Target**: Summits, conferences, hackathons, workshop series, product launch events

## Aesthetic

Crisp off-white canvas (`#FAFAF8`) with a single committed crimson-red accent (`#C41E22`).
The color system is built for scanning: event attendees find the date, venue, and register
button in under 3 seconds. Light ground keeps sponsor logos and speaker portraits at full
fidelity — no grayscale filter needed, no sponsor brand equity lost.

Crimson is not alarm and not consumer-tomato. At the chosen chroma (OKLCH C≈0.195, H≈22)
it reads "sold-out badge", "save the date" urgency — the premium red of a theater curtain
or a conference lanyard, not a warning state. The hero dark column (split-left) delivers
one focused moment of dark drama — then the page opens to the light canvas.

## Typography

Barlow Condensed 800 is the craft signature. Condensed grotesque at display scale
carries an event name and date in a narrow hero column without word-break. The
contrast with Lato (humanist body) is classic editorial: poster headline / programme body.

| Dimension | Value |
|---|---|
| Display | Barlow Condensed 800 |
| Body | Lato 400 / 700 |
| Display size range | 48–80px |
| Letter-spacing display | -0.01em |
| Letter-spacing body | 0.00em |

Self-hosted via Fontsource (`@fontsource/barlow-condensed`, `@fontsource/lato`).
No external CDN — visitor IP privacy.

## Primary Archetype

**A3 — Event / Conference**:
hero/split-left → logos/grid → process/horizontal-steps
→ features/three-col-icon → stats/four-up → testimonial/carousel
→ cta/newsletter-inline → faq/single-col → footer/minimal

## Differentiation from All 6 Existing Themes

| Dimension | ignite | nearest neighbor |
|---|---|---|
| Accent hue | Crimson #C41E22 (H≈22) | harvest copper/orange (H≈55) — 33 hue degrees away |
| Canvas ground | Light off-white | flux (dark charcoal), meridian (stone white similar but cooler) |
| Display font | Barlow Condensed | No condensed grotesque in library |
| Body font | Lato | No humanist grotesque in library |
| Register | "Urgent anticipation / event poster" | No event register |
| Radius | 10px card / 8px button | Between meridian (6px) and aurora (16px) |
| Shadow | Warm neutral | Amber-tinted (flux), purple-tinted (aurora) |

## Hero Architecture

`split-left` with dark left column (`hero-bg-from: #161210`):
- Left 50%: event name (Barlow Condensed 800, off-white), date line, venue, CTA button (inverse-lg = white btn)
- Right 50%: key visual — monogram, texture sentinel, or event identity mark on surface-1

Dark column is not full-page dark. Only the split — creating a decisive left-anchor without
the all-dark-hero pattern that flux already owns.

## Stats Band

`four-up` on full crimson background (`#C41E22`): white numerals at 48px+.
The only full-width crimson section on the page. Reads as "sold out energy" —
numbers in white on red feel urgent and committed, not decorative.

## Fonts

- Display: Barlow Condensed — `@fontsource/barlow-condensed`
- Body: Lato — `@fontsource/lato`

Both self-hosted via Fontsource (no external CDN).

## A11y

Minimum contrast pair: `#7D6E6A` (text-3) on `#FAFAF8` (surface-1) = 4.5:1 (AA).
All primary text pairs AAA. CTA button (crimson bg / off-white): 5.1:1 (AA).
Full pairs in `theme.yaml a11y.wcag_aa_pairs`.
