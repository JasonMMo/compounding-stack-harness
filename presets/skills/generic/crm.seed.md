---
domain: crm
label: CRM
version: "1.0"
entities:
  - contact
  - lead
  - opportunity
  - activity
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# CRM

## Purpose
Manages the customer relationship pipeline from first contact through closed deal, tracking leads, opportunities, and every customer-facing activity in between. Primary personas: sales representative managing their pipeline, sales manager reviewing team performance, and account manager nurturing existing customers. Core value: a unified view of every prospect and customer interaction that prevents deals from falling through the cracks.

## Core Entities

### contact
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| full_name | string | yes | Contact's full name. |
| email | string | no | Primary email address. |
| phone | string | no | Primary phone number. |
| company_name | string | no | Organization the contact belongs to. |
| contact_type | string (enum: prospect/customer/partner/vendor) | yes | Relationship classification. |
| owner_id | string | no | FK to the employee responsible for this contact. |

**Constraints**: At least one of `email` or `phone` must be present. `email` must be unique when provided. A contact's `contact_type` may be updated as the relationship evolves.

### lead
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| contact_id | string | no | FK to contact entity (set after qualification). |
| source | string (enum: web/referral/event/cold-call/other) | yes | How the lead was acquired. |
| status | string (enum: new/contacted/qualified/converted/disqualified) | yes | Lead lifecycle status. |
| estimated_value | number | no | Rough deal size estimate. |
| assigned_to | string | no | FK to employee working the lead. |

**Constraints**: A lead in `converted` status must have an associated `opportunity` record. A `disqualified` lead must include a disqualification reason (stored in `activity` log).

### opportunity
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| contact_id | string | yes | FK to contact entity. |
| lead_id | string | no | FK to originating lead (if converted). |
| name | string | yes | Short description of the deal. |
| stage | string (enum: prospecting/qualification/proposal/negotiation/closed-won/closed-lost) | yes | Sales pipeline stage. |
| amount | number | yes | Expected deal value. |
| probability | integer | yes | Win probability 0–100. |
| expected_close_date | string (date) | yes | Forecasted close date. |
| owner_id | string | yes | FK to employee owning the opportunity. |

**Constraints**: `probability` must be between 0 and 100. `closed-won` and `closed-lost` are terminal stages. `amount` must be >= 0.

### activity
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| activity_type | string (enum: call/email/meeting/note/task) | yes | Type of customer interaction. |
| contact_id | string | yes | FK to contact entity. |
| opportunity_id | string | no | FK to opportunity (if related). |
| lead_id | string | no | FK to lead (if related). |
| performed_by | string | yes | FK to employee who logged the activity. |
| performed_at | string (iso8601) | yes | When the activity occurred. |
| summary | string | yes | Brief description of what happened. |
| outcome | string | no | Result of the interaction (e.g., "demo scheduled"). |

**Constraints**: Activities are append-only for audit purposes; existing activity records should not be modified after creation. At least one of `opportunity_id` or `lead_id` should be provided for pipeline-linked activities, though standalone contact activities (e.g., support calls) are allowed.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **convert-lead**: Qualifies a lead, creates a contact record (if not already linked), creates an opportunity, and transitions the lead status to `converted` atomically. Future wire key: `crm.convert-lead`.
- **log-activity**: Creates an activity record linked to a contact, lead, or opportunity and updates the parent record's `updated_at` to surface it in recent-activity views. Future wire key: `crm.log-activity`.
- **score-opportunity**: Recalculates the opportunity's `probability` score based on stage, activity recency, and configured scoring model, then writes the updated value. Future wire key: `crm.score`.

## Business Rules
1. A lead cannot be marked `converted` without an associated `opportunity` record being created in the same operation.
2. `probability` must be 0 for `closed-lost` and 100 for `closed-won`; the adapter must enforce these values on stage transition.
3. At least one of `email` or `phone` must be present on a contact record; a contact with neither is rejected at creation.
4. An activity linked to a `closed-won` or `closed-lost` opportunity is allowed (post-close follow-up); no restriction on activity creation by opportunity stage.

## Integration Points
- **→ sales**: A `closed-won` opportunity triggers creation of a sales order in the sales domain; `contact_id` maps to `sales-order.customer_id`.
- **→ approval**: High-value opportunities (above a configurable threshold) may require manager approval before a proposal is sent, triggering an `approval.approval-request`.
- **→ reporting**: Pipeline stage distribution, win rates, and activity cadence are consumed by the reporting domain for sales performance dashboards.
