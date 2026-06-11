# Subagent Output Protocol — 결과 파일화

> 큰 subagent 산출물이 main context 로 통째 반환되면 변동비가 폭증한다.
> 지난 세션 보안 리뷰 64k 토큰이 main 으로 유입된 게 단일 변동비 주범 (HANDOFF 2026-06-11 #2).
> 이 규약은 **subagent → main 반환 경계**의 단일 진실이다. (subagent 가 내부 분석에 context-mode/ctx_execute 를 쓰는 것과는 별개 축.)

## 1. 원칙

subagent (custom 8-인격 + ad-hoc `Explore`/`general-purpose`) 가 **분석·리뷰·리포트·감사** 류의 큰 산출물을 낼 때:

> **전체 산출물은 파일로 쓰고, main 으로는 경로 + 짧은 envelope 만 반환한다.**

main session (CTO) 의 context 에는 *판정과 결정에 필요한 것*만 들어온다. 전체 근거·라인 인용·PoC·표는 파일에 남고, 필요할 때만 CTO 가 Read/ctx_execute_file 로 연다.

## 2. 임계 — 언제 파일화하나

반환 envelope 가 대략 **~30줄 또는 ~2KB** 를 넘기면 파일화한다. 그 미만의 단답(한 줄 판정, 짧은 목록)은 그냥 반환해도 된다.

판단 기준은 줄 수가 아니라 **"이게 CTO 의 다음 결정에 필요한가"** — 필요 없으면 파일로.

## 3. 산출물 위치

| 산출물 종류 | 위치 | 비고 |
|---|---|---|
| 인격별 누적 학습·판정 상세 | `docs/learn-logs/<role>.md` | 이미 각 loop step "기록·환류" 에 박혀 있음 |
| 인도물 단위 리뷰 (보안/QA/디자인 등) | `docs/delivery/<slug>/<role>-review.md` | 인도 패키지에 동행 |
| 일회성 스크래치 분석 (탐색·조사) | `out/analysis/<topic>.md` | **gitignored** (`out/`) — 재생성 가능 |

## 4. 반환 Envelope (main 으로 돌아가는 것)

순서 고정, 최대 ~30줄:

1. **판정/요약 한 줄** — `PASS` / `BLOCK` / `FAIL` / `PASS-WITH-CAVEAT` 또는 1줄 결론
2. **산출물 경로** — clickable `path:line` (CTO 가 필요 시 연다)
3. **CTO 결정·BLOCK 항목만** — 결정이 필요하거나 인도를 막는 항목 (≤5줄, 각 1줄). 없으면 생략
4. **비용 1줄** (선택) — turn 수 / 대략 \$

근거 본문·전체 표·라인별 인용·PoC 는 envelope 에 넣지 않는다 — 파일에만.

## 5. CTO 측 규율 (spawn 시)

ad-hoc agent (`Explore`/`general-purpose`) 는 자체 정의가 없으므로, **CTO 가 spawn prompt 에 명시**해야 한다:

> "전체 산출물은 `<위치>` 에 쓰고, 경로 + §4 envelope 만 반환하라."

custom 8-인격은 각자 loop SKILL 의 `## 출력 규약` 이 이 규약을 가리키므로 기본 적용된다. CTO 가 추가로 위치를 지정하면 그것을 우선한다.

## 6. Anti-patterns

- 전체 리뷰 본문을 main 으로 반환 (← 이 규약이 막으려는 것)
- 파일에 쓰고도 envelope 에 본문을 다시 복붙 (이중 비용)
- 판정만 반환하고 산출물 경로 누락 (CTO 가 근거에 닿을 수 없음)
- BLOCK 사유를 파일에만 두고 envelope 에서 생략 (인도 게이트가 안 보임)
- 스크래치 분석을 추적 경로(`docs/`)에 써서 repo 오염 (→ `out/analysis/`)
