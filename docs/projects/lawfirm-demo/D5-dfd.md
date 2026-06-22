---
document: D5
title: DFD — 법무법인 통합 업무관리 (lawfirm-demo)
owner: DBA / QA
status: DRAFT v0.1 (2026-06-23) — QA 게이트 미통과
generated: 2026-06-23
source_erd: docs/projects/lawfirm-demo/D4-erd.md
source_spec: docs/projects/lawfirm-demo/D1-functional-spec.md
source_flow: docs/projects/lawfirm-demo/D2-user-flow.md
---

# D5 DFD — 법무법인 통합 업무관리 (lawfirm-demo)

> `docs/projects/lawfirm-demo/` D5 슬롯 산출물.
> QA "데이터가 프로세스에 따라 올바르게 흐르는가" 검증의 기준 문서.
> D1 기능명세서 모듈 A~F 및 D2 시나리오 1~4와 1:1 대응한다.
> 가명 데이터 — 실존 인물·법인·사건과 무관.

---

## 1. Context Diagram (Level 0)

외부 엔티티, 시스템 경계, 데이터스토어 간 최상위 데이터 흐름.

```mermaid
flowchart TD
    %% ── 외부 엔티티 ────────────────────────────────────────────────────────
    CEO["CEO / 대표변호사\n(경영·감독)"]
    WORKER["업무담당자\n(어소시에이트·사무장)"]
    IT["IT담당자\n(운영·보안)"]
    LEGALAPP["killer-app\n(legal-pro, legal-rag.n9n.co.kr/pro)\n별개 앱·별개 DB·별개 로그인"]

    %% ── 시스템 경계 ─────────────────────────────────────────────────────────
    subgraph SYS["lawfirm-demo 시스템 (self-host, 사내망)"]
        FRONTEND["vanilla-htmx 프런트\n(FastAPI 서버사이드 렌더링)"]
        BACKEND["FastAPI 백엔드\n(REST API)"]
    end

    %% ── 데이터스토어 ────────────────────────────────────────────────────────
    DS_SESSION[("DS-S\n세션 스토어\n(서버 메모리/쿠키)")]
    DS_HR[("DS-1\nhr_department\nhr_employee")]
    DS_LEGAL[("DS-2\nlegal_case\nlegal_precedent\nlegal_case_party\nlegal_case_document")]
    DS_DOC[("DS-3\ndocument_document\ndocument_version\ndocument_category\ndocument_access_rule")]
    DS_APPROVAL[("DS-4\napproval_request\napproval_step\napproval_approver\napproval_decision")]

    %% ── 입력 흐름 ───────────────────────────────────────────────────────────
    CEO    -- "사건·결재 조회 요청" --> FRONTEND
    WORKER -- "사건·당사자·문서·결재 CRUD\n판례 키워드 검색" --> FRONTEND
    IT     -- "직원·부서·접근규칙 관리\n헬스체크" --> FRONTEND

    %% ── 출력 흐름 ───────────────────────────────────────────────────────────
    FRONTEND -- "HTML 페이지 (서버사이드 렌더)" --> CEO
    FRONTEND -- "HTML 페이지 (서버사이드 렌더)" --> WORKER
    FRONTEND -- "HTML 페이지 (서버사이드 렌더)" --> IT

    %% ── killer-app 경계 (단방향 진입 링크만) ───────────────────────────────
    WORKER -- "배너 클릭 (target=_blank)\n데이터 전달 없음" --> LEGALAPP
    CEO    -- "배너 클릭 (target=_blank)\n데이터 전달 없음" --> LEGALAPP

    %% ── 시스템 ↔ 데이터스토어 ──────────────────────────────────────────────
    BACKEND -- "R/W" --> DS_SESSION
    BACKEND -- "R/W" --> DS_HR
    BACKEND -- "R/W" --> DS_LEGAL
    BACKEND -- "R/W" --> DS_DOC
    BACKEND -- "R/W" --> DS_APPROVAL
```

**시스템 경계 원칙**

| 항목 | lawfirm-demo | legal-pro (killer-app) |
|---|---|---|
| 배포 서버 | 사내망 self-host | 별개 서버 (legal-rag.n9n.co.kr) |
| DB | 별개 PostgreSQL (lawfirm_demo) | 별개 PostgreSQL (legal_rag) |
| 인증 | 세션 쿠키 (demo/demo) | JWT 변호사 계정 |
| 데이터 공유 | 없음 | 없음 |
| 연결 방식 | 진입 링크 target=_blank (새 탭) | — |

---

## 2. Level 1 DFD — P1: 인증·세션 관리

**대응 기능**: D1 §3 모듈 A (A-01~A-04), D2 §2 공통 진입 플로우

```mermaid
flowchart TD
    USER["모든 페르소나\n(브라우저)"]
    DS_SESSION[("DS-S\n세션 스토어")]

    subgraph P1_AUTH["P1: 인증·세션 관리"]
        P1_1["P1.1\n로그인 폼 렌더\nGET /login"]
        P1_2["P1.2\n자격증명 검증\nPOST /login\n(username/password 대조)"]
        P1_3["P1.3\n세션 토큰 발급\n(SESSION_KEY 서명)"]
        P1_4["P1.4\n인증 게이트 미들웨어\n(모든 보호 라우트 전처리)"]
        P1_5["P1.5\n홈 화면 렌더\nGET /home\n(도메인 카드 4종\n+ killer-app 배너)"]
        P1_6["P1.6\n로그아웃\nPOST /logout\n(세션 폐기)"]
    end

    USER -- "GET /login" --> P1_1
    P1_1 -- "로그인 폼 HTML" --> USER

    USER -- "username, password\nPOST /login" --> P1_2
    P1_2 -- "인증 실패: 401 + 한국어 오류\n(폼 재렌더)" --> USER
    P1_2 -- "인증 성공: username" --> P1_3
    P1_3 -- "세션 토큰 SET-COOKIE" --> USER
    P1_3 -- "세션 저장\n(user=username, ts=now)" --> DS_SESSION

    USER -- "보호 라우트 접근\n(세션 쿠키 포함)" --> P1_4
    DS_SESSION -- "세션 조회 (유효/만료)" --> P1_4
    P1_4 -- "미인증/만료: 302 /login" --> USER
    P1_4 -- "인증됨: username 통과" --> P1_5
    P1_5 -- "홈 화면 HTML\n(KILLER_APP_URL 있으면 배너 표시)" --> USER

    USER -- "POST /logout" --> P1_6
    P1_6 -- "세션 삭제" --> DS_SESSION
    P1_6 -- "302 /login" --> USER
```

**데이터 항목**

| 흐름 | 데이터 | 형식 |
|---|---|---|
| USER → P1.2 | username, password | HTTP POST form |
| P1.3 → DS-S | 세션 키=값 (username, timestamp) | 서버 메모리 또는 암호화 쿠키 |
| P1.4 → DS-S | 세션 조회 (쿠키 token) | 키 조회 |
| DS-S → P1.4 | 세션 유효 여부 + username | Bool + str |

---

## 3. Level 1 DFD — P2: 사건 관리 (legal_case)

**대응 기능**: D1 §3 모듈 B-1 (B-01~B-04), D2 §3 시나리오 1 (사건 등록 단계)

```mermaid
flowchart TD
    WORKER["업무담당자"]
    DS_LEGAL[("DS-2\nlegal_case")]
    DS_HR[("DS-1\nhr_employee")]

    subgraph P2_CASE["P2: 사건 관리"]
        P2_1["P2.1\n사건 목록 조회\nGET /entities/legal-case\n(오프셋 페이징, 정렬, 검색)"]
        P2_2["P2.2\n사건 등록\nGET/POST /entities/legal-case/new\n(필수: case_number, title,\n case_type, filed_date)"]
        P2_3["P2.3\n사건 상세·수정\nGET /entities/legal-case/<id>\nPOST /entities/legal-case/<id>/edit"]
        P2_4["P2.4\n사건 삭제 확인\nGET/POST /entities/legal-case/<id>/delete\n(2단계 확인)"]
    end

    WORKER -- "GET + 쿼리파라미터\n(page, sort, q)" --> P2_1
    P2_1 -- "SELECT legal_case (페이징)" --> DS_LEGAL
    DS_LEGAL -- "사건 목록 rows" --> P2_1
    P2_1 -- "사건 목록 HTML" --> WORKER

    WORKER -- "사건 데이터\n{case_number, title, case_type,\n status, filed_date, court,\n next_hearing_date,\n assigned_attorney_id, summary}" --> P2_2
    P2_2 -- "SELECT hr_employee WHERE id=assigned_attorney_id\n(FK 유효성 검증)" --> DS_HR
    DS_HR -- "직원 행 존재 여부" --> P2_2
    P2_2 -- "INSERT legal_case" --> DS_LEGAL
    DS_LEGAL -- "신규 id" --> P2_2
    P2_2 -- "302 /entities/legal-case/<new_id>" --> WORKER

    WORKER -- "수정 데이터" --> P2_3
    P2_3 -- "SELECT / UPDATE legal_case WHERE id=<id>" --> DS_LEGAL
    DS_LEGAL -- "사건 row / 업데이트 결과" --> P2_3
    P2_3 -- "상세 HTML / 수정 완료 리디렉션" --> WORKER

    WORKER -- "삭제 확인 POST" --> P2_4
    P2_4 -- "DELETE legal_case WHERE id=<id>\n→ CASCADE: legal_case_party, legal_case_document 함께 삭제" --> DS_LEGAL
    P2_4 -- "delete_success.html" --> WORKER
```

---

## 4. Level 1 DFD — P3: 판례 관리 (legal_precedent)

**대응 기능**: D1 §3 모듈 B-2 (B-05~B-09)

```mermaid
flowchart TD
    WORKER["업무담당자"]
    DS_LEGAL[("DS-2\nlegal_precedent")]

    subgraph P3_PREC["P3: 판례 관리·검색"]
        P3_1["P3.1\n판례 목록 조회\nGET /entities/legal-precedent"]
        P3_2["P3.2\n판례 등록·수정·삭제\n(CRUD — 기본 패턴)"]
        P3_3["P3.3\n판례 키워드 검색\nGET /legal/search\n(FTS: plainto_tsquery 또는 ILIKE\nidx_precedent_fts GIN 활용)"]
    end

    WORKER -- "GET /entities/legal-precedent" --> P3_1
    P3_1 -- "SELECT legal_precedent" --> DS_LEGAL
    DS_LEGAL -- "판례 목록" --> P3_1
    P3_1 -- "판례 목록 HTML" --> WORKER

    WORKER -- "CRUD 요청" --> P3_2
    P3_2 -- "INSERT/UPDATE/DELETE legal_precedent" --> DS_LEGAL

    WORKER -- "검색어\nGET /legal/search?q=<keyword>" --> P3_3
    P3_3 -- "SELECT WHERE fts_vector @@ plainto_tsquery\n또는 holding ILIKE '%q%'" --> DS_LEGAL
    DS_LEGAL -- "판례 결과 목록" --> P3_3
    P3_3 -- "판례 검색 결과 HTML\n(killer-app과 다른 간이 검색)" --> WORKER
```

**주의**: `/legal/search` 는 lawfirm-demo 자체의 간이 키워드 검색(FTS)이다. legal-pro의 RAG 하이브리드 검색(ANN+FTS+RRF)과 다른 별개 기능이다.

---

## 5. Level 1 DFD — P4: 당사자 관리 (legal_case_party)

**대응 기능**: D1 §3 모듈 B-3 (B-10~B-13), D2 §3 시나리오 1 (당사자 추가 단계)

```mermaid
flowchart TD
    WORKER["업무담당자"]
    DS_LEGAL[("DS-2\nlegal_case\nlegal_case_party")]

    subgraph P4_PARTY["P4: 당사자 관리"]
        P4_1["P4.1\n당사자 목록 조회\nGET /entities/legal-case-party\n(전체 목록, case_id 필터 미지원)"]
        P4_2["P4.2\n당사자 등록\nPOST /entities/legal-case-party/new\n(필수: case_id, role, name)"]
        P4_3["P4.3\n당사자 상세·수정·삭제\n(CRUD 기본 패턴)"]
    end

    WORKER -- "GET 목록" --> P4_1
    P4_1 -- "SELECT legal_case_party" --> DS_LEGAL
    DS_LEGAL -- "당사자 목록" --> P4_1
    P4_1 -- "목록 HTML" --> WORKER

    WORKER -- "{case_id, role, name, notes}\nPOST" --> P4_2
    P4_2 -- "SELECT legal_case WHERE id=case_id\n(FK 유효성 검증)" --> DS_LEGAL
    DS_LEGAL -- "사건 행 존재 여부" --> P4_2
    P4_2 -- "INSERT legal_case_party\n(case_id FK → legal_case)" --> DS_LEGAL
    DS_LEGAL -- "신규 id" --> P4_2
    P4_2 -- "302 /entities/legal-case-party/<new_id>" --> WORKER

    WORKER -- "CRUD 요청" --> P4_3
    P4_3 -- "UPDATE/DELETE legal_case_party WHERE id=<id>" --> DS_LEGAL
```

---

## 6. Level 1 DFD — P5: 사건문서 관리 (legal_case_document)

**대응 기능**: D1 §3 모듈 B-4 (B-14~B-17), D2 §3 시나리오 1 (문서 첨부 단계)

```mermaid
flowchart TD
    WORKER["업무담당자"]
    DS_LEGAL[("DS-2\nlegal_case\nlegal_case_document")]

    subgraph P5_CDOC["P5: 사건문서 관리"]
        P5_1["P5.1\n사건문서 목록 조회\nGET /entities/legal-case-document\n(ingest_status 표시)"]
        P5_2["P5.2\n사건문서 등록\nPOST /entities/legal-case-document/new\n(필수: case_id, document_type, title)"]
        P5_3["P5.3\n사건문서 상세·수정·삭제\n(CRUD 기본 패턴)"]
    end

    WORKER -- "GET 목록" --> P5_1
    P5_1 -- "SELECT legal_case_document\n(ingest_status 포함)" --> DS_LEGAL
    DS_LEGAL -- "사건문서 목록" --> P5_1
    P5_1 -- "목록 HTML (색인 상태 표시)" --> WORKER

    WORKER -- "{case_id, document_type, title,\n filed_at, storage_key, notes}\nPOST" --> P5_2
    P5_2 -- "SELECT legal_case WHERE id=case_id\n(FK 유효성 검증)" --> DS_LEGAL
    DS_LEGAL -- "사건 행 존재 여부" --> P5_2
    P5_2 -- "INSERT legal_case_document\n(ingest_status='pending' 초기값\n case_id FK → legal_case)" --> DS_LEGAL
    DS_LEGAL -- "신규 id (ingest_status=pending)" --> P5_2
    P5_2 -- "302 /entities/legal-case-document/<new_id>" --> WORKER

    WORKER -- "CRUD 요청" --> P5_3
    P5_3 -- "UPDATE/DELETE legal_case_document WHERE id=<id>" --> DS_LEGAL
```

**흐름 메모**: 사건문서 등록 시 `ingest_status`는 항상 'pending'으로 초기화된다. 실제 텍스트 추출 및 색인은 외부 파이프라인(setup_lawfirm.py 또는 별도 ingest 프로세스)이 담당하며 lawfirm-demo UI의 범위 밖이다. 색인 완료 후 status가 'done'으로 갱신된다.

---

## 7. Level 1 DFD — P6: 인사 관리 (hr)

**대응 기능**: D1 §3 모듈 C (C-01~C-08)

```mermaid
flowchart TD
    IT["IT담당자"]
    CEO["CEO"]
    DS_HR[("DS-1\nhr_department\nhr_employee")]

    subgraph P6_HR["P6: 인사 관리"]
        P6_1["P6.1\n부서 CRUD\nGET/POST /entities/hr-department"]
        P6_2["P6.2\n직원 CRUD\nGET/POST /entities/hr-employee"]
    end

    IT -- "부서 등록·수정\n{code, name, parent_id, manager_id}" --> P6_1
    P6_1 -- "SELECT/INSERT/UPDATE/DELETE\nhr_department" --> DS_HR
    DS_HR -- "부서 rows" --> P6_1
    P6_1 -- "부서 목록·상세 HTML" --> IT

    IT -- "직원 등록·수정\n{employee_number, full_name,\n department_id, hire_date, status}" --> P6_2
    CEO -- "직원 조회" --> P6_2
    P6_2 -- "SELECT hr_department WHERE id=department_id\n(FK 유효성)" --> DS_HR
    DS_HR -- "부서 존재 여부" --> P6_2
    P6_2 -- "SELECT/INSERT/UPDATE/DELETE\nhr_employee" --> DS_HR
    DS_HR -- "직원 rows" --> P6_2
    P6_2 -- "직원 목록·상세 HTML" --> IT
    P6_2 -- "직원 목록·상세 HTML" --> CEO
```

---

## 8. Level 1 DFD — P7: 문서관리 (document)

**대응 기능**: D1 §3 모듈 D (D-01~D-16), D2 §6 시나리오 4

```mermaid
flowchart TD
    WORKER["업무담당자"]
    IT["IT담당자"]
    DS_DOC[("DS-3\ndocument_category\ndocument_document\ndocument_version\ndocument_access_rule")]
    DS_HR[("DS-1\nhr_employee\nhr_department")]

    subgraph P7_DOC["P7: 문서관리"]
        P7_1["P7.1\n카테고리 CRUD\nGET/POST /entities/document-category"]
        P7_2["P7.2\n문서 CRUD\nGET/POST /entities/document-document\n(current_version_id는 버전 등록 후 갱신)"]
        P7_3["P7.3\n버전 등록\nGET/POST /entities/document-version/new\n(document_id, version_number, 파일 정보)"]
        P7_4["P7.4\n접근규칙 관리\nGET/POST /entities/document-access-rule\n(principal_type: department/employee)"]
    end

    IT -- "카테고리 등록·수정" --> P7_1
    P7_1 -- "INSERT/UPDATE/DELETE document_category" --> DS_DOC
    DS_DOC -- "카테고리 rows" --> P7_1
    P7_1 -- "카테고리 목록 HTML" --> IT

    WORKER -- "문서 등록\n{title, category_id, owner_id, status}" --> P7_2
    P7_2 -- "SELECT document_category WHERE id=category_id" --> DS_DOC
    P7_2 -- "SELECT hr_employee WHERE id=owner_id" --> DS_HR
    DS_DOC -- "카테고리 존재" --> P7_2
    DS_HR -- "직원 존재" --> P7_2
    P7_2 -- "INSERT document_document\n(current_version_id=NULL 초기)" --> DS_DOC
    DS_DOC -- "신규 document_id" --> P7_2
    P7_2 -- "302 /entities/document-document/<id>" --> WORKER

    WORKER -- "버전 등록\n{document_id, version_number,\n file_name, file_size_bytes,\n mime_type, storage_key, checksum}" --> P7_3
    P7_3 -- "SELECT document_document WHERE id=document_id" --> DS_DOC
    DS_DOC -- "문서 존재" --> P7_3
    P7_3 -- "INSERT document_version" --> DS_DOC
    P7_3 -- "UPDATE document_document\nSET current_version_id=<new_ver_id>\nWHERE current_version_id IS NULL\n또는 is_published=True인 경우" --> DS_DOC
    DS_DOC -- "버전 id" --> P7_3
    P7_3 -- "302 /entities/document-version/<id>" --> WORKER

    IT -- "접근규칙 등록\n{document_id, principal_type,\n principal_id, permission, expires_at}" --> P7_4
    P7_4 -- "SELECT document_document WHERE id=document_id" --> DS_DOC
    DS_DOC -- "문서 존재" --> P7_4
    P7_4 -- "(다형 검증 — 앱 레이어)\nprincipal_type=department →\n  SELECT hr_department WHERE id=principal_id\nprincipal_type=employee →\n  SELECT hr_employee WHERE id=principal_id" --> DS_HR
    DS_HR -- "주체 존재 여부" --> P7_4
    P7_4 -- "INSERT document_access_rule\n(UNIQUE 위반 시 오류)" --> DS_DOC
    DS_DOC -- "신규 접근규칙 id" --> P7_4
    P7_4 -- "302 /entities/document-access-rule/<id>" --> IT
```

---

## 9. Level 1 DFD — P8: 전자결재 (approval)

**대응 기능**: D1 §3 모듈 E (E-01~E-16), D2 §5 시나리오 3 (결재 상신→승인)

```mermaid
flowchart TD
    WORKER["업무담당자"]
    CEO["CEO"]
    DS_APPROVAL[("DS-4\napproval_request\napproval_step\napproval_approver\napproval_decision")]
    DS_HR[("DS-1\nhr_employee")]

    subgraph P8_APPROVAL["P8: 전자결재"]
        P8_1["P8.1\n결재요청 목록 조회\nGET /entities/approval-request\n(상태별 필터 지원)"]
        P8_2["P8.2\n결재요청 등록 (상신)\nPOST /entities/approval-request/new\n{title, subject_type, subject_id,\n requester_id, expires_at}"]
        P8_3["P8.3\n결재단계 등록\nPOST /entities/approval-step/new\n{request_id, sequence, name,\n requires_all}"]
        P8_4["P8.4\n결재자 지정\nPOST /entities/approval-approver/new\n{step_id, employee_id}"]
        P8_5["P8.5\n결재결정 기록\nPOST /entities/approval-decision/new\n{step_id, approver_id,\n decision, comment}"]
        P8_6["P8.6\n상태 수정 (수동)\nPOST /entities/approval-*/edit\n(step.status, request.status)"]
    end

    WORKER -- "GET 목록" --> P8_1
    P8_1 -- "SELECT approval_request\n(페이징, 상태 필터)" --> DS_APPROVAL
    DS_APPROVAL -- "결재요청 목록" --> P8_1
    P8_1 -- "목록 HTML" --> WORKER
    P8_1 -- "목록 HTML" --> CEO

    WORKER -- "{title, subject_type, subject_id,\n requester_id}" --> P8_2
    P8_2 -- "SELECT hr_employee WHERE id=requester_id" --> DS_HR
    DS_HR -- "직원 존재" --> P8_2
    P8_2 -- "INSERT approval_request\n(status='pending' 초기값)" --> DS_APPROVAL
    DS_APPROVAL -- "신규 request_id" --> P8_2
    P8_2 -- "302 /entities/approval-request/<id>" --> WORKER

    WORKER -- "{request_id, sequence,\n name, requires_all}" --> P8_3
    P8_3 -- "SELECT approval_request WHERE id=request_id" --> DS_APPROVAL
    DS_APPROVAL -- "요청 존재" --> P8_3
    P8_3 -- "INSERT approval_step\n(UNIQUE: request_id+sequence)" --> DS_APPROVAL
    DS_APPROVAL -- "신규 step_id" --> P8_3

    WORKER -- "{step_id, employee_id}" --> P8_4
    P8_4 -- "SELECT approval_step WHERE id=step_id" --> DS_APPROVAL
    P8_4 -- "SELECT hr_employee WHERE id=employee_id" --> DS_HR
    DS_APPROVAL -- "단계 존재" --> P8_4
    DS_HR -- "직원 존재" --> P8_4
    P8_4 -- "INSERT approval_approver\n(UNIQUE: step_id+employee_id)" --> DS_APPROVAL
    DS_APPROVAL -- "신규 approver_id" --> P8_4

    WORKER -- "{step_id, approver_id,\n decision, comment, decided_at}" --> P8_5
    CEO -- "결재결정 등록" --> P8_5
    P8_5 -- "SELECT approval_approver WHERE id=approver_id" --> DS_APPROVAL
    P8_5 -- "SELECT approval_step WHERE id=step_id" --> DS_APPROVAL
    DS_APPROVAL -- "결재자·단계 존재" --> P8_5
    P8_5 -- "INSERT approval_decision\n(UNIQUE: step_id+approver_id)\ndecision: approved|rejected" --> DS_APPROVAL
    DS_APPROVAL -- "신규 decision_id" --> P8_5

    WORKER -- "상태 수정 (step.status, request.status)" --> P8_6
    P8_6 -- "UPDATE approval_step SET status=<s>\nUPDATE approval_request SET status=<s>" --> DS_APPROVAL
    DS_APPROVAL -- "업데이트 결과" --> P8_6
    P8_6 -- "수정 완료 HTML" --> WORKER
```

**결재 상태 전이 규칙** (앱 레이어 적용):

| 전이 | 조건 | 다음 상태 |
|---|---|---|
| approval_request: pending → in-progress | 1단계 승인 완료 | in-progress |
| approval_request: in-progress → approved | 마지막 단계 승인 완료 | approved |
| approval_request: in-progress → rejected | 임의 단계 반려 결정 | rejected |
| approval_step: pending → active | 이전 단계 완료 또는 첫 단계 | active |
| approval_step: active → approved | decision=approved (requires_all=true면 전원 승인) | approved |
| approval_step: active → rejected | decision=rejected 1건이라도 | rejected |

**현재 구현 한계**: 상태 전이는 업무담당자가 `approval-step` 및 `approval-request` 를 수동으로 수정하는 방식이다. 자동 전이 트리거(DB trigger 또는 백엔드 로직)는 미구현. Q-1(결재자 전용 처리 화면) 확정 후 자동화 여부 결정.

---

## 10. Level 2 상세 — 사건 등록 → 당사자 → 문서 흐름 (D2 시나리오 1)

**트리거**: 업무담당자가 신규 수임 사건을 시스템에 등록하고 당사자·문서를 연결.
**시드 기준**: C5 "업무상 횡령 고소 대응 사건" 등록 흐름.

```mermaid
flowchart TD
    WORKER["이수진 (EMP002, 업무담당자)"]
    DS_CASE[("legal_case")]
    DS_PARTY[("legal_case_party")]
    DS_CDOC[("legal_case_document")]
    DS_HR[("hr_employee")]

    A["P2.2 사건 등록 POST\n{case_number: CASE-2024-005,\n title: 업무상 횡령 고소 대응 사건,\n case_type: criminal,\n assigned_attorney_id: EMP010 임도현}"]
    B{"SELECT hr_employee\nWHERE id=EMP010"}
    C["INSERT legal_case\n(status=active, filed_date=2024-04-22)\n→ C5_id 발급"]
    D["P4.2 당사자 등록 (반복 3회)\n원고: 주식회사 미래테크 (plaintiff)\n피고: 유창호 (defendant)\n감정인: 공인회계사 나인규 (expert-witness)"]
    E{"SELECT legal_case\nWHERE id=C5_id"}
    F["INSERT legal_case_party\n(case_id=C5_id, role, name)\n× 3건"]
    G["P5.2 사건문서 등록\n{case_id: C5_id,\n document_type: evidence,\n title: 회계감정 보고서,\n storage_key: cases/c5/evidence_001.pdf}"]
    H["INSERT legal_case_document\n(case_id=C5_id,\n ingest_status=pending)"]

    WORKER --> A
    A --> B
    B --> DS_HR
    DS_HR -- "EMP010 존재 확인" --> B
    B -- "FK 유효" --> C
    C --> DS_CASE
    DS_CASE -- "C5_id" --> C
    C --> WORKER

    WORKER --> D
    D --> E
    E --> DS_CASE
    DS_CASE -- "C5_id 존재" --> E
    E -- "FK 유효" --> F
    F --> DS_PARTY
    DS_PARTY -- "당사자 3건 생성" --> F
    F --> WORKER

    WORKER --> G
    G --> E
    E -- "FK 유효" --> H
    H --> DS_CDOC
    DS_CDOC -- "문서 id (ingest_status=pending)" --> H
    H --> WORKER
```

**무결성 체크포인트**:
1. `assigned_attorney_id` → `hr_employee` FK ON DELETE RESTRICT — 직원 삭제 시 사건이 있으면 차단
2. `case_id` → `legal_case` FK ON DELETE CASCADE — 사건 삭제 시 당사자·사건문서 함께 삭제
3. `ingest_status` 초기값 = 'pending' — 등록 즉시 색인 대기 상태

---

## 11. Level 2 상세 — 결재 다단계 승인 흐름 (D2 시나리오 3)

**트리거**: 강민서(EMP007)가 AQ5 "SaaS 계약서 외부 발송 승인" 상신.
**시드 기준**: AQ5 1단계 완료(강민서 승인), 2단계 대기(김대호 미응답) 상태.

```mermaid
flowchart TD
    E7["강민서 (EMP007, 기업자문팀)"]
    EMP1["김대호 (EMP001, 대표변호사)"]
    DS_APPROVAL[("approval_request\napproval_step\napproval_approver\napproval_decision")]
    DS_HR[("hr_employee")]

    A1["P8.2 결재요청 등록\n{title: SaaS 계약서 의뢰인 외부 발송 승인,\n subject_type: dispatch,\n subject_id: <cdid(12)>,\n requester_id: E7}"]
    A2["INSERT approval_request\n(status=pending)"]
    B1["P8.3 결재단계 등록 × 2\nstep1: {sequence:1, 담당파트너 승인}\nstep2: {sequence:2, 대표변호사 최종승인}"]
    B2["INSERT approval_step × 2\n(UNIQUE: request_id+sequence)"]
    C1["P8.4 결재자 지정 × 2\nstep1 → E7 (강민서)\nstep2 → EMP1 (김대호)"]
    C2["INSERT approval_approver × 2\n(UNIQUE: step_id+employee_id)"]
    D1["P8.5 1단계 결재결정 기록\n{step_id: step1, approver_id: aa(step1,E7),\n decision: approved, comment: 1차 승인.}"]
    D2["INSERT approval_decision\n(step_id=step1, decision=approved)\nUPDATE approval_step SET status=approved\nUPDATE approval_request SET status=in-progress"]
    E1["2단계 대기 (현재 상태)\n김대호 응답 대기\napproval_approver.responded_at = NULL"]
    E2["(향후) P8.5 2단계 결재결정\n{decision: approved} → 최종 완료\nUPDATE approval_step step2 → approved\nUPDATE approval_request → approved"]

    E7 --> A1
    A1 -- "SELECT hr_employee WHERE id=E7" --> DS_HR
    DS_HR -- "E7 존재" --> A1
    A1 --> A2
    A2 --> DS_APPROVAL

    E7 --> B1
    B1 --> B2
    B2 --> DS_APPROVAL

    E7 --> C1
    C1 -- "SELECT hr_employee WHERE id=E7,EMP1" --> DS_HR
    DS_HR -- "두 직원 존재" --> C1
    C1 --> C2
    C2 --> DS_APPROVAL

    E7 --> D1
    D1 --> D2
    D2 --> DS_APPROVAL
    DS_APPROVAL -- "승인 완료 기록" --> D2
    D2 --> E1

    EMP1 -.->|"향후 응답"| E2
    E2 --> DS_APPROVAL
```

**상태 전이 검증 포인트**:
- AQ5 시드: `status=in-progress`, step1 `status=approved`, step2 `status=active`
- step2의 `approval_approver.notified_at` = 2026-06-21, `responded_at` = NULL (미응답)
- 최종 승인 시: step2 → approved, request → approved

---

## 12. killer-app 크로스앱 데이터 경계 (D2 §9)

```mermaid
flowchart LR
    subgraph LFD["lawfirm-demo (사내망)"]
        DB_LFD[("PostgreSQL\nlawfirm_demo\n14테이블")]
        UI_LFD["vanilla-htmx\n프런트"]
    end

    subgraph BORDER["데이터 경계\n(SSO 없음·데이터 공유 없음)"]
        LINK["배너 링크 클릭\ntarget=_blank\n(URL만 전달)"]
    end

    subgraph LEGAL_PRO["legal-pro (별개 서버)"]
        DB_LP[("PostgreSQL\nlegal_rag\n7엔티티")]
        UI_LP["React SPA\n/pro"]
    end

    UI_LFD --> LINK
    LINK --> UI_LP
    DB_LFD -.->|"공유 없음"| DB_LP
    UI_LFD -.->|"세션 전달 없음"| UI_LP
```

**정직 표기**:
- lawfirm-demo 와 legal-pro 는 **완전히 독립적인 데이터스토어**를 가진다.
- 배너 클릭은 URL 이동만 발생한다. 세션 토큰·사건 데이터·사용자 정보는 전달되지 않는다.
- legal-pro 접속 후 변호사 계정으로 별도 로그인이 필요하다.
- 이 경계를 넘는 데이터 흐름은 현재 인도 범위 내에 존재하지 않는다.

---

## 13. 프로세스 목록 (P1~P8)

| 번호 | 프로세스 | D1 기능 | D2 시나리오 | 주 데이터스토어 | 핵심 변환 |
|---|---|---|---|---|---|
| P1 | 인증·세션 관리 | A-01~A-04 | 공통 진입 | DS-S (세션) | 자격증명 검증 → 세션 토큰 발급/폐기 |
| P2 | 사건 관리 | B-01~B-04 | 시나리오 1, 2 | DS-2 (legal_case) | 사건 CRUD, FK 유효성(assigned_attorney_id) |
| P3 | 판례 관리·검색 | B-05~B-09 | (법무 검색) | DS-2 (legal_precedent) | 판례 CRUD + FTS 검색 |
| P4 | 당사자 관리 | B-10~B-13 | 시나리오 1 | DS-2 (legal_case_party) | 당사자 CRUD, case_id FK 검증 |
| P5 | 사건문서 관리 | B-14~B-17 | 시나리오 1 | DS-2 (legal_case_document) | 문서 CRUD, ingest_status 초기화 |
| P6 | 인사 관리 | C-01~C-08 | 시나리오 4 | DS-1 (hr_*) | 직원·부서 CRUD, department_id FK |
| P7 | 문서관리 | D-01~D-16 | 시나리오 4 | DS-3 (document_*) | 문서·버전·접근규칙 CRUD, 다형 principal 검증 |
| P8 | 전자결재 | E-01~E-16 | 시나리오 3 | DS-4 (approval_*) | 결재 상신→단계→결재자→결정, 상태 전이 |

---

## 14. DFD 검증 포인트 (QA 체크 기준)

> 이 목록이 QA의 "데이터가 프로세스에 따라 올바르게 흐르는가" 검증 입력이다.
> 각 포인트는 테스트 케이스 1건에 대응한다.

### P1 — 인증

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P1-01 | 잘못된 password POST /login | HTTP 401 + 한국어 오류 메시지 (폼 재렌더) |
| VP-P1-02 | 세션 쿠키 없이 보호 라우트 접근 | 302 /login 리디렉션 |
| VP-P1-03 | 만료된 세션으로 보호 라우트 접근 | 302 /login 리디렉션 |
| VP-P1-04 | POST /logout 후 세션 쿠키로 재접근 | 302 /login (세션 폐기 확인) |
| VP-P1-05 | 로그인 성공 후 홈 화면 렌더 | 도메인 카드 4종 표시. KILLER_APP_URL 설정 시 배너 표시 |

### P2 — 사건 관리

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P2-01 | 사건 등록 시 assigned_attorney_id가 hr_employee에 없는 UUID | INSERT 실패 (FK 위반 또는 앱 레이어 404) |
| VP-P2-02 | case_type에 허용되지 않은 값 ('other' 등) | INSERT 실패 (CHECK 제약 위반) |
| VP-P2-03 | status에 허용되지 않은 값 | INSERT 실패 (CHECK 제약 위반) |
| VP-P2-04 | 동일 case_number 중복 등록 | INSERT 실패 (UK 위반) |
| VP-P2-05 | 사건 삭제 시 linked legal_case_party 함께 삭제 | CASCADE 확인: party 건수 감소 |
| VP-P2-06 | 사건 삭제 시 linked legal_case_document 함께 삭제 | CASCADE 확인: doc 건수 감소 |

### P3 — 판례 관리·검색

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P3-01 | 동일 citation 중복 등록 | INSERT 실패 (UK 위반) |
| VP-P3-02 | /legal/search?q=이혼 키워드 검색 | legal_precedent 중 holding 또는 keywords에 "이혼" 포함 행 반환 |
| VP-P3-03 | /legal/search?q=존재하지않는키워드 | 0건 결과 HTML 렌더 (에러 아님) |

### P4 — 당사자 관리

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P4-01 | 당사자 등록 시 case_id가 legal_case에 없는 UUID | INSERT 실패 (FK 위반 또는 앱 레이어 404) |
| VP-P4-02 | role에 허용되지 않은 값 ('other' 등) | INSERT 실패 (CHECK 제약 위반) |
| VP-P4-03 | 동일 사건에 동일 역할 2명 등록 (예: C7 피고 2명) | INSERT 성공 (역할별 복수 허용, UNIQUE 없음) |

### P5 — 사건문서 관리

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P5-01 | 사건문서 등록 시 case_id FK 미존재 | INSERT 실패 (FK 위반) |
| VP-P5-02 | 사건문서 등록 후 ingest_status | 'pending' 으로 초기화됨 |
| VP-P5-03 | document_type에 허용되지 않은 값 | INSERT 실패 (CHECK 제약) |
| VP-P5-04 | ingest_status를 'done'으로 수정 후 다시 'pending'으로 수정 | UPDATE 성공 (상태 역전 허용 여부 앱 레이어 정책 확인 필요) |

### P6 — 인사 관리

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P6-01 | 직원 등록 시 department_id FK 미존재 | INSERT 실패 (FK ON DELETE RESTRICT) |
| VP-P6-02 | 직원 삭제 시 해당 직원이 assigned_attorney인 사건이 존재 | DELETE 실패 (FK ON DELETE RESTRICT — legal_case 보호) |
| VP-P6-03 | 직원 삭제 시 document_document.owner_id 참조 존재 | DELETE 실패 (FK ON DELETE RESTRICT) |
| VP-P6-04 | status에 허용되지 않은 값 | INSERT 실패 (CHECK 제약) |
| VP-P6-05 | employee_number 중복 등록 | INSERT 실패 (UK 위반) |

### P7 — 문서관리

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P7-01 | 문서 등록 시 category_id FK 미존재 | INSERT 실패 (FK ON DELETE RESTRICT) |
| VP-P7-02 | 문서 등록 시 owner_id(hr_employee) FK 미존재 | INSERT 실패 (FK ON DELETE RESTRICT) |
| VP-P7-03 | 동일 문서에 같은 version_number 중복 등록 | INSERT 실패 (UNIQUE: document_id+version_number) |
| VP-P7-04 | 접근규칙 등록 시 동일 (document_id, principal_type, principal_id) 중복 | INSERT 실패 (UNIQUE 제약) |
| VP-P7-05 | 접근규칙 permission에 허용되지 않은 값 | INSERT 실패 (CHECK 제약) |
| VP-P7-06 | 문서 삭제 시 linked document_access_rule 함께 삭제 | CASCADE 확인 |
| VP-P7-07 | 문서 삭제 시 linked document_version 함께 삭제 | CASCADE 확인 |
| VP-P7-08 | principal_type=department + principal_id가 hr_department에 없는 UUID | 앱 레이어 검증 실패 (DB FK 없음 — 앱 레이어 책임) |

### P8 — 전자결재

| VP-ID | 검증 항목 | 기대 결과 |
|---|---|---|
| VP-P8-01 | 결재요청 등록 시 requester_id FK 미존재 | INSERT 실패 (FK ON DELETE RESTRICT) |
| VP-P8-02 | approval_request.status에 허용되지 않은 값 | INSERT 실패 (CHECK 제약) |
| VP-P8-03 | 동일 request에 동일 sequence 중복 단계 등록 | INSERT 실패 (UNIQUE: request_id+sequence) |
| VP-P8-04 | 동일 step에 동일 employee 중복 결재자 등록 | INSERT 실패 (UNIQUE: step_id+employee_id) |
| VP-P8-05 | 결재결정 decision에 'pending' 값 | INSERT 실패 (CHECK: approved|rejected만 허용) |
| VP-P8-06 | 동일 (step_id, approver_id) 결재결정 중복 | INSERT 실패 (UNIQUE 제약) |
| VP-P8-07 | 결재요청 삭제 시 linked approval_step 함께 삭제 | CASCADE: step → approver → 삭제 연쇄 |
| VP-P8-08 | 결재요청 status 전이: pending → in-progress | 첫 단계 승인 후 status 수정 확인 |
| VP-P8-09 | 결재요청 status 전이: in-progress → approved | 마지막 단계 승인 후 status 수정 확인 |
| VP-P8-10 | AQ5 시드 검증: step1=approved, step2=active, request=in-progress | 시드 로드 후 상태 일치 확인 |

**검증 포인트 계수**: 총 **34개**
- P1 인증: 5개
- P2 사건: 6개
- P3 판례: 3개
- P4 당사자: 3개
- P5 사건문서: 4개
- P6 인사: 5개
- P7 문서관리: 8개
- P8 전자결재: 10개

---

## 15. QA 게이트 통과 기준 (Merge BLOCK 조건)

| 조건 ID | BLOCK 기준 |
|---|---|
| **BLK-D5-1** | VP-P1-01~VP-P1-02 (로그인 실패·미인증 접근) 1개 이상 FAIL |
| **BLK-D5-2** | VP-P2-01 (assigned_attorney_id FK 위반) FAIL — 사건-직원 관계 훼손 |
| **BLK-D5-3** | VP-P2-05~VP-P2-06 (사건 삭제 CASCADE) FAIL — 당사자·문서 고아 레코드 발생 |
| **BLK-D5-4** | VP-P5-02 (ingest_status 초기값 pending) FAIL — 색인 파이프라인 기준 오염 |
| **BLK-D5-5** | VP-P6-02 (담당 변호사 직원 삭제 RESTRICT) FAIL — 사건 데이터 정합 훼손 |
| **BLK-D5-6** | VP-P7-04 (접근규칙 UNIQUE 중복) FAIL — 권한 중복 허용은 보안 결함 |
| **BLK-D5-7** | VP-P8-06 (결재결정 UNIQUE 중복) FAIL — 동일 결재자 이중결정 허용 불가 |
| **BLK-D5-8** | VP-P8-07 (결재요청 삭제 CASCADE) FAIL — 고아 단계·결재자 발생 |

---

## 부록 A — D1 기능 ↔ DFD 프로세스 대응표

| D1 모듈 | 기능 ID | DFD 프로세스 | 데이터스토어 |
|---|---|---|---|
| A (인증) | A-01~A-04 | P1 | DS-S |
| B-1 (사건) | B-01~B-04 | P2 | DS-2 (legal_case) |
| B-2 (판례) | B-05~B-09 | P3 | DS-2 (legal_precedent) |
| B-3 (당사자) | B-10~B-13 | P4 | DS-2 (legal_case_party) |
| B-4 (사건문서) | B-14~B-17 | P5 | DS-2 (legal_case_document) |
| C-1 (직원) | C-01~C-04 | P6 | DS-1 (hr_employee) |
| C-2 (부서) | C-05~C-08 | P6 | DS-1 (hr_department) |
| D-1 (문서) | D-01~D-04 | P7 | DS-3 (document_document) |
| D-2 (버전) | D-05~D-08 | P7 | DS-3 (document_version) |
| D-3 (카테고리) | D-09~D-12 | P7 | DS-3 (document_category) |
| D-4 (접근규칙) | D-13~D-16 | P7 | DS-3 (document_access_rule) |
| E-1 (결재요청) | E-01~E-04 | P8 | DS-4 (approval_request) |
| E-2 (결재단계) | E-05~E-08 | P8 | DS-4 (approval_step) |
| E-3 (결재자) | E-09~E-12 | P8 | DS-4 (approval_approver) |
| E-4 (결재결정) | E-13~E-16 | P8 | DS-4 (approval_decision) |
| F (killer-app) | F-01~F-03 | 크로스앱 경계 §12 | 해당 없음 (데이터 공유 없음) |
