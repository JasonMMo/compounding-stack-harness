---
title: "Motion Tokens — 디자인 모션 토큰 시스템"
type: concept
created: 2026-06-28
updated: 2026-06-28
sources:
  - design/tokens/semantic.json
  - frontend/adapters/vanilla-htmx/token_css_generator.py (lines 418-428)
  - frontend/adapters/vanilla-htmx/static/css/tokens.css
  - frontend/adapters/react/src/tokens/tokens.gen.css
  - frontend/adapters/landing-astro/src/styles/tokens.gen.css
  - docs/architecture/motion-system.md
  - learn-log.md §Growth-87, §Growth-88, §Growth-130g
---

# Motion Tokens

3-어댑터(vanilla-htmx / react / landing-astro) 공통 모션 언어. 단일 진실은 `design/tokens/semantic.json → token_css_generator.py → tokens.css` 파이프라인이다.

관련: [[kwcag]] (reduced-motion a11y 근거), [[korean-ui-patterns]] (인터랙션 컨텍스트)

---

## 1. 3 토큰 패밀리

### Duration `[EXTRACTED]`

| 토큰 (CSS var) | 값 | 용도 |
|---|---|---|
| `--motion-duration-fast` | `150ms` | hover, focus, 즉각 피드백 |
| `--motion-duration-base` | `280ms` | 일반 전환, swap-in |
| `--motion-duration-slow` | `480ms` | 패널 슬라이드, 사이드바 |
| `--motion-duration-xslow` | `640ms` | 페이지 레벨 전환 |
| `--motion-duration-intro` | `900ms` | 최초 1회 스플래시 오버레이 |

### Easing `[EXTRACTED]`

| 토큰 | 값 | 특성 |
|---|---|---|
| `--motion-ease-standard` | `cubic-bezier(0.4,0,0.2,1)` | Material Design 표준, 기본 |
| `--motion-ease-emphasized` | `cubic-bezier(0.16,1,0.3,1)` | 빠른 가속·긴 감속, 드라마틱 진입 |
| `--motion-ease-exit` | `cubic-bezier(0.7,0,0.84,0)` | 빠른 이탈 |
| `--motion-ease-spring` | `cubic-bezier(0.34,1.56,0.64,1)` | 오버슈트, 스프링 감 |

### Stagger `[EXTRACTED]`

| 토큰 | 값 | 용도 |
|---|---|---|
| `--motion-stagger-tight` | `40ms` | 밀집 리스트 아이템 순차 등장 |
| `--motion-stagger-base` | `80ms` | 카드 그리드 순차 등장 |
| `--motion-stagger-loose` | `140ms` | 섹션 단위 순차 등장 |

---

## 2. 생성 파이프라인

```
design/tokens/semantic.json          ← 단일 진실 (motion 섹션)
        ↓
token_css_generator.py               ← raw layer + semantic layer 이중 출력
        ↓
tokens.css / tokens.gen.css          ← 3 어댑터 각각 소비
```

`semantic.json` 의 `motion.*` 키는 `{motion.duration.*}`, `{motion.easing.*}`, `{motion.stagger.*}` 참조 문법으로 raw.json 값을 간접 참조한다. `[EXTRACTED]`

raw layer CSS 변수명 패턴: `--raw-motion-duration-fast` (raw), `--motion-duration-fast` (semantic). 컴포넌트는 **semantic 변수만** 소비한다. `[EXTRACTED]`

---

## 3. Reduced-Motion 접근성 Override

`token_css_generator.py` 는 tokens.css 말미에 자동으로 아래 블록을 생성한다. `[EXTRACTED]`

```css
/* a11y: prefers-reduced-motion override (WCAG 2.3.3 / KWCAG) */
@media (prefers-reduced-motion: reduce) {
  :root {
    --motion-duration-base:  0.01ms;
    --motion-duration-fast:  0.01ms;
    --motion-duration-intro: 0.01ms;
    --motion-duration-slow:  0.01ms;
    --motion-duration-xslow: 0.01ms;
  }
}
```

모든 duration(`fast`·`base`·`slow`·`xslow`·`intro` 전 5종)을 `0.01ms` 로 붕괴시켜 사실상 즉시 전환. `[EXTRACTED]` override 목록은 `sem_pairs`(semantic 토큰셋)에서 `--motion-duration-*` 접두를 파생해 생성하므로, **신규 duration 토큰은 자동 커버**된다 — 하드코딩 드리프트 불가(Growth-131b). 과거 `xslow` 누락은 하드코딩 4종 시절의 a11y 갭이었고 해소됨. `[EXTRACTED]`

---

## 4. 3-어댑터 확산 현황

| 어댑터 | 토큰 파일 | 소비 현황 | Growth |
|---|---|---|---|
| vanilla-htmx | `static/css/tokens.css` | `--pico-transition` override + swap-transitions.css 연결 | 130g |
| react | `src/tokens/tokens.gen.css` | `app.css` button/input transition 2건 | 130g |
| landing-astro | `src/styles/tokens.gen.css` | 모션 토큰 포함, framer-motion 병행 | 88 |

`--motion-distance` 토큰은 vanilla-htmx 에 없다. `swap-transitions.css` 는 자체 변수 `--swap-distance: 8px` 를 사용하며, 추후 motion 팔레트로 승격 예정이다. `[EXTRACTED]`

---

## 5. G-69 No-JS-Visible 불변 규칙

모션 토큰을 소비하는 reveal 애니메이션은 반드시 **CSS default state = fully visible (opacity:1)** 에서 출발한다. `[EXTRACTED]` JS 가 `.in-view` 클래스를 추가할 때만 애니메이션이 작동하며, JS 없는 환경에서는 콘텐츠가 100% 노출된 상태로 정지한다. (AOS 식 `opacity:0` 기본값 패턴은 G-69 위반이다.)

관련 파일: `docs/architecture/motion-system.md §2 Hard invariants`
