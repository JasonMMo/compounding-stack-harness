# learn-log — Engineer

> Implementation hand. CTO 가 결정한 설계를 코드로 옮기는 인격의 ledger.

main 인덱스: [`../../learn-log.md §6`](../../learn-log.md). 인격 헌장: [`.claude/agents/engineer-agent.md`](../../.claude/agents/engineer-agent.md).

## §1 — Decision Log Format

각 항목:

```
### Growth-N (YYYY-MM-DD) — <title>
- Files touched: <경로 list>
- Implementation choices: <변수명·구조·error handling 등 인격 단독 결정>
- Tests added: <4계층 중 어느 layer>
- Catches surfaced: <CTO/QA 에 던진 escalation 신호>
- Cost: <turns / 추정 $>
```

## §2 — Growth History

### Growth-5d (2026-05-29) — M1 entry kickoff: wire-v1 contract + acme-erp profile

- Files touched:
  - `middle/contract/wire-v1.yaml` (신규 — 8 wire 키 정의)
  - `profiles/acme-erp.yaml` (신규 — sample ERP customer profile)
  - `docs/learn-logs/engineer.md` (this ledger)
- Implementation choices:
  - **Format: plain YAML (not OpenAPI 3.1)** — OpenAPI 3.1은 장기 목표(swappable-layers.md §8)이나, adapter 없는 M1 진입 시점에 toolchain 의존을 도입하는 것은 과도한 선행 투자. 순수 YAML로 시작해 키 구조를 확정한 뒤 CTO 결정으로 OpenAPI 로 migration.
  - **Key namespace: `<domain>.<verb>` 2-segment** — `auth.login`, `entity.read` 등. 3-segment(`entity.customer.read`)로 하면 지금은 더 명확하지만 generic contract가 도메인 수만큼 중복 선언되는 구조가 됨. entity_type을 request 필드로 받는 방식이 더 DRY.
  - **8키 선택**: auth.login, auth.logout, entity.read, entity.list, entity.create, entity.update, entity.delete, status.health — 14 generic domain 전부에서 공통으로 쓰이는 최소 집합. `entity.patch` vs `entity.update` → PATCH semantics를 update로 통일 (CTO에 escalation point 참조).
  - **`entity.delete` idempotent: true** — 동일 id를 두 번 DELETE해도 "없으면 success" 반환이 표준 REST 관행. adapter가 404를 성공으로 처리해야 함 — CTO/QA 확인 필요.
  - **profile comment에서 `yaml.safe_load` 문자열 제거** — G-4 guard가 파일 내 텍스트를 grep하므로, 주석에 해당 문자열이 있으면 오탐. "plain YAML parser dump pipeline"으로 대체.
  - **`auth.sso_client_secret: ${ACME_SSO_CLIENT_SECRET}`** — secrets 섹션 없이 auth 블록에 직접 포함. schema _README 예시(`datasource.password`)와 일관성 유지, 별도 secrets key는 CTO 결정 후 추가.
- Tests added: NONE (L1 pytest 대상 파일 없음 — contract/profile은 데이터 파일). G-4 guard pass = 사실상 L0 smoke.
- Catches surfaced (CTO escalation):
  1. `entity.update` PATCH vs PUT semantics — 현재 PATCH로 구현했으나 adapter가 PUT full-replace를 기대하는 경우 contract 변경 필요. CTO 판정 요청.
  2. `entity.delete` idempotency — 404-as-success 표준화 여부. adapter마다 다를 수 있음. contract에 명문화 필요.
  3. OpenAPI 3.1 migration timing — M1 첫 adapter 직전? 직후? CTO 결정 필요.
  4. `auth` 블록을 customer profile `secrets` 섹션으로 분리할지 — 현재 auth.sso_client_secret이 auth 블록에 있음. 별도 `secrets:` 키 추가는 schema v2 변경.
- Cost: ~12 turns / ~$0.5 추정

### Growth-7 (2026-05-29) — 첫 backend adapter springboot-jakarta + G-1 가드 구현 + paging 버그수정

- **Built**: `backend/adapters/springboot-jakarta/` — Spring Boot 3.2.5 Jakarta, 8 wire key REST, generic in-memory store, `ContractLoader` 런타임 contract 로드 (G-1 준수 — code set/status 하드코딩 0), error envelope 매핑. BUILD SUCCESSFUL, smoke 8/8, gradle wrapper 포함.
- **wire-v1.yaml fix**: 응답 error 필드 8곳 string→envelope object (codes.yaml 정합). error_envelope 공통 블록 추가.
- **G-1 활성**: `diagnose.py::g1` 본문 — codes.yaml code→http_status 쌍 로드 후 adapter 소스에서 동일줄 재선언 검출. ALLOW 필터 (주석/`andExpect`/`description`/`message`/import). springboot adapter PASS. False-negative 기록: 인접 2줄 분할 재선언 (v1 단일줄만).
- **버그수정 (QA BLOCK 환류)**: BUG-1 `list()` params null-guard 누락 → `emptyMap()` 정규화. BUG-2 cursor mode silent 200 → BAD_REQUEST (ContractLoader 경유). 회귀 테스트 3종.
- **Catch (CTO escalation)**: paging HTTP 직렬화 키 — Spring MVC 가 `paging.mode` dot-notation 을 param Map 에 누락 → CTO 가 flat-underscore (`paging_mode`) 표준 결정.
- **Cost**: ~3 round Sonnet / ~30 commits

## §3 — Open Loops (이 인격 책임)

- ~~M1 진입 시 첫 spawn — `middle/contract/` 첫 wire 키 schema 파일 작성~~ ✅ Growth-5d 완료
- ~~`scripts/diagnose.py` G-1 SPEC → PASS 전환~~ ✅ Growth-7 완료 (code→status 재선언 검출)
- adapter `paging.mode` fallback 제거 — flat-underscore 단일 표준 정착 시 (Growth-8 후보)
- frontend vanilla-htmx adapter 구현 (Growth-8) + CDO tokens.md → tokens JSON 생성
- `scripts/diagnose.py` G-2 SPEC → 활성 전환 시 함수 본문 보강 (profile path extractor)
- CTO escalation 4건 응답 대기 (Growth-5d Decision Log 참조)
