---
title: "Asset Search Architecture — 누적 자산 3-tier 검색"
type: concept
created: 2026-06-29
updated: 2026-06-29
sources:
  - knowledge/wiki/README.md (search coverage map)
  - scripts/ledger-index.py
  - 측정 세션 2026-06-29 (Measure-Command 분해)
  - create-context-graph 평가 (github.com/neo4j-labs/create-context-graph)
---

# Asset Search Architecture

누적 자산은 **유형에 따라 3개 검색 엔진**으로 나뉜다. 단일 통합 인덱스가 아니라, 자산의 형태에 맞는 도구를 쓰는 분할 설계다.

관련: [[legal-ai-search-strategy]] (제품 검색 패턴), [[claude-design-cloud-boundary]] (경계=정적 복제 패턴)

---

## 1. 3-tier 검색 매핑

| 데이터 유형 | 엔진 | 자료구조 | 호출 |
|---|---|---|---|
| 지식 prose (wiki/docs/presets) | **qmd search** | BM25 역색인 (FTS5) | `qmd search <q> -c <coll>` |
| 코드 심볼·엣지 | **codegraph** | SQLite 지식그래프 (MCP) | `codegraph_explore` 등 |
| 활동 원장 (learn-log + 역할원장) | **ledger-index** | 심볼-앵커 역인덱스 (JSON) | `ledger-index.py --symbol X` |

조회 규약: 통읽기 금지. qmd 는 `index.md → drill-down`, 원장은 심볼 스코프 조회, 코드는 codegraph 단일 explore. `[EXTRACTED]`

---

## 2. 측정된 성능 프로파일 (2026-06-29)

`Measure-Command` 분해로 체감 지연의 실체를 확정했다. `[EXTRACTED]`

| 항목 | 측정 | 분해 |
|---|---|---|
| qmd 바이너리 spawn | ~335ms | 고정비 (누적 무관) |
| qmd BM25 실검색 | ~30ms | 누적 무관 |
| ledger-index parse+extract | ~160ms (in-proc 콜드 85ms) | ★ **원장 길이에 선형 — 유일한 누적-민감 비용** |
| Python 기동 | ~50–200ms | 고정비 |

**핵심 발견**: 체감 "검색이 느려진다"는 *retrieval 엔진의 한계가 아니라* (a) 외부 바이너리 spawn 고정비 + (b) **평면 원장(190KB+360KB) 전체 재파싱**이다. wiki/docs 파일이 17개든 170개든 BM25 검색 자체는 ~30ms 로 일정. `[EXTRACTED]`

---

## 3. 적용된 최적화 — ledger-index incremental cache (Growth-131c)

유일한 누적-민감 지점만 정조준: `build_index()` 가 매 호출 전 원장을 재파싱하던 것을, **파일 content-hash(sha256) 기반 캐시**로 변경분만 재파싱하도록. `[EXTRACTED]`

- 캐시 대상 = parse+extract (파일 내용의 순수 함수). codegraph 검증·전역 dedup·정렬은 **매번 신선** (cg_names 는 원장과 독립 변동).
- content-hash 사용 (mtime 아님 — git checkout 의 mtime 리셋에 견고).
- 캐시(`docs/learn-logs/_index.cache.json`)는 gitignored 파생물. `_index.json` 발행 인덱스는 byte-identical 유지(검증됨).
- 효과: in-process 콜드 85ms → 웜 31ms (2.7x). 원장 누적 시 CLI 레벨에서도 발현.

---

## 4. Build-vs-Buy 결정 — create-context-graph (Neo4j) 거부 `[EXTRACTED]`

founder 가 [create-context-graph](https://github.com/neo4j-labs/create-context-graph) (Neo4j Labs, v0.9.0) 를 3-검색 앞단/메모리 대체 후보로 제시. **거부**.

| 거부 사유 | 근거 |
|---|---|
| 카테고리 불일치 | 인덱스 레이어가 아니라 **풀스택 앱 스캐폴더** — 끼울 자리 없음 |
| wedge 정면 충돌 | **Neo4j 서버 + LLM API 키**가 전제 → self-host·cost-aware·per-call-API-0 의 정반대 |
| 중복 | 우리는 이미 **임베디드** 그래프(codegraph SQLite) 보유 — Neo4j 는 무거운 중복 |
| 진단-처방 불일치 | Neo4j 가 푸는 건 다중홉 관계 추론. 우리 병은 평면파일 비대화 (§2) |

**차용한 것**: "그래프 메모리는 증분 갱신" 아이디어 → §3 incremental cache 의 self-host·인프라0 버전으로 흡수. 향후 다중홉 지식검색이 실제 니즈가 되면 기존 wiki `[[wikilink]]` 에서 **임베디드 SQLite 링크-그래프**를 빌드(서버 없이). `[INFERRED]`
