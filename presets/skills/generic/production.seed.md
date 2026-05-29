---
domain: production
label: Production & Manufacturing
version: "1.0"
entities:
  - work-order
  - bom
  - bom-line
  - operation
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Production & Manufacturing

## Purpose
Controls the shop-floor execution of manufacturing work: bills of materials define what components and operations are needed, and work orders track actual production runs from release through completion. Primary personas: production planner releasing work orders, shop-floor operator recording operation progress, and quality inspector signing off finished goods. Core value: traceability from finished-product back through every component consumed and every operation performed.

## Core Entities

### work-order
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| wo_number | string | yes | Human-readable unique work-order identifier. |
| bom_id | string | yes | FK to bill of materials used for this run. |
| item_id | string | yes | FK to inventory item being produced. |
| quantity_planned | number | yes | Planned production quantity. |
| quantity_produced | number | yes | Actual produced quantity so far. |
| status | string (enum: draft/released/in-progress/completed/cancelled) | yes | Work-order lifecycle status. |
| scheduled_start | string (iso8601) | no | Planned start datetime. |
| scheduled_end | string (iso8601) | no | Planned end datetime. |

**Constraints**: `wo_number` must be unique. `quantity_planned` must be > 0. A `completed` or `cancelled` work order is immutable. `scheduled_end` must be >= `scheduled_start` when both are provided.

### bom
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| item_id | string | yes | FK to the finished-goods inventory item this BOM produces. |
| version | string | yes | BOM version identifier (e.g., "1.0", "REV-B"). |
| is_active | boolean | yes | Whether this BOM may be used for new work orders. |
| description | string | no | Notes on this revision. |

**Constraints**: The pair (`item_id`, `version`) must be unique. Only active BOMs (`is_active: true`) may be referenced by new work orders. A BOM must have at least one `bom-line` before it can be marked active.

### bom-line
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| bom_id | string | yes | FK to bom entity. |
| component_item_id | string | yes | FK to inventory item used as a component. |
| quantity_per | number | yes | Quantity of component required per one finished unit. |
| unit_of_measure | string | yes | UOM for the component quantity. |
| is_critical | boolean | yes | Whether shortage of this component blocks production. |

**Constraints**: `quantity_per` must be > 0. A BOM line cannot reference the same `component_item_id` as the BOM's own `item_id` (no self-referential BOM). Circular BOM structures are forbidden.

### operation
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| work_order_id | string | yes | FK to work-order entity. |
| name | string | yes | Operation name (e.g., "Cutting", "Assembly", "QC Check"). |
| sequence | integer | yes | Execution order within the work order. |
| status | string (enum: pending/in-progress/completed/skipped) | yes | Operation status. |
| machine_id | string | no | FK to machine/resource (if applicable). |
| actual_start | string (iso8601) | no | When the operation actually started. |
| actual_end | string (iso8601) | no | When the operation actually ended. |

**Constraints**: `sequence` must be unique within a work order. Operations must be completed in `sequence` order unless explicitly marked `skipped`. `actual_end` must be >= `actual_start` when both are provided.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **release-work-order**: Validates component availability in inventory, transitions work order from `draft` to `released`, and reserves the required components via `inventory.reserve`. Future wire key: `production.release`.
- **complete-operation**: Records `actual_start`/`actual_end` for an operation, marks it `completed`, and advances the work order's progress. Future wire key: `production.complete-op`.
- **close-work-order**: Confirms final `quantity_produced`, consumes reserved components from inventory, produces a finished-goods stock movement, and transitions status to `completed`. Future wire key: `production.close-wo`.

## Business Rules
1. A work order may only be released (`production.release`) when sufficient inventory stock is available for all `is_critical: true` BOM components.
2. Operations must be completed in their defined `sequence` order; attempting to complete an operation out of sequence must be rejected unless all preceding operations are `completed` or `skipped`.
3. `quantity_produced` must not exceed `quantity_planned`; over-production requires a separate adjustment and managerial sign-off.
4. Closing a work order (`production.close-wo`) is only allowed when all operations are in `completed` or `skipped` status.

## Integration Points
- **→ inventory**: Work-order release triggers `inventory.reserve` for components; close triggers `inventory.adjust` (component consumption and finished-goods receipt).
- **→ quality**: Work-order completion triggers creation of an `inspection-plan` in the quality domain for finished-goods QC.
- **→ reporting**: Production throughput, operation cycle times, and waste/scrap ratios are consumed by the reporting domain for OEE dashboards.
