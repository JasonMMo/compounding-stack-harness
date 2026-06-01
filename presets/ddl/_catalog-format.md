# DDL Catalog Format

> CTO 결정 (Growth-10). `presets/ddl/catalog.yaml` 은 ddl 축 (Stage 2) 의 단일 진실 — 14 도메인 56 entity 의 **dialect-neutral 스키마**. dialect adapter 가 이를 각 SQL 방언으로 렌더하고, wire `entity.create`/`entity.update` 가 검증 소스로 읽으며, L2 풀테스트(HSQLDB)가 schema+seed smoke 를 돈다. 인간 서사는 `presets/skills/generic/*.seed.md` 의 entity 표가 소유 — catalog 는 **기계 진실**, seed 는 **서사**. 둘은 일치해야 하며 G-N 가드가 `seed entities ⊆ catalog entities` 를 검증한다.

## 1. 파일 구조

```
presets/ddl/
  _catalog-format.md       # 이 문서 (포맷 단일 진실)
  catalog.yaml             # 56 entity dialect-neutral 스키마
  dialects/
    postgres.yaml          # 타입 매핑 (프로덕션 디폴트)
    hsqldb.yaml            # 타입 매핑 (L2 풀테스트 방언)
    mysql.yaml             # (M1 후보 — 타입맵만)
    oracle.yaml            # (M1 후보 — 타입맵만)
  render.py                # catalog.yaml + dialect.yaml → CREATE TABLE DDL
```

## 2. Neutral Type 어휘 (closed set)

dialect adapter 가 매핑하는 유일한 타입 집합. catalog 는 이 8종만 쓴다:

| neutral type | 의미 | 비고 |
|---|---|---|
| `uuid` | 기본키·FK 식별자 | seed 의 "string (UUID)" |
| `string` | 짧은 가변 문자열 | `length:` 동반 (디폴트 255) |
| `text` | 긴 본문 | length 무제한 |
| `integer` | 정수 | |
| `decimal` | 고정소수 | `precision`/`scale` 동반 (금액 등) |
| `boolean` | 참/거짓 | |
| `date` | 날짜 | seed 의 "string (date)" |
| `timestamp` | 일시 | seed 의 "string (iso8601)" |
| `enum` | 폐집합 문자열 | `values:` 동반 → **VARCHAR + CHECK** 로 렌더 (전 방언 이식성) |

## 3. catalog.yaml 엔트리 형식

```yaml
version: "1.0"
entities:
  employee:
    domain: hr                      # 소속 도메인 (seed 와 1:1)
    table: hr_employee              # 물리 테이블명 (도메인 prefix, ASCII snake)
    primary_key: id
    columns:
      id:             { type: uuid, nullable: false }
      created_at:     { type: timestamp, nullable: false }
      updated_at:     { type: timestamp, nullable: false }
      employee_number:{ type: string, length: 64, nullable: false, unique: true }
      full_name:      { type: string, nullable: false }
      department_id:  { type: uuid, nullable: false,
                        fk: { entity: department, column: id, on_delete: restrict } }
      position_id:    { type: uuid, nullable: true,
                        fk: { entity: position, column: id, on_delete: set_null } }
      hire_date:      { type: date, nullable: false }
      status:         { type: enum, values: [active, on-leave, terminated], nullable: false }
    constraints:
      - { type: check, expr: "end_date >= start_date" }   # 해당 시
      - { type: unique, columns: [code] }                  # 복합/단일 unique
    indexes:
      - { columns: [department_id] }
```

**컬럼 키**: `type` (필수), `nullable` (필수), `length`/`precision`/`scale`/`values` (타입별), `unique` (단일 컬럼 unique), `fk` (`entity`/`column`/`on_delete`), `default`.
**on_delete**: `restrict` | `cascade` | `set_null` | `no_action`.
**모든 entity 표준 컬럼**: `id` (uuid PK), `created_at`, `updated_at` (timestamp) — seed 의 공통 3 컬럼 계승.

## 4. dialects/<dialect>.yaml 형식

```yaml
dialect: postgres
type_map:
  uuid: UUID
  string: VARCHAR
  text: TEXT
  integer: INTEGER
  decimal: NUMERIC
  boolean: BOOLEAN
  date: DATE
  timestamp: TIMESTAMP
  enum: VARCHAR          # + values 로 CHECK 생성
defaults:
  string_length: 255
quote: '"'                # 식별자 인용 문자 (mysql 은 `)
```

render.py 는 catalog 의 neutral type 을 `type_map` 으로 치환, enum 은 `VARCHAR(n) CHECK (col IN (...))`, fk 는 `REFERENCES`, on_delete 를 방언 문법으로 렌더.

## 5. Multi-tenancy 경계 (M5 게이트)

catalog 는 **tenant-agnostic** (단일 테넌트 self-host 기준). seed 의 "unique across all tenants" 표현은 self-host 에선 그냥 unique. `tenant_id` 컬럼·RLS 는 **M5 multi-tenant SaaS overlay** (Growth-73 4-조건 게이트) 로 미룬다 — catalog 에 지금 박지 않는다 (premature multi-tenancy 회피).

## 6. wire contract 정합

- `entity.create` 의 `data` 검증 = catalog entity 의 컬럼·타입·nullable·enum·unique. 위반 시 wire `VALIDATION_ERROR` (codes.yaml) + `details.fields`.
- adapter 에 검증 wiring (InMemoryEntityStore → catalog 읽기) 은 **후속 Growth** — Growth-10 은 catalog + dialect 렌더 + L2 smoke 까지. adapter 검증 연결은 별도.
- entity_type ↔ catalog entity 해소: customer profile `domains[].slug` → catalog entity key.

## 7. 가드 (Growth-10 신설 후보 G-N)

- `seed entities ⊆ catalog entities` — seed 가 선언한 entity 가 catalog 에 다 있는가 (드리프트 차단).
- catalog 의 모든 `fk.entity` 가 실재 catalog entity 인가 (dangling FK 차단).
- 모든 neutral type 이 §2 closed set 인가.
