---
domain: procurement
label: Procurement
version: "1.0"
entities:
  - purchase-order
  - purchase-order-line
  - vendor
  - requisition
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Procurement

## Purpose
Controls the source-to-pay process: internal purchase requisitions, vendor management, purchase order issuance, and goods receipt. Primary personas: purchaser raising and approving orders, finance controller reconciling payables, and warehouse operator confirming received goods. Core value: a controlled spending process that ensures every purchase is authorized, traceable, and reconciled against actual delivery.

## Core Entities

### purchase-order
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| po_number | string | yes | Human-readable unique PO identifier. |
| vendor_id | string | yes | FK to vendor entity. |
| requisition_id | string | no | FK to originating requisition (if applicable). |
| order_date | string (date) | yes | Date the PO was issued. |
| expected_delivery | string (date) | no | Expected goods receipt date. |
| status | string (enum: draft/issued/partially-received/received/cancelled) | yes | PO lifecycle status. |
| total_amount | number | yes | Sum of all line amounts. |
| currency | string | yes | ISO 4217 currency code. |

**Constraints**: `po_number` must be unique. A `cancelled` PO cannot be re-activated. `total_amount` must equal the sum of linked `purchase-order-line.line_total` values.

### purchase-order-line
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| po_id | string | yes | FK to purchase-order entity. |
| item_id | string | yes | FK to inventory item entity. |
| quantity_ordered | number | yes | Ordered quantity (must be > 0). |
| quantity_received | number | yes | Cumulative received quantity (updated on goods receipt). |
| unit_price | number | yes | Agreed unit price. |
| line_total | number | yes | quantity_ordered × unit_price. |

**Constraints**: `quantity_ordered` must be > 0. `quantity_received` cannot exceed `quantity_ordered`. Lines cannot be added to a `cancelled` or fully `received` PO.

### vendor
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Short vendor identifier code. |
| name | string | yes | Vendor legal name. |
| contact_email | string | no | Primary procurement contact email. |
| payment_terms | string | no | Standard payment terms (e.g., Net30, Net60). |
| is_approved | boolean | yes | Whether the vendor is on the approved vendor list. |

**Constraints**: `code` must be unique. Purchase orders may only be issued to approved vendors (`is_approved: true`). Removing approval does not cancel existing POs.

### requisition
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| requester_id | string | yes | FK to employee who raised the request. |
| department_id | string | yes | FK to HR department entity. |
| status | string (enum: draft/pending/approved/rejected/converted) | yes | Approval status. |
| total_estimated | number | yes | Estimated total cost. |
| required_by | string (date) | yes | Date goods or services are needed. |
| description | string | yes | Summary of what is being requested. |

**Constraints**: A `converted` requisition must have at least one linked purchase order. Approved requisitions are read-only except for the conversion step.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **issue-po**: Transitions a purchase order from `draft` to `issued`, sends the PO to the vendor (via notification), and creates a payable entry in the finance domain. Future wire key: `procurement.issue-po`.
- **receive-goods**: Records partial or full goods receipt against a PO line, updates `quantity_received`, advances PO status, and triggers `inventory.adjust` to increase stock. Future wire key: `procurement.receive`.
- **approve-requisition**: Transitions a requisition from `pending` to `approved` or `rejected`, records the approver's decision, and notifies the requester. Future wire key: `procurement.approve-requisition`.

## Business Rules
1. Purchase orders may only be issued to vendors where `is_approved: true`; issuing to an unapproved vendor must be rejected at the application layer.
2. `quantity_received` on a PO line must never exceed `quantity_ordered`; over-receipt must be rejected and flagged as a discrepancy.
3. A requisition must be in `approved` status before it can be converted to a purchase order.
4. Cancelling a PO that has any received goods (`quantity_received > 0` on any line) must be blocked; a partial-return process must be completed first.

## Integration Points
- **→ finance**: A goods receipt (`procurement.receive`) triggers creation of an accounts-payable invoice in the finance domain with the PO's `total_amount`.
- **→ inventory**: `procurement.receive` triggers `inventory.adjust` to increase on-hand stock for the received items.
- **→ approval**: A requisition exceeding the configured spend threshold triggers an `approval.approval-request` before the requisition can advance.
- **→ reporting**: PO spend, vendor performance, and requisition cycle times feed procurement analytics in the reporting domain.
