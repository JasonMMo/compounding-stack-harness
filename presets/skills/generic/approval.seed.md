---
domain: approval
label: Approval Workflow
version: "1.0"
entities:
  - approval-request
  - approval-step
  - approver
  - approval-decision
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Approval Workflow

## Purpose
Provides a generic, reusable approval engine that any domain can plug into when a business action requires human sign-off before proceeding. Primary personas: employee submitting a request, manager reviewing and approving or rejecting, and compliance officer auditing the decision trail. Core value: a single, consistent approval mechanism across all domains that produces a tamper-evident audit trail for every decision made.

## Core Entities

### approval-request
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| subject_type | string | yes | Entity type of the object requiring approval (e.g., leave-request, requisition). |
| subject_id | string | yes | Primary key of the object requiring approval. |
| requester_id | string | yes | FK to employee who submitted the request. |
| status | string (enum: pending/in-progress/approved/rejected/cancelled/expired) | yes | Overall request status. |
| title | string | yes | Short human-readable description of what is being approved. |
| expires_at | string (iso8601) | no | Deadline after which the request auto-expires if not resolved. |

**Constraints**: The pair (`subject_type`, `subject_id`) must be unique among non-terminal requests (prevents duplicate approval chains on the same object). A `cancelled` or `expired` request is terminal. An `approved` or `rejected` request is immutable.

### approval-step
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| request_id | string | yes | FK to approval-request entity. |
| sequence | integer | yes | Execution order of this step. |
| name | string | yes | Step name (e.g., "Line Manager Approval", "CFO Sign-off"). |
| status | string (enum: pending/active/approved/rejected/skipped) | yes | Step status. |
| requires_all | boolean | yes | Whether all assigned approvers must approve (true) or any one suffices (false). |

**Constraints**: `sequence` must be unique within a request. Steps are processed in ascending `sequence` order; the next step activates only after the current step is resolved. A `rejected` step immediately transitions the entire approval-request to `rejected`.

### approver
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| step_id | string | yes | FK to approval-step entity. |
| employee_id | string | yes | FK to the approving employee. |
| notified_at | string (iso8601) | no | When the approver was notified. |
| responded_at | string (iso8601) | no | When the approver submitted their decision. |

**Constraints**: The pair (`step_id`, `employee_id`) must be unique (no duplicate approver assignment per step). An approver record cannot be added to a step that is already `approved`, `rejected`, or `skipped`.

### approval-decision
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| step_id | string | yes | FK to approval-step entity. |
| approver_id | string | yes | FK to the approver who decided. |
| decision | string (enum: approved/rejected) | yes | The approver's decision. |
| comment | string | no | Optional justification or note from the approver. |
| decided_at | string (iso8601) | yes | Timestamp of the decision. |

**Constraints**: Approval decisions are immutable once recorded. Each approver may record only one decision per step. The pair (`step_id`, `approver_id`) must be unique in this table.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **submit-request**: Creates an approval-request with its steps and approvers, transitions status to `in-progress`, activates the first step, and notifies the assigned approvers. Future wire key: `approval.submit`.
- **approve-step**: Records an `approved` decision for the current step; if all required approvers have approved (or `requires_all: false`), advances to the next step or closes the request as `approved`. Future wire key: `approval.approve`.
- **reject-step**: Records a `rejected` decision, immediately transitions the current step and the parent approval-request to `rejected`, and notifies the original requester. Future wire key: `approval.reject`.

## Business Rules
1. Only one non-terminal approval-request may exist per (`subject_type`, `subject_id`) pair; submitting a duplicate must be rejected.
2. Steps must be processed in ascending `sequence` order; a step may not be acted on while a lower-sequence step is still `pending` or `active`.
3. When `approval-step.requires_all: true`, the step is `approved` only when every assigned approver has recorded an `approved` decision; a single rejection closes the step as `rejected`.
4. An `approval-request` that passes its `expires_at` without resolution must be transitioned to `expired` by the adapter (via a scheduled job or on-read check), blocking the subject action.

## Integration Points
- **→ hr**: Leave-request approval uses this domain; `subject_type: leave-request`, `subject_id` references the HR leave-request.
- **→ procurement**: Requisition approval and high-value PO approval route through this domain.
- **→ finance**: Period-close and high-value journal entries may require CFO approval before posting.
- **→ reporting**: Approval cycle times, rejection rates per domain, and pending approvals by approver are consumed by the reporting domain for governance dashboards.
