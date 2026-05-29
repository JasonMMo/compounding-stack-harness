# Swappable Layers Architecture

> 3-tier 중 **Middle layer 만 stable**, Frontend / Backend 는 customer 가 교체. 이전 repo 의 G-69 (web→subprocess single-source) + G-79 (web→adapter single-source) 가 일반 원칙으로 격상됨.

## 1. The Three Tiers

```
┌──────────────────────────┐    ┌────────────────────────┐    ┌──────────────────────────┐
│  Frontend adapter        │    │  Middle: wire-protocol │    │  Backend adapter         │
│  (pluggable)             │←──→│  contract              │←──→│  (pluggable)             │
│                          │    │  (stable, single src)  │    │                          │
│  - nexacro               │    │                        │    │  - springboot (jakarta)  │
│  - react                 │    │  - request schema      │    │  - springboot (javax)    │
│  - vue                   │    │  - response schema     │    │  - fastapi (python)      │
│  - vanilla-htmx          │    │  - error envelope      │    │  - node-express (ts)     │
│  - (open for new)        │    │  - paging contract     │    │  - go-chi                │
│                          │    │  - file upload contract│    │  - (open for new)        │
└──────────────────────────┘    └────────────────────────┘    └──────────────────────────┘
```

## 2. 왜 Middle 만 stable 인가

**Frontend 와 Backend 는 고객사 정치 문제**. 의료 SI 는 Nexacro, 스타트업은 React, 공공기관은 jQuery 가 표준. Backend 도 마찬가지 — 금융은 Java EE javax, 신생 은행은 Spring Boot Jakarta, 디지털 네이티브는 FastAPI/Go.

**Middle 은 정보 모델 문제**. 한 도메인의 entity·관계·검증 규칙은 frontend/backend 선택과 무관하다. 이걸 stable 로 두면:

- Frontend adapter 추가 비용 = 1주 (contract 를 그 프레임워크 어법으로 렌더링)
- Backend adapter 추가 비용 = 1~2주 (contract 를 그 프레임워크의 라우터/스키마로 렌더링)
- contract 자체는 **고객 도메인 + customer profile 만으로 결정**되므로 재사용 100%

## 3. Customer 가 교체하는 방법

`profiles/<slug>.yaml` 한 줄로 결정:

```yaml
version: 1
customer:
  slug: acme

stack:
  frontend: react           # nexacro | react | vue | vanilla-htmx
  backend:  springboot      # springboot | fastapi | node-express | go-chi

  # 각 adapter 의 sub-flavor (선택 사항)
  frontend_options:
    react_version: 18
    state: redux-toolkit
  backend_options:
    spring_lane: jakarta    # jakarta | javax
    persistence: mybatis    # mybatis | jpa | jdbc
    runner: boot            # boot | mvc
```

orchestrator 가 `stack.frontend` 와 `stack.backend` 를 읽어 해당 adapter 로 dispatch. customer 는 **2 줄만 바꾸면** 같은 도메인을 Nexacro+SpringBoot 에서 React+FastAPI 로 옮겨 받을 수 있다.

## 4. Middle Contract — Single Source 원칙

Frontend / Backend adapter 는 contract 의 정의를 **읽기만** 한다. **재구현 금지**.

이전 repo 의 두 가드를 일반 원칙으로:

- **이전 G-69** (web→`scripts/scaffold_cli.py` subprocess 만): web 경로가 codegen 로직을 재구현하면 6축 누적이 web 사용자에게만 우회되어 깨진다.
- **이전 G-79** (web→`extract_target_profile` 단일 호출): adapter 가 parser 를 재구현하면 maven/gradle 분기가 두 곳에 살아 drift.

→ **새 일반 원칙 (G-?, 첫 가드)**: Frontend/Backend adapter 안에서 `middle/contract/*` 에 정의된 schema/validator/error-envelope 를 **참조만** 한다. 같은 로직을 adapter 내에서 재선언하는 것을 정적으로 금지 (`scripts/workflow/diagnose.py` 가 grep 으로 가드).

## 5. Wire-Protocol Contract 의 구성

`middle/contract/` 디렉터리에 들어가는 것:

```
middle/contract/
  request/
    list.schema.yaml          # 목록 조회 request 표준
    detail.schema.yaml        # 단건 조회
    create.schema.yaml
    update.schema.yaml
    delete.schema.yaml
  response/
    envelope.schema.yaml      # 에러 코드, 메시지, payload 위치
    list.schema.yaml
    detail.schema.yaml
  paging/
    cursor.spec.md            # cursor 기반 페이징 규약
    offset.spec.md            # offset 기반 페이징 규약
  error/
    codes.yaml                # 표준 에러 코드 + 메시지
  upload/
    multipart.spec.md
```

각 adapter 는 이 contract 를 **자기 프레임워크의 어법으로 직렬화/역직렬화**. contract 변경 시 모든 adapter 가 갱신되도록 `diagnose.py` 가 enforcement.

## 6. Adapter Compliance Test

새 adapter 추가 시 통과해야 하는 게이트:

1. **Contract round-trip**: contract 의 모든 schema 를 그 adapter 가 emit/parse 가능
2. **Error envelope**: 표준 에러 코드를 그 adapter 가 모두 표현 가능
3. **Paging**: cursor + offset 둘 다 emit 가능
4. **풀테스트 L1+L2+L3+L4** 전체 그린

`tests/adapters/<kind>/test_compliance.py` 가 표준 테스트셋. 새 adapter 는 그 테스트셋만 패스시키면 머지.

## 7. 첫 구현 우선순위 (M1)

| Adapter | 이유 |
|---|---|
| **Backend: springboot-jakarta** | 시장 친화 (Java 17+, 새 프로젝트 표준) |
| **Backend: fastapi** | 매출 hedge (Python 시장, 도메인 전문가 agent 와 자연스러운 결합) |
| **Frontend: vanilla-htmx** | 빠른 검증 (LLM 호출 없이 데모 가능, 비용 0) |
| **Frontend: react** | 시장 친화 (스타트업/모던 SI) |

Nexacro frontend adapter 는 M2 이후 (이전 repo 자산 포팅) — 한국 SI 시장 진입 시점에 추가.

## 8. Open Questions

- Middle contract 의 직렬화 형식: OpenAPI 3.1 / JSON Schema / gRPC IDL / 자체 YAML?
  - 현재 선호: **OpenAPI 3.1 + 자체 확장** — 산업 표준 + adapter 도구 풍부.
- Adapter 가 의존하는 contract 버전 관리: SemVer + adapter 가 지원 범위 선언.
- Frontend 의 i18n: contract 안에 (locale 별 라벨 표준화) vs adapter 자유 — **현재 선호: contract 안**. 한국어/영어 라벨이 customer profile 에 일원화되도록.
