# Theme Library — Asset Index

> Visual-asset axis (8th axis) of the compound model (CLAUDE.md §3).
> Each theme is a `presets/themes/<slug>/` directory containing `theme.yaml` + `README.md`.
> Format: [`_theme-format.md`](_theme-format.md). Motion presets: [`_motion/presets.yaml`](_motion/presets.yaml).
>
> Themes inherit `design/tokens/semantic.json` as base and declare overrides only.
> Consumed by `frontend/adapters/landing-astro/` (Astro + Tailwind SSG).

---

## Registered Themes

| Slug | Name | Tone | Industry Fit | Persona Fit | A11y AA | Added |
|---|---|---|---|---|---|---|
| [aurora](aurora/theme.yaml) | Aurora | Bold gradient / SaaS energy | SaaS, fintech, tech startup, B2B platform | CEO-forward, ops secondary | PASS | 2026-06-15 |
| [studio](studio/theme.yaml) | Studio | Minimal editorial / portfolio | Creative agency, consulting, professional services, architecture | CEO, ops | PASS | 2026-06-15 |
| [harvest](harvest/theme.yaml) | Harvest | Warm drenched craft / artisan | Craft beverage, brewery, food CPG, artisan hospitality | CEO | PASS | 2026-06-15 |
| [atelier](atelier/theme.yaml) | Atelier | Ink-pressed deliberate sparse | Creative studio, design consultancy, architecture, portfolio | CEO, ops | PASS | 2026-06-15 |
| [kiln](kiln/theme.yaml) | Kiln | Earthen material handcraft | Artisan ceramics, craft studio, pottery, local maker, artisan F&B | CEO, ops | PASS | 2026-06-15 |
| [meridian](meridian/theme.yaml) | Meridian | Precise cool-stone / B2B advisory | Managed-IT, security advisory, consulting, professional services | CEO, ops, IT | PASS | 2026-06-16 |

---

## Default Theme Resolution

site-manifest 의 `theme:` 가 `default` 이거나 생략된 경우, landing-astro 어댑터는
**flagship = `aurora`** 로 해소한다. 알 수 없는 slug 는 경고 후 동일 폴백.

## Motion Presets

Shared across all themes. See [`_motion/presets.yaml`](_motion/presets.yaml) for full spec.

| Slug | Summary |
|---|---|
| `fade-simple` | Opacity 0→1, no transform. Reduced-motion safe anchor. |
| `fade-up` | Opacity 0→1 + translateY 24px→0. Standard entrance. |
| `stagger-children` | Parent triggers children with 80ms offset each. |
| `hover-lift` | translateY -4px + shadow deepen on hover. |
| `parallax-lite` | Section bg moves at 0.3× scroll speed (CSS only, no JS). |
| `reveal-on-scroll` | IntersectionObserver triggers fade-up when element enters viewport. |
| `slide-in-left` | translateX -40px→0 + opacity. For split-left hero media. |
| `scale-in` | scale 0.96→1 + opacity. For modal/card entrance. |

---

## Adding a Theme

1. Create `presets/themes/<slug>/theme.yaml` (follow `_theme-format.md`)
2. Create `presets/themes/<slug>/README.md`
3. Add a row to the table above
4. CDO a11y self-check: fill `theme.yaml a11y.wcag_aa_pairs` (minimum 3 pairs)
5. CTO review → file-per-commit (CLAUDE.md §9)

## Invariants

- ASCII slug only (G-8)
- No theme may redefine `raw.json` primitives — override semantic keys only
- `theme.yaml` must be pure declarative YAML (no code, no logic)
- `reduced_motion_fallback` must always point to `fade-simple`
- 웹폰트는 **self-host**(Fontsource npm 등) — 외부 CDN(Google Fonts 등) 금지. self-host 원칙(CLAUDE.md) + 방문자 IP 프라이버시. 어댑터가 번들에 포함하고 `font-display: swap`.
