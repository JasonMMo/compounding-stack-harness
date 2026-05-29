---
domain: inventory
label: Inventory Management
version: "1.0"
entities:
  - item
  - warehouse
  - stock-level
  - stock-movement
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Inventory Management

## Purpose
Tracks the quantity and location of every stocked item across one or more warehouses, recording every movement that changes stock as an immutable ledger entry. Primary personas: warehouse manager, purchasing officer, and operations analyst reviewing stock health. Core value: a real-time, auditable picture of what is on hand, where it is, and how it got there.

## Core Entities

### item
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| sku | string | yes | Stock-keeping unit code; unique. |
| name | string | yes | Item display name. |
| unit_of_measure | string | yes | Base UOM (e.g., EA, KG, BOX). |
| reorder_point | number | no | Stock level that triggers a reorder alert. |
| allow_negative_stock | boolean | yes | Whether stock level may go below zero. |

**Constraints**: `sku` must be unique. `allow_negative_stock` defaults to `false`; customer profile may override per-item.

### warehouse
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Short alphanumeric warehouse code. |
| name | string | yes | Warehouse display name. |
| address | string | no | Physical address. |
| is_active | boolean | yes | Whether the warehouse accepts stock movements. |

**Constraints**: `code` must be unique. Inactive warehouses must not be the target of new stock-movement records.

### stock-level
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| item_id | string | yes | FK to item entity. |
| warehouse_id | string | yes | FK to warehouse entity. |
| quantity_on_hand | number | yes | Current physical quantity. |
| quantity_reserved | number | yes | Quantity reserved for pending orders. |
| quantity_available | number | yes | Computed: on_hand − reserved (read-only). |

**Constraints**: The pair (`item_id`, `warehouse_id`) must be unique. `quantity_available` is a derived field; adapters must not write it directly. Unless `item.allow_negative_stock` is `true`, `quantity_on_hand` must not go below zero.

### stock-movement
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| item_id | string | yes | FK to item entity. |
| warehouse_id | string | yes | FK to warehouse entity. |
| movement_type | string (enum: receipt/issue/transfer/adjustment/return) | yes | Nature of the movement. |
| quantity | number | yes | Signed quantity delta (positive = in, negative = out). |
| reference_id | string | no | Source document ID (shipment, order, etc.). |
| reference_type | string | no | Entity type of the source document. |
| moved_at | string (iso8601) | yes | Business timestamp of the movement. |

**Constraints**: Stock movements are append-only; existing records must not be updated or deleted. Every movement must update the corresponding `stock-level` record atomically.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **adjust-stock**: Creates a signed `adjustment` stock-movement and updates `stock-level.quantity_on_hand` atomically. Used for cycle-count corrections. Future wire key: `inventory.adjust`.
- **transfer-stock**: Moves quantity from one warehouse to another by creating two linked movements (issue + receipt) in a single transaction. Future wire key: `inventory.transfer`.
- **reserve-stock**: Increments `quantity_reserved` for items allocated to a confirmed order, reducing `quantity_available` without changing `quantity_on_hand`. Future wire key: `inventory.reserve`.

## Business Rules
1. Unless `item.allow_negative_stock` is `true` for the item (or the customer profile enables it globally), no operation may reduce `stock-level.quantity_on_hand` below zero.
2. Stock movements are append-only; corrections are made by posting a new movement with the opposite sign, not by editing the original.
3. An `inventory.transfer` must be atomic: both the issue and receipt legs must succeed or both must be rolled back.
4. `inventory.reserve` must not reserve more than `quantity_available`; attempting to over-reserve must be rejected at the application layer.

## Integration Points
- **→ logistics**: An inbound delivery confirmation (`logistics.deliver`) triggers `inventory.adjust` to increase on-hand stock.
- **→ sales**: A confirmed sales order triggers `inventory.reserve` to allocate stock before physical fulfillment.
- **→ procurement**: A goods-receipt event from the procurement domain triggers `inventory.adjust` with movement type `receipt`.
- **→ reporting**: Stock-level snapshots and movement history feed inventory valuation and turnover reports.
