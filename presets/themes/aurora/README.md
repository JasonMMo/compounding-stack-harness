# Aurora — Theme Reference

**Slug**: `aurora`
**Tone**: Bold gradient / SaaS energy
**Version**: 1.0.0 (2026-06-15, CDO)

---

## Aesthetic Summary

Aurora uses a deep indigo-to-violet gradient as the hero anchor, projecting ambition
and technical credibility. Large 800-weight display type with tight negative
letter-spacing (-0.03em) creates a SaaS product launch feel. Card elements float
on white with elevated shadows; the alternating section background (violet-050) gives
breathing room without breaking the color story. CTAs are full-bleed gradient bands
with inverse white buttons.

The motion vocabulary is active: `reveal-on-scroll` entrances for content blocks,
`stagger-children` for grids and logo bars, `scale-in` for CTA sections.
The effect is kinetic but not fidgety — every animation has a clear purpose.

---

## When to Use

| Signal | Aurora fits? |
|---|---|
| Client is a SaaS / tech product launching B2B | Yes — primary use case |
| Client is a fintech or developer tool | Yes |
| Client wants "startup energy" or "bold and modern" | Yes |
| Client is a traditional professional services firm | No — use Studio |
| Client is a local retail or food business | No — consider a warmer theme |
| Client explicitly wants "clean and minimal" | No — use Studio |

---

## Persona Fit

**External-facing page viewers** (the SMB's customers/prospects):
- Tech-savvy B2B buyers who read product landing pages daily
- Decision-makers at growth-stage companies
- Developers or technical evaluators for developer-tool products

**Internal personas** (who approve the site):
- **CEO persona** — immediately impactful, "we look serious and credible"
- **Ops persona** — secondary; they will see the contact form path clearly

---

## Industry Tags

`saas` `fintech` `tech-startup` `b2b-platform` `developer-tools`

---

## Color Story

| Role | Value | Use |
|---|---|---|
| Hero gradient start | `#1E1B4B` (indigo-950) | Hero section background deep anchor |
| Hero gradient end | `#4C1D95` (violet-900) | Hero gradient terminus |
| Primary action | `#6D28D9` (violet-700) | All CTAs, links, focus rings |
| Section alt bg | `#F5F3FF` (violet-050) | Every other section (logos, testimonial) |
| Body surface | `#FFFFFF` | Main content sections |
| Accent glow | `rgba(139,92,246,0.35)` | Hero media drop shadow glow |

---

## Typography

Display font: **Plus Jakarta Sans** (fallback: Inter Variable).
`weight-display: 800` — hero headline at 60–72px desktop, 40–48px mobile.
`letter-spacing-display: -0.03em` — tight tracking on large display type.
Body: Inter Variable at 16px / regular weight — maximally readable.

---

## Responsive Behavior

| Breakpoint | Hero headline | Section padding |
|---|---|---|
| Mobile (< 640px) | 36px / weight 700 | 72px vertical |
| Tablet (640–1024px) | 48px / weight 800 | 96px vertical |
| Desktop (> 1024px) | 60–72px / weight 800 | 112px vertical |

`container-max: 1200px` — slightly narrower than default for focused reading.

---

## A11y Notes

- All text on gradient hero is white on darkest gradient point (14.5:1 — WCAG AAA).
- Primary violet-700 passes WCAG AA for interactive elements on white (6.12:1).
- `grayscale` logo filter: CMO/content team must verify supplied logo assets
  maintain 3:1 against white when desaturated.
- All motion falls back to `fade-simple` under `prefers-reduced-motion: reduce`.

---

## Files

- `theme.yaml` — token overrides, section styles, motion mapping
- `README.md` — this file
