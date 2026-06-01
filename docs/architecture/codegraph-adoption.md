# codegraph — 2-step Gate Measurement & Adoption Decision

> Growth-9 (2026-06-01). Growth-5f 가 `colbymchenry/codegraph` v0.9.7 을 install 하며 박은 **2-step adoption gate** 의 두 번째 step — "M1 첫 adapter Growth 마감 시 4-measurement → adopt/reject" — 의 실측·판정. install 결정 상세는 [cto.md#Growth-5f](../learn-logs/cto.md).

## 측정 환경

- 코드베이스: M1 Priority 2 완료 시점 (backend springboot-jakarta + frontend vanilla-htmx + 14 seed + contract + design tokens).
- Index 실측: **32 files / 511 nodes / 855 edges**, full reindex **780ms** parse (~2s wall), DB 1.49 MB.
- **언어별 인덱스**: python 15 / java 10 / yaml 4 / kotlin 2 / properties 1.
- **결정적 사실**: codegraph 는 **코드 언어만** 인덱스한다. `*.md` (skill seed 14, learn-logs, design patterns, contract README) 와 `*.json` (design tokens raw/semantic/persona) 은 **인덱스 0**.

## 4-Measurement 결과

### M-1 질문 답변율 — **부분 (코드 절반 O, 거버넌스 절반 X)**

Growth-5f 가 박은 canonical 질문 2종을 실측:

| 질문 유형 | 예시 | 결과 |
|---|---|---|
| **코드 구조형** ("X 가 어떻게 동작하나") | "frontend adapter 가 error envelope 를 어떻게 렌더하고 paging 을 직렬화하나" | **GOOD** — WireResponse.error / ContractLoader.httpStatusFor·messageFor 정확히 surface. (경미한 결함: frontend 질문에 backend 심볼로 치우침) |
| **인격-결정 owner형** ("누가 결정했나") | "wire entity.update PATCH-vs-PUT 결정 owner 인격 + 어느 Growth" | **FAIL** — PATCH 를 *구현한 코드* (EntityController.update, store.patch, smoke test) 만 반환. "engineer escalation → CTO Growth-5d 결정" 은 markdown ledger 에 살아 0 검출. |

→ codegraph 는 **"코드가 무엇을 하나"** 에 강하고, **"누가 왜 결정했나"** 에 무력하다. 후자가 Growth-5f 의 *원래 동기 질문* 이었다.

### M-2 7축 환류 자동화 — **약함 (diagnose.py 가 이미 더 잘함)**

- 7축 중 markdown 거주: skill (`*.seed.md`), expert-agent (`*.md`) — **codegraph 불가시**.
- json 거주: design tokens — **불가시**.
- yaml 거주: ddl catalog / customer profile / wire contract — codegraph 가시 (yaml 인덱스).
- 그러나 "축 자산 누락 탐지" 는 `scripts/diagnose.py` G-1~G-9 가 이미 **전 파일타입**(.md 포함)을 grep 으로 가드한다. codegraph 는 이 영역에서 추가 가치 미미.

### M-3 고객 가치 (lock-in 회피) — **PASS (단, 간접)**

- `.codegraph/` gitignore + source 에서 780ms 재생성 → **lock-in 0 확인**.
- 단 codegraph 는 **내부 dev 도구** — 고객은 직접 보지 않는다. "고객 가치" = CTO 탐색 속도 → 반복 비용 절감의 **간접** 효과뿐. 직접 매출/제품 가치 0.

### M-4 유지 비용 — **낮음 (단, stale 리스크)**

- 재인덱스 780ms / sync 더 빠름 / MCP stdio local / 외부 호출 0 / DB 1.5 MB.
- **숨은 비용**: 파일 watcher 가 세션 갭을 넘기지 못해 DB 가 **stale** 했다 (Growth-8 미반영, `index --force` 필요). → 큰 변경·세션 재개 후 `codegraph sync` 디스시플린 필요.

## 판정 — **조건부 ADOPT (scope 한정)**

| 항목 | 결정 |
|---|---|
| **채택 여부** | **ADOPT** — 단 **코드 네비게이션 도구** 로만. adapter/구현 작업 시 심볼 탐색·call path·impact 분석에 사용. 코드베이스가 adapter 추가로 커질수록 가치 증가. |
| **DESCOPE** | **거버넌스/결정-ownership 용도에서 명시적 제외.** "누가 왜 결정했나" 는 `docs/learn-logs/*` (per-agent ledger) + `scripts/diagnose.py` 가드가 단일 진실. codegraph 에 이 질문을 던지지 않는다. |
| **Axis 등록** | **안 함** (Growth-5f lean 확정). codegraph 는 7축을 운용하는 메타 도구지 축이 아니다. |
| **정착 위치** | 이 문서 (`docs/architecture/codegraph-adoption.md`). |
| **운영 룰** | 큰 변경·세션 재개 후 codegraph 의존 전 `codegraph sync` (또는 `index`). stale graph 리스크 차단. |
| **Tenant 분리** | 이미 충족 — `.codegraph/` 는 per-repo, gitignore, source 에서 재생성. 고객 self-host 시 그 고객의 `.codegraph/` 는 그 고객 데이터, 교차 누출 구조적으로 불가. export/sanitize API 는 M2 첫 고객 협의 시 재평가 (Growth-5f 와 동일). |
| **Reversibility** | 거부 전환 시 `codegraph uninit` (~10 min). 보존됨. |

## Open

- markdown/json 인덱스 부재는 upstream 한계 — 향후 codegraph 버전이 .md 지원 시 M-1 거버넌스 답변율 재측정 후보. 현재는 diagnose.py + ledger 분담이 정답.
- adapter 3개+ 도달 시 (M1 잔여 react/fastapi 후) 코드 네비게이션 ROI 재확인.
