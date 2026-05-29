# Table — Visual Standard

Applies to: entity.list response rendering. The primary data display component for all three personas, though density and default row count differ.

## Anatomy

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [+ New]   [Search: ____________]                      Showing 1-20/143 │
├──────┬───────────────┬────────────────┬──────────────┬──────────────────┤
│  ID  │  Name         │  Status        │  Created     │  Actions         │
├──────┼───────────────┼────────────────┼──────────────┼──────────────────┤
│  1   │  Acme Corp    │  ● Active      │  2026-05-01  │  [Edit] [Delete] │
│  2   │  Beta Ltd     │  ○ Inactive    │  2026-05-03  │  [Edit] [Delete] │
│  3   │  Gamma Inc    │  ⚠ Degraded   │  2026-05-07  │  [Edit] [Delete] │
├──────┴───────────────┴────────────────┴──────────────┴──────────────────┤
│  [< Prev]   Page 1 of 8   [Next >]                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

- Toolbar: action buttons (New) + search input left, count right.
- Header row: `font.label`, `color.text-2`, `surface-3` background, sortable columns show arrow icon.
- Body rows: `font.body`, `color.text-1`, alternating `surface-1` / `surface-2`.
- Actions column: right-aligned, condensed buttons.
- Pagination bar: below table, centered.

## Row states

```
State         Background          Text
────────────────────────────────────────────
default       surface-1           text-1
stripe-alt    surface-2           text-1
hover         color.primary-subtle text-1
selected      color.primary-subtle + left border 2px color.primary  text-1
focus-cell    (focus ring on cell, not row)
```

Hover background: `color.primary-subtle` (`accent.050`). Subtle, not distracting.

## Row density (persona-driven)

```
Persona   Row height   Font size token       Padding x/y          Default page size
ceo       48px         font.size-md          inset-md / 14px       10
ops       36px         font.size-md          inset-sm / 10px       20  ← default
it        28px         font.size-sm (13px)   inset-xs / 6px        50
```

Row density is applied via `data-persona` attribute on the table wrapper — CSS handles the rest via persona token overrides. No JS branching needed.

## Column header

```
background:      var(--color-surface-3)
color:           var(--color-text-2)
font-size:       var(--font-size-sm)
font-weight:     var(--font-weight-label)
padding:         var(--space-inset-sm) var(--space-inset-md)
border-bottom:   1px solid var(--color-border-strong)
text-align:      left   (numbers: right)
white-space:     nowrap
```

Sortable column header: adds `cursor: pointer`, sort icon (`↑` / `↓` / `↕`), `aria-sort="ascending|descending|none"`.

## Cell

```
padding:         var(--space-inset-xs) var(--space-inset-md)
border-bottom:   1px solid var(--color-border)
vertical-align:  middle
overflow:        hidden
text-overflow:   ellipsis
max-width:       320px   (configurable per column)
```

## Status badge in cell

Inline colored badge using semantic status tokens:

```
status ok       background: color.success-subtle  color: color.status-ok  ● dot
status degraded background: color.warning-subtle  color: color.warning-text ⚠
status down     background: color.danger-subtle   color: color.danger      ✕
```

Badge radius: `var(--radius-badge)`. Padding: `2px 6px`. Font: `font.caption`.

## Actions column

Compact button group. Use ghost variant for Edit, danger-ghost for Delete.

```
┌───────────────┐
│  [Edit] [Del] │
└───────────────┘
```

Delete triggers a confirmation modal before dispatching entity.delete.

## Pagination

```
Offset mode (default):
  [< Prev]  [1] [2] [3] ... [8]  [Next >]
  Shows page numbers if total pages <= 7, else first/last + ellipsis.
  Current page: background color.primary, text color.text-on-primary.

Cursor mode (infinite / append):
  [Load more]  button, centered below table.
  Shows remaining count: "Load 20 more (83 remaining)"
```

Pagination tokens:
```
page-button size:    28px x 28px
page-button radius:  var(--radius-control)
page-current-bg:     var(--color-primary)
page-current-text:   var(--color-text-on-primary)
gap between buttons: var(--space-gap-xs)
```

## Empty state

```
┌──────────────────────────────────────────────┐
│                                              │
│           [icon: empty box]                  │
│         No records found.                    │
│    [+ Create your first record]              │
│                                              │
└──────────────────────────────────────────────┘
```

- `color.text-3`, `font.size-md`, centered.
- CTA button links to entity.create form.

## Tokens summary

```
Table wrapper:    background: var(--color-surface-1) / border: 1px solid var(--color-border) / border-radius: var(--radius-card) / box-shadow: var(--shadow-card)
Header:           background: var(--color-surface-3) / color: var(--color-text-2)
Row hover:        background: var(--color-primary-subtle)
Border:           var(--color-border)
Font body:        var(--font-size-md) / var(--font-family-body)
Font label:       var(--font-size-sm) / var(--font-weight-label)
```

## a11y requirements

- `<table>` element with `<thead>`, `<tbody>`, `<th scope="col">` on header cells.
- Sortable `<th>` has `aria-sort` attribute: `"none"` | `"ascending"` | `"descending"`.
- Row selection: `<tr aria-selected="true|false">` and `role="row"`.
- Caption: `<caption>` or `aria-label` on the table with entity type name.
- Keyboard: Tab to table, then arrow keys for cell navigation (implement `tabindex="-1"` on cells, roving focus pattern).
- Pagination: Each page button has `aria-label="Page N"`. Current page: `aria-current="page"`.
- Status badges: color alone is not sufficient — include text or icon glyph alongside color.
- Large tables (>50 rows): provide column filter / search to reduce cognitive load (KWCAG 2.4.3).
- IT persona 50-row default: implement virtual scroll or server-side paging — never load all 50 rows into DOM without paging (performance + screen reader issue).
