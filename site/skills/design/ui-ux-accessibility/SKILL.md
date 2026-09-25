---
name: ui-ux-accessibility
description: >-
  Audit UI designs and code against hard usability, accessibility, and interaction
  rules. Runs a five-pass workflow: scope, Nielsen heuristic review, WCAG 2.2
  numeric audit (contrast ratios, target sizes, focus indicators, reflow, text
  spacing), ARIA/keyboard widget check, and a scored remediation report. Use when
  the user asks for UI review, accessibility audit, WCAG compliance, usability
  heuristic, ARIA fix, contrast check, target-size check, or pattern selection.
  Do NOT use for visual design generation (frontend-design-director owns that),
  component implementation (frontend-component-lab owns that), or backend tasks.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime deps.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-25"
---

# UI/UX & Accessibility Review

Knowledge-reference skill that converts vague design opinions into **hard
number-backed verdicts**. It does not redesign; it audits existing designs,
screenshots, or code against established standards (Nielsen heuristics, WCAG 2.2
AA, ARIA APG, Laws of UX) and returns a scored report with exact remediation
values. Core judgment: **if the rule has a number, cite the number; if it is a
pattern, name the pattern and its correct use-case.**

## Applicability Decision Table

| Sub-mode | Trigger | What You Check |
|----------|---------|-----------------|
| Heuristic review | "is this usable / heuristic eval / UX review" | Nielsen 10 heuristics pass |
| WCAG numeric audit | "accessible / WCAG / ADA / contrast / target size" | WCAG 2.2 AA numeric checklist |
| ARIA/keyboard fix | "screen reader / keyboard nav / ARIA / focus trap" | ARIA widget patterns + keyboard |
| Pattern selection | "modal or drawer / tabs or accordion / scroll or pagination" | UI pattern decision table |
| Full audit | "review this UI / audit this page" | All four passes |

## Input Checklist

| Input | Required | Notes |
|-------|----------|-------|
| Design artifact | yes | screenshot, Figma link, or code (HTML/CSS/JSX) |
| Target platform | yes (ask if missing) | Web desktop / mobile / iOS / Android |
| WCAG target level | no | default AA; AAA only if explicitly requested |
| Scope | no | whole page vs specific component; default whole page |

When inputs are missing, ask all at once:

> Please provide: 1) the design or code to audit; 2) target platform; 3) WCAG
> level (default AA); 4) scope (whole page or specific component).

## Pre-flight Checks

```bash
test -f references/wcag-2.2-checklist.md && \
test -f references/aria-patterns.md && \
test -f references/ui-patterns.md && echo OK
```

Expected output `OK`. If missing, continue with built-in tables and note
degraded mode in the report.

## Workflow

Five-step audit pipeline. Each step produces a structured finding list.

| Step | Action | Output | If Fails |
|------|--------|--------|----------|
| 1 scope | identify platform, level, components | scope table | no artifact -> stop and ask |
| 2 heuristic pass | Nielsen 10 heuristics | list of heuristic violations | none -> note "no major heuristic issues" |
| 3 WCAG numeric audit | check every AA number | table: SC ID / value / actual / pass-fail | tool not available -> manual estimate with caveat |
| 4 ARIA/keyboard check | widget roles + key combos | list of missing roles / dead keys | no code -> flag as "needs code review" |
| 5 report | score + remediate | prioritized findings table | n/a |

### Step 2: Nielsen Heuristics (compact)

| # | Heuristic | What to Check | Common Violation |
|---|-----------|---------------|-------------------|
| 1 | Visibility of system status | feedback within reasonable time after every action | silent submit, no loading spinner |
| 2 | Match between system and real world | user language, natural order, no jargon | backend field labels exposed to users |
| 3 | User control and freedom | undo/redo, emergency exit, cancel | no way out of a modal except success |
| 4 | Consistency and standards | same words/actions mean same thing everywhere | "Save" vs "Submit" for same action |
| 5 | Error prevention | prevent errors before they happen | destructive action without confirmation |
| 6 | Recognition rather than recall | options visible, don't make users remember | hidden commands behind unclear icons |
| 7 | Flexibility and efficiency of use | accelerators, shortcuts for power users | no keyboard shortcuts in data-dense UI |
| 8 | Aesthetic and minimalist design | no irrelevant info, strip clutter | every page full of marketing banners |
| 9 | Recognize/diagnose/recover errors | plain-language error messages with solution | "Error 500" without explanation |
| 10 | Help and documentation | searchable, task-focused, concrete steps | no help at all in complex flows |

### Step 3: WCAG 2.2 Numeric Audit (top AA numbers)

Full table in `references/wcag-2.2-checklist.md`. Quick numeric floor:

| SC ID | Name | Hard Number |
|-------|------|-------------|
| 1.4.3 | Contrast Minimum | 4.5:1 normal text; 3:1 large text (>=18pt/24px regular or >=14pt/18.66px bold) |
| 1.4.11 | Non-text Contrast | 3:1 for UI components / meaningful graphics |
| 1.4.12 | Text Spacing | line-height 1.5x, para spacing 2x, letter-spacing 0.12em, word-spacing 0.16em |
| 1.4.10 | Reflow | 320 CSS px width, no horizontal scroll (equals 1280px at 400% zoom) |
| 2.4.11 | Focus Appearance | 2px minimum perimeter, 3:1 contrast focused vs unfocused |
| 2.5.5 | Target Size Minimum | 24x24 CSS px minimum per pointer target |

### Step 4: ARIA / Keyboard Widget Check

Detailed patterns in `references/aria-patterns.md`. Core rule: **Tab/Shift+Tab
moves between components; arrow keys move within a component; Escape closes
overlays; Home/End jump to first/last in a set.**

| Widget | Required Role | Must-have Keys | Common Mistake |
|--------|---------------|----------------|----------------|
| Tabs | tablist / tab / tabpanel | Left/Right, Home, End, Enter/Space | arrows don't work, only Tab |
| Modal dialog | dialog, aria-modal=true | Tab trap, Escape closes | focus leaves dialog to background |
| Combobox | combobox, aria-expanded, aria-controls | Down, Up, Escape, typeahead | no aria-activedescendant |
| Switch | switch, aria-checked | Space toggles | using checkbox semantics for toggle |
| Menu | menu / menuitem | Down/Up, Home/End, Escape | mouse-only, no keyboard |

### Step 5: Report

Output a table:

| Priority | SC / Heuristic | Finding | Actual | Required | Fix |
|----------|---------------|---------|--------|----------|-----|
| P0 | 1.4.3 contrast | body gray on white | 2.1:1 | 4.5:1 | darken text to #444 |
| P1 | 2.5.5 target size | close icon | 16x16px | 24x24px | add 4px padding each side |

Priority: P0 = blocks accessibility, P1 = major usability gap, P2 = polish.

## Laws of UX Quick Reference

| Law | Principle | UI Application |
|-----|-----------|----------------|
| Fitts's Law | acquire time = f(distance, size) | larger, closer targets = faster; primary CTA big, near thumb |
| Hick's Law | decision time = f(choices) | reduce visible options; progressive disclosure |
| Jacob's Law | users expect your UI to work like others' | follow platform conventions, don't innovate on patterns |
| Miller's Law | working memory = 7 +/- 2 items | limit nav to 5-7 items; chunk content |
| Parkinson's Law | work expands to fill time | add visible deadlines / progress bars |
| Postel's Law | strict output, lenient input | accept flexible input, normalize behind scenes |
| Proximity | nearby items perceived as related | group labels with their inputs; separate unrelated groups |
| Similarity | look-alike items perceived as group | same action buttons same color/style |
| Tesler's Law | complexity is conserved; choose who bears it | shift complexity from user to system |
| Von Restorff | the odd one out is remembered | make primary CTA visually distinct |
| Zeigarnik | unfinished tasks are remembered | show progress bars / incomplete profile hints |
| Aesthetic-Usability | beautiful UIs tolerate more errors | polish first impressions; users forgive minor issues |
| Doherty Threshold | system response <400ms keeps flow | show loading state under 100ms, full result <400ms |
| Peak-End Rule | judge by peak + end, not average | make key moment memorable; end on confirmation |

## UI Pattern Selection Guide

Full guide in `references/ui-patterns.md`. Decision table:

| Pattern | Choose When | Alternative | Anti-pattern |
|---------|-------------|-------------|--------------|
| Modal dialog | focused decision, must interrupt | Drawer | modal for multi-step long flow |
| Drawer / side panel | contextual detail, keep page context | Full page | drawer for task completion |
| Tabs | parallel equal-weight panels | Accordion | tabs for >7 items or long prose |
| Accordion | sequential prose, FAQ style | Tabs | accordion for short content (just show it) |
| Infinite scroll | discovery / browsing / feed | Pagination | infinite scroll for search results / checkout |
| Pagination | task-oriented, search results, known count | Infinite scroll | pagination for social feed (kills momentum) |
| Toast / snackbar | low-priority feedback | Inline alert | toast for destructive action confirmation |

## Failure Remediation Table

| Symptom | Cause | Action |
|---------|-------|--------|
| No artifact provided | user asks "is my UI good?" without link | Stop; ask for screenshot/code + platform + level |
| Contrast ratio ambiguous | screenshot compression distorts colors | Use color picker on raw hex values; flag estimate |
| Target size looks small | padding not counted in hit area | Measure interactive area (not visual icon), include padding |
| Keyboard nav can't test | only screenshot, no code | Mark as "needs code verification"; do not guess pass/fail |
| Too many findings | overwhelming the user | Cap at top 10 P0/P1; list rest as appendix |
| AAA requested but AA baseline | user says "make it perfect" | Run AA fully, add AAA notes separately; don't conflate |
| Mobile vs desktop mismatch | target platform unclear | Ask; mobile uses 48dp touch (Material) vs 24px web (WCAG) |

## Quality / Delivery Checklist

- [ ] Every numeric finding cites the exact SC ID or standard name
- [ ] Contrast ratios are actual measured values, not guesses
- [ ] Target sizes include padding (hit area, not visual bounds)
- [ ] Keyboard findings name the exact key that is broken
- [ ] Pattern recommendations state when to use and when NOT to use
- [ ] Report is prioritized P0/P1/P2, not a flat list
- [ ] No vague "looks bad" — every finding has a number or pattern name

## Chain Position

- Upstream: receives designs from `design-brief-interpreter`
- Downstream: hands off to `frontend-design-director` for visual redesign,
  `frontend-component-lab` for accessible component implementation

## References

- `references/wcag-2.2-checklist.md` — full WCAG 2.2 AA checklist by POUR
  principle, each with SC ID, numeric requirement, and test method
- `references/aria-patterns.md` — detailed ARIA widget patterns: roles,
  required attributes, full keyboard interaction tables
- `references/ui-patterns.md` — UI pattern selection guide with use-cases,
  alternatives, and anti-patterns
- `references/sources-and-licenses.md` — all source URLs, license types,
  and attribution for extracted facts
