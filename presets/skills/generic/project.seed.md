---
domain: project
label: Project Management
version: "1.0"
entities:
  - project
  - task
  - milestone
  - resource-assignment
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Project Management

## Purpose
Plans and tracks work across projects: structured task hierarchies, milestone gates, and resource assignments. Primary personas: project manager structuring a delivery plan, team member updating task progress, and executive sponsor reviewing milestone health. Core value: real-time visibility into whether a project will deliver on time and whether the right people are working on the right things.

## Core Entities

### project
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Short unique project identifier. |
| name | string | yes | Project display name. |
| owner_id | string | yes | FK to employee who manages the project. |
| status | string (enum: planning/active/on-hold/completed/cancelled) | yes | Project lifecycle status. |
| start_date | string (date) | yes | Planned start date. |
| end_date | string (date) | yes | Planned end date. |
| budget | number | no | Approved budget in the account's base currency. |

**Constraints**: `code` must be unique. `end_date` must be >= `start_date`. A `completed` or `cancelled` project is immutable. Tasks and milestones may not be added to a `cancelled` project.

### task
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| project_id | string | yes | FK to project entity. |
| parent_task_id | string | no | FK to parent task (for sub-task hierarchies). |
| name | string | yes | Task name. |
| status | string (enum: todo/in-progress/blocked/done/cancelled) | yes | Task status. |
| assignee_id | string | no | FK to employee assigned to this task. |
| due_date | string (date) | no | Task deadline. |
| estimated_hours | number | no | Planned effort in hours. |
| actual_hours | number | no | Recorded effort in hours. |
| progress_pct | integer | yes | Completion percentage 0–100. |

**Constraints**: `progress_pct` must be between 0 and 100. Circular parent-task references are forbidden. A task in `done` status must have `progress_pct` of 100.

### milestone
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| project_id | string | yes | FK to project entity. |
| name | string | yes | Milestone name. |
| due_date | string (date) | yes | Target date for this milestone. |
| status | string (enum: pending/achieved/missed/cancelled) | yes | Milestone status. |
| achieved_at | string (iso8601) | no | Actual datetime the milestone was achieved. |
| description | string | no | What this milestone represents. |

**Constraints**: A `achieved` milestone must have `achieved_at` set. A `missed` milestone is one where `due_date` has passed and `status` is not `achieved`. Milestones may not be added to a `cancelled` project.

### resource-assignment
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| project_id | string | yes | FK to project entity. |
| employee_id | string | yes | FK to HR employee entity. |
| role | string | yes | Role on the project (e.g., Developer, Designer, PM). |
| allocated_hours | number | yes | Total hours allocated for this assignment. |
| start_date | string (date) | yes | Start of the assignment window. |
| end_date | string (date) | yes | End of the assignment window. |

**Constraints**: The pair (`project_id`, `employee_id`) must be unique (one active assignment per employee per project). `end_date` must be >= `start_date`. `allocated_hours` must be > 0.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **assign-resource**: Creates or updates a resource assignment, checks for over-allocation against other concurrent projects, and notifies the employee. Future wire key: `project.assign`.
- **update-progress**: Updates task `progress_pct` and `actual_hours`, and rolls up progress to the parent task and project level. Future wire key: `project.progress`.
- **close-milestone**: Marks a milestone `achieved`, sets `achieved_at` to now, and notifies the project owner and stakeholders. Future wire key: `project.close-milestone`.

## Business Rules
1. A milestone cannot be closed (`project.close-milestone`) if any tasks that are tagged as blocking that milestone are not in `done` status.
2. `progress_pct` on a task must not regress below its previous value without an explicit override by a project manager (prevents accidental resets).
3. An employee assignment (`project.assign`) must be rejected if it creates an over-allocation (allocated_hours across concurrent projects exceeds the employee's configured weekly capacity).
4. A project cannot be transitioned to `completed` while it has any tasks in `in-progress` or `blocked` status.

## Integration Points
- **→ hr**: Resource assignments reference `hr.employee` records; the HR domain supplies availability and capacity data.
- **→ approval**: High-budget projects (above a configurable threshold) require sponsor approval before transitioning from `planning` to `active`, triggering an `approval.approval-request`.
- **→ reporting**: Project burn rate, milestone adherence, and resource utilisation are consumed by the reporting domain for portfolio dashboards.
