# learn-logs — 인격 ledger 2단계 아카이브 규약 (Growth-144)

> 목적: 어떤 ledger/아카이브 파일도 **100KB Read 한도**(대형 파일 skip 규칙)에 닿지 않게 한다.
> 강제: `scripts/diagnose.py` **G-22** (90KB 초과 FAIL). 조회는 `qmd search` / `scripts/ledger-index.py` 우선 — 통읽기 금지.

## 파일 계층

| 계층 | 파일 | 성격 |
|---|---|---|
| live ledger | `docs/learn-logs/<role>.md`, `learn-log.md` | 최근 엔트리만. append 대상 |
| 아카이브 볼륨 | `docs/learn-logs/archive/<name>-NN.md` | 회전분 원문. 닫히면 불변 |
| 볼륨 인덱스 | `docs/learn-logs/growth-archive.md` | main §6 회전분의 볼륨 목록 (경로 안정성 유지용) |

## 1단계 — live ledger 회전 (ledger → 아카이브 볼륨)

- **트리거**: live ledger가 **64KB** 초과.
- **동작**: 최근 ~10 엔트리만 남기고, 그 이전 엔트리를 `archive/<role>-NN.md` (열린 볼륨 끝에 append, 없으면 `-01` 신설) 로 **원문 무수정 이동**.
- live ledger의 해당 섹션 상단에 회전 pointer 1줄: `> **회전**: Growth-X ~ Growth-Y → archive/<role>-NN.md (날짜, Growth-Z)`.
- main `learn-log.md` §6 의 회전(→ growth-archive 볼륨)도 동일 규약을 따른다.

## 2단계 — 아카이브 볼륨 분할 (볼륨 캡)

- **트리거**: 열린 볼륨이 **80KB** 도달.
- **동작**: 그 볼륨을 닫고(이후 불변), `-NN+1` 새 볼륨을 연다. 이후 회전분은 새 볼륨에만 append.
- 볼륨 헤더에 커버 범위(`Growth-X ~ Growth-Y`) 명시. 인덱스 파일(있으면)에 행 추가.
- 분할 경계는 항상 엔트리(`### Growth-N`) 또는 섹션(`## `) 경계 — 엔트리를 쪼개지 않는다. 섹션 중간에서 볼륨이 갈리면 다음 볼륨에 `## ... (계속)` 헤더 반복.

## 임계값 요약

| 값 | 의미 |
|---|---|
| 64KB | live ledger 회전 트리거 (여유 있게 시작) |
| 80KB | 아카이브 볼륨 닫기 |
| **90KB** | **G-22 FAIL** — 어떤 파일이든 이 선을 넘으면 가드가 막는다 |
| 100KB | Read skip 한도 (여기 닿으면 이미 실패) |

- 제외: `_index.md` / `_index*.json` (`scripts/ledger-index.py` 생성물 — 재생성 가능, scoped 조회 전용).

## 이력

- 2026-07-05 (Growth-144): 규약 제정. growth-archive.md 265KB → 볼륨 4개(01~04) 분할 + 인덱스 전환, engineer.md 79KB → 22KB (Growth-5d~70 → `archive/engineer-01.md`).
