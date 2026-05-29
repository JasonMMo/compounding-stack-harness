---
domain: asset
label: Asset Management
version: "1.0"
entities:
  - asset
  - asset-category
  - depreciation-schedule
  - maintenance-record
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Asset Management

## Purpose
Manages the full lifecycle of physical and digital fixed assets: acquisition, categorisation, depreciation tracking, and maintenance history. Primary personas: finance accountant calculating depreciation, facilities manager scheduling maintenance, and IT-담당자 tracking hardware inventory. Core value: an auditable register of every company asset with current book value and maintenance health, satisfying both accounting and operational requirements.

## Core Entities

### asset
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| asset_number | string | yes | Human-readable unique asset tag. |
| name | string | yes | Asset display name. |
| category_id | string | yes | FK to asset-category entity. |
| acquisition_date | string (date) | yes | Date the asset was acquired. |
| acquisition_cost | number | yes | Original purchase price. |
| current_book_value | number | yes | Net book value after accumulated depreciation. |
| status | string (enum: active/under-maintenance/disposed/written-off) | yes | Asset lifecycle status. |
| location | string | no | Physical or logical location of the asset. |
| serial_number | string | no | Manufacturer serial number. |

**Constraints**: `asset_number` must be unique. `current_book_value` must be >= 0. A `disposed` or `written-off` asset is terminal and must not be assigned a new maintenance schedule.

### asset-category
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Short category code (e.g., IT-HW, VEHICLE, MACHINERY). |
| name | string | yes | Category display name. |
| default_useful_life_years | integer | yes | Standard depreciation period in years for this category. |
| depreciation_method | string (enum: straight-line/declining-balance/units-of-production) | yes | Default method for new assets in this category. |

**Constraints**: `code` must be unique. `default_useful_life_years` must be > 0. A category with existing assets may not have its `depreciation_method` changed (would invalidate existing schedules).

### depreciation-schedule
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| asset_id | string | yes | FK to asset entity. |
| method | string (enum: straight-line/declining-balance/units-of-production) | yes | Depreciation method applied. |
| useful_life_years | integer | yes | Total depreciation period in years. |
| salvage_value | number | yes | Residual value at end of useful life. |
| start_date | string (date) | yes | Date depreciation begins. |
| annual_depreciation | number | yes | Calculated annual charge. |
| accumulated_depreciation | number | yes | Total depreciation posted to date. |

**Constraints**: One active depreciation schedule per asset at any time. `salvage_value` must be < `asset.acquisition_cost`. `accumulated_depreciation` must not exceed `acquisition_cost - salvage_value`.

### maintenance-record
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| asset_id | string | yes | FK to asset entity. |
| maintenance_type | string (enum: preventive/corrective/inspection/upgrade) | yes | Type of maintenance performed. |
| performed_at | string (iso8601) | yes | When maintenance was carried out. |
| performed_by | string | yes | Technician or vendor name. |
| cost | number | no | Cost of the maintenance activity. |
| description | string | yes | What was done. |
| next_due_date | string (date) | no | Scheduled date of the next maintenance. |

**Constraints**: Maintenance records are append-only; existing records must not be modified after creation. `next_due_date` must be >= `performed_at` date when set.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **register-asset**: Creates the asset record, generates a depreciation schedule based on the category defaults, and records an acquisition maintenance entry. Future wire key: `asset.register`.
- **record-depreciation**: Posts the periodic depreciation charge, updates `current_book_value` and `accumulated_depreciation` atomically, and creates a finance journal entry. Future wire key: `asset.depreciate`.
- **schedule-maintenance**: Creates a scheduled maintenance record with a `next_due_date`, sets asset status to `under-maintenance` if the maintenance is immediate, and notifies the assigned technician. Future wire key: `asset.schedule-maintenance`.

## Business Rules
1. An asset's `current_book_value` must equal `acquisition_cost` minus `accumulated_depreciation`; the adapter must recompute and write this value whenever depreciation is posted.
2. Depreciation must not be posted against a `disposed` or `written-off` asset.
3. Only one active depreciation schedule is permitted per asset; creating a second schedule must first close the existing one.
4. A `disposed` or `written-off` asset must not have new maintenance records created against it.

## Integration Points
- **→ finance**: `asset.depreciate` triggers a journal entry in the finance domain posting the depreciation expense and accumulated depreciation.
- **→ procurement**: Asset acquisition is triggered by a goods-receipt in the procurement domain, passing the `total_amount` as `acquisition_cost`.
- **→ reporting**: Asset net-book-value summaries, upcoming maintenance schedules, and depreciation forecasts are consumed by the reporting domain.
