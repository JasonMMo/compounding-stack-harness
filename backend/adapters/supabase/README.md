# backend/adapters/supabase — Supabase Backend Adapter

> **상태**: implemented (M1). Supabase managed PostgreSQL + PostgREST 를
> middle wire-protocol contract 와 연결하는 swap-compatible backend adapter.

## 목적

소규모 고객이 자체 DB 서버 운영 부담 없이 Supabase 의 hosted PostgreSQL 을
사용할 수 있도록 한다. Customer profile 에서 `stack.backend: supabase` 를
지정하면 fastapi 대신 이 adapter 가 활성화된다.

| 항목 | 설명 |
|---|---|
| kind | `supabase` |
| 스택 | PostgREST (via httpx) + FastAPI shared routers |
| 상태 | implemented — unit tests 16/16 PASS |
| 포트(기본) | 8081 (env `PORT` 로 변경 가능) |

## 격리 원칙

- middle contract (`middle/contract/wire-v1.yaml`) 를 **읽기만** 한다. 재구현 금지 (G-1).
- PostgREST 호출은 `supabase_client.py` / `supabase_store.py` 내부에만 위치.
- 교체: `stack.backend: supabase` → `stack.backend: fastapi` 로만 변경하면 된다.

## sys.modules 세임(Seam) 메커니즘

`main.py` 는 shared fastapi routers 를 import 하기 **전에** 다음 순서로 실행한다:

```python
import supabase_store
sys.modules["store"] = supabase_store   # routers의 `from store import entity_store` → 우리 것
sys.path.insert(0, FASTAPI_DIR)         # shared wire_response, catalog_validator, routers/* 공유
from routers import auth, entity, status
```

fastapi adapter 파일을 **한 줄도 수정하지 않고** store 만 교체한다. Open-closed 원칙.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `supabase_client.py` | httpx.Client 팩토리 + 모듈 레벨 싱글톤. env 검증 (fail-fast). |
| `supabase_store.py` | `SupabaseEntityStore` + `entity_store` 싱글톤. 6-method interface. catalog slug→table 해석. |
| `main.py` | 세임 주입 + FastAPI app (auth/entity/status 라우터). |
| `requirements.txt` | fastapi, uvicorn, httpx, pyyaml, python-dotenv |
| `Dockerfile` | 빌드 컨텍스트 = repo root. fastapi adapter dir + middle/contract + presets/ddl 복사. |
| `tests/test_supabase_store.py` | httpx.MockTransport 기반 unit tests (16개). |
| `../../presets/ddl/supabase-rls/README.md` | RLS 정책 가이드 + copy-paste SQL 템플릿. |

## 환경 변수

```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>   # 서버사이드 전용 — RLS 우회
```

두 변수 중 하나라도 없으면 서버 시작 시 `RuntimeError` 로 즉시 실패한다.

`SUPABASE_ANON_KEY` 는 이 adapter 에서 사용하지 않는다 (서버사이드 전용 설계).

## 실행

```bash
# 로컬
cd backend/adapters/supabase
SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... uvicorn main:app --port 8081

# Docker (repo root 에서)
docker build -f backend/adapters/supabase/Dockerfile -t compounding-supabase .
docker run -e SUPABASE_URL=... -e SUPABASE_SERVICE_ROLE_KEY=... -p 8081:8081 compounding-supabase
```

## 테스트 실행

```bash
cd backend/adapters/supabase
pip install httpx pyyaml
python -m pytest tests/ -q
# Expected: 16 passed
```

## Slug → Table 해석

`presets/ddl/catalog.yaml` 의 `table:` 필드를 import 시 캐시한다.

| 예시 | 해석 |
|---|---|
| `employee` | `hr_employee` (catalog hit) |
| `department` | `hr_department` (catalog hit) |
| `stock-level` | `stock_level` (catalog miss → hyphen→underscore fallback) |

## L4 Live Activation (Supabase 프로젝트 생성 후 — 턴키 순서)

unit 16 PASS 는 `httpx.MockTransport` 기반(네트워크 0)이라 L4 live 와 별개다.
아래는 파운더가 Supabase 프로젝트를 프로비저닝한 뒤 실행하는 순서다.

1. **프로젝트 프로비저닝 (인터랙티브, 파운더 전용)** — `https://supabase.com/dashboard`
   로그인 → New project → region/비밀번호 설정. (계정·프로젝트 생성은 자동화 불가.)
2. **env 채우기** — `infra/secrets/supabase.env.example` 를 `infra/secrets/supabase.env`
   로 복사 후 두 값 입력 (Project Settings > API: Project URL + service_role secret).
   `supabase.env` 는 gitignored 볼트 — 절대 커밋 금지.
3. **스키마 적용** — Supabase SQL Editor 에서 `presets/ddl/supabase-rls/README.md`
   의 컬럼 기본값(`id`/`created_at`/`updated_at`) + `set_updated_at` 트리거 + 엔티티
   테이블 DDL(`python scripts/workflow/render.py` 산출물) 실행. catalog `table:` 명과
   일치해야 slug→table 해석이 맞는다.
4. **L4 smoke** — env 로드 후:
   ```powershell
   # infra/secrets/supabase.env 의 두 값을 환경변수로 로드한 뒤
   uvicorn main:app --port 8081   # backend/adapters/supabase 에서
   # 다른 터미널: 한 엔티티에 대해 create→get→patch→delete HTTP 라운드트립 확인
   #   POST /api/v1/entity/<slug> ; GET .../{id} ; PATCH .../{id} ; DELETE .../{id}
   ```
   기대: 4-메서드 round-trip rc=0, PostgREST 가 id/created_at/updated_at 채움.
5. **결과 환류** — 통과 시 본 README 상태 → `live-verified`, learn-log Growth 엔트리.

## Open Loops (구현 보류 항목)

1. **L4 live 테스트**: Supabase 프로젝트 미존재 → live 미실행. 위 "L4 Live Activation"
   순서대로 프로비저닝 후 실행 (env 템플릿 `infra/secrets/supabase.env.example`).

2. **Supabase Auth (GoTrue) 통합 보류**: 현재 shared `routers/auth.py` 의
   in-memory demo/demo 인증 재사용. 실제 multi-user 인증은 GoTrue JWT +
   per-user RLS 정책 필요 (M5 milestone 예정).

3. **filter/sort/paging 푸시다운 보류**: 현재 entity router 가 Python 에서
   처리. 대규모 테이블에서는 PostgREST WHERE/ORDER BY/LIMIT/OFFSET 으로
   푸시다운해야 성능 확보 가능 (TODO in `supabase_store.py::find_all`).

4. **RLS 정책**: `presets/ddl/supabase-rls/README.md` 에 스타터 SQL 템플릿
   제공. service_role 은 RLS 를 자동 우회. 테넌트별 정책은 M5 범위.

## self-host 옵션

Supabase 를 자체 서버에 설치하는 경우 (Coolify 지원):
- `SUPABASE_URL` 을 내부 IP 로 변경
- Coolify → Docker Compose 방식으로 배포 가능
- 상세: [`docs/architecture/deployment-topology.md`](../../docs/architecture/deployment-topology.md)
