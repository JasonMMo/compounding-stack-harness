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

## 클라우드 craft 브리지 (design-cloud bridge, Growth-130 WP-4 파일럿 측정)

claude.ai/design(`/design-sync`)을 **섹션 컴포넌트 craft 엔진**으로 쓰되, repo 복리·고객 인도물과 분리한다. 설계: [`docs/architecture/design-cloud-bridge.md`](../../../docs/architecture/design-cloud-bridge.md).

**언제 쓰나 (파일럿 측정 결과 기준)**:
- ✅ **재사용 섹션 컴포넌트 1건 craft** (pricing/hero 등 카탈로그 섹션) — 측정: cloud 2~3분 1-shot vs repo 코드 baseline ~25분(blind, 3 cycle). 4통증(카드정렬·하이라이트·CTA 하단고정·반응형)을 baseline 과 **독립적으로 동일 기법 수렴** = 해답 정합성 신호. export 충실도 HIGH(우리 Props/variant/DEC-3/data-loop 보존, **기존 semantic 토큰명 그대로 사용** — 예: `color-surface-1` 신규 아님 기존 소비), a11y 개선(aria-labelledby/role/focus-visible) 무료.
- ❌ **전체 UI layer 이전 금지** — 데이터 바인딩(screen-manifest typed-form) 손실 + 복리 역전(고객별 재craft) + 미세 tweak 왕복 지연. 3-tier 중 cloud 는 **authoring-only**, 경계는 토큰JSON/무명 컴포넌트뿐.

**절차 (정규화 게이트 — 비협상)**:
1. **무명 컴포넌트만 craft** — PII·고객 slug·기밀 0. claude-design 은 BAA 적용 제외·학습 기본 → 의뢰인 데이터 절대 업로드 금지. 공유 스코프 = `frontend/adapters/landing-astro/src/sections/` 한정(전체 repo 연결 = G-16 위반).
2. **인도** — claude-design 클라우드 폴더는 read-only(로컬 디스크 쓰기 불가). download 카드 → `staging/design-sync/<slug>/` 수동 배치. 파일명 ASCII slug(G-8, 공백 금지).
3. **정규화** — `python scripts/design/normalize.py staging/design-sync/<slug>`. **단, cloud 가 토큰-구동 .astro 로 self-normalize 해 오면 normalize.py 스켈레톤은 거의 redundant** — CDO 가 토큰 커버리지·variant 분해만 확인.
4. **토큰 규약 (위 §3 재적용)** — cloud 가 만든 신규 토큰(예: `shadow-card-hover`·`shadow-card-lg`)은 **theme.yaml 후보, semantic.json 직등록 금지**. 컴포넌트는 인라인 fallback(`var(--x, <기본>)`)으로 미등록 상태에서도 렌더 — 2개 테마 이상 재사용 시 semantic 승격.
5. **컨벤션 판정 (CDO, 미결)** — cloud 산출은 scoped `<style>`+시맨틱 클래스, 기존 landing-astro 섹션은 Tailwind 유틸리티. 둘 다 CSS var 토큰 소비로 동작. 혼용 vs 재표현은 라이브 다수 검증 후 결정 — 파일럿 단계에선 **production 덮어쓰기 금지, 신규 variant 로 병존**.
6. **CI 가드** — G-16~G-20(업로드스코프·결합누출·교차테넌트·DTCG스키마·정규화게이트)이 직붙임·누출 차단.

**부수 발견 — repo 시각검증 레버**: baseline 의 ~25분 blind 는 코드 결함이 아니라 `large-file-guard` 훅이 **repo 경로 하위 PNG Read 차단**한 아티팩트(scratchpad 복사 시 즉시 읽힘). 즉 단축 레버 2개 — ① cloud 도입 ② **훅을 PNG 스크린샷에 한해 완화**(②만으로 baseline 도 cloud급 단축). headless 검증: `chrome --headless --screenshot` → scratchpad PNG Read.

## Anti-patterns

- 하드코딩 hex / adapter 별 토큰 fork / contract 암묵 변경 / 페르소나 없는 단일 화면 / 장식적 복잡성 (비전문 사용자 3 페르소나가 기준)
- 기능성 섹션의 런타임 config 를 catalog schema 에 포함 → site_manifest.py 오검증 유발
- 클라우드 craft 산출의 production 직붙임(정규화 게이트 우회) / PII·고객 slug 업로드 / cloud 신규 토큰 semantic.json 직등록(theme.yaml 선행 원칙 위반)
