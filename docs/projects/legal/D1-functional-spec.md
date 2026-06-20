# D1 — 기능명세서 : 법무 통합 제품 (사건관리 + 판례 RAG 검색)

> 문서 번호: D1  
> owner: PM  
> 상태: DRAFT v0.1 (2026-06-20)  
> 연관 anchor: `docs/projects/legal/README.md`  
> 다운스트림: D2(유저플로우) · D3(와이어프레임) · D4(ERD) · D5(DFD)

---

## 1. 제품 개요 & 범위

### 1.1 제품 정의

법무 통합 제품은 **사건관리 CRUD 와 판례 RAG 검색을 하나의 bespoke 법무앱**으로 제공한다. 별개의 두 앱이 아니라 단일 내러티브 — 변호사가 사건 화면 컨텍스트에서 곧바로 판례·사건문서 검색을 호출할 수 있다.

- **인도 형태**: self-host (고객사 사내 서버에 docker 기반 설치)
- **티어**: Lite (검색+인용, LLM 생성 없음)
- **구현 상태**: 서비스 백엔드 LIVE (`legal-rag.n9n.co.kr/app`), 통합 프런트엔드는 미완 (frontend adapter `legal-pro` 설계 예정)

### 1.2 범위 — In Scope

| 영역 | 포함 기능 |
|---|---|
| 사건관리 | 사건 목록 조회, 상태 확인, 사건별 문서 색인 현황 |
| 판례 RAG 검색 | 자연어 질의 → 하이브리드 검색(FTS+ANN+RRF) → 랭킹 청크 + 출처 인용 반환 |
| 인증·격리 | 변호사 이메일+비밀번호 로그인, JWT, 사건·문서 RLS 격리 |
| 문서 인제스트 | PDF/DOCX/TXT 파일 → 청크 → 로컬 임베딩 → DB 저장 (관리자/서비스 토큰 경로) |
| 운영 | 헬스체크(shallow/deep), 환경변수 기반 설정 |

### 1.3 범위 — Out of Scope

| 제외 항목 | 이유 |
|---|---|
| LLM 답변 생성 (생성형 AI) | Pro 티어 게이트. 현재 Lite 티어만 인도. honest-promise 원칙 (Growth-24) |
| 외부 클라우드 임베딩 API | 법률문서 외부 전송 금지 (보안 정책 A5). 로컬 사이드카만 허용 |
| 판례 DB 외부 구독 연동 (로앤비·Westlaw) | 범위 외. 고객 보유 문서 + 직접 인제스트 경로만 |
| 결재·인사 도메인 (approval, hr) | profile 에 도메인으로 등재되어 있으나 이번 인도 범위 외 |
| OCR 처리 (스캔본 PDF) | 문서 현황 점검 후 별도 협의 필요 |
| 멀티테넌트 SaaS 모드 | M5 게이트 조건 미충족. self-host 단독 |
| 재판 전략 자동 수립 (B안) | A안(판례 묶음 제시) 만 채택. Growth-24 honest-promise 원칙 |

---

## 2. 페르소나별 기능 요건

### 2.1 CEO (대표 변호사·파트너)

**목표**: 법적 기밀유지 의무 준수 확인, 투자 타당성 판단, 직원 생산성 향상.

| 요건 | 설명 |
|---|---|
| 데이터 외부 전송 없음 증빙 | 임베딩·검색 전 과정이 사내 서버 내부에서 실행됨을 인도 문서로 확인 |
| RLS 격리 가시성 | 변호사별 사건 격리가 정책(DDL)에 의해 강제됨을 확인 가능 |
| 운영 비용 구조 투명성 | 검색당 외부 API 과금 없음 (서버 실비 제외). 월 추가 청구 없는 구조 |
| 인도물 패키지 | 설치 런북 + 기능명세서(이 문서) + ERD + DFD 를 인도 패키지로 제공 |

**직접 사용 시나리오**: 없음 (비직접 사용자). 운영 현황 대시보드 수요는 D2에서 확인.

### 2.2 업무담당자 (사무장·선임 변호사)

**목표**: 유사 판례 신속 탐색, 사건문서 재활용, 신입 온보딩 가속.

| 요건 | 설명 |
|---|---|
| 자연어 판례 검색 | "이혼 소송 재산분할 최근 판례" 형태 쿼리 → 랭킹 청크 + 출처 번호 반환 |
| 사건 컨텍스트 검색 | 특정 사건(`case_id`) 범위로 검색 스코프 제한 가능 |
| 인용 출처 확인 | 검색 결과마다 `court`, `case_number`, `decision_date`, `holding_summary` 표시 |
| 사건 목록 조회 | 자기 담당 사건 목록 + 각 사건의 문서 색인 상태(`indexed/pending/failed`) 확인 |
| 격리 보장 | 타 변호사 담당 사건의 문서가 검색 결과에 섞이지 않음 (RLS 검색 계층까지) |
| 브라우저 UI | 코드 지식 없이 브라우저에서 로그인 → 검색 → 결과 확인 가능 |

### 2.3 IT 담당자

**목표**: 설치·운영·보안 요건 충족, 사내망 격리 유지.

| 요건 | 설명 |
|---|---|
| Self-host 완전 설치 | Docker 기반 3컨테이너(app + embed-sidecar + postgres). 외부 의존 없음 |
| 사내망 폐쇄 | `LEGAL_RAG_EMBED_URL` = 로컬/사내망 주소만 허용. 외부 URL = 배포 차단 |
| 환경변수 시크릿 관리 | Coolify 볼트 주입. 평문 `.env` 파일 서버 보관 금지 |
| 헬스체크 엔드포인트 | `GET /health` (shallow, 인증 없음) + `GET /health/detail` (X-Service-Token 필요) |
| RLS 활성화 확인 | `relrowsecurity=t, relforcerowsecurity=t` DDL 적용 검증 스크립트 제공 |
| 하드닝 체크리스트 | 7항목 체크리스트 (`docs/runbooks/legal-rag-install.md §7`) 완료 후 인도 |
| rate-limit | `/auth/login` IP 기준 5 req/min (Traefik 미들웨어) |

---

## 3. 기능 목록 (ID별)

### 모듈 A — 인증·세션 관리

| ID | 기능명 | 설명 | 페르소나 | 엔드포인트 | RLS 요건 |
|---|---|---|---|---|---|
| F-01 | 변호사 로그인 | 이메일+비밀번호 → JWT 발급. bcrypt(cost 12) 검증. 이메일 열거 방지(dummy hash 상시 실행) | 업무담당자 | `POST /auth/login` | 없음 (pre-auth) |
| F-02 | JWT 검증 | Bearer JWT HS256 서명 검증. `sub` claim = attorney UUID → RLS 세션변수 설정 | 시스템 | 모든 보호 엔드포인트 미들웨어 | `SET LOCAL app.current_user_id` |
| F-03 | 서비스 토큰 인증 | `X-Service-Token` 헤더 검증 (ingest·health/detail 전용). 상수시간 비교 | IT담당자 | `/ingest`, `/health/detail` | `BYPASSRLS` (app_service 역할) |
| F-04 | 로그인 rate-limit | Traefik 미들웨어로 IP당 5 req/min. 브루트포스 차단 | IT담당자 | `POST /auth/login` (Traefik layer) | 없음 |

### 모듈 B — 사건 관리

| ID | 기능명 | 설명 | 페르소나 | 엔드포인트 | RLS 요건 |
|---|---|---|---|---|---|
| F-05 | 담당 사건 목록 조회 | JWT 변호사에게 배정된 사건 목록. 각 사건의 문서 총수·색인 완료·대기·실패 카운트 포함 | 업무담당자 | `GET /cases` | `assigned_attorney_id = user_id OR partner_id = user_id` |
| F-06 | 사건 상태 표시 | 사건별 `status` (open/closed 등) 및 `doc_total/doc_indexed/doc_pending/doc_failed` 집계 | 업무담당자 | `GET /cases` 응답 | 위임 (F-05와 동일) |
| F-07 | 사건 삭제 없음 | 사건 레코드는 삭제하지 않는다 (법적 감사 요건). DELETE 정책 없음 | CEO | DDL 정책 | `NO DELETE POLICY` 명시 |

### 모듈 C — 판례 RAG 검색

| ID | 기능명 | 설명 | 페르소나 | 엔드포인트 | RLS 요건 |
|---|---|---|---|---|---|
| F-08 | 하이브리드 검색 | 자연어 쿼리 → FTS(plainto_tsquery) + ANN(HNSW cosine) → RRF(k=60) 병합 → top-K 랭킹 청크 반환 | 업무담당자 | `POST /search` | `app_user` 역할 + `SET LOCAL app.current_user_id` |
| F-09 | 사건 스코프 검색 | `case_id` 파라미터로 검색 범위를 특정 사건의 문서로 제한 | 업무담당자 | `POST /search` `case_id` 필드 | 위임 (F-08과 동일) |
| F-10 | 인용 출처 해결 | 각 청크의 `source_id` → `legal_precedent` (case_number, court, decision_date, holding_summary) 또는 `legal_case_document` (document_title, document_type) 메타데이터 조회 | 업무담당자 | `POST /search` 응답 `CitationOut` | 위임 (F-08과 동일) |
| F-11 | 쿼리 로그 기록 | 검색마다 `legal_rag_query_log` 에 attorney_id·query_text·embedding·latency_ms 기록. `query_log_id` 응답에 포함 | IT담당자 | 내부 (`citation.log_query`) | `app_service` BYPASSRLS 경로 |
| F-12 | LLM 생성 없음 보장 | `SearchResponse.note` 에 Lite 티어 선언 명시. 응답에 `answer_text` 없음. 생성형 경로 구조적 배제 | CEO/업무담당자 | `POST /search` 응답 | 해당 없음 |
| F-13 | 검색 청크 RLS 격리 | 판례 청크: 전 변호사 접근 가능. 사건문서 청크: 담당 or 파트너 변호사만 가시 (검색 계층까지 격리) | CEO/IT담당자 | `POST /search` (DB RLS 레이어) | 청크 RLS Policy (`rls_legal_chunk_case_doc_select`) |

### 모듈 D — 문서 인제스트

| ID | 기능명 | 설명 | 페르소나 | 엔드포인트 | RLS 요건 |
|---|---|---|---|---|---|
| F-14 | 파일 인제스트 | PDF/DOCX/TXT 파일 → 텍스트 추출 → ~500 token 청크 분할(50 token 오버랩) → 로컬 임베딩(768-dim) → `legal_document_chunk` upsert | IT담당자 | `POST /ingest` | `app_service` BYPASSRLS (인제스트 파이프라인 전용) |
| F-15 | path-traversal 방어 | `file_path` 를 `LEGAL_RAG_INGEST_ROOT` 하위로만 허용. `os.path.realpath` 로 symlink·`..` 우회 차단 | IT담당자 | `POST /ingest` 검증 레이어 | 해당 없음 |
| F-16 | 인제스트 멱등성 | 동일 `(source_id, source_type, chunk_index)` 재실행 시 기존 청크 덮어쓰기. 부분 실패 후 재실행 안전 | IT담당자 | `POST /ingest` | 해당 없음 |
| F-17 | 임베딩 사이드카 격리 | 외부 클라우드 임베딩 API 호출 없음. 로컬 `intfloat/multilingual-e5-base` 모델(768-dim) 전용. 사이드카 미기동 시 503 반환 (no cloud fallback) | IT담당자 | embed sidecar `POST /embed/batch` | 해당 없음 |
| F-18 | e5 비대칭 프리픽스 | 인제스트=`passage: `, 검색=`query: ` 프리픽스 적용. 첫 인제스트 후 프리픽스 변경 금지 (전 코퍼스 재임베딩 강제, G-87) | IT담당자 | 사이드카 호출 규약 | 해당 없음 |

### 모듈 E — 운영·관리

| ID | 기능명 | 설명 | 페르소나 | 엔드포인트 | RLS 요건 |
|---|---|---|---|---|---|
| F-19 | Shallow 헬스체크 | `{"status":"ok"}` 200 반환. 인증 없음. 내부 상태 미노출 (인프라 정찰 방지). Coolify/Traefik liveness probe 전용 | IT담당자 | `GET /health` | 없음 |
| F-20 | Deep 헬스체크 | DB pool + embed 사이드카 reachability 확인. `X-Service-Token` 필수 | IT담당자 | `GET /health/detail` | 서비스 토큰 인증 |
| F-21 | SPA 정적 파일 서빙 | `/app/*` — vanilla JS SPA. 브라우저 비전문 사용자 시연용. API 라우트가 우선 | 업무담당자 | `GET /app/*` (StaticFiles) | 없음 (auth는 SPA 내 JS 레이어) |
| F-22 | prod 모드 API 문서 비활성 | `LEGAL_RAG_ENV=prod` 시 `/docs`, `/redoc`, `/openapi.json` 비활성. 정보 노출 방지 | IT담당자 | FastAPI 설정 | 해당 없음 |

---

## 4. 비기능 요건 (NFR)

### 4.1 보안 · 데이터 격리

| NFR-ID | 요건 | 기준 | 검증 방법 |
|---|---|---|---|
| N-01 | 데이터 외부 전송 없음 | 임베딩·검색·인제스트 전 과정 사내 서버 내부 실행. 외부 API 호출 0 | `LEGAL_RAG_EMBED_URL` 이 로컬/사내망 주소임을 환경변수 감사로 확인 |
| N-02 | RLS 사건 격리 | 변호사별 사건 목록·문서·검색 청크가 독립 격리. 타 변호사 데이터 교차 노출 0 | `deploy/preview/legal-rag.verify-search.sh` A/B/C 단언 |
| N-03 | 파트너 전체 가시 | `partner_id` 지정 파트너 변호사는 전 사건 조회 가능 | A 단언 (이준호 = partner, 전 사건 검색 가능) |
| N-04 | 인용 환각 0 | 검색 응답의 `CitationOut` 은 DB에 존재하는 `legal_document_chunk.id` 만 참조. 자유 텍스트 생성 없음 | 구조적 보장 — LLM 생성 경로 없음 |
| N-05 | bcrypt 인증 | 비밀번호 bcrypt cost 12 해시 저장. 평문 비밀번호 DB 미저장 | seed SQL 검토 |
| N-06 | JWT HS256 단일 서명 | `LEGAL_RAG_JWT_SECRET` 으로 서명·검증. `sub` claim = attorney UUID | 토큰 디코딩 검증 |
| N-07 | path-traversal 차단 | `/ingest` `file_path` 는 `LEGAL_RAG_INGEST_ROOT` 하위만 허용 | `os.path.realpath` + `commonpath` 검증 (F-15) |
| N-08 | Traefik TLS 종단 | HTTPS 443 종단. HTTP → HTTPS 리디렉션. 사내망 self-host 경로 | `openssl s_client` 인증서 확인 (runbook §7 #5) |

### 4.2 Self-Host 운영

| NFR-ID | 요건 | 기준 |
|---|---|---|
| N-09 | 컨테이너 3개 구성 | app(FastAPI) + embed-sidecar(multilingual-e5-base 내장) + postgres(pgvector+pg_bigm) |
| N-10 | 외부 네트워크 불필요 | embed 사이드카 `HF_HUB_OFFLINE=1`. 런타임 외부 다운로드 없음 |
| N-11 | DB 확장 요건 | PostgreSQL 15+, pgvector, pg_bigm (Korean FTS 보조) |
| N-12 | 시크릿 볼트 관리 | `LEGAL_RAG_JWT_SECRET`, `LEGAL_RAG_DB_DSN`, `LEGAL_RAG_SERVICE_TOKEN` 을 Coolify 볼트 또는 동등한 시크릿 관리 시스템에 주입 |
| N-13 | 멱등 설치 | DDL + seed 재실행 안전 (`IF NOT EXISTS`, upsert 패턴) |

### 4.3 API 비용 경계

| NFR-ID | 요건 | 기준 |
|---|---|---|
| N-14 | 검색당 외부 API 비용 0 | 로컬 embed 사이드카 전용. 클라우드 호출 시 503 (no fallback) |
| N-15 | 인제스트당 외부 API 비용 0 | 동일 사이드카 경로. 판례 1,000건 기준 임베딩 비용 $0 (로컬 모델) |

### 4.4 성능 가이드 (Lite 티어)

| NFR-ID | 요건 | 기준 (목표치, 라이브 검증 후 확정) |
|---|---|---|
| N-16 | 검색 응답 시간 | FTS+ANN+RRF 병합 포함 < 3s (embed 사이드카 hot 상태, 청크 수 < 50,000) |
| N-17 | 동시 사용자 | 30명 규모 법무법인. 동시 검색 5명 이하 상정 (session 인증, SSO 불필요) |

---

## 5. 추적성 매트릭스 — 기능 ↔ 엔드포인트 ↔ 엔티티

| F-ID | 기능명 | 엔드포인트 | 주요 테이블/엔티티 | 데이터 격리 |
|---|---|---|---|---|
| F-01 | 변호사 로그인 | `POST /auth/login` | `legal_attorney` | pre-auth, RLS 없음 |
| F-02 | JWT 검증 | (미들웨어) | — | `SET LOCAL app.current_user_id` |
| F-03 | 서비스 토큰 인증 | `/ingest`, `/health/detail` | — | BYPASSRLS (app_service) |
| F-04 | 로그인 rate-limit | Traefik layer | — | IP 기반 |
| F-05 | 사건 목록 조회 | `GET /cases` | `legal_case`, `legal_case_document` | `assigned_attorney_id` or `partner_id = user_id` |
| F-06 | 사건 상태 표시 | `GET /cases` | `legal_case_document.ingest_status` | 위임 (F-05) |
| F-07 | 사건 삭제 없음 | DDL 정책 | `legal_case` | `NO DELETE POLICY` |
| F-08 | 하이브리드 검색 | `POST /search` | `legal_document_chunk` | `app_user` + `SET LOCAL` |
| F-09 | 사건 스코프 검색 | `POST /search` (`case_id`) | `legal_document_chunk.case_id` | 위임 (F-08) |
| F-10 | 인용 출처 해결 | `POST /search` 응답 | `legal_precedent`, `legal_case_document` | 위임 (F-08) |
| F-11 | 쿼리 로그 기록 | 내부 (citation.log_query) | `legal_rag_query_log` | BYPASSRLS (app_service) |
| F-12 | LLM 생성 없음 | `POST /search` 응답 구조 | — | 구조적 배제 |
| F-13 | 검색 청크 RLS 격리 | `POST /search` (DB 레이어) | `legal_document_chunk` | 청크 policy 2개 (precedent/case_doc) |
| F-14 | 파일 인제스트 | `POST /ingest` | `legal_document_chunk` | BYPASSRLS (app_service) |
| F-15 | path-traversal 방어 | `POST /ingest` 검증 | — | INGEST_ROOT 경계 |
| F-16 | 인제스트 멱등성 | `POST /ingest` | `legal_document_chunk` UNIQUE(source_id, source_type, chunk_index) | 해당 없음 |
| F-17 | 임베딩 사이드카 격리 | embed sidecar `/embed/batch` | — | 로컬 바인딩 전용 |
| F-18 | e5 비대칭 프리픽스 | embed 호출 규약 | `legal_document_chunk.model_version` | 불변식 (G-87) |
| F-19 | Shallow 헬스체크 | `GET /health` | — | 없음 |
| F-20 | Deep 헬스체크 | `GET /health/detail` | — | 서비스 토큰 |
| F-21 | SPA 정적 파일 서빙 | `GET /app/*` | — | SPA 내 JS auth |
| F-22 | prod API 문서 비활성 | FastAPI 설정 | — | 없음 |

---

## 6. 핵심 가정 · 결정 기록

| 항목 | 결정 | 근거 |
|---|---|---|
| 통합 단일 앱 | 사건관리 + RAG 검색을 한 앱으로 | README §1 — 별개 2앱 아님, 단일 내러티브 |
| Lite 티어 고정 | 검색+인용만, LLM 생성 없음 | honest-promise 원칙 (Growth-24). Pro 티어는 로드맵 |
| 로컬 임베딩 only | 클라우드 API fallback 없음 | 법률문서 외부 전송 금지 (보안 A5) |
| RLS를 검색 계층까지 | `/search` 도 RLS 적용 (청크 레벨) | 목록 격리만으로는 불충분. verify-search.sh B 단언으로 라이브 실증 |
| 사건 삭제 정책 없음 | DELETE 미지원 | 법적 감사 요건. 논리 삭제(status 변경)로 대체 |
| 파트너 전체 가시 | `partner_id` 기반 교차 가시 | 파트너 변호사의 감독 업무 요건 |
| 인제스트 BYPASSRLS | app_service 역할 사용 | 청크 쓰기는 인증 파이프라인이 아닌 서비스 토큰 경로 |
| e5 프리픽스 고정 | 첫 인제스트 후 변경 금지 | 전 코퍼스 재임베딩 강제 방지 (G-87) |

---

## 7. 열린 질문 (D2/D4/D5 진행 전 확인 필요)

| # | 질문 | owner | 우선순위 |
|---|---|---|---|
| Q-1 | 사건 CRUD (생성·수정 화면) 가 이번 인도 범위인가, 아니면 조회 전용인가? — `GET /cases` 만 존재, `POST /cases` 없음 | PM → CEO | 높음 |
| Q-2 | 판례 직접 인제스트 vs 사건문서 인제스트 중 데모 우선 경로는? seed 는 양쪽 모두 존재 | PM → 업무담당자 | 중간 |
| Q-3 | `legal_rag_query_log.query_text` 평문 저장 — 개인정보보호법 관점에서 고객사 IT 담당자와 협의 필요 여부 | PM → IT담당자 | 중간 |
| Q-4 | 결재·인사 도메인(approval, hr) 은 추후 통합 계획이 있는가? D4 ERD 설계에 영향 | PM → CEO | 낮음 |
| Q-5 | OCR 처리 범위 — 스캔본 PDF 비율이 고객사에서 얼마나 되는가? 구축 범위 영향 | PM → 업무담당자 | 중간 |

---

## 부록 A — 엔티티 목록 (D4 ERD 입력)

| 엔티티 | 테이블명 | 모듈 | 비고 |
|---|---|---|---|
| 변호사 | `legal_attorney` | 인증 | is_active, bcrypt 해시, display_name |
| 사건 | `legal_case` | 사건관리 | RLS: assigned_attorney_id, partner_id |
| 당사자 | `legal_case_party` | 사건관리 | 원고·피고, RLS 위임 |
| 사건문서 | `legal_case_document` | 사건관리·인제스트 | ingest_status 열거형 |
| 판례 | `legal_precedent` | RAG | court, case_number, decision_date, holding_summary |
| 문서청크 | `legal_document_chunk` | RAG 인제스트 | embedding vector(768), source_type 다형성 |
| 쿼리로그 | `legal_rag_query_log` | 운영·감사 | attorney_id, query_text, latency_ms |

## 부록 B — DDL 파일 적용 순서

```
01_extensions.sql        — pgvector, pg_bigm, 롤 정의
02_legal_case_augment.sql — legal_case RLS + FTS 컬럼
03_precedent_augment.sql  — legal_precedent FTS + 인용 메타
04_case_document_augment.sql — ingest_status, FK
05_case_party_rls.sql     — legal_case_party RLS
06_legal_document_chunk.sql  — 청크 테이블 + 벡터 인덱스 + RLS
07_rag_query_log.sql      — 쿼리 로그
08_legal_attorney.sql     — 변호사 인증 테이블
09_grants.sql             — app_user 권한 부여
```
