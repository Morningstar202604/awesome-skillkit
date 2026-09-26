# WCAG 2.2 AA Numeric Checklist

Organized by the four POUR principles: Perceivable, Operable, Understandable,
Robust. Each criterion lists the exact numeric requirement and how to test
manually. Source: W3C WCAG 2.2 Recommendation (W3C Document License).

---

## Table of Contents

- [Perceivable](#perceivable)
- [Operable](#operable)
- [Understandable](#understandable)
- [Robust](#robust)
- [AAA Bonus Numbers (if requested)](#aaa-bonus-numbers-if-requested)

## Perceivable

### 1.1.1 Non-text Content (A)
- **Requirement**: All non-text content has a text alternative that serves the
  equivalent purpose.
- **Test**: Every meaningful image has alt text; decorative images have empty
  alt (`alt=""`); icons have accessible names.

### 1.2.1 Audio-only and Video-only (A)
- **Requirement**: Pre-recorded audio-only and video-only content has
  alternatives (transcript / description).

### 1.2.2 Captions (A)
- **Requirement**: Pre-recorded video has captions.

### 1.2.4 Captions (Live) (AA)
- **Requirement**: Live video has captions.

### 1.2.5 Audio Description (Pre-recorded) (AA)
- **Requirement**: Pre-recorded video has audio description.

### 1.3.1 Info and Relationships (A)
- **Requirement**: Information, structure, and relationships can be
  programmatically determined.
- **Test**: Headings are `h1-h6` (not styled divs); lists are `<ul>/<ol>`;
  form inputs have associated `<label>`; tables use proper semantics.

### 1.3.2 Meaningful Sequence (A)
- **Requirement**: Reading order is preserved in the DOM.

### 1.3.3 Sensory Characteristics (A)
- **Requirement**: Instructions do not rely solely on shape, color, or sound.

### 1.3.4 Orientation (AA)
- **Requirement**: Page works in both portrait and landscape (unless landscape
  is essential).

### 1.3.5 Identify Input Purpose (AA)
- **Requirement**: Input fields that collect user info use `autocomplete`
  attributes (e.g., `name`, `email`, `tel`, `street-address`).

### 1.4.1 Use of Color (A)
- **Requirement**: Color is not the only visual means of conveying
  information.
- **Test**: Error states use icon + text, not just red; links are underlined
  or have a distinct affordance beyond color.

### 1.4.2 Audio Control (A)
- **Requirement**: Auto-playing audio can be paused or stopped.

### 1.4.3 Contrast (Minimum) (AA)
- **Requirement**: Contrast ratio of text vs background:
  - **Normal text**: at least **4.5:1**
  - **Large text** (18pt / 24px regular, or 14pt / 18.66px bold): at least
    **3:1**
  - **Exempt**: inactive UI components, pure decoration, incidental text in
    a photograph, logotypes
- **Test**: Use a contrast checker on foreground/background hex values.

### 1.4.11 Non-text Contrast (AA)
- **Requirement**: Visual information required to identify UI components and
  states has **3:1** contrast against adjacent colors.
- **Applies to**: form field borders, focus indicators, icon strokes, chart
  lines, button outlines.
- **Exempt**: inactive components, decorative elements, logotypes.

### 1.4.12 Text Spacing (AA)
- **Requirement**: Content does not lose information or functionality when
  all of the following are set:
  - Line height: at least **1.5x** font size
  - Paragraph spacing: at least **2x** font size
  - Letter spacing: at least **0.12em**
  - Word spacing: at least **0.16em**
- **Test**: Apply the CSS snippet below and check for clipping/overlap:
  ```css
  * {
    line-height: 1.5 !important;
    margin-bottom: 2em !important;
    letter-spacing: 0.12em !important;
    word-spacing: 0.16em !important;
  }
  ```

### 1.4.10 Reflow (AA)
- **Requirement**: Content can be presented at **320 CSS pixels** width
  without loss of information and without scrolling in two dimensions.
- **Equivalent**: 1280px viewport at 400% zoom.
- **Exception**: content requiring 2D layout (data tables, maps,
  diagrams).
- **Test**: Resize browser to 320px wide; no horizontal scrollbar.

### 1.4.4 Resize Text (AA)
- **Requirement**: Text can be resized to **200%** without loss of content
  or functionality, without assistive technology.

### 1.4.5 Images of Text (AA)
- **Requirement**: Avoid images of text (use real text instead), unless the
  text is part of a logo or cannot be styled otherwise.

---

## Operable

### 2.1.1 Keyboard (A)
- **Requirement**: All functionality is available via keyboard.
- **Test**: Tab through every interactive element; no mouse-only actions.

### 2.1.2 No Keyboard Trap (A)
- **Requirement**: Keyboard focus can never get trapped in a component.
- **Test**: Once focus enters a widget, Tab/Escape/arrows must let you exit.

### 2.4.1 Bypass Blocks (A)
- **Requirement**: Skip-to-content link is available.

### 2.4.2 Page Titled (A)
- **Requirement**: Page has a unique, descriptive `<title>`.

### 2.4.3 Focus Order (A)
- **Requirement**: Focus order preserves meaning and operability.

### 2.4.4 Link Purpose (In Context) (A)
- **Requirement**: Link text makes sense out of context (no "click here").

### 2.4.5 Multiple Ways (AA)
- **Requirement**: More than one way to find a page (nav, search, sitemap).

### 2.4.6 Headings and Labels (AA)
- **Requirement**: Headings and labels describe topic/purpose.

### 2.4.7 Focus Visible (AA)
- **Requirement**: Keyboard focus indicator is visible.

### 2.4.11 Focus Appearance (AA) — *new in WCAG 2.2*
- **Requirement**: When focus indicator is visible:
  - Indicator area is at least a **2 CSS pixel** thick perimeter of the
    focused component
  - Contrast ratio between focused and unfocused states is at least **3:1**
  - The focus indicator is not overlapped by other content
- **Test**: Tab through; check that outline/ring is >=2px and meets 3:1.

### 2.4.12 Focus Not Obscured (Minimum) (AA) — *new in WCAG 2.2*
- **Requirement**: When a component receives focus, it is not entirely hidden
  by author-created content (e.g., sticky headers, banners).

### 2.5.1 Pointer Gestures (A)
- **Requirement**: All functionality using multipoint/path gestures has a
  single-point alternative.

### 2.5.2 Pointer Cancellation (A)
- **Requirement**: Functions triggered by pointer down/up can be aborted or
  undone.

### 2.5.3 Label in Name (A)
- **Requirement**: Accessible name includes the visible label text (e.g.,
  button shows "Search" and `aria-label` contains "Search").

### 2.5.4 Motion Actuation (A)
- **Requirement**: Motion-triggered functions have a button alternative and
  can be disabled.

### 2.5.7 Dragging Movements (AA) — *new in WCAG 2.2*
- **Requirement**: All functions that use dragging can also be done with a
  single pointer (no drag required).

### 2.5.8 Target Size (Minimum) (AA) — *new in WCAG 2.2*
- **Requirement**: Target size for pointer input is at least **24 x 24 CSS
  pixels**.
- **Exceptions**:
  - **Spacing**: undersized targets (under 24px) must be spaced so that a
    24px diameter circle centered on each target does not overlap another
    target
  - **Equivalent**: the function is available via an equivalent control
    elsewhere
  - **Exception**: inline targets within a line of text
- **Test**: Measure the hit area (including padding) of every clickable
  element.

### 3.2.1 On Focus (A)
- **Requirement**: Focus does not cause unexpected context changes.

### 3.2.2 On Input (A)
- **Requirement**: Changing input does not unexpectedly submit or navigate.

### 3.2.3 Consistent Navigation (AA)
- **Requirement**: Navigation components appear in the same order across
  pages.

### 3.2.4 Consistent Identification (AA)
- **Requirement**: Components with same functionality are identified
  consistently.

### 3.2.6 Consistent Help (A) — *new in WCAG 2.2*
- **Requirement**: Help mechanisms (contact link, help button, FAQ) appear
  in a consistent location across pages.

---

## Understandable

### 3.1.1 Language of Page (A)
- **Requirement**: `<html lang="en">` is set.

### 3.1.2 Language of Parts (AA)
- **Requirement**: Foreign language passages have `lang` attribute.

### 3.3.1 Error Identification (A)
- **Requirement**: When an input error is automatically detected, the error
  is described in text.
- **Test**: Submit a form with bad input; the error message must name the
  field and explain what is wrong.

### 3.3.2 Labels or Instructions (A)
- **Requirement**: Input fields have visible labels or instructions.

### 3.3.3 Error Suggestion (AA)
- **Requirement**: Error text includes the suggested correction.

### 3.3.4 Error Prevention (Legal, Financial, Data) (AA)
- **Requirement**: Submissions for legal/financial/data transactions are
  reversible, checked, or confirmed.

### 3.3.7 Redundant Entry (A) — *new in WCAG 2.2*
- **Requirement**: Information already entered in a multi-step process is
  pre-filled or available for selection, not re-entered by the user.

### 3.3.8 Accessible Authentication (Minimum) (AA) — *new in WCAG 2.2*
- **Requirement**: Authentication does not require solving a cognitive
  function test (e.g., remembering a password, answering a security question)
  unless it uses one of: a password, a passkey, or an input of existing
  information that the user already knows (e.g., phone number).
- **Note**: Captcha and memory-based knowledge tests fail this criterion.

---

## Robust

### 4.1.1 Parsing (A)
- **Requirement**: No major markup errors (valid HTML).

### 4.1.2 Name, Role, Value (A)
- **Requirement**: All UI components have programmatically determinable name,
  role, and value; states are updated and communicated to assistive tech.
- **Test**: Every custom widget has correct ARIA role, state attributes
  (`aria-expanded`, `aria-checked`, `aria-selected`).

### 4.1.3 Status Messages (AA)
- **Requirement**: Status messages can be programmatically determined via
  role or properties so they are announced by assistive tech without
  receiving focus (e.g., `role="status"` for form success, `role="alert"`
  for errors).

---

## AAA Bonus Numbers (if requested)

| SC ID | Name | AAA Value |
|-------|------|-----------|
| 1.4.6 | Contrast (Enhanced) | 7:1 normal text; 4.5:1 large text |
| 1.4.8 | Visual Presentation | 200% zoom, no horizontal scroll |
| 2.4.3 | Focus Appearance (Enhanced) | full 2px+ indicator, no exceptions |
| 2.5.5 | Target Size (Enhanced) | 44x44 CSS px (formerly 2.5.5 AAA in 2.1) |
| 3.3.5 | Help | context-sensitive help available |
