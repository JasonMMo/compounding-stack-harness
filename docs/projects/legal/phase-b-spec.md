> [← 법무 통합 제품](README.md)

# Phase B 빌드 스펙 — 사건관리 화면 (Read-Only)

> owner: PM  
> 상태: DRAFT v0.1 (2026-06-21)  
> 구현 대상: `frontend/adapters/legal-pro/` (React + Vite)  
> 상위 입력: D1 · D2 · D3 · D4 + 라이브 API 계약 (`services/legal-rag/api.py`)  
> 하위 소비자: engineer (이 문서가 구현 단일 계약)

---

## 1. 범위 & 의존성

### 1.1 Phase B 포함

| 항목 | 설명 |
|---|---|
| CasesScreen (`/cases`) | `GET /cases` 를 호출하는 사건 목록 화면. 페이지네이션(limit/offset/total) 포함 |
| CaseDetailScreen (`/cases/:id`) | `GET /cases/{case_id}` 를 호출하는 사건 상세 + 소속 문서 목록 화면 |
| wire.ts 확장 | `apiListCases`, `apiGetCase` 함수 추가. Phase A 기존 코드 건드리지 않음 |
| App.tsx 라우트 추가 | `/cases`, `/cases/:id` 두 라우트 등록 (Phase A `/search`, `/login` 유지) |
| 사건현황 탭 → 판례검색 탭 진입 동선 | 사건 행의 [검색] 버튼이 `PrecedentSearchScreen` 으로 `case_id` 를 query-param 또는 state 로 전달. Phase A `PrecedentSearchScreen` 재사용 — 재구현 금지 |

### 1.2 Phase B 제외 (out-of-scope)

| 제외 항목 | 차단 슬롯 | 근거 |
|---|---|---|
| 사건 생성 (`POST /cases`) | G-2 / Q-1 | API 미구현. Q-1(CEO 범위 확정) 선결 |
| 사건 수정 (`PATCH /cases/{id}`) | G-2 / Q-1 | 동일 |
| 사건 삭제 | G-5 | 법적 감사 요건 — 의도된 설계 결정(F-07). 영구 배제 |
| 원문 서빙 drawer (`GET /documents/…`) | G-3 | 파일 다운로드/미리보기 UX 미확정. 버튼은 `aria-disabled` 유지 |
| 사건 당사자(party) 표시 | Q-1 | `legal_case_party` 읽기 엔드포인트 미존재. 추후 Q-1 슬롯 |

### 1.3 차단 없음 확인

Phase B 에서 사용하는 읽기 엔드포인트 3종은 백엔드에 이미 구현·라이브 상태다:

- `GET /cases` — `CasesResponse` 반환. RLS 적용, 페이지네이션 지원
- `GET /cases/{case_id}` — `CaseDetailResponse` 반환. UUID 검증, 404 은폐 적용
- `GET /documents/{source_type}/{source_id}` — `DocumentResponse` 반환. Phase B 에서는 버튼 `aria-disabled` 유지 (G-3). 추후 G-3 해소 시 해제

---

## 2. 화면 목록

### 2.1 CasesScreen — 사건 목록

| 항목 | 내용 |
|---|---|
| D2 S-ID | S-09 (로딩) / S-10 (정상, 혼합) / S-11 (빈 목록) / S-12 (로드 실패) |
| D3 와이어프레임 | §11 S-09, §12 S-10, §13 S-11, §14 S-12 |
| 라우트 | `/cases` |
| 진입 | 로그인 성공 후 탭 [사건 현황] 클릭, 또는 `/cases` 직접 접근 (RequireAuth 가드) |
| 이탈 | [검색] 버튼 → `/search?case_id=<uuid>` 이동. 행 클릭 → `/cases/:id` 이동. 탭 [문서 검색] 클릭 → `/search` 이동 |
| 탭 active | 사건 현황 탭이 `aria-selected="true"` |

**판례검색 패널 통합 동선**: 사건 행의 [검색] 버튼 클릭 시 Phase A `PrecedentSearchScreen` 으로 이동하되, `case_id` 를 React Router의 `state` 또는 URL query-param(`?case_id=<uuid>`)으로 전달한다. `PrecedentSearchScreen` 은 해당 값을 초기 사건 필터 드롭다운에 자동 설정한다. 이것이 D3 §1 에 정의된 "1앱 단일 내러티브" 연결 고리다. Phase A `PrecedentSearchScreen` 은 재구현하지 않는다.

### 2.2 CaseDetailScreen — 사건 상세

| 항목 | 내용 |
|---|---|
| D2 S-ID | [[S-16]] (D2 점선 플레이스홀더 → Phase B 에서 확정 화면으로 승격) |
| D3 와이어프레임 | §18 [[S-16]] 힌트 |
| 라우트 | `/cases/:id` |
| 진입 | CasesScreen 사건 행 클릭 → push `/cases/<uuid>` |
| 이탈 | [← 목록으로] 버튼 → `/cases`. [검색] 버튼 → `/search?case_id=<uuid>` |
| 탭 active | 사건 현황 탭 유지 (`aria-selected="true"`) |

**내용**: 사건 메타(case_number, title, status, case_type, description, opened_at) + 소속 문서 목록(CaseDocumentItem 목록, ingest_status 뱃지). [검색] 버튼은 CasesScreen 과 동일하게 해당 `case_id` 를 `PrecedentSearchScreen` 으로 전달.

**존재 은폐**: 백엔드가 타 변호사 사건을 404 로 처리. 프런트는 404 응답을 "사건을 찾을 수 없습니다." 메시지로 렌더링 (사건 존재 여부 노출 금지).

---

## 3. 데이터 바인딩 표

### 3.1 CasesScreen — `GET /cases` 응답 바인딩

`GET /cases?limit={n}&offset={m}` → `CasesResponse`

| UI 요소 | 응답 필드 | 타입 | 예시 | 비고 |
|---|---|---|---|---|
| 사건번호 열 | `cases[i].case_number` | `str` | `"2024가합12345"` | |
| 사건명 열 | `cases[i].title` | `str` | `"손해배상(불법행위)"` | |
| 사건 상태 열 | `cases[i].status` | `str` | `"active"` | UI 매핑: active→진행중, closed→종결, intake→접수중, trial→재판중, appeal→항소중, withdrawn→취하 |
| 색인 상태 뱃지 | `cases[i].doc_indexed` / `doc_pending` / `doc_failed` | `int` | `34`, `0`, `2` | 뱃지 로직: doc_failed>0→실패, doc_pending>0→대기중, else→완료 (우선순위: 실패>대기>완료) |
| 문서 수 열 | `cases[i].doc_total` | `int` | `36` | `"36건"` 표시 |
| 행 클릭 대상 ID | `cases[i].case_id` | `str` (UUID) | `"f47ac10b-58cc-..."` | `/cases/<case_id>` 이동용 |
| [검색] 버튼 payload | `cases[i].case_id` | `str` (UUID) | 위 동일 | `/search?case_id=<id>` 또는 router state |
| **페이지네이션: 전체 건수** | `total` | `int` | `42` | "총 42건" 표시 |
| **페이지네이션: 현재 페이지** | `offset` / `limit` | `int` | `0`, `20` | 페이지 번호: `Math.floor(offset/limit)+1` |
| **페이지네이션: 이전/다음** | `offset`, `limit`, `total` | `int` | — | 이전: `offset-limit >= 0`, 다음: `offset+limit < total` |
| 빈 상태 조건 | `cases.length === 0 && total === 0` | — | — | S-11 렌더 |

**페이지 컨트롤 UI 동작**:
- 기본 page size: `limit=20` (서버 default 50 을 UI 기본으로 20 으로 오버라이드 가능)
- 서버 hard cap: `limit` 최대 200 (`_CASES_LIST_MAX_LIMIT`)
- 페이지 이동 시 `offset = (page-1) * limit` 으로 계산하여 재호출
- `total` 을 사용해 전체 페이지 수 계산: `Math.ceil(total / limit)`

### 3.2 CaseDetailScreen — `GET /cases/{case_id}` 응답 바인딩

`GET /cases/{case_id}` → `CaseDetailResponse`

| UI 요소 | 응답 필드 | 타입 | 예시 | 비고 |
|---|---|---|---|---|
| 사건번호 | `case_number` | `str` | `"2024가합12345"` | |
| 사건명 | `title` | `str` | `"손해배상(불법행위)"` | |
| 사건 상태 | `status` | `str` | `"active"` | 위 status UI 매핑 동일 |
| 사건 유형 | `case_type` | `str \| null` | `"civil"` | null이면 표시 생략 |
| 사건 개요 | `description` | `str \| null` | `"불법행위로 인한..."` | null이면 표시 생략 |
| 접수일 | `opened_at` | `str \| null` | `"2024-03-15"` | DB `filed_date::text` 값 |
| 종결일 | `closed_at` | `str \| null` | `null` | null이면 표시 생략 |
| 문서 목록 아이템 — 제목 | `documents[i].title` | `str \| null` | `"원고 손해배상 청구 준비서면"` | |
| 문서 목록 아이템 — 유형 | `documents[i].document_type` | `str \| null` | `"brief"` | |
| 문서 목록 아이템 — 색인상태 뱃지 | `documents[i].ingest_status` | `str \| null` | `"done"` | done→색인완료, pending/processing→대기중, error→실패, null→상태불명 |
| 원문 보기 버튼 | `documents[i].doc_id` | `str` (UUID) | — | `aria-disabled="true"` 고정 (G-3 보류). title="원문 서빙 준비 중" tooltip |
| 문서 건수 소계 | `documents.length` | `number` | `12` | "문서 12건" 표시 |

### 3.3 인용 카드(PrecedentSearchScreen) 재사용 — 데이터 바인딩 불변

Phase A 의 `CitationOut` 바인딩은 Phase B 에서 변경 없이 유지된다.

| 필드 | 타입 | Phase B 변경 여부 |
|---|---|---|
| `chunk_id` | `str` | 불변 |
| `source_type` | `'precedent' \| 'case_document'` | 불변 |
| `relevance` | `number \| null` | 불변 (`Math.round(relevance*100)%` 표시) |
| `rrf_score` | `number` | 불변 (IT 상세 패널) |
| `holding_summary` | `str \| null` | 불변 (판례 카드 판시요지) |

---

## 4. 보존 계약 (불변식)

engineer 가 Phase B 를 구현하는 동안 절대 깨지 않아야 하는 계약이다.

### 4.1 RLS — 프런트는 JWT 전달만

모든 읽기 요청에 `Authorization: Bearer <token>` 헤더를 전달한다. 데이터 격리(RLS)는 백엔드 DB 레이어가 강제한다. 프런트는 attorney 필터링 로직을 직접 구현하지 않는다. `getToken()` (App.tsx) 을 통해 세션스토리지 토큰을 읽어 `wire.ts` 의 `legalRequest` 에 전달하는 패턴을 그대로 따른다.

### 4.2 페이지네이션 — offset 기반, total 표시 (D2 G-4 계약)

`GET /cases?limit={n}&offset={m}` 호출. 응답의 `total` 필드(RLS 필터 후 DB COUNT)를 사용해 전체 페이지 수를 계산하여 UI에 표시한다. `total` 없이 다음 페이지 존재 여부를 추측하는 infinite-scroll 패턴 금지. 페이지 컨트롤은 "이전" / "다음" 또는 번호 형태 모두 허용하나, 반드시 `total` 기반으로 계산한다.

### 4.3 임베디드 판례검색 — citation 1:1 · relevance% 계약 보존

사건 화면에서 `PrecedentSearchScreen` 으로 진입할 때, Phase A 가 구현한 `CitationOut.relevance` → `Math.round(relevance*100)%` 표시 계약을 변경하지 않는다. `case_id` 전달 방식(query-param 또는 router state)은 engineer 가 선택하되, `PrecedentSearchScreen` 의 내부 검색 로직·API 호출·인용 카드 렌더링은 수정 금지다.

### 4.4 middle contract 읽기전용 (open-closed)

`frontend/adapters/legal-pro/src/contract/contract.gen.ts` 와 `middle/contract/` 는 읽기만 한다. Phase B 신규 엔드포인트(`/cases`, `/cases/:id`)는 `contract.gen.ts` 에 새 상수를 추가하는 방식으로 확장하되, 기존 상수(`auth_login`, `search`, `health`) 는 변경하지 않는다.

---

## 5. Out-of-Scope (명시)

| 항목 | 보류 슬롯 | 해소 조건 |
|---|---|---|
| 사건 생성 화면 (`POST /cases`) | G-2 / Q-1 | CEO 가 Q-1 (사건 CRUD 범위) 확정 → engineer 가 API 구현 → 별도 스펙 |
| 사건 수정 화면 (`PATCH /cases/{id}`) | G-2 / Q-1 | 위 동일 |
| 사건 삭제 | G-5 | 영구 배제 (F-07, 법적 감사 불변). 해소 조건 없음 |
| 원문 서빙 drawer | G-3 | `GET /documents/{source_type}/{source_id}` UX(파일 다운로드 vs 인앱 뷰어) 확정 후 별도 스펙. "원문 보기 →" 버튼은 `aria-disabled` 유지 |
| 사건 당사자(party) 목록 | Q-1 연동 | `GET /cases/{id}/parties` 엔드포인트 미존재. Q-1 범위 확정 후 검토 |
| `legal_rag_query_log` 이력 UI | Q-3 | query_text 평문저장 개인정보 협의 후 별도 설계 |
| 파트너 전용 CEO 캡션 | 추후 | `partner_id` 여부를 JWT claim 에서 읽어야 함. 현재 claim 에 `is_partner` 없음. 추후 백엔드 JWT 확장 필요 |

---

## 6. 수용 기준 (Acceptance Criteria)

Phase B 완료 판정 체크리스트. QA 게이트 통과 + 아래 전 항목 충족이 인도 조건.

### AC-01 — L3 빌드 PASS

```
cd frontend/adapters/legal-pro && npm run build
```

TypeScript 컴파일 에러 0건, Vite 빌드 성공 (BUILD SUCCESS). `tsc --noEmit` 통과 포함.

### AC-02 — CasesScreen 목록 렌더

- 로그인 후 `/cases` 진입 시 `GET /cases` 호출, 사건 행이 테이블로 렌더된다.
- `case_number`, `title`, `status`(한국어 매핑), `doc_total`, 색인 상태 뱃지가 각 행에 표시된다.
- 색인 상태 뱃지 우선순위(실패 > 대기 > 완료)가 올바르게 적용된다.

### AC-03 — 페이지네이션 동작

- `total` 값 기반으로 페이지 컨트롤이 렌더된다.
- 이전/다음 버튼이 올바른 `offset` 을 계산하여 재호출한다.
- `total === 0` 이면 S-11 빈 상태 메시지가 표시된다.

### AC-04 — RLS 격리 확인 (UI 레벨)

- 로그인한 변호사의 JWT 로 `/cases` 호출 시, 해당 변호사가 접근 불가한 사건이 목록에 없어야 한다 (백엔드 RLS가 보장; 프런트 단언: JWT 없이 호출 시 401 → 로그인 화면 리디렉션).

### AC-05 — CaseDetailScreen 렌더

- CasesScreen 에서 사건 행 클릭 → `/cases/:id` 진입.
- `GET /cases/{case_id}` 응답의 `case_number`, `title`, `status`, `description`, `opened_at`, 문서 목록이 올바르게 렌더된다.
- 문서 목록의 `ingest_status` 뱃지가 색인상태 매핑(done/pending·processing/error/null)에 따라 올바르게 표시된다.

### AC-06 — 404 존재 은폐

- 접근 불가 `case_id` 로 `/cases/:id` 진입 시 백엔드 404 → "사건을 찾을 수 없습니다." 메시지 표시. 별도 403 분기 금지 (백엔드가 404로 은폐).

### AC-07 — 판례검색 연동

- CasesScreen 사건 행의 [검색] 버튼 클릭 → `PrecedentSearchScreen` 으로 이동, 해당 `case_id` 가 사건 필터 드롭다운에 자동 설정된다.
- CaseDetailScreen 의 [검색] 버튼도 동일하게 동작한다.
- `PrecedentSearchScreen` 의 기존 코드는 변경되지 않았다.

### AC-08 — 원문 보기 버튼 aria-disabled

- CaseDetailScreen 의 모든 문서 행에서 "원문 보기" 버튼은 `aria-disabled="true"`, `tabindex="-1"`, 클릭 핸들러 없음, `title="원문 서빙 준비 중"` 상태여야 한다 (G-3 보류).

### AC-09 — 에러 상태

- `GET /cases` 401 → 세션 만료 메시지 + 로그인 화면 리디렉션 (wire.ts `clearToken()` 패턴).
- `GET /cases` 5xx → "사건 목록을 불러오지 못했습니다." 메시지.
- `GET /cases/{id}` 404 → AC-06 단언.

### AC-10 — 삭제 UI 없음

- CasesScreen, CaseDetailScreen 어디에도 삭제 버튼, 삭제 메뉴, 삭제 확인 다이얼로그가 존재하지 않는다 (F-07, G-5).

---

## 7. 열린 질문

| # | 질문 | owner | 영향 |
|---|---|---|---|
| OQ-1 | `GET /cases` 의 기본 `limit` 를 UI에서 20으로 오버라이드할 것인지, 서버 default(50)를 그대로 쓸 것인지 | CTO | 페이지네이션 초기 page size UX |
| OQ-2 | CasesScreen에서 사건 행 클릭 시 `/cases/:id` drill-down 화면을 같은 탭 레이아웃 안에 렌더할 것인지, 전체 라우트 전환으로 처리할 것인지 (현재 스펙은 전체 라우트 전환 가정) | CTO | 탭 active 상태 유지 여부 |
| OQ-3 | `case_id` 를 `PrecedentSearchScreen` 에 전달하는 방식으로 React Router `state` vs URL query-param(`?case_id=`) 중 어느 것을 표준으로 삼을 것인지 | engineer | URL 공유 가능성, 뒤로가기 UX |
| OQ-4 | JWT claim 에 `is_partner` 또는 `role` 이 없어 파트너 변호사임을 프런트에서 식별 불가. D3 S-10 의 "파트너 로그인 중" 캡션을 이번 Phase B 에 포함할 것인지 (포함하려면 백엔드 JWT 확장 필요) | CTO | 백엔드 JWT 확장 여부 |
