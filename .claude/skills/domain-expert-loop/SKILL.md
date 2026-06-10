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

## Anti-patterns

- phantom entity 키 (Growth-14 acme-erp 교훈) / 추측 컨벤션 / 직접 머지 / 산업 특수 지식을 generic 에 욱여넣기 (vertical 에스컬레이션 대신)
