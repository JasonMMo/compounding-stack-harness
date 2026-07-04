# Growth Archive Vol.04 — Growth-129 ~ Growth-134

> `growth-archive.md`(인덱스) 산하 볼륨. 원문 무수정 이동. 규약: `docs/learn-logs/README.md`.

## Growth-68 ~ Growth-134 (2026-06-15 ~ 2026-06-30, 이동: Growth-143) (계속)

### Growth-129 — lawfirm-demo 헤더 좌우 여백 "반영 안 됨"의 2중 결함 규명 + headless 검증 하니스 skill화

**맥락**: founder가 lawfirm-demo `/board/case-deadline` 글로벌 헤더의 좌우 여백이 Redeploy+캐시삭제 후에도 그대로고 "browser 사이즈에 비례해 여백이 늘고 준다 / 반영이 안됐어, 남의 다리 긁는 기분"이라 재점검 요청. 처음 padding(48→24px) 가설은 틀렸다 — 고정 px는 뷰포트-비례 여백을 못 만든다. 추측 중단, 라이브 DOM 측정으로 전환.

- **결함 ①(반영을 가로막던 enabler)**: vanilla-htmx PWA 서비스워커 `/static/sw.js`(전 데모 공통)가 `/static/css|js`를 **cache-first + 고정 캐시명 `csh-v1`**로 서빙 → sw.js 무변경+캐시명 고정이라 브라우저가 SW 재설치 안 함 → 옛 app.css 영구 서빙. HTML(network-first)은 신선, CSS(cache-first)만 stale인 **비대칭**이 결정적 단서. 수정: 전부 **network-first(+오프라인 폴백)**, `csh-v1→csh-v2` bump로 activate가 독성 캐시 일괄 삭제 (commit 87091ac). 이후 Redeploy는 새로고침 1회로 항상 반영.
- **결함 ②(진짜 시각 원인)**: Pico CSS v2 classless가 **body 직계 `<header>`/`<footer>`에 reading-container max-width**(xxl 1450px) + 가운데정렬을 자동 적용 → 뷰포트 1822px에서 헤더가 1450px로 좁아지고 좌측 186px 여백(비례)이 생김. app-layout grid를 `minmax(0,1fr)`로 풀폭 만든 이전 수정(디자인 수정-4)은 무효 — grid **컬럼**만 풀폭, 헤더 **아이템**의 Pico max-width는 별개. 직계 아닌 `<main class=app-main>`(app-body div 안)은 Pico `body>main` 미적용 → 본문은 멀쩡, 헤더만 좁은 이유. 수정: `.app-header,.app-footer,.app-header-minimal { max-width:none; width:100%; margin-inline:0 }`. class 셀렉터(0,1,0) > Pico `:where()`(0,0,0)라 `!important` 불필요 (commit f252336, 디자인 수정-6).
- **왜 SW만 고치고 reload해도 안 변했나**: 새 CSS가 닿아도 그 CSS 자체에 헤더 수정이 없었음(②가 아직 미커밋). 두 결함은 founder 체감상 상호의존 — ①이 새 CSS를 브라우저까지 보내고, ②가 실제 여백을 제거.
- **측정 증거**(라이브 로그인 demo/demo, vw=1822): BEFORE 헤더 `{x:186, w:1450}` → 후보 CSS 주입 AFTER `{x:0, w:1822, 로고 x:61}` = 풀폭, 좌측 여백 0. **배포 0회로 수정을 증명.**
- **반복 작업 skill화**: 이 측정-주입 워크플로(puppeteer-core@23 `$TEMP/node_modules` + 로컬 Chrome, 라이브 로그인, getBoundingClientRect/getComputedStyle 측정, 후보 CSS `addStyleTag` 주입으로 redeploy 전 증명)를 `.claude/skills/htmx-demo-verify/`(SKILL.md + scripts/verify_live_css.mjs)로 추출. 기존 webapp-testing(로컬 Playwright)과 구분 — 이건 **이미 배포된 라이브** 데모 검증 + 배포 전 CSS 주입 증명. "디자인 수정 반영 안 됨" 3대 원인(SW stale / Pico max-width / push 누락) 변별표 동봉.
- **전파**: 두 수정 모두 공통 vanilla-htmx 어댑터 → 전 ~10개 라이브 데모가 각 Redeploy 시 흡수. 진단법 메모리 2종 환류([[pwa-sw-stale-cache]], [[pico-container-maxwidth-shell]]).
- **잔여 founder**: lawfirm-demo Redeploy 1회(새 sw.js + 새 app.css 둘 다) → 새로고침 1회로 헤더 풀폭 확인. SW 잔류 시 F12→Application→Service Workers→Unregister 후 reload.
- **교훈**: "배포가 안 보인다"는 추측 금지 — 라이브 DOM을 측정하고 후보 CSS를 주입해 증명한 뒤 커밋한다. 뷰포트-비례 여백 = max-width 컨테이너(고정 px padding 아님). HTML은 되는데 CSS만 안 되면 SW stale.
- §6 rollup: [Growth-129] lawfirm 헤더 여백 2중 결함 규명 — PWA SW stale 캐시(87091ac, network-first+csh-v2) + Pico 컨테이너 max-width(f252336, .app-* max-width:none). headless Chrome으로 x=186 w=1450→x=0 w=1822 측정 증명. 반복 검증 워크플로 → htmx-demo-verify skill 추출. 메모리 2종 환류. 전 데모 공통.

### Growth-130 — claude.ai/design ↔ repo 분리·통합 아키텍처 (deep-research 기반 설계 박제)

**맥락**: founder "디자인 조정 반복작업·시간 과다 + axis-8 산출물 밋밋. claude.ai/design 기능 활용 needs. 단 클라우드 분리 + 고객 복제본(구조변경0·데이터누출0) 가능해야". CTO 진단: 밋밋함은 구조적(토큰 재색칠+고정 variants), 시간싱크는 배포-왕복. claude-design=배포없는 즉시-렌더 craft 엔진이나 경계 선결. deep-research 하니스 가동(8 findings, 3-vote adversarial).

- **연구 확정 제약**: Claude Design = 유료티어·**BAA 제외(beta)**·기본 학습허용(opt-out 카브아웃2) → PII 절대 업로드금지(C2~C4). DTCG 토큰 2025.10(W3C CG, Rec 아님)·Style Dictionary v5+ include/source·Storybook Package Composition·vercel/platforms는 런타임라우팅(우린 빌드타임 정적이 우월).
- **아키텍처 4파트**(`docs/architecture/design-cloud-bridge.md`): (A)분리경계=클라우드 authoring-only/넘는것은 DTCG 토큰JSON뿐, 우리 raw→semantic→theme.yaml 계층이 곧 경계(신표준0) (B)정규화 게이트=CDO가 클라우드 컴포넌트를 catalog variant+토큰으로 분해해야 머지(직접붙임=복리붕괴) (C)복제본=빌드타임 물리격리(landing-astro SSG+고객 theme/profile 주입, 구조변경0) (D)CI가드 5종(업로드스코프·클라우드결합누출·교차테넌트누출·DTCG스키마·정규화게이트).
- **환류**: wiki synthesis [[claude-design-cloud-boundary]] + source [[deep-research-design-cloud-2026-06]] + index 2줄. 원본 `out/`(gitignored).
- **잔여**: ~~Phase2 가드5종~~(WP-2) · ~~Phase3 복제본 CLI~~(WP-3) · ~~WP-4 파일럿 측정~~(A/B 종결: cloud craft 2~3분 vs baseline 25분, 충실도 HIGH·normalize LOW, 라이브 픽셀 양 arm PASS, 판정=재사용 섹션 craft 한정 도입+repo 시각검증 훅 완화, design-loop SKILL 박제) **종결**. **잔여 = founder 채택결정 게이트**: 채택 시 → 신규 variant 로 landing-astro 병존 빌드(production Pricing.astro 덮어쓰기 ✗)·shadow 2종 theme.yaml 등록·scoped-CSS vs Tailwind 컨벤션 CDO 판정·net-new 섹션 재측정. legal 고객엔 BAA beta졸업 재검증 전 PII 금지.
- §6 rollup: [Growth-130] claude.ai/design 분리·통합 아키텍처 박제 — deep-research(BAA제외·학습기본·DTCG·Style Dictionary v5+·빌드타임 물리격리) 기반. 경계=토큰JSON, 정규화 게이트, 복제본 누출0·결합0·구조변경0, CI가드5종 후보. 문서+wiki 3페이지 환류. 구현은 후속 Phase.

### Growth-131 — HTMX swap/settle 전환 프리셋 (vanilla net-new 모션 역량)

**맥락**: 정찰이 "최고 레버리지 후속"으로 지목 — landing-astro 페이지 전환에 대응하는 vanilla-htmx 콘텐츠-스왑 전환. 기존 어댑터는 motion 토큰을 소비하되(Growth-130g) 스왑은 전부 무전환 스냅(`hx-swap=innerHTML` 다수).

- **신설**: `static/css/swap-transitions.css` — opt-in `.swap-fade/-up/-down/-slide-in` + `.swap-stagger`. library-free, `--motion-*` 토큰 구동, base.html 링크.
- **2단계 메커니즘**: IN=삽입-트리거 1회성 CSS animation(`.swap-* > *`, settle 타이밍 무의존 → footgun 회피, JS innerHTML 덮어쓰기 화면에도 작동) / OUT=`.htmx-swapping` opacity 페이드(`hx-swap` 에 `swap:120ms` 명시 시 가시).
- **불변식**: resting opacity 항상 1(opacity:0 은 keyframe from·htmx-swapping 한정) → G-69 no-JS-visible 유지. `prefers-reduced-motion` 전용 블록이 transform·stagger·duration 전면 중화(WCAG 2.3.3). 미적용 화면 byte-identical(motion off 기본 계승).
- **토큰 환류**: 미사용이던 `--motion-stagger-base` 첫 소비(계단식 6단계 캡). 신규 design 토큰 0(adapter-local `--swap-distance:8px`, motion-distance 승격 여지 주석).
- **데모 2곳**: `legal_precedent_search.html`(#results=fade-up+stagger) · `list-master-detail.html`(#detail-panel=slide-in, 행 swap:120ms).
- **검증**: L3 토큰빌드 PASS · L1 132 pass(잔여 1 fail=app.css hex, 무관 기존) · 가드 신규위반 0(FAIL 3건 out/·ledger·legal catalog 전부 기존) · CSS 브레이스 24/24·6 토큰참조 실존·키프레임 4종 정합.
- §6 rollup: [Growth-131] HTMX swap/settle 전환 프리셋 신설(swap-transitions.css) — opt-in fade/slide+stagger, motion 토큰 구동, IN=삽입트리거(settle footgun 회피)·OUT=htmx-swapping, G-69+reduced-motion 안전, --motion-stagger 첫 소비, 데모 2곳. landing 페이지전환 대응 vanilla net-new.

### Growth-131 라이브 검증 (lawfirm-demo redeploy 후, htmx-demo-verify headless Chrome)

- **fade-up+stagger LIVE PASS**: `/legal/search` 실제 htmx 검색 스왑에서 `#results` 자식이 `swap-in-up` 발화·토큰해석 280ms 확증. Stage0(에셋 200·`@keyframes swap-in-up`·`.swap-stagger` 라이브 서빙, SW stale 아님·push 반영) + 스타일시트 라이브 적용 PASS. (8/9 체크)
- **slide-in 라이브 미행사 — 코드결함 아님/deploy-config**: lawfirm-demo 에 `MASTER_DETAIL_ENTITIES` env 미설정 → `/type1`→`/home` 리다이렉트, 전 legal 엔티티가 `list.html`(plain)로 렌더(master-detail/top-bottom/modal 전부 false, server.py:567 `entity_type in _MD_ENTITIES` 게이트). slide-in CSS 계약은 로컬 headless 픽스처 13/13(swap-in-x·280ms)로 증명필. 라이브 확인하려면 founder가 `MASTER_DETAIL_ENTITIES=legal-case` 설정+redeploy.
- **부수 결함 환류(79a685e)**: htmx-demo-verify 로그인 패턴이 `/api/auth/login`(백엔드 JSON 토큰, Set-Cookie 없음) POST → 세션 미설정 → 인증 대상 대신 `/login` 페이지를 조용히 측정하던 결함. `/login` 폼 제출(세션쿠키)로 교정·라이브 스모크(`.app-header` x:0 w:1822) 확증. 메모리 [[htmx-demo-verify-skill]] 환류.
- §6 rollup: [Growth-131-verify] fade-up+stagger 라이브 PASS(/legal/search 실 htmx 스왑, swap-in-up 280ms). slide-in 은 lawfirm-demo MASTER_DETAIL_ENTITIES 미설정으로 라이브 미행사(코드 OK, config 갭). htmx-demo-verify 로그인 결함(/api/auth/login→/login 폼) 교정 환류.

### Growth-131 live-verify 종결 (slide-in 게이트 해소)
- founder가 lawfirm-demo에 `MASTER_DETAIL_ENTITIES=legal-case` env 추가 + redeploy → 이전 검증의 config-gap 해소.
- `verify_live_swap.mjs` 재실행 **12/12 PASS** (이전 8/9 → slide-in Stage2 4-check 전부 GREEN).
- Stage2: `/type1` master-detail 도달, `#detail-panel`=`swap-slide-in`, **실제 행 클릭 htmx swap에서 `swap-in-x` 발화 + duration 280ms(`--motion-duration-base` 토큰 해석)** 확증.
- 결론: swap-transitions.css 두 프리셋(fade-up/stagger, slide-in) 모두 라이브에서 실제 htmx swap에 행사됨. 코드 결함 0, 잔여 config-gap 0. Growth-131 end-to-end LIVE 종결.

### Growth-131b — reduced-motion override xslow 누락 a11y 갭 수정 (하드코딩→토큰셋 파생)
- CTO가 wiki 환류(Growth-131) 중 적발: reduced-motion override가 `--motion-duration-xslow`(640ms 페이지레벨 전환)를 붕괴 안 시킴. 원인=override 토큰 목록 하드코딩(fast/base/slow/intro 4종)이 토큰셋과 드리프트.
- 결함 2곳: `token_css_generator.py`(vanilla, py) + `build-tokens.mjs`(react, js) 동일 하드코딩. landing-astro는 token-override 없음(컴포넌트별 처리, 무관).
- 근본 수정(engineer): 하드코딩 4줄 → `sem_pairs`/`semPairs`에서 `--motion-duration-*` 접두 필터·정렬 순회로 파생. **신규 duration 토큰 자동 커버, 재발 불가**(open-closed).
- 재생성 검증: vanilla tokens.css L385-389 + react tokens.gen.css L274-278 모두 5종(xslow 포함) 붕괴 확인. pytest 26 passed(기존 무관 app.css raw-hex 1 fail 유지), diagnose 새 FAIL 0. wiki motion-tokens.md §3 INFERRED→EXTRACTED 해소.
### Growth-131c — ledger-index incremental cache (누적-민감 재파싱 제거) + create-context-graph 거부 결정
- founder가 create-context-graph(Neo4j Labs, github.com/neo4j-labs/create-context-graph)를 3-검색 앞단/메모리 대체 후보로 제시. CTO 측정으로 진단 후 거부.
- 측정(Measure-Command 분해): qmd "느림"=바이너리 spawn ~335ms 고정비(BM25 실검색 ~30ms, 누적 무관). 유일한 누적-민감 비용=ledger-index의 평면원장(190KB+360KB) 전체 재파싱 ~160ms. Neo4j는 둘 다 못 고침(서버왕복 추가)+self-host/cost-aware wedge 정면충돌+codegraph SQLite 중복.
- 차용한 아이디어("그래프 메모리 증분 갱신")만 흡수: `ledger-index.py` build_index에 content-hash(sha256) 캐시(`_index.cache.json`, gitignored). parse+extract만 캐시(파일내용 순수함수), codegraph 검증·전역 dedup·정렬은 매번 신선. mtime 아닌 content-hash(checkout 견고).
- 정확성: HEAD 원본과 `_index.json` byte-identical(sha256 c7022ec8, 콜드·웜 동일) 독립 검증. in-proc build_index 콜드 85ms→웜 31ms(2.7x). diagnose 새 FAIL 0. 커밋 41e413c(ledger-index.py)+805d7b1(.gitignore) 푸시.
- 환류: wiki concepts/asset-search-architecture.md 신설(누적 자산 3-tier 검색 + 측정 프로파일 + 결정), index.md +1줄, qmd wiki 재색인(asset-search 검색 85% 확인). 사용자 최초 질문("누적 자산 검색 방식")의 커버리지 갭 종결.
- Files touched:
  - `scripts/ledger-index.py`
  - `.gitignore`
  - `knowledge/wiki/concepts/asset-search-architecture.md`
  - `knowledge/wiki/index.md`

### Growth-132 — 한방 RAG 데모 D0: services/hanbang-rag/ 포크 (legal-rag → 한방 버티컬)
- CTO greenlight 3결정(테이블 hanbang_rag_*, auth+단일데모계정, FastAPI독립+postgres/embed공유) 확정 후 D0 착수. engineer-agent 위임.
- **재구현 금지 준수**: ingest/retrieve/citation/auth/db/embed_client/config + embed-adapter 카피 후 최소 SQL 교체만. 검색 파이프라인(FTS+ANN+RRF) 완전 재사용.
- **테이블 네이밍(founder 확정)**: `hanbang_rag_notice` / `hanbang_rag_document_chunk` / `hanbang_rag_user` / `hanbang_rag_query_log` (서비스 슬러그=테이블 프리픽스 일치).
- **단일 소스타입 단순화**: legal-rag의 precedent+case_document 2갈래 → 한방 고시(notice) 1갈래. ingest의 _CHECK_CASE_DOC/_UPDATE_CASE_DOC_STATUS 분기·citation의 _RESOLVE_CASE_DOC 분기·Citation case 필드 전부 제거. Citation 메타=고시번호/소관부처/발령일자/요약.
- **D0 범위 경계**: api.py(D1 신규작성)·web/(D3 카피교체) 의도적 제외 — legal 엔티티 의존성이 pytest를 깨뜨리므로 파이프라인 코어+단위테스트만.
- **CTO 통합검증(보고 비신뢰, 독립 재현)**: ①잔존 legal_ 테이블 참조 0(주석 3건뿐) ②hanbang_rag_ 34곳 적용 ③pytest **29 passed** 독립 재현 ④api.py/web 부재 확인. PASS.
- 커밋: 실질변경 3파일(ingest/retrieve/citation) 단독 + 복사본 3그룹(인프라/embed-adapter/tests) = 8커밋. master 푸시(8485419..a953a71).
- **D1 미결(인계)**: hanbang_rag_notice 컬럼스키마 확정→citation SELECT/Citation 매핑 검증, document_chunk의 case_id 컬럼 잔재 제거여부, hanbang_rag_query_log/hanbang_rag_user DDL 신규작성, api.py 신규작성(/search,/ingest,/health,/auth/login,/documents/notice/*).
- 비용: postgres·embed-adapter 공유로 신규 월비용 ≈ FastAPI 컨테이너 1개+서브도메인. M3(첫 버티컬→두번째) 기여.
### Growth-133 — 한방 RAG 데모 D1: DDL(4테이블) + api.py 신규 + case_id legal 잔재 정리
- DBA가 contract-first DDL 작성: D0 코드가 SELECT/INSERT하는 컬럼을 역도출해 `services/hanbang-rag/sql/` 8파일(00_extensions~07_seed). 매핑표 불일치 0(citation/ingest/retrieve/auth의 모든 SQL ↔ DDL 컬럼 1:1).
- **4테이블**: hanbang_rag_notice(고시번호/소관부처/발령일자/notice_type TEXT/요약/전문) · hanbang_rag_document_chunk(vector(768) HNSW cosine + FTS simple GIN, source_type='notice' CHECK) · hanbang_rag_user(bcrypt) · hanbang_rag_query_log.
- **RLS 단순화(CTO 지침)**: 한방 고시=공개 참조데이터(PII 0, 전 사용자 동일열람) → notice/chunk RLS 비활성(legal 청크격리 RLS 미포팅), 쓰기제한은 grant(app_user INSERT 미부여)로. query_log만 user_id RLS(Phase 2 멀티계정 대비·legal 패턴 재사용). 향후 공개 랜딩 테넌트는 CISO 게이트 후 재검토.
- **case_id legal 잔재 clean 제거**: DBA가 DDL에서 제거 → engineer가 코드 정합. ingest UPSERT 9→8컬럼, retrieve _FETCH_CHUNKS_SQL row 재인덱싱(case_id 제거로 row[3]=chunk_index/row[4]=chunk_text/row[5]=token_count)·case_filter 고정 빈값·RetrievedChunk 필드 제거. CTO가 grep으로 제거범위 확인 후 결정(테스트 1곳만 검증=contained).
- **engineer cwd-hook-fragility 재발**: Read/Edit 차단으로 직접수정 불가 → fail-safe 패치스크립트(`_patch_d1_case_id.py`, 미발견시 sys.exit(1)) 작성. **CTO가 라인별 검토 후 적용** — 결함 적발: open(w) newline 미지정 → Windows LF→CRLF 변환. 적용 후 3파일 LF 정규화로 교정. 메모리 [[subagent-cwd-hook-fragility]] 재확증.
- **api.py 신규(~310줄)**: legal api.py(63KB) 모델로 lean 재작성. /auth/login(hanbang_rag_user+JWT)·/health·/health/detail·/ingest(notice 고정, service token)·/search(retrieve→citation→log_query, rls_session)·/documents/notice/{id}(full_text 원문, 인터뷰 신뢰전달). case/party/attorney/document-upload 엔드포인트 전부 제외. retrieve/citation/ingest/auth/db 와이어만(재구현 0).
- **CTO 통합검증**: case_id 잔재 0(주석조차)·py_compile 8모듈 OK·pytest **29 passed**·DDL↔코드 불일치 0. api.py L115 pyright(**docs_kwargs None 추론)·import 미해결은 config/추론 아티팩트(런타임 무해, py_compile/pytest 통과)→D3 pyrightconfig 정리.
- 커밋: DDL 2그룹(schema/grants+seed) + api.py + ingest/retrieve/test 단독 = 6커밋 푸시.
- **D2 미결**: VPS corpus 수집(fetch_hanbang_admrul.py, 고시 4건)→XML파싱→hanbang_rag_notice INSERT→/ingest. sql/ DB적용(psql/Coolify). bcrypt 실해시(CISO). 배포env 5종(DSN/EMBED_URL/JWT_SECRET/SERVICE_TOKEN/INGEST_ROOT). catalog.yaml 환류 후보="공개 참조데이터+RAG 청크" 패턴(CTO 승인 후).
### Growth-134 — 한방 RAG 데모 D2(일부): corpus 라이브 수집 (founder "corpus만 먼저" 게이트)
- founder가 D2 진행을 "corpus만 먼저 수집"으로 선택(DB적용·ingest·배포는 DSN/Coolify 준비 시점까지 대기). CTO가 VPS(187.77.140.157) SSH로 실수집 수행.
- **스크립트 업그레이드**(fetch_hanbang_admrul.py): PoC(본문 1건 증명) → 다건 수집 + manifest.json(ingest 연결). engineer 설계 위임했으나 cwd-hook로 파일 못읽어 **dict 키 불일치**(부처명/법령일련번호 vs 실제 ministry/seq) → CTO(integrator)가 실제 키로 보정 적용(PowerShell, engineer 구조적 blind).
- **핵심 발견 — admrul API 본문 구조**: law.go.kr `lawService.do?target=admrul&ID=<일련번호>&type=XML`이 고시별로 다르게 반환. 건강보험 「요양급여 세부사항」·「행위 급여·비급여 목록표 및 상대가치점수」는 **개정문(thin, ~3K자, 별표 미포함)만** → 데모 corpus 부적합. 의료급여수가·비급여보고·의료기술분류는 **전문(rich, 180~720K자)** 반환. **큐레이션 정답=키워드+제목필터 ✗, 검증된 seq 직접지정 ○**(TARGET_SEQS 상수).
- **버그 수정**: empty-detector(`"없습니다" in decoded`)가 1MB 정상문서를 부분문자열 매칭으로 오탐 거부 → `len<300 or (len<2000 and marker)` 로 수정. 의료급여수가 720K 수신 회복.
- **수집 corpus 3건(~1.97MB, 전부 보건복지부 고시 원문)**: 의료급여수가 기준(720K, 추나12·한방38·한의7) + 비급여 진료비용 보고(544K, 추나13·약침3·첩약1) + 보건의료기술 분류체계(183K, 한의5). manifest.json(seq/name/ministry/date/char_count/xml_file) parse_detail_meta로 본문 XML서 메타 추출. VPS out/corpus/hanbang/.
- **데모-적합 caveat(founder 보고)**: 수집 corpus는 **의료급여+비급여**가 중심, 페르소나(한의원 청구담당)의 주력인 **건강보험 요양급여/상대가치점수 전문은 API 한계로 미수집**. 실제 한방 급여 내용(추나/약침/한방)은 풍부해 "고시 원문 검색" 데모 신뢰전달엔 충분하나, 건강보험 상대가치 corpus 보강은 follow-up(별표 별도 API 또는 HIRA 경로).
- 커밋: fetch 스크립트 다건화(ed5126b 직전)+큐레이션(bf19557). 3커밋 푸시.
- **D2 잔여(founder 게이트)**: shared postgres에 sql/ 8파일 적용(DSN) → XML 파싱→hanbang_rag_notice INSERT(manifest 기반)→/ingest 청킹·임베딩. bcrypt 실해시(CISO). 배포env 5종은 D3. VPS 잔여 probe 파일(probe*.py) 정리 필요(무해, OC 비내장).
