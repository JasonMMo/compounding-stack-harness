# Landing Pattern Matrix — Combinatorial Diversity Blueprint

> CDO doc. Decision-oriented map for the multi-session buildout of diverse landing-page patterns.
> Canonical positions: section-type taxonomy (§1), variant table (§2), page archetypes (§3),
> buildout backlog (§4), invariants (§5).
> Last updated: 2026-06-16 (CDO, Growth-79 — A1 SaaS archetype + flux theme + 3 new variants)

---

## Context: The sameness problem

`gtm-landing` (aurora theme) and `hopwell` (harvest theme) are currently:

```
hero → features/carousel → faq → cta → footer
```

Same 5-section spine, same carousel variant for features, different colors only.
Two pages, zero structural DNA difference. The lever is **section-layout variants × page
archetypes**, not themes. Themes are cosmetic; archetypes are structural.

---

## §1 Section-Type Taxonomy

Full set warranting catalog support for marketing/landing pages.
Ordered by usage frequency across archetypes.

| # | Type slug       | Label                      | Role on page                                    |
|---|-----------------|----------------------------|-------------------------------------------------|
| 1 | `hero`          | Hero Banner                | First fold; sets register and CTA anchor        |
| 2 | `features`      | Feature / Value Props      | "What you get" — mid-page anchor                |
| 3 | `logos`         | Logo Bar / Social Proof    | Trust signal; can appear above or below fold    |
| 4 | `testimonial`   | Testimonials               | Qualitative proof; peer voice                   |
| 5 | `process`       | How-It-Works / Process     | Sequential steps; lowers barrier to entry       |
| 6 | `stats`         | Stats / Metrics Band       | Quantitative proof; scannable numbers           |
| 7 | `pricing`       | Pricing Table              | Decision-point; high-intent section             |
| 8 | `gallery`       | Gallery / Showcase         | Visual evidence; image/video-led                |
| 9 | `story`         | Story / About              | Brand origin, founder voice, mission            |
|10 | `team`          | Team / People              | Social trust; reduces faceless-brand fear       |
|11 | `faq`           | FAQ Accordion              | Objection handling; long-tail SEO               |
|12 | `cta`           | CTA Band                   | Conversion action; often repeated at bottom     |
|13 | `lead`          | Lead / Newsletter          | Inline capture; lighter than full contact form  |
|14 | `footer`        | Footer                     | Nav, legal, brand close                         |

**Currently in catalog**: hero, logos, features, pricing, testimonial, faq, cta, footer, lead, gallery, story (Growth-77), process, team (Growth-78), stats (Growth-79) — 14 of 14.
**Missing from catalog**: none — full taxonomy registered.

---

## §2 Variant Table Per Section Type

Format: short-name | structural description | status.
Status: HAVE (existing variant name) or NEED.

### hero (currently: centered, split-left, split-right, fullscreen-video, glowy-waves, brew)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| centered         | Text + CTA centered, full-width bg image or gradient behind                 | HAVE           |
| split-left       | Text left 50%, media right 50%, above-fold only                             | HAVE           |
| split-right      | Media left 50%, text right 50% (mirror of split-left)                      | HAVE           |
| fullscreen-video | Background video fills viewport, text overlaid at center                    | HAVE           |
| glowy-waves      | Dark canvas + animated React island; pills + stats strip below CTA          | HAVE           |
| brew             | Warm full-bleed image + grain texture overlay; no JS required               | HAVE           |
| bento-grid       | Text left column, 2×2 or 3×2 product screenshot bento grid right            | NEED           |
| headline-only    | Single massive display heading, one sub-line, no imagery — type as design   | NEED           |
| scroll-reveal    | Two-panel: headline locks, right panel scrolls product scenes               | NEED           |

### features (currently: three-col-icon, two-col-alternating, single-col-list, carousel)

| Variant             | Structural description                                                   | Status         |
|---------------------|--------------------------------------------------------------------------|----------------|
| three-col-icon      | 3-column grid, icon + heading + text per card                            | HAVE           |
| two-col-alternating | Alternating image-left / image-right rows with text                      | HAVE           |
| single-col-list     | Vertical list, no grid; tight typographic rhythm                         | HAVE           |
| carousel            | Horizontal scroll with image, heading, description per slide             | HAVE           |
| bento-mosaic        | Irregular CSS grid — one large feature card spans 2 rows, rest smaller   | NEED           |
| timeline-horizontal | Horizontal numbered steps with connecting line; doubles as process       | NEED           |

### logos (currently: horizontal-scroll, grid, marquee-3d)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| horizontal-scroll| Static centered row, responsive wrap                                        | HAVE           |
| grid             | 2-3 row grid of logos with optional copy                                    | HAVE           |
| marquee-3d       | Perspective proof wall, React island, infinite scroll                       | HAVE           |
| quote-band       | Single customer quote spans full width, logo beside name; no logo grid      | HAVE           |

### testimonial (currently: single-card, carousel, grid)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| single-card      | One quote, large display, centered; author photo + attribution              | HAVE           |
| carousel         | Swipeable cards; one visible at a time                                      | HAVE           |
| grid             | 2-3 column card grid                                                        | HAVE           |
| pull-quote-wall  | Full-bleed section; 2-3 large pull quotes in an asymmetric column layout    | NEED           |

### process (currently: numbered-stack, horizontal-steps)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| numbered-stack   | Vertical numbered steps, each with a headline and one-line description      | HAVE           |
| horizontal-steps | Left-to-right numbered steps with connectors; collapses to stack mobile     | HAVE           |
| split-animation  | Step number locks left, right column scrolls through step content           | NEED           |

### stats (currently: ticker-band, four-up)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| four-up          | 4 stats in a row; large number, small label; full crimson band (ignite)     | HAVE           |
| ticker-band      | Full-width band, stats inline, subtle separator; no card boxing             | HAVE           |

### gallery (currently: masonry-3col, parallax-scroll)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| masonry-3col     | 3-column masonry of images; no equal heights                                | HAVE           |
| parallax-scroll  | Sticky full-viewport chapters; scale+overlay on scroll; editorial body+CTA below each; scroll-driven (React island, framer-motion useScroll); texture: sentinel for photo-free demo | HAVE           |
| full-bleed-strip | Single image fills full viewport width, tall aspect ratio                   | NEED           |
| grid-2x2         | 2×2 product screenshot grid with optional caption per cell                  | NEED           |

### story (currently: founder-split, timeline-year)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| founder-split    | Photo left, long-form founder text right; typographic emphasis on one quote | HAVE           |
| timeline-year    | Vertical timeline with year markers and short milestones                    | HAVE           |

### team (currently: headshot-grid)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| headshot-grid    | 3-4 column grid of photo + name + role; monogram-initials avatar fallback   | HAVE           |
| headshot-list    | Horizontal cards; photo + name + two-line bio                               | NEED           |

### faq (currently: single-col, two-col)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| single-col       | Full-width accordion, one column                                            | HAVE           |
| two-col          | Two-column accordion split                                                  | HAVE           |
| categorized      | Tab or pill filter to switch FAQ category; accordion within                 | NEED           |

### cta (currently: centered, left-aligned, with-image, newsletter-inline)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| centered         | Headline + subhead + button, centered on solid or gradient band             | HAVE           |
| left-aligned     | Text left, button right — asymmetric, wider layouts                         | HAVE           |
| with-image       | CTA copy left, product or scene image right                                 | HAVE           |
| newsletter-inline| Email input + submit inline in dark band; DEMO_MODE stub; A3 archetype     | HAVE           |

### lead (currently: minimal-field)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| minimal-field    | Single email input + submit, centered, no other fields                      | HAVE           |
| multi-field-card | Name + email + optional message in a raised card; contact-form pattern      | NEED           |

### pricing (currently: two-tier, three-tier, toggle-annual-monthly)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| two-tier         | 2 cards side-by-side                                                        | HAVE           |
| three-tier       | 3 cards; middle card highlighted                                             | HAVE           |
| toggle-annual-monthly | Price toggle switch above card grid                                   | HAVE           |
| comparison-table | Feature comparison rows; tiers as columns; HAVE/NO cell values             | NEED           |

### footer (currently: minimal, full-links, newsletter)

| Variant          | Structural description                                                      | Status         |
|------------------|-----------------------------------------------------------------------------|----------------|
| minimal          | Brand name + tagline + legal; single row                                    | HAVE           |
| full-links       | 3-4 column link grid + logo + social icons                                  | HAVE           |
| newsletter       | Link grid + inline email capture in footer                                  | HAVE           |

---

**Variant count summary**:
14 section types · 52 total variants · 33 HAVE · 19 NEED
(Growth-77 additions: gallery/parallax-scroll HAVE + story/timeline-year HAVE + lead/minimal-field HAVE; gallery/full-bleed-strip added as NEED)
(Growth-78 additions: logos/quote-band HAVE + process/numbered-stack HAVE + team/headshot-grid HAVE — A6 B2B-services archetype shipped)
(Growth-79 additions: stats section type NEW + features/bento-mosaic HAVE + stats/ticker-band HAVE + testimonial/pull-quote-wall HAVE — A1 SaaS Product Launch CDO spec shipped; flux theme added)
(Growth-80 follow-on: process/horizontal-steps HAVE + stats/four-up HAVE + cta/newsletter-inline HAVE — A3 Event/Conference archetype shipped; ignite theme added)

---

## §3 Page Archetypes

5 archetypes with ordered section compositions and variant picks.
Two archetypes sharing the same variant in the same slot is a warning sign — avoid.

### A1 — SaaS Product Launch

Target: B2B SaaS, dev tool, platform. Dense, trust-heavy, conversion-optimized.

```
hero           / glowy-waves    (dark canvas; pills + stats strip)
logos          / horizontal-scroll (trust fast; above features)
features       / bento-mosaic   (irregular grid breaks card-sameness)
process        / numbered-stack (shows the workflow)
stats          / ticker-band    (quantitative proof band)
testimonial    / pull-quote-wall (qualitative proof, large format)
pricing        / three-tier     (decision point)
faq            / two-col        (objection handling)
cta            / left-aligned   (asymmetric close)
footer         / full-links
```

DNA: Dark hero → tight social proof → irregular feature grid → process → numbers → quotes → pricing.

---

### A2 — Creative Agency / Portfolio

Target: design studio, brand consultancy, architecture firm. Sparse, image-led, typographic.

```
hero           / headline-only  (display type as design, no imagery trap)
gallery        / masonry-3col   (work speaks first)
story          / founder-split  (POV, not mission statement)
features       / single-col-list (capabilities as a spare list)
testimonial    / single-card    (one strong quote, not a grid)
team           / headshot-list  (faces, brief bio)
cta            / with-image     (project image beside contact invite)
footer         / minimal
```

DNA: Type-first hero → work grid → founder voice → spare list → one quote → faces → close.
Almost no overlap with A1 (shared: single-card testimonial only).

---

### A3 — Event / Conference

Target: summit, hackathon, workshop series, product launch event.

```
hero           / split-left     (date + venue left, key visual right)
logos          / grid           (sponsors above fold)
process        / horizontal-steps (schedule or session flow)
features       / three-col-icon (speakers or track highlights)
stats          / four-up        (seats, speakers, sessions, past attendees)
testimonial    / carousel       (past attendee quotes)
cta            / newsletter-inline (register / join waitlist)
faq            / single-col
footer         / minimal
```

DNA: Split hero with date → sponsor grid → horizontal timeline → speaker cards → numbers → register.
Shared with A1: faq/single-col, minimal footer. Everything else diverges.

---

### A4 — F&B / Local / Artisan — **BUILT** (Growth-77, 2026-06-16)

Live: **https://terra-ceramics.n9n.co.kr** (kiln 테마, artisan wheel-thrown ceramics studio)
Theme: kiln — clay terracotta #C9A078 + wood-ash neutrals + kiln-ember accent #B5501A; Cormorant Garamond + Source Serif 4.

Target: brewery, restaurant, coffee roaster, food CPG, local hospitality.

```
hero           / brew           (full-bleed image + texture; no JS)
gallery        / parallax-scroll (scroll-driven sticky chapters; texture:clay/ash/ember sentinel — FIRST SCROLL-CINEMATIC)
story          / timeline-year  (founding story; craft provenance)
features       / two-col-alternating (product detail rows with image)
lead           / minimal-field  (launch list or reservation; soft ask)
faq            / single-col
footer         / minimal
```

DNA: Image-drenched hero → scroll-cinematic material chapters → origin story → product detail rows → soft capture.
No logos section (no enterprise trust signals in this register). Shortest composition — 7 sections.
Note: gallery variant changed from full-bleed-strip (NEED) to parallax-scroll (HAVE) — scroll-driven motion answers the CEO same-pattern critique on the time axis.

---

### A5 — Mobile App

Target: consumer app, SaaS with a mobile product, utility tool.

```
hero           / split-right    (phone mockup left, text right)
logos          / marquee-3d     (press logos or app-store badges as proof wall)
features       / carousel       (swipeable — mirrors mobile gesture vocabulary)
gallery        / grid-2x2       (screenshots of 4 key app screens)
stats          / four-up        (downloads, ratings, users, countries)
testimonial    / grid           (app-store review grid aesthetic)
cta            / centered       (app-store download button pair)
footer         / minimal
```

DNA: Phone-first split hero → press wall → swipeable features → screenshot grid → reviews → download.
Shares carousel/features with hopwell, but everything surrounding it is different.

---

### A6 — B2B Services / Consulting — **BUILT** (Growth-78, 2026-06-16)

Live: **https://meridian.n9n.co.kr** (meridian 테마, MERIDIAN managed-IT / security advisory)
Theme: meridian — cool-stone white #F7F8F4 + deep forest-green #1A5C3A (navy-reflex avoided, AAA throughout); Syne + DM Sans.

Target: IT consultancy, HR firm, legal, accountancy, managed services.

Shipped composition (all HAVE variants — the blueprint's split-animation / comparison-table / categorized remain NEED):
```
hero           / centered       (deep-forest dark bg; clear headline, no grain)
logos          / quote-band     (one client quote on dark band; more credible than logo soup)
process        / numbered-stack (how engagement works; bold numerals + step copy)
features       / two-col-alternating (service detail)
team           / headshot-grid  (named experts; monogram-initials avatars — no stock faces)
testimonial    / carousel       (client voice)
faq            / single-col      (leadership objections)
cta            / left-aligned    (forest-green band; book a risk review)
footer         / full-links
```
Original blueprint (NEED variants for a future richer A6 instance):
process/split-animation · pricing/comparison-table · faq/categorized.

DNA: Clear centered hero → single-client quote → numbered process → alternating services → faces → close.
Shares almost nothing structurally with A1 (different hero, different features, different proof format).
All sections Astro-native (zero React islands) — entire archetype renders without JS (Growth-69).

---

## §4 Prioritized Buildout Backlog

Ordered by: (visible differentiation delivered / implementation cost). First 10.

| # | Item                                   | Type     | Variant          | Impact reason                                              | Source hint          |
|---|----------------------------------------|----------|------------------|------------------------------------------------------------|----------------------|
| ~~1~~ | ✅ `process` + numbered-stack (DONE Growth-78) | NEW TYPE | numbered-stack | Built; shipped in A6 MERIDIAN                       | done                 |
| ~~2~~ | ✅ `stats` section type + ticker-band (DONE Growth-79) | NEW TYPE | ticker-band | Built; CDO spec in out/a1-saas/; catalog registered | done |
| 3 | hero / bento-grid                      | NEW VAR  | bento-grid       | Breaks the centered/split duopoly; screenshotable for SaaS | 21st.dev bento       |
| 4 | hero / headline-only                   | NEW VAR  | headline-only    | Maximum visual contrast to all 3 existing heroes; type-led | build from scratch   |
| ~~5~~ | ✅ features / bento-mosaic (DONE Growth-79) | NEW VAR | bento-mosaic | Built; CDO spec in out/a1-saas/; catalog registered | done |
| 6 | `gallery` section type + full-bleed-strip | NEW TYPE | full-bleed-strip | A4 archetype requires it; single image > card grids      | build from scratch   |
| ~~7~~ | ✅ logos / quote-band (DONE Growth-78)  | NEW VAR  | quote-band       | Built; shipped in A6 MERIDIAN                              | done                 |
| 8 | `story` section type + founder-split   | NEW TYPE | founder-split    | A2 and A4 archetypes; differentiates from faceless SaaS   | build from scratch   |
| ~~9~~ | ✅ process / horizontal-steps (DONE Growth-80 follow-on) | NEW VAR | horizontal-steps | Built; A3 Event archetype shipped; ignite theme | done |
| ~~10~~ | ✅ testimonial / pull-quote-wall (DONE Growth-79) | NEW VAR | pull-quote-wall | Built; CDO spec in out/a1-saas/; catalog registered | done |

**21st.dev notes**: Items 3, 5, 9 have strong analogs in 21st.dev component library (bento, timelines).
Items 1, 2, 4, 6, 7, 8, 10 are better built from scratch — simpler than adapting a component with
its own design opinions.

---

## §5 Invariants

Every new variant and section type must satisfy all five before merge.

1. **Theme-tokenized**: No hardcoded hex/rgb in component source. All color references through
   semantic tokens (`--color-primary`, `--color-surface-1`, etc.). The same variant renders
   correctly under aurora, studio, and harvest without code changes.

2. **No-JS visible** (Growth-69 rule): The section must render its full content without JavaScript.
   React islands are permitted only where genuine interaction is required (carousel swipe,
   animated canvas, accordion toggle). Static layout, type, and imagery must be Astro-native.
   Progressive enhancement; never a blank section before hydration.

3. **impeccable-detector clean**: Before merge, run the variant through the `/impeccable critique`
   gate. Must pass: no reflex-reject font choices, no repeated tiny uppercase kicker on every
   section heading as a structural default, no purple/cyan gradient + glow dark-neon palette,
   no identical icon-above-heading card grid unless that IS the variant's named structural point.

4. **Catalog-registered**: Every new section type must add an entry to
   `presets/site-sections/catalog.yaml` with `copy_slots`, `asset_slots`, `item_slots` (if
   applicable), and `variants` list before any profile references it. Every new variant must be
   appended to the `variants` list of its parent type. One-off page-level implementations not in
   the catalog are prohibited — the catalog is the reuse gate.

5. **Archetype-traceable**: Every new variant must appear in at least one archetype in §3 of this
   document (updated if needed). Variants with no archetype home are design inventory without
   a use case — they do not ship.

---

*End of landing-pattern-matrix.md — CDO, 2026-06-15*
