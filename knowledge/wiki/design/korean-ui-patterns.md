---
slug: korean-ui-patterns
type: SYNTHESIZED
updated: 2026-06-12
sources: deep-research (B2B SaaS/공공 SI + 대기업 디자인 시스템), KRDS GitHub 직접 분석
related: design/templates/, profiles/_README.md (stack.ui_theme), token_css_generator.py
---

# 한국 업무용 UI 패턴 — 리서치 & 구현 현황

> Growth-40 deep-research + Growth-42 KRDS 클론 분석. 구현 산출물: `design/templates/`.

---

## 1. KRDS — 공공 고객 핵심 자원

- **정체**: 행정안전부 공식 디지털 정부 서비스 디자인 시스템 (2025년 공공기관 의무화)
- **GitHub**: `KRDS-uiux/krds-uiux` v1.1.0
- **74개 컴포넌트** — table, tab, side_navigation, accordion, pagination, modal, form 요소 등 전부 포함
- **CDN (빌드 없음)**:
  ```html
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/krds-uiux@1.1.0/resources/cdn/krds.min.css">
  <script src="https://cdn.jsdelivr.net/npm/krds-uiux@1.1.0/resources/cdn/krds.min.js" defer></script>
  ```
  크기: `krds.min.css` 579KB / `krds.min.js` 183KB
- **영업 포인트**: 공공 SI 고객에게 "정부 표준 준수" — 재량이 아닌 의무
- **주의**: KRDS `table.html` = semantic 기본 테이블 (Fixed Header/Column 없음) → Dense Fixed 패턴은 `design/templates/dense-table.html` 별도 사용

### KRDS 핵심 마크업 패턴

| 컴포넌트 | 클래스 | JS 필요 |
|---|---|---|
| Table | `krds-table-wrap` + `tbl col data` | ✗ |
| Tab | `krds-tab-area layer` → `tab line full` → `tablist` | ✓ (자동) |
| Side Nav | `krds-side-navigation` → `lnb-list` → `lnb-toggle` | ✓ (자동) |
| Accordion | `krds-accordion` | ✓ (자동) |

---

## 2. 한국 공공/기업 SI UI 3대 패턴

| 패턴 | 규격 | 구현 현황 |
|---|---|---|
| **Dense Table** | Fixed Header(세로) + Fixed Column(가로) + Hover Action | `design/templates/dense-table.html` ✅ |
| **좌측 트리메뉴** | 아코디언 접기/펼치기 + localStorage 상태 유지 | Growth-39 사이드바 ✅ / `design/templates/krds-side-nav.html` ✅ |
| **탭 기반 화면** | 업무 화면 기본 구조 (eGovFrame 표준) | `design/templates/tab-form.html` ✅ / `design/templates/krds-tab.html` ✅ |

- **Hover Action 패턴**: 마우스오버 시 행 액션 노출 (opacity 0→1). 트레이드오프: 혼란 감소 vs 신규 사용자 발견성 저하
- **eGovFrame**: jQuery Ajax 기반, 공공 SI 레거시 지배적

---

## 3. 대기업 디자인 시스템 공통 패턴

| 시스템 | 특징 |
|---|---|
| **삼성 One UI** | Focus Block 3유형, 아이콘 색상 앱 내부 연속, Nav 3분리 |
| **네이버파이낸셜 deFign** (2023) | Figma API → 토큰 자동 추출 전 서비스 적용 |
| **카카오스타일 ZDS** (2024) | Vanilla Extract `createGlobalThemeContract` 토큰 계약 |

**공통**: semantic 색상 토큰 계약(textPrimary/background 등) + variant 체계 + 라이트/다크 이분법

---

## 4. 라이브러리 적합성 (vanilla-htmx 기준)

| 라이브러리 | 적합 | 이유 |
|---|---|---|
| **KRDS HTML Kit** | ✅ | 빌드 없음, CDN, 공식 한국 표준 |
| Channel.io Bezier | ❌ | React AppProvider 필수 |
| shadcn/ui | ❌ | 빌드 필요 + KWCAG 추가 작업 |
| Shoelace | ❌ | 2025년 7월 개발 중단 → Web Awesome 전환 |
| Ant Design | △ | CDN 가능하나 번들 무거움, React 최적화 |

---

## 5. 구현 현황 — harness 통합

`stack.ui_theme` 키로 분기 (Growth-41~44 완성):

```
stack.ui_theme: public-sector  →  KRDS CDN + Pico 스킵
stack.ui_theme: saas (기본)    →  Pico CSS + tokens.css (Hostinger 스타일)
```

**전 구간**: profile → preview_package.py → compose `UI_THEME` build arg → Dockerfile `ENV` → server.py context → base.html Jinja2 `{% if ui_theme == 'public-sector' %}` 분기

### 생성된 정적 스니펫 (`design/templates/`)

| 파일 | 목적 | 테마 |
|---|---|---|
| `dense-table.html` | Fixed Header+Column, Hover Action | saas (커스텀) |
| `tab-form.html` | 탭 기반 폼, 2열 grid | saas (커스텀) |
| `krds-tab.html` | KRDS 공식 탭, ARIA 완전 | public-sector |
| `krds-table.html` | KRDS semantic 테이블 | public-sector |
| `krds-side-nav.html` | KRDS LNB 4-depth | public-sector |

---

## 6. 미답 질문 (다음 리서치)

- Web Awesome(Shoelace 후계) vanilla-htmx Shadow DOM 직렬화 해결 여부
- KRDS v2.x 로드맵 — 2025년 이후 업데이트 주기
- Figma Community 한국어 UI 키트 품질
