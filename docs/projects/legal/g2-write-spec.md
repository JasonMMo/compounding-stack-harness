> [← 법무 통합 제품](README.md)

# G-2 빌드 스펙 — 사건 쓰기 (Write)

> owner: PM  
> 상태: DRAFT v0.1 (2026-06-22)  
> 구현 대상: `frontend/adapters/legal-pro/` (React + Vite) + `services/legal-rag/api.py`  
> 상위 입력: D1(F-xx) · D2(S-17, G-2) + 라이브 DDL(`presets/ddl/augments/legal/`) + 라이브 API 계약  
> 하위 소비자: engineer (이 문서가 G-2 구현 단일 계약), QA, CISO

---

## 0. 경계 선언 (읽기 전 필독)

| 구분 | 내용 |
|---|---|
| **이번 범위 (G-2)** | (1) 사건 메타 생성/수정, (2) 당사자(`case_party`) 등록/수정, (3) 문서 첨부 (업로드 → ingest → ingest_status 뱃지 표시) |
| **이번 범위 아님** | 원문 전체 열람 뷰어 (파일 다운로드·미리보기 drawer) — **G-3, phase 2**. 단 문서 행의 ingest_status 뱃지 표시는 이번 포함 |
| **영구 배제** | 사건·당사자·문서 삭제 — 법적 감사 요건 (D1 F-07, DDL `NO DELETE POLICY`). 해소 조건 없음 |
| **생성자 제약** | 담당 변호사 본인만 사건·당사자·문서를 생성할 수 있다. RLS INSERT 정책이 `assigned_attorney_id = current_user` 를 DB 계층에서 강제한다. 파트너가 주니어에게 사건을 배정하는 워크플로우는 v1 불가 |

---

## 1. 범위 & 의존성

### 1.1 G-2 포함 (3 sub-phase)

| sub-phase | 항목 | 이유 |
|---|---|---|
| **C1** | 사건 메타 생성 (`POST /cases`) + 수정 (`PATCH /cases/{id}`) | DDL·RLS 완비. 최저 리스크 |
| **C2** | 당사자(`case_party`) 등록 (`POST /cases/{id}/parties`) + 수정 (`PATCH /cases/{id}/parties/{party_id}`) | PII(이름·연락처) RLS 격리 완비. C1 사건 존재 선결 |
| **C3** | 문서 첨부 업로드 (`POST /cases/{id}/documents`, multipart) + 비동기 ingest + 상태 폴링 | 파일업로드 + BackgroundTasks + 저장 볼륨 + CISO 게이트. 최고 리스크 |

각 sub-phase 는 독립 머지 가능하도록 설계한다.

### 1.2 G-2 제외 (out-of-scope)

| 제외 항목 | 슬롯 | 근거 |
|---|---|---|
| 원문 전체 열람 뷰어 (파일 다운로드/인앱 미리보기) | G-3 phase 2 | UX(다운로드 vs 인앱 뷰어) 미확정. 이번 범위 아님 |
| 사건·당사자·문서 삭제 | 영구 배제 | 법적 감사 요건 (D1 F-07) |
| 파트너가 주니어에게 배정하는 워크플로우 | v2 후보 | JWT claim 에 `is_partner` 없음. RLS 설계 변경 필요 |
| 사건 검색·목록 필터·정렬 변경 | Phase B 유지 | 읽기화면 기존 계약 불변 |
| content_text 즉시 기록 | phase 2 (G-3 대비) | 현재 ingest.py 미기록. 추후 보강 |
| mime/size 컬럼 추가 | DBA 별도 augment 후보 | 현재 DDL 에 없음. 이번 필수 아님 |

### 1.3 차단 없음 확인

G-2 에서 추가할 쓰기 엔드포인트는 백엔드 미구현 상태다. engineer 가 이 스펙을 입력으로 구현한다. 하지만 DDL·RLS·ingest pipeline 은 이미 live 이므로 신규 DDL 없이 API 레이어만 추가하면 된다.

---

## 2. 화면 목록

### 2.1 CaseCreateScreen — 사건 생성 폼

| 항목 | 내용 |
|---|---|
| D2 S-ID | S-17 (미확정 → G-2 에서 확정) |
| 라우트 | `/cases/new` |
| 진입 | CasesScreen `[새 사건 등록]` 버튼 클릭 |
| 이탈 | 저장 성공 → `/cases/<new_case_id>` (CaseDetailScreen). 취소 → `/cases` |
| 탭 active | 사건 현황 탭 (`aria-selected="true"`) |

**필드**: case_number (필수), title (필수), case_type (선택), status (필수, 기본값 `intake`), description (선택), opened_at (선택).

### 2.2 CaseEditScreen — 사건 수정 폼

| 항목 | 내용 |
|---|---|
| 라우트 | `/cases/:id/edit` |
| 진입 | CaseDetailScreen `[사건 수정]` 버튼 클릭 (담당/파트너 변호사만 버튼 표시) |
| 이탈 | 저장 성공 → `/cases/<id>`. 취소 → `/cases/<id>` |

**필드**: CaseCreateScreen 동일 (case_number 표시 전용, 수정 불가 선택 — OQ-5 참조).

### 2.3 PartyPanel — 당사자 등록/수정 패널

| 항목 | 내용 |
|---|---|
| 위치 | CaseDetailScreen 내 "당사자" 섹션 (별도 라우트 없음, 인라인 패널) |
| 진입 | CaseDetailScreen 의 `[당사자 추가]` 버튼 클릭 → 폼 패널 슬라이드인 |

**필드**: role (필수, SELECT: plaintiff/defendant/witness/opposing-counsel/expert-witness), name (필수), notes (선택). `contact_id` 는 v1 미노출 (contact 엔티티 연동 미구현 — OQ-6).

### 2.4 DocumentUploadPanel — 문서 첨부 패널

| 항목 | 내용 |
|---|---|
| 위치 | CaseDetailScreen 내 "문서" 섹션 `[문서 업로드]` 버튼 클릭 → 오버레이 |
| 파일 선택 | `<input type="file" accept=".pdf,.docx,.txt,.md">` |
| 업로드 후 | 즉시 201 응답 → 문서 목록에 행 추가(ingest_status=pending 뱃지) |
| 상태 폴링 | GET CaseDetail 주기적 재호출(3~5초) 또는 수동 새로고침으로 ingest_status 갱신 |

**필드 (폼 입력)**: 파일(필수), document_type (필수, SELECT: complaint/brief/evidence/court-order/contract/correspondence/other), title (선택, 미입력 시 sanitized 파일명 사용), filed_at (선택), notes (선택).

---

## 3. API 엔드포인트 명세

### 3.1 C1 — 사건 메타 CRUD

#### POST /cases — 사건 생성

**메서드·경로**: `POST /cases`  
**인증**: Bearer JWT 필수 (미들웨어 검증)  
**요청 바디** (`application/json`):

| 필드 | 타입 | 필수 | 검증 규칙 |
|---|---|---|---|
| `case_number` | `str` | Y | 최대 64자, 공백 불가 |
| `title` | `str` | Y | 최대 512자 |
| `case_type` | `str \| null` | N | enum: civil/criminal/administrative/family/commercial/other. null 허용 |
| `status` | `str` | Y (default: `intake`) | enum: intake/active/trial/appeal/closed/withdrawn |
| `description` | `str \| null` | N | 최대 4000자 |
| `opened_at` | `str \| null` | N | ISO date string `YYYY-MM-DD`. null 허용 |

**RLS INSERT**: `assigned_attorney_id` 를 JWT `sub`(current_user_id) 로 서버가 고정 주입. 클라이언트가 이 필드를 제출해도 무시. DB RLS `WITH CHECK (assigned_attorney_id = current_setting(...)::uuid)` 가 최종 강제.

**응답 201** (`CaseOut`):

```json
{
  "case_id": "<uuid>",
  "case_number": "2026가합99001",
  "title": "...",
  "status": "intake",
  "doc_total": 0,
  "doc_indexed": 0,
  "doc_pending": 0,
  "doc_failed": 0
}
```

**오류**:
- 401: JWT 없음/만료
- 403: RLS 위반 (DB exception → 500 대신 403 으로 wrapping)
- 422: 검증 실패 (Pydantic ValidationError)
- 409: case_number unique 충돌 (DB unique violation → 409 wrapping)

---

#### PATCH /cases/{case_id} — 사건 수정

**메서드·경로**: `PATCH /cases/{case_id}`  
**인증**: Bearer JWT 필수  
**경로 파라미터**: `case_id` UUID 형식 검증  
**요청 바디** (`application/json`, partial — 제출 필드만 업데이트):

| 필드 | 타입 | 검증 규칙 |
|---|---|---|
| `title` | `str \| null` | 최대 512자 |
| `case_type` | `str \| null` | enum 동일 |
| `status` | `str \| null` | enum 동일 |
| `description` | `str \| null` | 최대 4000자 |
| `opened_at` | `str \| null` | ISO date `YYYY-MM-DD` |
| `closed_at` | `str \| null` | ISO date `YYYY-MM-DD`. status=closed 시 자동 설정 권고 |

`case_number` 수정 불가 (필드 존재해도 무시 — immutable PK 대용). `assigned_attorney_id`, `partner_id` 수정 불가 (application layer 에서 명시 차단. v1 배정 변경 기능 없음).

**RLS UPDATE**: `USING (assigned_attorney_id=user OR partner_id=user)` + `WITH CHECK` 동일. 타 변호사 사건 PATCH 시도 → 404 (존재 은폐).

**응답 200** (`CaseDetailResponse` — 기존 모델 재사용):

```json
{
  "case_id": "<uuid>",
  "case_number": "...",
  "title": "...",
  "status": "active",
  "case_type": "civil",
  "description": "...",
  "opened_at": "2026-01-15",
  "closed_at": null,
  "documents": [...]
}
```

**오류**: 401, 404 (미존재 또는 타 변호사 사건 = 존재 은폐), 422.

---

### 3.2 C2 — 당사자 CRUD

#### POST /cases/{case_id}/parties — 당사자 등록

**메서드·경로**: `POST /cases/{case_id}/parties`  
**인증**: Bearer JWT 필수  
**요청 바디** (`application/json`):

| 필드 | 타입 | 필수 | 검증 규칙 |
|---|---|---|---|
| `role` | `str` | Y | enum: plaintiff/defendant/witness/opposing-counsel/expert-witness |
| `name` | `str` | Y | 최대 256자 |
| `notes` | `str \| null` | N | 최대 2000자 |

`contact_id` 는 v1 미노출 — 서버가 NULL 고정. 클라이언트 제출 필드 무시.

**RLS INSERT**: `EXISTS(SELECT 1 FROM legal_case WHERE id=case_id AND (assigned_attorney_id=user OR partner_id=user))`. 부모 사건이 없거나 접근 불가 → 404 (존재 은폐).

**응답 201** (`CasePartyOut` — 신규 모델):

```json
{
  "party_id": "<uuid>",
  "case_id": "<uuid>",
  "role": "plaintiff",
  "name": "주식회사 한빛테크",
  "notes": "원고 법인."
}
```

**오류**: 401, 404 (사건 미존재 또는 접근 불가), 422.

---

#### PATCH /cases/{case_id}/parties/{party_id} — 당사자 수정

**메서드·경로**: `PATCH /cases/{case_id}/parties/{party_id}`  
**인증**: Bearer JWT 필수  
**요청 바디** (`application/json`, partial):

| 필드 | 타입 | 검증 규칙 |
|---|---|---|
| `role` | `str \| null` | enum 동일 |
| `name` | `str \| null` | 최대 256자 |
| `notes` | `str \| null` | 최대 2000자 |

**RLS UPDATE**: 부모 `legal_case` 를 통한 동일 USING+WITH CHECK. 타 변호사 사건의 party 수정 시도 → 404.

**응답 200** (`CasePartyOut` 동일 구조).

**오류**: 401, 404 (사건·party 미존재 또는 접근 불가), 422.

---

### 3.3 C3 — 문서 첨부 업로드

#### POST /cases/{case_id}/documents — 문서 업로드

**메서드·경로**: `POST /cases/{case_id}/documents`  
**인증**: Bearer JWT 필수  
**콘텐츠타입**: `multipart/form-data`  
**요청 파트**:

| 파트명 | 타입 | 필수 | 검증 규칙 |
|---|---|---|---|
| `file` | binary | Y | 확장자 allowlist: `.pdf .docx .txt .md`. 최대 크기: 20MB. content-type 점검. 빈 파일 거부 |
| `document_type` | `str` | Y | enum: complaint/brief/evidence/court-order/contract/correspondence/other |
| `title` | `str` | N | 최대 512자. 미입력 시 sanitized 파일명 사용 |
| `filed_at` | `str` | N | ISO date `YYYY-MM-DD`. null 허용 |
| `notes` | `str` | N | 최대 2000자 |

**서버 처리 (확정 디폴트)**:

1. 파일 확장자·크기·content-type 검증 (실패 시 400).
2. `storage_key` 서버 생성: `legal/cases/<case_id>/<uuid4>_<sanitized_filename>`. 클라이언트 파일명 경로 신뢰 금지 (path traversal 차단).
3. 파일을 `LEGAL_STORAGE_ROOT/<storage_key>` 에 저장 (로컬 디스크 볼륨, Coolify 영속 볼륨 필요 — devops 후속 AC 명시).
4. `legal_case_document` 행 INSERT (`app_user` RLS, `ingest_status='pending'`, `storage_key` 기록) → **즉시 201 반환**.
5. FastAPI `BackgroundTasks` 로 `ingest_file(conn=app_service, ...)` 비동기 실행 → `ingest_status`: pending → processing → done/error.

**RLS INSERT**: `legal_case_document` 에 대한 `rls_legal_case_document_insert` 정책 적용 (부모 사건 담당/파트너 변호사만). 접근 불가 사건 → 404 (존재 은폐).

**응답 201** (`CaseDocumentUploadOut` — 신규 모델):

```json
{
  "doc_id": "<uuid>",
  "case_id": "<uuid>",
  "title": "원고 손해배상 청구 준비서면",
  "document_type": "brief",
  "ingest_status": "pending",
  "filed_at": null,
  "notes": null
}
```

**오류**:
- 400: 확장자 비허용 / 크기 초과 / 빈 파일
- 401: JWT 없음/만료
- 404: 사건 미존재 또는 접근 불가 (존재 은폐)
- 413: Content-Length 초과 (미들웨어 레벨)
- 422: form 파라미터 검증 실패

**CISO 게이트**: C3 머지 전 CISO 리뷰 필수. 점검 항목: 확장자 allowlist 준수, path traversal 차단 (`os.path.realpath` + `commonpath` 패턴 — F-15 계승), storage_key uuid 생성, content-type 점검, 20MB 상한 적용.

---

## 4. 데이터 바인딩 표

### 4.1 C1 — 사건 생성/수정 폼 바인딩

| UI 요소 | 요청 필드 | 타입 | 예시 | 비고 |
|---|---|---|---|---|
| 사건번호 입력 | `case_number` | `str` | `"2026가합99001"` | 수정 폼에서 readonly |
| 사건명 입력 | `title` | `str` | `"손해배상"` | |
| 사건유형 SELECT | `case_type` | `str \| null` | `"civil"` | civil/criminal/administrative/family/commercial/other |
| 사건상태 SELECT | `status` | `str` | `"intake"` | intake/active/trial/appeal/closed/withdrawn |
| 사건개요 textarea | `description` | `str \| null` | `"..."` | |
| 접수일 date input | `opened_at` | `str \| null` | `"2026-06-22"` | |

**status UI 매핑** (Phase B 계승): intake→접수중, active→진행중, trial→재판중, appeal→항소중, closed→종결, withdrawn→취하.

### 4.2 C2 — 당사자 폼 바인딩 (legal_case_party 실측 컬럼 1:1)

seed INSERT 컬럼 확인 결과: `(id, created_at, updated_at, case_id, role, name, contact_id, notes)`.  
05_case_party_rls.sql 확인 결과: 구조 컬럼 추가 없음 (RLS 전용 augment).

| UI 요소 | DB 컬럼 / 요청 필드 | 타입 | 예시 | 비고 |
|---|---|---|---|---|
| 역할 SELECT | `role` | `str` | `"plaintiff"` | CHECK: plaintiff/defendant/witness/opposing-counsel/expert-witness |
| 당사자명 입력 | `name` | `str` | `"주식회사 한빛테크"` | DB 컬럼명: `name` |
| 메모 textarea | `notes` | `str \| null` | `"원고 법인."` | DB 컬럼명: `notes` |
| (미노출) | `contact_id` | `uuid \| null` | `null` | v1 미노출, 서버 NULL 고정 |
| (서버 생성) | `id` | `uuid` | — | 서버 생성 |
| (서버 생성) | `case_id` | `uuid` | — | 경로 파라미터에서 서버 주입 |
| (서버 생성) | `created_at`, `updated_at` | `timestamp` | — | 서버 생성 |

**role UI 매핑**: plaintiff→원고, defendant→피고, witness→증인, opposing-counsel→상대방 대리인, expert-witness→전문가 증인.

### 4.3 C3 — 문서 업로드 폼 바인딩 (legal_case_document 컬럼 1:1)

| UI 요소 | DB 컬럼 / 요청 필드 | 타입 | 예시 | 비고 |
|---|---|---|---|---|
| 파일 선택 | (binary) | file | `complaint.pdf` | 서버가 storage_key 로 변환 |
| 문서유형 SELECT | `document_type` | `str` | `"brief"` | CHECK 동일 |
| 문서제목 입력 | `title` | `str \| null` | `"준비서면"` | 미입력 시 sanitized 파일명 |
| 제출일자 date | `filed_at` | `str \| null` | `"2026-06-01"` | |
| 메모 textarea | `notes` | `str \| null` | `"..."` | |
| (서버 생성) | `storage_key` | `str` | `legal/cases/<id>/<uuid>_complaint.pdf` | 서버 uuid 생성 |
| (서버 설정) | `ingest_status` | `str` | `"pending"` | INSERT 시 `pending` 고정 |
| (서버 설정) | `ingested_at` | `timestamp \| null` | `null` | ingest 완료 시 갱신 |
| (미기록) | `content_text` | `text \| null` | `null` | phase 2 (G-3) 보강 권고 — 현재 ingest.py 미기록 |
| (서버 생성) | `id`, `case_id` | `uuid` | — | 서버 생성/주입 |

**ingest_status 뱃지** (Phase B 계승, 의미 불변): pending·processing→대기중(노란 뱃지), done→색인완료(초록), error→실패(빨강), null→상태불명(회색).

---

## 5. 보존 계약 (불변식)

engineer 가 G-2 를 구현하는 동안 절대 깨지 않아야 하는 계약이다.

### 5.1 RLS — 격리 유지

모든 쓰기 요청에 `Authorization: Bearer <token>` 헤더를 전달한다. DB RLS 가 attorney 격리를 강제한다. 서버 API 는 `assigned_attorney_id` 를 JWT `sub` 에서 주입하며, 클라이언트가 제출한 값을 신뢰하지 않는다. `ingest_file` 호출은 반드시 `app_service`(BYPASSRLS) 커넥션을 사용한다 — `app_user` 커넥션으로 호출 시 RLS 오류 발생.

### 5.2 쓰기 API 는 middle contract 읽기전용 (open-closed)

신규 엔드포인트(`POST /cases`, `PATCH /cases/{id}`, 당사자·문서 엔드포인트)는 `middle/contract/` 를 변경하지 않는다. `contract.gen.ts` 에 경로 상수만 추가 확장한다. 기존 상수 (`auth_login`, `search`, `health`, `cases_list`, `case_detail`) 는 수정 금지.

### 5.3 기존 읽기화면·검색 무회귀

Phase B 가 구현한 `CasesScreen`, `CaseDetailScreen`, `PrecedentSearchScreen` 은 G-2 구현 중 수정하지 않는다. G-2 진입점(`[새 사건 등록]`, `[사건 수정]`, `[당사자 추가]`, `[문서 업로드]` 버튼)을 기존 화면에 추가하되, 기존 렌더 로직·API 호출·라우트는 건드리지 않는다.

### 5.4 ingest_status 뱃지 의미 보존

Phase B 에서 확립한 뱃지 매핑(pending·processing→대기중, done→색인완료, error→실패, null→상태불명)을 G-2 이후에도 변경하지 않는다. 새로 업로드된 문서의 ingest_status=pending 뱃지가 즉시 목록에 표시되어야 한다.

### 5.5 append-only 문서 (법적 감사)

`legal_case_document` 에는 `app_user` UPDATE/DELETE 정책이 없다 (DDL `04_case_document_augment.sql`). G-2 는 INSERT 엔드포인트만 추가하며, 문서 수정·삭제 UI 를 만들지 않는다.

### 5.6 비동기 ingest — app_service 커넥션 분리

`BackgroundTasks` 에 등록되는 `ingest_file` 함수는 반드시 `app_service` 역할 커넥션(BYPASSRLS)을 사용한다. 요청 핸들러의 `app_user` 커넥션을 BackgroundTask 에 전달하면 커넥션 해제 후 오류 발생 — 별도 커넥션 풀에서 획득할 것.

---

## 6. 구현 sub-phase 순서

의존도·리스크 순으로 독립 머지 가능하게 설계한다.

### C1 — 사건 메타 CRUD (최저 리스크)

**의존**: DDL ready (`02_legal_case_augment.sql`), 기존 `GET /cases` 패턴 참조 가능.  
**백엔드**: `POST /cases`, `PATCH /cases/{id}` 추가. Pydantic 모델 `CaseCreateIn`, `CaseUpdateIn` 신규.  
**프런트**: CasesScreen `[새 사건 등록]` 버튼 → CaseCreateScreen. CaseDetailScreen `[사건 수정]` 버튼 → CaseEditScreen.  
**QA 게이트**: AC-01 ~ AC-04.

### C2 — 당사자 CRUD (PII, C1 선결)

**의존**: C1 완료 (사건 존재 선결). `05_case_party_rls.sql` 완비.  
**백엔드**: `POST /cases/{id}/parties`, `PATCH /cases/{id}/parties/{party_id}`. 신규 모델 `CasePartyOut`.  
**프런트**: CaseDetailScreen 내 PartyPanel (인라인, 별도 라우트 없음).  
**QA 게이트**: AC-05 ~ AC-07 (PII 음성 포함).

### C3 — 문서 첨부 + 비동기 ingest (최고 리스크, C1 선결)

**의존**: C1 완료. `ingest.py::ingest_file` 라이브. Coolify 영속 볼륨 마운트 확인 필요 (devops).  
**백엔드**: `POST /cases/{id}/documents` (multipart). 신규 모델 `CaseDocumentUploadOut`. BackgroundTasks 통합. `LEGAL_STORAGE_ROOT` 환경변수 설정.  
**프런트**: CaseDetailScreen 내 DocumentUploadPanel. ingest_status 폴링(3~5초 재호출 또는 수동 새로고침).  
**CISO 게이트**: 머지 전 CISO 리뷰 필수.  
**QA 게이트**: AC-08 ~ AC-12.

---

## 7. 수용 기준 (Acceptance Criteria)

QA 게이트 통과 + 아래 전 항목 충족이 G-2 인도 조건.

### C1 — AC-01 ~ AC-04

#### AC-01 — L3 빌드 PASS

```
cd frontend/adapters/legal-pro && npm run build
cd services/legal-rag && python -m pytest -q
```

TypeScript 컴파일 에러 0건, pytest 전체 PASS. G-2 신규 코드 포함.

#### AC-02 — 사건 생성 성공 (RLS 양성)

담당 변호사 JWT 로 `POST /cases` 정상 필드 제출 → 201, `CaseOut` 반환, `case_id` UUID 형식 확인. 생성 직후 `GET /cases` 에 해당 사건 노출.

#### AC-03 — 사건 수정 성공

`PATCH /cases/{id}` 로 `title` 수정 → 200, 수정 값 반영된 `CaseDetailResponse` 반환. `case_number` 제출해도 응답에서 기존 값 유지 (수정 무시).

#### AC-04 — 사건 쓰기 RLS 음성 테스트 (타 변호사 사건 쓰기 거부)

변호사 B 토큰으로 변호사 A 전용 사건(A 담당, partner_id 없음)에 `PATCH /cases/{case_a_id}` 시도 → 404 (존재 은폐). `POST /cases` 로 생성 후 B 토큰으로 수정 시도 = 동일 거부.

---

### C2 — AC-05 ~ AC-07

#### AC-05 — 당사자 등록 성공 (RLS 양성)

담당 변호사 JWT 로 `POST /cases/{id}/parties` 에 role/name 제출 → 201, `CasePartyOut` 반환. `GET /cases/{id}` 응답(또는 별도 party 목록 엔드포인트)에 party 행 노출.

#### AC-06 — 당사자 수정 성공

`PATCH /cases/{id}/parties/{party_id}` 로 `name` 수정 → 200, 수정 값 반영. `contact_id` 제출해도 응답에서 null 유지.

#### AC-07 — 당사자 쓰기 RLS 음성 테스트

변호사 B 토큰으로 변호사 A 사건의 party 등록 시도(`POST /cases/{case_a_id}/parties`) → 404. party 수정 시도(`PATCH /cases/{case_a_id}/parties/{party_id}`) → 404.

---

### C3 — AC-08 ~ AC-12

#### AC-08 — 문서 업로드 성공 (비동기 ingest, RLS 양성)

담당 변호사 JWT 로 `.pdf` 파일 (< 20MB) 과 `document_type=brief` 를 `multipart/form-data` 로 `POST /cases/{id}/documents` 제출 → **즉시 201** 반환, `ingest_status=pending`. 이후 `GET /cases/{id}` 재호출 시 동일 doc_id 의 `ingest_status` 가 processing 또는 done 으로 갱신됨 (60초 이내).

#### AC-09 — 업로드 보안 거부 (CISO 게이트)

- `.exe`, `.sh`, `.jpg` 등 비허용 확장자 파일 업로드 → 400.
- 20MB 초과 파일 업로드 → 400 또는 413.
- `../../../etc/passwd` 형태의 파일명 제출 → storage_key 에 원본 경로 없음 (uuid 로만 생성됨) 확인.

#### AC-10 — 문서 업로드 RLS 음성 테스트

변호사 B 토큰으로 변호사 A 전용 사건에 `POST /cases/{case_a_id}/documents` 시도 → 404.

#### AC-11 — ingest_status 뱃지 폴링

업로드 후 CaseDetailScreen 의 해당 문서 행에 `ingest_status=pending` 뱃지(대기중)가 즉시 표시됨. 3~5초 후 자동 또는 수동 새로고침으로 done/error 뱃지로 갱신.

#### AC-12 — Coolify 영속 볼륨 마운트 (devops 사전 확인)

`LEGAL_STORAGE_ROOT` 가 Coolify 영속 볼륨에 마운트됨을 devops 가 확인하고 `docs/runbooks/legal-rag-install.md` 에 볼륨 마운트 항목 추가. 컨테이너 재시작 후 업로드 파일 보존 확인. C3 머지 선결 조건.

---

## 8. 열린 위험 & 후속

| # | 유형 | 내용 | owner | 영향 |
|---|---|---|---|---|
| OQ-5 | 설계 결정 | `case_number` 가 수정 가능해야 하는지 여부 (접수번호가 법원 공문 후 변경되는 사례 존재). v1 은 readonly 로 설계하되, 필요 시 별도 `PATCH /cases/{id}/case-number` 엔드포인트 추가 | CTO | PATCH 요청 바디 처리 |
| OQ-6 | 범위 | `contact_id` (당사자 연락처 엔티티 FK) 를 v1 에서 노출할지 여부. 현재 NULL 고정. 노출 시 contact 엔티티 별도 CRUD 필요 | CTO | C2 바인딩 확장 |
| OQ-7 | devops | Coolify 영속 볼륨 마운트 path 및 백업 정책 확인 (AC-12 선결) | DevOps | C3 배포 가능 여부 |
| OQ-8 | CISO | 업로드 파일 mime/size 컬럼 (`legal_case_document` 에 추가 여부). 감사 이력용. 현재 DDL 없음. 필요 시 DBA augment 의뢰 | CISO | C3 DDL 변경 여부 |
| OQ-9 | 인프라 | BackgroundTasks 비동기 ingest 중 컨테이너 재시작 시 pending 상태 잔류 처리. ingest 재시작 훅(startup 에서 pending 재처리) 필요 여부 | CTO | 운영 안정성 |
| OQ-10 | phase 2 | `content_text` 컬럼 보강 — ingest.py 에서 현재 미기록. G-3 원문 보기 대비 이 값이 필요. ingest.py 수정은 G-3 스펙에서 처리 | CTO | G-3 의존 |
| OQ-11 | phase 2 | `GET /cases/{id}/parties` 읽기 전용 엔드포인트 — Phase B 에서 party 목록이 CaseDetailResponse 에 없음. C2 구현 시 CaseDetailResponse 확장 또는 별도 엔드포인트 추가 결정 필요 | CTO | C2 응답 계약 |
