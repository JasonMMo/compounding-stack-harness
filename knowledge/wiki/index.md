# Wiki Index — 페이지 카탈로그

> LLM 내비게이션 진입점. **모든 ingest 는 여기 1줄을 추가한다.** 형식: `- [slug](경로) — 1줄 요약 (updated: YYYY-MM-DD)`. 과거 지식 조회는 이 파일 먼저, 본문은 drill-down (규약: [README.md](README.md)).

## Sources

- [lawfirm-demo profile](../../profiles/lawfirm-demo.yaml) — 30명 법무법인, legal vertical M3 첫 고객 프로파일 초안 (updated: 2026-06-11) `[INFERRED]`
- [deep-research-design-cloud-2026-06](sources/deep-research-design-cloud-2026-06.md) — claude.ai/design 분리·통합 deep-research(8 findings, 1차출처 12종) (updated: 2026-06-26) `[EXTRACTED]`
- [deep-research-hanbang-rag-2026-06](sources/deep-research-hanbang-rag-2026-06.md) — 한의원 self-host RAG 시장성·규제·경쟁(1차) + 게이트①②(2차): **2차에서 두 게이트 조건부 통과 — 규제는 법률상 비의료기기 유력(가이드라인1건 확인 남음), corpus는 law.go.kr API 합법경로 확인(HIRA 스크레이핑 회피)**. WTP/경쟁은 별도 트랙 (updated: 2026-06-30) `[EXTRACTED]`
- [deep-research-hanbang-billing-pivot-2026-07](sources/deep-research-hanbang-billing-pivot-2026-07.md) — "공개 급여기준 검색 → 사적 청구·삭감 인텔리전스" 피벗 근거 조사: **피벗 근거 불충분**. 삭감 페인 크기 미확증·확증 분쟁은 전부 자보채널(건보 아님)·self-host 법적필연성 반대방향(소상공인 면제)·무료AI 정확도 미조사. 한의맥이 base 독점(삭감기능 백지) (updated: 2026-07-01) `[EXTRACTED]`
- [deep-research-mobile-cashflow-hedge-2026-07](sources/deep-research-mobile-cashflow-hedge-2026-07.md) — legal-rag 덩어리 파이프라인 헤지용 현금흐름 후보 발굴: 돈 버는 인디앱 7개=전부 web+1인+AI-wrapper+SEO. 톱차트=솔로 사망, 미드테일이 자리. **founder 확정=한국 커머스 셀러 AI 유틸(Tier A #1)**. 방법론: deep-research 하니스 추정치랭킹 부적합→구성적 단일에이전트 (updated: 2026-07-02) `[SYNTHESIZED]`
- [deep-research-benchmark-hunt-2026-07](sources/deep-research-benchmark-hunt-2026-07.md) — "돈 버는 앱 벤치마킹→5% 개선" 새 후보 발굴(108 agent): **깨끗한 새 SMB 버티컬 없음**. 강한 증거 수렴은 금융권 망분리(전자금융감독규정시행세칙 2026-04-20) 1개뿐인데 WTP 직접증거0·엔터프라이즈=SMB포지션 충돌. 팀챗/비번/개발툴=레드오션, 병원망분리·NineHire·SKT CCaaS=반증. **피벗 금지, 리소스는 legal-rag 유지** (updated: 2026-07-01) `[EXTRACTED]`
- [deep-research-rag-revenue-pipeline-2026-07](sources/deep-research-rag-revenue-pipeline-2026-07.md) — 제로베이스·산업무관 RAG 수익 파이프라인(엔드투엔드) 조사: **확증된 WTP는 고위험 전문서비스(법률 Harvey·금융 Hebbia)+엔터프라이즈검색(Glean)+SaaS 기능부착뿐**. 이기는 조합=고단가 seat 구독+연간계약+land-expand+도메인전문가 하이터치 CS. usage/outcome 과금 이행 0. 해자 문제는 미해결(낙관·비관 둘 다 기각). **우리 함의: legal 버티컬만 시장정렬, self-host·저터치는 이기는 GTM과 충돌** (updated: 2026-07-01) `[EXTRACTED]`

## Entities

- [legal-case](entities/legal-case.md) — 사건 생애 관리 (case_number, status 흐름, 담당변호사, 의뢰인) (updated: 2026-06-11) `[EXTRACTED]`
- [precedent](entities/precedent.md) — 판례 등록소 (citation unique key, holding/full_text, tsvector 검색) (updated: 2026-06-11) `[EXTRACTED]`
- [case-party](entities/case-party.md) — 사건 당사자 (plaintiff/defendant/witness/opposing-counsel) (updated: 2026-06-11) `[EXTRACTED]`
- [case-document](entities/case-document.md) — 사건 첨부 문서 (소장·준비서면·증거·법원명령) (updated: 2026-06-11) `[EXTRACTED]`

## Concepts

- [asset-search-architecture](concepts/asset-search-architecture.md) — 누적 자산 3-tier 검색(qmd BM25 / codegraph SQLite / ledger-index) + 측정된 성능 프로파일(체감 지연=spawn 고정비+평면원장 재파싱) + incremental cache + create-context-graph(Neo4j) 거부 결정 (updated: 2026-06-29) `[EXTRACTED]`
- [motion-tokens](concepts/motion-tokens.md) — 3 토큰 패밀리(duration/ease/stagger) + semantic.json→codegen 파이프라인 + reduced-motion override + 3-어댑터 확산 현황 (updated: 2026-06-28) `[EXTRACTED]`
- [legal-ai-search-strategy](concepts/legal-ai-search-strategy.md) — A안 augment 패턴: FTS+RAG 하이브리드 ✅ 구현·라이브(Growth-93/97), 전략 자동생성(B안) 제외 (updated: 2026-06-20) `[EXTRACTED]`
- [smb-ai-guide-lite](concepts/smb-ai-guide-lite.md) — Lite 티어: 로컬 임베딩 즉답 위젯 + 리드폼, API 비용 0, 데이터 외부 유출 0, SMB 리드젠 범용 패턴 (updated: 2026-06-18) `[SYNTHESIZED]`
- [smb-ai-market-2026h1](concepts/smb-ai-market-2026h1.md) — 시장조사 salvage: GTM 피벗 검증(AI공급 얇음·홈페이지 레드오션), self-host는 규제업종만 법적필수, 진입 use case 2(규제RAG/크몽외주) (updated: 2026-06-18) `[SYNTHESIZED]`
- [legal-rag-pattern](concepts/legal-rag-pattern.md) — 규제업종 하이브리드 검색 아키텍처: neutral catalog+dialect overlay / FTS+ANN+RRF / chunk.id 인용 무결성 / 로컬 임베딩 사이드카 (updated: 2026-06-18) `[EXTRACTED]`
- [legal-mvp-spec](concepts/legal-mvp-spec.md) — 소형 법무법인 RAG MVP 명세: 타깃·7쿼리 패턴·MVP IN/OUT 경계·WTP 가설(미검증) (updated: 2026-06-18) `[EXTRACTED]`

## Design

- [korean-ui-patterns](design/korean-ui-patterns.md) — 한국 공공/기업 SI UI 3대 패턴 + KRDS 74개 컴포넌트 + harness 통합 현황 (updated: 2026-06-12) `[SYNTHESIZED]`
- [kwcag](design/kwcag.md) — KWCAG 2.2 4원칙·명도대비·ARIA 체크리스트, 법적 근거, WCAG 차이점 (updated: 2026-06-13) `[SYNTHESIZED]`
- [korean-ux-conventions](design/korean-ux-conventions.md) — 타이포그래피·날짜/금액 표기·폼 레이아웃·버튼 텍스트·테이블 인터랙션 실무 기준 (updated: 2026-06-13) `[SYNTHESIZED]`

## Syntheses

- [lawform-competitive-analysis](syntheses/lawform-competitive-analysis.md) — 로폼 경쟁분석: 로폼=계약/대기업법무팀/생성형/구독, 소형로펌 사건축은 사각지대. killer-app K1 기일가디언·K2 이해충돌검사(사건축·검색형·self-host로 비경쟁 우회) (updated: 2026-06-25) `[SYNTHESIZED]`
- [claude-design-cloud-boundary](syntheses/claude-design-cloud-boundary.md) — claude.ai/design 워크벤치 분리·통합: 토큰 JSON 단일경계, BAA제외/학습기본 → PII 업로드금지, 빌드타임 정적 복제본(누출0·결합0·구조변경0), CI 가드5종. 설계: docs/architecture/design-cloud-bridge.md (updated: 2026-06-26) `[SYNTHESIZED]`
