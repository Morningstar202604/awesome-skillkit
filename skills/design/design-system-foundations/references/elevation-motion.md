# Elevation & Motion Reference

Hard-number tables for border radius, box shadow elevation levels, border widths,
motion duration tiers, easing curves, stagger rules, and reduced motion.

## Table of Contents

- [Border Radius Scale](#border-radius-scale)
- [Box Shadow Elevation](#box-shadow-elevation)
- [Border Width Rules](#border-width-rules)
- [Motion Duration Tiers](#motion-duration-tiers)
- [Easing Curves (CSS cubic-bezier)](#easing-curves-css-cubic-bezier)
- [Stagger Rules](#stagger-rules)
- [Reduced Motion](#reduced-motion)
- [Sources](#sources)

## Border Radius Scale

### Standard scale

| Token | Value | px | Typical Use |
|---|---|---|---|
| none | 0 | 0 | sharp edges, data tables, code blocks |
| xs | 0.125rem | 2px | badges, checkboxes, small tags, avatars (small) |
| sm | 0.25rem | 4px | compact buttons, labels, tooltips, timestamps |
| md | 0.375rem | 6px | default buttons, inputs, selects (Atlassian) |
| lg | 0.5rem | 8px | cards, default interactive elements (most common) |
| xl | 0.75rem | 12px | large cards, modal dialogs, dropdown menus |
| 2xl | 1rem | 16px | hero containers, featured panels |
| 3xl | 1.5rem | 24px | decorative large surfaces |
| full | 9999px | 9999px | pills, avatars, circular FABs |

### Radius by element height

| Element Height | Recommended Radius |
|---|---|
| 16–24px (badges, tags) | 2–4px |
| 32–40px (buttons, inputs) | 6–8px |
| 48–64px (cards, dropdowns) | 8–12px |
| 80px+ (hero, modals) | 16–24px |
| Pill / circular | 9999px (50% of height) |

### Sharp vs rounded decision

| Vibe | Radius | Use Case |
|---|---|---|
| Technical / data-heavy | 0–2px | dashboards, admin tools, code editors |
| Clean / professional | 4–6px | SaaS, enterprise apps |
| Friendly / modern | 8px | consumer apps, marketing sites (default) |
| Playful / soft | 12–16px | kids apps, wellness, lifestyle brands |
| Pill | 9999px | buttons, tags, avatars only — never for large containers |

Rule: pick ONE radius for the system default and stick to it. Do not mix 4px
buttons with 12px cards randomly.

## Box Shadow Elevation

### Material Design paired-shadow system

Each elevation level uses two shadows: a key light (tight, dark) and an ambient
light (wide, soft) to simulate directional lighting.

| Level | dp Elevation | CSS Box Shadow | Use |
|---|---|---|---|
| 0 | 0dp | `none` | flat surfaces, cards on colored backgrounds |
| 1 | 1dp | `0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)` | resting cards, raised buttons, switches |
| 2 | 2dp | `0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)` | hover cards, snackbars, FAB rest |
| 3 | 3dp | `0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)` | FAB pressed, bottom navigation |
| 4 | 4dp | `0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)` | dropdown menus, small modals |
| 5 | 5dp | `0 19px 38px rgba(0,0,0,0.30), 0 15px 12px rgba(0,0,0,0.22)` | large modals, popovers, top navigation |

### Dark mode elevation

In dark mode, shadows alone are nearly invisible. Material M3 uses a tonal
overlay instead:

| Elevation | Surface Lightness Overlay (white alpha) |
|---|---|
| 0 | 0% |
| 1 | +5% |
| 2 | +8% |
| 3 | +11% |
| 4 | +12% |
| 5 | +14% |

Apply as a semi-transparent white overlay on top of the dark surface color.

## Border Width Rules

| Element | Default Width | Focus / Active Width |
|---|---|---|
| Card border | 1px | 1px |
| Input border | 1px | 2px |
| Button border | 1px (outlined variant) | 2px |
| Divider / horizontal rule | 1px | — |
| Focus ring | 2px | 2px offset, transparent base |
| Border on colored background | 0 (use shadow) | — |
| Table row divider | 1px | — |

## Motion Duration Tiers

| Tier | Duration Range | Default | Use Case |
|---|---|---|---|
| Micro / instant | 100ms | 100ms | button press, toggle, hover color, checkbox |
| Standard | 200–300ms | 250ms | dropdown, tooltip, tab change, card hover, link underline |
| Complex | 300–400ms | 350ms | drawer, expansion panel, accordion, bottom sheet |
| Entrance | 400–500ms | 450ms | modal enter, page section reveal, hero animation |
| Exit | 150–200ms | 180ms | element leaving (always faster than entrance) |

Rule: exit animations are 50–100ms faster than entrance animations. Users wait
for things to appear, but want things to go away quickly.

## Easing Curves (CSS cubic-bezier)

### Material Design 2 (classic)

| Curve | cubic-bezier | Use |
|---|---|---|
| Standard (FastOutSlowIn) | `cubic-bezier(0.4, 0, 0.2, 1)` | default on-screen transition |
| Deceleration / ease-out | `cubic-bezier(0, 0, 0.2, 1)` | element entering screen |
| Acceleration / ease-in | `cubic-bezier(0.4, 0, 1, 1)` | element leaving screen |
| Sharp | `cubic-bezier(0.4, 0, 0.6, 1)` | states that end abruptly |

### Material Design 3 (emphasized)

| Curve | cubic-bezier | Use | Duration |
|---|---|---|---|
| Emphasized | `cubic-bezier(0.2, 0, 0, 1)` | begin and end on screen | 300–500ms |
| Emphasized decelerate | `cubic-bezier(0.05, 0.7, 0.1, 1)` | enter the screen | 250–400ms |
| Emphasized accelerate | `cubic-bezier(0.3, 0, 0.8, 0.15)` | exit the screen | 200ms |

### Built-in CSS easings (for reference)

| CSS Name | Approximation | Use |
|---|---|---|
| `ease` | `cubic-bezier(0.25, 0.1, 0.25, 1)` | default, general |
| `ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | entrance |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | exit |
| `ease-in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | symmetric, dialogs |

## Stagger Rules

| Scenario | Stagger Delay Between Items |
|---|---|
| Short list (3–5 items) | 80–100ms |
| Medium list (6–10 items) | 50–80ms |
| Long list (10+ items) | 30–50ms |
| Grid (row by row) | 50ms per row, 50ms per column |
| Max total delay before last item starts | 300ms |

Formula: `delay = index * stagger_interval`. Never let the last item start more
than 300ms after page load — users should not wait for animation to see content.

## Reduced Motion

### Required implementation

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### What to disable vs keep

| Type | Reduced Motion Behavior |
|---|---|
| Fade-in / opacity | keep (opacity changes are safe) |
| Slide / translate / transform | disable or reduce to opacity-only |
| Parallax scrolling | disable entirely |
| Auto-playing carousels | disable |
| Hover micro-interactions | keep (user-initiated, short) |
| Focus transitions | keep (accessibility critical) |

Users with vestibular disorders, motion sensitivity, or old age may have reduced
motion enabled at the OS level. This is not optional — it is a WCAG 2.1 AAA
criterion and a quality floor.

## Sources

- Border radius scale: Maersk Design System, Atlassian Design System, USWDS, Tailwind CSS border-radius docs.
- Box shadow elevation levels: Material Design elevation system (m2.material.io/guidelines/material-design/elevation-shadows.html); cross-referenced from multiple CSS shadow guides.
- Motion duration and easing: Material Design motion specs (m2.material.io/guidelines/motion/duration-easing.html; m3.material.io/styles/motion/easing-and-duration).
- Stagger timing: common practice across Framer Motion, GSAP, and CSS animation guides.
- prefers-reduced-motion: MDN Web Docs; W3C WCAG 2.1; Josh Comeau's accessible animations guide.
