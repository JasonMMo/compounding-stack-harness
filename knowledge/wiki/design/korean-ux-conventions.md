---
slug: korean-ux-conventions
type: SYNTHESIZED
updated: 2026-06-13
sources: 한국 B2B UX 실무 관행 (더존, 영림원, eGovFrame, 공공 SI 패턴)
related: design/kwcag.md, design/korean-ui-patterns.md, design/templates/
---

# 한국어 UX 관행 — 타이포그래피·폼·인터랙션

> vanilla-htmx + FastAPI harness에서 한국어 UI 구현 시 바로 적용 가능한 실무 기준.

---

## 1. 타이포그래피

### 폰트 우선순위

```css
body {
  font-family: 'Pretendard', 'Noto Sans KR', 'Apple SD Gothic Neo',
               'Malgun Gothic', sans-serif;
  font-size: 16px;      /* base */
  line-height: 1.6;     /* 한국어 가독성 최적 */
  letter-spacing: -0.02em; /* 한글 자간 미세 조정 */
  word-break: keep-all; /* ★ 한국어 줄바꿈 — 어절 단위 유지 */
}
```

| 폰트 | 특징 | 사용 권고 |
|---|---|---|
| **Pretendard** | 라틴·한글 동시 최적, Variable Font | ★ 1순위 (harness 현행) |
| Noto Sans KR | Google 무료, 범용 | Pretendard 없을 때 |
| Apple SD Gothic Neo | macOS/iOS 시스템 | 시스템 폰트 fallback |
| Malgun Gothic | Windows 시스템 | 구형 PC 환경 |

**`word-break: keep-all`은 필수**: 없으면 한글이 글자 단위로 잘려 "이메일 주" / "소를" 처럼 깨짐.

### 텍스트 크기 계층

```css
/* 업무용 UI 기준 — 정보 밀도 우선 */
--text-xs:   12px;  /* 보조, 툴팁 */
--text-sm:   13px;  /* 테이블 셀, 폼 hint */
--text-base: 14px;  /* 테이블 본문, 폼 입력 (업무용 밀도 우선) */
--text-md:   16px;  /* 일반 본문 */
--text-lg:   18px;  /* 소제목 */
--text-xl:   20px;  /* 페이지 제목 */
```

> 공공/ERP는 14px base가 관행 (정보 밀도 > 가독성). 소비자 앱은 16px.

---

## 2. 날짜·시간·숫자 표기

### 날짜

| 용도 | 형식 | 예시 |
|---|---|---|
| 공식 문서, 테이블 | `YYYY.MM.DD` | 2026.06.13 |
| ISO 저장 (DB) | `YYYY-MM-DD` | 2026-06-13 |
| 연월만 | `YYYY년 MM월` | 2026년 06월 |
| 상대 표시 | n분 전 / n시간 전 / 어제 | 3시간 전 |

```html
<!-- 날짜 입력 필드 -->
<input type="date" placeholder="YYYY.MM.DD">
<!-- 또는 텍스트 + 마스킹 -->
<input type="text" placeholder="2026.06.13" maxlength="10">
```

### 시간

```
HH:MM (24시간제) — 업무 시스템 기본
오전/오후 HH:MM — 소비자향, 공지사항
```

### 숫자·금액

```javascript
// 천 단위 구분
(1234567).toLocaleString('ko-KR')  // "1,234,567"

// 금액 표기
"1,234,567원"          // ★ 한국 표준 (숫자 + 원)
"₩1,234,567"           // 국제 문서에서 사용
"KRW 1,234,567"        // 회계 시스템

// 음수 금액
"-1,234원"             // 일반
"(1,234원)"            // 회계 관행 (적자 괄호 표기)
```

---

## 3. 폼 레이아웃 관행

### 레이블 위치

**좌측 레이블 + 우측 입력** (한국 업무용 표준):

```html
<div class="form-row">
  <!-- 2:8 또는 3:9 비율 -->
  <label class="form-label" for="name">고객명</label>
  <div class="form-field">
    <input id="name" type="text">
  </div>
</div>
```

```css
.form-row    { display: grid; grid-template-columns: 120px 1fr; gap: 8px; align-items: center; }
.form-label  { text-align: right; padding-right: 8px; font-weight: 500; }
```

> 소비자향(모바일 우선)은 상단 레이블. 업무용 PC UI는 좌측 레이블이 공간 효율 우위.

### 필수 항목 표시

```html
<!-- ★ 방식 1: 레이블 뒤에 빨간 별표 (가장 일반적) -->
<label for="name">고객명 <span class="required" aria-hidden="true">*</span>
  <span class="sr-only">(필수)</span>
</label>

<!-- 방식 2: 필드 그룹 상단 범례 -->
<p class="form-note"><span class="required">*</span> 필수 입력 항목입니다.</p>
```

```css
.required { color: #E53E3E; font-weight: bold; }
.sr-only  { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }
```

### 그룹박스 (필드 구분선)

```html
<!-- 한국 업무 화면 특유: fieldset으로 섹션 구분 -->
<fieldset class="form-group">
  <legend class="form-group__title">기본 정보</legend>
  <!-- fields -->
</fieldset>
```

---

## 4. 버튼 텍스트 & 배치 관행

### 버튼 텍스트

| 상황 | 권고 텍스트 | 피해야 할 것 |
|---|---|---|
| 새 데이터 생성 | **등록** | Save, Submit, 생성 |
| 기존 데이터 수정 저장 | **저장** | Update, 수정완료 |
| 조회 실행 | **조회** | Search, 검색 |
| 레이어팝업 닫기 | **닫기** | Cancel (취소와 구분) |
| 작업 취소 | **취소** | 뒤로, Cancel |
| 삭제 확인 | **삭제** | Delete, OK |
| 긍정 확인 | **확인** | OK, Yes |

### 버튼 배치 (좌→우 순서)

```
[부정/취소]  [긍정/확인]      ← 한국 표준 (우측 = 주 액션)
예: [취소] [저장]
    [삭제] [확인]

단, 모달 파괴적 액션:
[아니오] [예, 삭제합니다]    ← 주 액션도 우측
```

---

## 5. 오류 메시지 어조

```
정중 명령형 (표준): "이름을 입력해 주세요."
금지: "이름 입력!" / "Error: required field" / "잘못된 입력"

숫자 범위: "1~100 사이의 숫자를 입력해 주세요."
형식 오류: "날짜 형식이 올바르지 않습니다. (예: 2026.06.13)"
중복: "이미 사용 중인 이메일입니다."
```

```html
<!-- 인라인 오류 — 필드 바로 아래 -->
<input aria-invalid="true" aria-describedby="email-err">
<p id="email-err" class="field-error" role="alert">
  올바른 이메일 형식으로 입력해 주세요.
</p>
```

```css
.field-error { color: #E53E3E; font-size: 12px; margin-top: 4px; }
.field-error::before { content: "⚠ "; }
```

---

## 6. 테이블 인터랙션 패턴

### 표준 업무 테이블 구조

```html
<table>
  <thead>
    <tr>
      <th class="col-check"><input type="checkbox" aria-label="전체 선택"></th>
      <th class="col-no">No.</th>    <!-- 순번 — 필수 관행 -->
      <th>고객명</th>
      <th>등록일</th>
      <th class="col-action">관리</th>  <!-- 액션 열 -->
    </tr>
  </thead>
</table>
```

### Hover Action (행 위 마우스오버 시 버튼 노출)

```css
.row-actions { opacity: 0; transition: opacity 0.15s; }
tr:hover .row-actions { opacity: 1; }
```

> 발견성 저하 트레이드오프 — 신규 사용자 교육 필요. 공공 SI에서 일반적이나 초보자 혼란 주의.

### 일괄 작업 (Bulk Action)

```html
<!-- 체크박스 선택 후 상단 툴바 출현 -->
<div class="bulk-toolbar" hidden>
  <span class="selected-count">3개 선택됨</span>
  <button>일괄 삭제</button>
  <button>내보내기</button>
</div>
```

### 페이지네이션

```html
<!-- 숫자 페이징 (한국 표준) -->
<nav aria-label="페이지 탐색">
  <button aria-label="이전 페이지">◀</button>
  <button aria-current="page">1</button>
  <button>2</button>
  <button>3</button>
  <button aria-label="다음 페이지">▶</button>
</nav>
<!-- 행 수 선택: 10 / 20 / 50 / 100 -->
<select aria-label="페이지당 행 수">
  <option>10</option><option>20</option><option>50</option>
</select>
```

---

## 7. 검색/조회 패널 패턴

한국 업무 화면 표준 레이아웃: **상단 검색 → 결과 테이블**.

```html
<section class="search-panel">
  <div class="search-fields">
    <!-- 조건 필드들 (2~4열 그리드) -->
    <label>기간 <input type="date"> ~ <input type="date"></label>
    <label>상태 <select>...</select></label>
  </div>
  <div class="search-actions">
    <button type="submit" class="btn-primary">조회</button>  <!-- 우측 또는 필드 끝 -->
    <button type="reset">초기화</button>
  </div>
</section>
<section class="result-panel">
  <!-- Dense Table -->
</section>
```

---

## 8. 모달/레이어팝업 관행

```
크기: 소 400px / 중 600px / 대 800px / 전체화면
헤더: 제목 + 우측 X 버튼 (닫기)
바닥: [취소] [확인] 또는 [닫기]
배경: dim overlay (rgba 0.4~0.6)
ESC 키: 닫힘
포커스 트랩: 모달 내부만 Tab 순환
```

> 한국 업무 시스템은 "레이어팝업"이라 부름. 새 창(window.open) 방식은 팝업 차단으로 사실상 사용 불가.
