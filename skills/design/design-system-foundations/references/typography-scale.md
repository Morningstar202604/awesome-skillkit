# Typography Scale Reference

Hard-number tables for modular type scales, line height, letter spacing, and line
length. All px values computed from a 16px base unless noted.

## Table of Contents

- [Modular Ratios](#modular-ratios)
- [Full Type Scale Tables (16px base)](#full-type-scale-tables-16px-base)
- [Line Height by Element](#line-height-by-element)
- [Letter Spacing (Tracking)](#letter-spacing-tracking)
- [Max Line Length (Measure)](#max-line-length-measure)
- [Paragraph Spacing](#paragraph-spacing)
- [Font Pairing Rules](#font-pairing-rules)
- [Sources](#sources)

## Modular Ratios

| Ratio | Name | Character | Best For |
|---|---|---|---|
| 1.067 | Minor Second | Very tight, subtle | dense data dashboards |
| 1.125 | Major Second | Subtle, gentle | long-form editorial, many text levels |
| 1.200 | Minor Third | Balanced | most UI applications |
| 1.250 | Major Third | Clear hierarchy, modern | marketing, landing pages, general web |
| 1.333 | Perfect Fourth | Strong, confident | display, hero sections, editorial |
| 1.414 | Augmented Fourth (sqrt 2) | Dramatic, bold | few, well-differentiated levels |
| 1.500 | Perfect Fifth | Strong contrast | display-heavy, bold statements |
| 1.618 | Golden Ratio | Striking, classic | dramatic editorial, single hero numbers |

## Full Type Scale Tables (16px base)

### 1.25 — Major Third

| Step | Multiplier | px | rem |
|---|---|---|---|
| -2 | 0.4096 | 6.55 | 0.41 |
| -1 | 0.5120 | 8.19 | 0.51 |
| 0 | 0.6400 | 10.24 | 0.64 |
| 1 | 0.8000 | 12.80 | 0.80 |
| base | 1.0000 | 16.00 | 1.00 |
| 2 | 1.2500 | 20.00 | 1.25 |
| 3 | 1.5625 | 25.00 | 1.56 |
| 4 | 1.9531 | 31.25 | 1.95 |
| 5 | 2.4414 | 39.06 | 2.44 |
| 6 | 3.0518 | 48.83 | 3.05 |
| 7 | 3.8147 | 61.04 | 3.81 |
| 8 | 4.7684 | 76.30 | 4.77 |

### 1.333 — Perfect Fourth

| Step | Multiplier | px | rem |
|---|---|---|---|
| -2 | 0.5633 | 9.01 | 0.56 |
| -1 | 0.7500 | 12.00 | 0.75 |
| base | 1.0000 | 16.00 | 1.00 |
| 2 | 1.3330 | 21.33 | 1.33 |
| 3 | 1.7769 | 28.43 | 1.78 |
| 4 | 2.3686 | 37.90 | 2.37 |
| 5 | 3.1573 | 50.52 | 3.16 |
| 6 | 4.2087 | 67.34 | 4.21 |
| 7 | 5.6102 | 89.76 | 5.61 |

### 1.414 — Augmented Fourth

| Step | Multiplier | px | rem |
|---|---|---|---|
| -1 | 0.7072 | 11.31 | 0.71 |
| base | 1.0000 | 16.00 | 1.00 |
| 2 | 1.4140 | 22.62 | 1.41 |
| 3 | 2.0000 | 32.00 | 2.00 |
| 4 | 2.8280 | 45.25 | 2.83 |
| 5 | 4.0000 | 64.00 | 4.00 |
| 6 | 5.6560 | 90.51 | 5.66 |

### 1.5 — Perfect Fifth

| Step | Multiplier | px | rem |
|---|---|---|---|
| -1 | 0.6667 | 10.67 | 0.67 |
| base | 1.0000 | 16.00 | 1.00 |
| 2 | 1.5000 | 24.00 | 1.50 |
| 3 | 2.2500 | 36.00 | 2.25 |
| 4 | 3.3750 | 54.00 | 3.38 |
| 5 | 5.0625 | 81.00 | 5.06 |
| 6 | 7.5938 | 121.50 | 7.59 |

### 1.618 — Golden Ratio

| Step | Multiplier | px | rem |
|---|---|---|---|
| -1 | 0.6180 | 9.89 | 0.62 |
| base | 1.0000 | 16.00 | 1.00 |
| 2 | 1.6180 | 25.89 | 1.62 |
| 3 | 2.6180 | 41.89 | 2.62 |
| 4 | 4.2360 | 67.78 | 4.24 |
| 5 | 6.8540 | 109.66 | 6.85 |

## Line Height by Element

| Element Type | Line Height | CSS Unitless | Rationale |
|---|---|---|---|
| Display / hero (48px+) | 1.0–1.1 | 1.05 | very tight for visual impact |
| H1 (32–48px) | 1.1–1.2 | 1.15 | tight, large size gives natural breathing room |
| H2 (24–32px) | 1.2–1.3 | 1.2 | compact |
| H3–H6 (16–24px) | 1.3–1.4 | 1.35 | moderate |
| Body (14–18px) | 1.4–1.6 | 1.5 | default readability |
| Small text / caption (12–14px) | 1.5–1.7 | 1.6 | extra space for small x-height |
| All-caps label | 1.3–1.4 | 1.35 | tight tracking needs compact leading |
| Long-form article | 1.6–1.75 | 1.7 | maximum reading comfort |

Rule: line height decreases as font size increases. Use unitless values so
line-height scales with font-size inheritance.

## Letter Spacing (Tracking)

| Element | Letter Spacing | Rationale |
|---|---|---|
| Display text (64px+) | -0.03em to -0.02em | large open counters need tightening |
| H1–H2 (24–48px) | -0.02em | optical correction for large sizes |
| H3–H6 (16–24px) | -0.01em to 0 | minimal adjustment |
| Body (14–18px) | 0 | default font metrics are tuned for body |
| Small text / caption | +0.01em | slight looseness aids small-size legibility |
| All-caps label / eyebrow | +0.05em to +0.1em | caps have no descenders; tracking out improves readability |
| Button text | 0 to +0.01em | depends on font; default is fine |

Never track out body paragraphs — it reduces word cohesion and slows reading.

## Max Line Length (Measure)

| Language / Script | Optimal CPL | Min CPL | Max CPL |
|---|---|---|---|
| English / Latin (long-form) | 66 | 45 | 75 |
| English / Latin (UI / dashboard) | 50–60 | 35 | 75 |
| CJK (Chinese / Japanese) | 20–40 characters | 15 | 45 |
| Arabic / RTL | 40–60 | 30 | 70 |

CSS implementation:

```css
.reading-column {
  max-width: 65ch;  /* ~66 characters for Latin script */
}
```

Lines shorter than 45 CPL create excessive line breaks and fragment reading
rhythm. Lines longer than 75 CPL cause eye-tracking fatigue and reduced
comprehension.

## Paragraph Spacing

| Content Type | Paragraph Margin |
|---|---|
| UI / dashboard | 0.75em–1em |
| Marketing / landing | 1em–1.25em |
| Long-form article / blog | 1.25em–1.5em |

Use `margin-bottom` on paragraphs, not extra line breaks.

## Font Pairing Rules

| Rule | Detail |
|---|---|
| Max families | 2 typefaces per product |
| Safe combination | Serif (headings) + Sans-serif (body) |
| Weight contrast | heading weight 600–700, body weight 400 |
| X-height contrast | pair a large-x-height sans with a smaller-x-height serif |
| Same foundry | when in doubt, pick both from the same superfamily (e.g. Inter + Inter Display) |
| Avoid | two display serifs, two script fonts, same weight paired across families |

## Sources

- Modular scale ratios and px calculations derived from standard modular scale math (base 16px, multiply by ratio per step up and divide per step down)
- Line height and letter spacing values cross-referenced from Material Design type guidance, web typography best practices, and WCAG 1.4.12 (Text Spacing)
- Max line length 45–75 CPL, 66 ideal: Robert Bringhurst, *The Elements of Typographic Style*; confirmed by U.S. Web Design System, MAX.gov Design System, and UXPin typography guidelines
