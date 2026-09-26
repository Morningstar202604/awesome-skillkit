# ARIA Widget Patterns — Detailed Reference

Source: W3C ARIA Authoring Practices Guide (APG). Each widget lists the
required roles, attributes, and full keyboard interaction contract.

---

## Table of Contents

- [Global Keyboard Conventions](#global-keyboard-conventions)
- [Tabs](#tabs)
- [Modal Dialog](#modal-dialog)
- [Combobox](#combobox)
- [Menu / Menubar](#menu--menubar)
- [Switch (Toggle)](#switch-toggle)
- [Listbox](#listbox)
- [Treegrid](#treegrid)
- [Tooltip](#tooltip)
- [Alert / Status](#alert--status)
- [Roving tabindex Pattern](#roving-tabindex-pattern)

## Global Keyboard Conventions

- **Tab / Shift+Tab**: move focus between components (the tab ring)
- **Arrow keys**: move focus within a composite widget
- **Home / End**: jump to first / last item in a set
- **Enter / Space**: activate / select / toggle
- **Escape**: close overlay, cancel, return to trigger
- **PageUp / PageDown**: scroll or move by page (when applicable)

Rule: once focus enters a composite widget (tabs, menu, grid, tree, listbox),
arrow keys handle internal navigation; Tab exits the widget entirely.

---

## Tabs

**Roles**: `tablist` (container), `tab` (each tab), `tabpanel` (content)

**Required attributes**:
- `tab`: `aria-selected="true|false"`, `aria-controls` points to tabpanel
- `tabpanel`: `aria-labelledby` points to the tab that controls it
- Only one tab has `aria-selected="true"`

**Keyboard interaction**:

| Key | Action |
|-----|--------|
| Tab | moves focus to active tab; next Tab goes to tabpanel |
| Right Arrow | activates next tab; wraps to first at end |
| Left Arrow | activates previous tab; wraps to last at start |
| Home | activates first tab |
| End | activates last tab |
| Enter / Space | activates tab (if not already activated on focus) |

**Common mistakes**:
- Tabs that only respond to mouse clicks, no arrow keys
- Multiple tabs marked `aria-selected="true"`
- Tabpanel not associated via `aria-labelledby`
- Focus never moves to tabpanel (screen reader users stuck)

---

## Modal Dialog

**Roles**: `dialog` (or `alertdialog` for urgent interrupts)

**Required attributes**:
- `aria-modal="true"`
- `aria-labelledby` or `aria-label` (accessible name)

**Behavior**:
- Focus is trapped inside the dialog when open
- Focus returns to the trigger element when closed
- Background content is inert / `aria-hidden="true"`

**Keyboard interaction**:

| Key | Action |
|-----|--------|
| Tab | moves to next tabbable element inside dialog |
| Shift+Tab | moves to previous tabbable element inside dialog |
| (wraps) | Tab from last element goes to first, and vice versa |
| Escape | closes the dialog |

**Common mistakes**:
- Focus escapes to background behind the modal
- No Escape to close
- No `aria-modal` or `role="dialog"`
- Focus not returned to trigger on close
- Long multi-step flows inside a modal (should be a full page)

---

## Combobox

**Roles**: `combobox` (the input), with a listbox or tree popup

**Required attributes**:
- `aria-expanded="true|false"` on the combobox input
- `aria-controls` points to the popup element
- `aria-autocomplete="list"` or `"both"` or `"inline"`
- `aria-activedescendant` used when focus stays on the input and active
  option is indicated via ID reference

**Keyboard interaction**:

| Key | Action |
|-----|--------|
| Down Arrow | opens popup, moves to next option |
| Up Arrow | moves to previous option |
| Alt+Down Arrow | optional: opens popup |
| Escape | closes popup |
| Enter | selects active option and closes |
| Tab | commits selection and closes |
| Type characters | typeahead filters / selects matching option |
| Home / End | first / last option |

**Common mistakes**:
- No `aria-expanded` state
- `aria-activedescendant` missing so screen readers don't announce selection
- Closing on Escape but keeping the typed text as uncommitted

---

## Menu / Menubar

**Roles**: `menu` (container), `menuitem`, `menuitemcheckbox`,
`menuitemradio`

**Keyboard interaction**:

| Key | Action |
|-----|--------|
| Down Arrow | next menu item |
| Up Arrow | previous menu item |
| Right Arrow | opens submenu / moves to next top-level menu (menubar) |
| Left Arrow | closes submenu / moves to previous top-level menu |
| Home | first item |
| End | last item |
| Enter | activates item |
| Escape | closes menu, returns focus to trigger |

**Common mistakes**:
- Menu items are divs without `menuitem` role
- No arrow key navigation (only mouse hover)
- Submenus that don't close on Escape

---

## Switch (Toggle)

**Roles**: `switch`

**Required attributes**: `aria-checked="true|false"`

**Keyboard interaction**:

| Key | Action |
|-----|--------|
| Space | toggles the switch |
| Enter | optional: toggles |

**Common mistakes**:
- Using `role="checkbox"` for a binary on/off toggle
- Not updating `aria-checked` when toggled

---

## Listbox

**Roles**: `listbox` (container), `option` (each item)

**Required attributes**:
- `aria-selected="true"` on the selected option
- `aria-label` or `aria-labelledby` on listbox

**Keyboard interaction**:

| Key | Action |
|-----|--------|
| Down Arrow | next option |
| Up Arrow | previous option |
| Home | first option |
| End | last option |
| Type characters | typeahead to matching option |

---

## Treegrid

**Roles**: `treegrid` (container), `row` (each row), `gridcell` (cells),
`rowheader` optionally

**Required attributes**:
- `aria-expanded="true|false"` on expandable rows
- `aria-selected` on selected rows (if multi-select allowed)

**Keyboard interaction**:

| Key | Action |
|-----|--------|
| Down Arrow | next row |
| Up Arrow | previous row |
| Right Arrow | expands collapsed row / moves to next cell in row |
| Left Arrow | collapses expanded row / moves to previous cell |
| Home | first row |
| End | last row |
| PageUp / PageDown | scroll by page |

---

## Tooltip

**Roles**: `tooltip`

**Required behavior**:
- Triggered on focus or hover
- Tooltip content is associated via `aria-describedby` on the trigger
- Dismisses on blur, Escape, or mouse leave

**Common mistakes**:
- Tooltip that only shows on hover, never on keyboard focus
- No `role="tooltip"` so screen readers don't announce it

---

## Alert / Status

**Roles**: `alert` (important, time-sensitive), `status` (non-important
feedback)

**Behavior**:
- `role="alert"`: live region, interrupts, `aria-live="assertive"`
- `role="status"`: live region, polite, `aria-live="polite"`
- Focus does NOT move to the alert; it is announced by screen readers

**Common mistakes**:
- Using a visible alert div without `role="alert"` so screen readers miss it
- Putting focus on the alert and trapping keyboard there

---

## Roving tabindex Pattern

Used in composite widgets (tabs, menubar, listbox, treegrid, radiogroup):
- Only the currently active item has `tabindex="0"`
- All other items have `tabindex="-1"`
- Arrow keys move active state and update `tabindex`
- This way Tab enters the widget once, arrow keys move within, Tab exits
