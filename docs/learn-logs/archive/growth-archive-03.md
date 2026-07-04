# Growth Archive Vol.03 — Growth-97 ~ Growth-128

> `growth-archive.md`(인덱스) 산하 볼륨. 원문 무수정 이동. 규약: `docs/learn-logs/README.md`.

## Growth-68 ~ Growth-134 (2026-06-15 ~ 2026-06-30, 이동: Growth-143) (계속)

### Growth-97 (2026-06-20) — 법무 RAG 브라우저 데모 라이브: `/app` SPA 화면전환 복구(`[hidden]` CSS 결함), M3 비전문 구매자 시연 가능 (M3 vertical)
- **1줄 rollup**: 이미 빌드돼 있던 SPA(`web/`, `/app` 마운트, 로그인+검색+사건현황+인용카드+접근성)가 1개 CSS 결함으로 화면전환 불능 → 1줄로 복구해 **브라우저 데모 라이브**. founder Redeploy 후 로그인→검색 전환·A/B 격리 화면시연 확인.
- **근본원인/교훈**: SPA 가 화면·패널·배너 가시성을 HTML `hidden` 속성(`el.hidden=...`)으로 토글하는데 `app.css` 에 전역 `[hidden]` 리셋이 없어, `.login-wrapper`/`.app-root` 의 `display:flex`(author)가 UA `[hidden]{display:none}` 을 덮어 **`hidden` 속성이 무력화**(author cascade > UA). `showScreen()`/패널 토글이 "에러 없이 전환만 안 됨" 증상. 픽스: `[hidden]{display:none !important}` 전역 1줄(normalize.css 표준) — 화면+모든 `.hidden` 토글 일괄 복구. **교훈: author `display` 클래스가 하나라도 있으면 `[hidden]` 전역 리셋은 필수(빠지면 정적·단위테스트 불가시, 브라우저 실행에서만 발현)**.
- **정직성**: 오늘 새 UI 빌드 없음 — CDO 가 이미 빌드해 둔 자산의 막힌 데를 뚫음. 진단은 정적으로 확정(JS 정상 → CSS cascade 위반) 후 design-agent(CDO) 에 1줄 위임, CDO 스킬 자가환류. web/ 는 이미지 bake-in → 적용에 Redeploy 필요(git pull 불충분), 브라우저 CSS 캐시는 강력새로고침으로 무효화.
- **누적 자산**: runbook §4-6(브라우저 데모 경로 `/app` + `[hidden]` 함정노트) · 커밋 cafea04(per-file).
- **Open loops**: 내일 founder 질문 예정 — 관련도(`rrf_score`)·청크 의미·조절 방법(top_k·청크 토큰타깃·RRF k·하이브리드 가중치). [[legal-rag-mvp-build]]

### Growth-98 (2026-06-20) — 법무 통합 제품 D1~D5 페르소나 드래프팅 + DFD 게이트 false-positive 2단 검증 (M3 vertical)
- **1줄 rollup**: `docs/projects/legal/README.md` 골격의 D1~D5 슬롯을 4 페르소나 3-wave 오케스트레이션으로 산출 — D1 기능명세(PM, F-01~F-22+NFR22), D2 유저플로우(PM, 4플로우+screen inventory S-01~S-17), D3 와이어프레임(CDO, 16뷰+theme `legal-pro` 권고), D4 ERD(DBA, 8엔티티/10관계), D5 DFD(DBA P1~P25 + QA §9 검증게이트 21단언). 각 페르소나 envelope-only 반환(subagent-output-protocol)으로 main context 보호.
- **근본원인/교훈**: QA 가 DFD 게이트에서 I-1(임베딩 `passage:`/`query:` prefix 미적용 → BLK-1 merge BLOCK)을 founder 보고 직전까지 올렸으나, **CTO 독립 소스검증 결과 false positive**. prefix 는 메인 `embed_client.py`(thin wrapper, raw text 의도된 전달)가 아니라 **embed-adapter 사이드카**(`embed-adapter/app.py`: `/embed`→query·`/embed/batch`→passage, `_embed_local()` 적용, 불변식 테스트 `test_adapter.py` 보유)가 적용. 호출부 정합(ingest=batch/passage, search=single/query)이며 caller-split 은 **기존 정적 가드 G-87 으로 이미 보호**. QA 가 사이드카+G-87 둘 다 미열람. **교훈: 서브에이전트의 결함 판정(특히 cross-service/사이드카 경계)은 founder-facing 보고 전 CTO 독립검증 필수 — thin wrapper 만 보고 결함 단정 금지**. [[subagent-cross-service-verify]]
- **정직성**: 라이브 검색 prefix·rrf_score 품질 정상 확정(메모리 legal-rag "LIVE·동작" 유효, 품질 미달 아님). 새 코드 0 — 문서 산출 + 거짓 BLOCK 정정만. D5 §9.1/9.2/9.4/9.5 + README §3/§7 의 BLK-1 표기를 "철회(false positive)" 로 일괄 정정.
- **누적 자산**: D1~D5 정식 standalone 문서 5종(`docs/projects/legal/D{1..5}-*.md`) — §2 3중용도(영업·인도물·구현입력). DFD 게이트 = 코드 前 설계검증 + CTO 독립검증 2단 프로세스 패턴 확립.
- **Open loops**: BLOCK 아닌 triage 갭 — 엔드포인트 G-1~G-6(D2), 성능 I-2(FTS+ANN 병렬화), 데이터모델(polymorphic FK·keywords 1NF), 열린질문 Q-1(사건 CRUD 범위)/Q-3(query_text 평문 PIPA). 다음: adapter/theme `legal-pro` 구현 패스. [[legal-unified-product-docs]] [[legal-rag-mvp-build]]

### Growth-99 (2026-06-20) — 한국어 형태소 분석기(pg_bigm/pgroonga) "조건부 장착·기본 비활성" 설계 근거 follow-up 박음 (M3 vertical)
- **1줄 rollup**: founder 질문("형태소 분석기 적용을 왜 미뤘나")에 코드 독립검증 후 답 — 미적용이 아니라 **조건부 opt-in + 기본 비활성**. 런타임 FTS 는 `to_tsvector('simple', …)`(형태소 없음, `retrieve.py`/06_chunk.sql:86), pg_bigm 는 `01_extensions.sql:14-22` 가 `pg_available_extensions` 가드로 감싸 있으면 켜고 없으면 plainto_tsquery degrade, pgroonga 는 주석 대안만.
- **유보 근거 4종(CTO 판단, follow-up 트리거 명시)**: ①preview/데모 티어 pgvector-only 이미지 호환 — 필수 의존으로 걸면 데모 깨짐(G-4 round-trip 정신, 환경차를 강결합화 금지) ②**하이브리드라 한계효용 낮음** — `'simple'` 토큰화 약점(동의어·어미변화)을 e5-base ANN 이 상쇄, RRF 병합이 두 약점 보완(`legal-rag-pattern.md §2`) → 형태소 분석기 marginal gain 이 FTS-only 대비 작음 ③운영비용 — pgroonga 별도 빌드+큰 이미지, mecab-ko 사전 운영부담, 데모 12청크엔 premature ④비-블로킹 — 정밀도 gap 인지·문서화됨, follow-up 일 뿐 게이트 차단 아님. **트리거: 한국어 substring recall 이 ANN 으로도 안 잡히는 실쿼리가 실고객 코퍼스(M2/M3)에서 발생하는 시점.**
- **정직성**: 새 코드 0 — 설계 근거 환류만. 메모리 legal-rag "미검증 리스크" 한국어 FTS 항목과 정합. [[legal-rag-mvp-build]] [[subagent-cross-service-verify]]

### Growth-100 (2026-06-20) — 법무 RAG 원문보기 슬라이드오버 구현(GET /documents + drawer) + founder 데이터제안 카테고리/저작권 정정 (M3 vertical)
- **1줄 rollup**: founder 요청("판례 데이터 추가 + 원문보기 우측 슬라이드 레이어, bigcase.ai 참고, 타당성 검토")에 대해 — **UI 기능은 구현, law.go.kr 실데이터 수집은 founder 결정 보류**로 갈라 진행(외출 중 "진행 가능하면 진행" 승인). engineer 위임 구현: `api.py` `GET /documents/{source_type}/{source_id}`(JWT+`rls_session` 강제, precedent=full_text/holding fallback, case_document=content_text·RLS 자동격리, 행없음→404 존재미노출 fail-safe) + web drawer(우측 translateX 슬라이드, role=dialog/aria-modal/포커스트랩/ESC·백드롭, 기존 tokens.css 준수). 이미 있던 `aria-disabled` "원문 보기 →" 버튼 활성화. 단위 118→**134 passed/4 skip**(CTO `rtk proxy pytest` 독립 재실행 검증), 5파일 per-file 커밋 2d7a5b9~0bd67b0 푸시.
- **타당성 검토 3분기(CTO)**: ①UI 슬라이드오버=타당(법률검색 표준 master-detail, 버튼 이미 stub, 원문직접표시=인용무결성 강화·생성아님=thesis정합) ②**"판례를 seed_case_documents.sql에 추가"=대상파일 오류** — 그 파일은 판례 아니라 **사건서류**(소장·준비서면, 가명필수=의뢰인비밀·CISO룰), 판례는 별도 `seed_precedents.sql`(22건 가상). law.go.kr엔 판결문만 존재(소장 없음) ③**law.go.kr 실데이터 자동수집=보류** — 판결문 자체는 저작권 비보호(저작권법§7)나 사이트 약관·편집저작권·"api 사용안함" 룰 + outward-facing ToS리스크 → 명시승인 전 미실행. **기능 구현엔 새 데이터 불요**(precedent.full_text 이미 채워짐).
- **검증/진단**: app.js 진단 `openDocDrawer not found`(line422)는 편집중 stale 스냅샷 — 함수선언 hoist(174정의/623참조) + `/search` 응답에 source_type/source_id 실존(api.py:198-199, retrieve.py:110) 소스레벨 정합 확인. Python import 에러는 app-dir 런타임해석 Pyright false-positive.
- **founder 게이트(복귀 후)**: ①브라우저 실검증(web/ bake-in→Redeploy 필요, drawer 표시·full_text·**박서연→이준호 사건문서 404 격리** 화면, Growth-97류 정적불가) ②law.go.kr/실판례 데이터 정책 결정 ③CDO drawer 비주얼 리뷰 ④cross-attorney 404 격리 실DB 통합테스트(C2 `pytest -m postgres` 자리 마련됨). [[legal-rag-mvp-build]]

### Growth-101 (2026-06-21) — 법무 RAG C2 postgres 통합테스트 6종 + C1 production 최소권한 하드닝 DDL (M3 vertical)
- **인격/Axis/Milestone**: CTO(스코프 확정·내부소스 정독·2-레인 병렬 위임·통합검증·per-file 커밋·푸시) + Engineer(C2 테스트 5+1) + DBA(C1 하드닝 DDL) / **backend(테스트)·ddl(하드닝)** / M3. 8커밋 1b27f1f..1b6b181 origin/master 푸시.
- **1줄 rollup**: Growth-100 게이트④ + open-loop(C2 `pytest -m postgres`, C1 production app_service 비-슈퍼유저) 동시 종결. **C2**: D5-dfd §9.5 흡수목록 6종 구현(미구현 6→0) — G-P7 재인제스트 멱등(upsert COUNT 불변)·G-P8a/b ingest_status done/error 전이·G-P17 `/search`→query_log +1·G-P19 app_user→legal_attorney `InsufficientPrivilege`·G-P15 RLS 검색격리(이준호 c001 가시/박서연 0건, verify-search.sh A/B의 pytest 등가). 공용 픽스처 `conftest.py`: `pg_conn` force_rollback 트랜잭션(DB 무오염)+`stub_embed_client`(사이드카 미접속·외부 API 0)+`DUMMY_VEC`. `LEGAL_RAG_DB_DSN_POSTGRES` DSN 게이트 — 미설정 시 자동 skip, 라이브 실행은 founder. **C1**: `presets/ddl/augments/legal/10_production_hardening.sql`(ADD-ONLY·production 전용·프리뷰 apply-schema 미포함) — `ALTER ROLE app_service NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION`(BYPASSRLS만 의도적 유지=ingest 교차사건 write+legal_attorney 로그인 read 필수, ≠슈퍼유저), 소유권 미의존 최소 GRANT(legal_attorney SELECT·chunk SELECT/INSERT/UPDATE·case_document SELECT+UPDATE(ingest_status,ingested_at) 열범위·precedent SELECT), query_log 비부여.
- **검증/진단**: 단위 **188 passed/10 skipped**(10 skip = postgres 마크 전량 DSN 미설정 자동 skip, 수집오류 0). `-m postgres` 단독도 10 skip 클린. Pyright 경고는 전부 false-positive — `ingest_file(**common)` dict-unpacking이 keyword-only 시그니처를 정적해석 못해 str→param 오인(런타임 정상), `import psycopg` 미해소는 dev env 부재(라이브 venv 존재, G-P19는 함수내 lazy import), stub `embed(text)` 미사용 인자=실 EmbedClient 인터페이스 일치용. docker 데몬 미가동이라 로컬 실 PG 미기동 — founder-gate skip 패턴(런북 §9 선례) 채택.
- **문서 환류**: 런북 §7 하드닝 7→8항목(#8 production 최소권한 절차+rolsuper 검증+G-P19 회귀게이트). D5-dfd §9.2 6행 미구현→구현됨·계수 미구현 0, §9.5 단언↔테스트파일 매핑표.
- **Open loops**: C2 6종 **라이브 실행은 founder 게이트**(실 PG+seed+ingest 필요, preview DB 준비됨) · C1 production 별도 owner 롤 분리(REASSIGN OWNED)는 법무법인별 연산자 결정(DDL은 문서화만) · G-88(seed UUID 가드)·WTP 인터뷰 3~5곳(PM) 미해결 잔존. [[legal-rag-mvp-build]] [[legal-rag-korean-lexical-pass]]

### Growth-102 (2026-06-21) — 법무 통합 제품 별도 adapter 결정 + `legal-pro` React 어댑터 Phase A 빌드 (M3 vertical)
- **인격/Axis/Milestone**: CTO(adapter 갈림길 확정·스코프 페이즈분리·검증 독립실행·검색계약 검수·푸시·원장) + Engineer(스캐폴드·검색화면 포팅·16 per-file 커밋) / **frontend** / M3. founder 가 stack 결정(AskUserQuestion): CTO 권장(라이브 vanilla-JS SPA 승격) 기각, **React+Vite 별도 어댑터** 택함.
- **1줄 rollup**: 법무 통합 제품(사건관리+판례검색)의 §5 미확정 갈림길 해소 — vanilla-htmx 위 theme 레이어 ✗, **별도 `frontend/adapters/legal-pro/` (React+Vite, `react` 어댑터 변형)** 로 확정. 동기: 7 데모가 한 디자인(vanilla-htmx)이라 의뢰자에게 "하나처럼" 보이는 약점 → legal 을 시각적으로 다른 프리미엄 제품으로. **Phase A**(차단없음) 빌드: 스캐폴드(package/vite/tsconfig/codegen/build-tokens) + legal-pro 테마 baked-in(build-tokens.mjs 가 `services/legal-rag/web/styles` 3 CSS 연결 — 라이브가 단일 진실, 재발산 방지) + `PrecedentSearchScreen.tsx`(app.js → React/TS 포팅) + LoginScreen(JWT). **Phase B**(사건관리 CRUD) = `/cases` G-1~G-6 미구현 + Q-1 스코프 미확정에 차단, App.tsx/README 에 마킹. 중간 contract 읽기전용(codegen 은 legal-rag 실 FastAPI 경로 + error 카탈로그만 읽음, 제너릭 wire 미사용).
- **검증/진단**: **L3 build PASS (CTO 독립 재실행)** — `npm run codegen && build:tokens && tsc --noEmit && vite build`, 38 모듈, dist(CSS 27.11kB/JS 175.08kB) 696ms. node_modules 존재 확인. IDE 진단(`process`/`vite`/`test does not exist`/`js-yaml` 미선언)은 LSP 가 빌드 tsconfig 대신 앱 tsconfig 로 vite.config·node 스크립트 해석한 false-positive — 실 `tsc --noEmit` clean. **검색 응답계약 보존 검수**(PrecedentSearchScreen 정독): `관련도 round(relevance*100)%`(rrf_score 폴백만)·citation `key=chunk_id` 1:1·환각0(반환 인용만)·키워드일치 뱃지(fts_rank)·"출처 인용만 제공" 무생성 note·AND·OR·empty/error/sidecar-down 모두 충실. 원문보기 alert()·사건필터 select 은 Phase B TODO 마킹.
- **문서 환류**: README §5 "미확정"→"확정"(별도 adapter + 페이즈표). 메모리 [[legal-unified-product-docs]] adapter 결정 블록.
- **Open loops**: Phase B 사건관리 CRUD(`/cases` G-1~G-6 엔드포인트 backend 선행 + Q-1 CRUD 범위 PM/founder 확정) · 원문보기 드로어(openDocDrawer, `/documents` 검증 필요) · legal-pro 어댑터 단위테스트 미작성(react 어댑터엔 4종 존재 — 후속) · L4 live(배포 후 HTTP) 미실행. [[legal-rag-mvp-build]] [[marketing-site-track]]

### Growth-103 (2026-06-21) — 법무 RAG `/cases` 읽기 backend 뚫기 + G-4 페이지네이션 (Phase B 부분 해제, M3)
- **인격/Axis/Milestone**: CTO(읽기/쓰기 스코프 분할·기존 라우트 감사 위임·pytest 독립검증·construction-site 정독으로 Pyright FP 기각·푸시·원장) + Engineer(페이지네이션 구현·테스트 23종) / **backend** / M3. 5커밋 dffcde0..f4a594b.
- **1줄 rollup**: legal-pro Phase B(사건관리 화면) 차단요인 중 **읽기측 해제**. 감사 결과 `GET /cases`·`GET /cases/{id}`(G-1)·`GET /documents`(G-3)는 **이미 구현돼 있었음**(Growth-100 포함) — 재구현 회피. 신규는 **G-4 페이지네이션**만: `GET /cases` 에 `limit`/`offset`(기본 50/0·최대 200) + COUNT(*) 진짜 total, `POST /search` 에 `offset`(기본0·≤500, RRF **후** 슬라이스로 랭킹·인용 1:1 불변). 전부 `rls_session`(app_user) 내 실행, 슈퍼유저 bypass 없음. **쓰기측(`POST/PATCH /cases`=G-2)은 Q-1(사건 CRUD 범위) 미확정에 의도적 보류** — list_cases docstring TODO.
- **검증/진단**: **pytest tests/ 211 passed/11 skipped (CTO 독립 재현, 0 실패)**, 11 skip=postgres-mark DSN 게이트. Pyright "offset/limit 인자 누락"(api.py 444/720/722/742)은 **stale-line FP** — 실 construction site `CasesResponse(cases,total,limit,offset)`(464)·`SearchResponse(...,offset=eff_offset)`(758)은 전 필드 명시, 모델은 `Field(0)`/`Field(50)` 기본값 보유(필수는 total). 진단 라인은 engineer 편집 중간상태 기준(720/722/742는 현재 log_query/CitationOut 위치). 테스트의 possibly-unbound FP 는 기존 lazy-import 패턴. embed-adapter 수집에러는 무관 기존파일(9bfaa12).
- **문서 환류**: D2 §9 갭표 동기화 후속(G-1 기구현·G-3 no-gap·G-4 해소·G-2 Q-1 보류) — 소규모 follow-up. 메모리 [[legal-unified-product-docs]].
- **Open loops**: G-2 쓰기(`POST/PATCH /cases`)=Q-1 사건 CRUD 범위 PM/founder 확정 선행 · legal-pro Phase B 사건화면(읽기 endpoint 준비됨, 프런트 위임 가능) · 페이지네이션 RLS 격리 라이브 실행=founder(postgres-mark) · D2 갭표 동기화. [[legal-rag-mvp-build]]

### Growth-104 — legal-pro Phase B 사건관리 read 화면 (기획 스펙 → 구현)

**맥락**: founder 가 A안(Phase B 프런트) 택함 + "legal-rag 때 적용한 기획단계 문서 작성하고 진행". D1~D5(제품 전체)는 이미 있어 0부터 재생성은 낭비 → **Phase B 구현 슬라이스용 빌드 스펙**을 PM 산출(D1~D5 관련 단면을 구현 계약으로 응축).

**기획 (PM, e101cbd)**: `docs/projects/legal/phase-b-spec.md` — CasesScreen(목록·페이지네이션) + CaseDetailScreen(상세·문서목록) read-only. 데이터 바인딩 표를 라이브 `api.py` CaseOut(8필드)/CaseDetailResponse(9필드)/CaseDocumentItem(4필드)와 1:1 정합(**CTO 독립검증 — 추측 0**). 생성/수정(G-2)은 Q-1 보류 out-of-scope 명시. 보존계약 4종(RLS·G-4·citation 1:1·middle 읽기전용) + AC-01~10. README §5 Phase B 를 read(차단해소·구현중)/write(Q-1보류) 분리(e9c4b9e).

**CTO 가 OQ 확정**: page size limit=20 / 전체 라우트 전환 / `?case_id=` query-param / 파트너캡션 제외(JWT claim 부재).

**구현 (engineer, 45c2bb9..a3057c8, 5커밋)**: wire.ts(apiListCases/apiGetCase) · CasesScreen · CaseDetailScreen · App.tsx(라우트·탭) · PrecedentSearchScreen(`?case_id=` 최소연결). L3 `npm run build` PASS(40 modules, CTO 재현 807ms). AC-01~10 코드 충족.

**가드 발동 — stale 진단 + 눈속임 의심 2건 다 CTO 직접 기각**:
1. 빌드 직후 LSP 가 App.tsx(CasesScreen/CaseDetailScreen/useLocation never read)·PrecedentSearchScreen(useSearchParams/selectedCaseId never read) 5건 "unused" 경보 → **소스 직접 읽어 전부 사용 확인**(144/152/50행, 244/299행). 편집 중간 스냅샷 stale FP. [[subagent-cross-service-verify]] 패턴 재현.
2. case_id 연동이 프런트만이고 백엔드 미필터면 "사건필터" 뱃지가 눈속임일 위험 → `api.py:712` 가 `hybrid_search(case_id=req.case_id)` 로 **검색 자체를 사건범위로 필터**(로그도 727행 기록) 확인. 연동 실제.

**revenue**: M3(법무 첫 버티컬) flagship 진전. **cost**: API 미사용(로컬 build·소스검증만). 잔여: L4 라이브(dist→Coolify 배포), 페이지네이션 라이브 단언(시드 ~6건/변호사라 20페이지서 미발화), G-2 write=Q-1 선행, 원문 drawer=G-3.

### Growth-105 — legal-pro L4 배포 준비 (전략 A: /pro 동일오리진) + Dockerfile 결함 가드

**맥락**: founder "배포부터". DevOps 가 서빙전략 + 설정 산출.

**전략 A (DevOps 권고·CTO 승인)**: legal-rag FastAPI 가 `/pro` 에 legal-pro dist 를 StaticFiles 로 추가 서빙(api.py:880 조건부 `if os.path.isdir`, 기존 `/app` 패턴과 일관). **동일 오리진 → CORS 0**, 새 서브도메인·Traefik 라우터 불필요. vite `base=/pro/` + BrowserRouter `basename=/pro` 정렬. multi-stage Dockerfile(Node20 build stage → dist 를 web/pro 로 COPY).

**가드 발동 — 배포 깨질 결함 CTO 적발**: DevOps 1차 산출(5커밋)이 **build 재검증 없이** 끝났고, Dockerfile Stage 1 이 어댑터를 `/src` 에 직접 COPY → prebuild(codegen/build-tokens)의 `REPO_ROOT=resolve(__dirname,'..'×4)` 가 `/` 로 해석 → `/middle`·`/presets`·`/services/legal-rag/web/styles` 부재 → **컨테이너 빌드 실패**. 로컬 `npm run build` 는 PASS(repo 경로 존재)라 founder 가 Redeploy 눌렀을 때만 깨지는 함정. CTO 가 REPO_ROOT 손계산 + prebuild 경로참조 grep 으로 근본원인 확정 → DevOps 에 repo-레이아웃 보존 COPY 구조 지시 → 수정(6aae618: 어댑터를 `/src/frontend/adapters/legal-pro` 에 두고 REPO_ROOT→`/src`, 의존 서브트리 3종 COPY). .dockerignore 가 그 경로 미배제 확인. 교훈: **빌드설정 변경은 변경한 환경(컨테이너)에서 재현해야 — 로컬 PASS 가 컨테이너 PASS 를 보장 안 함**. [[subagent-cross-service-verify]] 의 "thin wrapper 보고 단정 금지" 와 짝.

**라이브 트리거 경계**: 외부 API/SSH 금지(founder 룰) → DevOps 산출 = 로컬설정+절차문서+커밋까지, 실제 Coolify Redeploy 는 founder 실행. 절차: `deploy/preview/legal-pro.md`. **cost**: API 미사용. **revenue**: M3 flagship 데모 라이브화 직전. 잔여: founder Redeploy → `/pro` 스모크(7항목) → 통과 시 L4 종결.

### Growth-106 — legal-pro G-2 사건 쓰기: Q-1 확정 + C1(사건 메타 CRUD) 구현
- **Q-1 확정**(founder): 사건 쓰기 범위 = 사건+당사자+문서첨부, 삭제 영구배제(법적 감사), 생성자=담당변호사 본인. 원문보기(G-3)는 phase 2.
- **DDL/RLS 선완비 발견**: `02/04/05_*.sql` 에 case/case_party/case_document app_user INSERT·UPDATE RLS 정책 이미 존재 → G-2는 API 레이어만 추가(신규 DDL 0). 문서는 append-only(UPDATE/DELETE 정책 부재).
- **PM 빌드스펙** `docs/projects/legal/g2-write-spec.md`: 3 sub-phase(C1 메타/C2 당사자/C3 문서첨부+비동기ingest) 독립머지, AC-01~12(RLS 음성 4종 포함), CISO 업로드 게이트.
- **C1 구현**(engineer, 9커밋 381d5da..1226d61): `POST /cases`+`PATCH /cases/{id}`(api.py, rls_session SET LOCAL·assigned_attorney_id 서버주입·404 존재은폐) + CaseCreate/EditScreen + wire.ts + 라우트(/cases/new·:id/edit 정적우선) + 진입버튼. AC-01 PASS(pytest 244·npm build 0err). RLS 라이브 AC는 @pytest.mark.postgres 보류(founder DSN 게이트).
- **CTO 가드**: (a) 엔지니어가 DDL 불일치 보고(case_type CHECK에 other 없음) → 스펙 정합 수정(OQ-12). (b) 엔지니어가 API↔DB 실컬럼 교정(description→summary, opened_at→filed_date). (c) diagnostics 대량 발생했으나 전부 확정 FP(pydantic Field기본값·lazy import·stale never-read), App.tsx 라우트 실연결·RLS 주입 직접 소스검증.
- **CTO 판정**: OQ-11(party 노출) = C2에서 CaseDetailResponse에 parties 가산(additive, documents 패턴).
- 다음: C2(당사자 CRUD) → C3(문서첨부+ingest, CISO 게이트). C1 라이브 RLS AC는 founder DSN 실행.

### Growth-107 — legal-pro G-2 C2(당사자 parties CRUD, PII) 구현 + CTO 회귀 적발

- **범위**: G-2 sub-phase C2 — 당사자 등록/수정. `POST /cases/{case_id}/parties`·`PATCH /cases/{case_id}/parties/{party_id}` + 신규 `CasePartyOut`/`CasePartyCreateIn`/`CasePartyUpdateIn` 모델 + `CaseDetailResponse.parties` 가산(OQ-11 additive) + CaseDetailScreen 인라인 PartyPanel + wire/codegen. engineer 7커밋(86d1d0a..acffa0c).
- **DDL 선완비**: 05_case_party_rls.sql(RLS-only augment)에 select/insert/update 정책 이미 존재, role CHECK = plaintiff/defendant/witness/opposing-counsel/expert-witness. 신규 DDL 0.
- **CTO spec-vs-DDL 판정**: 스펙 name 256자·notes 2000자 → 렌더 컬럼 VARCHAR(255) 초과. C1 case_type 'other'와 동형, **DDL 충실하게 name·notes 255 cap** 확정(catalog `string` maxlen 미지정→렌더 기본 255, postgres 빌드 미체크인). pydantic max_length=255.
- **PII RLS→404 존재은폐 경계(CTO 직접 소스검증)**: create_party = RLS INSERT WITH CHECK EXISTS(legal_case 소유) 위반 → psycopg 예외 "policy" 매칭 → 404(타 변호사는 부모 case 비가시→EXISTS false→위반). update_party = RLS UPDATE USING 조용히 0행 + 이후 SELECT None → 404. 양쪽 사건·party 존재 은폐 확정.
- **CTO 회귀 적발(핵심)**: 엔지니어가 C1+C2 테스트 파일만 돌려 "70 passed" 보고했으나, CTO 전체 스위트 재현 → **2 fail**. get_case_detail에 parties SELECT(3번째 execute) 추가가 Phase B `test_case_detail_endpoint.py` 깨뜨림 — (a) mock 미갱신으로 `notes=pr[4]` IndexError, (b) "필드 불변" 단언이 새 parties 필드 미반영. **프로덕션 코드는 정상**(실 SELECT 5컬럼), 테스트 픽스처 staleness. 동일 엔지니어 재디스패치 → acffa0c 수정(parties fetchall mock + 필드셋 가산 + parties 라운드트립 단언). CTO 재현 **281 passed/17 skipped/0 fail**.
- **diagnostics 전부 확정 FP**: wire.ts party_create 미존재(실제 contract.gen.ts:19-20 존재)·CaseDetailScreen PartyPanel/handleRefresh never-read(line 568 렌더링·466 사용)·pydantic Field/lazy import possibly-unbound — npm build 0 error·pytest green로 교차확인.
- **하드닝 노트(향후)**: create_party 예외 substring 매칭("check"/"permission")은 pydantic 선검증 덕에 안전하나 psycopg SQLSTATE 42501(InsufficientPrivilege) 타입 캐치가 더 견고.
- **교훈**: 엔지니어 self-test 범위가 변경 파일에만 국한되면 cross-file 회귀를 놓침. CTO 게이트는 **반드시 전체 스위트 재현** — envelope의 "N passed"를 부분 스위트로 신뢰 금지. [[subagent-cross-service-verify]] 연장.
- 다음: C3(문서첨부+비동기 ingest, CISO 게이트) → 그 후 phase 2 G-3(원문보기). C2 라이브 RLS AC-05~07은 founder DSN 실행(@pytest.mark.postgres).

### Growth-108 — legal-pro G-2 C3(문서첨부+비동기 ingest) CISO 게이트 통과 + 푸시

- **범위**: G-2 sub-phase C3 — `POST /cases/{case_id}/documents`(멀티파트 업로드 → INSERT-before-write → FastAPI BackgroundTasks 비동기 ingest). engineer 9커밋(5bd1da9..c1c4047) + CTO 후속 4커밋(69d057e..544030f). config.storage_root·_sanitize_filename·_build_storage_key(uuid 접두 ≤255)·realpath+commonpath 경로방어·CaseDetailScreen DocumentUploadPanel(AC-11 5s 폴링)·python-multipart 의존성.
- **CTO 설계 정련**: 스펙 대비 INSERT 먼저(rls_session) → 파일 디스크 쓰기 순서. RLS 거부 시 고아 파일 0. 비동기 ingest는 fresh app_service(BYPASSRLS) 커넥션(요청 핸들러 커넥션 재사용 금지) + 예외 시 별도 커넥션으로 status=error(column-scoped grant 내).
- **CTO 잠복결함 적발(cross-cutting)**: 09_grants.sql에 app_user가 GRANT SELECT만 보유 — legal_case/party/document INSERT·UPDATE grant 부재. Postgres는 RLS 평가 前 table privilege 검사 → C1/C2/C3 쓰기가 실DB에서 "permission denied"로 전멸. 라이브 AC가 founder DSN 게이트(미실행)+유닛 mock이라 가려짐. dba-agent가 3 GRANT 추가(64e2480, 별도 푸시), document는 INSERT-only(append-only 04 정합).
- **CISO 게이트(PASS, BLOCK 0)**: `docs/projects/legal/security/c3-upload-review.md`. 경로탐색 이중방어·확장자(x.pdf.exe→거부)·RLS 404 존재은폐·BackgroundTask 격리·외부egress 0 PASS. CAVEAT 4건 중 **2건 본 패스에서 해결**: D(substring→psycopg 타입캐치 SQLSTATE 42501, 69d057e) + G(python-multipart>=0.0.18 CVE-2024-53498, ace99cb). A(file.read 무제한 OOM)·AC-12(영구볼륨)→deploy/legal-pro.md §9 배포가이드(544030f). C(magic bytes 미검증, Low)→보류.
- **CAVEAT-D 환류(C1/C2/C3 3회 반복 가드의무)**: RLS 위반 판별을 예외 메시지 substring("policy"/"check"/"rls"/"permission")에서 `psycopg.errors.InsufficientPrivilege`(42501) 타입캐치로 교체 — CHECK제약(23514) 오탐 제거. create_case(Unique→409, 42501→403)·create_party·upload(42501→404). psycopg.errors는 ModuleNotFoundError 폴백(prod 항상 존재).
- **CTO 검증 함정 2건**: (a) 직전 세션 CTO pytest "No tests collected"는 **영속 cwd가 services/legal-rag**라 rootdir 오판 — 올바른 디렉터리에서 313 passed/19 skipped 재현(이후 subshell `(cd …)`로 cwd 보존). (b) 같은 영속 cwd가 상대경로 PreToolUse 훅(large_file_guard/output_filter)을 깨뜨려 Bash/Read 데드락 → **PowerShell Set-Location으로 공유 세션 cwd 리셋**해 복구(메모리 subagent-cwd-hook-fragility 재현, 메인세션도 영향). 교훈: Bash `cd X &&`는 영속 — 항상 subshell 또는 절대경로.
- **검증**: CTO 전체 스위트 재현 **313 passed / 0 fail / 19 skipped**(타입캐치 후 회귀 0). 라이브 RLS AC-08/AC-10(@pytest.mark.postgres)은 founder DSN+STORAGE_ROOT 게이트.
- 다음: **phase 2 G-3 원문보기** — founder가 "원래 되던 기능(구 /app openDocDrawer)"으로 지적. 백엔드 `GET /documents/{source_type}/{source_id}`(api.py:1587) + `.doc-drawer` CSS 완비, React 어댑터 wire/컴포넌트만 미배선(PrecedentSearchScreen alert 스텁). 판례(full_text)는 즉시 동작 가능, 사건문서(content_text)는 OQ-10 의존. C3 라이브 AC·Coolify 영구볼륨은 founder.

### Growth-109 — legal-pro G-3 판례 원문보기 드로어 React 재배선 + 푸시

- **범위**: phase 2 G-3 — founder가 "원래 되던 기능인데 안붙어있다"로 지적한 판례 원문보기. 구 vanilla SPA(`/app` web/app.js openDocDrawer)가 React 어댑터 이관 시 `alert(...)` 스텁으로 회귀한 것. engineer 3파일(e11e869 DocDrawer 신규 / 863e9cb wire / b047399 PrecedentSearchScreen). 백엔드 `GET /documents`(api.py:1587)·`.doc-drawer__*` CSS는 완비 상태라 미변경, React wire/컴포넌트/버튼만 배선.
- **구현**: (1) wire.ts `apiGetDocument` — `LEGAL_RAG_ENDPOINTS.document_read` 상수 치환(encodeURIComponent)+Bearer(legalRequest 경유), `DocumentReadOut`는 백엔드 `DocumentResponse`(api.py:283) 12필드 1:1 미러, legalRequest에 404→`code='NOT_FOUND'` 분기 추가(기존 INTERNAL 덮어쓰기 수정). (2) DocDrawer.tsx 신규 — loading/error/success 3상태, 404 전용 메시지, ESC·백드롭 닫기, is-open 트랜지션, 판례 메타행+holding fallback 뱃지, case_document body 미충전(OQ-10) 안내. (3) PrecedentSearchScreen — alert 스텁 제거→drawerTarget state+openDrawer/closeDrawer, CitationCard에 onOpenDrawer 전달, DocDrawer 조건부 렌더.
- **CTO 통합검증(envelope 독립검증)**: engineer가 "build PASS"라 보고했고 IDE 진단은 `onOpenDrawer` 미배선/미사용을 표시(stale, 편집 중 스냅샷 — 라인번호도 최종본과 불일치). **직접 4중 확인**: ① 실제 파일 read로 렌더구역 배선 확인(491·499-505) ② `npm run build` 재실행 → tsc 0 err·vite 43 modules PASS ③ 백엔드 DocumentResponse 12필드 ↔ DocumentReadOut 1:1 grep 대조 ④ `.doc-drawer__*` 13클래스 tokens.gen.css 실존 grep 확인. 전부 정합. [[subagent-cross-service-verify]] 적용 — envelope "build PASS"도 stale 진단과 충돌 시 재현 필수.
- **결과**: 판례(full_text) 즉시 동작 = "원래 되던 기능" 회복. 사건문서(content_text) 원문은 OQ-10(content_text 충전) 의존 보류 — DocDrawer는 양 source_type 일반화, case_document 빈본문 시 안내문. CaseDetailScreen 사건문서 버튼(aria-disabled) 미변경.
- 다음: 라이브 검증은 founder Coolify Redeploy(C3+G-3 동반 반영, STORAGE_ROOT=/data/legal-docs/case-uploads 기존 영구마운트 하위로 설정 완료) 후 `/pro/search` 원문보기 스모크. C3 라이브 RLS AC·STEP3 업스트림 바디제한(Traefik buffering, CAVEAT-A)은 founder/후속.

### Growth-110 — legal G-2 C3 라이브 첫 배포 3갭 해소 (문서업로드 end-to-end LIVE)
- 트리거: founder 라이브(/pro) 테스트에서 G-2 쓰기 4건 실패 → CTO 코드 핑거프린트 진단. **코드는 정상, 전부 배포환경 갭 3개**.
- 갭1 **DB grant 미적용**: 09_grants.sql INSERT/UPDATE(L27-29) 라이브 미반영(앱 Redeploy는 DDL 미실행 — DDL-in-repo≠live-DB). 증상 사건생성403(api.py:828)/당사자추가404(1038)/당사자수정500(update_party는 42501 catch 無). 확증: role_table_grants에 app_user의 query_log INSERT만 존재. 수정: Coolify db Terminal서 GRANT 6줄 한줄씩 재적용(웹터미널 heredoc 깨짐 → -c 분리).
- 갭2 **compose passthrough 누락**: app environment에 LEGAL_RAG_STORAGE_ROOT 매핑 부재 → 컨테이너 미주입 → 500(api.py:1273). 수정 커밋 e5d7dd9.
- 갭3 **bind-mount 비-root 쓰기**: appuser(Dockerfile:67) vs root소유 /data/legal-rag/ingest → 파일쓰기 except 500(api.py:1338-1355). 수정: 호스트 `mkdir+chmod 0777 case-uploads`(preview; prod는 chown UID+0750). redeploy 불요·존속.
- 환류: 런북 deploy/preview/legal-pro.md §9 재구성(b6353c4). compose 패스스루 e5d7dd9/3eae1a3.
- 결과: founder 4건 전부 라이브 PASS. 문서 pending→done(폴링 5회=정상). 인격: CTO 진단·integrator, DevOps 런북·compose(위임), CISO 0777 preview-caveat.
- §6 rollup: [Growth-110] G-2 C3 라이브 3갭(grant/compose-env/bind-perm) 해소 → 문서업로드 LIVE. → docs/learn-logs/{devops,security}.md

### Growth-111 — legal-pro G-3 판례 원문보기 라이브 스모크 PASS (phase 2 종결)
- 트리거: founder Redeploy 후 `/pro/search` 판례검색 → [원문 보기] 라이브 확인 = "정상적으로 보인다". Growth-109 React 재배선(DocDrawer/wire/PrecedentSearchScreen)이 실배포에서 동작 확증.
- 결과: **phase 2 G-3 end-to-end 종결** — 판례(full_text) 드로어 즉시 표시 = 구 vanilla `/app openDocDrawer` 기능 React 어댑터(`/pro`)에서 완전 회복. 사건문서(content_text) 본문은 설계대로 OQ-10(content_text 충전) 의존 보류, DocDrawer 안내문 표시.
- 라이브 검증 0추가 코드 — Growth-109 재배선 + Growth-110 동반 Redeploy로 이미 반영. founder 스모크가 최종 게이트.
- 잔여(후속·founder 게이트): 라이브 RLS AC(AC-08/10, founder DSN @pytest.mark.postgres)·STEP3 Traefik 바디제한(CAVEAT-A, prod 전 필수)·OQ-10 case_document content_text 충전·prod bind-mount 하드닝(chmod 0777→chown UID+0750).
- §6 rollup: [Growth-111] G-3 원문보기 `/pro` 라이브 PASS → 통합 법무제품(G-2 쓰기 + G-3 원문보기 + 판례 RAG검색) end-to-end LIVE.

### Growth-112 — lawfirm-demo 메인 데모 격상: 4도메인 가상 데이터 + 포털 카드 재포지셔닝
- 방향(founder): lawfirm-demo(법무법인 전반 업무 메뉴)를 **메인 데모**로, legal-pro(`/pro` RAG)는 **killer app 링크**로. 포털 법무 카드 1장 + lawfirm-demo 내부 양쪽(배너+메뉴) 크로스링크. 두 앱은 물리적 별개(다른 배포·DB·로그인)임을 정직 표기.
- 포털 카드: 이미 repo 커밋됨(8dcbf8d)이나 demo-portal 미배포로 라이브 부재 → 문구 강화(통합 업무관리+AI 판례검색 부각, 358e52e). founder Redeploy 시 반영.
- B1 데이터(DBA 위임): 14테이블 4도메인(legal/hr/document/approval) 스키마 전부 존재·데이터만 공백 확인. 가명 30인 법무법인 증분 시드 `scripts/demo/seed_lawfirm_full.py`(신규 1083줄) + setup_lawfirm.py importlib 연동. 부서5/직원14/판례12/사건10/당사자28/사건문서22/카테고리6/문서10/버전14/접근규칙8/결재요청7/단계13/결재자14/결정10. 멱등(ON CONFLICT DO NOTHING), 컬럼은 out DDL 1:1.
- **CTO 게이트 결함 적발**: DBA가 `py_compile PASS`로 보고했으나 Pyright 진단이 `_E3` 미정의 노출. py_compile은 문법만 검사 → module-level dict 평가 시 NameError로 시드 전멸. `_E3`→`_EMP3`(베이스 직원) 수정 + **실제 import 검증**(모든 모듈스코프 리터럴 평가) 재게이트 통과. 교훈: 시드/리터럴 스크립트 검증은 py_compile 불충분 → import 실행 필수. [[subagent-cross-service-verify]] 연장.
- 라이브 적용은 founder(`DATABASE_URL=... python scripts/demo/setup_lawfirm.py`, no-SSH/API 경계).
- 다음: B2 killer-app 링크(배너+메뉴) → D1~D5 문서(데이터 기준) → DFD 검증 → 영업/인도물 패키징.
- §6 rollup: [Growth-112] lawfirm-demo 메인 데모화 — 4도메인 가상데이터 시드 + 포털 카드 강화(killer app legal-pro 부각).

### Growth-113 — lawfirm-demo killer-app 크로스링크(B2): env 구동 배너+사이드바 양쪽

- **B2 완료**: lawfirm-demo 화면 상단 배너 + 좌측 메뉴 양쪽에 "AI 판례검색 ↗" 링크 → legal-pro(`legal-rag.n9n.co.kr/pro`). founder "양쪽" 요구 충족.
- **개방-폐쇄 설계**: base.html(전 데모 공유) 하드코딩 대신 `KILLER_APP_URL` env 구동 조건부(기존 MASTER_DETAIL_ENTITIES env 패턴 답습). lawfirm-demo compose env에만 배선 → 그 데모에만 노출, 타 데모 무영향. 향후 타 프로파일도 env 한 줄 재사용. 4커밋(server 59e20da/base cbf8953/css d5c13c6/compose 602c6b9).
- **정직 표기**: target=_blank rel=noopener + "외부 시스템 · 별도 로그인 필요"(SSO 아님 — 물리적 별개 배포·DB·로그인).
- **CTO 게이트**: engineer 산출 독립 검증 — server.py g_killer_app(인증 한정·미설정 None) 정확, base.html 삽입 위치 정확, app.css 참조 토큰 전부 tokens.css 실존 확인(--color-primary-subtle/--color-text-on-primary 등), AST+Jinja PASS. 표시된 Pyright 진단은 기존 Flask 타입 쿼크(무관).
- engineer 보고 KILLER_APP_URL 후보가 루트(`/`)였으나 CTO가 killer app 실체=legal-pro `/pro`로 정정 배선.
- **founder 액션**: lawfirm-demo Coolify Redeploy → 배너/사이드바 라이브. (env는 compose에 배선됨 — 수동 입력 불요)
- §6 rollup: [Growth-113] lawfirm-demo killer-app 크로스링크(B2) — env(KILLER_APP_URL) 구동 배너+사이드바 양쪽, legal-pro /pro 연결. B2 종결, D1~D5 문서 단계 진입 대기.

### Growth-114 — lawfirm-demo D1~D5 문서 5종 + DFD 검증(결함 1 적발, BLK-D5-8)

- **D1~D5 전 문서 완성**(docs/projects/lawfirm-demo/): D1 기능명세(402)·D2 유저플로우(503)·D3 와이어프레임(439)·D4 ERD(552)·D5 DFD(724). 전부 **실제 시드 데이터 + 실제 server.py 라우트 + 실제 out DDL 기준**, killer-app 경계(별개 DB·SSO없음) 정직 표기. 3중용도(영업·인도물·구현입력).
- **CTO 독립 게이트 전건 수행**: D2 라우트 ↔ server.py 1:1, D4 ERD의 FK·ON DELETE 정책 ↔ out DDL **정확 일치**(assigned_attorney_id RESTRICT, principal_id/subject_id 다형+UNIQUE/인덱스, CASCADE/RESTRICT/SET NULL), D3 셸 ↔ base.html(g_killer_app 조건부) 정합. 날조 0.
- **DFD 검증(QA)**: D5 34 검증포인트 정적 감사(seed↔DDL). scripts/demo/dfd_verify.py(160줄, 외부DB 불요 import 검증) rc=0, 시드 FK 무결성 전항목 OK. 25 PASS / 1 FAIL / 9 N-A(인증·런타임 → founder 라이브검증 이관).
- **DEFECT-1(CTO 확인)**: `presets/ddl/catalog.yaml:1349` approval-decision.step_id `on_delete: restrict` ↔ 부모 체인(approval-step.request_id cascade:1309, approver.step_id cascade:1329) 불일치 → decision 존재하는 결재요청 삭제 시 cascade가 RESTRICT 리프에서 막혀 FK 위반. generic baseline catalog 결함. **수정 방향은 설계 판단**(cascade-all 단순화 vs decision 불변성 audit). 데모엔 cascade 권장(1줄+regen). QA BLOCK 정당.
- **flaky 교훈**: design-agent 대용량 단일 Write 2회 stream-idle timeout → 읽기 2개 한정+≤350줄 집약 지시로 3회차 성공(439줄). 큰 산출 서브에이전트는 입력·분량 타이트 제약이 안정적.
- **founder 액션**: ① DEFECT-1 수정 방향 결정 ② demo-portal/lawfirm-demo Redeploy ③ 시드 라이브 적용. 잔여: DEFECT-1 fix+regen, 패키징(영업/인도물).
- §6 rollup: [Growth-114] lawfirm-demo D1~D5 문서 5종 완성(실데이터 기준·CTO 게이트 전건) + DFD 정적검증(dfd_verify.py, 25P/1F/9NA) — DEFECT-1(approval cascade 불일치, catalog:1349) 적발·BLOCK. 패키징·fix 대기.

### Growth-115 — DEFECT-1 수정: approval-decision CASCADE 통일 + 회귀 가드 강화 (BLK-D5-8 RESOLVED)

- **founder 승인**: "CTO 의견에 동의" → DEFECT-1 cascade 수정 착수.
- **근본 위치는 catalog**: out DDL 직접수정이 아니라 `presets/ddl/catalog.yaml` approval-decision 엔티티 수정(단일 진실, regen 산출). 복리식 축적 — 전 프로파일 재발 방지.
- **CTO 게이트가 최초 QA 권고를 정정**: D5 보고서 초안 권고는 "step_id 만 CASCADE, approver_id 는 RESTRICT 유지(approver 단독삭제 방지)"였으나 **체인을 완전히 못 푼다**. catalog 정의순서상 approval_approver 가 approval_decision 보다 먼저 생성 → PG 가 approval_step cascade 시 approver 를 먼저 삭제 → 그 시점 살아있는 decision.approver_id RESTRICT 즉시 발동 → 재차단. 따라서 **두 FK 모두 CASCADE**(CTO 원안 "cascade 로 통일"과 일치). 서브에이전트(QA)/문서의 권고도 CTO 독립검증 대상이라는 [[subagent-cross-service-verify]] 패턴 재확인.
- **수정 3파일**: ① catalog.yaml step_id+approver_id restrict→cascade(5639a8f) ② dfd_verify.py VP-P8-07 가드 강화(0faaae4) ③ DFD 보고서 BLOCK→PASS(99e7433). out DDL 은 scaffold.py regen(gitignored).
- **회귀 가드 교훈**: 기존 VP-P8-07 은 `'ON DELETE CASCADE' in DDL` 부분일치 → DEFECT-1 을 **스크립트가 못 잡았다**(보고서 FAIL 은 QA 수동판정). approval_decision CREATE TABLE 블록 파싱해 두 FK 모두 CASCADE 직접확인하도록 교체. 약한 substring 가드 = false PASS 위험 패턴.
- **재검증**: `dfd_verify.py` rc=0, RESULT PASS=35 / FAIL=0 / N-A=9. VP-P8-07 PASS.
- **guard 노트**: diagnose.py G-8/G-9/G-12 FAIL 은 선존(G-12 위반=document-chunk/rag-query-log 엔티티, approval 무관). 내 변경은 fk 마커 보존·on_delete 값만 변경 → G-12 무영향 확인.
- **잔여**: 패키징(PM/CMO 영업·인도물), 9 N-A 라이브검증(founder Redeploy 후).
- §6 rollup: [Growth-115] DEFECT-1 수정 — catalog approval-decision 두 FK CASCADE 통일(QA 초안권고 CTO 정정: approver_id 도 cascade라야 체인 무결) + VP-P8-07 회귀가드 강화. dfd_verify rc=0/35P·0F. BLK-D5-8 RESOLVED.

### Growth-116 — lawfirm-demo 패키징: 인도 README + 영업 원페이저 (PM/CMO 병렬)

- **잔여 1 패키징 종결**: lawfirm-demo 메인데모 인도 패키지 2종 산출. PM/CMO 병렬 위임(다른 파일 → 충돌 없음).
- **PM**: `docs/projects/lawfirm-demo/README.md` — D1~D5+검증보고서 6문서 인덱스 표, 3페르소나(CEO/업무담당자/IT)별 관심문서 안내, 메인데모↔legal-pro 관계도(ASCII)+정직성 경계(별개 배포·DB·SSO아님), 구 `docs/delivery/lawfirm-demo/`(FTS 단독) 포함·확장 관계, founder Redeploy 잔여액션, 보안경고(CAVEAT-A Traefik 바디제한).
- **CMO**: `docs/projects/lawfirm-demo/sales-onepager.md` — 핵심 가치제안, 페르소나별 베네핏, self-host vs SaaS 비교표, 5분 영업 데모 스크립트(4도메인 순회→killer-app 핸드오프), 정직 고지 인라인(생성형 아님·SSO 미지원).
- **CTO 게이트(독립 소스검증)**: ① README D1~D5+검증보고서 링크 6건 전부 실존 ② 시드 수치·DFD결과(PASS=35/FAIL=0/N-A=9) 정확 ③ CMO 마케팅 주장 `GET /health` 의심→`frontend/adapters/vanilla-htmx/server.py:735` 실존 확인(날조 아님) ④ 판례 드로어·하이브리드 검색 모두 기실현 기능. 날조 0.
- **교훈**: 마케팅 산출물의 기능 주장은 [[subagent-cross-service-verify]]대로 CTO가 소스 1건씩 확인(/health 실존 검증). 영업 카피라도 검증가능성이 신뢰자산.
- **잔여**: 9 N-A 라이브검증(인증·런타임) — founder가 demo-portal/lawfirm-demo Redeploy + 시드 라이브 적용 후. (코드/문서 측 lawfirm-demo 메인데모 트랙 종결, 이후는 founder 게이트)
- §6 rollup: [Growth-116] lawfirm-demo 패키징 종결 — 인도 README(PM)+영업 원페이저(CMO) 병렬 산출, CTO 게이트 전건(링크 실존·시드수치·/health 소스확인). 잔여=founder Redeploy 후 9 N-A 라이브검증.

### Growth-117 — lawfirm-demo 라이브 시드 배선: SEED_FILE 경로(in-memory 백엔드 적재)

- **stale 가정 적발(CTO probe)**: "#3 시드 라이브 적용 = `DATABASE_URL=... setup_lawfirm.py`"는 부정확. 소스 확인 결과 라이브 lawfirm-demo(Coolify)는 저장소 2분리 — business 엔티티(사건/문서/결재)=백엔드 `InMemoryEntityStore`(SEED_FILE json 또는 wire), 판례검색=`legal.py`→postgres. **라이브 compose엔 postgres·DATABASE_URL·SEED_FILE 전무.** demo/demo 직접 로그인 probe로 `/entities/legal-case` 0건·`/legal/search` "결과없음" = 양 스토어 빈 셸 확정. founder가 Coolify Environment 탭 확인 → DATABASE_URL/SEED_FILE 미설정 교차확인.
- **경로 결정**: Option A(SEED_FILE) 채택. B(lawfirm-demo 자체 postgres 판례 FTS)는 **killer-app(legal-pro, LIVE)이 AI 판례검색을 이미 커버 → 중복**이라 생략. 데모 흐름의 판례검색=legal-pro 핸드오프.
- **기존 인프라 재사용**: `seed-data/*.json`(7개 데모 선례) + Dockerfile이 `seed-data/`→`/app/seed-data/` 굽음(line33) + `store._load_seed_file`(SEED_FILE env). **빠진 건 lawfirm-demo.json 하나뿐.** scp·bind-mount 불요(이미지 빌드시 베이크) → founder Redeploy만.
- **engineer 산출(3파일)**: ① `scripts/demo/gen_seed_lawfirm_json.py` 생성기(base+new 14엔티티 직렬화, 건수 self-assert, 멱등, 실제 import 검증) ② `seed-data/lawfirm-demo.json` 173건 ③ compose backend `SEED_FILE` env. 6ad481c/c09b018/10b8c2c.
- **CTO 게이트(독립 검증, envelope 불신)**: entity_type 키 manifest 14개 1:1, id 전건 유니크, 레코드 필드 manifest 부합, **FK 무결성 11종 dangling 0**(legal-case.assigned_attorney_id·case-party.case_id·approver.step_id·approval-decision.approver_id·document.current_version_id 등), `store._load_seed_file` 독립 dry-run 173건 무경고. Pyright 진단 4건(importlib Optional None-access)→`sys.path` import 패턴(dfd_verify 동일)으로 정리.
- **교훈**: manager_id/current_version_id처럼 **postgres POST-INSERT UPDATE로 채우는 값은 in-memory 스토어(UPDATE 없음)에선 최초 로드 시점에 backfill** 필수. postgres 시드 ≠ in-memory 시드(스토어 의미론 차이). [[subagent-cross-service-verify]]대로 FK 무결성·store 호환을 CTO가 직접 재현.
- **잔여**: founder lawfirm-demo Coolify Redeploy → 4도메인 라이브 데이터 확인 → 9 N-A 라이브검증.
- §6 rollup: [Growth-117] lawfirm-demo 라이브 시드 배선 — stale 가정(setup_lawfirm postgres) 적발·정정, Option A(SEED_FILE in-memory) 채택(B는 killer-app 중복 생략). 생성기+173건 json+compose env, CTO 게이트 FK 11종 dangling0·store dry-run 무경고. founder Redeploy 대기.

### Growth-118 — lawfirm-demo 라이브 종결: Redeploy + 9 N-A 라이브검증

- **founder Redeploy 완료**: 4도메인 라이브 데이터 렌더·legal-pro 링크 동작 확인. SEED_FILE 자동 적재 확증(CTO probe: /entities/legal-case 10행·/entities/approval-request 7행 approved4/in-progress1/pending1/rejected1).
- **9 N-A 라이브검증(CTO HTTP probe, demo/demo)**: 7 PASS — VP-P1-01 틀린비번 401+한글, P1-02 무세션 302, P1-03(proxy) 무효토큰 302, P1-04 로그아웃후 옛쿠키 302(서버세션무효화), P1-05 4도메인14엔티티+killer배너, P3-03 없는키워드 200+"결과없음"(에러아님), P5-04 ingest done→pending store.patch 무가드 허용(비파괴 소스검증). **2 N-A 유지**: P8-08/09 결재 워크플로 자동전이 — **generic CRUD에 상태머신 부재**(status 수동필드), 결함 아니라 business-system 산출물 범위. DFD 작성자 "app layer runtime" N-A와 일치.
- **정직 고지**: 실 결재 워크플로 전이 원하면 백엔드 커스텀 로직(별도 기능). 시드 다양상태로 데모 화면은 사실적.
- **검증 비파괴 원칙**: P5-04는 라이브 시드 훼손 회피 위해 store.patch 소스 의미론으로 검증(throwaway 레코드 주입 회피). founder가 막 데모 가동한 환경 존중.
- **lawfirm-demo 메인데모 트랙 완전 종결**: 정적 35 PASS + 라이브 7 PASS, 미해결 결함 0. D1~D5 문서·DFD·DEFECT-1 fix·패키징(README/원페이저)·라이브 시드·라이브검증 전부 완료. M1 generic harness baseline 기여.
- §6 rollup: [Growth-118] lawfirm-demo 라이브 종결 — Redeploy 후 9 N-A 라이브검증 7 PASS/2 N-A(워크플로 범위). 시드 라이브 확증(case10·approval7). 메인데모 트랙 완전 종결, 미해결 결함 0.

### Growth-119 — legal-rag pg_bigm 라이브 활성화 → OR `=%` 퇴행 적발·DROP 롤백 → OR→LIKE 재배선 + 테스트 사각 폐쇄

- **활성화 시도→퇴행 적발**: founder가 pg_bigm `CREATE EXTENSION`+인덱스+Redeploy 했더니 검색 키워드 뱃지가 **사라짐**. CTO 라이브 진단(psql): `chunk_text =% '손해배상'`(sim_limit 0.1)=**0행** vs tsquery=**22행**. 근본: retrieve.py OR+bigm이 `=%`(문자열 **전체** 유사도)를 써서 짧은쿼리 vs 긴 500토큰 청크에 구조적 0 → pg_bigm 켜면 OR이 tsquery보다 **퇴행**. Growth-99의 "한계효용 낮음" 경고가 실측으로 확인.
- **즉시 롤백**: founder `DROP EXTENSION pg_bigm CASCADE` + Redeploy → probe=False → tsquery 복귀(손해배상 22건·뱃지 회복). 볼륨 보존이라 extension 재생성 쉬움.
- **꼼꼼한 수정(engineer)**: OR/AND bigm 분기를 단일 `if use_bigm`으로 병합, 둘 다 `_build_bigm_like(query, op)`의 **LIKE 부분문자열 + bigm_similarity 랭킹** 사용(AND 분기가 이미 정답 템플릿이었음). LIKE는 한국어 토큰내부 부분문자열(손해배상금→손해배상)까지 잡아 tsquery보다 우위. 죽은 `_FTS_BIGM_SQL`·`_BIGM_SIMILARITY_LIMIT`·`SET LOCAL` 제거. 3커밋 df8862e/48ba7a2/32e446f 푸시.
- **★ 테스트 사각 폐쇄(핵심 교훈)**: `test_case_scoped_search`가 pg_bigm=False 강제라 **hybrid_search의 bigm 경로가 단위에서 한 번도 안 돌아** `=%%` 이스케이프(1차)·`=%` 의미론 퇴행(2차)을 둘 다 놓쳤다. ① `test_bigm_search_path.py`(신규) — `_BIGM_AVAILABLE=True` 패치+conn mock으로 OR/AND FTS SQL에 LIKE 포함·`=%` 부재 assert(8케이스, 회귀가드) ② `test_postgres_integration.py` — DSN 게이트 실 bigm LIKE OR ≥1행 검증. **mock-only 테스트는 라이브 경로를 못 잡는다 → 통합테스트로 실경로 게이트 필수**.
- **CTO 게이트(envelope 불신, 직접 재실행)**: retrieve.py 정독(병합분기 LIKE 정확·`=%` 실행코드 0=주석만), Pyright `_FTS_BIGM_SQL undefined` 진단은 stale(병합 중간상태) 확인, 단위 **321 passed/0 failed**, postgres 20 skip 클린(psycopg false-positive). `_build_or_tsquery` 잔존은 test_fts_or_tsquery가 import(죽은코드 아님).
- **인프라 함정**: 서브에이전트 pytest가 cwd≠repo root라 Bash 훅(상대경로 scripts/hooks) 데드락 → PowerShell 툴로 우회([[subagent-cwd-hook-fragility]]).
- **정직 한계**: "계약해지"↔"계약 해지"(띄어쓰기 복합어)는 LIKE로도 안 풀림(literal 부재) — 정규화 또는 ANN 영역. pg_bigm은 substring-in-token만 개선. 활성화 ROI는 Growth-99 판단대로 제한적.
- **잔여(founder 배포)**: extension 재생성(`CREATE EXTENSION pg_bigm`+인덱스) → legal-rag app Redeploy(코드변경=재빌드 필요) → OR "손해배상" 뱃지 회복+substring 우위 확인.
- §6 rollup: [Growth-119] legal-rag pg_bigm OR `=%` 퇴행(라이브 0 vs tsquery 22) 적발·DROP 롤백·OR→LIKE 재배선 수정 + mock 사각 폐쇄(bigm-path 단위+postgres 통합테스트). 321 passed. founder 재배포 대기. Growth-99 한계효용 경고 실증.

### Growth-120 — 큐드 태스크 관리 프리셋 3-Phase (협업 코어 + 칸반 + Lite-AI), 14커밋

- **발단**: 패션 인바운드發 큐드 결정([[queued-task-mgmt-preset]]) 착수. gate(deep-research salvage) clear. CTO 발견 — **greenfield 아님**: catalog `project` 도메인(task 상태머신·assignee·subtask 이미 존재) **확장**. founder 가 차별화 3레이어(칸반+활동로그+Lite-AI) 전부 선택.
- **P1 복리 코어**: catalog 협업 5엔티티(task-comment/attachment/label/label-link/activity)+task.priority(DBA, 타입드 FK·polymorphic 회피) → seed v1.1 환류(칸반 상태머신 선환류) → `taskflow-demo.yaml` 프로파일. scaffold rc=0 10테이블. **교훈: render는 profile entities만 emit → M:N 조인은 화면 없어도 profile에 명시해야 DDL 완결(FK-closure로 안 잡힘, link→label 방향).**
- **P2 칸반 보드(차별화)**: `board_descriptor`(status enum 자동 board-enabled, per-entity 하드코딩 0=open-closed) + `/board` 라우트 + `_TASK_STATUS_MACHINE`(seed 1:1) + board.html(HTML5 DnD+htmx, var(--*)만) + 보드토글. 26테스트(무효전이 422). 기존 화면 무회귀.
- **P3 Lite-AI(스코프 레퍼런스, founder 택)**: `search-similar` 서비스 — EmbeddingProvider Protocol + LocalEmbeddingProvider(TASKFLOW_EMBED_URL env·stdlib urllib·**클라우드 URL 하드코딩/폴백 0**) + trigram Jaccard 렉시컬 폴백(순수 python) + 순수 python 코사인. 응답 `mode` 명시=정직 라벨링. 30테스트. **전역룰(api 미사용·$0) 준수**, [[product-two-tier-selfhost-ai]] Lite 티어 정렬.
- **CTO 게이트(envelope 불신, 매 Phase 직접 재실행)**: catalog FK 9건 실존, board 상태머신 seed 대조, P3 클라우드 호출 0 grep + board 26/search 30 테스트 독립 재실행. Pyright 신규진단 전건 기존 false-positive(@app.context_processor 등) 판별.
- **인프라 함정 재발·해법**: `cd vanilla-htmx` 가 Bash·PowerShell **공유 cwd** 둘 다 오염 → 훅 deadlock. PowerShell `Set-Location` 절대경로 복구, 이후 pytest는 `(cd … && pytest)` 서브셸 또는 Push/Pop-Location 격리. [[subagent-cwd-hook-fragility]] 강화.
- **잔여(비차단)**: 프론트 search-similar mode 뱃지 surface(CDO) · `project.search-similar` middle contract 와이어키 등록 · 보드 컬럼색상 토큰(CDO)·모바일 터치 DnD·fragment 부분재렌더 · taskflow SEED_FILE 데모데이터 · TEI 라이브 검증(founder DSN 게이트, legal-rag TEI 재사용).
- §6 rollup: [Growth-120] 큐드 태스크 관리 프리셋 3-Phase — P1 협업 코어(catalog 5엔티티+seed+프로파일, render=profile-scope 교훈), P2 칸반 보드(open-closed board view-kind+상태머신, 26테스트), P3 Lite-AI search-similar(로컬임베딩+렉시컬폴백, 클라우드0·$0, 30테스트). 14커밋 푸시. CTO 매-Phase 독립검증. 기존 project 도메인 확장(복리), 신규 도메인 날조 0.

### Growth-121 — taskflow-demo 데모 라이브化: 선언적 시드(51레코드) + 프론트 search-similar surface, 6커밋

**맥락**: Growth-120 에서 taskflow-demo 3-Phase(협업+칸반+Lite-AI) 코드 완성. founder "데모데이터+프론트 surface 로 라이브 시연 가능하게". 백엔드 search 라우터는 `entity_store.find_all("task")` 에서 라이브 후보를 읽음 → seed_loader 로 들어간 태스크가 그대로 검색대상. 프론트는 `/api/*` 패스스루 프록시 보유(단 JSON → htmx 스왑용 서버렌더 fragment 필요).

- **시드**(`profiles/seed/taskflow-demo.seed.yaml`, 51레코드): smallmfg-demo 스키마 준용 선언적 fixture. 의존순서(dept→emp→project→milestone→label→task→link→comment→activity), FK `{$ref}`, id/타임스탬프 server-set. 칸반 데모용 5상태 전부 분산(todo4·in-progress4·blocked3·done5·cancelled1, progress_pct 상태정합), Lite-AI 데모용 태스크명 4테마(인증/결제/UI/인프라) 클러스터링. dry-run OK 51 refs resolvable.
- **프론트 surface**(server.py `/tasks/similar` 라우트 + similar_results.html fragment + board.html 검색박스 + app.css `.similar-*` + test_similar.py 11테스트): 백엔드 search-similar 프록시 후 서버렌더. **mode 배지 honesty** — semantic→"AI 의미검색"(accent), lexical→"키워드 검색"(muted) 배타적 분기, lexical 절대 AI 라벨링 안 함. 검색박스 entity_type=='task' 게이팅(보드 제너릭). 빈쿼리 무프록시, non-200 graceful.
- **CTO 독립검증**: dry-run 51 refs(utf-8 재실행, 내 콘솔 cp949 함정 회피) + 배지 honesty grep + 37테스트(11 similar+26 board 무회귀) + git status 스코프(backend/ 무수정 확인). 6커밋 파일별 푸시.
- **교훈**: ①프론트 htmx 는 JSON 아닌 HTML 스왑 → 패스스루 프록시 있어도 서버렌더 fragment 라우트 별도 필요(board 패턴 재사용). ②Windows 콘솔 cp949 → seed_loader dry-run 은 `PYTHONIOENCODING=utf-8` 필수(— em-dash 인코딩 실패). ③배지 honesty 는 코드 주석+배타적 Jinja 분기+테스트(lexical 결과에 "AI 의미검색" 부재 단언) 3중으로 박음.
- **잔여(비차단·founder 런타임 게이트)**: ①라이브 seed_loader 실행(백엔드 :8080 기동 후 POST, founder DSN/런타임) ②TEI 연결시 mode=semantic 실증(현재 env 미설정→lexical) ③search box list 뷰에도 노출 검토 ④`project.search-similar` middle contract 와이어키 등록.
- §6 rollup: [Growth-121] taskflow-demo 라이브化 — 선언적 시드 51레코드(5상태 분산+4테마 클러스터, dry-run OK) + 프론트 search-similar surface(서버렌더 fragment, mode 배지 honesty 3중 방어, task 게이팅). 6커밋. CTO 독립검증(스코프 backend 무수정+37테스트+배지 grep). 라이브 실행만 founder 런타임 게이트 잔여.

### Growth-122 — taskflow-demo Coolify 라이브 배포 + F-5 폼 타입 coercion 결함 수정, 3커밋

**맥락**: Growth-121 에서 taskflow-demo 라이브化(시드+surface) 코드 완성. founder "데모를 서버에서 고객에게 시연하고 싶다" → Coolify 배포 산출물 생산 + 라이브 배포(founder 실행) + 첫 폼 편집에서 드러난 일반 결함 수정.

- **배포 산출물**(devops, 5파일): `deploy/preview/taskflow-demo.compose.yml`(3서비스 — backend:8081 + **seeder 1회성** + frontend:5000, 헬스게이트 체인) + `scripts/taskflow-seeder/{Dockerfile,entrypoint.sh}`(backend healthy 대기→scaffold.py manifest 생성→공유볼륨→seed_loader 51건) + `infra/registry/taskflow-demo.yaml` + `docs/runbooks/taskflow-demo-deploy.md`. **인메모리 store 매 redeploy 재시드 = 시연마다 깨끗한 데이터**(의도). **gitignored manifest → seeder 가 빌드시 생성해 named volume 으로 frontend 전달**(lawfirm host bind-mount 디렉터리화 함정 회피).
- **CTO 독립검증으로 critical 결함 적발**(devops envelope 는 success 보고): compose healthcheck 가 `/health` 를 쳤으나 실제 라우트는 `/api/status/health`(status 라우터 prefix). 그대로면 **backend 영원히 unhealthy→seeder 미실행→frontend 미기동 데드락**. → Edit 수정 + 런북 smoke 예시 2건(`/health`, `entities/board_task`) 동반 수정. [[subagent-cross-service-verify]] 재확인 — thin wrapper 만 보고 success 단정 금지, cross-service 경계는 CTO 가 독립 소스검증.
- **라이브 배포(founder 실행, deploy_to_coolify.py)**: project `tmxqpuzxk4uywv67bhywnnty`/app `q1378vp78qvwfv5hh5hzv80o`, https://taskflow-demo.n9n.co.kr. registry manifest_server_path=null → SCP 자동 skip(seeder 설계 정합). TLS 첫 배포시 Traefik DEFAULT CERT(자가서명)→2분 후 LE 발급 정상(타이밍, lawfirm/shop 동일). DNS 는 `*.n9n.co.kr` 와일드카드 상설로 무선결([[infra-stack]] 갱신, 재질문 금지).
- **F-5 결함 — 폼→contract 타입 coercion**(라이브 첫 편집서 발현): project 편집 저장 → `422 budget: must be a number (decimal)`. **근본원인**: vanilla-htmx `entity_update`/`entity_create_post` 가 `request.form.items()` 를 **문자열 그대로** 백엔드 전송. 백엔드 `catalog_validator.py:247` decimal 검증은 int/float 만 허용·문자열 거부. seed_loader 경로(YAML 숫자)는 통과했으나 브라우저 폼 경로에서 드러남 = **taskflow 한정 아닌 어댑터 일반 결함**(decimal/integer/boolean 모두). **수정**: manifest 필드타입 구동 `_coerce_form_value`/`_coerce_form_data` 헬퍼(server.py) — integer→int, decimal→정수면 int 아니면 float(금액 float 정밀도 회피), boolean→truthy, 그 외 문자열, ValueError→원본유지(백엔드 명확 422 위임). **budget 하드코딩 아닌 타입 구동=복리**(모든 프로필 숫자/불린 필드 자동 적용). **백엔드 strict 는 설계의도이므로 무수정** — 어댑터가 contract 에 맞춰 보내는 게 원칙.
- **CTO 독립검증(founder payload 활용)**: founder 가 실제 /edit payload 제공(`created_at=1782271380918&...&budget=44999999`). ①Pyright "_coerce_form_data not accessed" 오탐 의심 → 두 핸들러(line 618/678) 호출 직접 확인 ②payload 의 id/created_at/updated_at 가 2차 timestamp 422 일으킬 리스크 → manifest `hidden_fields:['id','created_at','updated_at']` 실측으로 핸들러 `k not in hidden` 필터링 확증 ③field types 로 budget→int 44999999 변환·나머지 문자열 정합 추적. 116 passed(1 pre-existing hex FAIL 무관). **재배포 후 라이브 정상 동작 확인(founder)**.
- **교훈**: ①폼 어댑터는 HTTP 폼=전부 문자열 → strict wire contract 앞단에서 **manifest 타입 구동 coercion 필수**(특정 필드 하드코딩 금지). ②founder 가 준 실제 payload 는 cross-field 리스크(hidden 필터·2차 검증) 추적의 1급 단서 — 단일 에러 메시지만 보지 말고 payload 전체로 후속 결함 예측. ③Pyright "not accessed" 는 Flask 데코레이터·stale 분석서 오탐 빈발 → 실제 호출부 grep 으로 반증.
- §6 rollup: [Growth-122] taskflow-demo Coolify 라이브 배포(taskflow-demo.n9n.co.kr, seeder 재시드 패턴, manifest named-volume) + CTO 가 compose healthcheck 데드락 결함 적발·수정 + F-5 폼 타입 coercion 일반결함 수정(manifest 구동, 어댑터가 strict contract 에 맞춤). founder payload 로 hidden 필터 2차검증. 재배포 후 라이브 정상. 3커밋.

### Growth-123 — taskflow project.search-similar 와이어키 contract 등록 (Growth-121 잔여 ④), 3커밋

**맥락**: Growth-121 에서 taskflow-demo Lite-AI 유사검색 프론트 surface 완성. 백엔드 라우터(`routers/task_search.py`)는 동작했으나 와이어 키 `project.search-similar` 가 **어댑터-로컬**(docstring 에 "pending contract registration" TODO)이라 middle single-source 미등록 = 복리 축적 누락. founder "와이어키 등록부터 하자(가장 짧음)".

- **contract 등록**(`middle/contract/wire-v1.yaml`, +58줄): `project` 도메인 신설(auth/entity 비즈니스 그룹과 status 인프라 사이). `project.search-similar` 키 — request `query_text`(req)/`exclude_id`/`top_n`(default 5, adapter clamp 1~50), response `mode`(semantic|lexical, ALWAYS present)/`items`(score+full entity)/`total`/`error`. `idempotent: true`(read-only). **honesty contract 명문화** — lexical 결과를 AI/semantic 으로 라벨링 금지, mode 배지 표시 의무, cloud API cost zero(self-host embed/local fallback). 헤더 namespace 주석에 hyphenated multi-word verb(search-similar) 허용 명시.
- **라우터 docstring 갱신**(`task_search.py`): "pending registration" TODO 제거 → "registered in wire-v1.yaml, Growth-123" 참조로. README(`middle/contract/README.md`) 키 카운트 8→9, 도메인 목록에 project 추가.
- **CTO 검증**: 라우터 실제 모양과 contract 1:1 대조(GET/POST 양쪽 query_text/exclude_id/top_n, _run_search 빈쿼리 lexical no-op, 500 error envelope). YAML 파싱 OK(9키). **G-1 wire-protocol single-source 가드 PASS**. task_search 테스트 30 passed 무회귀.
- **교훈**: ①어댑터가 먼저 동작하고 contract 가 뒤따르는 패턴은 정상이나, "pending registration" docstring TODO 는 복리 누락 신호 — 동작 확인 즉시 single-source 승격. ②contract 는 코드 모양을 그대로 박는 게 아니라 honesty/idempotent/clamp 같은 **불변 계약**을 명문화하는 자리(특히 mode 배지 의무는 코드 주석만으론 약함 → contract 박제).
- **잔여(taskflow Growth-121)**: ③ search box list 뷰 노출 검토(CTO), ② TEI 연결 시 mode=semantic 실증(founder env 게이트).
- §6 rollup: [Growth-123] taskflow `project.search-similar` 와이어키 등록 — 어댑터-로컬→middle wire-v1 single-source 승격(project 도메인 신설, mode honesty/idempotent/clamp 계약 박제). 라우터 TODO 제거·README 8→9. G-1 PASS, 30테스트 무회귀. 3커밋 푸시.

### Growth-124 — taskflow 유사검색 바 list-뷰 노출 + 공유 partial 추출 (Growth-121 잔여 ③), 7커밋

**맥락**: Growth-121 에서 taskflow Lite-AI 유사검색을 **board.html 에만** 인라인으로 surface. founder "이어서 마무리" → 잔여 ③ list 뷰 노출. board 인라인 블록을 그대로 복붙하면 중복 누적 = 복리 위반 → **공유 partial 추출 후 board+list 양쪽 include** 방식 채택.

- **공유 partial**(`templates/_similar_search.html`, 신규): board 인라인 블록(15줄)을 self-gated partial 로 추출. `{% if entity_type == 'task' %}` 게이트를 partial **내부**에 두어 include 를 무조건화(비-task 는 무출력) — 호출부가 게이트 중복 안 함. honesty: mode 배지는 fragment(similar_results.html)가 유지하므로 partial 은 입력바만.
- **배선**: board.html 인라인 → include 리팩터(기능 동일). list.html + list-master-detail + list-modal + list-top-bottom **4개 list 레이아웃 전부**에 include 추가(task 가 env 로 어느 레이아웃에 배정돼도 동일 기대 충족). list 의 기존 substring 툴바와는 **별개** — 그건 entity.list filter(부분일치), 이건 Lite-AI 의미/키워드 유사도(wire `project.search-similar`, mode 배지).
- **테스트**(test_similar.py +3): `/entities/task` 바 노출 / `/board/task` 무회귀 / `/entities/department` 미노출(self-gate 검증). Flask 테스트 클라이언트(mock _proxy_request).
- **CTO 검증 함정 회피**: standalone Jinja 렌더 스모크가 base.html 미충족 컨텍스트(Flask context_processor 의 manifest 전역 부재)로 content 블록 비어 **False 오판** → Flask 테스트 클라이언트로 전환해 실재 검증. **템플릿 검증은 standalone Jinja 아닌 app test_client 가 정답**(context_processor 의존). 119 passed(1 pre-existing hex FAIL 무관, app.css 무수정).
- **교훈**: ①두 번째 surface 추가 = 복붙 신호 → 즉시 partial 추출(게이트는 partial 내부로 끌어와 호출부 무조건화). ②Jinja 템플릿 검증을 standalone Environment 로 하면 base.html 의 context_processor 전역이 비어 블록이 통째로 누락돼 false negative — Flask `app.test_client()` 사용. ③`git -C <repo>` 는 Bash persisted-cwd 훅 깨짐([[subagent-cwd-hook-fragility]])을 우회하는 안정 패턴.
- **잔여(taskflow Growth-121)**: ② TEI 연결 시 mode=semantic 실증(founder env 게이트)만 남음.
- §6 rollup: [Growth-124] taskflow 유사검색 바 list-뷰 노출(4 레이아웃 전부) — board 인라인 블록을 self-gated 공유 partial(_similar_search.html)로 추출해 board+list include. substring 툴바와 별개 Lite-AI 유사도. +3 테스트(노출/무회귀/미노출). standalone Jinja false negative 함정 → Flask test_client 전환. 7커밋.

### Growth-125 — taskflow mode=semantic 실현: embed-adapter 재사용 + provider 비대칭 재배선 (Growth-121 잔여 ②), 5커밋

**맥락**: Growth-121~124 로 Lite-AI 유사검색 contract·프론트·테스트 완성. 잔여 ② "TEI 연결 시 mode=semantic 실증"만 남음 — 백엔드는 `TASKFLOW_EMBED_URL` 미설정 시 lexical 폴백이라 라이브가 "키워드 검색" 배지뿐. founder "mode=semantic 으로 해보자". CTO 분석: 백엔드 provider 는 **native TEI 형식**(`{"inputs"}`→`[[...]]`)인데, 우리 8축 자산 legal-rag embed-adapter 는 다른 규약(`{"text"}`/`{"embedding"}`, `/embed/batch`). founder 결정 A= **embed-adapter 재사용**(한국어 e5·오프라인·복리 우선, provider 수정 감수).
- **provider 재배선**(`services/task_search.py`): `EmbeddingProvider` 프로토콜 `embed(texts)` → **`embed_query(text)`+`embed_passages(texts)` 비대칭 2-메서드**(G-87 e5 query/passage head). `LocalEmbeddingProvider` 가 `TASKFLOW_EMBED_URL` **베이스 URL** 에 `/embed`(query head)·`/embed/batch`(passage head) 부착, stdlib urllib 만. `search_similar` 의미경로: 검색어→embed_query, 후보 task→embed_passages(빈 텍스트는 `(제목 없음)` 치환해 adapter 422 회피). taskflow 가 G-87 비대칭 분리의 **새 one-directional caller**(검색어=query·task=passage 의미적으로 정확히 부합).
- **인프라**(`taskflow-demo.compose.yml`): `embed` 서비스 추가(legal-rag embed-adapter 빌드 재사용, multilingual-e5-base baked·오프라인·internal-only). backend env `TASKFLOW_EMBED_URL=http://embed:8080`. **backend depends_on embed 일부러 생략** — embed 미가동/워밍업(~60s) 중에도 backend 는 lexical 로 즉시 서빙, healthy 되면 semantic 으로 전환(honesty-fallback resilience 보존). Coolify net 격리로 legal-rag embed 공유 불가 → 본 스택 자체 인스턴스(RAM +~500MB, registry cost_note 환류).
- **검증**: task_search L1 30 passed(fake provider 도 2-메서드로 갱신, query/passage 분리). G-1 wire PASS. compose YAML 유효(4서비스). 잔존 3 FAIL(G-8 out/·G-9 §6누적·G-12 legal FK)은 전부 기존·무관.
- **교훈**: ①provider 규약을 맞출 때 "단일 embed 로 query+passage 한방"은 G-87 비대칭 head 를 silently 깨뜨림 → 프로토콜 자체를 query/passage 2-메서드로 분리해 caller 가 교차 못 하게 강제. ②사이드카는 backend 와 hard depends_on 결합하지 말 것 — graceful-fallback 설계의 resilience(미가동 시 lexical)가 오케스트레이션 레벨에서 사라짐.
- **잔여**: L4 live `mode=semantic` 실증 — Coolify 재배포(embed 이미지 빌드 ~수분) 후 `taskflow-demo.n9n.co.kr` 검색에서 "AI 의미검색" 배지 확인(push 자동배포 또는 founder redeploy). taskflow Growth-121 잔여 전부 종결.
- §6 rollup: [Growth-125] taskflow mode=semantic 실현 — legal-rag embed-adapter(한국어 e5) 재사용, provider 를 비대칭 embed_query/embed_passages(G-87 query/passage head) 로 재배선. compose embed 사이드카+TASKFLOW_EMBED_URL=http://embed:8080(depends_on 생략=lexical resilience 보존). L1 30 PASS·G-1 PASS. **L4 live PASS** — 재배포 후 	askflow-demo.n9n.co.kr 검색이 'AI 의미검색'(semantic, cosine top 86%) 확증, lexical-distinct 쿼리 3종 전부 semantic. taskflow Growth-121 잔여 전부 종결. 5커밋.

### Growth-126 — entity.list 자유텍스트 `search` 결함 수정: 전 데모 검색 0건 → 부분일치 (G-126), 5커밋

**맥락**: founder "데모 포털 카드의 데모들 전부 검색이 안 된다". CTO 진단 — vanilla-htmx 공유 리스트 툴바의 자유텍스트 "검색…" 박스가 `?search=<term>` 전송하나, 백엔드 entity.list 가 비예약키를 **exact field=value 필터**로 처리 → 레코드에 없는 `search` 필드에 매칭 → **모든 업종 데모에서 검색 시 0건**(공유 어댑터 결함, taskflow 한정 아님).
- **수정**: `search` 를 예약키로 승격, 전 필드값 대소문자무시 substring(OR) 매치를 `filter` 이후 적용. fastapi(`routers/entity.py` _matches_search)+springboot(`EntityController.java` matchesSearch) 양 어댑터 파리티. contract(`wire-v1.yaml`)에 `search` 필드 명문화(어댑터는 exact 필터 금지 — 없는 필드라 0건).
- **테스트**: fastapi L1 7케이스(부분일치/대소문자/비-name OR/무매치0/공백·미지정 전체반환 회귀가드/filter결합) + `_shared` 컴플라이언스 1케이스(양 어댑터 라이브). fastapi 전체 86 passed. G-1 PASS.
- **검증 한계**: springboot 미배포(전 데모 fastapi) → L3 gradle 은 오프라인 플러그인 미캐시·무네트워크 룰로 본 환경 미검증, 변경은 matchesFilter 패턴 1:1 미러+컴플라이언스 라이브 가드로 보증.
- **교훈**: UI 가 노출한 기능(자유텍스트 검색)이 백엔드 계약에 없으면 "조용히 0건"으로 죽는다 — 비예약키=exact-filter 라는 어댑터 디폴트가 자유텍스트 박스와 충돌. 새 입력 표면은 contract 예약키+의미 정의가 선행돼야.
- **잔여(founder)**: 9개 데모 Coolify 재배포(공유 fastapi 백엔드 재빌드로 픽업).
- §6 rollup: [Growth-126] entity.list 자유텍스트 `search` 결함 — 비예약키 exact-filter 오용으로 전 업종 데모 검색 0건. `search` 예약키 승격+전필드 substring(OR, filter 이후) fastapi+springboot 파리티, contract 명문화. fastapi 86 passed+컴플라이언스 가드. 교훈: UI 노출 기능이 계약에 없으면 조용히 0건. founder 9데모 재배포 잔여. 5커밋.
### Growth-127 — 소형 로펌 killer-app 2종(K1 기일 가디언·K2 이해충돌 검사) + 로폼 경쟁분석, 15커밋

**맥락**: founder "소형 법무법인 타겟 killer app 추가 — 로폼(business.lawform.io) 분석해 needs 도출, 로폼 구독 SaaS 와 경쟁 회피·in-house 완성형으로". CTO 분석(wiki synthesis 환류 [[lawform-competitive-analysis]]): 로폼=계약(contract)축·생성형·클라우드구독·대기업법무팀/개인 → **소형 로펌의 사건(case)축은 사각지대**. 정면충돌(CLM·계약생성) 회피, 사건축·검색형·self-host 로 우회. founder 선택 K1+K2 둘 다.
- **K1 기일·기한 가디언**: catalog `case-deadline`(legal, FK case_id→legal-case)+DDL augment `11_legal_case_deadline.sql`(신규테이블·case-scoped RLS)+profile/seed 12건(임박4·미래5·지남1·완료2). vanilla-htmx 리스트 임박(D-7·pending) 하이라이트(server.py imminent_ids + list.html tr--imminent + app.css warning 토큰), 종료상태 제외. honest: "누락 방지" 아님 "임박 표시".
- **K2 이해충돌 검사**: `project.search-similar` 를 `entity_type` 파라미터(기본 task, open-closed)로 일반화 → `case-party` 이름 유사검색 재사용. wire contract 명문화. case-party 리스트에 conflict 위젯(_similar_search.html 분기)+conflict_results.html(mode 배지·"후보일 뿐 최종판단 변호사" 면책). embed 사이드카 재사용(미설정 시 lexical 폴백).
- **검증**: fastapi 90 passed(K2 4 신규). 라이브 로컬: case-deadline 12건 서빙·conflict "박서연" 5건. scaffold lawfirm-demo 15엔티티 정상. py_compile OK. app.css 기존 raw-hex 3줄(834-836) 토큰 교정(가드 부분개선). G-1 PASS, 신규 G-12 위반 0.
- **잔여(founder)**: ①lawfirm-demo Coolify 재배포(공유 fastapi+프론트 재빌드) ②**manifest scp**(out/lawfirm-demo/screen-manifest.json → /data/coolify/manifests/lawfirm-demo/, case-deadline nav 노출 필수) ③seed 기일 날짜 2026-06 앵커(시간경과 시 임박 퇴색 — 주기 갱신).
- **교훈**: 경쟁 SaaS 와 같은 축에서 싸우지 말고 사각지대(사건축)를 self-host 완성형으로 — 차별화=기능 더하기 아니라 축 바꾸기. 기존 검색엔진을 entity_type 파라미터 하나로 새 killer-app(이해충돌)으로 재사용=복리.
- §6 rollup: [Growth-127] 소형로펌 killer-app K1 기일가디언(case-deadline entity+DDL+임박 하이라이트)·K2 이해충돌검사(search-similar→entity_type 일반화로 case-party 재사용). 로폼=계약/구독/생성형, 사각지대=사건축 → self-host 검색형 우회([[lawform-competitive-analysis]]). fastapi 90 passed·라이브로컬 PASS. 잔여 founder: 재배포+manifest scp. 15커밋.

### Growth-127 후속 — manifest scp→seeder 전환 + 칸반 카드 셀렉트 full-width 결함 수정

- **manifest 공급 scp→seeder 전환** (푸시 b79f1ec): scp publickey denied(no-SSH 경계) → 제너릭 `scripts/manifest-generator/`(Dockerfile+entrypoint, scaffold→공유볼륨, manifest-only ∵ SEED_FILE) + lawfirm compose 를 host bind-mount→공유볼륨 seeder 패턴 전환. scp 영구 제거, 나머지 8 scp-데모 재사용 자산.
- **칸반 카드 상태 셀렉트 full-width 결함** (푸시 ed726d0): founder "칸반 카드 width 100%". CTO 라이브 probe — 카드/컬럼 정상(컨테이너 flex, 컬럼 240px, 3컬럼12카드). 진짜 원인=제너릭 엔티티 카드 상태변경 `<select class="form-input board-card__move-select">`가 `.form-input{width:100%}`(app.css:683) 상속, `.board-card__move-select` width 미정의 → 셀렉트가 카드 폭 전체로. task 엔티티=버튼이라 무관, lawfirm 6 board 엔티티 전부 제너릭→전 카드 증상. 수정: `display:inline-block;width:auto;max-width:100%`(정의순서상 .form-input 뒤→승리). board L1 26 passed. 교훈: 공유 폼 유틸클래스(.form-input)를 컴팩트 컨텍스트(카드/툴바)에 재사용 시 width override 누락이 조용한 레이아웃 결함.
- §6 rollup: [Growth-127 후속] manifest scp→in-cluster seeder 영구전환(b79f1ec, 8데모 재사용) + 칸반 카드 상태셀렉트 full-width 결함 수정(ed726d0, .form-input width:100% 상속 차단). board L1 26 PASS. founder 잔여: lawfirm-demo Redeploy.


### Growth-128 — 소형 로펌 killer-app K3 타임시트·빌링 (time-entry·case-invoice 엔티티 + 청구 롤업), 11커밋

**맥락**: K1(기일 가디언)·K2(이해충돌) 종결 후 founder가 K3 타임시트·빌링 선택 — 시간당 청구는 소형 로펌 수익 핵심, 사건축 자연 동반. CTO 설계 → engineer-agent(sonnet) 위임, K1(case-deadline) 누적 패턴 1:1 미러.

- **신규 엔티티 2**: `time-entry`(table legal_time_entry — case_id FK cascade·employee_id cross-domain fk-exempt[K1 assigned_attorney 관습]·minutes/hourly_rate/amount integer·billable·status[draft/submitted/billed]) + `case-invoice`(table legal_invoice — client_name·subtotal/tax/total·status[draft/issued/paid]). DDL 12/13 = K1 case-scoped RLS(ENABLE+FORCE, attorney/partner)·set_updated_at 트리거·인덱스·idempotent ADD-ONLY 미러.
- **Killer 기능(K1 imminent_ids 미러)**: server.py entity_list가 entity_type=="time-entry"일 때 billable_total/unbilled_total(status!=billed)/total_minutes 롤업 계산(billable 타입 강제변환) → list.html 청구 요약 배너 + tr--unbilled 미청구 하이라이트. 개방-폐쇄(time-entry 가드). honest: "기록 기반 청구 합계 집계"만, 자동 청구서 생성·법적 효력 주장 금지.
- **시드**: time-entry 25(billable 23·status 혼합)·case-invoice 6(부가세 10% 정합). amount=round(분/60×시급) 0오류, FK dangling 0.
- **CTO 게이트 — CRITICAL 적발/수정**: engineer가 신규 엔티티를 `invoice` 키로 명명 → **기존 finance 도메인 `invoice`(finance_invoice)와 같은 /entities 매핑에서 YAML 키 충돌**. PyYAML이 로드 전 중복키 dedupe → finance_invoice 소실·payment.invoice_id FK 오염되나 **G-10이 dedupe된 결과만 봐서 PASS(silent 결함)**. CTO 독립 yaml.safe_load 검증으로 적발([[subagent-cross-service-verify]] 재확인). 신규 엔티티 `invoice`→`case-invoice` 리네임(finance 불가침, 5파일 일관: catalog·profile·seed gen·seed json·DDL 주석)으로 복구. 재검증: invoice→finance_invoice·case-invoice→legal_invoice 공존 확정.
- **검증**: fastapi 90·billing L1 13·board L1 26 green, scaffold rc=0(17엔티티 manifest), diagnose 신규 FAIL 0. 11커밋(2c3f062).
- **교훈**: 멀티도메인 catalog에 엔티티 추가 시 **전역 키 유일성**을 먼저 확인(도메인 prefix 관습 case-/legal- 활용). YAML 중복키는 파서가 조용히 삼켜 가드를 우회 — CTO는 safe_load 후 키 존재를 직접 단언해야 한다.
- **잔여 founder**: lawfirm-demo Coolify Redeploy(frontend+backend 재빌드, seeder가 manifest 재생성) → time-entry·case-invoice nav 등장 + 청구 롤업 배너 라이브.
- §6 rollup: [Growth-128] K3 타임시트·빌링 — time-entry·case-invoice 엔티티+DDL(K1 RLS 미러)+청구 롤업 배너(billable/unbilled/총시간, imminent_ids 패턴). CTO 게이트가 invoice↔finance_invoice YAML 키 충돌(G-10 우회 silent 결함) 적발→case-invoice 리네임 복구. fastapi 90·billing 13·board 26 green. 11커밋.
