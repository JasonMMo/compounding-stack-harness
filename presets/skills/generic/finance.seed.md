---
domain: finance
label: Finance & Accounting
version: "1.0"
entities:
  - account
  - journal-entry
  - invoice
  - payment
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Finance & Accounting

## Purpose
Maintains the chart of accounts, double-entry journal ledger, accounts-receivable invoices, and payment records. Primary personas: finance controller, accountant, and CFO reviewing period-close reports. Core value: a tamper-evident, balanced ledger that satisfies audit requirements and feeds management reporting.

## Core Entities

### account
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Chart-of-accounts code (e.g., 1001). |
| name | string | yes | Account display name. |
| type | string (enum: asset/liability/equity/revenue/expense) | yes | Account classification. |
| currency | string | yes | ISO 4217 currency code (e.g., KRW, USD). |
| is_active | boolean | yes | Whether the account accepts new postings. |

**Constraints**: `code` must be unique. Inactive accounts (`is_active: false`) must not appear on new journal-entry lines. Deleting an account that has posted journal entries is forbidden; deactivate instead.

### journal-entry
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| entry_date | string (date) | yes | Accounting date of the entry. |
| reference | string | no | External reference number (e.g., invoice ID). |
| description | string | yes | Narrative describing the transaction. |
| status | string (enum: draft/posted/reversed) | yes | Posting status. |
| lines | array of objects | yes | Debit/credit lines (see constraints). |
| period_id | string | yes | FK to accounting period; must be open. |

**Constraints**: The sum of all debit amounts must equal the sum of all credit amounts before `finance.post-journal` is accepted (balanced-entry invariant). Posted entries are immutable; reversal requires a new counter-entry via `finance.post-journal`.

### invoice
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| invoice_number | string | yes | Human-readable unique invoice identifier. |
| counterparty_id | string | yes | FK to customer or vendor (CRM contact / procurement vendor). |
| issue_date | string (date) | yes | Date invoice was issued. |
| due_date | string (date) | yes | Payment due date. |
| total_amount | number | yes | Total invoice amount in `currency`. |
| currency | string | yes | ISO 4217 currency code. |
| status | string (enum: draft/issued/partially-paid/paid/overdue/cancelled) | yes | Lifecycle status. |

**Constraints**: `invoice_number` must be unique. An invoice in `paid` or `cancelled` status cannot be edited. `due_date` must be >= `issue_date`.

### payment
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| invoice_id | string | yes | FK to invoice being settled. |
| payment_date | string (date) | yes | Date payment was received or made. |
| amount | number | yes | Payment amount. |
| method | string (enum: bank-transfer/card/cash/cheque) | yes | Payment method used. |
| reference | string | no | Bank reference or transaction ID. |

**Constraints**: The sum of all payments linked to an invoice must not exceed `invoice.total_amount`. When the sum equals `total_amount`, the invoice status auto-transitions to `paid`.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **post-journal**: Validates balance (debits = credits), checks the accounting period is open, marks the entry `posted`, and writes the ledger impact atomically. Future wire key: `finance.post-journal`.
- **reconcile**: Matches open payments against invoices and marks matched invoices `paid`; produces a reconciliation report. Future wire key: `finance.reconcile`.
- **close-period**: Locks all journal entries in the period, runs closing entries, and prevents further postings. Future wire key: `finance.close-period`.

## Business Rules
1. Journal entries must balance: sum of all line debit amounts must equal sum of all line credit amounts before posting is accepted.
2. No postings are allowed to a closed accounting period; the adapter must reject `finance.post-journal` requests where `period_id` references a closed period.
3. An invoice in `paid` or `cancelled` status is immutable; any update attempt must be rejected with a descriptive error.
4. Payment amounts are always positive; negative adjustments use credit notes (a separate invoice with negative `total_amount`).

## Integration Points
- **→ procurement**: When goods are received against a purchase order, the purchase order's `total_amount` flows into an accounts-payable invoice automatically.
- **→ sales**: A confirmed sales order triggers creation of a receivable invoice in the finance domain.
- **→ reporting**: Period-close summaries and trial-balance data are consumed by the reporting domain for financial statements.
