# Skill Seeds — Asset Manifest

> Axis 1 (skill) of the 7-axis compound model (CLAUDE.md §3). Each seed is a
> Karpathy-style minimal domain definition the `domain-expert-*` agents curate
> into DDL / adapters. Format: [`generic/_seed-format.md`](generic/_seed-format.md).

## generic/ — 14 baseline domains (M1)

| Domain | Label | Entities | Future ops |
|---|---|---|---|
| [hr](generic/hr.seed.md) | Human Resources | employee, department, position, leave-request | hire / terminate / approve-leave |
| [finance](generic/finance.seed.md) | Finance & Accounting | account, journal-entry, invoice, payment | post-journal / reconcile / close-period |
| [logistics](generic/logistics.seed.md) | Logistics & Shipping | shipment, carrier, route, tracking-event | dispatch / track / deliver |
| [inventory](generic/inventory.seed.md) | Inventory Management | item, warehouse, stock-level, stock-movement | adjust / transfer / reserve |
| [sales](generic/sales.seed.md) | Sales Management | sales-order, sales-order-line, price-list, discount | confirm / fulfill / cancel |
| [crm](generic/crm.seed.md) | CRM | contact, lead, opportunity, activity | convert-lead / log-activity / score |
| [procurement](generic/procurement.seed.md) | Procurement | purchase-order, purchase-order-line, vendor, requisition | issue-po / receive / approve-requisition |
| [production](generic/production.seed.md) | Production & Manufacturing | work-order, bom, bom-line, operation | release / complete-op / close-wo |
| [quality](generic/quality.seed.md) | Quality Management | inspection-plan, inspection-result, defect, corrective-action | start-inspection / record-defect / close-ca |
| [project](generic/project.seed.md) | Project Management | project, task, milestone, resource-assignment | assign / progress / close-milestone |
| [asset](generic/asset.seed.md) | Asset Management | asset, asset-category, depreciation-schedule, maintenance-record | register / depreciate / schedule-maintenance |
| [document](generic/document.seed.md) | Document Management | document, document-version, document-category, access-rule | upload / publish / archive |
| [approval](generic/approval.seed.md) | Approval Workflow | approval-request, approval-step, approver, approval-decision | submit / approve / reject |
| [reporting](generic/reporting.seed.md) | Reporting & Analytics | report-definition, report-schedule, report-parameter, report-output | run / schedule / export |

## Adding industry verticals

New verticals land as `presets/skills/<industry>/*.seed.md` (e.g. `medical/`, `manufacturing/`), curated by the matching `.claude/agents/domain-expert-<industry>.md`. Follow `generic/_seed-format.md`. Update this manifest when a new domain or vertical is added.
