# Wiki Index — 페이지 카탈로그

> LLM 내비게이션 진입점. **모든 ingest 는 여기 1줄을 추가한다.** 형식: `- [slug](경로) — 1줄 요약 (updated: YYYY-MM-DD)`. 과거 지식 조회는 이 파일 먼저, 본문은 drill-down (규약: [README.md](README.md)).

## Sources

- [lawfirm-demo profile](../../profiles/lawfirm-demo.yaml) — 30명 법무법인, legal vertical M3 첫 고객 프로파일 초안 (updated: 2026-06-11) `[INFERRED]`
- [deep-research-design-cloud-2026-06](sources/deep-research-design-cloud-2026-06.md) — claude.ai/design 분리·통합 deep-research(8 findings, 1차출처 12종) (updated: 2026-06-26) `[EXTRACTED]`
- [deep-research-hanbang-rag-2026-06](sources/deep-research-hanbang-rag-2026-06.md) — 한의원 self-host RAG 시장성·규제·경쟁: **규제 게이트 미통과(SaMD 안전항 0-3 반증), 비임상 HIRA 급여청구 corpus 만 안전, WTP/경쟁 미검증**. legal-rag 포팅은 엔지니어링 저리스크 (updated: 2026-06-30) `[EXTRACTED]`

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
