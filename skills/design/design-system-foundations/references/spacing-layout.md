# Spacing & Layout Reference

Hard-number tables for the 8pt grid, spacing scale, container widths, gutters,
section spacing, and z-index layering.

## 8pt Grid Rules

| Rule | Detail |
|---|---|
| Base unit | 4px (half-step for fine adjustments) |
| Primary grid | 8px (all major spacing, padding, margins) |
| Where to use 4px steps | icon-to-label gap, tight badge padding, dense form fields |
| Where to use 8px steps | everything else: component padding, section margins, gutters |
| Forbidden values | 14px, 18px, 22px, 26px, 30px, 34px — any number not divisible by 4 |
| Icon grid alignment | 8pt grid aligns to 16x16 and 24x24 icon sizes (both multiples of 8) |
| Why 8 | divides cleanly at 1x, 2x, and 3x display densities; common multiple of 1, 2, 4 |

## Full Spacing Scale

| Token | px | rem (16px base) | Common Use |
|---|---|---|---|
| space-0 | 0 | 0 | reset, no spacing |
| space-px | 1 | 0.0625 | hairline border |
| space-0.5 | 2 | 0.125 | icon detail, tight inner gap |
| space-1 | 4 | 0.25 | icon + text gap, badge padding |
| space-1.5 | 6 | 0.375 | compact vertical padding (half step) |
| space-2 | 8 | 0.5 | button internal padding, form gaps |
| space-2.5 | 10 | 0.625 | fine adjustment (use sparingly) |
| space-3 | 12 | 0.75 | vertical button padding, card inner |
| space-4 | 16 | 1.0 | default card padding, paragraph margin |
| space-5 | 20 | 1.25 | step between 4 and 6 |
| space-6 | 24 | 1.5 | card margin, section padding |
| space-8 | 32 | 2.0 | major layout spacing, form sections |
| space-10 | 40 | 2.5 | large component margins |
| space-12 | 48 | 3.0 | desktop section breaks |
| space-14 | 56 | 3.5 | between major blocks |
| space-16 | 64 | 4.0 | hero vertical rhythm |
| space-20 | 80 | 5.0 | top-level page sections |
| space-24 | 96 | 6.0 | between hero and content |
| space-32 | 128 | 8.0 | full-screen section separation |

## Container Max Widths by Breakpoint

| Breakpoint | Tailwind | Bootstrap 5 | Material UI v5 | Typical Container Max |
|---|---|---|---|---|
| xs (< 640px) | 0 | 0 | 0 | 100% fluid, 16px side padding |
| sm (>= 640px) | 640px | 576px | 600px | 540px |
| md (>= 768px) | 768px | 768px | 900px | 720px |
| lg (>= 1024px) | 1024px | 992px | 1200px | 960–1024px |
| xl (>= 1280px) | 1280px | 1200px | 1536px | 1140–1200px |
| 2xl (>= 1536px) | 1536px | 1400px | — | 1280–1320px |

### Content column widths

| Content Type | Max Width | Rationale |
|---|---|---|
| Long-form reading (article) | 640–720px | ~66 characters per line at 16px |
| Marketing landing page | 1200–1280px | wide hero, multiple columns |
| Dashboard / data table | 1440px+ | data density needs width |
| Modal dialog | 480–640px | focused task |
| Sidebar / aside | 280–320px | narrow, scannable |

## Gutter Sizes (Horizontal Padding)

| Viewport | Gutter Each Side |
|---|---|
| Mobile (< 768px) | 16px minimum |
| Tablet (768–1023px) | 24px |
| Desktop (>= 1024px) | 32px |
| Wide desktop (>= 1440px) | 32–48px |

Content must never touch viewport edges. Use fluid side padding with clamp:
`padding-inline: clamp(16px, 5vw, 48px)`.

## Margin and Padding Ratios

| Relationship | Ratio | Example |
|---|---|---|
| Paragraph margin to line height | 0.75x–1.5x | 16px line-height -> 12–24px paragraph margin |
| Section padding to gutter | 2x–3x | 24px gutter -> 48–72px section padding |
| Card padding to card gap | 1:1 to 1.5:1 | 16px padding -> 16–24px gap between cards |
| Component margin to component size | 0.5x | 48px tall button -> 24px margin |

## Section Spacing

| Section Type | Vertical Padding (Desktop) |
|---|---|
| Between paragraphs | 16–24px |
| Between cards in a grid | 24–32px |
| Between major sections | 64–96px |
| Hero to content | 96–128px |
| Footer to content | 64–96px |

On mobile, reduce section spacing by ~30%: 48–64px between sections instead of
64–96px.

## Z-Index Scale

### Bootstrap convention (complex apps)

| Layer | Token | Value | Use |
|---|---|---|---|
| Base | z-base | 0 | default stacking |
| Raised | z-raised | 1 | above default flow |
| Dropdown | z-dropdown | 1000 | dropdown menus |
| Sticky | z-sticky | 1020 | sticky headers, sidebars |
| Fixed | z-fixed | 1030 | fixed navbars, FAB |
| Offcanvas backdrop | z-offcanvas-backdrop | 1040 | off-screen panel backdrop |
| Offcanvas | z-offcanvas | 1045 | off-screen panel |
| Modal backdrop | z-modal-backdrop | 1050 | dialog overlay |
| Modal | z-modal | 1055 | modal dialog |
| Popover | z-popover | 1070 | popover content |
| Tooltip | z-tooltip | 1080 | tooltips (always on top) |

### Simplified scale (small apps)

| Layer | Value |
|---|---|
| base | 0 |
| dropdown | 10 |
| sticky | 20 |
| fixed | 30 |
| overlay / backdrop | 40 |
| modal | 50 |
| popover | 60 |
| toast | 70 |
| tooltip | 80 |

Rules:

- Never use z-index 9999 or 999 — it escapes the system and causes bugs
- Always use named tokens, never raw numbers in components
- Leave 10-unit gaps between layers for future insertion
- Tooltips always sit above everything else

## Sources

- 8pt grid system: widely adopted by Material Design, Apple HIG, Google. Confirmed by multiple design system references.
- Spacing scale values: cross-referenced from Tailwind CSS spacing scale, PIE Design System, GEL (PageSuite), and 8pt grid guides.
- Container widths: Bootstrap 5 container max-widths (getbootstrap.com), responsive design guides.
- Z-index scale: Bootstrap 5.3 z-index documentation (getbootstrap.com/docs/5.3/layout/z-index/); Material UI z-index scale.
