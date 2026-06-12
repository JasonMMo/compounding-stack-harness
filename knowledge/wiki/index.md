# Wiki Index — 페이지 카탈로그

> LLM 내비게이션 진입점. **모든 ingest 는 여기 1줄을 추가한다.** 형식: `- [slug](경로) — 1줄 요약 (updated: YYYY-MM-DD)`. 과거 지식 조회는 이 파일 먼저, 본문은 drill-down (규약: [README.md](README.md)).

## Sources

- [lawfirm-demo profile](../../profiles/lawfirm-demo.yaml) — 30명 법무법인, legal vertical M3 첫 고객 프로파일 초안 (updated: 2026-06-11) `[INFERRED]`

## Entities

- [legal-case](entities/legal-case.md) — 사건 생애 관리 (case_number, status 흐름, 담당변호사, 의뢰인) (updated: 2026-06-11) `[EXTRACTED]`
- [precedent](entities/precedent.md) — 판례 등록소 (citation unique key, holding/full_text, tsvector 검색) (updated: 2026-06-11) `[EXTRACTED]`
- [case-party](entities/case-party.md) — 사건 당사자 (plaintiff/defendant/witness/opposing-counsel) (updated: 2026-06-11) `[EXTRACTED]`
- [case-document](entities/case-document.md) — 사건 첨부 문서 (소장·준비서면·증거·법원명령) (updated: 2026-06-11) `[EXTRACTED]`

## Concepts

- [legal-ai-search-strategy](concepts/legal-ai-search-strategy.md) — A안 augment 패턴: tsvector 1단계 + RAG 2단계, 전략 생성 제외 (updated: 2026-06-11) `[INFERRED]`

## Design

- [korean-ui-patterns](design/korean-ui-patterns.md) — 한국 공공/기업 SI UI 3대 패턴 + KRDS 74개 컴포넌트 + harness 통합 현황 (updated: 2026-06-12) `[SYNTHESIZED]`
- [kwcag](design/kwcag.md) — KWCAG 2.2 4원칙·명도대비·ARIA 체크리스트, 법적 근거, WCAG 차이점 (updated: 2026-06-13) `[SYNTHESIZED]`
- [korean-ux-conventions](design/korean-ux-conventions.md) — 타이포그래피·날짜/금액 표기·폼 레이아웃·버튼 텍스트·테이블 인터랙션 실무 기준 (updated: 2026-06-13) `[SYNTHESIZED]`

## Syntheses

(없음)
