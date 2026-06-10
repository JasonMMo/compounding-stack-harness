---
slug: case-party
confidence: EXTRACTED
updated: 2026-06-11
source: lawfirm-demo (Growth-24 PM loop #1)
---

# case-party (사건 당사자)

> catalog entity: `case-party` (domain: `legal`). seed: `presets/skills/legal/case-management.seed.md`.

## 정의

사건에 연루된 관계자 목록. 한 사건에 원고·피고·증인·상대방 변호인·전문가 증인이 복수 존재할 수 있다. `[EXTRACTED]` — 법무 업무 특성상 당사자 관리가 필수.

## 역할 (role)

| 값 | 의미 |
|---|---|
| `plaintiff` | 원고 (민사·행정) |
| `defendant` | 피고 |
| `witness` | 증인 |
| `opposing-counsel` | 상대방 변호인 |
| `expert-witness` | 전문가 증인 |

## 관계

- `case_id` → [[legal-case]] (cascade delete)
- `contact_id` → `crm.contact` (nullable — 외부 인물이면 null 가능)

## 주의

같은 사람이 두 역할(예: 증인이자 계약 당사자)을 맡는 경우 행이 2개. `(case_id, role, name)` unique 미적용 — 동일인 복수 역할 허용.
