# Theme Format — Single Source of Truth

> CDO 결정 (Growth-Phase-2, 2026-06-15). `presets/themes/<slug>/theme.yaml` 은
> visual-asset 축 (8번째 축) 의 단일 진실. 각 테마는 `design/tokens/semantic.json`
> 을 base 로 상속하고 **override 만** 선언한다 — 재정의 또는 중복 금지.
> 소비자: `frontend/adapters/landing-astro/` (Astro + Tailwind SSG).

---

## 1. 상속 규약

```
raw.json  →  semantic.json  →  theme.yaml (override)  →  persona/*.json (further override)
```

- `theme.yaml` 은 `semantic.json` 의 키를 override 할 수 있다.
- `raw.json` 의 palette 값을 직접 재정의하는 것은 금지 — raw 값은 **raw.json 만** 소유.
- 테마는 `{color.accent.600}` 같은 raw reference 표현이 아닌 **실제 hex/CSS 값** 을 선언.
  - 이유: theme.yaml 을 읽는 Tailwind config 빌더가 raw.json 의 reference resolver 를
    실행하지 않아도 되도록 (zero-dependency 파싱).
- 테마가 선언하지 않은 토큰은 semantic.json 값이 그대로 적용된다.

---

## 2. theme.yaml 스키마

```yaml
# ── Identity ──────────────────────────────────────────────────────────────────
slug: <ascii-slug>              # 파일명 디렉터리명 일치 (G-8)
name: <Human Label>
version: "1.0.0"
description: <1-sentence aesthetic summary>
persona_fit:                    # 어느 고객 페르소나/업종에 적합한가
  personas: [ceo, ops, it]     # 적합한 내부 페르소나 (optional)
  industry_tags: []             # 예: [saas, fintech, creative, consulting]
  tone: <e.g. "bold energetic" | "minimal editorial">

# ── Color Override ─────────────────────────────────────────────────────────────
# Keys must match semantic.json color.* keys exactly. Unknown keys are rejected.
color:
  primary: <hex>
  primary-hover: <hex>
  primary-active: <hex>
  primary-subtle: <hex>
  primary-border: <hex>
  surface-1: <hex>
  surface-2: <hex>
  surface-3: <hex>
  text-1: <hex>
  text-2: <hex>
  text-3: <hex>
  text-link: <hex>
  text-link-hover: <hex>
  # theme-specific additions (landing-only, not in semantic.json):
  hero-bg-from: <hex>           # gradient start (if hero uses gradient bg)
  hero-bg-to: <hex>             # gradient end
  section-alt-bg: <hex>         # alternating section background
  accent-glow: <rgba>           # optional glow for hero elements

# ── Typography Override ────────────────────────────────────────────────────────
# Keys must match semantic.json font.* keys or extend with landing-specific keys.
font:
  family-display: <CSS font stack>   # landing heading font (may differ from body)
  family-body: <CSS font stack>      # override base sans if needed
  # Landing-specific scale extensions (larger than app UI needs):
  size-5xl: <px>               # hero headline: 48px
  size-6xl: <px>               # hero headline large: 60px
  size-7xl: <px>               # hero headline XL: 72px (desktop only)
  line-5xl: <px>
  line-6xl: <px>
  line-7xl: <px>
  weight-display: <CSS weight> # display/hero heading weight (e.g. 800)
  letter-spacing-display: <em> # tracking for display text (e.g. -0.02em)
  letter-spacing-body: <em>

# ── Spacing Override ───────────────────────────────────────────────────────────
# Section-level spacing — extends semantic.json space.* (app UI has no section gap)
space:
  section-y: <px>              # vertical padding per section (e.g. 96px)
  section-y-mobile: <px>       # mobile (e.g. 64px)
  container-max: <px>          # max content width (e.g. 1200px)
  container-gutter: <px>       # horizontal padding at smallest breakpoint

# ── Radius Override ────────────────────────────────────────────────────────────
radius:
  card: <px>
  button: <px>
  badge: <px>
  hero-media: <px>             # image/video in hero section

# ── Shadow Override ────────────────────────────────────────────────────────────
shadow:
  card: <CSS box-shadow>
  hero-media: <CSS box-shadow>
  cta-band: <CSS box-shadow>

# ── Motion ────────────────────────────────────────────────────────────────────
# References slugs from presets/themes/_motion/presets.yaml.
# Do NOT inline motion values here — reference only.
motion:
  default_preset: <motion-slug>   # applied to any section without explicit override
  section_presets:                # per-section-type override
    hero: <motion-slug>
    logos: <motion-slug>
    features: <motion-slug>
    pricing: <motion-slug>
    testimonial: <motion-slug>
    faq: <motion-slug>
    cta: <motion-slug>
    footer: <motion-slug>
  reduced_motion_fallback: fade-simple   # must always point to a valid slug

# ── Section Variant Styles ─────────────────────────────────────────────────────
# Maps catalog variant names (presets/site-sections/catalog.yaml) to style hints.
# The Astro adapter reads these hints and applies Tailwind classes accordingly.
# Style hint keys are standardised (see §3). Unknown hint keys are ignored (open).
sections:
  hero:
    centered:
      bg: gradient                # solid | gradient | image | video | none
      text_align: center
      cta_style: primary-lg       # primary-lg | primary-outline | ghost
      media_position: below       # above | below | behind | none
    split-left:
      bg: solid
      text_align: left
      cta_style: primary-lg
      media_position: right
    split-right:
      bg: solid
      text_align: left
      cta_style: primary-lg
      media_position: left
    fullscreen-video:
      bg: video
      text_align: center
      cta_style: primary-outline
      media_position: behind

  logos:
    horizontal-scroll:
      filter: grayscale           # none | grayscale | grayscale-hover
      divider: none               # none | top | bottom | both
    grid:
      filter: grayscale
      divider: bottom

  features:
    three-col-icon:
      icon_style: filled          # filled | outline | emoji
      card_style: flat            # flat | elevated | bordered | ghost
      layout: grid-3
    two-col-alternating:
      icon_style: none
      card_style: ghost
      layout: alternating
    single-col-list:
      icon_style: outline
      card_style: ghost
      layout: stack

  pricing:
    two-tier:
      highlight_tier: none        # none | left | right | index (0-based)
      card_style: elevated
      show_toggle: false
    three-tier:
      highlight_tier: 1           # middle tier highlighted
      card_style: elevated
      show_toggle: false
    toggle-annual-monthly:
      highlight_tier: 1
      card_style: elevated
      show_toggle: true

  testimonial:
    single-card:
      layout: centered
      quote_style: large          # large | normal
      avatar: circle              # circle | square | none
    carousel:
      layout: centered
      quote_style: normal
      avatar: circle
      autoplay: false             # never autoplay (a11y: 2.2 enough time)
    grid:
      layout: grid-3
      quote_style: normal
      avatar: circle

  faq:
    single-col:
      divider: line               # line | space | none
      icon: chevron               # chevron | plus | arrow
      animation: collapse         # collapse | fade (reference motion preset via adapter)
    two-col:
      divider: line
      icon: chevron
      animation: collapse

  cta:
    centered:
      bg: primary                 # primary | dark | light | gradient
      text_align: center
      cta_style: inverse-lg       # inverse-lg = white btn on dark bg
    left-aligned:
      bg: dark
      text_align: left
      cta_style: inverse-lg
    with-image:
      bg: light
      text_align: left
      cta_style: primary-lg
      media_position: right

  footer:
    minimal:
      cols: 1
      show_social: false
      divider: top
    full-links:
      cols: 4
      show_social: true
      divider: top
    newsletter:
      cols: 2
      show_social: true
      show_newsletter_form: true
      divider: top

# ── A11y Self-check ───────────────────────────────────────────────────────────
# CDO fills this block when publishing a theme. Machine-readable for G-15 gate.
a11y:
  contrast_checked: true
  wcag_aa_pairs:                  # spot-checked pairs; not exhaustive
    - bg: <hex>
      fg: <hex>
      ratio: <float>
      note: <context>
  kwcag_notes: <free text>
  reduced_motion_safe: true       # true if reduced_motion_fallback is set
```

---

## 3. Section style hint vocabulary (closed set)

Astro adapter maps these to Tailwind utilities. Extensions require CTO+CDO agreement.

| Key | Type | Values |
|---|---|---|
| `bg` | string | `solid` `gradient` `image` `video` `none` `primary` `dark` `light` |
| `text_align` | string | `left` `center` `right` |
| `cta_style` | string | `primary-lg` `primary-outline` `ghost` `inverse-lg` |
| `media_position` | string | `above` `below` `behind` `left` `right` `none` |
| `filter` | string | `none` `grayscale` `grayscale-hover` |
| `divider` | string | `none` `top` `bottom` `both` `line` `space` |
| `icon_style` | string | `filled` `outline` `emoji` `none` |
| `card_style` | string | `flat` `elevated` `bordered` `ghost` |
| `layout` | string | `grid-3` `alternating` `stack` `centered` `grid-2` |
| `quote_style` | string | `large` `normal` |
| `avatar` | string | `circle` `square` `none` |
| `autoplay` | bool | false only — autoplay is a11y violation (WCAG 2.2.2) |
| `highlight_tier` | int\|string | tier index (0-based) or `none` |
| `show_toggle` | bool | pricing annual/monthly toggle |
| `show_social` | bool | footer social links |
| `show_newsletter_form` | bool | footer newsletter |
| `cols` | int | footer columns |
| `icon` | string | `chevron` `plus` `arrow` |
| `animation` | string | `collapse` `fade` |

---

## 4. Tailwind / CSS Custom Property 매핑 규칙

`scripts/build-tokens.mjs` (P3 어댑터 내부) 가 `theme.yaml` 을 읽어:

1. `color.*` → CSS custom properties `--color-<key>` + Tailwind `theme.extend.colors`
2. `font.family-*` → Tailwind `theme.extend.fontFamily`
3. `font.size-*` → Tailwind `theme.extend.fontSize` (key는 `5xl`/`6xl`/`7xl`)
4. `space.section-y` → Tailwind `theme.extend.spacing.section-y`
5. `radius.*` → Tailwind `theme.extend.borderRadius`
6. `shadow.*` → Tailwind `theme.extend.boxShadow`

CSS custom properties 는 `:root {}` 에 선언 → Tailwind 의 `var(--color-*)` 참조.

---

## 5. Motion 참조 규약

`motion.section_presets.<section>` 의 값은 `presets/themes/_motion/presets.yaml` 의
`presets[].slug` 중 하나여야 한다. 알 수 없는 slug 는 빌드 경고 (warn, not error).

`reduced_motion_fallback` 은 항상 `fade-simple` 을 가리켜야 한다 — 이 프리셋은
`presets.yaml` 의 불변 항목이며 삭제 불가.

Astro adapter 는 `prefers-reduced-motion: reduce` 미디어 쿼리를 감지하면
`reduced_motion_fallback` 프리셋만 적용한다 (WCAG 2.3.3 준수).

---

## 6. 파일 구조 컨벤션

```
presets/themes/
  _theme-format.md          # 이 문서
  _INDEX.md                 # 등록된 테마 인덱스
  _motion/
    presets.yaml            # 재사용 모션 프리셋 (참조 전용)
  <slug>/
    theme.yaml              # 토큰 override + 섹션 스타일 + motion 매핑
    README.md               # 미감·용도·페르소나 적합성
```

`<slug>` 는 ASCII lowercase kebab (G-8). 예: `aurora`, `studio`, `obsidian`, `bloom`.

---

## 7. 새 테마 등록 절차

1. `presets/themes/<slug>/theme.yaml` 생성 — 이 포맷 준수
2. `presets/themes/<slug>/README.md` 생성
3. `presets/themes/_INDEX.md` 에 행 추가
4. a11y 자체 점검: `a11y.wcag_aa_pairs` 최소 3쌍 기록
5. CTO 검수 후 파일당 별도 커밋 (CLAUDE.md §9)

---

## 8. 금지 사항 (Invariants)

- `raw.json` 의 primitive 이름 재사용 금지 (namespace collision)
- `theme.yaml` 에 JS/Python 로직 삽입 금지 — **순수 선언 데이터** 만
- hex 외의 색: `rgba(…)` 는 glow/overlay 한정, `hsl()` 은 현재 미지원
- autoplay 설정 금지 (a11y WCAG 2.2.2)
- 테마가 `middle/contract/` 를 참조하거나 변경하는 것 금지 (G-1)
