# Studio — Theme Reference

**Slug**: `studio`
**Tone**: Minimal editorial / portfolio
**Version**: 1.0.0 (2026-06-15, CDO)

---

## Aesthetic Summary

Studio is built on restraint. Where Aurora announces itself with color and gradient,
Studio earns attention through composition and space. The hero rests on a warm
off-white canvas (stone-50 #FAFAF9) with near-zero gradient — the content is the
spectacle. Typography uses DM Serif Display at normal weight for headings, creating
a publication-quality voice. Body copy is DM Sans — humanist, legible, contemporary.

Card radius is virtually eliminated (4px); buttons are near-square (2px radius).
Shadows are whisper-thin. The alternating section background is cool zinc-100 for
structural clarity without visual noise. CTAs use a near-black solid band (zinc-900)
as a stark contrast moment — the only place boldness appears.

Motion is deliberate and unhurried: `fade-up` as the default, `fade-simple` for
footers and logo bars. The result reads as confidence, not performance.

---

## When to Use

| Signal | Studio fits? |
|---|---|
| Client is a creative agency / design studio | Yes — primary use case |
| Client is a consulting, law, or architecture firm | Yes |
| Client says "clean", "minimal", "sophisticated" | Yes |
| Client wants to convey heritage, craft, or expertise | Yes |
| Client is a tech startup wanting "bold and energetic" | No — use Aurora |
| Client is a SaaS product with feature comparison | No — consider Aurora |
| Client has a strong brand color they want prominent | Possibly — review color override |

---

## Persona Fit

**External-facing page viewers**:
- High-value B2B service buyers: procurement directors, C-level at mid-market firms
- Design-literate evaluators who notice when sites "try too hard"
- Portfolio reviewers (potential hires, collaborators, press)

**Internal personas** (who approve the site):
- **CEO persona** — "this looks expensive and trustworthy"
- **Ops persona** — appreciates the clear information hierarchy

---

## Industry Tags

`creative-agency` `consulting` `professional-services` `architecture` `law` `design-studio`

---

## Color Story

| Role | Value | Context |
|---|---|---|
| Primary / CTA background | `#18181B` (zinc-900) | Buttons, CTA band, links |
| Hero canvas | `#FAFAF9` (stone-50) | Warm off-white page anchor |
| Gradient terminus | `#F5F5F4` (stone-100) | Hero gradient end (very subtle) |
| Alt section bg | `#F4F4F5` (zinc-100) | Every other section |
| Decorative border | `#A1A1AA` (zinc-400) | Card borders, dividers |
| Body surface | `#FFFFFF` | Feature, pricing, testimonial sections |

There is no colored accent. Brand identity comes from typography and composition,
not hue. If a client has a strong brand color, the color override block in
`theme.yaml` can introduce it as `primary` without disturbing the rest.

---

## Typography

Display font: **DM Serif Display** (serif) at weight 400 — unconventional choice
for a sans-dominant web landscape; signals editorial authority.
Fallback chain includes Georgia for environments without web font loading.

Body: **DM Sans Variable** — friendly but professional. Pairs cleanly with the
serif display. No font clash because DM Serif is used only at H1/H2 level.

`letter-spacing-display: -0.01em` — minimal tracking reduction for large display
type (less aggressive than Aurora; editorial restraint).

---

## Responsive Behavior

| Breakpoint | Hero headline | Section padding |
|---|---|---|
| Mobile (< 640px) | 32px / weight 400 | 80px vertical |
| Tablet (640–1024px) | 48px / weight 400 | 112px vertical |
| Desktop (> 1024px) | 56–64px / weight 400 | 128px vertical |

`container-max: 1120px` — narrower max-width concentrates reading.
`container-gutter: 32px` — generous gutter creates margin breathing room.

---

## A11y Notes

- Near-black primary (zinc-900) on any background in this theme exceeds 15:1 — WCAG AAA.
- White text on CTA dark band (zinc-900): 18.1:1 — WCAG AAA.
- `grayscale-hover` on logos: logos are full color by default (accessible), only
  transition to gray on mouse hover. Keyboard/touch users always see full color.
- Card bordered style uses zinc-200 border (decorative only, non-interactive) —
  WCAG 1.4.11 non-interactive exemption documented in a11y block.
- All motion defaults to `fade-up` (non-aggressive entrance). No loops.
- `prefers-reduced-motion: reduce` falls back to `fade-simple` per spec.
- No autoplay anywhere. FAQ uses `collapse` animation (expand/collapse on
  user trigger — WCAG 2.2 compliant).

---

## Files

- `theme.yaml` — token overrides, section styles, motion mapping
- `README.md` — this file
