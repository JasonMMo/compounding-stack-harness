# Form — Visual Standard

Applies to: entity.create, entity.update, auth.login — any screen where user submits data to the wire contract.

## Field anatomy

```
┌────────────────────────────────────────────────────────────┐
│  Label text  [required marker *]                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Input value or placeholder                          │  │
│  └──────────────────────────────────────────────────────┘  │
│  Helper text or validation message                         │
└────────────────────────────────────────────────────────────┘
```

- Label: always visible, never placeholder-only. WCAG 1.3.1 / KWCAG 1.3.1.
- Required marker: `*` after label, with `aria-required="true"` on the input.
- Helper text: below input, `font.caption`, `color.text-3`.
- Validation message: replaces helper text, `color.danger`, `font.caption`.

## Input states

```
State       Border                  Background      Text
──────────────────────────────────────────────────────────
default     color.border-input      surface-1       text-1
hover       color.border-strong     surface-1       text-1
focus       color.border-focus (2px) surface-1      text-1   + shadow.focus-ring
filled      color.border-input      surface-1       text-1
error       color.danger-border     danger-subtle   text-1
disabled    color.border            surface-2       text-disabled
readonly    color.border            surface-2       text-2
```

## Input sizing

```
Height:   36px (md, default)
Padding:  var(--space-inset-sm) var(--space-inset-md)    (top/bottom, left/right)
Radius:   var(--radius-input)
Font:     var(--font-size-md) / var(--font-family-body)
```

## Tokens used

```
Label:
  font-size:   var(--font-size-sm)
  font-weight: var(--font-weight-label)
  color:       var(--color-text-2)
  margin-bottom: var(--space-gap-xs)

Input:
  height:        36px
  padding:       var(--space-inset-sm) var(--space-inset-md)
  border:        1px solid var(--color-border-input)
  border-radius: var(--radius-input)
  background:    var(--color-surface-1)
  color:         var(--color-text-1)
  font-size:     var(--font-size-md)
  font-family:   var(--font-family-body)
  transition:    var(--motion-transition-control)

Focus (added):
  border-color:  var(--color-border-focus)
  outline:       2px solid var(--color-border-focus)
  outline-offset: -1px
  box-shadow:    var(--shadow-focus-ring)

Error (added):
  border-color:  var(--color-danger-border)
  background:    var(--color-danger-subtle)

Helper / error text:
  font-size:     var(--font-size-xs)
  color:         var(--color-text-3)   [helper] / var(--color-danger) [error]
  margin-top:    var(--space-gap-xs)
```

## Form layout grid

```
Single column (mobile, ops default for complex forms):
┌────────────────────────────────────┐
│ Label                              │
│ ┌──────────────────────────────┐   │
│ │ Input                        │   │
│ └──────────────────────────────┘   │
│ Label                              │
│ ┌──────────────────────────────┐   │
│ │ Input                        │   │
│ └──────────────────────────────┘   │
│               [Cancel]  [Save]     │
└────────────────────────────────────┘

Two column (ops, wider screens, related fields):
┌─────────────────────┬──────────────────────┐
│ Label               │ Label                │
│ ┌─────────────────┐ │ ┌──────────────────┐ │
│ │ Input           │ │ │ Input            │ │
│ └─────────────────┘ │ └──────────────────┘ │
└─────────────────────┴──────────────────────┘
```

Field gap within column: `var(--space-stack-md)`.
Column gap: `var(--space-gap-xl)`.

## Select / dropdown

Same dimensions and state tokens as text input. Use native `<select>` for vanilla-htmx adapter — custom dropdown requires JS component which is out of scope for v1. Custom chevron icon via CSS background-image.

## Textarea

Same tokens as input. Min-height: 80px (3 rows equivalent). Resize: vertical only.

## Fieldset / group

```
<fieldset>
  <legend> — font.label, color.text-2, margin-bottom gap-sm
  [fields...]
</fieldset>
```

Border: none (use visual grouping via surface-2 background + radius.card padding instead for modern look).

## Form action bar

Primary and secondary actions at BOTTOM of form (not top). Right-aligned.

```
┌────────────────────────────────────────────────────────┐
│                                [Cancel]  [Save Record] │
└────────────────────────────────────────────────────────┘
```

Space between buttons: `var(--space-gap-sm)`.
Margin-top from last field: `var(--space-stack-lg)`.

## a11y requirements

- All inputs have a visible `<label>` with `for` matching input `id`. No `placeholder` as sole label.
- Error messages associated via `aria-describedby` pointing to the error `<span id>`.
- Error state also announced by `role="alert"` on the error container or by `aria-live="polite"` on the form status region.
- Tab order follows visual top-to-bottom, left-to-right flow. Do not manipulate `tabindex` beyond 0/-1.
- Form submission errors: focus moves to first error field or to an error summary at top of form (KWCAG 3.3.1).
- `autocomplete` attributes on auth fields: `username`, `current-password`, `new-password` per HTML spec.
- Persona: IT persona shows all fields including system/audit fields (id, created_at, updated_at) as readonly inputs. CEO and ops personas hide system fields by default.
