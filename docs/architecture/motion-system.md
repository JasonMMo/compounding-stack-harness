# Motion System — Progressive-Enhancement Scroll Choreography (Growth-87)

> CTO architecture blueprint. Raises the marketing-site quality ceiling from "static brochure (B급)"
> toward "A급 designed experience" **without** abandoning the impeccable taste-floor or the
> Growth-69 no-JS-visible invariant. Library-free. Motion is a *themeable, opt-in dial*, not a default.
>
> Trigger: founder pointed at sanggong.co.kr (Korean landing web-agency: fullPage.js scroll-snap +
> AOS entrance + Swiper + GSAP). We reproduce the **effect** as accumulated variants, not the stack.

## 1. Why this lifts the ceiling (the diagnosis)

The "B급" ceiling is **not** capped by impeccable (no glow/neon/glass) — that is the taste *floor*.
It is capped by two concrete absences: **(a) motion** (we scroll like a brochure) and **(b) bold
composition**. ~80% of the perceived A-tier feel of Korean promo landings is scroll choreography.
So: keep the floor (impeccable), lift the ceiling with motion. Target = *A급 designed experience,
self-host-safe, content fully visible without JS*.

## 2. Hard invariants (non-negotiable)

- **G-69 (no-JS-visible)**: every element's **CSS default state is fully visible** (opacity:1, no
  transform). The reveal animation is applied *only* when JS adds an `.in-view`/`.motion-ready`
  class. JS off → content is 100% present and readable. This is the inverse of AOS (which hides
  by default and reveals via JS — that would violate G-69).
- **`prefers-reduced-motion: reduce`**: all motion collapses to instant/none.
- **Library-free**: no GSAP, jQuery, AOS, fullPage.js, Swiper. Vanilla `IntersectionObserver` +
  CSS `scroll-snap` + CSS transitions only. (GSAP-class timeline choreography is explicitly OUT —
  cost, bundle, and G-69 tension. If ever needed, it is a separately-gated decision.)
- **impeccable floor stays**: no glow, neon, dark-mode-neon, glassmorphism. Motion adds *timing &
  depth*, not garish effects.
- **Cost ≈ 0**: build-time CSS + one tiny vanilla script. No infra/LLM cost.

## 3. The two profile dials (open-closed; default = today's behavior)

Added to `site:` block in the profile schema. **Both default to off/none** so all existing demos
render byte-identically until opted in.

| key | values | meaning | default |
|---|---|---|---|
| `site.scroll_mode` | `normal` \| `snap` | `snap` = full-screen `scroll-snap-type:y mandatory`, `100dvh` sections | `normal` |
| `site.motion` | `off` \| `subtle` \| `rich` | entrance-reveal + parallax intensity. `subtle` = conservative B2B, `rich` = promo landing | `off` |

Same variants serve a conservative bank and a flashy promo client by flipping one key — that is the
accumulation: *one motion layer, dialed per customer*, not per-customer bespoke code.

## 4. Components to build (the accumulated assets)

1. **scroll-snap shell** — layout primitive in the landing-astro adapter (BaseLayout / page
   dispatch). When `scroll_mode=snap`: wrap sections in a snap container, each section `min-height:
   100dvh; scroll-snap-align:start`. Unsupported browser → normal scroll (graceful). No library.
2. **IO reveal directive** — vanilla script (~30 lines, no deps). Elements opted-in via
   `data-reveal` (+ optional `data-reveal-delay`). On `DOMContentLoaded` the script adds
   `motion-ready` to `<html>` (gates all motion CSS behind JS presence), then an
   `IntersectionObserver` toggles `.in-view`. **CSS default (no `motion-ready`) = visible**; only
   `html.motion-ready [data-reveal]:not(.in-view)` sets the hidden/offset start state. → G-69 holds.
   Respect `prefers-reduced-motion`.
3. **Motion tokens** (8th-axis theme system) — `--motion-duration`, `--motion-ease`,
   `--motion-distance`, `--motion-stagger`. Each theme sets its own intensity; `site.motion` scales
   them (subtle vs rich). aurora = restrained defaults.
4. **3 motion-aware section variants** — chosen to also retire existing NEED backlog (synergy):
   - `hero/scroll-reveal` (existing NEED) — staged entrance of headline → subhead → CTA.
   - `gallery/full-bleed-strip` (existing NEED) — horizontal parallax / scroll-driven strip.
   - one process or stats variant with pinned/staged reveal (pick during design).
5. **Guard** — extend G-15 (marketing-site visual gate) or add G-16: any section using motion must
   pass a **JS-off content-visible check** (render with JS disabled → all copy present) +
   `prefers-reduced-motion` honored. Wire into diagnose.py.

## 5. Pilot

Apply `scroll_mode=snap` + `site.motion=subtle` (or `rich`) to **gtm-landing** (our own shopfront,
aurora, just Koreanized) → rebuild → **CTO visual verify (JS-on render + JS-off content check)** →
QA gate → DevOps redeploy to gtm-landing.n9n.co.kr. It becomes the live demo of our raised ceiling
for prospects. Then the variants are matrix-§2 HAVE and reusable across all customers/themes.

## 6. Out of scope (record so it is not silently assumed done)

- GSAP-level timeline choreography, scroll-jacking, cursor-follow/magnetic micro-interactions
  (JS-required → G-69 tension; revisit only behind an explicit gate).
- Raising motion across *all* existing demos — they stay `motion:off` until individually opted in.
- The 3 other themes' Korean display-font gap (kiln·studio·harvest) — separate Growth-86 backlog.

## 7. Persona loop

CDO (motion tokens, dial semantics, IO-reveal CSS spec with G-69-default-visible, 3 variant
designs) → Engineer (scroll-snap shell, IO directive, token wiring, 3 variants, profile-schema
keys, site_manifest passthrough, tests) → CTO (visual verify both JS states) → QA (G-69 JS-off gate
+ 4-layer) → DevOps (pilot redeploy + live verify).
