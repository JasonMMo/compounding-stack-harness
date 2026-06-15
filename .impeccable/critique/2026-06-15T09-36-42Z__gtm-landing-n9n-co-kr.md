---
target: gtm-landing
total_score: 27
p0_count: 0
p1_count: 2
timestamp: 2026-06-15T09-36-42Z
slug: gtm-landing-n9n-co-kr
---
# Critique — gtm-landing (https://gtm-landing.n9n.co.kr), Brand register

## Design Health Score (Nielsen 10)

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Contact form shows success; no real loading states (acceptable for static landing) |
| 2 | Match System / Real World | 3 | Copy plain and clear; minor product jargon |
| 3 | User Control and Freedom | 3 | Links/tabs work; standard landing freedom |
| 4 | Consistency and Standards | 3 | Aurora tokens consistent across sections |
| 5 | Error Prevention | 3 | Form has required markers; low stakes |
| 6 | Recognition Rather Than Recall | 3 | Minimal nav, clear sections |
| 7 | Flexibility and Efficiency | 3 | No shortcuts (fine for landing) |
| 8 | Aesthetic and Minimalist | 2 | Slop tells: gradient text, em-dash overuse, 4/4 reflex-reject fonts, indigo-glow SaaS reflex |
| 9 | Error Recovery | 2 | Contact form is demo stub — submit silently no-ops |
| 10 | Help and Documentation | 3 | FAQ section serves as help |
| **Total** | | **27/40** | **Acceptable (borderline Good)** |

## Anti-Patterns Verdict — does it look AI-generated?

**LLM assessment**: Partially, yes. The indigo gradient + canvas glow hero on dark is the *first-order category reflex* for an AI/dev tool ("AI codegen → indigo-glow SaaS hero"). Gradient headline text is an absolute ban. Feature carousel images are /login screens — weak proof. Otherwise composition is clean and the proof-marquee of real generated systems is genuinely distinctive.

**Deterministic scan** (detect.mjs on built dist/index.html):
- `gradient-text` (warning, line 2): `bg-clip-text + bg-gradient` — the hero "Zero dev team." gradient. On the skill's Absolute Bans list.
- `em-dash-overuse` (warning): 9 em-dashes in body copy — AI cadence tell.

**Agreement**: LLM + detector agree on gradient text. Detector additionally caught em-dash cadence the eye glosses over. No false positives.

**Brand-register tell (LLM, detector can't see)**: fonts = Plus Jakarta Sans · Inter · DM Sans · DM Serif Display — **all four on impeccable's reflex-reject font list** (training-data defaults → monoculture).

## Overall Impression
Solid B+ landing that converts, but it wears three AI fingerprints (gradient text, reflex fonts, indigo-glow SaaS hero) that undercut the "we craft real systems" claim. Biggest single opportunity: kill the gradient text + move off default fonts → instant de-slop with no structural change.

## What's Working
1. **Proof marquee of our own generated systems** — distinctive, honest, on-thesis. Not a stock-photo wall; real screenshots. This is the page's strongest, least-AI move.
2. **No-JS resilience** — hero/marquee/first feature render without JS (hard-won, rare in AI landings).
3. **Honest M1 framing** — no fake testimonials, no invented pricing; stats are real.

## Priority Issues

- **[P1] Gradient text on hero headline** — absolute ban, detector-confirmed. *Why*: decorative gradient on the most important text = instant AI tell, and reduces contrast/legibility. *Fix*: solid ink/brand color; create emphasis via weight + size, not gradient. *Command*: `/impeccable typeset`
- **[P1] Font stack is 4/4 reflex-reject** (Plus Jakarta, Inter, DM Sans, DM Serif Display). *Why*: training-data default fonts read as generic AI output; contradicts a craft brand. *Fix*: pick a contrast-axis pairing off the default list (one distinctive display + one neutral text). *Command*: `/impeccable typeset`
- **[P2] Indigo-glow SaaS hero = first-order category reflex**. *Why*: guessable theme from the category alone. *Fix*: either commit harder to a distinctive register or quiet the glow/gradient toward restraint. *Command*: `/impeccable bolder` (distinctive) or `/impeccable quieter` (restraint)
- **[P2] Carousel feature images are /login screens**. *Why*: a login page doesn't visually prove "AI domain experts"; weakens the strongest claims. *Fix*: swap to domain-rich app screens or purpose-built mockups per feature. *Command*: `/impeccable polish`
- **[P2] Em-dash overuse (9)**. *Why*: AI cadence tell across the copy. *Fix*: vary punctuation — commas, colons, periods. *Command*: `/impeccable clarify`

## Persona Red Flags (Landing → Jordan, Riley, Casey)

- **Jordan (first-timer)**: the feature carousel shows only the ACTIVE feature; 2 of 3 core value props are hidden behind tabs a first-timer may never click. Risk: they leave knowing 1/3 of why to care.
- **Riley (stress tester)**: submitting the contact form shows a success message but silently does nothing (demo stub). This is Riley's exact red flag — "appears to work but silently fails." Acceptable as a labeled demo, but on a real client deploy it would erode trust.
- **Casey (mobile)**: hero CTA reachable; proof assets light (130KB). Check carousel tab tap-target size (44×44) on mobile.

## Minor Observations
- Eyebrow "AI-POWERED CODE GENERATION" above the hero is the tracked-uppercase-kicker pattern (borderline slop scaffold) — one deliberate kicker is fine, watch for it repeating per-section.
- Stats row (14+/5/0 bits) flirts with the hero-metric template; currently OK because values are real and few.

## Questions to Consider
- What would a confident, *non-indigo-glow* version of this hero look like — could the proof-marquee BE the hero?
- Does "Zero dev team." need a gradient to land, or does weight alone hit harder?
- Should the 3 feature value props be visible at once (de-tab the carousel) so first-timers get all three?
