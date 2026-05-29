---
domain: hr
label: Human Resources
version: "1.0"
entities:
  - employee
  - department
  - position
  - leave-request
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Human Resources

## Purpose
Manages the full employee lifecycle — from hire to termination — along with organizational structure (departments, positions) and employee time-off (leave requests). Primary personas: HR administrator, department manager, IT-담당자 provisioning access. Core value: a single authoritative record of who works here, in what role, and whether they are active.

## Core Entities

### employee
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| employee_number | string | yes | Unique identifier used in payroll systems. |
| full_name | string | yes | Legal full name. |
| department_id | string | yes | FK to department entity. |
| position_id | string | no | FK to position entity. |
| hire_date | string (date) | yes | Date employment started. |
| status | string (enum: active/on-leave/terminated) | yes | Current employment status. |

**Constraints**: `employee_number` must be unique across all tenants. `status` transitions follow the state machine: active → on-leave → active, active → terminated (terminal). Terminated employees are soft-deleted (status change only, record retained).

### department
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Short alphanumeric code (e.g., HR, FIN, OPS). |
| name | string | yes | Full department name. |
| parent_id | string | no | FK to parent department (supports org hierarchy). |
| manager_id | string | no | FK to employee who manages this department. |

**Constraints**: `code` must be unique. Circular parent references are forbidden; depth limit is 10 levels. A department cannot be deleted while it has active employees.

### position
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| title | string | yes | Job title displayed to end users. |
| grade | string | no | Pay grade or band (e.g., L3, Senior). |
| department_id | string | no | FK to department (optional: cross-dept positions allowed). |
| headcount_limit | integer | no | Maximum employees that can hold this position simultaneously. |

**Constraints**: If `headcount_limit` is set, the adapter must reject an `hr.hire` operation that would exceed it.

### leave-request
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| employee_id | string | yes | FK to employee entity. |
| leave_type | string (enum: annual/sick/unpaid/maternity/paternity) | yes | Category of leave. |
| start_date | string (date) | yes | First day of leave (inclusive). |
| end_date | string (date) | yes | Last day of leave (inclusive). |
| status | string (enum: draft/pending/approved/rejected/cancelled) | yes | Workflow status. |
| reason | string | no | Employee-provided rationale. |

**Constraints**: `end_date` must be >= `start_date`. An employee cannot have two overlapping active (pending or approved) leave requests for the same period.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **hire-employee**: Atomically creates an employee record, assigns a position, and triggers onboarding notifications. Future wire key: `hr.hire`.
- **terminate-employee**: Sets employee status to `terminated`, revokes access tokens via downstream integration, and records the termination reason and effective date. Future wire key: `hr.terminate`.
- **approve-leave**: Transitions a leave-request from `pending` to `approved`, deducts the leave balance, and notifies the employee. Future wire key: `hr.approve-leave`.

## Business Rules
1. An employee cannot have two overlapping active leave requests (status `pending` or `approved`) covering the same calendar days.
2. A terminated employee's record must not be physically deleted; `status` is set to `terminated` and the record is retained for audit.
3. If a position has a `headcount_limit`, hiring into that position when the current active headcount equals the limit must be rejected at the application layer before any DB write.
4. Leave requests in `approved` status can only be cancelled before the `start_date`; post-start cancellations require a separate adjustment operation.

## Integration Points
- **→ approval**: A leave-request with `status: pending` triggers an `approval.approval-request` when the customer profile's leave policy requires manager sign-off.
- **→ finance**: Employee `hire_date`, `status`, and `position_id` (with associated pay grade) are read by the payroll sub-process in the finance domain.
- **→ reporting**: Employee headcount and leave-balance aggregates are consumed by the reporting domain for workforce dashboards.
