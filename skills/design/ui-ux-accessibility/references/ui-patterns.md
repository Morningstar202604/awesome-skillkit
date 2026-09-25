# UI Pattern Selection Guide

Detailed decision guide for common UI layout and interaction patterns. Each
entry lists the pattern, when to choose it, alternatives, and anti-patterns
to avoid.

---

## Overlay Patterns

### Modal Dialog

**Choose when**:
- User must make a focused decision before continuing (confirm delete,
  payment confirmation, login wall)
- Task is short (1-3 steps)
- Interruption is justified by the consequence

**Alternatives**:
- Drawer: if the task is contextual and page background should stay visible
- Toast: if feedback is low-priority and no action needed
- Full page: if task is multi-step or needs a URL

**Anti-patterns**:
- Modal with a long form or multi-step wizard
- Modal that opens automatically on page load (except login/paywall)
- Modal without a clear close button or Escape key

### Drawer / Side Panel

**Choose when**:
- User needs contextual detail or secondary controls while keeping page
  context
- Preview of record details, filters, shopping cart, navigation
- Content is secondary to the main task

**Alternatives**:
- Modal: if the task requires interruption and focus
- Full page: if the drawer content is deep and needs its own URL

**Anti-patterns**:
- Drawer that contains a full task flow (checkout, onboarding)
- Drawer that pushes content around on mobile (use overlay instead)

### Toast / Snackbar

**Choose when**:
- Low-priority feedback: "Saved", "Copied to clipboard", "Settings updated"
- Single action undo (e.g., "Message sent — Undo")
- Auto-dismiss after 4-10 seconds

**Alternatives**:
- Inline alert: for form validation errors
- Modal: for destructive action confirmations

**Anti-patterns**:
- Toast for error messages that block progress
- Toast that requires user action to dismiss (that's a notification, not a toast)

---

## Content Organization

### Tabs

**Choose when**:
- Multiple parallel content sections of roughly equal importance and length
- Users need to switch between views quickly
- Content sections are peers (e.g., "Details | Reviews | Specifications")

**Alternatives**:
- Accordion: if content is sequential prose or FAQ-style
- Scroll-spy / anchor nav: if all content fits on one page and users scroll
  through it

**Anti-patterns**:
- Tabs with more than 7 items (use a dropdown or nested nav)
- Tabs where one panel is much longer than others (unbalanced)
- Hover-activated tabs (keyboard inaccessible)

### Accordion

**Choose when**:
- Sequential content in a long page (FAQ, product description, help center)
- Users typically read one section at a time
- Mobile-first where vertical space is constrained
- Multiple sections can be expanded simultaneously (multi-expand mode for FAQ)

**Alternatives**:
- Tabs: if panels are parallel and equal-weight
- Just show everything: if sections are short (1-2 sentences each)

**Anti-patterns**:
- Accordion for short content (just show it, don't hide it behind a click)
- Accordion where users need to compare across sections simultaneously
- Single-expand accordion for FAQ (users may need multiple answers at once)

### Infinite Scroll

**Choose when**:
- Discovery / browsing context (social media feed, image gallery, news feed)
- No fixed endpoint; users scroll to explore
- Content is homogeneous and consumed sequentially

**Alternatives**:
- Pagination: if users need to jump to a specific page or return to a
  result
- "Load more" button: middle ground — explicit, user-initiated

**Anti-patterns**:
- Infinite scroll for search results (users can't find "page 3 of 12")
- Infinite scroll for checkout or task flows (no way back to a specific item)
- Infinite scroll without scroll-to-top button (lost your place)

### Pagination

**Choose when**:
- Task-oriented browsing: search results, product catalog, data tables
- Users need to know total count ("Page 3 of 47")
- Users need to jump to a specific page or bookmark a result

**Alternatives**:
- Infinite scroll: for social feeds and discovery
- Load more button: for moderate-length lists

**Anti-patterns**:
- Pagination with 100+ pages (use infinite scroll or faceted filters)
- Pagination without showing total count or current position

---

## Form & Input Patterns

### Inline Validation

**Choose when**:
- Form field errors can be detected immediately (email format, required
  field)
- Feedback appears on blur or after typing pauses (300-500ms debounce)

**Anti-patterns**:
- Validating on every keystroke (annoying)
- Error appearing before the user finishes typing

### Multi-step Wizard / Stepper

**Choose when**:
- Long form divided into logical steps (checkout, onboarding, application)
- Each step has a clear focus
- Progress is visible

**Anti-patterns**:
- Stepper for a 3-field form (just show all fields)
- Stepper that doesn't allow going back to edit previous steps

### Autocomplete / Combobox

**Choose when**:
- Long list of options (>20 items)
- User knows roughly what they are looking for (typeahead)

**Anti-patterns**:
- Combobox for 3-5 options (use radio buttons or a select)

---

## Navigation Patterns

### Breadcrumbs

**Choose when**:
- Deep information architecture (>3 levels)
- Users need to know where they are in the hierarchy

**Anti-patterns**:
- Breadcrumbs on flat sites with only 1-2 levels

### Sticky / Fixed Header

**Choose when**:
- Primary navigation must remain accessible while scrolling
- Long pages where users need to navigate away

**Anti-patterns**:
- Sticky headers that take up more than 60px on mobile (steal content space)
- Sticky headers that cover focused content (WCAG 2.4.12 violation)

---

## Feedback Patterns

### Skeleton Loader

**Choose when**:
- Content is loading and you want to show layout
- Perceived performance improvement

**Alternatives**:
- Spinner: for short waits (<1 second)
- Nothing: for very fast loads (<200ms)

**Anti-patterns**:
- Skeleton that looks nothing like the actual content layout
- Skeleton for fast operations (just show the content)

### Empty State

**Choose when**:
- List has no items, search has no results, inbox is empty
- Include a clear call-to-action (e.g., "Create your first project")

**Anti-patterns**:
- Empty state that says "No data" without explanation or next step

---

## Platform-Specific Target Size Rules

| Platform | Minimum Touch Target | Notes |
|----------|---------------------|-------|
| WCAG 2.2 (web) | 24 x 24 CSS px | AA minimum; includes spacing exception |
| Material Design (Android) | 48 x 48 dp | ~9mm physical; icon visual may be 24dp with 12dp padding |
| Apple HIG (iOS) | 44 x 44 pt | Recommended minimum hit area |
| WCAG AAA (enhanced) | 44 x 44 CSS px | Formerly 2.5.5 AAA in WCAG 2.1 |

Note: Material 48dp and Apple 44pt are *recommended* platform guidelines;
WCAG 2.2 AA sets the legal floor at 24 CSS px. When auditing, use the
platform's recommendation as the practical target and WCAG 24px as the hard
minimum.
