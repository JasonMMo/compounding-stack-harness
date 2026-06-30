# 한방 RAG 데모 스파이크 빌드 계획서

> 작성자: engineer-agent | 기준: legal-rag 코드 직접 탐색 결과
> 대상: services/legal-rag → services/hanbang-rag 포크

---

## 1. Legal-rag 스택 현황 맵

### (a) Corpus-독립적 재사용 가능 파일

| 파일 경로 | 역할 | 포크 시 처리 |
|---|---|---|
| `services/legal-rag/ingest.py` | 텍스트추출→청크→배치임베딩→upsert 파이프라인 | 재사용. SQL 2줄 교체 (확인: `_CHECK_PRECEDENT_SQL` → `hanbang_notice`) |
| `services/legal-rag/retrieve.py` | FTS+ANN+RRF 하이브리드 검색, pg_bigm 지원 | 재사용. `legal_document_chunk` 테이블명만 교체 |
| `services/legal-rag/embed_client.py` | 로컬 임베딩 사이드카 HTTP 클라이언트 | 무변경 복사 |
| `services/legal-rag/embed-adapter/` | 로컬 임베딩 모델 FastAPI 컨테이너 (multilingual-e5-base) | 무변경 복사 |
| `services/legal-rag/auth.py` | JWT HS256 mint/verify | 무변경 복사 (user 테이블명만 seed 레벨에서 교체) |
| `services/legal-rag/db.py` | psycopg 풀 + rls_session() | 무변경 복사 |
| `services/legal-rag/config.py` | env-driven Settings (env var 이름만 HANBANG_RAG_* 로 prefix 변경) | env var prefix 교체 |
| `services/legal-rag/citation.py` | 청크→출처 메타데이터 JOIN 해소 | SQL 교체 (`legal_precedent` → `hanbang_notice`) |

### (b) Legal 도메인 특정 — 교체 필요

| 파일 경로 | 역할 | 포크 시 처리 |
|---|---|---|
| `services/legal-rag/api.py` | FastAPI 앱 전체 | 재구현. 사건(/cases) + 당사자 + 문서업로드 엔드포인트 제거. /search + /ingest + /health + /documents/notice/* 유지 |
| `services/legal-rag/web/index.html` | 바닐라 JS SPA (법률 문서 검색 UI, 사건현황 탭 포함) | 교체. 검색 탭만, 카피 전면 교체 |
| `services/legal-rag/web/app.js` | SPA 로직 (cases 탭, 판례 드로어 포함) | 교체. 검색+드로어만 |
| `services/legal-rag/web/styles/tokens.css` | 디자인 토큰 | 조정 (브랜드 컬러) — CDO 위임 |
| `out/legal-rag-deploy/00_base.sql` 참고 | DDL schema (legal_case/legal_attorney 등 법무 엔티티) | 신규 DDL 작성: hanbang_notice + hanbang_document_chunk + hanbang_user |
| `services/legal-rag/Dockerfile` | multi-stage (Node legal-pro React + Python runtime) | 교체. legal-pro React 스테이지 제거, 바닐라 SPA만 |
| seed scripts (inline) | legal_attorney/legal_precedent INSERT (테스트코드에 내장, 확인) | 신규 시드: hanbang_notice 4건 + hanbang_user 1건 (데모 계정) |

---

## 2. 한방 포크 최소 변경 목록

슬러그: `hanbang-rag` | 신규 서비스 디렉터리: `services/hanbang-rag/`

| # | 변경 항목 | 작업 내용 | 비고 |
|---|---|---|---|
| 1 | **DDL** | `hanbang_notice` (고시번호·소관부처·발령일자·요약·전문), `hanbang_document_chunk` (법무 청크 테이블 리네임), `hanbang_user` (데모 로그인) | `case_type` CHECK 제거, `notice_type` TEXT 컬럼으로 대체 |
| 2 | **ingest.py** | `_CHECK_PRECEDENT_SQL` 2줄 → `hanbang_notice` 참조 | 5줄 수정 |
| 3 | **retrieve.py** | `legal_document_chunk` → `hanbang_document_chunk` (테이블명 상수 교체) | 3줄 수정 |
| 4 | **citation.py** | `legal_precedent` → `hanbang_notice`, 필드명 매핑 조정 | ~10줄 수정 |
| 5 | **api.py** | 신규 작성. case/party/document_upload 엔드포인트 제거. /search + /ingest + /health + /auth/login + /documents/notice/* 유지 | legal-rag api.py 400줄 → 약 150줄 |
| 6 | **web/** | 카피 교체: "법률 문서 검색" → "한방 급여 고시 검색". 사건 탭 제거. 예시 질의 5개 교체 | index.html + app.js |
| 7 | **시드 스크립트** | `scripts/corpus/seed_hanbang_notices.py` — hanbang_notice 4건 INSERT + hanbang_user 1건 | VPS에서 corpus 수집 후 실행 |
| 8 | **Dockerfile** | legal-pro React 스테이지 제거, 바닐라 SPA COPY만 | 단순화 |
| 9 | **Coolify 신규 스택** | hanbang-rag 전용 compose (FastAPI + postgres + embed-adapter), 새 서브도메인 (`hanbang-rag.n9n.co.kr`) | 인프라 결정 필요 (항목 §6) |

> **재구현 금지 원칙 준수**: ingest/retrieve/citation/auth/embed 파이프라인은 코드를 읽기만 하고 카피 후 최소 교체. 검색 로직은 완전 재사용.

---

## 3. Corpus 큐레이션 후보

`fetch_hanbang_admrul.py` SEARCH_KEYWORDS: `["첩약 급여", "한방 건강보험", "한의약", "약침"]`

| 우선순위 | 고시 후보 | 검색어 | 제안 이유 |
|---|---|---|---|
| ★1 | **첩약 건강보험 적용 시범사업 관련 고시** | `첩약 급여` | 적용 질환·상한액·처방 제한이 청구 핵심 페인 |
| ★2 | **요양급여의 적용기준 및 방법에 관한 세부사항 (한방)** — 추나요법·한방물리요법 | `한의약` | 추나 급여인정범위가 일선 청구 오류 1위 |
| ★3 | **한의 약침 급여기준 고시** | `약침` | 회수·용량·부위 제한 조회 빈도 높음 |
| ★4 | **건강보험 행위 급여·비급여 목록 (한의 편)** | `한방 건강보험` | 수가점수 직접 조회 — CEO 인터뷰 임팩트 최대 |

> 실수집은 VPS(187.77.140.157)에서 `fetch_hanbang_admrul.py` 실행. `OUT_DIR = out/corpus/hanbang/`. 수집 후 `.txt` 변환 → `/ingest` 엔드포인트 호출.

---

## 4. 데모/마케팅 페르소나·시나리오

**타겟 페르소나**: 한의원 청구담당자 (원장 또는 원무직원), 월 심사청구 100~300건

| # | 검색 질의 예시 | 페인 포인트 |
|---|---|---|
| 1 | `추나요법 급여 인정 횟수 기준` | 주 1회 인정인지 월 4회인지 매번 심사기준 찾다 시간 소모 |
| 2 | `첩약 시범사업 적용 질환 목록` | 적용 가능 질환인지 확인 안 하고 청구 → 삭감 |
| 3 | `약침 급여 청구 시 용량 제한` | 용량 초과 청구 → 자동 삭감, 반환금 발생 |
| 4 | `한방 물리요법 비급여 전환 조건` | 비급여로 처리해야 하는 케이스 구분 불명확 → 민원 |
| 5 | `한의 행위 상대가치점수 조회` | 수가 계산 오류 시 환자 과다 청구 분쟁 |

> 시나리오: 인터뷰어가 질의 1-3을 라이브 입력 → 고시 원문 청크 + 출처 고시번호 즉시 표시 → "이게 AI가 답한 게 아니라 고시 원문입니다" 로 신뢰 전달.

---

## 5. 빌드 단계 (스파이크)

| 단계 | 작업 | 완료 기준 | 예상 리스크 |
|---|---|---|---|
| **D0** | `services/hanbang-rag/` 디렉터리 생성, 파일 복사, 5개 SQL 교체 (ingest/retrieve/citation), Dockerfile 단순화 | L1: `pytest -q` PASS (ingest/retrieve 단위 테스트 통과) | 테이블명 오타 → SQL 에러 |
| **D1** | DDL 작성 (`hanbang_notice` + `hanbang_document_chunk` + `hanbang_user`), api.py 신규 작성 (case 엔드포인트 제거) | L1: api.py pytest PASS; 스키마 수동 검증 | source_type 값 매핑 오류 |
| **D2** | VPS에서 corpus 수집 (`fetch_hanbang_admrul.py`), XML→텍스트 변환, 4건 시드 INSERT, `/ingest` 호출 | L2: DB에 chunk 12~30개 확인, `/health/detail` OK | XML 파싱 실패 → 수동 텍스트 추출 대안 필요 |
| **D3** | 웹 UI 카피 교체 (hanbang 검색 특화), 예시 질의 5개, Coolify 배포 | L4: 브라우저에서 질의 1-3 검색 → 청크 + 고시번호 반환 PASS | Coolify 환경변수 누락 (legal-rag 런북 §9 참고) |
| **D4** | 인터뷰 리허설 + 마케팅 랜딩 연결 지점 확인 | 인터뷰 시나리오 5개 전부 올바른 청크 반환 | 관련 고시 미수집 → corpus 보강 |

> D0~D4 총 예상: **3~4일** (개발 집중 시). 각 단계는 전 단계 L1/L2 PASS 후 진행.

---

## 6. 마케팅 폭 vs 인터뷰 폭

| 항목 | 인터뷰 최소본 (D0~D3) | 마케팅 랜딩 추가 (D4+, CDO 위임) |
|---|---|---|
| 인증 | 데모 단일 계정 (email/pw 하드코딩 시드) | 소셜 로그인 or 신청 게이트 |
| UI 품질 | 기능 동작 확인 수준 (토큰.css 컬러 최소 조정) | 디자인 토큰 전면 교체, 모바일 반응형, 한방 브랜드 컬러 |
| corpus 규모 | 4건 (추나+첩약+약침+행위목록) | 추가 10~20건, 자동 수집 파이프라인 |
| 결과 표시 | 청크 텍스트 + 고시번호 + RRF 점수 | 고시 원문 슬라이드오버, 고시 발령일 배지, 관련 고시 크로스링크 |
| 배포 URL | `hanbang-rag.n9n.co.kr` (내부 데모용) | 공개 랜딩 페이지 (`hanbang.yesnic도메인`) |

---

## CTO 결정 필요 사항 (greenlight 전)

1. **테이블명 전략**: `legal_document_chunk` 테이블명을 그대로 쓰되 hanbang DB에 배포할지 (`hanbang_document_chunk`로 리네임할지) — 리네임 시 retrieve.py 수정 3줄 추가, 유지 시 법무 네이밍이 혼재.

2. **인증 모델**: 데모용 단일 계정 (시드 고정 bcrypt 해시)으로 충분한지, 아니면 공개 접근(인증 제거)으로 랜딩 타겟팅할지 — 보안 정책 결정 (CISO 관련).

3. **배포 위치**: Coolify 신규 스택(별도 VPS 포트)으로 hanbang-rag 독립 배포할지, legal-rag 기존 VPS에 동거 배포할지 — DevOps 비용 영향.

---

## CTO greenlight (2026-06-30) — 결정 확정, D0 착수 승인

> 위 3개 결정 + 빌드 GO. 이 섹션이 post-clear 빌드의 단일 출처. founder 승인필요 표기 항목만 별도.

| # | 결정 | 확정 | 사유 |
|---|---|---|---|
| 1 | 테이블명 전략 | **`hanbang_*` 리네임** (notice/document_chunk/user) | 별도 버티컬·별도 DB·마케팅 정체성. 3줄 추가는 사소, 도메인 혼재 방지가 우선. retrieve.py 테이블명 상수만 교체 |
| 2 | 인증 모델 | **auth 유지 + 시드 단일 데모계정** (인터뷰용). 인증 제거 ✗ | corpus는 공개 고시(PII 0)라 공개 read 자체는 저위험이나, 멀티테넌트 RLS 데모를 무인증 노출하지 않는다. **공개 랜딩의 read-only 데모 테넌트는 CISO 게이트 후 Phase 2** (founder 공개 결정 시점에 security-loop) |
| 3 | 배포 위치 | **하이브리드: hanbang 전용 FastAPI 컨테이너 + 독립 서브도메인(`hanbang-rag.n9n.co.kr`), 단 postgres 인스턴스·embed-adapter 사이드카는 legal-rag와 공유** | 정체성은 독립(마케팅 URL 분리), infra 비용은 hedge — 신규 VPS/postgres 0, embed 모델(multilingual-e5-base) 동일하므로 사이드카 1개 공유로 RAM 절감. DB는 별도(스키마 격리). DevOps-loop으로 비용 1줄 측정 |

**D0 착수 조건**: 위 3건 확정으로 충족. 빌드는 D0(파일 복사+SQL 교체, L1 PASS)부터 순차.
**founder 승인 필요 (빌드 차단 아님, 병렬)**: ②의 공개 랜딩 노출 시점 — 인터뷰 데모(무공개)는 지금 진행, 공개 URL은 founder가 "공개" 결정 시 CISO 게이트.
**비용 메모**: postgres·embed 공유로 신규 월비용 ≈ FastAPI 컨테이너 1개 + 서브도메인뿐. legal-rag 대비 증분 최소.
