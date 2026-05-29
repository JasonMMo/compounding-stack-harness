---
domain: sales
label: Sales Management
version: "1.0"
entities:
  - sales-order
  - sales-order-line
  - price-list
  - discount
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Sales Management

## Purpose
Manages the full sales-order lifecycle from quote through fulfilment, backed by configurable price lists and discount rules. Primary personas: sales representative creating orders, sales manager approving discounts, and customer service agent tracking order status. Core value: a controlled, auditable process from customer request to revenue recognition that enforces pricing rules consistently.

## Core Entities

### sales-order
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| order_number | string | yes | Human-readable unique order identifier. |
| customer_id | string | yes | FK to CRM contact or customer record. |
| order_date | string (date) | yes | Date the order was placed. |
| status | string (enum: draft/confirmed/partially-fulfilled/fulfilled/cancelled) | yes | Order lifecycle status. |
| currency | string | yes | ISO 4217 currency code for this order. |
| total_amount | number | yes | Sum of all line amounts after discounts. |
| price_list_id | string | no | FK to price-list used for this order. |

**Constraints**: `order_number` must be unique. Orders in `fulfilled` or `cancelled` status are immutable. `total_amount` must equal the sum of all linked `sales-order-line.line_total` values.

### sales-order-line
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| order_id | string | yes | FK to sales-order entity. |
| item_id | string | yes | FK to inventory item entity. |
| quantity | number | yes | Ordered quantity (must be > 0). |
| unit_price | number | yes | Price per unit at time of order. |
| discount_id | string | no | FK to discount applied to this line. |
| discount_amount | number | no | Computed discount amount (read-only). |
| line_total | number | yes | (quantity × unit_price) − discount_amount. |

**Constraints**: `quantity` must be greater than zero. `line_total` is a derived field; adapters must recompute it whenever `quantity`, `unit_price`, or `discount_id` changes. Lines may not be added to a `cancelled` or `fulfilled` order.

### price-list
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| name | string | yes | Price-list display name. |
| currency | string | yes | ISO 4217 currency code this list applies to. |
| valid_from | string (date) | yes | Date from which the price list is effective. |
| valid_to | string (date) | no | Expiry date (null = indefinite). |
| is_default | boolean | yes | Whether this list is applied when no explicit list is chosen. |

**Constraints**: Only one price list per currency may have `is_default: true` at any time. `valid_to` must be >= `valid_from` when set.

### discount
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Unique discount code. |
| discount_type | string (enum: percentage/fixed-amount) | yes | How the discount is calculated. |
| value | number | yes | Percentage (0–100) or fixed amount depending on `discount_type`. |
| valid_from | string (date) | yes | Effective start date. |
| valid_to | string (date) | no | Expiry date (null = indefinite). |
| min_order_amount | number | no | Minimum order value required to apply this discount. |

**Constraints**: `code` must be unique. Percentage discounts must have `value` between 0 and 100 (exclusive). Fixed-amount discounts must not exceed the line total they are applied to.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **confirm-order**: Validates stock availability via `inventory.reserve`, transitions order from `draft` to `confirmed`, and triggers invoice creation in the finance domain. Future wire key: `sales.confirm`.
- **fulfill-order**: Records shipment dispatch, transitions order to `fulfilled` (or `partially-fulfilled`), and updates inventory stock levels. Future wire key: `sales.fulfill`.
- **cancel-order**: Releases any inventory reservations, transitions order to `cancelled`, and voids any associated invoice if unpaid. Future wire key: `sales.cancel`.

## Business Rules
1. An order may only be confirmed (`sales.confirm`) if all line items have sufficient available stock in inventory (respects `inventory.reserve` rules).
2. Discounts applied to order lines must be within their `valid_from`/`valid_to` window at the time the order is confirmed; expired discounts are rejected at confirmation.
3. `sales-order.total_amount` must always equal the sum of all `sales-order-line.line_total` values; any edit to a line must trigger a recalculation of the order total.
4. Cancellation of a confirmed order automatically releases reserved inventory via `inventory.reserve` reversal.

## Integration Points
- **→ inventory**: Order confirmation triggers `inventory.reserve`; fulfillment triggers stock-level deduction via `inventory.adjust`.
- **→ finance**: A confirmed sales order triggers creation of a receivable invoice in the finance domain.
- **→ logistics**: Order fulfillment creates a shipment record in the logistics domain.
- **→ crm**: Order creation and status changes update the associated CRM opportunity pipeline stage.
