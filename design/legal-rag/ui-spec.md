# UI 스펙 — 법무법인 self-host RAG 검색도구

> 버전: 0.1.0 (MVP / M3 첫 버티컬)
> 담당: CDO (design-agent)
> 대상 구현자: engineer-agent (HTML/Jinja 템플릿 + CSS 적용)
> 최종 변경: 2026-06-19

---

## 0. 제품 성격 원칙 (번역 금지 — engineer 가 UI 문구 판단 시 기준)

이 도구는 **검색 + 인용 도구**다. LLM 이 답을 생성하지 않는다.
화면 어디에도 "AI 가 답변합니다", "AI 추천", "답변 생성 중" 같은 메타포를 쓰지 않는다.
모든 결과 카드는 출처(판례 번호 또는 문서 제목)를 반드시 표시한다.
**생성형 답변 영역은 존재하지 않는다.**

시각 언어 키워드: 정돈 · 권위 · 신뢰 · 기밀 · 가독성. 화려함은 반한다.

---

## 1. 디자인 토큰 — legal-rag override

기반: `design/tokens/raw.json` + `design/tokens/semantic.json`
법무 버티컬 전용 override (CSS 변수로 실체화 → `tokens.css`):

### 1-1. 팔레트 override

법무 컨텍스트는 일반 accent(파란색)보다 **네이비** 계열이 권위 표현에 적합.
accent ramp 를 네이비로 override 한다 (raw.json 브랜드 색 미정 상태를 버티컬 레벨에서 독립 결정).

| 토큰 이름 (CSS 변수)         | 값 (hex)   | 용도                              |
|------------------------------|-----------|-----------------------------------|
| `--lr-navy-900`              | `#0F1729` | 로그인 헤더 배경, 최심 강조       |
| `--lr-navy-800`              | `#1A2744` | 주 네이비 (primary action)        |
| `--lr-navy-700`              | `#243659` | hover                             |
| `--lr-navy-600`              | `#2E4470` | active / pressed                  |
| `--lr-navy-100`              | `#E8EDF5` | primary-subtle 배경               |
| `--lr-navy-050`              | `#F2F5FA` | surface-subtle                    |
| `--lr-gold-500`              | `#B8960C` | 판례 뱃지 강조 (권위 상징, 절제) |
| `--lr-gold-100`              | `#FDF8E7` | 판례 뱃지 배경                    |

gray scale, red, green, yellow 는 semantic.json 값 그대로 상속.

### 1-2. 시맨틱 토큰 매핑 (이 CSS 변수가 컴포넌트에서 쓰인다)

| 시맨틱 변수                  | 매핑 값                   | 비고                              |
|------------------------------|--------------------------|-----------------------------------|
| `--color-primary`            | `var(--lr-navy-800)`     | 버튼, 링크, 포커스 링              |
| `--color-primary-hover`      | `var(--lr-navy-700)`     |                                   |
| `--color-primary-subtle`     | `var(--lr-navy-100)`     | 뱃지 배경 등                      |
| `--color-surface-1`          | `#FFFFFF`                | 카드, 모달 내부                   |
| `--color-surface-2`          | `#F7F8FA`                | 페이지 배경                       |
| `--color-surface-3`          | `#EEF1F6`                | 사이드바, 분리선 배경             |
| `--color-border`             | `#D4D9E3`                | 카드·입력 테두리                  |
| `--color-border-focus`       | `var(--lr-navy-800)`     | 포커스 링 색                      |
| `--color-text-1`             | `#111827`                | 본문 주 텍스트                    |
| `--color-text-2`             | `#374151`                | 부제목, 메타                      |
| `--color-text-3`             | `#6B7280`                | 캡션, 플레이스홀더                |
| `--color-danger`             | `#DC2626`                | 에러, 실패 상태                   |
| `--color-success`            | `#16A34A`                | 색인 완료 상태                    |
| `--color-warning`            | `#B45309`                | 대기/진행 상태                    |
| `--color-badge-precedent-bg` | `var(--lr-gold-100)`     | 판례 뱃지 배경                    |
| `--color-badge-precedent-fg` | `var(--lr-gold-500)`     | 판례 뱃지 텍스트                  |
| `--color-badge-document-bg`  | `var(--lr-navy-100)`     | 사건문서 뱃지 배경                |
| `--color-badge-document-fg`  | `var(--lr-navy-800)`     | 사건문서 뱃지 텍스트              |

### 1-3. 타이포그래피

폰트 스택 (외부 CDN 없음 — 시스템/웹세이프 한글):

```
-apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo',
'Malgun Gothic', '맑은 고딕', 'Noto Sans KR', 'Nanum Gothic', sans-serif
```

Pretendard 는 self-host 설치 전까지 사용 보류. 설치 시 stack 앞에 삽입.

| 역할 변수              | 크기 / 행높이 / 굵기           | 용도                  |
|------------------------|--------------------------------|-----------------------|
| `--text-heading-page`  | 20px / 28px / 600              | 페이지 제목           |
| `--text-heading-card`  | 15px / 22px / 600              | 카드 제목 (판시요지)  |
| `--text-body`          | 14px / 22px / 400              | 본문 발췌, 일반 텍스트|
| `--text-meta`          | 12px / 18px / 400              | 메타 정보 (날짜, 번호)|
| `--text-label`         | 12px / 18px / 500              | 뱃지, 상태 레이블     |
| `--text-caption`       | 11px / 16px / 400              | 부연 캡션             |
| `--text-input`         | 15px / 24px / 400              | 검색 입력창           |

### 1-4. 간격

| 변수               | 값     | 용도                              |
|--------------------|--------|-----------------------------------|
| `--space-page-h`   | 24px   | 페이지 좌우 여백                  |
| `--space-page-v`   | 20px   | 페이지 상하 여백                  |
| `--space-card-pad` | 16px   | 카드 내부 패딩                    |
| `--space-card-gap` | 12px   | 카드 간 세로 간격                 |
| `--space-meta-gap` | 8px    | 메타 항목 간 가로 간격            |
| `--space-section`  | 24px   | 섹션 간 여백                      |

### 1-5. 반경 / 그림자

| 변수                 | 값                                                        |
|----------------------|-----------------------------------------------------------|
| `--radius-card`      | 6px                                                       |
| `--radius-badge`     | 4px                                                       |
| `--radius-btn`       | 4px                                                       |
| `--radius-input`     | 4px                                                       |
| `--shadow-card`      | `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)`|
| `--shadow-input-focus` | `0 0 0 3px rgba(26,39,68,0.20)`                         |

---

## 2. 화면 1 — 로그인

### 2-1. 레이아웃 ASCII

```
┌──────────────────────────────────────────────────────────────┐
│          [페이지 배경: --color-surface-2, 전체 뷰포트]        │
│                                                              │
│         ┌────────────────────────────────────┐              │
│         │  [로그인 카드: w=360px, 중앙 정렬]  │              │
│         │  ┌──────────────────────────────┐  │              │
│         │  │  [헤더 배경: --lr-navy-900]   │  │              │
│         │  │  [로고/워드마크 자리]          │  │              │
│         │  │  법률 문서 검색 시스템         │  │              │
│         │  └──────────────────────────────┘  │              │
│         │                                    │              │
│         │  이메일                             │              │
│         │  [______________________________]  │              │
│         │                                    │              │
│         │  비밀번호                           │              │
│         │  [______________________________]  │              │
│         │                                    │              │
│         │  [      로그인      ]               │              │
│         │  (btn-primary, 전폭)                │              │
│         │                                    │              │
│         │  [오류 메시지 영역 — 조건부]         │              │
│         │                                    │              │
│         │  ─────────────────────────────     │              │
│         │  사내 서버에서 동작합니다.           │              │
│         │  외부 네트워크로 데이터가 전송되지   │              │
│         │  않습니다.                          │              │
│         └────────────────────────────────────┘              │
│                                                             │
└──────────────────────────────────────────────────────────────┘
```

### 2-2. 컴포넌트 anatomy

- `.login-wrapper` — `display:flex; align-items:center; justify-content:center; min-height:100vh; background: var(--color-surface-2)`
- `.login-card` — `width:360px; background:#fff; border-radius:8px; box-shadow: var(--shadow-card); overflow:hidden`
- `.login-card__header` — `background: var(--lr-navy-900); padding:28px 24px 24px; text-align:center`
  - `.login-card__wordmark` — `color:#fff; font-size:18px; font-weight:600; letter-spacing:0.02em`
  - `.login-card__subtitle` — `color: rgba(255,255,255,0.65); font-size:12px; margin-top:4px`
- `.login-card__body` — `padding:24px`
  - `.form-field` → `label.form-label` + `input.form-input`
  - `.btn.btn--primary.btn--full` — 전폭 로그인 버튼
  - `.login-card__alert` — 에러 시 표시 (`role="alert"`)
- `.login-card__footer` — `border-top:1px solid var(--color-border); padding:12px 16px; font-size:11px; color: var(--color-text-3); line-height:1.6`
  - 문구: "사내 서버에서 동작합니다. 외부 네트워크로 데이터가 전송되지 않습니다."

### 2-3. 상태

| 상태           | 처리                                                         |
|----------------|--------------------------------------------------------------|
| 로딩 중        | 버튼 `disabled` + 텍스트 "로그인 중..." + `aria-busy="true"` |
| 인증 실패      | `.login-card__alert` 표시, "이메일 또는 비밀번호가 올바르지 않습니다." |
| 서버 오류      | "서버에 연결할 수 없습니다. IT 담당자에게 문의하세요."        |

---

## 3. 화면 2 — 검색 + 인용 결과

### 3-1. 레이아웃 ASCII

```
┌──────────────────────────────────────────────────────────────────────┐
│ .app-header [--lr-navy-900, h=52px, sticky top=0]                    │
│  [워드마크]              [사건 선택 드롭다운] [사용자 이름] [로그아웃] │
├──────────────────────────────────────────────────────────────────────┤
│ .search-bar-section [surface-1, border-bottom]                       │
│  ┌────────────────────────────────────────────────────── [검색] ─┐  │
│  │ 판례나 사건 관련 내용을 한국어로 입력하세요...                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  [검색 파라미터: 결과 수 선택 ▾]  [현재 사건: 2024가합12345 ▾]       │
├──────────────────────────────────────────────────────────────────────┤
│ .results-section [surface-2, flex:1, overflow-y:auto]                │
│                                                                      │
│  검색 결과 23건 · "손해배상 과실상계"                                 │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ [뱃지: 판례]  대법원 · 2023다56789 · 2023.11.15.               │ │
│  │                                                                 │ │
│  │ 판시요지: 과실상계 비율 결정에 있어 피해자의 과실이 전체의       │ │
│  │ 40%를 초과하는 경우 법원은 이를 별도로...                        │ │
│  │                                                                 │ │
│  │ [본문 발췌]                                                     │ │
│  │ "...원고의 과실 비율을 40%로 보아 손해액에서 공제한 원심의 판단  │ │
│  │ 은 정당하고..."                                                  │ │
│  │                                                                 │ │
│  │  관련도 0.87  청크 #42  [원문 보기 →]                           │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ [뱃지: 사건문서]  준비서면 · 2024-06-01                         │ │
│  │                                                                 │ │
│  │ 원고 측 손해배상 주장 근거 — 제3항                              │ │
│  │                                                                 │ │
│  │ "...피고의 과실이 70% 이상임을 입증하는 다음의 증거를 제출하며..." │ │
│  │                                                                 │ │
│  │  관련도 0.81  청크 #8  [원문 보기 →]                            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  [빈 결과 / 로딩 / 에러 상태 — §3-4 참조]                            │
└──────────────────────────────────────────────────────────────────────┘
```

### 3-2. 컴포넌트 anatomy — 인용 카드 (.citation-card)

```
.citation-card
  ├── .citation-card__header
  │     ├── .citation-badge  (source_type에 따라 .citation-badge--precedent / --document)
  │     └── .citation-card__meta
  │           ├── .meta-item  (판례: 법원 이름)
  │           ├── .meta-sep  (·)
  │           ├── .meta-item  (사건번호)
  │           └── .meta-item  (선고일 또는 문서 날짜)
  ├── .citation-card__holding  (판례 판시요지, source_type=precedent 시만 표시)
  ├── .citation-card__excerpt
  │     └── 본문 발췌 텍스트 (검색어 강조: <mark class="search-highlight">)
  └── .citation-card__footer
        ├── .relevance-score  "관련도 0.87"
        ├── .chunk-ref        "청크 #42"
        └── .citation-card__link  "원문 보기 →"  (href 또는 disabled 상태)
```

**source_type 분기 렌더링:**

| 필드              | precedent (판례)                 | case_document (사건문서)          |
|-------------------|----------------------------------|-----------------------------------|
| 뱃지 클래스        | `.citation-badge--precedent`     | `.citation-badge--document`       |
| 뱃지 텍스트        | "판례"                           | "사건문서"                        |
| 헤더 메타 1        | `court` (법원명)                 | `document_type` (준비서면 등)     |
| 헤더 메타 2        | `case_number` (사건번호)         | `document_title` (문서 제목)      |
| 헤더 메타 3        | `decision_date` (선고일)         | 없음 또는 ingest 날짜             |
| 판시요지 영역      | `holding_summary` (있을 때만)    | 표시 안 함                        |

null 필드는 해당 `.meta-item` 을 아예 렌더링하지 않는다 (빈 문자열 표시 금지).

### 3-3. 검색창 컴포넌트 (.search-bar)

```
.search-bar
  ├── .search-bar__input  (textarea 또는 input, 자연어 한국어)
  └── .search-bar__btn    (btn.btn--primary "검색")
.search-bar-controls (검색창 하단 1줄)
  ├── .search-param-select  (결과 수: 5 / 10 / 20)
  └── .case-filter-select   (사건 필터 드롭다운)
```

입력창 placeholder: "판례나 사건 관련 내용을 한국어로 입력하세요"
버튼 텍스트: "검색"
주의: "AI 검색", "스마트 검색" 같은 문구 금지.

### 3-4. 상태별 렌더링

| 상태                  | 클래스                | 메시지 / 표현                                                              |
|-----------------------|-----------------------|----------------------------------------------------------------------------|
| 초기 (미검색)         | `.results--empty-initial` | "검색어를 입력하면 관련 문서를 출처와 함께 보여줍니다."             |
| 로딩 중               | `.results--loading`   | `.skeleton-card` x 3 (높이 고정 회색 블록) + `aria-busy="true"`           |
| 결과 있음             | `.results--has-results` | 결과 수 헤더 + `.citation-card` 목록                                    |
| 결과 없음             | `.results--empty`     | "입력하신 내용과 일치하는 문서가 없습니다. 다른 표현으로 다시 검색해 보세요." |
| 검색 오류             | `.results--error`     | "검색 중 오류가 발생했습니다. 잠시 후 다시 시도하세요."                   |
| 사이드카 다운         | `.results--sidecar-down` | "검색 서비스가 일시적으로 이용 불가합니다. IT 담당자에게 문의하세요." (health 체크 기반) |

---

## 4. 화면 3 — 사건현황

### 4-1. 레이아웃 ASCII

```
┌──────────────────────────────────────────────────────────────────────┐
│ .app-header [동일 헤더]                                               │
├──────────────────────────────────────────────────────────────────────┤
│ .page-title-bar                                                      │
│  담당 사건 현황                                                       │
├──────────────────────────────────────────────────────────────────────┤
│ .case-table-section                                                  │
│                                                                      │
│  ┌──────────────┬─────────────┬───────────────┬────────────┬───────┐ │
│  │ 사건번호      │ 사건명      │ 색인 상태      │ 문서 수    │ 검색  │ │
│  ├──────────────┼─────────────┼───────────────┼────────────┼───────┤ │
│  │ 2024가합12345│ 손해배상    │ ● 색인 완료    │ 34건       │ [검색]│ │
│  │ 2024나56789  │ 계약 위반   │ ○ 대기 중      │ 12건       │ [검색]│ │
│  │ 2024다11111  │ 부동산      │ ✕ 색인 실패    │ 8건        │ [검색]│ │
│  └──────────────┴─────────────┴───────────────┴────────────┴───────┘ │
│                                                                      │
│  [색인 실패 행 — .case-row--error: 배경 --color-danger 5% tint]      │
└──────────────────────────────────────────────────────────────────────┘
```

### 4-2. 컴포넌트 anatomy

```
.case-table  (table 요소)
  ├── thead > tr > th.case-th  (5열)
  └── tbody
        └── tr.case-row  (ingest_status별 modifier)
              ├── .case-row--indexed   (색인 완료)
              ├── .case-row--pending   (대기 중)
              └── .case-row--error     (실패, 배경 tint)
              └── td 내:
                    .case-number       (사건번호)
                    .case-title        (사건명)
                    .ingest-status-badge (상태 뱃지)
                    .doc-count         (문서 수)
                    .btn.btn--sm.btn--outline (검색 버튼)
```

### 4-3. ingest_status 뱃지 매핑

| ingest_status 값 | 클래스                       | 텍스트       | 색            |
|-----------------|------------------------------|-------------|---------------|
| `indexed`       | `.ingest-badge--indexed`     | 색인 완료    | success green |
| `pending`       | `.ingest-badge--pending`     | 대기 중      | warning amber |
| `failed`        | `.ingest-badge--failed`      | 색인 실패    | danger red    |
| 기타/unknown    | `.ingest-badge--unknown`     | 상태 불명    | gray          |

---

## 5. 공통 컴포넌트 스펙

### 5-1. 버튼 (.btn)

```
.btn                  — 기본 (공통 패딩, 폰트, 반경, 트랜지션)
  .btn--primary       — 네이비 채움 배경
  .btn--outline       — 테두리만, 배경 투명
  .btn--ghost         — 배경/테두리 없음, 텍스트만
  .btn--danger        — 적색 채움
  .btn--sm            — 소형 (패딩 축소)
  .btn--full          — width:100%
```

규칙:
- 모든 `.btn` 에 `cursor:pointer; user-select:none`
- `:disabled` 상태: `opacity:0.5; cursor:not-allowed; pointer-events:none`
- `:focus-visible` 상태: `outline: 3px solid var(--color-border-focus); outline-offset:2px`

### 5-2. 폼 요소

```
.form-field           — 필드 래퍼 (margin-bottom)
  label.form-label    — 레이블 (font-weight:500, display:block, margin-bottom:4px)
  input.form-input    — 입력 필드
  .form-error         — 인라인 에러 메시지 (role="alert", color:danger)
```

`.form-input` 규칙:
- `border: 1px solid var(--color-border); border-radius: var(--radius-input)`
- `:focus` → `border-color: var(--color-border-focus); box-shadow: var(--shadow-input-focus); outline:none`
- `::placeholder` → `color: var(--color-text-3)`

### 5-3. 뱃지 (.citation-badge)

```
.citation-badge                        — 공통 (인라인 블록, 패딩, 폰트 12px 500, 반경 4px)
  .citation-badge--precedent           — gold 팔레트
  .citation-badge--document            — navy 팔레트
```

### 5-4. 앱 헤더 (.app-header)

- `background: var(--lr-navy-900); color:#fff; height:52px; position:sticky; top:0; z-index:200`
- 내부 flex: 워드마크 좌, 컨트롤 우
- `.header-wordmark`: 흰색 텍스트, 15px / 600
- `.header-user`: 사용자 이름 표시, 12px
- `.btn.btn--ghost` (로그아웃): 흰색 텍스트/테두리, 소형

### 5-5. 스켈레톤 로딩 (.skeleton-card)

- 실제 `.citation-card` 와 동일한 높이/반경의 회색 블록
- 배경: `linear-gradient(90deg, #e5e7eb 25%, #f3f4f6 50%, #e5e7eb 75%)` — 좌우 shimmer 애니메이션
- 애니메이션: `@keyframes skeleton-shimmer` (2s infinite)
- 3개 노출 → 실제 결과 렌더 시 교체

---

## 6. 클래스명 규약 (engineer 준수 필수)

아래 클래스명은 `app.css` 에 정의된 이름과 1:1 대응한다.
HTML 템플릿 작성 시 이 이름을 그대로 사용한다. 임의 변형 금지.

### 6-1. 레이아웃

| 클래스                  | 설명                                    |
|-------------------------|-----------------------------------------|
| `.app-root`             | body 직하위 루트 래퍼                    |
| `.app-header`           | 상단 고정 헤더                           |
| `.header-wordmark`      | 헤더 내 서비스명                         |
| `.header-controls`      | 헤더 우측 컨트롤 영역                    |
| `.header-user`          | 헤더 사용자 이름 텍스트                  |
| `.page-main`            | 헤더 아래 스크롤 영역                    |
| `.page-title-bar`       | 페이지 제목 바 (사건현황 등)             |
| `.login-wrapper`        | 로그인 페이지 전체 래퍼                  |
| `.login-card`           | 로그인 카드                              |
| `.login-card__header`   | 로그인 카드 헤더 (네이비 배경)           |
| `.login-card__wordmark` | 카드 내 서비스명                         |
| `.login-card__subtitle` | 카드 내 부제목                           |
| `.login-card__body`     | 카드 폼 영역                             |
| `.login-card__alert`    | 로그인 에러 메시지                       |
| `.login-card__footer`   | 카드 하단 self-host 안내                 |

### 6-2. 검색

| 클래스                    | 설명                                      |
|---------------------------|-------------------------------------------|
| `.search-bar-section`     | 검색창 섹션 래퍼                           |
| `.search-bar`             | 검색창 + 버튼 flex 래퍼                    |
| `.search-bar__input`      | 검색 입력 필드                             |
| `.search-bar__btn`        | 검색 실행 버튼                             |
| `.search-bar-controls`    | 검색창 하단 파라미터 컨트롤 행             |
| `.search-param-select`    | 결과 수 선택 select                        |
| `.case-filter-select`     | 사건 필터 select                           |
| `.results-section`        | 결과 표시 영역                             |
| `.results-header`         | "검색 결과 N건 · 쿼리" 헤더               |
| `.results-list`           | 카드 목록 ul/div                           |
| `.results--loading`       | 로딩 상태 modifier                         |
| `.results--empty`         | 빈 결과 modifier                           |
| `.results--empty-initial` | 초기 미검색 modifier                       |
| `.results--error`         | 오류 상태 modifier                         |
| `.results--sidecar-down`  | 사이드카 다운 modifier                     |
| `.results-message`        | 상태 메시지 텍스트 (empty/error 등)        |

### 6-3. 인용 카드

| 클래스                      | 설명                                      |
|-----------------------------|-------------------------------------------|
| `.citation-card`            | 인용 카드 래퍼                             |
| `.citation-card__header`    | 카드 상단 (뱃지 + 메타)                   |
| `.citation-badge`           | 출처 종류 뱃지 (공통)                      |
| `.citation-badge--precedent`| 판례 뱃지                                 |
| `.citation-badge--document` | 사건문서 뱃지                              |
| `.citation-card__meta`      | 메타 정보 flex 행                          |
| `.meta-item`                | 개별 메타 항목                             |
| `.meta-sep`                 | 메타 구분자 (·)                            |
| `.citation-card__holding`   | 판시요지 (판례만)                          |
| `.citation-card__excerpt`   | 본문 발췌                                 |
| `.search-highlight`         | 검색어 강조 span (mark 요소)              |
| `.citation-card__footer`    | 카드 하단 (관련도·청크 ref·링크)          |
| `.relevance-score`          | 관련도 점수 표시                           |
| `.chunk-ref`                | 청크 번호 표시                             |
| `.citation-card__link`      | "원문 보기 →" 링크/버튼                   |
| `.skeleton-card`            | 로딩 스켈레톤 카드                         |

### 6-4. 사건현황

| 클래스                      | 설명                                      |
|-----------------------------|-------------------------------------------|
| `.case-table-section`       | 테이블 섹션 래퍼                           |
| `.case-table`               | 사건 목록 table 요소                       |
| `.case-th`                  | 테이블 헤더 th                             |
| `.case-row`                 | 사건 행 tr                                 |
| `.case-row--indexed`        | 색인 완료 행 modifier                      |
| `.case-row--pending`        | 대기 중 행 modifier                        |
| `.case-row--error`          | 색인 실패 행 modifier                      |
| `.case-number`              | 사건번호 td                                |
| `.case-title`               | 사건명 td                                  |
| `.doc-count`                | 문서 수 td                                 |
| `.ingest-status-badge`      | 색인 상태 뱃지 (공통)                      |
| `.ingest-badge--indexed`    | 색인 완료 modifier                         |
| `.ingest-badge--pending`    | 대기 중 modifier                           |
| `.ingest-badge--failed`     | 실패 modifier                              |
| `.ingest-badge--unknown`    | 불명 modifier                              |

### 6-5. 공통 폼 / 버튼

| 클래스          | 설명                              |
|-----------------|-----------------------------------|
| `.form-field`   | 폼 필드 래퍼                       |
| `.form-label`   | 레이블                             |
| `.form-input`   | 텍스트 입력 필드                   |
| `.form-select`  | 선택 필드 (select)                 |
| `.form-error`   | 인라인 에러 메시지                 |
| `.btn`          | 버튼 기본                          |
| `.btn--primary` | 주 버튼 (네이비)                   |
| `.btn--outline` | 외곽선 버튼                        |
| `.btn--ghost`   | 투명 버튼                          |
| `.btn--danger`  | 위험 버튼 (빨강)                   |
| `.btn--sm`      | 소형 버튼                          |
| `.btn--full`    | 전폭 버튼                          |

---

## 7. 페르소나별 인터랙션 규약

### 7-1. CEO (대표변호사)

- 목표: 담당 사건 전체 현황 파악, 핵심 판례 확인
- 기본 진입: **사건현황 화면**
- 인터랙션 패턴: 사건현황 → 특정 사건 [검색] 클릭 → 검색 화면(해당 사건 필터 자동 적용)
- 정보 밀도: **낮음** — 카드당 판시요지 1~2줄, 본문 발췌 최대 3줄(CSS `line-clamp:3`)
- 불필요 정보 숨김: rrf_score, chunk_index — 화면에 표시하되 시각적으로 축소(text-3 색상, 10px)

### 7-2. 업무담당자 (어쏘·사무직)

- 목표: 특정 논점 판례 조사, 서면 작성 근거 수집
- 기본 진입: **검색 화면**
- 인터랙션 패턴: 직접 검색어 입력 → 인용 카드 확인 → 원문 보기 → 재검색
- 정보 밀도: **보통** — 본문 발췌 최대 5줄(line-clamp:5), rrf_score 표시
- 반복 검색 UX: 검색창에 이전 쿼리 유지(JS 불변, HTML value attribute 로 서버 사이드 echo)

### 7-3. IT 담당자

- 목표: 색인 상태 모니터링, 서비스 상태 확인
- 기본 진입: **사건현황 화면** + health 상태 표시 영역
- 추가 표시 항목: chunk_id, ann_rank, fts_rank (IT 페르소나 전용, 기본 숨김 → `.details-toggle` 클릭 시 펼침)
- 사이드카 상태 배너: `/health` 체크 결과를 `.health-banner` 로 상단 표시 (정상 시 비표시)
- `.health-banner--ok / --warn / --down` 3 상태

---

## 8. 접근성 체크리스트 (WCAG AA + KWCAG 2.2)

### 8-1. 색 대비

| 요소                  | 배경                 | 전경               | 최소 비율 | 달성 예상 |
|-----------------------|----------------------|--------------------|-----------|-----------|
| 본문 텍스트           | `#F7F8FA`            | `#111827`          | 4.5:1     | ~15:1     |
| 버튼 레이블(primary)  | `#1A2744`            | `#FFFFFF`          | 4.5:1     | ~12:1     |
| 뱃지 텍스트(금색)     | `#FDF8E7`            | `#B8960C`          | 4.5:1     | 요검증    |
| 뱃지 텍스트(네이비)   | `#E8EDF5`            | `#1A2744`          | 4.5:1     | ~8:1      |
| 플레이스홀더          | `#FFFFFF`            | `#6B7280`          | 3.0:1     | ~4.5:1    |
| 상태 텍스트(에러)     | `#FFFFFF`            | `#DC2626`          | 4.5:1     | 요검증    |

**주의**: 금색 뱃지 (`#B8960C` on `#FDF8E7`) 는 개발 전 실측 필요. 통과 못 하면 `#92720A` 로 어둡게.

### 8-2. 키보드 / 포커스

- 모든 인터랙티브 요소(버튼, 링크, 입력, 선택, 드롭다운) `tab` 순서 논리적 구성
- `:focus-visible` 표시 필수 (`outline:3px solid var(--color-border-focus); outline-offset:2px`)
- 모달/드롭다운 열림 시 포커스 트랩 (vanilla JS — skip if no modal in MVP)
- 검색 입력 후 `Enter` 키로 검색 실행

### 8-3. ARIA / 시맨틱 마크업

| 요소                   | 마크업 규칙                                                     |
|------------------------|-----------------------------------------------------------------|
| 로그인 에러            | `role="alert"` — 스크린리더 즉시 읽기                           |
| 로딩 상태              | `aria-busy="true"` on results section                           |
| 검색 결과 없음         | `role="status"` — polite 읽기                                   |
| 인용 카드 목록         | `<ul>` + `<li>` — 리스트 시맨틱                                 |
| 테이블                 | `<table>` + `<caption>` + `<th scope="col">` — 정렬 시맨틱     |
| 뱃지                   | `aria-label="출처 유형: 판례"` — 시각 텍스트 보완               |
| 검색 입력              | `aria-label="법률 문서 검색"` (label 없을 때)                   |
| 건강 배너              | `role="status"` or `role="alert"` depending on severity        |

### 8-4. 반응형 (MVP 최소 기준)

- 최소 지원 뷰포트: 1024px (데스크탑 사무용 PC 기준)
- 768px 이하: 단일 컬럼, 헤더 컨트롤 축소 — MVP 에서 best-effort
- 폰트 크기: 최소 12px (KWCAG 기준)

---

## 9. 미해결 / 주의 사항

1. **금색 뱃지 대비 실측 미완**: `#B8960C` on `#FDF8E7` — 브라우저 DevTools 또는 WebAIM Contrast Checker 로 확인 후, 4.5:1 미달 시 `#92720A` 사용.
2. **원문 보기 링크 href**: 백엔드가 원문 파일 서빙 엔드포인트를 제공하지 않으면 `.citation-card__link` 는 `aria-disabled="true"` 처리. engineer 가 API 계약 확인 후 결정.
3. **검색어 강조 (`<mark>`)**: 서버 사이드 echo 시 XSS 방지 필수 (Jinja `| e` 이스케이프 후 mark 래핑). frontend JS 강조 대안도 가능.
4. **Pretendard 폰트**: self-host 설치 계획 있으면 `/web/fonts/` 에 woff2 추가 후 `@font-face` 선두에 선언. 현재 스펙은 시스템 폰트 fallback.
5. **IT 담당자 `.details-toggle`**: MVP 에서 JS 없이 `<details>/<summary>` HTML 네이티브로 구현 권장.
6. **`/health` 폴링 주기**: IT 담당자 화면에서만 30초 폴링 (`setInterval`) — 다른 화면은 불필요.
7. **검색 결과 페이지네이션**: 현재 API 계약에 없음 → MVP 는 `top_k` 파라미터로 단일 페이지. 추후 cursor/offset 추가 시 UI 확장.
8. **다크모드**: 미지원 (MVP 범위 밖). `prefers-color-scheme` 무시.
