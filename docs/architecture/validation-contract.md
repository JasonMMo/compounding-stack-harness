# Adapter Validation Contract

> CTO 결정 (Growth-12). `entity.create`/`entity.update` 가 `presets/ddl/catalog.yaml` 스키마로 입력을 검증하는 규약. codes.yaml 의 `VALIDATION_ERROR` description ("a field violated the DDL catalog schema") 을 실제로 작동시킨다. 모든 backend adapter (springboot-jakarta, fastapi, 미래) 가 동일하게 구현 — catalog 를 **읽기만**, 규칙 재선언 금지 (G-1).

## 1. 단일 진실 & 읽기 방식

- 검증 규칙의 단일 진실 = `presets/ddl/catalog.yaml` (56 entity). adapter 는 이를 런타임 로드 (codes.yaml/wire-v1.yaml 로딩과 동형 — `ContractLoader` 패턴 확장).
- adapter 는 catalog 스키마를 **하드코딩하지 않는다**. entity 컬럼·타입·enum·length·unique 는 전부 catalog 에서 읽는다.

## 2. entity_type 해소 — backward-compatible

```
entity_type ∈ catalog.entities  →  그 entity 스키마로 검증 (enforce)
entity_type ∉ catalog.entities  →  schema-less 통과 (검증 안 함, generic store 원래 동작)
```

**이 lenient 규칙이 핵심.** 기존 컴플라이언스 suite 와 generic 사용은 catalog 에 없는 임의 entity_type (예: `product`, `customer`)을 쓴다 — 이들은 검증 없이 통과해 **하위 호환 유지**. catalog 에 정의된 entity (예: `employee`, `invoice`) 만 스키마 enforce. 검증은 *additive* 이지 breaking 이 아니다.

## 3. 검증 체크 (entity.create)

catalog entity 의 각 컬럼에 대해, 순서대로:

| 체크 | 조건 | 위반 시 |
|---|---|---|
| **required** | `nullable: false` 컬럼이 data 에 없거나 null | `VALIDATION_ERROR` (422) |
| **type** | 값이 neutral type 과 불일치 (integer 아님, boolean 아님, date 형식 위반 등) | `VALIDATION_ERROR` (422) |
| **enum** | `type: enum` 인데 값이 `values[]` 에 없음 | `VALIDATION_ERROR` (422) |
| **length** | `type: string` 이고 `length` 초과 | `VALIDATION_ERROR` (422) |
| **unique** | `unique: true` 컬럼 값이 store 의 기존 레코드와 충돌 | `CONFLICT` (409) |

- **VALIDATION_ERROR (422)** 는 `details.fields` 로 위반 필드별 사유: `{ "details": { "fields": { "status": "must be one of [active, on-leave, terminated]" } } }` (codes.yaml 명세 준수). 여러 필드 위반 시 모두 수집해 한 번에 반환 (fail-fast 아님 — UX).
- **unique 충돌은 CONFLICT (409)** — VALIDATION_ERROR 아님. codes.yaml CONFLICT = "Unique constraint violation, duplicate create". `details.fields.<col> = "must be unique"`.

### 서버 생성 컬럼 (검증 제외)

`id` (uuid PK), `created_at`, `updated_at` — adapter 가 생성. client 입력 불요 → **required 체크 제외**. client 가 `id` 를 보내도 무시 (서버 생성 우선).

## 4. 검증 체크 (entity.update / PATCH)

부분 갱신 — **공급된 필드만** 검증:

- 공급된 필드: **type / enum / length / unique** 체크 적용.
- **required 는 적용 안 함** (부재 필드 = 변경 없음, PATCH semantics).
- `id` 변경 불가 (기존 동작 유지).

## 5. FK 참조 무결성 — Growth-15 Part C 구현

`fk:` 블록이 선언된 컬럼에 대해 런타임 참조 대상 존재 검증을 수행한다 (entity.create AND entity.update 양쪽).

**체크 규칙**:

| 조건 | 동작 |
|---|---|
| 컬럼에 `fk:` 블록 없음 (fk-exempt, polymorphic 포함) | **skip** — 강제 안 함 |
| nullable fk 컬럼이 null 이거나 absent | **skip** — 검증 대상 없음 |
| non-null fk 값 공급됨 | store 에서 `fk.entity` 타입으로 해당 id lookup |
| lookup 결과 없음 | `VALIDATION_ERROR` (422), `details.fields.<col> = "referenced <fk.entity> not found"` |
| lookup 결과 있음 | 통과 |

**추가 규칙**:
- update(PATCH): 공급된 fk 컬럼만 검증; absent = 변경 없음 = skip.
- FK 오류는 다른 field 오류와 동일한 `details.fields` 맵에 수집 (collect-all, fail-fast 아님).
- 오류 코드는 **VALIDATION_ERROR** (dangling fk 는 field violation — 새 코드 불필요).
- http_status 는 codes.yaml 로더에서 읽음 (G-1: 422 하드코딩 금지).
- 단일 진실: fk 대상은 catalog 에서 읽음. 관계를 코드에 하드코딩하지 않는다.
- store 접근은 validator 에 주입된 store 참조를 통해 cross-type lookup.
  - Python: `store.find_by_id(ref_entity, ref_id)` (None → not found)
  - Java: `store.findById(refEntity, refId).isEmpty()` (Optional → empty → not found)

**구현 위치**:
- Python: `backend/adapters/fastapi/catalog_validator.py` → `CatalogValidator._check_fk()`
- Java: `backend/adapters/springboot-jakarta/…/contract/CatalogValidator.java` → `checkFk()`
- 양 어댑터에서 `validate()` 의 unique check 직후, collect-all 루프 안에서 호출.

**fk-exempt 컬럼 (강제 안 함)**:
- `journal-entry.period_id` — `accounting-period` entity 가 catalog 에 없음 (외부 ref)
- `invoice.counterparty_id` — polymorphic (crm_contact or procurement_vendor)
- 기타 `fk:` 블록이 없는 모든 uuid 컬럼

## 6. Compliance 게이트 (DIM-5 + DIM-6)

공유 suite `tests/adapters/_shared/test_compliance.py`. springboot·fastapi 양쪽 동일 통과해야 머지 (adapter-agnostic 일관).

### DIM-5 — 스키마 검증 (Growth-12)

catalog entity (예: `employee`)로:

- 누락 required (full_name 없이 create) → VALIDATION_ERROR + details.fields.full_name
- 잘못된 enum (status="bogus") → VALIDATION_ERROR + details.fields.status
- length 초과 (employee_number > 64) → VALIDATION_ERROR
- type 불일치 (headcount_limit="abc" on position) → VALIDATION_ERROR
- unique 중복 (동일 employee_number 2회) → **CONFLICT**
- schema-less entity_type (`product`) → 검증 통과 (하위호환)
- PATCH 로 잘못된 enum → VALIDATION_ERROR / PATCH 로 required 누락 → **통과** (부분갱신)

### DIM-6 — FK 참조 무결성 (Growth-15 Part C)

parent=`carrier`, child=`route` (carrier_id → carrier, required), nullable FK=`position.department_id`, fk-exempt=`journal-entry.period_id`:

- F1: child create with bogus parent id → VALIDATION_ERROR + details.fields.carrier_id = "referenced carrier not found"
- F2: create parent first, then child with real parent id → 201 success
- F3: nullable FK (position.department_id) omitted → 201 success (no FK error)
- F4: PATCH fk col to bogus id → VALIDATION_ERROR + details.fields.carrier_id
- F5: PATCH unrelated field, fk col absent → 200 success (absent fk not re-checked)
- F6: fk-exempt col (journal-entry.period_id, no `fk:` block) with arbitrary id → 201 success (not enforced)

## 7. 구현 형태

- adapter 내 `CatalogValidator` (springboot: Java 클래스 / fastapi: Python 모듈) — catalog 로드 + `validate(entity_type, data, partial: bool, current_id, store) → list[FieldError]`.
- create/update 컨트롤러가 store 쓰기 **전에** 호출. 위반 시 wire error 반환 (VALIDATION_ERROR / CONFLICT, http_status 는 codes.yaml).
- catalog 경로 해소: repo-root 기준 `presets/ddl/catalog.yaml` (contract loader 의 경로 해소 패턴 재사용).
- FK check: `_check_fk` / `checkFk` 메서드가 unique check 직후 실행. store 는 validator 에 주입.
