---
domain: logistics
label: Logistics & Shipping
version: "1.0"
entities:
  - shipment
  - carrier
  - route
  - tracking-event
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Logistics & Shipping

## Purpose
Manages outbound and inbound shipments from dispatch through delivery, including carrier contracts, predefined routes, and the immutable chain of tracking events. Primary personas: warehouse operator dispatching shipments, logistics coordinator tracking in-transit goods, and customer-facing IT-담당자 exposing delivery status. Core value: full traceability of goods movement with a reliable, append-only event trail.

## Core Entities

### shipment
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| shipment_number | string | yes | Human-readable unique identifier. |
| carrier_id | string | yes | FK to carrier entity. |
| route_id | string | no | FK to route entity (optional for ad-hoc shipments). |
| origin_address | string | yes | Departure address (free-text or structured). |
| destination_address | string | yes | Delivery address. |
| status | string (enum: draft/dispatched/in-transit/out-for-delivery/delivered/returned/cancelled) | yes | Current shipment status. |
| estimated_delivery | string (iso8601) | no | Carrier-provided ETA. |
| weight_kg | number | no | Total shipment weight in kilograms. |

**Constraints**: `shipment_number` must be unique. Once `status` is `delivered` or `returned`, no further status transitions are allowed. A cancelled shipment cannot be re-activated.

### carrier
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Short carrier code (e.g., FEDEX, DHL, CJ). |
| name | string | yes | Full carrier name. |
| tracking_url_template | string | no | URL template with `{tracking_number}` placeholder. |
| is_active | boolean | yes | Whether the carrier accepts new shipments. |

**Constraints**: `code` must be unique. Inactive carriers cannot be assigned to new shipments.

### route
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| name | string | yes | Route display name. |
| carrier_id | string | yes | FK to carrier that operates this route. |
| origin_hub | string | yes | Departure hub identifier. |
| destination_hub | string | yes | Destination hub identifier. |
| transit_days | integer | yes | Standard transit time in business days. |
| is_active | boolean | yes | Whether new shipments may use this route. |

**Constraints**: A route must reference an active carrier. Deactivating a route does not affect in-flight shipments already assigned to it.

### tracking-event
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| shipment_id | string | yes | FK to shipment entity. |
| event_time | string (iso8601) | yes | When the event occurred (carrier-reported). |
| event_code | string | yes | Standardised event code (e.g., PICKUP, TRANSIT, DELIVERED). |
| location | string | no | Location where the event occurred. |
| message | string | no | Human-readable event description. |

**Constraints**: Tracking events are append-only; existing events must not be updated or deleted. `event_time` may differ from `created_at` (carrier-reported vs. system-ingested time).

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **dispatch-shipment**: Transitions a shipment from `draft` to `dispatched`, assigns a tracking number from the carrier, and records a PICKUP tracking event. Future wire key: `logistics.dispatch`.
- **update-tracking**: Ingests one or more tracking events from a carrier webhook or polling job and advances shipment status accordingly. Future wire key: `logistics.track`.
- **confirm-delivery**: Marks a shipment `delivered`, records a DELIVERED tracking event with GPS/timestamp, and triggers downstream inventory and finance notifications. Future wire key: `logistics.deliver`.

## Business Rules
1. Tracking events are immutable once written; deletion is forbidden even for erroneous entries (append a corrective event instead).
2. A shipment cannot be dispatched (`logistics.dispatch`) if its assigned carrier is inactive.
3. Status transitions must follow the defined state machine; skipping states (e.g., `draft` → `delivered` directly) is rejected at the application layer.
4. A shipment in `delivered`, `returned`, or `cancelled` status is terminal and must not accept further status-changing operations.

## Integration Points
- **→ inventory**: A `delivered` inbound shipment triggers `inventory.adjust` to increase stock levels for the received items.
- **→ sales**: Outbound shipment status changes are surfaced to the sales domain so sales-order fulfillment status stays in sync.
- **→ reporting**: Carrier on-time delivery rates and transit-time averages are aggregated by the reporting domain.
