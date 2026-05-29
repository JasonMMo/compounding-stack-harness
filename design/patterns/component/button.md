# Button — Visual Standard

Applies to: vanilla-htmx adapter (primary target), react adapter (same spec).
Wire contract operations that trigger buttons: entity.create, entity.update, entity.delete, auth.login, auth.logout.

## Variants

```
[variant]     [usage]                            [semantic tokens]
primary       Main action (Save, Login, Create)  bg: color.primary / text: color.text-on-primary
secondary     Secondary action (Cancel, Back)    bg: color.surface-1 / border: color.border-strong / text: color.text-2
danger        Destructive action (Delete)        bg: color.danger / text: color.text-on-danger
ghost         Tertiary / icon-only               bg: transparent / text: color.text-2
```

## States per variant (primary shown, others follow same pattern)

```
State        Background              Border               Text               Shadow
─────────────────────────────────────────────────────────────────────────────────────
default      color.primary           none                 text-on-primary    shadow.xs
hover        color.primary-hover     none                 text-on-primary    shadow.sm
focus        color.primary           2px color.border-focus (outline, not border)   shadow.focus-ring
active       color.primary-active    none                 text-on-primary    none
disabled     color.surface-3         color.border         text-disabled      none
loading      color.primary (50% op)  none                 text-on-primary    none
```

## Sizes

```
Size   Height  Padding-x    Font token       Radius
sm     28px    space.inset-sm   font.size-sm     radius.control
md     36px    space.inset-md   font.size-md     radius.control   ← default
lg     44px    space.inset-lg   font.size-lg     radius.control
```

Minimum touch target 44x44px (KWCAG 2.4, WCAG 2.5.5). Use lg or pad sm/md to reach 44px total hit area.

## ASCII mock

```
┌─────────────────────────────────────────────────┐
│  [PRIMARY]   [ Secondary ]   [!Danger]   Ghost  │
│                                                  │
│  ┌───────────────┐  ┌───────────────┐           │
│  │  Save Record  │  │    Cancel     │           │
│  └───────────────┘  └───────────────┘           │
│  ▲ bg: primary      ▲ bg: white                 │
│    text: white        border: gray.300           │
│                       text: gray.700             │
└─────────────────────────────────────────────────┘
```

## Tokens used

```
background:       var(--color-primary)
color:            var(--color-text-on-primary)
padding:          var(--space-inset-sm) var(--space-inset-md)
border-radius:    var(--radius-control)
font-size:        var(--font-size-md)
font-weight:      var(--font-weight-label)
font-family:      var(--font-family-body)
box-shadow:       var(--shadow-xs)
transition:       var(--motion-transition-control)
```

Focus state (ALL variants — keyboard and pointer):
```
outline:          2px solid var(--color-border-focus)
outline-offset:   2px
box-shadow:       var(--shadow-focus-ring)
```

## a11y requirements

- `type="button"` on all non-submit buttons (prevents accidental form submission).
- `type="submit"` on the primary action inside a `<form>`.
- Disabled via `disabled` attribute (not `aria-disabled` alone) so it is removed from tab order.
- Loading state: `aria-busy="true"` + spinner with `aria-label="Loading"` or visually hidden text.
- Icon-only buttons: `aria-label` required. Icon is `aria-hidden="true"`.
- Minimum contrast: primary and danger variants verified at 4.5:1+. See README.md contrast table.
- Focus ring must be visible in both light mode and any high-contrast OS mode. Use `outline`, not `box-shadow` alone (box-shadow is suppressed in Windows High Contrast Mode).
- Delete/danger actions: require a confirmation step before final action (two-step confirm — per KWCAG 3.3.4 and standard UX practice).
