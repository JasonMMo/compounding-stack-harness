# landing-astro — Marketing Site Frontend Adapter

Astro + Tailwind SSG adapter for the `marketing-site` deliverable kind.
Reads `out/<slug>/site-manifest.json` at build time and generates one static
HTML page per `site.pages[]` entry.

Part of the **visual-asset (8th) axis** — compounding-stack-harness.

---

## Quick Start

```bash
# 1. Generate site-manifest for your profile (repo root)
python scripts/workflow/scaffold.py --profile agency-demo

# 2. Install adapter dependencies
cd frontend/adapters/landing-astro
npm install

# 3. Codegen + build tokens + build site
npm run build

# 4. Preview
npm run preview
```

The build pipeline (`npm run build`) runs three steps:

1. `node scripts/codegen.mjs` — generates `src/lib/contract.gen.ts` from `middle/contract/wire-v1.yaml`
2. `node scripts/build-tokens.mjs <theme>` — generates `src/styles/tokens.gen.css` + `src/styles/tailwind-theme.gen.js`
3. `astro build` — SSG, emits `dist/`

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `PUBLIC_SITE_MANIFEST` | `out/agency-demo/site-manifest.json` (repo root) | Absolute path to site-manifest.json |
| `PUBLIC_API_BASE` | `""` (relative) | Base URL for API calls (contact form POST). Example: `https://api.example.com` |

Set in `.env.local` (gitignored) or pass at build time:

```bash
PUBLIC_SITE_MANIFEST=/path/to/out/my-client/site-manifest.json \
PUBLIC_API_BASE=https://api.my-client.com \
npm run build
```

---

## Theme Resolution (DEC-1)

| `site-manifest.theme` | Resolved theme |
|---|---|
| `aurora` | `presets/themes/aurora/theme.yaml` (flagship) |
| `studio` | `presets/themes/studio/theme.yaml` |
| `default` | Falls back to `aurora` (warning emitted to stderr) |
| unknown slug | Falls back to `aurora` (warning emitted to stderr) |

Build a specific theme:

```bash
node scripts/build-tokens.mjs aurora   # or studio
```

---

## Self-Hosted Fonts (DEC-2)

No external CDN. Fonts are bundled via `@fontsource` npm packages:

| Theme | Display font | Body font |
|---|---|---|
| aurora | Plus Jakarta Sans | Inter |
| studio | DM Serif Display | DM Sans |

`font-display: swap` is the `@fontsource` package default.

---

## Contact Form — Backend Pairing (DEC-5)

The contact form (`src/components/ContactForm.astro`) POSTs to the `entity.create` wire key:

```
POST <PUBLIC_API_BASE>/api/entities/lead
Content-Type: application/json

{
  "entity_type": "lead",
  "data": { "name": "...", "email": "...", "message": "..." }
}
```

**Backend adapter responsibility (P3 scope boundary):**
- The paired backend adapter must handle `POST /api/entities/lead`
- It must persist the lead record (database, CRM, or email)
- Response: `{ entity_type: "lead", id: "<generated>", data: {...} }`

No new wire key was created — `entity.create` is reused (G-1 open-closed).

---

## Section Components

All 8 section types from `presets/site-sections/catalog.yaml` are implemented:

| Type | Component | Variants |
|---|---|---|
| `hero` | `src/sections/Hero.astro` | centered, split-left, split-right, fullscreen-video |
| `logos` | `src/sections/Logos.astro` | horizontal-scroll, grid |
| `features` | `src/sections/Features.astro` | three-col-icon, two-col-alternating, single-col-list |
| `pricing` | `src/sections/Pricing.astro` | two-tier, three-tier, toggle-annual-monthly |
| `testimonial` | `src/sections/Testimonial.astro` | single-card, carousel, grid |
| `faq` | `src/sections/Faq.astro` | single-col, two-col |
| `cta` | `src/sections/Cta.astro` | centered, left-aligned, with-image |
| `footer` | `src/sections/Footer.astro` | minimal, full-links, newsletter |

---

## Motion

Motion presets from `presets/themes/_motion/presets.yaml` are implemented via
a lightweight inline `IntersectionObserver` island in `BaseLayout.astro`.

- `prefers-reduced-motion: reduce` → all animations fall back to `fade-simple` (CSS `@media`, no JS needed)
- No autoplay on any component (WCAG 2.2.2 invariant)

### Intro Overlay (one-time splash)

**동작**: 사이트 첫 방문 시 브랜드 워드마크가 전체 화면 오버레이로 잠깐 노출된 뒤 퇴장 애니메이션으로 사라진다.

**motion 다이얼 게이트**: `site.motion=subtle` 또는 `rich` 일 때만 `IntroOverlay` 마크업이 HTML 에 출력된다. `motion=off` 시 마크업 자체가 없으므로 콘텐츠는 즉시 가시.

**한 번만 재생**: `sessionStorage` 키 `landing-intro-played` 로 제어. 같은 세션 내 재방문 및 Astro View Transition 내비게이션 시 오버레이를 재생하지 않는다. `astro:page-load` 이벤트에 리스너를 등록해 VT 이후에도 항상 세션 키를 재확인한다.

**소비 토큰**:
- `--motion-duration-intro` (900ms) — 퇴장 animation-duration
- `--motion-ease-emphasized` (`cubic-bezier(0.16,1,0.3,1)`) — 퇴장 animation-timing-function

**G-69 보장 (4가지 경로)**:

| 경로 | 처리 방식 |
|---|---|
| JS 비활성화 | CSS 기본 상태가 `opacity:0; visibility:hidden` — `.is-active` 미추가 → 콘텐츠 즉시 가시 |
| `motion=off` | `isMotionOn` 게이트로 마크업 자체가 미출력 |
| `prefers-reduced-motion: reduce` | JS early-return + CSS `display:none !important` (belt-and-suspenders) |
| 세션 재방문 / VT nav | `sessionStorage` 키 존재 → JS early-return → 오버레이 숨김 상태 유지 |

**구현 파일**:
- `src/components/IntroOverlay.astro` — 마크업 + `<script>` 로직
- `src/styles/global.css` — `.intro-overlay` 상태별 CSS + `@keyframes intro-overlay-exit` + reduced-motion block

---

### Page Transitions (Brick-3b)

**동작**: `site.motion=subtle` 또는 `rich` 을 설정하면 Astro View Transitions API 기반 페이지 전환이 자동 적용된다. 전환 효과는 cross-fade(opacity) + 미세 상승(translateY 8px→0) — 절제된 impeccable floor 준수.

**motion 다이얼 게이트**:

| `site.motion` | `<ViewTransitions />` | 페이지 전환 |
|---|---|---|
| `off` (기본) | 미탑재 | 표준 풀-페이지 내비게이션 (전환 JS 0) |
| `subtle` | 탑재 | cross-fade + micro-rise (280ms) |
| `rich` | 탑재 | cross-fade + micro-rise (280ms) |

**적용 조건**: `BaseLayout.astro`의 `isMotionOn` 게이트(`motion === 'subtle' || 'rich'`) 로 제어. 고객이 profile에서 `site.motion: subtle` 한 줄만 켜면 모든 페이지에 자동 적용된다.

**G-69 보장**: `motion=off` 시 `<ViewTransitions />` 태그 자체가 HTML에 미출력 → 관련 JS/메타 0바이트. 콘텐츠는 항상 즉시 가시.

**폴백**:
- `prefers-reduced-motion: reduce` → `::view-transition-old/new(root) { animation: none !important }` (즉시 스왑, WCAG 2.3.3)
- View Transitions API 미지원 브라우저 → Astro 내장 폴백으로 일반 내비게이션 자동 전환 (추가 처리 불필요)

**소비 토큰**:
- `--motion-duration-base` (280ms) — 페이지 전환 duration
- `--motion-ease-emphasized` (`cubic-bezier(0.16,1,0.3,1)`) — 전환 easing

> `--motion-duration-intro` (900ms) 는 **미사용** — 일회성 인트로 오버레이 전용으로 보존.

---

## Tests

```bash
# Section component existence + DEC-5 assertions (no install needed)
node --test tests/sections.test.mjs

# Token build (requires npm install)
node --test tests/tokens.test.mjs

# Wire codegen + DEC-5 schema (requires npm install)
node --test tests/wire.test.mjs

# L3 build smoke — runs full astro build, checks dist/ (requires npm install + Python)
node --test tests/smoke.test.mjs
```

---

## G-8 (ASCII slug)

All files in this adapter use ASCII slug names. `scripts/diagnose.py G-8` passes.

## G-1 (contract single source)

- `src/lib/contract.gen.ts` is generated by `scripts/codegen.mjs` from `middle/contract/wire-v1.yaml`
- No component hardcodes endpoint paths or entity_type values
- Contact form derives POST URL from `ENDPOINT_MAP["entity_create"]` template
