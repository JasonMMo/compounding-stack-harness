---
name: domain-expert-loop
description: Run the domain-expert curation loop — catalog grounding, customer-language interview, profile curation from existing catalog keys only, seed PR for gaps, knowledge-store contribution. Use when domain-expert agents curate customer domains, map needs to the 14 baseline, or draft preset seeds.
---

# Domain-Expert Loop

> 실행 주체: `domain-expert-*` (`.claude/agents/domain-expert-generic.md` 외 vertical). PM 과의 경계: PM = *무엇이 필요한가*, expert = *그것이 도메인적으로 무엇인가*.

## Loop Steps

| # | 단계 | 동작 | Exit 기준 |
|---|---|---|---|
| 1 | **Catalog grounding** | `presets/ddl/catalog.yaml` 현행 entity 키 확인 — 큐레이션은 **존재하는 키에서만** (phantom 키 = scaffold 빌드 오류) | 사용 가능 키 목록 확보 |
| 2 | **사례 검색** ★지식 저장소 | `qmd search "<도메인>" -c wiki -c presets` + `knowledge/generic/verified-profiles/` — 유사 고객 사례·기존 seed 확인 | 신규/재사용 판정 |
| 3 | **인터뷰** | 고객 도메인 언어로 5~10 질문 (PM 의 needs note 가 입력). 모르는 컨벤션은 추측 말고 질문 | 도메인→baseline 매핑 초안 |
| 4 | **Profile 큐레이션** | `profiles/<slug>.yaml` domains 블록 작성 (catalog 키만). 매핑 불가 도메인 → step 5 | profile 이 scaffold.py 검증 통과 |
| 5 | **갭 처리** | catalog 미존재 entity 는 Karpathy seed 형식 (`presets/skills/<industry>/<slug>.seed.md`) PR 초안 — 직접 머지 금지, 인간 결재. vertical 신호 (baseline 매핑 불가 5+) 는 CEO 보고 | 갭 = PR 초안 또는 에스컬레이션 |
| 6 | **환류** ★지식 저장소 | 검증된 profile 사례 → `knowledge/generic/verified-profiles/` (PII 제거) + 도메인 지식 → `knowledge/wiki/concepts/` (라벨 필수: 고객 발언 `[EXTRACTED]` vs 추론 `[INFERRED]`) + index.md 1줄 | INDEX/wiki 갱신 자가 점검 |

## 지식 저장소 프로토콜

- **시작**: step 1·2 — catalog 와 사례가 인터뷰보다 먼저 (같은 질문 반복 방지).
- **종료**: step 6 — 산업 지식의 단일 누적 위치는 preset seed + wiki concepts.

## 출력 규약

큐레이션 근거·인터뷰 기록·매핑 상세는 산출물(`profiles/<slug>.yaml`·seed·wiki)에 직접 쓰거나 일회성이면 `out/analysis/<topic>.md` 에 쓰고, main 으로는 **요약 + 경로 + 갭/에스컬레이션 항목만** 반환한다 (envelope §4). 규약: [`subagent-output-protocol.md`](../../../docs/architecture/subagent-output-protocol.md).

## deliverable_kind 분기

`profiles/<slug>.yaml` 의 `stack.deliverable_kind` 가 `marketing-site` 이면 Step 1 의 grounding 대상이 달라진다.

| deliverable_kind | Step 1 grounding | Step 4 큐레이션 대상 | Step 5 갭 |
|---|---|---|---|
| `business-system` (기본) | `presets/ddl/catalog.yaml` entity 키 | profile `domains[]` 블록 | DDL entity seed PR |
| `marketing-site` | `presets/site-sections/catalog.yaml` section 타입 | profile `site.pages[].sections[]` 블록 | section-type seed (CDO 협업) |

`marketing-site` 경로에서 domain-expert 의 역할은 **산업 특화 copy 슬롯 값·KB 구조·추천 규칙** 을 제공하는 것이다 (section 타입 자체는 CDO 소유). 기능성 섹션(예: `ai-guide`)의 `ai_config` 를 채우는 도메인 지식(KB YAML 스키마, 규칙 파일 구조)도 domain-expert 가 seed 로 남긴다 — `presets/skills/<industry>/<domain>.seed.md`.

참고 사례: `presets/skills/telecom/leadgen.seed.md` (2026-06-18) — 통신 판매점 AI 즉답 패턴.

## Anti-patterns

- phantom entity 키 (Growth-14 acme-erp 교훈) / 추측 컨벤션 / 직접 머지 / 산업 특수 지식을 generic 에 욱여넣기 (vertical 에스컬레이션 대신)
- `marketing-site` 프로파일에서 DDL entity 키를 찾으려 하는 것 (위 분기표 참조)
