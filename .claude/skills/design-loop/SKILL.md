---
name: design-loop
description: Run the CDO design loop — token single-source grounding, persona mapping from the knowledge store, contract-consistency check, accessible artifact, ledger record. Use when design-agent works on design tokens, UI systems, portal/landing visuals, or persona interactions.
---

# Design Loop

> 실행 주체: `design-agent` (`.claude/agents/design-agent.md`). 하드 제약: 토큰 단일 진실 — adapter 별 재정의 금지 (CSS custom property 파이프라인, Growth-16).

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 1 | **Token grounding** | `design/tokens` 현행 확인 — 모든 비주얼 산출은 토큰에서 파생. 새 값 필요 시 토큰 추가가 먼저, 하드코딩 hex 금지 | 토큰 커버리지 판정 |
| 2 | **페르소나 검색** ★지식 저장소 | `qmd search "<페르소나> 인터랙션" -c wiki -c docs` — 고객 인터뷰의 실제 사용 맥락 (`knowledge/wiki/entities/` 고객 페이지, `[EXTRACTED]` 행동 묘사) | 페르소나별 요구 매핑 |
| 3 | **Contract 정합성** | 인터랙션이 wire-protocol contract·screen-manifest 가 제공하는 것 안에서 성립하는지 CTO 와 확인 — 디자인이 contract 변경을 암묵 요구하면 에스컬레이션 | contract 변경 요구 0 또는 보고 |
| 4 | **산출** | 페르소나 분기 (CEO=요약/지표, 업무담당자=빠른 입력, IT-담당자=설정/감사) + 접근성 (대비·키보드·라벨) 기본 적용 | 3 페르소나 + a11y 체크 |
| 5 | **검증** | 토큰 하드코딩 grep (hex 0), adapter 간 동일 토큰 소비 확인 (QA 적대 검증 대상 — Growth-16) | hex 0 + 파이프라인 일관 |
| 6 | **기록·환류** ★지식 저장소 | `docs/learn-logs/cdo.md` 갱신. 검증된 페르소나 인터랙션 패턴 → `knowledge/wiki/concepts/` + index.md 1줄 | ledger + wiki 반영 |

## 지식 저장소 프로토콜

- **시작**: step 2 — 페르소나 가정 대신 wiki 의 실제 고객 기록.
- **종료**: step 6 — 패턴이 두 고객에서 반복되면 디자인 시스템 승격 후보.

## 출력 규약

디자인 근거·토큰 표·페르소나 인터랙션 상세는 `docs/learn-logs/cdo.md` (누적) 또는 인도물 단위면 `docs/delivery/<slug>/design-review.md` 에 쓰고, main 으로는 **요약 + 경로 + 결정 항목만** 반환한다 (envelope §4). 규약: [`subagent-output-protocol.md`](../../../docs/architecture/subagent-output-protocol.md).

## 기능성(Interactive) 섹션 타입 추가 시 규약

카탈로그에 **정적 콘텐츠 셸 이상의 런타임 동작**(임베딩 추론, API 호출, 리드 제출 등)이 필요한 섹션을 신설할 때:

1. **CDO 소유 (catalog schema)**: `copy_slots`, `asset_slots`, `item_slots`, `variants` — 검증 대상 스키마에 포함.
2. **Engineer 후속 (catalog 주석)**: 런타임 기능 설정(`ai_config{}` 등)은 `site_manifest.py` 검증 대상이 **아님**. catalog YAML 주석으로 문서화하고 schema 에 포함하지 않는다.
3. **테마 토큰 확장**: 인터랙티브 컴포넌트가 필요로 하는 전용 색·반경·그림자 토큰은 `theme.yaml` 에 추가 선언 (예: `ai-guide-bg`, `ai-guide-panel` 반경). semantic.json 에 즉시 올리지 않는다 — 두 테마 이상에서 반복되면 그때 semantic 승격.
4. **contract 정합성**: 기능 동작이 wire-protocol contract 변경을 요구하면 CTO 에스컬레이션 — Step 3 기존 규칙 적용.
5. **wiki ingest**: 새 인터랙티브 패턴은 `knowledge/wiki/concepts/<slug>.md` + index.md 1줄로 즉시 환류 (Step 6).

참고 사례: `ai-guide` 섹션 타입 (2026-06-18) — `concepts/smb-ai-guide-lite.md`.

## Anti-patterns

- 하드코딩 hex / adapter 별 토큰 fork / contract 암묵 변경 / 페르소나 없는 단일 화면 / 장식적 복잡성 (비전문 사용자 3 페르소나가 기준)
- 기능성 섹션의 런타임 config 를 catalog schema 에 포함 → site_manifest.py 오검증 유발
