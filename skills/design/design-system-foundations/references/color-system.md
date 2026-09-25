# Color System Reference

Hard-number tables for color spaces, contrast ratios, palette construction, dark
mode conversion, and accessible color pairs.

## Color Space Comparison

| Space | Perceptually Uniform? | Use Case | Notes |
|---|---|---|---|
| sRGB / HEX | No | legacy, web compatibility | every browser supports it; not uniform |
| HSL | No | quick color picking | same L% can look wildly different (yellow vs blue) |
| HSV / HSB | No | design tools | similar non-uniformity to HSL |
| OKLCH | Yes | modern palette generation, gradients | L channel matches perceived brightness; equal L steps = even ramp |
| CIELAB / CIELUV | Partially | color science reference | older, less smooth than OKLCH |

### Why OKLCH matters

- Equal numeric changes in L produce equal perceived brightness, regardless of hue
- Generate a 5-step ramp by holding C and H constant, stepping L from 95 to 25
- Same-L buttons across hues actually match in brightness
- Linear interpolation in OKLCH passes through perceptually smooth midpoints
  (sRGB/HSL interpolation passes through muddy gray)
- Supports Display P3 wide gamut on modern devices

CSS syntax: `oklch(lightness% chroma hue)` — e.g. `oklch(70% 0.15 250)`.

## WCAG Contrast Ratios

### Text contrast (WCAG 2.1)

| Level | Normal Text | Large Text | UI Components |
|---|---|---|---|
| AA minimum | 4.5:1 | 3:1 | 3:1 |
| AAA enhanced | 7:1 | 4.5:1 | — |

Large text defined as: >= 18pt (24px) regular, OR >= 14pt (18.66px) bold.

### Contrast formula

Relative luminance: `L = 0.2126*R + 0.7152*G + 0.0722*B` (linearized).
Contrast ratio = `(L1 + 0.05) / (L2 + 0.05)`, where L1 is the lighter color.

### Quick contrast check rules

| Pair Type | Target |
|---|---|
| Body text on white bg | >= 4.5:1 (use near-black, not pure black) |
| Body text on light gray bg | >= 4.5:1 |
| White text on blue primary | check — many blues fail at 4.5:1 |
| Placeholder text | >= 4.5:1 (if it conveys meaning) |
| Disabled text | no requirement, but do not use for critical info |
| Focus ring | >= 3:1 against adjacent color |

## 60-30-10 Color Distribution

| Role | Share | Typical Hue | Use For |
|---|---|---|---|
| Dominant (neutral) | 60% | gray / off-white / near-black | page background, large surfaces |
| Secondary (brand/structure) | 30% | muted brand hue or neutral dark | cards, headers, secondary UI, borders |
| Accent (action) | 10% | saturated brand hue | primary buttons, links, focus rings, active states |

### Example (light mode, blue brand)

| Role | Color | Approx Hex | Share |
|---|---|---|---|
| Dominant | Off-white background | #FAFAFA | 60% |
| Secondary | Dark text / slate cards | #1F2937 / #FFFFFF | 30% |
| Accent | Blue primary action | #2563EB | 10% |

### Example (dark mode, blue brand)

| Role | Color | Approx Hex | Share |
|---|---|---|---|
| Dominant | Near-black surface | #121212 | 60% |
| Secondary | Light text / elevated cards | #E5E7EB / #1E1E1E | 30% |
| Accent | Lighter blue accent | #60A5FA | 10% |

## Palette Construction Steps

1. Pick a base hue (brand color)
2. Generate a monochromatic ramp: 9–11 steps, lightness from 95% down to 15%
   (use OKLCH L steps of ~10% per level)
3. Pick neutral ramp: warm or cool grays, 9 steps from #FFFFFF to #111111
4. Add semantic colors: success (green), warning (amber), error (red), info (blue)
   — each as a 5-step ramp
5. Assign semantic roles: primary, on-primary, surface, on-surface, muted, border
6. Test every text/background pair for >= 4.5:1 contrast

### Tailwind-style ramp structure (9 steps per hue)

| Step | Lightness (OKLCH) | Use |
|---|---|---|
| 50 | 97% | hover-subtle, subtle backgrounds |
| 100 | 93% | active-subtle, tinted backgrounds |
| 200 | 85% | borders, subtle dividers |
| 300 | 75% | disabled, placeholder |
| 400 | 65% | secondary text |
| 500 | 55% | default primary |
| 600 | 48% | primary hover |
| 700 | 40% | primary active |
| 800 | 32% | dark mode primary |
| 900 | 25% | deep dark surfaces |

## Dark Mode Conversion Rules

| Token | Light Mode | Dark Mode | Conversion Note |
|---|---|---|---|
| Background / surface | L: 95–98% | L: 5–15% | not pure black; use #121212 not #000000 |
| Surface variant | L: 90% | L: 20% | elevated card surfaces |
| On-surface text | L: 10–15% | L: 85–95% | near-white, not pure #FFFFFF |
| Muted text | L: 45–55% | L: 60–70% | desaturated |
| Primary brand | L: 50–55% | L: 65–75% | lighter AND less saturated on dark |
| On-primary | L: 100% (white) | L: 10–15% (dark) | swap for contrast |
| Border | L: 85–90% (black alpha) | L: 25–30% (white alpha) | use white at low alpha, not light gray |
| Elevation overlay | none | +5% white per elevation level | Material M3 tonal surface overlay |

Critical: do NOT simply invert hex values. Inverting #000000 to #FFFFFF creates
harsh contrast and eye strain. Dark mode surfaces should be at 5–20% lightness,
not 0%.

## Common Accessible Color Pairs (>= 4.5:1)

| Text Color | Background | Ratio | Use |
|---|---|---|---|
| #1F2937 (gray-800) | #FFFFFF | 14.1:1 | body text on white |
| #FFFFFF | #1D4ED8 (blue-700) | 8.6:1 | white on blue button |
| #FFFFFF | #B91C1C (red-700) | 7.2:1 | white on error |
| #FFFFFF | #15803D (green-700) | 7.1:1 | white on success |
| #111827 (gray-900) | #F3F4F6 (gray-100) | 15.3:1 | dark on light gray |
| #E5E7EB (gray-200) | #111827 (gray-900) | 12.6:1 | light on dark |
| #9CA3AF (gray-400) | #111827 (gray-900) | 5.9:1 | muted text on dark (passes AA) |

Pairs to AVOID (fail AA):

| Text Color | Background | Ratio | Problem |
|---|---|---|---|
| #9CA3AF | #FFFFFF | 2.7:1 | too light for body text |
| #3B82F6 | #FFFFFF | 3.6:1 | blue on white fails normal text |
| #22C55E | #FFFFFF | 1.9:1 | green too light |
| #FBBF24 | #FFFFFF | 1.3:1 | yellow nearly invisible |

## Color Temperature and Saturation Guidelines

| Surface Type | Saturation | Example |
|---|---|---|
| Backgrounds / surfaces | low (desaturated) | neutral grays, off-whites |
| Secondary UI | low-medium | muted brand tints |
| Accents / CTAs | high (saturated) | vivid brand color |
| Error states | medium-high | clear red, not pastel |
| Success states | medium | confident green, not neon |

Rule: desaturate large surfaces, saturate small accents. A page that is 60%
saturated color is overwhelming.

## Sources

- WCAG 2.1 contrast ratios: W3C WCAG 2.1, Techniques for WCAG 2.1
- Material Design 3 color system: m3.material.io/styles/color
- OKLCH perceptual uniformity: Bjorn Ottosson's OKLCH work; oklch.org; Front-End Checklist
- 60-30-10 rule: widely cited UI/interior design principle, confirmed by UXPin and multiple design system references
- Dark mode surface values: Material Design dark theme guidance (m2.material.io/design/color/dark-theme.html)
