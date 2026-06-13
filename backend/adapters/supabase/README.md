# backend/adapters/supabase — Supabase Backend Adapter (Planned)

> **상태**: scaffold (미구현). Supabase managed PostgreSQL + Auth + Storage 를 middle wire-protocol contract 와 연결하는 adapter.

## 목적

소규모 고객이 자체 DB 서버 운영 부담 없이 Supabase 의 hosted PostgreSQL 을 사용할 수 있도록 한다.

| 항목 | 설명 |
|---|---|
| kind | `supabase` |
| 스택 | Supabase JS/Python SDK + PostgREST |
| 상태 | planned — customer profile `stack.backend: supabase` 지정 시 활성화 |
| 포트(기본) | N/A (managed cloud or self-hosted Supabase) |

## 격리 원칙

- middle contract (`middle/contract/wire-v1.yaml`) 를 **읽기만** 한다. 재구현 금지 (G-1).
- Supabase SDK 호출은 이 adapter 내부에만 위치. 다른 adapter 나 server.py 에 누출 금지.
- 교체: `stack.backend: supabase` → `stack.backend: fastapi` 로만 변경하면 된다.

## 구현 계획

1. `supabase_client.py` — Supabase Python 클라이언트 초기화 (SUPABASE_URL, SUPABASE_ANON_KEY env vars)
2. `store.py` — InMemoryStore 와 동일 인터페이스, 내부만 Supabase REST/PostgREST 로 교체
3. 8 wire key REST 경로 구현 (backend/adapters/INDEX.md §공통 계약 동일)
4. RLS (Row Level Security) 정책 가이드 — 고객용 `presets/ddl/supabase-rls/` 에 배치
5. 공유 compliance suite 통과 — `ADAPTER_BASE_URL=<supabase-url> pytest tests/adapters/springboot-jakarta/ -v`

## 환경 변수

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>   # 서버사이드 전용
```

## self-host 옵션

Supabase 를 자체 서버에 설치하는 경우 (Coolify 지원):
- `SUPABASE_URL` 을 내부 IP 로 변경
- Coolify → Docker Compose 방식으로 배포 가능
- 상세: [`docs/architecture/deployment-topology.md`](../../docs/architecture/deployment-topology.md)
