---
domain: reporting
label: Reporting & Analytics
version: "1.0"
entities:
  - report-definition
  - report-schedule
  - report-parameter
  - report-output
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Reporting & Analytics

## Purpose
Provides a metadata-driven reporting layer: report definitions describe what data to retrieve and how to present it, schedules automate periodic delivery, parameters allow runtime customisation, and outputs store the rendered results for download or distribution. Primary personas: business analyst configuring reports, executive reviewing scheduled dashboards, and IT manager managing report infrastructure. Core value: non-technical users get consistent, accurate business data on demand or on schedule without writing queries.

## Core Entities

### report-definition
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Unique report identifier slug. |
| name | string | yes | Display name of the report. |
| domain | string | yes | Source domain this report draws data from (e.g., hr, finance). |
| description | string | no | What the report shows and who it is for. |
| output_format | string (enum: table/chart/pivot/export-csv/export-xlsx) | yes | Default rendering format. |
| is_active | boolean | yes | Whether the report may be run or scheduled. |
| owner_id | string | yes | FK to employee who maintains this report definition. |

**Constraints**:  must be unique. Inactive reports () must not be run or scheduled. A report definition must have at least one linked  before it can be published for general use.

### report-schedule
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| report_definition_id | string | yes | FK to report-definition entity. |
| cron_expression | string | yes | UNIX cron expression defining run frequency. |
| is_active | boolean | yes | Whether the schedule is currently enabled. |
| recipient_ids | array of strings | yes | FKs to employees who receive the output. |
| next_run_at | string (iso8601) | no | Computed next scheduled execution time. |
| last_run_at | string (iso8601) | no | Timestamp of the most recent execution. |

**Constraints**:  must be a valid 5-field UNIX cron expression. A schedule may only be created for an active report definition.  must contain at least one entry.

### report-parameter
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| report_definition_id | string | yes | FK to report-definition entity. |
| name | string | yes | Parameter identifier (e.g., date_from, department_id). |
| label | string | yes | Human-readable label shown in the UI. |
| data_type | string (enum: string/integer/number/boolean/date/enum) | yes | Expected value type. |
| is_required | boolean | yes | Whether the parameter must be supplied at run time. |
| default_value | string | no | Default value applied when the parameter is omitted (serialised as string). |
| enum_values | array of strings | no | Allowed values when  is . |

**Constraints**: Parameter  must be unique within a report definition. When  is ,  must be non-empty.  must conform to  when provided.

### report-output
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| report_definition_id | string | yes | FK to report-definition entity. |
| triggered_by | string (enum: manual/schedule) | yes | How the run was initiated. |
| triggered_by_id | string | no | FK to employee (manual) or report-schedule (scheduled). |
| status | string (enum: queued/running/completed/failed) | yes | Execution status. |
| started_at | string (iso8601) | no | When execution began. |
| completed_at | string (iso8601) | no | When execution finished. |
| storage_key | string | no | Opaque storage reference to the rendered output file. |
| row_count | integer | no | Number of data rows in the output. |
| error_message | string | no | Non-null on failure. |

**Constraints**: Report outputs are append-only; existing records must not be modified after  reaches  or .  must be >=  when both are set.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **run-report**: Executes a report definition with supplied parameter values, creates a  record, fetches data from the source domain, renders the output, and stores the result. Future wire key: .
- **schedule-report**: Creates or updates a , validates the cron expression, sets , and activates the scheduler. Future wire key: .
- **export-report**: Retrieves a completed  by ID and returns the file contents as a download stream in the requested format. Future wire key: .

## Business Rules
1. A report may only be run () against an active report definition (); running against an inactive definition must be rejected.
2. All  parameters must be supplied at run time; missing required parameters must cause immediate rejection before any data query is issued.
3. Report outputs are immutable once in  or  status; to re-run, a new  record must be created via a fresh  call.
4. A report schedule may only be created against an active report definition; deactivating a report definition must also deactivate all its linked schedules.

## Integration Points
- **-> all domains**: The reporting domain reads entity data from every other domain; it emits no write events. It is a pure read consumer.
- **-> approval**: Report definitions that expose sensitive financial or personnel data may require approval before being activated, triggering an .
- **-> document**: Completed report outputs may be published into the document domain as versioned documents for long-term retention and access control.
