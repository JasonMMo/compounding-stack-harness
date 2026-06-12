---
slug: kwcag
type: SYNTHESIZED
updated: 2026-06-13
sources: KWCAG 2.2 공식 문서 (과학기술정보통신부), 장애인차별금지법
related: design/korean-ui-patterns.md, design/templates/
---

# KWCAG 2.2 — 한국형 웹 콘텐츠 접근성 지침

> 공공기관·업무용 UI 구현 시 체크리스트. 법적 의무 + 영업 포인트.

---

## 1. 법적 근거 & 의무 적용

| 구분 | 내용 |
|---|---|
| 법률 | 장애인차별금지 및 권리구제 등에 관한 법률 (장차법) 제21조 |
| 고시 | 과학기술정보통신부 고시 (KWCAG 2.2, 2022년 개정) |
| 의무 대상 | 공공기관 웹사이트 (2008~), 민간 사업자 50인 이상 (2015~), 전체 민간 (2022~) |
| 미준수 시 | 과태료 부과 + 시정명령 + 법원 손해배상 청구 가능 |

**harness 영업 포인트**: 공공 SI 고객에게 `stack.ui_theme: public-sector` + KRDS 사용 = KWCAG 기반 준수 자동화.

---

## 2. 4원칙 & 핵심 기준

### 인식 가능성 (Perceivable)

| 기준 | 요구사항 | 구현 |
|---|---|---|
| 대체 텍스트 | 모든 비텍스트 콘텐츠에 `alt` 속성 | `<img alt="설명">`, 장식 이미지는 `alt=""` |
| 명도 대비 | 일반 텍스트 **4.5:1** 이상, 확대 텍스트(18pt+) **3:1** 이상 | Pico CSS 기본 통과, 커스텀 색상은 직접 검증 |
| 텍스트 크기 조정 | 200% 확대 시 콘텐츠·기능 손실 없음 | `font-size` em/rem 사용, px 고정 금지 |
| 명확한 지시 | 색상만으로 정보 전달 금지 (모양·텍스트 병행) | 오류 표시: 빨간색 + 아이콘 + 텍스트 |

> **가장 자주 위반**: 명도 대비. 회색 플레이스홀더, 비활성 버튼, 보조 텍스트가 4.5:1 미만인 경우 다수.

### 운용 가능성 (Operable)

| 기준 | 요구사항 | 구현 |
|---|---|---|
| 키보드 접근성 | 모든 기능 키보드로 조작 가능 | `tabindex`, 커스텀 컴포넌트에 `keydown` 핸들러 |
| 포커스 표시 | 키보드 포커스 시각적 표시 | `outline: 2px solid var(--brand)` — `outline: none` 금지 |
| 건너뛰기 링크 | 반복 내비게이션 건너뛰기 | `<a href="#main" class="skip-link">본문 바로가기</a>` |
| 깜빡임 제한 | 초당 3회 이하, 또는 아예 없음 | 애니메이션 `.flash` 사용 시 주의 |
| 충분한 시간 | 시간 제한 조정 또는 연장 가능 | 세션 만료 전 연장 UI 제공 |

### 이해 가능성 (Understandable)

| 기준 | 요구사항 | 구현 |
|---|---|---|
| 언어 명시 | `<html lang="ko">` | base.html에 반드시 포함 |
| 레이블 제공 | 모든 입력 필드에 `<label>` 연결 | `for` 속성 or `aria-label` |
| 오류 식별 | 오류 위치·원인·정정 방법 제시 | 인라인 오류 메시지 (입력 필드 바로 아래) |
| 일관성 | 동일 기능은 동일 레이블 | "저장" → "저장", "Submit"→"저장" 혼용 금지 |

### 견고성 (Robust)

| 기준 | 요구사항 | 구현 |
|---|---|---|
| 문법 준수 | 표준 HTML 마크업, 유효한 시작/종료 태그 | W3C validator 통과 권고 |
| WAI-ARIA | 커스텀 위젯에 role/aria-* 속성 | `role="dialog"`, `aria-expanded`, `aria-label` |
| 보조기술 호환 | 스크린리더 NVDA/센스리더 테스트 | 공공 SI는 센스리더 필수 확인 |

---

## 3. 명도 대비 실무 기준

```
일반 텍스트 (18px 미만 normal, 14px 미만 bold):  4.5:1 이상
확대 텍스트 (18px 이상 normal, 14px 이상 bold): 3.0:1 이상
비텍스트 (아이콘, UI 컴포넌트 경계선):           3.0:1 이상
```

**검증 도구**: Colour Contrast Analyser (Windows 앱), browser devtools Accessibility 탭.

**harness 토큰에서 주의할 색상**:
- `--color-text-muted` (회색 보조 텍스트) — 4.5:1 확인 필수
- placeholder 색상 — 흔히 너무 연함
- disabled 상태 버튼 — 의도적 저대비 허용 (비활성 상태임을 알 수 있을 때)

---

## 4. 빠른 구현 체크리스트 (HTML)

```html
<!-- 1. lang 속성 -->
<html lang="ko">

<!-- 2. 건너뛰기 링크 -->
<a href="#main-content" class="skip-link">본문 바로가기</a>
<style>.skip-link { position:absolute; left:-9999px; } .skip-link:focus { left:0; }</style>

<!-- 3. 이미지 alt -->
<img src="logo.png" alt="회사명 로고">   <!-- 의미 있는 이미지 -->
<img src="deco.png" alt="">             <!-- 장식용 -->

<!-- 4. 레이블 연결 -->
<label for="name">이름 <span aria-hidden="true">*</span><span class="sr-only">(필수)</span></label>
<input id="name" type="text" aria-required="true">

<!-- 5. 오류 메시지 -->
<input aria-describedby="name-error" aria-invalid="true">
<p id="name-error" role="alert">이름을 입력해 주세요.</p>

<!-- 6. 커스텀 모달 -->
<div role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <h2 id="modal-title">확인</h2>
  ...
</div>

<!-- 7. 포커스 표시 — CSS에서 절대 제거 금지 -->
/* :focus-visible { outline: 2px solid #0057B7; outline-offset: 2px; } */
```

---

## 5. KWCAG 2.2 vs WCAG 2.1/2.2 차이점

| 항목 | KWCAG 2.2 | WCAG 2.1 |
|---|---|---|
| 대비 기준 | 동일 (4.5:1 / 3:1) | 동일 |
| 포인터 접근성 | WCAG 2.1 AA 포함 | WCAG 2.1부터 추가 |
| 깜빡임 | 초당 3회 (WCAG와 동일) | 동일 |
| 언어 | 한국어 공식 문서 존재 | 영어 원문 |
| 법적 효력 | 한국 법령 기반 (장차법) | 자발적 표준 (EU는 법령화) |
| 추가 기준 | 자막 제공, 화면 낭독 프로그램 호환 강조 | 비슷하나 표현 다름 |

> 실무 결론: WCAG 2.1 AA 수준 = KWCAG 2.2 대부분 충족. KRDS 사용 시 접근성 기본기 내장.

---

## 6. 미답 (추가 조사 시)

- 센스리더 최신 버전 테스트 환경 구성
- KWCAG 2.2 검사도구 자동화 (axe-core, Pa11y 한국어 지원 수준)
- KRDS v1.1.0 ARIA 구현 완성도 실측
