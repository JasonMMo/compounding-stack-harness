# Backend Adapters — Axis Manifest

> Pluggable **backend** 축 (CLAUDE.md §3, §4). 각 adapter 는 middle wire-protocol contract (`middle/contract/`) 를 **읽기만** 하여 자기 프레임워크 어법으로 직렬화한다. contract 재구현 금지 (G-1). customer profile 의 `stack.backend` 한 줄로 교체.

## 등록된 adapter

| kind | 스택 | 상태 | 포트(기본) | 등록 |
|---|---|---|---|---|
| **springboot-jakarta** | Spring Boot 3.2.5 / Jakarta EE / Java 17 / Gradle | M1 — 23/23 compliance, L1/L4 green | 8080 | Growth-7 |
| **fastapi** | FastAPI / Uvicorn (ASGI) / Python 3.11+ | M1 — L1 16/16, shared compliance suite green | 8081 | Growth-11 |

> 로드맵 후보 (swappable-layers.md §7): node-express (ts), go-chi. javax lane Spring 은 금융 레거시 게이트 시.

## 공통 계약 (모든 backend adapter)

- **8 wire key** REST 매핑 (동일 경로 — compliance suite 가 path-coupled):
  `auth.login`→POST /api/auth/login · `auth.logout`→POST /api/auth/logout ·
  `entity.read`→GET /api/entities/{type}/{id} · `entity.list`→GET /api/entities/{type} ·
  `entity.create`→POST /api/entities/{type} · `entity.update`→PATCH /api/entities/{type}/{id} ·
  `entity.delete`→DELETE /api/entities/{type}/{id} · `status.health`→GET /api/status/health
- **런타임 contract 로드** — `codes.yaml` (code→http_status) + `wire-v1.yaml` 을 기동 시 읽음. 하드코딩 0 (G-1).
- **error envelope** — `{ "error": { "code", "message", "details"? } }`, http_status 는 codes.yaml.
- **flat-underscore paging** — `paging_mode`/`paging_page`/`paging_size`/`paging_cursor`/`sort_field`/`sort_direction` (Growth-7 표준, dot-notation 금지).
- **idempotent delete** — 404→success. **PATCH semantics** — 공급된 필드만 병합, id 불변.

## 공유 compliance suite — adapter-agnostic 검증

`tests/adapters/springboot-jakarta/test_compliance.py` 는 `ADAPTER_BASE_URL` 로 파라미터화된 **black-box HTTP** suite. **모든 backend adapter 가 동일 suite 를 통과해야 머지** (swappable-layers §6).

```bash
# 어느 backend adapter 든 동일 suite:
ADAPTER_BASE_URL=http://localhost:8081 pytest tests/adapters/springboot-jakarta/ -v
```

Growth-11 에서 fastapi 가 이 suite 를 그대로 통과 = "한 wire contract 가 Java·Python 두 backend 를 동일하게 구동" 차별화 실증 + suite 가 진짜 adapter-agnostic 임을 검증.

## 새 backend adapter 추가 절차

1. `backend/adapters/<kind>/` 에 contract 런타임 로더 + 8 wire key REST (위 경로 정확히) + in-memory store 구현.
2. G-1 준수 — code→http_status 재선언 0 (codes.yaml 런타임 읽기).
3. 위 공유 compliance suite 를 `ADAPTER_BASE_URL` 로 자기 adapter 에 겨눠 green.
4. 4계층 풀테스트 (L1/L3/L4; L2 는 ddl 축) + 이 표에 행 추가.
5. README.md (이 axis 의 README 구조 미러).
