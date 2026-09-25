# Breakpoints & Design Tokens Reference

Hard-number tables for responsive breakpoint comparison across frameworks,
navigation pattern transitions, container queries vs media queries, and design
token hierarchy with naming conventions.

## Responsive Breakpoint Comparison

### Mobile-first min-width breakpoints

| Label | Tailwind CSS v3/v4 | Bootstrap 5 | Material UI v5 | Material M3 | Device Class |
|---|---|---|---|---|---|
| xs / compact | 0 | 0 | 0 | < 600dp | phone portrait |
| sm | 640px | 576px | 600px | 600–839dp | large phone / small tablet |
| md | 768px | 768px | 900px | 840–1199dp | tablet portrait / small laptop |
| lg | 1024px | 992px | 1200px | 1200–1599dp | laptop / desktop |
| xl | 1280px | 1200px | 1536px | 1600dp+ | large desktop |
| 2xl / xxl | 1536px | 1400px | — | — | ultra-wide |

### Key differences

| Framework | sm starts at | Extra tier |
|---|---|---|
| Tailwind | 640px | 2xl at 1536px |
| Bootstrap | 576px | xxl at 1400px |
| Material UI v5 | 600px | xl at 1536px |
| Material M3 | 600dp (compact/medium split) | 5 tiers total |

Rule: pick ONE framework's breakpoints and stay consistent. Do not mix Tailwind's
640px sm with Bootstrap's 576px sm in the same project.

## Container Max Widths

| Breakpoint | Bootstrap 5 | Tailwind (container) |
|---|---|---|
| xs (< 576px) | 100% | 100% |
| sm (>= 576px) | 540px | 640px |
| md (>= 768px) | 720px | 768px |
| lg (>= 992/1024px) | 960px | 1024px |
| xl (>= 1200/1280px) | 1140px | 1280px |
| xxl / 2xl (>= 1400/1536px) | 1320px | 1536px |

## Navigation Pattern Transitions

| Viewport Range | Navigation Pattern |
|---|---|
| < 768px (mobile) | hamburger menu, or bottom tab bar (max 5 tabs) |
| 768–1023px (tablet) | condensed nav: icons + text labels, or hamburger |
| 1024–1279px (small desktop) | full horizontal nav, condensed search |
| >= 1280px (desktop) | full horizontal nav, all links visible |

### Common navigation breakpoints

| Pattern | Collapse At |
|---|---|
| Horizontal nav -> hamburger | < 768px (most common) |
| Horizontal nav -> hamburger | < 1024px (if many nav items) |
| Sidebar -> icon rail | < 1024px |
| Bottom tab bar (mobile apps) | always on < 768px |
| Two-column -> single column | < 768px |
| Three-column -> two-column -> single | 1024px -> 768px |

## Media Queries vs Container Queries

| Approach | Syntax | Use For |
|---|---|---|
| Media query | `@media (min-width: 768px)` | viewport-level layout changes, page-level breakpoints |
| Container query | `@container (min-width: 400px)` | component-level changes based on parent width |
| Container query support | modern browsers (2023+) | cards, sidebar widgets, embedded components |

Rule: use media queries for page layout. Use container queries for components
that appear in different contexts (e.g. a card that looks different in a sidebar
vs in a 3-column grid).

## Mobile-First Approach

| Principle | Detail |
|---|---|
| Start with | base styles for smallest screen (0px+) |
| Add enhancements | with `min-width` media queries going up |
| Never | start desktop-first and undo with `max-width` queries |
| Reason | mobile CSS is simpler and faster; progressive enhancement |

## Design Token Hierarchy

Three-tier architecture: Global -> Alias -> Component.

### Tier 1: Global Tokens (Primitives)

Raw, context-free values. The palette and scales. No semantic meaning.

```
--color-blue-50: #eff6ff
--color-blue-500: #3b82f6
--color-blue-900: #1e3a8a
--space-1: 4px
--space-4: 16px
--radius-md: 8px
--font-size-lg: 18px
--duration-standard: 250ms
```

### Tier 2: Alias Tokens (Semantic)

Map primitives to meaning. Theming lives here.

```
--color-primary: var(--color-blue-500)
--color-on-primary: #ffffff
--color-surface: #ffffff
--color-on-surface: #1f2937
--color-border: var(--color-gray-200)
--space-card-padding: var(--space-4)
--radius-card: var(--radius-md)
--duration-interactive: var(--duration-standard)
```

### Tier 3: Component Tokens

Map aliases to specific components. Most specific layer.

```
--button-primary-bg: var(--color-primary)
--button-primary-text: var(--color-on-primary)
--button-primary-radius: var(--radius-sm)
--card-bg: var(--color-surface)
--card-shadow: var(--shadow-2)
--input-border: var(--color-border)
```

## Token Naming Convention

### Scale-based naming (most common)

Pattern: `category-step` or `category-name-step`

| Category | Examples |
|---|---|
| Color | `color-blue-500`, `color-gray-100`, `color-red-600` |
| Spacing | `space-1`, `space-4`, `space-8`, `space-16` |
| Radius | `radius-sm`, `radius-md`, `radius-lg`, `radius-full` |
| Font size | `font-size-sm`, `font-size-md`, `font-size-lg`, `font-size-xl` |
| Font weight | `font-weight-regular`, `font-weight-medium`, `font-weight-bold` |
| Shadow | `shadow-sm`, `shadow-md`, `shadow-lg`, `shadow-xl` |
| Duration | `duration-fast`, `duration-standard`, `duration-slow` |
| Easing | `easing-standard`, `easing-decelerate`, `easing-accelerate` |
| Z-index | `z-dropdown`, `z-sticky`, `z-modal`, `z-tooltip` |

### Semantic alias naming

Pattern: `category-role-state`

```
color-primary-default
color-primary-hover
color-primary-active
color-surface-default
color-on-surface
color-border-default
color-border-focus
```

### Rules

- Never use raw values in components — always reference a token
- Global tokens are never directly used by components (go through alias)
- Dark mode swaps alias token values, not global token values
- Keep token count under 100 per category; merge rarely-used steps

## Token Categories Checklist

| Category | Token Count Target |
|---|---|
| Color (global palette) | 9–11 steps per hue, 5–7 hues |
| Color (semantic aliases) | 15–25 roles |
| Spacing | 12–16 steps |
| Typography (font size) | 8–10 steps |
| Typography (line height) | 4–6 values |
| Radius | 6–8 steps |
| Shadow | 5 levels |
| Duration | 4–5 tiers |
| Easing | 3–5 curves |
| Z-index | 8–10 layers |

## Sources

- Breakpoint values: Tailwind CSS docs (tailwindcss.com/docs/responsive-design); Bootstrap 5.3 docs (getbootstrap.com/docs/5.0/layout/breakpoints/); Material UI v5 docs; Material Design 3 breakpoints (m3.material.io/foundations/layout/breakpoints).
- Design token hierarchy: Design Tokens Community Group (designtokens.org); zeroheight design tokens guide; Figma design tokens resource; Adobe Spectrum token naming.
- Token naming conventions: zeroheight naming guide; Tailwind utility class naming.
