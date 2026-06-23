---
domain: project
label: Project Management
version: "1.1"
entities:
  - project
  - task
  - milestone
  - resource-assignment
  - task-comment
  - task-attachment
  - task-label
  - task-label-link
  - task-activity
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
| priority | string (enum: low/normal/high/urgent) | yes | Task priority level. |
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

### task-comment
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| task_id | string | yes | FK to task entity (cascade delete). |
| author_id | string | yes | FK to employee who wrote the comment (restrict delete). |
| body | string (text) | yes | Comment body text. |
| edited_at | string (iso8601) | no | Timestamp of last edit, null if never edited. |

**Constraints**: `body` must not be empty. `edited_at` must be set whenever `body` is updated after initial creation. Comments are owned by `author_id`; edit permission is restricted to the author or a project manager.

### task-attachment
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| task_id | string | yes | FK to task entity (cascade delete). |
| uploader_id | string | yes | FK to employee who uploaded the file (restrict delete). |
| filename | string | yes | Original file name as uploaded. |
| content_type | string | yes | MIME type (max 128 chars). |
| byte_size | integer | yes | File size in bytes. |
| storage_key | string | yes | Opaque key for retrieval from the configured storage backend. |

**Constraints**: `byte_size` must be > 0. `storage_key` must be unique. Deletion of the attachment record must trigger removal of the backing file from storage (application layer).

### task-label
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| project_id | string | yes | FK to project entity (cascade delete). |
| name | string | yes | Label display name within the project. |
| color | string | yes | Hex color code for UI rendering (max 16 chars, e.g. `#FF5733`). |

**Constraints**: The pair (`project_id`, `name`) must be unique — label names are scoped per project. Labels are deleted when their parent project is deleted.

### task-label-link
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| task_id | string | yes | FK to task entity (cascade delete). |
| label_id | string | yes | FK to task-label entity (cascade delete). |

**Constraints**: The pair (`task_id`, `label_id`) must be unique (no duplicate label application). This is a pure M:N join table — UI manages it inline via the task form; no dedicated CRUD screen.

### task-activity
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp (immutable). |
| updated_at | string (iso8601) | yes | Technical update timestamp (must equal created_at — append-only). |
| task_id | string | yes | FK to task entity (cascade delete). |
| actor_id | string | yes | FK to employee who triggered the action (restrict delete). |
| action | string (enum: created/updated/status-changed/assigned/commented/label-changed) | yes | Type of action recorded. |
| field | string | no | Name of the field that changed (for `updated` action). |
| old_value | string | no | Previous value serialised as string. |
| new_value | string | no | New value serialised as string. |

**Constraints**: Records are append-only — no UPDATE or DELETE allowed at the application layer. `field`, `old_value`, `new_value` are only populated for `updated` and `status-changed` actions.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **assign-resource**: Creates or updates a resource assignment, checks for over-allocation against other concurrent projects, and notifies the employee. Future wire key: `project.assign`.
- **update-progress**: Updates task `progress_pct` and `actual_hours`, and rolls up progress to the parent task and project level. Future wire key: `project.progress`.
- **close-milestone**: Marks a milestone `achieved`, sets `achieved_at` to now, and notifies the project owner and stakeholders. Future wire key: `project.close-milestone`.
- **comment**: Adds a task-comment record and appends a `commented` task-activity entry. Future wire key: `project.comment`.
- **attach**: Uploads a file to the configured storage backend, creates a task-attachment record, and appends a `updated` task-activity entry. Future wire key: `project.attach`.
- **label**: Adds or removes task-label-link entries for a task, and appends a `label-changed` task-activity entry for each change. Future wire key: `project.label`.
- **move-card**: Transitions a task's `status` field following the kanban state machine (todo → in-progress → blocked → done), appends a `status-changed` task-activity entry, and optionally notifies the assignee. Future wire key: `project.move-card`.
- **search-similar**: Semantic similarity search over task names and descriptions using the Lite-AI wire key. Intended for surfacing related tasks during creation. Future wire key: `project.search-similar`.

## Business Rules
1. A milestone cannot be closed (`project.close-milestone`) if any tasks that are tagged as blocking that milestone are not in `done` status.
2. `progress_pct` on a task must not regress below its previous value without an explicit override by a project manager (prevents accidental resets).
3. An employee assignment (`project.assign`) must be rejected if it creates an over-allocation (allocated_hours across concurrent projects exceeds the employee's configured weekly capacity).
4. A project cannot be transitioned to `completed` while it has any tasks in `in-progress` or `blocked` status.
5. `task-activity` records are append-only: no UPDATE or DELETE is permitted at the application or database layer. Any attempt to modify or remove an activity entry must return an error.
6. Deleting a task cascades to all of its task-comment, task-attachment, task-label-link, and task-activity records. The application layer must additionally remove backing files for any task-attachment records before the cascade delete executes.
7. The `move-card` operation must enforce the kanban state machine: valid transitions are `todo → in-progress`, `in-progress → blocked`, `blocked → in-progress`, and `in-progress → done`. Direct transitions that skip states (e.g., `todo → done`) are forbidden unless the caller holds project-manager privilege.

## Integration Points
- **→ hr**: Resource assignments reference `hr.employee` records; the HR domain supplies availability and capacity data.
- **→ approval**: High-budget projects (above a configurable threshold) require sponsor approval before transitioning from `planning` to `active`, triggering an `approval.approval-request`.
- **→ reporting**: Project burn rate, milestone adherence, and resource utilisation are consumed by the reporting domain for portfolio dashboards.
