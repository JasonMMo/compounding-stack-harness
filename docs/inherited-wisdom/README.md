# Inherited Wisdom — 7 Meta-Lessons

> 이전 repo [business-fullstack-creater](https://github.com/) 의 79 Growth 경험에서 추출한 **메타 교훈**. 코드는 가져오지 않음. 트랩 번호 (G-47/50/77 등) 도 가져오지 않음. **원리만** 가져옴.

새 repo 에서는 이 7가지가 **첫 줄부터 가드/구조/컨벤션** 으로 들어가야 한다.

## Lesson 1 — Wire-Protocol Source of Truth in Codegen

**증상**: 한 codegen 산출물의 동일 정보 (예: HTTP 라우트, 에러 코드) 가 두 곳 이상에서 선언되면 시간이 갈수록 drift. 어느 한쪽이 진실인지 모호해진다.

**규칙**: 모든 codegen 은 **단일 wire-protocol contract** 를 source of truth 로 두고, frontend/backend adapter 가 그것을 **읽기만** 한다. 재선언 금지.

**이 repo 적용**: `middle/contract/` 디렉터리가 single source. `diagnose.py` 가 "adapter 내부에서 contract 키 재정의" 를 정적 검출.

→ `swappable-layers.md` §4

## Lesson 2 — Context Path Consistency Requires Dual Guards

**증상**: 한 URL 컨텍스트 경로 (예: `/uiadapter`) 가 라우터·디스패처·런처·문서 4곳에 박혀있는데 한 곳을 바꾸면 나머지가 깨진다.

**규칙**: 컨벤션 경로는 **단일 상수** 에서 emit + **정적 가드** 가 "다른 곳에서 같은 문자열을 hardcode 하는 것" 을 검출. 한 가드만으로는 부족 — emit + grep 두 겹.

**이 repo 적용**: 컨텍스트 경로는 customer profile + middle contract 에 1회 선언. adapter 가 동일 문자열을 별도 hardcode 하면 `diagnose.py` 가 거부.

## Lesson 3 — Single-Source Delegation + Static Guard (G-69/G-79 일반화)

**증상**: web layer 가 빠르다고 codegen 로직을 자체 구현하면, CLI 와 web 산출물이 drift. 6축 누적이 web 사용자에게만 우회된다.

**규칙**: 새 진입점 (web, IDE 플러그인, API 등) 은 기존 진입점의 **함수 호출** 또는 **subprocess** 로만 위임. 재구현 금지. 정적 가드가 "재구현 패턴" 을 grep 으로 검출.

**이 repo 적용**: 새 진입점 추가 시 `diagnose.py` 가드 동반 머지가 머지 조건.

## Lesson 4 — `${ENV_VAR}` Round-Trip Preservation

**증상**: YAML 파서가 `${DB_PASS}` 같은 placeholder 를 평문으로 해석하거나 quote 처리하면 customer profile round-trip 시 비밀값이 깨진다.

**규칙**: customer profile YAML 의 `${...}` 토큰은 read/write round-trip 시 **텍스트 패치 방식** 으로 보존. yaml 라이브러리 자동 직렬화 금지.

**이 repo 적용**: `profiles/` 의 모든 read/write 는 round-trip safe helper 경유. 단위 테스트 필수.

## Lesson 5 — Asset-Exposure Harness Pattern

**증상**: 축적된 자산 (preset, guard, agent) 이 디렉터리에 묻혀 있어서 사용자가 "지금 뭘 쓸 수 있는지" 모른다. 자산이 보이지 않으면 누적 효과도 안 보인다.

**규칙**: 모든 축의 누적 상태가 **자동 노출되는 web/CLI 인터페이스** 가 있어야 한다. 예: status board, asset index page, `/list-presets`.

**이 repo 적용**: M1 에 generic harness baseline 의 일부로 `/status` 페이지 (포털) 우선 작성. preset/agent 개수 + 가드 개수 + customer 개수 1눈에.

## Lesson 6 — Self-Host Single-Mode + Multi-Condition Gate

**증상**: self-host 와 SaaS 를 처음부터 둘 다 지원하려 하면 양쪽 의사결정 비용이 곱셈으로 증가. 어느 쪽도 깊지 못함.

**규칙**: **단일 모드 (self-host)** 로 시작. SaaS 등 2번째 모드 진입은 **다조건 AND 게이트** (예: customer N개 + 매출 \$M + 보안 인증 + 멀티테넌트 격리 검증) 충족 시에만.

**이 repo 적용**: M1~M4 self-host only. M5 SaaS 는 charter §게이트 명시.

## Lesson 7 — Persona-Driven Gating

**증상**: "이 기능 끝났어?" 의 합의가 안 됨. 개발자는 코드를, PM 은 데모를, 고객은 운영을 본다.

**규칙**: 모든 milestone 의 인수 기준은 **명시적 페르소나가 그 기능을 사용한다** 로 표현. "코드 작성 완료" 가 아니라 "<페르소나> 가 <행동> 을 <시간> 안에 완료".

**이 repo 적용**: 3 페르소나 (CEO / 업무담당자 / IT-담당자) 가 모든 milestone 인수 기준에 등장. revenue-roadmap.md 의 모든 milestone 이 페르소나·시간·산출물 명시.

---

## What we did NOT inherit

- 이전 repo 의 18 trap guards (G-47, G-50a, G-77 등) — **번호는 폐기**. 원리만 위 7 lesson 으로. 새 repo 는 G-1 부터 자기 가드 번호.
- 이전 repo 의 14 preset 내용 — **재작성**. nexacro/uiadapter 가정 제거.
- 이전 repo 의 코드 — **0 copy**. 영감만.
- 이전 repo 의 customer profile `profiles/acme.yaml` 같은 샘플 — 새 schema 에 맞춰 새로.

## Why not copy

이전 repo 의 모든 자산은 nexacro/uiadapter 강결합과 한국 SI 컨텍스트에 깊이 박혀있다. 일반화하려면 **재해석 비용 > 재작성 비용**. 메타 교훈만 7개 추출해서 첫 줄부터 박는 게 훨씬 빠르다.

## How to use this folder

- M1 진입 전: 7 lesson 을 위 7 가드 (G-1 ~ G-7) 로 `diagnose.py` 에 박는다.
- M1 진행 중: 새 guard 추가 시 7 lesson 중 어디에 해당하는지 명시.
- Quarterly: 7 lesson 자체를 재검토 — 새 메타 교훈 추가 가능 (Lesson 8+).
