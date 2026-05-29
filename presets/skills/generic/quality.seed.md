---
domain: quality
label: Quality Management
version: "1.0"
entities:
  - inspection-plan
  - inspection-result
  - defect
  - corrective-action
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Quality Management

## Purpose
Ensures product and process conformance through structured inspection plans, recorded inspection results, defect tracking, and corrective action management. Primary personas: quality inspector executing inspection plans, QA engineer analysing defect trends, and quality manager closing corrective actions. Core value: a closed-loop system where every defect has a root cause and a verified fix, preventing recurrence.

## Core Entities

### inspection-plan
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| name | string | yes | Inspection plan name. |
| reference_type | string (enum: work-order/shipment/vendor/process) | yes | Type of entity this plan applies to. |
| reference_id | string | yes | ID of the referenced entity instance. |
| status | string (enum: pending/in-progress/passed/failed/cancelled) | yes | Inspection lifecycle status. |
| assigned_to | string | no | FK to employee conducting the inspection. |
| due_date | string (date) | no | Deadline for completing the inspection. |

**Constraints**: An inspection plan in `passed` or `failed` status is immutable. A `cancelled` plan may not be restarted; a new plan must be created.

### inspection-result
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| inspection_plan_id | string | yes | FK to inspection-plan entity. |
| checkpoint | string | yes | Name of the checkpoint being evaluated. |
| result | string (enum: pass/fail/observation) | yes | Outcome of this checkpoint. |
| measured_value | string | no | Actual measured value (free-text for flexibility). |
| expected_value | string | no | Target or tolerance spec. |
| inspector_id | string | yes | FK to employee who recorded this result. |
| recorded_at | string (iso8601) | yes | When the result was recorded. |

**Constraints**: Results are append-only; existing records must not be modified. A `fail` result automatically triggers defect creation in the same operation. All checkpoints in a plan must be evaluated before the plan can be closed.

### defect
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| inspection_result_id | string | yes | FK to the inspection-result that raised this defect. |
| defect_code | string | yes | Standardised defect classification code. |
| severity | string (enum: critical/major/minor) | yes | Impact classification. |
| description | string | yes | Detailed description of the non-conformance. |
| status | string (enum: open/under-review/corrective-action-raised/closed) | yes | Resolution status. |
| disposition | string (enum: rework/scrap/accept-with-deviation/pending) | no | How the defective item is handled. |

**Constraints**: A `critical` defect automatically sets the parent inspection plan to `failed` status. A defect cannot be closed without a linked corrective action that is itself `closed`.

### corrective-action
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| defect_id | string | yes | FK to defect entity. |
| root_cause | string | yes | Documented root cause analysis. |
| action_description | string | yes | Steps taken to address the root cause. |
| owner_id | string | yes | FK to employee responsible for implementing the action. |
| due_date | string (date) | yes | Target completion date. |
| status | string (enum: open/in-progress/verification-pending/closed) | yes | Implementation status. |
| verified_by | string | no | FK to employee who verified effectiveness. |
| verified_at | string (iso8601) | no | When verification was completed. |

**Constraints**: A corrective action cannot be `closed` without both `verified_by` and `verified_at` being set. `due_date` must be >= `created_at` date.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **start-inspection**: Transitions an inspection plan from `pending` to `in-progress`, records the start time, and notifies the assigned inspector. Future wire key: `quality.start-inspection`.
- **record-defect**: Creates a defect linked to a `fail` inspection result, sets the plan status to `failed` if severity is `critical`, and optionally triggers a corrective action. Future wire key: `quality.record-defect`.
- **close-corrective-action**: Verifies action effectiveness, sets `verified_by` and `verified_at`, transitions status to `closed`, and closes the linked defect if all actions are resolved. Future wire key: `quality.close-ca`.

## Business Rules
1. A `critical` defect immediately transitions the parent inspection plan to `failed` status; no further checkpoints are required but may still be recorded.
2. A corrective action cannot be closed unless `verified_by` and `verified_at` are both populated, confirming independent verification of effectiveness.
3. A defect cannot transition to `closed` status unless all linked corrective actions are also `closed`.
4. All inspection checkpoints in a plan must have a recorded result before the plan can be transitioned to `passed` or `failed` via a normal close.

## Integration Points
- **→ production**: Work-order completion (`production.close-wo`) triggers creation of a finished-goods inspection plan in the quality domain.
- **→ procurement**: Goods receipt (`procurement.receive`) may trigger a vendor-type inspection plan for incoming materials.
- **→ approval**: A corrective action for a `critical` defect may require senior QA manager approval, triggering an `approval.approval-request`.
- **→ reporting**: Defect rates by code, first-pass yield, and corrective action cycle times are consumed by the reporting domain.
