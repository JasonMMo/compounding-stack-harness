# Seed Format Specification — presets/skills/generic/

> CTO decision (Growth-6). This file is the canonical format reference for all `*.seed.md` files under this directory.
> All domain seeds MUST follow this structure. Tooling and the domain-expert-generic agent parse this shape.

## File naming

```
presets/skills/generic/<domain-slug>.seed.md
```

`<domain-slug>` must be an ASCII slug (G-8): lowercase letters and hyphens only.

## Format

```markdown
---
domain: <slug>            # ASCII slug, matches file name
label: <Human Label>      # Title-cased display name
version: "1.0"
entities:                 # wire entity_type slugs this domain exposes
  - <entity-slug>
wire_keys:                # wire-v1.yaml keys this domain uses today
  - entity.read
  - entity.list
  - entity.create
  - entity.update
  - entity.delete
---

# <Label>

## Purpose
One paragraph: what this domain manages, which business persona uses it, and the core value delivered.

## Core Entities

### <entity-slug>
| Field | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Primary key (UUID). |
| ... | ... | ... | ... |

**Constraints**: free-prose invariants specific to this entity.

## Domain Operations
Operations beyond generic CRUD (entity.read / list / create / update / delete).
List only operations that require a new wire key when the first adapter lands.

- **<operation>**: Description. Future wire key: `<domain>.<verb>`.

## Business Rules
Numbered invariants an adapter MUST enforce at the application layer.
1. ...

## Integration Points
Cross-domain dependencies — upstream data this domain reads, downstream events it emits.
- **→ <other-domain>**: relationship (e.g., "employee is referenced by leave-request.employee_id").
```

## Principles (Karpathy seed philosophy)

- **Minimal**: only what a new engineer needs to understand the domain in 2 minutes. No implementation details.
- **Machine-parseable**: YAML frontmatter gives tooling the index; markdown body gives the expert agent context.
- **Compound-friendly**: when a new operation or entity is discovered in a real customer project, update the seed — never duplicate the definition elsewhere.
- **Wire-aware**: `wire_keys` must stay in sync with `middle/contract/wire-v1.yaml`. Seeds reference keys; they do not define them.
