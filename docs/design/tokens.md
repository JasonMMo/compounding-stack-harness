# Design Tokens — compounding-stack-harness

> Single source of truth for visual language. Adapter-agnostic: tokens are expressed
> as CSS custom properties AND a JSON surface so every frontend adapter
> (react / vue / vanilla-htmx / nexacro) can consume them in its own idiom.
>
> Status: M0 draft — brand color undecided. System-gray + 1 accent (blue-trust)
> are stable until brand is confirmed with CEO + CMO.

---

## 0. Two-Layer Architecture

```
raw tokens        →   semantic tokens   →   persona override tokens
(palette / scale)     (role-named)          (density / emphasis shift)

raw.blue-60       →   color.primary     →   [ceo]   color.primary (same, lighter bg)
raw.gray-90       →   color.text-base   →   [it]    color.text-base (monospace weight bump)
```

Components and adapters reference **semantic tokens only**.
Raw tokens are stable building blocks, never referenced by components directly.
Persona overrides are CSS class scopes (`.persona-ceo`, `.persona-ops`, `.persona-it`)
that re-define semantic tokens locally.

---

## 1. Raw Token Palette

### 1.1 Grays (system neutral)

| Token key         | Value   | Notes                          |
|-------------------|---------|-------------------------------|
| `raw.gray-0`      | #FFFFFF | pure white                     |
| `raw.gray-5`      | #F8F9FA | near-white surface             |
| `raw.gray-10`     | #F1F3F5 | subtle background              |
| `raw.gray-20`     | #E9ECEF | divider / border               |
| `raw.gray-30`     | #DEE2E6 | disabled border                |
| `raw.gray-40`     | #CED4DA | placeholder text bg            |
| `raw.gray-50`     | #ADB5BD | placeholder text, muted icon   |
| `raw.gray-60`     | #868E96 | secondary label                |
| `raw.gray-70`     | #495057 | body text (light mode)         |
| `raw.gray-80`     | #343A40 | heading (light mode)           |
| `raw.gray-90`     | #212529 | primary text, max contrast     |
| `raw.gray-100`    | #000000 | pure black                     |

### 1.2 Blue — Trust Accent (brand placeholder)

Blue is chosen for M0 because trust/authority reads as blue in Korean B2B market
(corporate ERP, banking, public sector).
When brand color is confirmed this palette is replaced — semantic layer
means only `raw.json` changes, components are unaffected.

| Token key         | Value   | Notes                          |
|-------------------|---------|-------------------------------|
| `raw.blue-5`      | #E8F4FD | very light tint, CEO card bg   |
| `raw.blue-10`     | #D0E8FA | light tint                     |
| `raw.blue-20`     | #A5CCF5 | hover state, focus ring base   |
| `raw.blue-40`     | #4D9DE0 | interactive, link              |
| `raw.blue-60`     | #1971C2 | primary action (AA on white)   |
| `raw.blue-70`     | #1864AB | primary action hover           |
| `raw.blue-80`     | #145591 | primary action active/pressed  |
| `raw.blue-90`     | #0F3F6B | dark mode primary              |

### 1.3 Semantic Status Colors

Status colors are used in badges, alerts, and IT-console indicators.
All values are chosen to meet WCAG AA contrast (4.5:1) against white `raw.gray-0`.

| Token key         | Value   | Usage                          | Contrast on #FFF |
|-------------------|---------|-------------------------------|------------------|
| `raw.green-60`    | #2B8A3E | success, operational, active   | 5.3:1  AA pass   |
| `raw.yellow-60`   | #E67700 | warning, pending, degraded     | 4.6:1  AA pass   |
| `raw.red-60`      | #C92A2A | error, critical, failed        | 5.8:1  AA pass   |
| `raw.orange-60`   | #D9480F | destructive action warning     | 5.1:1  AA pass   |
| `raw.purple-60`   | #6741D9 | info / system message          | 5.4:1  AA pass   |

### 1.4 Type Scale (rem, base 16px browser default)

| Token key         | rem    | px equivalent | Usage                           |
|-------------------|--------|---------------|---------------------------------|
| `raw.size-xs`     | 0.75   | 12            | label, badge, caption           |
| `raw.size-sm`     | 0.875  | 14            | secondary text, form helper     |
| `raw.size-base`   | 1.0    | 16            | body text — KWCAG min for AA    |
| `raw.size-md`     | 1.125  | 18            | card title, section subtitle    |
| `raw.size-lg`     | 1.25   | 20            | page subtitle                   |
| `raw.size-xl`     | 1.5    | 24            | page heading                    |
| `raw.size-2xl`    | 2.0    | 32            | CEO dashboard KPI number        |
| `raw.size-3xl`    | 2.5    | 40            | landing hero                    |

### 1.5 Spacing Scale (rem)

| Token key         | rem    | px   |
|-------------------|--------|------|
| `raw.space-1`     | 0.25   | 4    |
| `raw.space-2`     | 0.5    | 8    |
| `raw.space-3`     | 0.75   | 12   |
| `raw.space-4`     | 1.0    | 16   |
| `raw.space-5`     | 1.5    | 24   |
| `raw.space-6`     | 2.0    | 32   |
| `raw.space-7`     | 2.5    | 40   |
| `raw.space-8`     | 3.0    | 48   |
| `raw.space-10`    | 4.0    | 64   |
| `raw.space-12`    | 6.0    | 96   |

---

## 2. Semantic Tokens (16 minimum)

These are the tokens adapters and components use. Each maps to a raw value and
can be overridden per persona.

### 2.1 Color — Semantic

| Semantic key            | Default (light)     | Maps to raw        | Role                              |
|-------------------------|---------------------|--------------------|-----------------------------------|
| `color.primary`         | #1971C2             | raw.blue-60        | primary CTA, link, active tab     |
| `color.primary-hover`   | #1864AB             | raw.blue-70        | primary hover state               |
| `color.primary-subtle`  | #E8F4FD             | raw.blue-5         | tinted bg for cards / chips       |
| `color.danger`          | #C92A2A             | raw.red-60         | error, delete confirm, critical   |
| `color.warning`         | #E67700             | raw.yellow-60      | pending, at-risk, degraded        |
| `color.success`         | #2B8A3E             | raw.green-60       | operational, saved, online        |
| `color.info`            | #6741D9             | raw.purple-60      | system notice, tip                |
| `color.text-base`       | #212529             | raw.gray-90        | primary body text                 |
| `color.text-secondary`  | #495057             | raw.gray-70        | helper, secondary label           |
| `color.text-disabled`   | #ADB5BD             | raw.gray-50        | disabled field label              |
| `color.text-inverse`    | #FFFFFF             | raw.gray-0         | text on dark/primary bg           |
| `color.surface-1`       | #FFFFFF             | raw.gray-0         | page / card background            |
| `color.surface-2`       | #F8F9FA             | raw.gray-5         | sidebar / panel bg                |
| `color.surface-3`       | #F1F3F5             | raw.gray-10        | table row alt, input bg           |
| `color.border`          | #DEE2E6             | raw.gray-20        | default divider, input outline    |
| `color.focus-ring`      | #4D9DE0             | raw.blue-20        | keyboard focus outline (a11y)     |

### 2.2 Typography — Semantic

| Semantic key              | Default value       | Role                              |
|---------------------------|---------------------|-----------------------------------|
| `type.font-base`          | system-ui, sans-serif | body text stack (no brand font yet) |
| `type.font-mono`          | 'Cascadia Code', 'Consolas', monospace | IT console, code block |
| `type.size-body`          | raw.size-base (1rem) | standard readable body            |
| `type.size-heading`       | raw.size-xl (1.5rem) | page-level heading                |
| `type.size-label`         | raw.size-sm (0.875rem) | form labels, table headers      |
| `type.size-kpi`           | raw.size-2xl (2rem)  | CEO dashboard KPI numbers         |
| `type.weight-normal`      | 400                  | body                              |
| `type.weight-medium`      | 500                  | label, tab, nav item              |
| `type.weight-bold`        | 700                  | heading, KPI                      |
| `type.line-height-tight`  | 1.25                 | heading, KPI card                 |
| `type.line-height-base`   | 1.6                  | body text — WCAG SC 1.4.8         |
| `type.line-height-loose`  | 1.8                  | long-form reading (CEO brief)     |

### 2.3 Spacing — Semantic

| Semantic key              | Maps to             | Role                              |
|---------------------------|---------------------|-----------------------------------|
| `space.component-gap`     | raw.space-4 (16px)  | gap between form fields           |
| `space.section-gap`       | raw.space-6 (32px)  | gap between sections              |
| `space.card-pad`          | raw.space-5 (24px)  | card inner padding                |
| `space.table-cell-pad`    | raw.space-2 (8px)   | table cell padding (default)      |
| `space.inline-icon`       | raw.space-2 (8px)   | gap between icon and label        |

### 2.4 Shape / Elevation

| Semantic key          | Default value | Role                            |
|-----------------------|---------------|---------------------------------|
| `radius.sm`           | 4px           | badge, chip                     |
| `radius.md`           | 8px           | card, input, button             |
| `radius.lg`           | 12px          | modal, panel                    |
| `radius.pill`         | 999px         | tag, status pill                |
| `shadow.card`         | 0 1px 3px rgba(0,0,0,0.08) | default card lift |
| `shadow.modal`        | 0 8px 32px rgba(0,0,0,0.18) | modal overlay    |
| `shadow.focus`        | 0 0 0 3px color.focus-ring | keyboard focus   |

### 2.5 Motion

| Semantic key          | Default value | Note                              |
|-----------------------|---------------|-----------------------------------|
| `motion.duration-fast`  | 120ms        | micro-interaction (checkbox toggle) |
| `motion.duration-base`  | 200ms        | panel expand, tab switch          |
| `motion.duration-slow`  | 350ms        | modal open, page transition       |
| `motion.easing-default` | ease-in-out  | standard                          |
| `motion.easing-enter`   | ease-out     | element entering viewport         |
| `motion.easing-exit`    | ease-in      | element leaving viewport          |

`prefers-reduced-motion: reduce` is honored by every adapter: all duration values
collapse to 0ms and transforms are removed. This satisfies WCAG 2.3.3 (AAA) and
is required by KWCAG 2.1 항목 6.4 (움직임 제어).

---

## 3. Persona Override Tokens

Each persona is a CSS scope that re-declares selected semantic tokens.
The JSON equivalent is the `persona/<id>.json` file consumed by JS adapters.

### 3.1 Persona A — CEO (의사결정자)

**Design rationale**: CEO accesses 2–3 times per day, on a laptop or tablet, for
status checks and exception reviews. Information density is low. Headings are large,
whitespace is generous, KPI numbers dominate. Tone: authoritative, calm, trustworthy.
Color is used sparingly — accent only for action or alert.

CSS scope: `.persona-ceo`

| Token override                | CEO value           | Why                                    |
|-------------------------------|---------------------|----------------------------------------|
| `color.surface-1`             | #FFFFFF             | clean, no clutter                      |
| `color.surface-2`             | #F8F9FA             | card background is barely off-white    |
| `color.primary-subtle`        | #E8F4FD             | KPI card tint — calm blue              |
| `type.size-body`              | 1.125rem (18px)     | slightly larger for quick scan         |
| `type.size-heading`           | 1.75rem (28px)      | prominent section headers              |
| `type.size-kpi`               | 2.5rem (40px)       | KPI number large and unambiguous       |
| `type.line-height-base`       | 1.8                 | breathing room                         |
| `space.card-pad`              | 2rem (32px)         | generous card inner padding            |
| `space.section-gap`           | 3rem (48px)         | wide section separation                |
| `density.info-rows-visible`   | 5                   | max rows before "see more" collapses   |
| `density.table-compact`       | false               | no compact tables for CEO              |
| `motion.duration-base`        | 250ms               | slightly slower — feels deliberate     |

### 3.2 Persona B — 업무담당자 (현장 사용자)

**Design rationale**: Ops users work inside forms 4–6 hours a day. Efficiency is
the goal: keyboard navigation, clear field validation, predictable layouts.
Information density is medium. Users are used to enterprise ERP-style forms.
Color is used for form state (error/warning/success on fields), not decoration.

CSS scope: `.persona-ops`

| Token override                | Ops value           | Why                                    |
|-------------------------------|---------------------|----------------------------------------|
| `color.surface-1`             | #FFFFFF             | standard                               |
| `color.surface-3`             | #F1F3F5             | alternating row bg in work tables      |
| `type.size-body`              | 1rem (16px)         | compact but readable                   |
| `type.size-heading`           | 1.375rem (22px)     | moderate heading                       |
| `type.size-label`             | 0.875rem (14px)     | form labels                            |
| `type.line-height-base`       | 1.6                 | standard                               |
| `space.card-pad`              | 1.5rem (24px)       | standard                               |
| `space.table-cell-pad`        | 0.75rem (12px)      | slightly more than raw — scannable     |
| `space.component-gap`         | 1rem (16px)         | form fields breathe but are compact    |
| `density.info-rows-visible`   | 15                  | work table shows more rows             |
| `density.table-compact`       | false               | standard row height                    |
| `motion.duration-base`        | 200ms               | responsive feel                        |

### 3.3 Persona C — IT-담당자 (운영자)

**Design rationale**: IT staff read raw data, logs, config states, and error codes.
Information density is high. Monospace font for IDs, hostnames, log lines.
Color is used as signal (green=up, red=down, yellow=degraded) not decoration.
Status indicators must be immediately scannable — color + icon + text (never
color alone, per WCAG 1.4.1 and KWCAG 항목 7.1.2).

CSS scope: `.persona-it`

| Token override                | IT value            | Why                                    |
|-------------------------------|---------------------|----------------------------------------|
| `color.surface-1`             | #F8F9FA             | slight off-white reduces eye strain    |
| `color.surface-2`             | #F1F3F5             | panel / sidebar                        |
| `type.font-base`              | type.font-mono      | IDs, hostnames, paths in mono          |
| `type.size-body`              | 0.875rem (14px)     | compact — IT users expect density      |
| `type.size-heading`           | 1.25rem (20px)      | moderate                               |
| `type.size-label`             | 0.75rem (12px)      | table header, badge — small but clear  |
| `type.line-height-base`       | 1.5                 | dense but not cramped                  |
| `space.card-pad`              | 1rem (16px)         | tight                                  |
| `space.table-cell-pad`        | 0.5rem (8px)        | compact table rows                     |
| `space.component-gap`         | 0.75rem (12px)      | tight form groups                      |
| `density.info-rows-visible`   | 50                  | raw data tables show full pagination   |
| `density.table-compact`       | true                | compact row height                     |
| `motion.duration-base`        | 100ms               | fast — IT users prioritize response    |

---

## 4. Accessibility Floor

All tokens and any component consuming them must meet or exceed the following.
This is a mandatory gate — not a guideline — before any screen ships.

### 4.1 WCAG AA Requirements (minimum, all personas)

| Check                  | Requirement                               | How verified                     |
|------------------------|-------------------------------------------|----------------------------------|
| Text contrast          | 4.5:1 normal text, 3:1 large text (>=18px or >=14px bold) | All semantic color pairs listed in §5 |
| Non-text contrast      | 3:1 for UI components and state borders    | focus ring, input border, icon    |
| Focus visible (2.4.7)  | Focus indicator visible at all times       | `shadow.focus` token + no outline:none |
| Focus appearance (2.4.11, AA in WCAG 2.2) | Focus area >= component perimeter, offset >= 2px | `shadow.focus` = 3px ring |
| Reflow (1.4.10)        | No horizontal scroll at 320px viewport    | Enforced by layout patterns       |
| Text resize (1.4.4)    | Text resizable to 200% without loss       | rem-based type scale (§1.4)       |
| Use of color (1.4.1)   | Color never the sole differentiator       | Status = color + icon + text      |
| Motion (2.3.3)         | Reduced-motion honored                    | motion tokens collapse to 0ms     |

### 4.2 KWCAG 2.1 Additional Requirements (Korean market gate)

KWCAG 2.1 (한국형 웹 콘텐츠 접근성 지침) adds or tightens several items
relevant to this product's target market (중소·중견기업, 금융·의료·제조).

| KWCAG 항목 | Requirement                                  | CDO token / pattern note              |
|------------|----------------------------------------------|---------------------------------------|
| 항목 1.1.1 | Non-text content has text alternative        | All icons require aria-label or title |
| 항목 1.3.1 | Info and relationships via markup            | Tables use `<th scope>`, forms use `<label for>` |
| 항목 1.4.1 | Color not used as sole visual means          | Status: color.success/warning/danger + icon glyph |
| 항목 1.4.3 | Minimum contrast 4.5:1 (same as WCAG)        | Verified in §5 contrast table         |
| 항목 2.1.1 | All functions operable by keyboard           | Tab order, Enter/Space activation enforced |
| 항목 2.1.2 | No keyboard trap                             | Modal focus lock must have Esc release |
| 항목 2.4.3 | Focus order — logical sequence               | DOM order = visual order in all layouts |
| 항목 2.4.7 | Focus visible                                | `shadow.focus` token mandatory        |
| 항목 3.1.1 | Language of page declared                    | `<html lang="ko">` (or "en" for English mode) |
| 항목 6.4   | User controls motion/animation               | prefers-reduced-motion respected       |

### 4.3 Focus State Specification

Every interactive element that can receive keyboard focus must render:

```
outline: 3px solid var(--color-focus-ring);  /* #4D9DE0 — 3:1 on white */
outline-offset: 2px;
```

No adapter may override this with `outline: none` or `outline: 0` on a focusable
element without providing an equivalent visible custom focus indicator.

The 3px width + 2px offset meets WCAG 2.4.11 (Focus Appearance, AA in 2.2) —
a perimeter >= the longer of: 2 CSS pixels or the component perimeter.

### 4.4 Minimum Touch Target

For mobile / tablet (CEO persona is likely on iPad):

- Minimum touch target: 44x44px (WCAG 2.5.5 AAA, but enforced as AA-equivalent
  for tablet surfaces)
- Minimum tap target spacing: 8px gap between adjacent targets

---

## 5. Contrast Reference Table

Critical color pairs for spot-checking during component implementation.

| Foreground              | Background              | Ratio  | Pass |
|-------------------------|-------------------------|--------|------|
| color.text-base (#212529) | color.surface-1 (#FFF) | 16.1:1 | AAA  |
| color.text-secondary (#495057) | color.surface-1 (#FFF) | 7.4:1 | AAA |
| color.primary (#1971C2) | color.surface-1 (#FFF) | 5.0:1  | AA   |
| color.text-inverse (#FFF) | color.primary (#1971C2) | 5.0:1 | AA   |
| color.danger (#C92A2A)  | color.surface-1 (#FFF)  | 5.8:1  | AA   |
| color.warning (#E67700) | color.surface-1 (#FFF)  | 4.6:1  | AA   |
| color.success (#2B8A3E) | color.surface-1 (#FFF)  | 5.3:1  | AA   |
| color.text-disabled (#ADB5BD) | color.surface-1 (#FFF) | 2.3:1 | INTENTIONAL FAIL — disabled state is exempt per WCAG 1.4.3 |
| color.text-base (#212529) | color.surface-3 (#F1F3F5) | 13.9:1 | AAA |
| color.primary (#1971C2) | color.primary-subtle (#E8F4FD) | 4.6:1 | AA |

---

## 6. Display Token Summary (Persona x Category Matrix)

Quick reference for adapter implementors.

| Token category      | CEO              | 업무담당자 (Ops)  | IT-담당자        |
|---------------------|------------------|------------------|------------------|
| Base font size      | 18px             | 16px             | 14px             |
| KPI / headline size | 40px             | 22px             | 20px             |
| Font family         | system-ui        | system-ui        | monospace        |
| Line height         | 1.8              | 1.6              | 1.5              |
| Card padding        | 32px             | 24px             | 16px             |
| Table cell padding  | 16px (inherited) | 12px             | 8px              |
| Visible rows (table)| 5 + collapse     | 15               | 50               |
| Table compact mode  | off              | off              | on               |
| Motion duration     | 250ms            | 200ms            | 100ms            |
| Info density label  | LOW              | MEDIUM           | HIGH             |

---

## 7. Adapter Portability Contract

Tokens are published in two surfaces. Adapters must consume exactly one of these
surfaces — never hardcode values from this document.

### 7.1 CSS Custom Properties (react / vue / vanilla-htmx)

Tokens are declared on `:root` for the default (ops) persona, with persona scopes
overriding relevant keys.

```css
/* example — not exhaustive */
:root {
  --color-primary:         #1971C2;
  --color-danger:          #C92A2A;
  --color-text-base:       #212529;
  --color-surface-1:       #FFFFFF;
  --color-focus-ring:      #4D9DE0;
  --type-size-body:        1rem;
  --type-line-height-base: 1.6;
  --space-card-pad:        1.5rem;
  --radius-md:             8px;
  --motion-duration-base:  200ms;
}

.persona-ceo {
  --type-size-body:        1.125rem;
  --type-size-kpi:         2.5rem;
  --type-line-height-base: 1.8;
  --space-card-pad:        2rem;
  --motion-duration-base:  250ms;
}

.persona-it {
  --type-font-base:        'Cascadia Code', 'Consolas', monospace;
  --type-size-body:        0.875rem;
  --type-line-height-base: 1.5;
  --space-card-pad:        1rem;
  --space-table-cell-pad:  0.5rem;
  --motion-duration-base:  100ms;
}
```

### 7.2 JSON Token Surface (nexacro / server-side template engines / design tools)

Token values are exported as flat JSON (format follows Style Dictionary convention)
so Nexacro adapter, Figma token plugin, and any non-CSS consumer can import them.

```json
{
  "color": {
    "primary":        { "value": "#1971C2",  "comment": "AA on white 5.0:1" },
    "danger":         { "value": "#C92A2A",  "comment": "AA on white 5.8:1" },
    "text-base":      { "value": "#212529"  },
    "surface-1":      { "value": "#FFFFFF"  },
    "focus-ring":     { "value": "#4D9DE0"  }
  },
  "type": {
    "size-body":      { "value": "1rem"     },
    "size-kpi":       { "value": "2rem"     },
    "line-height-base": { "value": 1.6      }
  },
  "persona": {
    "ceo": {
      "type.size-body":        { "value": "1.125rem" },
      "type.size-kpi":         { "value": "2.5rem"   },
      "type.line-height-base": { "value": 1.8         },
      "space.card-pad":        { "value": "2rem"      }
    },
    "ops": {},
    "it": {
      "type.font-base":        { "value": "'Cascadia Code', 'Consolas', monospace" },
      "type.size-body":        { "value": "0.875rem" },
      "type.line-height-base": { "value": 1.5         },
      "space.card-pad":        { "value": "1rem"      }
    }
  }
}
```

### 7.3 Nexacro-Specific Note

Nexacro does not support CSS custom properties natively. The Nexacro adapter must
read the JSON surface (`persona/<id>.json`) and inject values into Nexacro's
theme XTHEME file. The mapping is:
- `color.*` → Nexacro `ThemeColor` entries
- `type.size-*` → Nexacro `Font.size` entries
- `space.*` → Nexacro `Margin` / `Padding` entries

This mapping is owned by the Nexacro frontend adapter, not by this token document.
Token values here remain the single source.

---

## 8. Persona x Milestone Alignment

Tokens evolve as the product moves through milestones.
Decisions locked at each gate:

| Milestone | Token change                                           | Persona impact                                    |
|-----------|--------------------------------------------------------|--------------------------------------------------|
| **M0**    | This document. Gray + blue-trust. Persona density defined. | All 3 personas have a base token set.         |
| **M1**    | Brand accent finalized (CEO + CMO decision). raw.blue replaced with real brand color. semantic layer unchanged. | Demo-ready visuals. |
| **M2**    | First customer's stack.frontend confirmed → adapter-specific token verification. Dark mode question resolved (see §9). | Ops + IT personas tested in production. |
| **M3**    | First vertical's domain-specific status colors (e.g., medical risk levels, manufacturing OEE tiers). | New `raw.domain-*` tokens added without touching semantic layer. |
| **M4**    | External contributor token compliance gate added to adapter compliance test. | Community adapters must pass token contract. |
| **M5**    | Multi-tenant theming: tenant-level brand override on top of persona tokens (3-layer: raw → semantic → persona → tenant). | Each tenant customer can supply their logo + primary color. |

---

## 9. Open Questions for CTO

These decisions require CTO (wire-protocol / stack) input or cross-agent resolution.

1. **Dark mode policy**: Should dark mode be a persona-level token override or a
   separate full token set? IT-담당자 most likely to want dark mode (long sessions,
   terminal familiarity). Decision affects CSS variable structure and Nexacro XTHEME
   file count. CDO recommendation: dark mode as a second CSS scope
   (`.theme-dark.persona-it`) — but this doubles the Nexacro theme files.
   CTO + CDO alignment needed before M1 adapter work begins.

2. **i18n label tokens**: swappable-layers.md §8 prefers labels in contract
   (Korean/English in customer profile). Does the token layer own the
   `lang` attribute injection, or does each adapter manage it independently?
   If the token layer owns it, a `locale.*` token group is needed here.

3. **Token versioning**: When raw.blue is replaced by brand color at M1,
   does the semantic layer guarantee no downstream adapter breakage?
   CDO says yes (semantic abstraction holds), but CTO should confirm the
   adapter compliance test covers token-value changes (not just schema changes).

4. **CEO persona — mobile breakpoint**: CEO is described as accessing on laptop
   or tablet (positioning.md Persona A). Should CEO persona tokens include
   responsive overrides (e.g., `type.size-kpi` drops from 40px to 28px at
   viewport < 768px)? This would add a `breakpoint.*` token group.

---

## 10. JSON Token Files (canonical paths)

The actual machine-readable token files live at:

```
docs/design/
  tokens.md              <- this document (human-readable spec)
  tokens/
    raw.json             <- palette + scale (M1: update brand color here only)
    semantic.json        <- 16+ semantic keys
    persona/
      ceo.json           <- CEO overrides
      ops.json           <- ops overrides (empty = all defaults apply)
      it.json            <- IT overrides
```

These JSON files are the source consumed by adapters. This `.md` file is the
specification document that governs what goes into them.
The JSON files are to be generated from this spec by the engineer agent at M1
(task: translate §1–§3 tables into Style Dictionary JSON).

---

## 11. CTO Decisions (Growth-5c, 2026-05-29)

§9 의 4 open questions 에 대한 CTO 응답.

| Q  | Decision                              | Rationale (1줄)                                   | Next step                              |
|----|---------------------------------------|---------------------------------------------------|-----------------------------------------|
| Q1 | Dark mode 보류 (M0~M1 light only)    | M2 첫 고객 IT 페르소나 실사용 패턴 확인 후 결정    | 추천안 `.theme-dark.persona-it` 메모 보존 |
| Q2 | i18n label 소유권 = adapter           | token 층은 시각만, `<html lang>` + label 은 adapter | `locale.*` token group 추가 안 함         |
| Q3 | Token versioning compliance test = YES| brand color (raw.blue → 실 brand) 교체 시 actual value 변경도 verify | Engineer 가 M1 adapter 작성 시 fixture 에 token snapshot 포함 |
| Q4 | CEO mobile breakpoint = 추가          | iPad 사용 시 KPI 40px 가 viewport 압도            | `breakpoint.tablet: 768px` + CEO `type.size-kpi` 28px / `space.section-gap` 32px override |

§3.1 CEO 페르소나 표에 추가할 row (CDO 가 다음 Growth 에서 박음):
- `breakpoint.tablet` | 768px | < 768px 에서 viewport 초과 회피
- override < 768px: `type.size-kpi` 28px, `space.section-gap` 32px
