---
domain: document
label: Document Management
version: "1.0"
entities:
  - document
  - document-version
  - document-category
  - access-rule
wire_keys:
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# Document Management

## Purpose
Manages the full lifecycle of business documents — creation, versioning, publishing, access control, and archival. Primary personas: business user uploading and sharing documents, department manager controlling who can access sensitive files, and compliance officer ensuring retention policies are met. Core value: a structured, version-controlled document repository with fine-grained access control that prevents unauthorised disclosure and ensures the right people always find the current version.

## Core Entities

### document
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| title | string | yes | Document display title. |
| category_id | string | yes | FK to document-category entity. |
| owner_id | string | yes | FK to employee who owns/authored the document. |
| status | string (enum: draft/published/archived/deleted) | yes | Document lifecycle status. |
| current_version_id | string | no | FK to the active document-version (set after first upload). |
| retention_date | string (date) | no | Date after which the document may be purged per retention policy. |

**Constraints**: A `deleted` document is soft-deleted; its record is retained for audit. The `current_version_id` always points to the latest published version; drafts do not advance it. An `archived` document is read-only.

### document-version
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| document_id | string | yes | FK to document entity. |
| version_number | string | yes | Version label (e.g., "1.0", "2.3", "DRAFT-4"). |
| uploaded_by | string | yes | FK to employee who uploaded this version. |
| file_name | string | yes | Original filename including extension. |
| file_size_bytes | integer | yes | File size in bytes. |
| mime_type | string | yes | MIME type (e.g., application/pdf, image/png). |
| storage_key | string | yes | Opaque storage reference (S3 key or filesystem path). |
| checksum | string | yes | SHA-256 hash of the file contents. |
| is_published | boolean | yes | Whether this version is the active published version. |

**Constraints**: Version numbers must be unique within a document. Document versions are immutable once uploaded; the file bytes must not be modified (upload a new version instead). Only one version per document may have `is_published: true` at a time.

### document-category
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| code | string | yes | Short alphanumeric category code. |
| name | string | yes | Category display name. |
| parent_id | string | no | FK to parent category (supports hierarchy). |
| default_retention_days | integer | no | Default retention period in days for documents in this category. |

**Constraints**: `code` must be unique. Circular parent references are forbidden. A category cannot be deleted while it has documents; reassign documents first.

### access-rule
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| created_at | string (iso8601) | yes | Record creation timestamp. |
| updated_at | string (iso8601) | yes | Last modification timestamp. |
| document_id | string | yes | FK to document this rule applies to. |
| principal_type | string (enum: employee/department/role) | yes | Type of entity being granted access. |
| principal_id | string | yes | ID of the employee, department, or role. |
| permission | string (enum: read/edit/admin) | yes | Access level granted. |
| expires_at | string (iso8601) | no | Optional expiry for time-limited access. |

**Constraints**: The combination (`document_id`, `principal_type`, `principal_id`) must be unique. An expired access rule (`expires_at` in the past) is treated as non-existent; adapters must not serve document content based on expired rules.

## Domain Operations
Operations beyond generic CRUD that require a dedicated wire key when the first adapter lands.

- **upload-version**: Accepts the file binary, computes checksum, stores the file via the configured storage adapter, creates a `document-version` record, and optionally advances to `is_published: true`. Future wire key: `document.upload`.
- **publish-document**: Sets a specific `document-version` as the active published version, updates `document.current_version_id`, and transitions document status to `published`. Future wire key: `document.publish`.
- **archive-document**: Transitions document status to `archived`, making it read-only while retaining all versions and access history. Future wire key: `document.archive`.

## Business Rules
1. Document versions are immutable once uploaded; the underlying file bytes must never be modified in-place — a new version must be created for any change.
2. Only one document-version per document may have `is_published: true` at any time; publishing a new version must atomically unpublish the previous one.
3. Access rules with an `expires_at` in the past must be treated as if they do not exist; the adapter must enforce this check at read time, not just at write time.
4. An `archived` document is read-only; any write operation (version upload, access-rule change, metadata edit) must be rejected until the document is un-archived by an admin.

## Integration Points
- **→ approval**: A document requiring manager sign-off before publication triggers an `approval.approval-request` linked to the document and version.
- **→ hr**: Access rules referencing `principal_type: employee` or `principal_type: department` resolve their principals via the HR domain.
- **→ reporting**: Document creation rates, access frequency, and upcoming retention-date expirations are consumed by the reporting domain for compliance dashboards.
