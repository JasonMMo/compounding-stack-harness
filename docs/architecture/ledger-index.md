# Ledger Index — 심볼-앵커 교차-인격 검색 인덱스

> Self-improve 지식 누적의 context-weight + cross-agent 통증을 해결하는 경량 인덱스.
> think-grid (`D:\AI\workspace\think-grid\README.md`) 의 *아이디어*(심볼에 앵커된 학습 + 백링크 검색)만 흡수하고,
> 그 *인프라*(sync-graph.js mirror / Obsidian / node+sqlite3)는 **채택하지 않는다** — codegraph 와 기존 원장을 재사용.

## 1. 문제

`learn-log.md` (327줄) + `docs/learn-logs/<role>.md` 6 인격 원장 (Σ860줄, 계속 증가) 은 **시간순 prose**다.
"`CatalogValidator` 에 대해 engineer·QA 가 각각 뭘 배웠나" 를 알려면 295줄+214줄을 통째로 읽어야 한다 →
① 누적될수록 context 무거움 ② CTO 의 cross-agent 통합이 O(전체) 비용.

think-grid 이 짚은 빠진 조각 = **심볼에 앵커된 역인덱스**. 단 think-grid 처럼 codegraph 를 markdown 으로 복제하면
방금 token-savior→codegraph 로 없앤 "코드그래프 2개" redundancy 가 재발하므로, **인덱스만** 만든다.

## 2. 설계 계약

신규 자산 **1개**: `scripts/ledger-index.py` (diagnose.py 의 형제, pure-local, 0 LLM, 0 신규 인프라 — sqlite3 는 stdlib).

### 2.1 입력
- `learn-log.md` (agent = `main`)
- `docs/learn-logs/{cto,engineer,qa,cdo,cmo}.md` (agent = 파일 stem)
- **제외**: `synthesis-template.md` (템플릿, 엔트리 아님)

### 2.2 엔트리 파싱
- 구분자 정규식: `^### Growth-(\d+) \((\d{4}-\d{2}-\d{2})\)\s*[—-]?\s*(.*)$` → `(growth_n, date, title)`
- agent: `# learn-log — <Role>` H1 또는 파일 stem 매핑. main `learn-log.md` → `main`.
- 한 엔트리의 body = 다음 `### ` 직전까지.

### 2.3 앵커 추출 (엔트리가 다루는 심볼 집합)
1. **File 앵커**: `- Files touched:` 필드의 경로 list.
2. **Symbol 후보**: 엔트리 body 안의 백틱 토큰 `` `Foo` `` + `[[wikilink]]` 타깃.
3. **codegraph 교차검증**: `.codegraph/codegraph.db` 를 **READ-ONLY** 로 열어 `SELECT DISTINCT name FROM nodes` 1회 로드 →
   후보가 실존 심볼이면 `verified:true`, 아니면 **drop 하지 말고** `unverified` 로 분류 (feedback-guards-must-work: 데이터 silent 손실 금지).

### 2.4 출력 — `docs/learn-logs/_index.json`
```json
{
  "generated_from_commit": "<git rev-parse HEAD>",
  "symbols": {
    "CatalogValidator": [
      {"agent":"engineer","growth":12,"date":"2026-06-01","title":"...","file":"docs/learn-logs/engineer.md","verified":true}
    ]
  },
  "files": { "backend/adapters/fastapi/...": [ {"agent":"...","growth":12,"...":"..."} ] },
  "unverified": [ {"symbol":"...","agent":"...","growth":12,"...":"..."} ]
}
```
- **wall-clock 금지**: 타임스탬프 대신 `generated_from_commit` = `git rev-parse HEAD`. 내용 무변경 시 재빌드해도 JSON diff 0 (clean git).
- `--md` 플래그(옵션): `_index.md` 사람 가독 버전 (심볼 → bullet). Option-C(Obsidian) 로 가는 문을 싸게 열어둠 — 지금은 기본 off.

### 2.5 CLI
| 명령 | 동작 |
|---|---|
| `python scripts/ledger-index.py` | 인덱스 빌드 (`_index.json` 갱신) |
| `--symbol <name>` | 해당 심볼 엔트리만 출력 — **에이전트 검색 경로** (전체 원장 read 대체) |
| `--check` | stale 앵커(과거 verified→현재 codegraph 부재) 있으면 list + rc=1 — **G-11 가드 후보** (지금은 게이트 아님) |
| `--md` | `_index.md` 동시 출력 |

## 3. 제약 준수
- **G-8 ASCII slug**: `_index.json` / `_index.md` ASCII ✅.
- **최소 영향**: 기존 860줄 retrofit **불필요** — 백틱/Files-touched 에서 auto-추출. 앞으로 명시 앵커는 additive 옵션.
- **charter §5 비용**: 0 LLM, 0 신규 infra (sqlite3 stdlib). codegraph DB 는 읽기만.
- **codegraph 재사용**: think-grid 의 sync-graph.js mirror 대신 codegraph.db 를 검증 소스로만 read → 코드그래프 2개 재발 방지.

## 4. 운영 룰
- 각 Growth 엔트리 마무리 시 `python scripts/ledger-index.py` 재빌드 (추후 `/contribute-back` 에 hook 후보).
- 에이전트 cross-agent 통합: 전체 원장 read 대신 `--symbol` 로 scoped 조회.
- **`_index.json` / `_index.md` 는 gitignore** — `.codegraph/` 와 동일한 *재생성 가능 로컬 캐시*. (초안 §4 는 commit 을 제안했으나 CTO 가 번복: `generated_from_commit` 이 HEAD 를 담아 커밋마다 stale → noisy diff. 소스 원장이 단일 진실, 인덱스는 파생물.)

## 5. 비채택 결정 기록 (think-grid 대비)
| think-grid 요소 | 우리 결정 | 이유 |
|---|---|---|
| `sync-graph.js` (codegraph→.md mirror) | **비채택** | codegraph 중복, .md churn. 인덱스만. |
| Obsidian Graph View 의존 | **비채택** (문은 `--md` 로 열어둠) | 인간 전용 시각화, 에이전트 context 절감 아님 |
| `.context/` vault | **비채택** | dormant skeleton, 우리 `docs/learn-logs/` 와 중복 |
| node + sqlite3 driver | **비채택** | Python stdlib sqlite3 로 충분, 신규 의존 0 |
