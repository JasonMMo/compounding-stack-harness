# Design Tokens — Generator Spec and Reference Convention

## Layer structure

```
raw.json       Primitive values. No semantics. The most stable layer.
semantic.json  Meaning layer. Components reference ONLY these keys.
persona/
  ceo.json     Override keys only (low density)
  ops.json     Override keys only (medium density — closest to semantic baseline)
  it.json      Override keys only (high density, monospace)
```

Merge order: `raw.json` → `semantic.json` → `persona/<name>.json`

Persona files declare ONLY keys that differ. The CSS generator deep-merges in this order.

## Reference syntax

Semantic and persona values use curly-brace references:

```
"{color.accent.600}"
```

This resolves to the value at `raw.json → color → accent → 600`.

Dotted path segments map directly to JSON object keys at each level.

## CSS custom properties generator contract

The engineer's CSS generator must:

1. Parse `raw.json` and emit `:root` variables with double-underscore namespace:
   - `color.gray.900` → `--raw-color-gray-900: #111827;`
   - `space.8` → `--raw-space-8: 16px;`

2. Parse `semantic.json`, resolve all `{...}` references to their raw values, and emit:
   - `color.primary` → `--color-primary: #2563EB;`
   - `space.inset-md` → `--space-inset-md: 16px;`
   - `font.family-body` → `--font-family-body: -apple-system, ...;`
   - `shadow.focus-ring` → `--shadow-focus-ring: 0 0 0 3px rgba(...);`

3. For persona overrides, emit a scoped block that overrides only the declared keys:
   ```css
   [data-persona="ceo"] {
     --space-inset-md: 20px;
     --space-page-gutter: 32px;
     /* ... only the overridden keys */
   }
   [data-persona="it"] {
     --font-family-body: 'JetBrains Mono', ...;
     --space-inset-md: 6px;
     /* ... */
   }
   ```

4. Font shorthand keys (`font.body`, `font.heading-1`, etc.) are documentation hints — the generator does NOT emit them as single CSS variables. Instead it emits the component parts separately (`--font-size-md`, `--font-line-md`, etc.) and pattern docs specify which parts to combine in component CSS.

5. The `_meta`, `_density`, and `note` keys are stripped — not emitted as CSS variables.

6. Compound values containing spaces (font-family strings, box-shadow strings) must be emitted without extra quoting beyond what CSS requires.

## Key naming convention in CSS output

Input JSON path → CSS custom property name:

- Dots become hyphens
- Underscores in JSON keys stay as hyphens in CSS (JSON `line_height` → CSS `line-height` suffix)
- Semantic keys drop category prefix ambiguity: `color.primary` → `--color-primary` (not `--semantic-color-primary`)
- Raw keys are namespaced: `color.gray.900` → `--raw-color-gray-900`

## Brand color placeholder

The accent ramp is placeholder blue (`#2563EB` at 600). When the brand color is decided:
1. Update `raw.json → color.accent.*` with the new ramp
2. All semantic tokens that reference `{color.accent.*}` update automatically
3. No component code changes required

This is the primary reason components must never reference raw hex directly.

## Contrast ratios verified (gray scale on white)

| Token            | Hex     | Ratio  | WCAG AA body |
|------------------|---------|--------|--------------|
| gray.400         | #9CA3AF | 3.05:1 | PASS (WCAG 1.4.11 non-text — `border-input` ops+it) |
| gray.500         | #6B7280 | 4.61:1 | PASS |
| gray.600         | #4B5563 | 6.30:1 | PASS |
| gray.700         | #374151 | 9.02:1 | PASS |
| gray.800         | #1F2937 | 12.63:1 | PASS (AAA) |
| gray.900         | #111827 | 17.28:1 | PASS (AAA) |
| accent.500       | #3B82F6 | 4.56:1 | PASS (just) |
| accent.600       | #2563EB | 4.68:1 | PASS |

Primary semantic pairings:
- `text-1` (#111827) on `surface-1` (#FFFFFF): **17.28:1 AAA**
- `text-2` (#374151) on `surface-1` (#FFFFFF): **9.02:1 AA**
- `text-3` (#6B7280) on `surface-1` (#FFFFFF): **4.61:1 AA** (use only for non-essential labels, not body text)
- `text-on-primary` (#FFFFFF) on `primary` (#2563EB): **6.84:1 AA**
- `text-on-danger` (#FFFFFF) on `danger` (#DC2626): **5.08:1 AA**

Input border semantic pairings (WCAG 1.4.11 non-text contrast, threshold 3:1):
- `border-input` (#9CA3AF, gray.400) on `surface-1` (#FFFFFF): **3.05:1 PASS** — ops + it personas
- `border-input` CEO override (#D1D5DB, gray.300) on `surface-1` (#FFFFFF): **1.87:1 — documented exemption** — CEO persona only; justified by visible label + surrounding chrome context (CTO decision, Growth-8 2026-05-29)
- `border` (#E5E7EB, gray.200) on `surface-1` (#FFFFFF): **1.52:1** — decorative/non-interactive edges only (table dividers, card borders); 1.4.11 does not apply

`text-disabled` (#9CA3AF) on white is intentionally below AA (3.05:1) — disabled state communicates non-interactivity and is exempt per WCAG 1.4.3 exception.
