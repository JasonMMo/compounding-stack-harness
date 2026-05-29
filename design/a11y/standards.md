# Accessibility Standards — WCAG AA + KWCAG

Version: 1.0.0 (Growth-8, 2026-05-29)
Scope: All 14 baseline domain CRUD screens + auth + status health screen.
Minimum bar: WCAG 2.1 AA + KWCAG 2.1 (한국 웹 콘텐츠 접근성 지침 2.1).

KWCAG is a superset of WCAG 2.1 AA in most areas. Compliance with KWCAG implies WCAG 2.1 AA. Items marked [KR] are KWCAG additions or stricter than WCAG baseline.

---

## 1. Perceivable

### 1.1 Text alternatives
- [ ] All images have `alt` text. Decorative images: `alt=""`.
- [ ] Status icons (health dot, badge icon) have adjacent visible text or `aria-label`. Color alone is not sufficient.
- [ ] File upload preview shows filename as text (not icon only).

### 1.2 Time-based media
- [ ] No video/audio in baseline CRUD screens. N/A for M1 scope.

### 1.3 Adaptable
- [ ] Form labels programmatically associated via `<label for>` or `aria-labelledby`.
- [ ] Table headers use `<th scope="col|row">`.
- [ ] Reading and focus order matches visual order. No CSS-only reordering that breaks logical sequence.
- [ ] Required fields: `aria-required="true"` on input, `*` in label.
- [ ] Error messages: `aria-describedby` on input pointing to error element.
- [KR] Heading hierarchy: h1 → h2 → h3 only, no skips. Page title is always h1.

### 1.4 Distinguishable
- [ ] Body text contrast ≥ 4.5:1. See design/tokens/README.md contrast table.
  - `text-1` (#111827) on `surface-1` (#FFFFFF): 17.28:1 PASS
  - `text-2` (#374151) on `surface-1` (#FFFFFF): 9.02:1 PASS
  - `text-3` (#6B7280) on `surface-1` (#FFFFFF): 4.61:1 PASS (non-essential labels)
- [ ] Large text (18px normal / 14px bold) contrast ≥ 3:1.
- [ ] UI components (input borders, button borders) contrast ≥ 3:1 against adjacent background.
  - `border-input` (#9CA3AF, gray.400) on `surface-1` (#FFFFFF): 3.05:1 — PASS (ops + it personas).
  - `border` (#E5E7EB, gray.200) on `surface-1` (#FFFFFF): 1.52:1 — `border` is for decorative/non-interactive edges only (table dividers, card borders). WCAG 1.4.11 does not apply to non-interactive chrome.
  - **CEO persona exemption (documented):** CEO persona overrides `border-input` to gray.300 (#D1D5DB, 1.87:1 vs surface-1). This is a documented WCAG 1.4.11 exemption — justified by CEO low-density layout where every input is accompanied by a visible label above and surrounding chrome that provides shape context. ops and it personas use `border-input` at gray.400 (3.05:1) and remain fully compliant. Decision: CTO, Growth-8 (2026-05-29).
- [ ] Focus indicator: visible at ≥ 3:1 contrast against adjacent background. `shadow.focus-ring` + `outline: 2px solid border-focus` — PASS.
- [ ] Text does not overflow or truncate when browser font size increased to 200%.
- [ ] No horizontal scroll at 320px viewport width (single column responsive layout).
- [KR] Color is never the sole means of conveying information (status, error, required).

---

## 2. Operable

### 2.1 Keyboard accessible
- [ ] All interactive elements reachable by Tab key.
- [ ] No keyboard trap: pressing Escape closes modal/dropdown and returns focus to trigger.
- [ ] Modal: focus locked inside while open. Returns to trigger element on close.
- [ ] Dropdown/select: arrow keys navigate options. Enter selects. Escape closes.
- [ ] Table sort: header buttons activated by Enter/Space.
- [ ] Table row action buttons: reachable by Tab within row.
- [ ] Pagination: each page button is focusable.
- [ ] Skip navigation link: first focusable element on each page, visible on focus. Jumps to `<main>`.
- [KR] All functions operable by keyboard alone (no mouse-only interactions).

### 2.2 Enough time
- [ ] No auto-refresh or auto-advance in M1 CRUD screens.
- [ ] Session timeout: warn user 2 minutes before expiry with dismissible dialog offering extend option. (auth.login / session management — implementation note for backend adapter.)
- [KR] Session timeout warning is keyboard accessible and screen-reader announced.

### 2.3 Seizures
- [ ] No content flashes more than 3 times per second. Motion transitions (150ms–250ms) are below threshold.

### 2.4 Navigable
- [ ] Page `<title>` describes current page: "{Entity Type} List — {App Name}", "{Entity Type} Detail — {App Name}", etc.
- [ ] Skip to main content link.
- [ ] Focus visible at all times (not removed by CSS).
- [ ] Link purpose clear from link text alone or with context. Avoid "click here" or "more".
- [ ] Table column sort direction communicated in header: `aria-sort` attribute.
- [KR] Consistent navigation: sidebar / top nav appears in same location and order on every page.
- [KR] Multiple ways to find content: sidebar navigation + search input on list pages.

### 2.5 Input modalities
- [ ] All actions performable by single pointer (no complex gestures).
- [ ] Minimum touch target: 44x44px. See button.md and table.md action buttons.
- [KR] Touch target minimum strictly enforced for mobile breakpoint (ops persona may use tablet).

---

## 3. Understandable

### 3.1 Readable
- [ ] `<html lang="ko">` for Korean deployments, `lang="en"` for English. Set at profile level.
- [ ] Error messages in user's language, specific about what went wrong and how to fix it.

### 3.2 Predictable
- [ ] No context changes on focus (no auto-submit, no navigation on input focus).
- [ ] No context changes on input (no form submission on select change without warning).
- [ ] Consistent identification: same component looks and behaves the same across all 14 domains.

### 3.3 Input assistance
- [ ] Error identification: field in error state + error message below field + error summary at top of form on submit failure.
- [ ] Labels and instructions: visible before input (not only on focus/hover).
- [ ] Error suggestion: if error type is known, suggest correction ("Must be at least 8 characters").
- [ ] Error prevention for legal / financial / data-loss operations: review step before final submit. Delete action requires two-step confirmation.
- [KR] Form submit errors: focus moves to first error field or error summary.
- [KR] Required fields identified before form submission (not only after failure).

---

## 4. Robust

### 4.1 Compatible
- [ ] Valid HTML: no duplicate IDs, properly nested elements.
- [ ] All custom interactive widgets have ARIA role, name, and state.
- [ ] `aria-live="polite"` region for status messages (save success, load complete, error summary).
- [ ] `role="dialog"` on modals with `aria-modal="true"` and `aria-labelledby` pointing to dialog title.
- [ ] `role="alert"` for urgent messages (session expiry warning, delete confirmation).
- [ ] Test with: screen reader (NVDA + Chrome on Windows, VoiceOver + Safari on macOS/iOS).
- [KR] Test with 한국어 VoiceOver / NVDA Korean TTS.

---

## 5. Checklist by screen type (14 baseline domains)

The 14 baseline domain CRUD screens all share the same screen types. Check all items above per screen type:

### List screen (entity.list)
- Specific items: 1.3 table headers, 2.1 sort keyboard, 2.4 page title, 3.2 consistent.
- Status column: color + text/icon (1.4).
- Empty state: not empty of ARIA content.

### Detail screen (entity.read)
- Specific items: 1.3 field labels, 2.4 breadcrumb navigation, 3.1 language.
- IT persona shows raw IDs and timestamps — these must be in `<code>` elements.

### Create / Edit form screen (entity.create / entity.update)
- Specific items: 1.3 all label associations, 2.1 keyboard, 2.5 touch target, 3.3 all.
- Required field markers + aria-required.
- Form action bar accessible by keyboard.

### Delete confirmation (entity.delete trigger)
- Modal: focus lock, role="dialog", aria-modal, aria-labelledby.
- Two-step: confirm button text is specific: "Delete [Entity Name]", not just "Delete".
- Cancel returns focus to Delete button in table row.

### Auth screens (auth.login, auth.logout)
- autocomplete attributes.
- Password field: toggle visibility button with aria-label.
- Login error: general message only (do not distinguish "user not found" from "wrong password" — security).

### Status health screen (status.health)
- Status indicators: color + text + icon all three.
- `aria-live` region auto-updates when status changes.
- IT persona primary landing — must load fast and be screen-reader scannable quickly.

---

## 6. Testing protocol

| Tool | Scope | When |
|---|---|---|
| axe DevTools (browser ext) | Automated scan all screens | Before each M1 screen PR |
| NVDA + Chrome | Screen reader manual | Once per screen type |
| Keyboard-only navigation | All interactive elements | Per screen before merge |
| Color contrast analyser | All text/background pairs | Token change only |
| 200% browser zoom | No overflow, no scroll | Per screen |
| 320px viewport | Responsive single column | Per screen |

KWCAG compliance report: generate once at M1 demo milestone, file in `design-reports/2026-M1-kwcag.md`.

---

## 7. Escalation triggers

Report to CTO + CEO immediately if:
- KWCAG compliance requires a paid screen reader compatibility library (cost gate).
- A wire-contract field is needed for a11y metadata (e.g., `aria-label` content served from API) — this is a contract change (CTO territory).
- A frontend adapter cannot implement keyboard navigation for a pattern (adapter compliance issue).
