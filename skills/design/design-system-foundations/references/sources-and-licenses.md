# Sources and Licenses

Every source consulted while building this skill, what was extracted, and the
applicable license. All extracted facts are numeric values, ratios, and tables —
no prose passages were copied.

## Typography

| Source | URL | What Was Extracted | License |
|---|---|---|---|
| Modular scale ratios (1.067–1.618) | studiolimb.com/guides/modular-type-scale-guide.html | ratio names and character descriptions | educational reference, no explicit license |
| Type scale px calculations | design.dev/guides/typography-web-design/ | perfect fifth and golden ratio scale examples | educational reference |
| Type scale CSS guide | fontfyi.com/ko/blog/type-scale-css-custom-properties/ | major third, perfect fourth scale use cases | educational reference |
| Line height rules | humanstandards.org/code-design-tokens/accessible-typography/ | line height by content type table | educational reference |
| Letter spacing rules | stacklesson.com/css/css-typography/text-spacing-readability/ | -0.02em headings, +0.05em all-caps values | educational reference |
| Max line length (45–75 CPL, 66 ideal) | design.max.gov/visual-typography.html | 66 char ideal, 50–75 range, max-width: 35em | U.S. Government public domain |
| Line length research | uxpin.com/studio/blog/optimal-line-length-for-readability/ | 50–75 CPL, 66 optimal confirmation | educational reference |
| Bringhurst measure principle | stellae.design/en/ux/paragraph-width | 45–75 CPL, 66 ideal from Elements of Typographic Style | book citation |

## Color

| Source | URL | What Was Extracted | License |
|---|---|---|---|
| WCAG contrast ratios | m3.material.io/foundations/designing/color-contrast | 4.5:1 normal, 3:1 large text | Material Design (Apache 2.0 / CC BY) |
| WCAG 2.0 legibility | m2.material.io/design/color/text-legibility.html | 4.5:1 AA, 3:1 large text | Material Design |
| Dark theme properties | m2.material.io/design/color/dark-theme.html | dark surfaces, desaturation, elevation depth | Material Design |
| Color system roles | m3.material.io/styles/color/system/how-the-system-works | standard/medium/high contrast levels | Material Design 3 |
| OKLCH perceptual uniformity | oklch.org | L channel uniform, equal L steps = even ramp | educational reference |
| OKLCH vs HSL | frontendchecklist.io/rules/css/color-oklch | why HSL is non-uniform, OKLCH benefits | open checklist, MIT-style |
| 60-30-10 rule | uxpin.com/studio/blog/choose-color-pallete/ | 60% dominant, 30% secondary, 10% accent | educational reference |
| 60-30-10 dark mode | sixtythirtyten.co/blog/60-30-10-dark-mode-color-palette-css | dark mode color distribution | educational reference |

## Spacing & Layout

| Source | URL | What Was Extracted | License |
|---|---|---|---|
| 8pt grid system | gridmakerpro.com/grids/typography-grids/8pt-spacing-grid/ | 8/16/24/32/40/48/56/64 scale, 4pt subdivisions | educational reference |
| Spacing scale tokens | recursoswebyseo.com/diseno-web/reticula-8pt-sistema-espaciado/ | space-1 through space-4 px values | educational reference |
| PIE design spacing tokens | pie.design/foundations/spacing/tokens/global/ | 0/2/4/8/12px token values | open source design system |
| GEL spacing | gel.pageuppeople.com/latest/foundations/spacing-gPjX38g3 | 4px base, 8pt rhythm, 4pt fine adjustments | open design system |
| Container max widths | getbootstrap.com/docs/5.3/layout/containers/ | sm 540, md 720, lg 960, xl 1140, xxl 1320 | Bootstrap (MIT) |
| Bootstrap breakpoints | getbootstrap.com/docs/5.0/layout/breakpoints/ | sm 576, md 768, lg 992, xl 1200, xxl 1400 | Bootstrap (MIT) |
| Z-index scale | getbootstrap.com/docs/5.3/layout/z-index/ | dropdown 1000, sticky 1020, fixed 1030, modal 1055, tooltip 1080 | Bootstrap (MIT) |

## Elevation & Motion

| Source | URL | What Was Extracted | License |
|---|---|---|---|
| Box shadow elevation levels | m2.material.io/guidelines/material-design/elevation-shadows.html | 0–5 dp elevation system | Material Design |
| Shadow CSS values | tooleras.com/blog/css-box-shadow-complete-guide | elevation 1–5 exact box-shadow CSS | educational reference |
| Radius scale | designsystem.maersk.com/foundations/corner-radius/ | xs 2, sm 4, md 6, lg 8, xl 12, 2xl 16, full 9999 | open design system |
| Atlassian radius | atlassian.design/foundations/radius | xsmall 2, small 4, medium 6 | open design system |
| Border radius tokens | designsystemproblems.com/token-management/border-radius-tokens/ | sm 2, md 4, lg 8, xl 12, 2xl 16, full 9999 | educational reference |
| Material motion duration/easing | m2.material.io/guidelines/motion/duration-easing.html | standard cubic-bezier(0.4,0,0.2,1) | Material Design |
| M3 easing and duration | m3.material.io/styles/motion/easing-and-duration | emphasized 500ms, decelerate 400ms, accelerate 200ms | Material Design 3 |
| M3 motion specs | m3.material.io/styles/motion/overview/specs | spring curves and durations | Material Design 3 |
| prefers-reduced-motion | developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion | reduce media query syntax | MDN (CC BY-SA) |
| Reduced motion CSS | joshwcomeau.com/react/prefers-reduced-motion/ | 0.01ms duration override pattern | educational reference |
| Stagger timing | motion.dev/docs/stagger | 50–100ms stagger between items | educational reference |

## Breakpoints & Tokens

| Source | URL | What Was Extracted | License |
|---|---|---|---|
| Tailwind breakpoints | tailwindcss.com/docs/responsive-design | sm 640, md 768, lg 1024, xl 1280, 2xl 1536 | Tailwind (MIT) |
| Bootstrap breakpoints | getbootstrap.com/docs/5.0/layout/breakpoints/ | sm 576, md 768, lg 992, xl 1200, xxl 1400 | Bootstrap (MIT) |
| Material M3 breakpoints | m3.material.io/foundations/layout/breakpoints | compact <600, medium 600–839, expanded 840–1199, large 1200–1599 | Material Design 3 |
| MUI v5 breakpoints | mui.com | xs 0, sm 600, md 900, lg 1200, xl 1536 | MUI (MIT) |
| Token hierarchy | design.dev/guides/design-systems/ | global -> alias -> component three tiers | educational reference |
| Token naming | zeroheight.com/learn/naming-your-design-tokens-a-practical-guide | scale-based naming: color-500, space-4, radius-md | educational reference |
| Token levels | uxpin.com/studio/blog/what-are-design-tokens/ | three-tier token architecture | educational reference |
| Figma design tokens | figma.com/resource-library/design-tokens/ | component token layer definition | educational reference |

## License Notes

- Material Design documentation is licensed under CC BY 4.0, with code examples
  under Apache 2.0.
- Bootstrap and Tailwind CSS are MIT-licensed open source projects.
- MDN Web Docs content is CC BY-SA 2.5.
- U.S. federal government design systems (USWDS, MAX.gov) are public domain.
- All third-party blog posts and educational articles are referenced for factual
  numeric values only; no prose was copied.
- This skill itself is Apache-2.0 licensed, consistent with the skillkit repository.
