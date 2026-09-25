---
name: design-system-foundations
description: >-
  Hard-number reference for design system foundations: typography scales, color
  contrast values, 8pt spacing tokens, radius/shadow elevation, motion duration
  and easing curves, responsive breakpoints, and z-index layering. Use when the
  user asks to build or audit a design system, pick a type scale, define color
  tokens, set spacing units, spec micro-interaction motion, choose responsive
  breakpoints, or establish design token naming. Do NOT use for visual design
  direction or brand personality (frontend-design-director owns that), component
  implementation, or layout QA. Trigger words: design system, typography scale,
  color palette, spacing system, design tokens, UI spacing, responsive breakpoints,
  type scale, color contrast, motion spec, box shadow elevation.
license: Apache-2.0
compatibility: Pure prompt-based; no runtime deps.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: reference
  tier: standard
  verified-date: "2026-09-25"
---

# Design System Foundations

Numeric, decision-table reference for the foundational tokens every UI needs:
type scale, color contrast and palette structure, spacing on an 8pt grid, radius
and shadow elevation, motion duration and easing, responsive breakpoints, and
z-index layering. Every value is a hard number from a published design system
(Material Design, Tailwind, Bootstrap, WCAG, Apple HIG) — no vague aesthetic
advice. When in doubt, prefer the table over intuition.

## Applicability Decision Table

| User Need | Use This Skill | Route Elsewhere |
|---|---|---|
| Pick a modular type scale ratio and generate px sizes | Yes — typography quick reference | font pairing for brand voice -> frontend-design-director |
| Build a color palette with accessible contrast ratios | Yes — color quick reference | brand mood / personality -> frontend-design-director |
| Define spacing tokens on an 8pt grid | Yes — spacing quick reference | component padding decisions -> frontend-component-lab |
| Specify box shadow elevation and border radius | Yes — elevation quick reference | custom shadow art direction -> frontend-design-director |
| Set motion duration and easing curves | Yes — motion quick reference | choreographed page-load moments -> frontend-design-director |
| Choose responsive breakpoints and navigation transitions | Yes — breakpoints quick reference | actual grid implementation -> layout-spec-auditor |
| Establish design token hierarchy and naming | Yes — tokens reference | code-level token implementation -> frontend-component-lab |
| Full design system from scratch | Yes — all sections, in order | — |

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Scope | yes | which area: typography / color / spacing / motion / breakpoints / full system |
| Platform | yes | web desktop / mobile / both — determines breakpoint set and type base |
| Base font size | no | default 16px; type scale tables use 16px base unless stated |
| Existing framework | no | Tailwind / Bootstrap / Material — match their token names when specified |
| Dark mode needed | no | yes / no — affects color token count |

When inputs are missing, assume: web, 16px base, no framework, dark mode optional.
Do not block on missing inputs — defaults are standard and documented.

## Pre-flight Checks

Pure prompt reference skill — no runtime dependencies. Only self-check:

```bash
test -d references && echo OK
```

Expected output `OK`. If missing, continue with the inline quick-reference tables
below; full tables in references/ are supplementary depth.

## Workflow

Five-step pipeline. Each step produces a token table; carry tokens forward.

| Step | Action | Output | If Fails |
|---|---|---|---|
| 1 audit current | list every hard-coded px/rem/hex value in current UI | audit table of mismatched values | no existing UI -> skip to step 2 |
| 2 choose scale | pick type ratio, color palette shape, spacing base, motion duration tier | one decision per category, with rationale | pick defaults: 1.25 type, 8pt spacing, 200-300ms motion |
| 3 generate tokens | expand scale into full token table (12 steps typography, 9 steps spacing, 5 elevation levels) | token table ready for CSS variables | numbers look wrong -> recompute from ratio in references/typography-scale.md |
| 4 apply | map tokens to components: button padding, card radius, modal shadow, nav breakpoint | component-to-token mapping table | component needs a value outside the scale -> add a new step, do not invent a one-off |
| 5 verify | contrast >= 4.5:1, spacing all multiples of 4/8, motion respects prefers-reduced-motion, breakpoints match chosen framework | pass/fail checklist | any fail -> return to step 3 and regenerate affected tokens |

## Typography Quick Reference

### Modular type scale (16px base)

| Step | 1.25 Major Third | 1.333 Perfect Fourth | 1.414 Augmented Fourth | 1.5 Perfect Fifth | 1.618 Golden Ratio |
|---|---|---|---|---|---|
| display | 71.53px | 89.76px | 118.17px | 121.50px | 168.27px |
| h1 | 57.22px | 67.34px | 83.55px | 81.00px | 104.00px |
| h2 | 45.78px | 50.52px | 59.08px | 54.00px | 64.28px |
| h3 | 36.62px | 37.90px | 41.79px | 36.00px | 39.73px |
| h4 | 29.30px | 28.43px | 29.55px | 24.00px | 24.56px |
| h5 | 23.44px | 21.33px | 20.88px | 18.00px | 15.18px |
| h6 | 18.75px | 16.00px | 14.76px | 12.00px | 9.38px |
| body-lg | 20.00px | 20.00px | 20.00px | 20.00px | 20.00px |
| body | 16.00px | 16.00px | 16.00px | 16.00px | 16.00px |
| body-sm | 12.80px | 12.00px | 11.31px | 10.67px | 9.89px |
| caption | 10.24px | 9.00px | 8.00px | 8.00px | 6.11px |

Choose: 1.25 for most UI (clear, restrained). 1.333 for editorial/marketing. 1.5+
only when hierarchy is dramatic and steps are few.

### Line height and letter spacing

| Element | Line Height | Letter Spacing |
|---|---|---|
| Display / hero | 1.0–1.1 | -0.03em to -0.02em |
| H1–H2 | 1.1–1.2 | -0.02em |
| H3–H6 | 1.2–1.3 | -0.01em to 0 |
| Body | 1.4–1.6 (default 1.5) | 0 |
| Small text / caption | 1.5–1.7 | 0.01em |
| All-caps label | 1.3–1.4 | +0.05em to +0.1em |
| Long-form reading | 1.6–1.75 | 0 |

### Line length (measure)

| Metric | Value |
|---|---|
| Minimum acceptable | 45 characters per line |
| Ideal | 66 characters per line |
| Maximum acceptable | 75 characters per line |
| CSS target | `max-width: 65ch` |
| Paragraph spacing | 0.75em–1.5em (use margin-bottom) |

Full tables in [references/typography-scale.md](references/typography-scale.md).

## Color System Quick Reference

### Contrast ratios (WCAG 2.1 AA)

| Text Type | Minimum Ratio | Notes |
|---|---|---|
| Normal text (< 18pt / 14pt bold) | 4.5:1 | WCAG AA |
| Large text (>= 18pt regular / >= 14pt bold) | 3:1 | WCAG AA |
| Normal text enhanced | 7:1 | WCAG AAA |
| UI components / graphics | 3:1 | non-text contrast |
| Disabled states | no requirement | do not rely on them for meaning |

### 60-30-10 color distribution

| Role | Share | Use For |
|---|---|---|
| Dominant (neutral) | 60% | backgrounds, large surfaces |
| Secondary (brand/structure) | 30% | cards, headers, secondary UI |
| Accent (action) | 10% | buttons, links, focus states, CTAs |

### Dark mode conversion rules

| Token | Light Mode | Dark Mode |
|---|---|---|
| Background / surface | 90–98% lightness | 5–20% lightness |
| Body text | 5–15% lightness | 85–95% lightness |
| Primary accent | 45–55% lightness | 60–70% lightness (desaturated) |
| Elevation overlay | none | light surface tint at 5% per elevation step |
| Border | 10–20% black | 20–30% white |

Do NOT simply invert colors — desaturate accents on dark surfaces and lift
surface lightness with elevation.

Full tables in [references/color-system.md](references/color-system.md).

## Spacing & Layout Quick Reference

### 8pt spacing scale

| Token | px | rem (16px base) | Typical Use |
|---|---|---|---|
| space-0 | 0 | 0 | reset |
| space-0.5 | 2 | 0.125 | hairline gap, icon detail |
| space-1 | 4 | 0.25 | icon + text gap, tight badge padding |
| space-2 | 8 | 0.5 | button internal padding, form field gaps |
| space-3 | 12 | 0.75 | vertical button padding, card inner spacing |
| space-4 | 16 | 1.0 | default card padding, paragraph margin |
| space-5 | 20 | 1.25 | fine-tune step (use sparingly) |
| space-6 | 24 | 1.5 | card margin, section padding |
| space-8 | 32 | 2.0 | major layout spacing, form section gap |
| space-10 | 40 | 2.5 | large component margin |
| space-12 | 48 | 3.0 | section break on desktop |
| space-16 | 64 | 4.0 | hero section vertical rhythm |
| space-20 | 80 | 5.0 | major page sections |
| space-24 | 96 | 6.0 | between top-level sections |
| space-32 | 128 | 8.0 | full-screen section separation |

Rule: 4pt steps only for dense UI (icon-to-label, tight padding). 8pt steps
everywhere else. Never use 14, 18, 22, 30 — they break the grid.

### Container and gutter widths

| Breakpoint | Container Max Width | Gutter (horizontal padding) |
|---|---|---|
| Mobile (< 768px) | 100% fluid | 16px each side |
| Tablet (768–1023px) | 720px | 24px each side |
| Desktop (1024–1439px) | 960–1140px | 32px each side |
| Wide desktop (>= 1440px) | 1200–1280px | 32–48px each side |
| Reading column (long-form) | 640–720px | fluid |

Full tables in [references/spacing-layout.md](references/spacing-layout.md).

## Radius / Shadow / Border Quick Reference

### Border radius scale

| Token | Value | Typical Use |
|---|---|---|
| none | 0 | sharp edges, data tables |
| xs | 2px | badges, checkboxes, small tags |
| sm | 4px | compact buttons, labels, tooltips |
| md | 6–8px | default buttons, inputs, cards |
| lg | 12px | large cards, modal dialogs |
| xl | 16px | hero containers, featured panels |
| 2xl | 24px | decorative large surfaces |
| full | 9999px | pills, avatars, circular buttons |

### Box shadow elevation (Material Design)

| Level | CSS Box Shadow | Use |
|---|---|---|
| 0 | `none` | flat surfaces, cards on colored bg |
| 1 | `0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)` | resting cards, raised buttons |
| 2 | `0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)` | hover cards, snackbars |
| 3 | `0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)` | FAB, bottom navigation |
| 4 | `0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)` | dropdowns, small modals |
| 5 | `0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22)` | large modals, popovers |

### Border width

| Use | Width |
|---|---|
| Default divider / card border | 1px |
| Focus ring | 2px |
| Card on colored background | 0 (use shadow instead) |
| Input border | 1px (2px on focus) |

Full tables in [references/elevation-motion.md](references/elevation-motion.md).

## Motion Quick Reference

### Duration tiers

| Tier | Duration | Use |
|---|---|---|
| Micro | 100ms | button press, toggle switch, hover color |
| Standard | 200–300ms | dropdown, tooltip, tab change, card hover |
| Complex | 300–400ms | drawer, expansion panel, accordion |
| Entrance | 400–500ms | modal enter, page section reveal |
| Exit | 150–200ms | element leaving screen (faster than enter) |

### Easing curves (CSS cubic-bezier)

| Curve | Value | Use |
|---|---|---|
| Standard | `cubic-bezier(0.4, 0, 0.2, 1)` | default on-screen transition (Material 2) |
| Deceleration / ease-out | `cubic-bezier(0, 0, 0.2, 1)` | element entering screen |
| Acceleration / ease-in | `cubic-bezier(0.4, 0, 1, 1)` | element leaving screen |
| Emphasized (M3) | `cubic-bezier(0.2, 0, 0, 1)` | high-attention motion |
| Emphasized decelerate (M3) | `cubic-bezier(0.05, 0.7, 0.1, 1)` | prominent entrance |
| Emphasized accelerate (M3) | `cubic-bezier(0.3, 0, 0.8, 0.15)` | prominent exit |
| Sharp | `cubic-bezier(0.4, 0, 0.6, 1)` | states that abruptly end |

### Stagger and reduced motion

| Rule | Value |
|---|---|
| Stagger between list items | 50–100ms (use 50ms for long lists, 100ms for short) |
| Max total stagger delay | 300ms before last item starts |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` -> set duration to 0.01ms, disable transforms |

Full tables in [references/elevation-motion.md](references/elevation-motion.md).

## Responsive Breakpoints Quick Reference

### Framework comparison (mobile-first min-width)

| Label | Tailwind | Bootstrap 5 | Material UI v5 | Material M3 |
|---|---|---|---|---|
| xs / compact | 0 | 0 | 0 | < 600dp |
| sm | 640px | 576px | 600px | 600–839dp |
| md | 768px | 768px | 900px | 840–1199dp |
| lg | 1024px | 992px | 1200px | 1200–1599dp |
| xl | 1280px | 1200px | 1536px | 1600dp+ |
| 2xl / xxl | 1536px | 1400px | — | — |

### Navigation pattern transitions

| Viewport | Navigation Pattern |
|---|---|
| < 768px | hamburger menu / bottom tab bar |
| 768–1023px | condensed nav with icons + labels, or hamburger |
| >= 1024px | full horizontal nav with all links visible |

Full tables in [references/breakpoints-tokens.md](references/breakpoints-tokens.md).

## Failure Remediation Table

| Symptom | Likely Cause | Fix |
|---|---|---|
| Type scale steps feel too similar | ratio too small (1.125–1.2) | bump to 1.25 minimum; for display work go 1.333 |
| Headings look oversized and cartoonish | ratio too large (1.5+) with too many steps | drop to 1.25–1.333; keep display steps to 2–3 |
| Color palette feels muddy or neon | built in HSL, not OKLCH | rebuild ramp in OKLCH: same L step, hold C and H constant |
| Dark mode text is hard to read | just inverted light palette | lift text to 85–95% lightness, desaturate accents |
| Spacing feels random | values not on 4/8 grid | snap every px to nearest multiple of 4 (preferred 8) |
| Shadows look flat or muddy | single shadow layer | use paired key + ambient shadow (see elevation table) |
| Motion feels slow or sluggish | duration too long for micro-interactions | micro = 100ms; standard = 200–300ms; exit faster than enter |
| Overlays stack incorrectly | z-index ad-hoc | adopt Bootstrap scale: dropdown 1000, modal 1055, tooltip 1080 |
| Layout breaks between 768 and 1024 | no tablet-specific breakpoint | add md breakpoint at 768–900 range |

## Quality / Delivery Checklist

- [ ] Type scale: all steps computed from one ratio, rounded to 2 decimals
- [ ] Line height scales with font size (larger text = tighter line height)
- [ ] Body text contrast >= 4.5:1 on chosen background
- [ ] Large text / UI elements contrast >= 3:1
- [ ] All spacing values are multiples of 4 (preferably 8)
- [ ] Radius uses no more than 4 steps across the system
- [ ] Shadow elevation has exactly 5 levels, no custom one-off shadows
- [ ] Motion: every animation has a duration token and easing token
- [ ] `prefers-reduced-motion: reduce` is implemented
- [ ] Breakpoints match chosen framework (do not mix Tailwind and Bootstrap values)
- [ ] z-index values come from a named scale, never hard-coded 9999
- [ ] Token names follow: category-step (e.g. `color-primary-500`, `space-4`, `radius-md`)

## Chain Position

- Upstream: receives design brief and visual direction from **frontend-design-director**
- Downstream: hands verified token tables to **layout-spec-auditor** for grid QA
- Downstream: hands component token mappings to **frontend-component-lab** for implementation
- This skill outputs numeric references only — it does not write component code or render layouts.

## References

- [references/typography-scale.md](references/typography-scale.md) — full type scale tables per ratio, line height/letter spacing by element, font pairing guide, max line length by language
- [references/color-system.md](references/color-system.md) — color space comparison, palette construction steps, 60-30-10 examples, dark mode conversion, contrast calculation, accessible color pairs
- [references/spacing-layout.md](references/spacing-layout.md) — 8pt grid rules, full spacing scale, container widths by breakpoint, gutter/margin tables, section spacing, z-index scale
- [references/elevation-motion.md](references/elevation-motion.md) — radius scale, box shadow elevation levels with exact CSS, border rules, motion duration table, easing curve table, stagger rules, reduced motion
- [references/breakpoints-tokens.md](references/breakpoints-tokens.md) — responsive breakpoint comparison, navigation pattern transitions, design token hierarchy and naming convention
- [references/sources-and-licenses.md](references/sources-and-licenses.md) — every source, URL, license, and what was extracted
