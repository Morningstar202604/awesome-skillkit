# Layout and Chart Rules: Type Hierarchy · Information Density · Chart Decision Tree (layout-and-chart-rules)

> "Ugly slides" are 90% a matter of layout detail, not aesthetic talent. This table nails down the quantifiable rules: font sizes, information per slide, and which data suits which chart.
> Iron rule: one idea per slide; the audience gets the point within 3 seconds; body text must be readable from the back row of the projection hall.

## 1. Type hierarchy table (16:9 full-screen projection baseline)

| Element | Minimum size | Recommended range | Notes |
|------|---------|---------|------|
| Cover title | 36pt | 40-60pt | Largest text on the page; holds only the title |
| Section-divider title | 32pt | 36-48pt | Pacing beats between chapters; large text, little content |
| Slide title | 24pt | 24-32pt | Top of every slide; **use a conclusion sentence** ("Revenue up 40%", not "Revenue status") |
| Body / bullets | 18pt | 18-24pt | **Below 18pt it's unreadable in projection** |
| Chart axis labels / legend | 14pt | 14-18pt | Scale down with the body but no smaller than 14 |
| Footnote / source / page number | 10pt | 10-12pt | The audience needn't read it; just know the source exists |

**Line and character count**: ≤6 lines of body per slide (bullets), ≤15 Chinese characters per line (the 6×15 rule). Over → split slides or move to speaker notes.

## 2. Three information-density tiers (set the tier before laying out)

| Tier | Content per slide | Fits |
|------|---------|------|
| Statement slide | 1 big number / 1 conclusion + minimal decoration | Key turning points, fundraising pitches |
| Standard slide | Title + 3-5 bullets or 1 chart | Most slides |
| Comparison slide | Two-column comparison table / before-after contrast | Option comparison, competitive analysis |

- **One visual focus per slide**: either the chart is the hero or the big type is the hero; don't let both compete.
- Put the script in the notes area: the words on the slide are for the audience to scan; full sentences go in speaker notes.

## 3. Chart-selection decision tree (which data suits which chart)

```
What does the data need to express?
├─ Comparison ▸ few categories → bar chart (horizontal bars when category names are long)
│        ▸ comparison with a time dimension → grouped bar chart
├─ Trend ▸ line chart (≤5 lines; beyond that, split charts or add interactive highlighting)
├─ Share ▸ ≤5 parts → donut chart (use pie sparingly: angle comparison is hard for the eye)
│        ▸ multi-period share change → 100% stacked bar (don't use multiple pies)
├─ Correlation ▸ scatter plot (bubble size = third dimension)
├─ Funnel/conversion ▸ funnel chart (conversion rate) / flowchart (step dependencies)
├─ Ranking ▸ horizontal bars in descending order (always sort; unsorted bars are a disaster)
└─ Single metric ▸ big number + ring progress (don't pad with a chart)
```

**Chart discipline**:
- The bar-chart y-axis **starts at 0** — a truncated axis is visual lying.
- Data labels only on key points (highest/lowest/latest); labeling everything = labeling nothing.
- One message per chart; write the conclusion directly as the chart title ("Q3 South China drove 45% of the growth")
- Dual-axis charts are risky; the audience can't tell which line belongs to which axis.

## 4. Alignment and grid

- Uniform margins across the whole deck (suggest 1.2cm top/bottom, 1.5cm left/right as one set, aligned on every slide).
- Only three legal alignment states: left-aligned (default) / centered (cover and section dividers) / table numbers right-aligned.
- Consistent spacing for like elements: bullet spacing, chart-to-title spacing, uniform across the deck (a 2px gap the audience can't name but feels as messy).
- Put related content close, pull unrelated content apart — spacing itself is grouping information (Gestalt proximity principle).

## 5. Color and contrast

| Rule | Baseline |
|------|------|
| Body contrast | WCAG AA: contrast ≥4.5:1 (dark gray #333 on white ✓; light gray #999 on white ✗) |
| Deck's main color | 1 primary + 1 accent + grayscale, **plus at most 1 semantic red/green** (up/down, success/failure) |
| Chart series colors | Same chart series uses a single-hue lightness ramp; same category across charts uses the same color (Q1 blue → Q2 forever blue) |
| Dark background, white text | Contrast still ≥4.5:1; projectors are dim, so bump the font size one notch on dark-background slides |

- Give the accent color only to the most important thing: at most one accent-colored text block per slide.
- Don't use a clashing red/blue/green/yellow set — that's a patch for low contrast, not a color scheme.

## 6. Negative list (the most common failures we've seen)

- **Whole paragraphs on screen**: a 200-character paragraph pasted onto a slide → split into 3-4 bullets, verb-led.
- **Titles state the topic, not the conclusion**: "Sales status" → "East China sales exceeded target by 23%"
- **Overloaded text**: >40 Chinese characters per slide → split or delete
- **Rainbow charts**: 7 colors in one chart → single-hue ramp + highlight the key series
- **3D charts / shadows / gradients**: perspective distorts numeric perception; all banned.
- **Fancy fonts / script fonts**: projection blurs the glyph; use a system sans-serif / Source Han Sans.
- **Missing page numbers**: in a review, "turn to page 12" with no page number = disaster.
