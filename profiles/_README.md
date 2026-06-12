# Customer Profile Schema v1

> `profiles/<slug>.yaml` 한 장이 한 고객의 모든 관습을 담는다. 7번째 축 = customer 의 누적 위치. 단, 이전 repo 와 달리 `stack.frontend` / `stack.backend` 가 추가됨 (pluggable F/B).

## Naming

- 파일명: `<slug>.yaml` — ASCII slug only (G-1). 예: `acme.yaml`, `foo-bank.yaml`.
- 한글 파일명 금지.

## Schema (v1)

```yaml
version: 1                          # 스키마 버전. 1 만 지원.

customer:
  slug: acme                        # ASCII slug, 파일명과 동일
  display: ACME 코퍼레이션          # 한글/영어 표시명 (이중)
  status: active                    # draft | active | deprecated
  contact: ops@acme.example         # 옵셔널
  industry: generic                 # generic | medical | manufacturing | logistics | finance | ...

# ── Pluggable Frontend/Backend (이 repo 의 차별화) ─────────
stack:
  frontend: react                   # nexacro | react | vue | vanilla-htmx
  backend:  springboot              # springboot | fastapi | node-express | go-chi
  frontend_options:
    react_version: 18
    state: redux-toolkit
  backend_options:
    spring_lane: jakarta            # springboot 선택 시 — jakarta | javax
    persistence: mybatis            # mybatis | jpa | jdbc
    runner: boot                    # boot | mvc

# ── DDL (Stage 2) ───────────────────────────────────
ddl:
  dialect: postgres                 # postgres | hsqldb | mysql | oracle
  schema: acme
  idempotent_strategy: on_conflict

# ── Domains (이 고객이 다루는 도메인 목록) ──────────
domains:
  - slug: customer                  # 14 baseline 중
    display: 고객
    entities: [customer, contact, address]
    seen_at: 2026-06-01             # 처음 scaffold 된 날
  - slug: order
    display: 주문
    entities: [order, order_line, fulfillment]
    seen_at: 2026-06-15
  # 산업 특수 도메인은 vertical agent 가 후속 추가
  # - slug: emr_visit              # (의료 vertical 예)
  #   display: 진료기록
  #   industry: medical

# ── Datasource (비밀값은 ${ENV_VAR} round-trip 보존) ────
datasource:
  username: ${ACME_DB_USER}
  password: ${ACME_DB_PASS}
  url_template: "jdbc:postgresql://{host}:{port}/{db}"
  host: db.acme.internal
  port: 5432
  db: acme_prod

# ── Overlay (배포 시 적용) ─────────────────────────
overlay:
  target_pkg_prefix: com.acme.app   # backend=springboot 일 때 의미
  shell_app_id: acme-portal
  maven:                            # backend=springboot && backend_options.runner=boot
    group_id: com.acme
    artifact_id_template: "{slug}-shell"
    version: 1.0.0-SNAPSHOT
  vault_agent: false                # M3 ops pack 옵션
  sso_keycloak: false               # M3 ops pack 옵션
  feedback_url: https://forms.example.com/feedback  # (optional) 데모·preview 피드백 CTA URL.
                                    # 있으면 홈 화면 하단과 푸터에 "추가 요청·의견 남기기" 링크 렌더.
                                    # 없으면(키 생략) 미표시.

# ── Defaults ───────────────────────────────────────
defaults:
  locale: ko-KR                     # 한국어 라벨 우선
  timezone: Asia/Seoul

# ── Cost tracking (per-customer ledger) ────────────
billing:
  llm_budget_usd_per_month: 100     # CTO 가 알림 임계치로 사용
  prepaid_credits_usd: 0
```

## Required Fields

- `version` (must be `1`)
- `customer.slug` (ASCII slug)
- `customer.display`
- `stack.frontend`
- `stack.backend`
- `ddl.dialect`
- `domains` (적어도 1개)

## ${ENV_VAR} Round-Trip Preservation (G-2 일반화)

`${...}` 토큰은 read/write round-trip 시 **텍스트 패치 방식** 으로 보존. yaml 라이브러리의 quote/escape 로 깨지지 않게.

테스트:
```python
profile = load_profile("profiles/acme.yaml")
save_profile("profiles/acme.yaml", profile)
# 파일 내용 = 원본 동일 (placeholder 손상 0)
```

## 작성 도움

처음 작성하는 customer 는 `domain-expert-generic` agent 에게 인터뷰 요청:

```
@domain-expert-generic 새 고객 "ACME 코퍼레이션" 의 profile 초안 작성 도움.
- 산업: 일반 SI
- 첫 도메인: 고객관리, 주문
- frontend: 미정 (질문 받음)
- backend: 미정 (질문 받음)
```

agent 가 5~10 질문으로 빈칸 채움.

## Out of Scope (v1)

- 멀티 데이터센터 (M5 SaaS 모드에서)
- per-domain 별도 stack (모든 도메인이 같은 stack 공유 — 단순성 유지)
- 도메인별 `naming.java_field` / `naming.sql_column` 분기 (스키마에 자리만, 분기 로직은 후속)
