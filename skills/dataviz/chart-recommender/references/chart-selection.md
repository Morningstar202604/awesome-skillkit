# Chart Selection Lexicon

> Once you have the data characteristics, use this table to pick the chart type. Look-up order: **first fix the analytical intent (§2) → then match the chart-type applicability conditions (§3) → finally run visual encoding and taboos (§§4–5)**. This document only solves "what to draw," not "how to draw it prettily."

## Table of Contents

- [1. 30-second quick reference: intent → chart type](#1-30-second-quick-reference-intent--chart-type)
- [2. Data type → chart type mapping table](#2-data-type--chart-type-mapping-table)
- [3. Applicability conditions and counterexamples for each chart type](#3-applicability-conditions-and-counterexamples-for-each-chart-type)
- [4. Visual encoding priority](#4-visual-encoding-priority)
- [5. Common error list](#5-common-error-list)
- [6. Color schemes](#6-color-schemes)
- [7. Output specification checklist](#7-output-specification-checklist)

## 1. 30-second quick reference: intent → chart type

| What you want to say | First choice | Second choice | Never |
|---|---|---|---|
| "Who is bigger" | Bar chart | Dot plot / lollipop | Pie (>5 categories), radar |
| "How did it change" | Line chart | Area chart (single series only) | Using bars to plot 50 time points |
| "How much of the total" | Stacked bar / percentage stack | Pie (≤5 categories) | 3D pie, nested donuts |
| "Is there a relationship" | Scatter plot | Heatmap (when dense) | Dual-y-axis line |
| "What does the distribution look like" | Histogram / box plot | Violin / beeswarm | Using a single mean point to stand for the whole distribution |
| "Where does it come from / go to" | Sankey | Funnel (single chain) | A "flow" cobbled from pies |
| "Where is it" | Choropleth map | Scatter map | 3D globe |
| "How far from baseline" | Deviation bar chart | Dumbbell chart | Dual y-axis |

## 2. Data type → chart type mapping table

| Data shape | Intent | Recommended type | Alternative | Taboo |
|---|---|---|---|---|
| 1 categorical + 1 numeric | Compare magnitudes | Horizontal bar | Lollipop | Pie >5 categories, radar |
| 1 categorical + 1 numeric + time | Compare + trend | Grouped bar / line | Small multiples (facet) | Cramming 20 lines into one chart |
| 1 time + 1 numeric | Trend | Line chart | Area chart | Bar (when points are too dense) |
| 1 time + multiple series | Trend comparison | Multi-line (≤5) | Small multiples | Dual y-axis, rainbow colors |
| 1 time + positive/negative cumulative | Up/down | Waterfall | Deviation bar | Line (loses cumulative semantics) |
| 2 numeric | Correlation | Scatter | Hex binning / density contour | Line (connects unordered data) |
| 1 categorical + 1 numeric distribution | Distribution comparison | Box plot / violin | Beeswarm (small n) | Drawing only the mean bar |
| 1 numeric | Distribution shape | Histogram | Kernel density curve | Pie |
| 2 categorical + 1 numeric | Cross comparison | Heatmap | Grouped bar | 3D bar |
| 3 numeric | Multivariate relationship | Scatter matrix / bubble | Parallel coordinates | 3D scatter |
| Hierarchy + numeric | Composition | Treemap | Sunburst | Nested pies |
| Two-stage flow | Conversion | Funnel | Sankey | Stacked bar (loses order) |
| Geography + numeric | Spatial distribution | Choropleth | Bubble map | 3D globe, map without a projection note |

## 3. Applicability conditions and counterexamples for each chart type

**Bar chart** — fits: ≤20 categories, comparing magnitudes. Key points: baseline must be 0; switch to horizontal when there are many categories or long labels.
Counterexample: 12 categories as vertical bars with labels rotated 90°, forcing readers to tilt their heads.

**Line chart** — fits: evenly spaced time, emphasizing rate of change. Key points: ≤5 lines; line width > point size.
Counterexample: plotting 30 countries' 10-year data as 30 lines, the legend longer than the chart.

**Pie chart** — fits: **only when** categories ≤5 and the max/min share differ markedly, and you need to express "part of a whole."
Counterexample: a pie for 12 categories is a disaster; the eye is far worse at comparing angles and areas than lengths.
If slices are near 1/5 each, readers can't tell which is bigger — switch to a bar chart.

**Histogram** — fits: seeing the shape of a univariate distribution (bimodal, skew, outliers). Key points: bin count between
`√n` and `2∛n`; different binning can change conclusions, so always label the bin count.
Counterexample: using a histogram to compare two groups with very different sample sizes (use a density curve or normalize by proportion instead).

**Box plot** — fits: comparing multiple distributions, medium sample sizes, outliers present. Key points: must label n.
Counterexample: at n<10 the quartiles are highly unstable; use a beeswarm to plot every point instead.

**Scatter plot** — fits: correlation between two numeric columns, outlier detection. Key points: when overplotting, lower opacity or bin.
Counterexample: sorting the scatter by a column then connecting it into a line, manufacturing a trend that doesn't exist.

**Stacked chart** — fits: total changes over time and you care about composition. Key points: ≤5 categories, largest on the bottom;
when comparing category magnitudes, switch to grouped or percentage stack.
Counterexample: using a stacked bar to compare one middle category — its baseline is lifted by the categories below, so the heights aren't comparable.

**Heatmap** — fits: a cross matrix of two categorical dimensions. Key points: use a sequential color palette; missing values get their own neutral gray.
Counterexample: coloring categories with no inherent order with a gradient, implying a continuity that doesn't exist.

**Radar chart** — fits: almost only "multiple dimensions of the same entity vs itself at another time point," with ≤6 axes and the same unit.
Counterexample: multi-entity radar charts; the area changes with axis order, and the ordering can be manipulated.

**Dual y-axis** — fits: two different units that need to sit on the same time axis for comparison, with both sides' units and colors explicitly labeled.
Counterexample: putting two unrelated metrics together and manufacturing "high synchronization" fake correlation by tuning the axis ranges.

## 4. Visual encoding priority

Precision from high to low: **position > length > angle > area > volume > lightness > hue**.

| Encoding | Readable precision | Why |
|---|---|---|
| Position (scatter, dot plot) | Highest | Shared scale; distances compared directly |
| Length (bar) | High | Linear mapping; human length-ratio estimates err by ~5% |
| Angle (pie) | Medium-low | Must reconstruct the ratio in the head; small angles especially hard |
| Area (bubble) | Low | Read off by square root; doubling radius quadruples area, easy to overestimate |
| Lightness (heatmap) | Low | Relies on uniform palette perception; varies across screens |
| Hue (categorical coloring) | Distinction only | Can't express magnitude, only "different" |

Corollary: **if the same data can be shown by position, don't use area**; put a reference circle beside a bubble chart;
put "the important quantity" on the position/length channel, and hand "the secondary quantity" to color.

## 5. Common error list

1. **Truncated y-axis**: bars that don't start at 0 exaggerate differences. Lines may be truncated, but must be labeled.
2. **Dual-y-axis abuse**: axis ranges are arbitrary, manufacturing any "correlation." Don't use unless necessary.
3. **Anything 3D**: 3D pie / 3D bar perspective makes near elements look bigger, causing systematic misreading.
4. **Rainbow palette for values**: hue carries no magnitude semantics and is perceptually non-uniform; use a sequential palette for values.
5. **Coloring ordinal values as categorical**: `low/mid/high` in three unrelated hues, so readers can't see the order;
   use a single-hue lightness ramp instead.
6. **Encoding >7 categories with color**: the eye has a reliable limit on distinguishable hues; beyond that, facet or group.
7. **Redundant, conflicting double encoding**: expressing the same info with both length and color in inconsistent directions, adding confusion.
8. **Legend detached from the graphic**: too many, too far away, forcing the eye to dart back and forth; label directly on the chart when you can.
9. **Mean bar standing for a distribution**: hides bimodality, skew, and outliers; overlay error bars or switch to a box plot.
10. **Treating missing as 0**: sums and trends get systematically dragged down; leave missing blank and explain.
11. **Area/volume encoding proportion**: scaling circles by diameter rather than area, overestimating by often several times.
12. **Uneven time axis**: plotting by month but months have different day counts, or skipped months compressed to equal spacing, distorting the trend.

## 6. Color schemes

| Type | Use | Key points | Example values |
|---|---|---|---|
| Qualitative | Distinguishing unordered categories | ≤7 colors; distinguishable under color-vision deficiency; avoid red-green pairs | `#4C72B0` `#DD8452` `#55A868` `#C44E52` `#8172B3` |
| Sequential | Continuous magnitude/intensity | Single hue light to dark; perceptually uniform (e.g. viridis); no rainbow | Light `#EAF2FB` → dark `#1F4E79` |
| Diverging | Natural midpoint (0, mean, ±deviation) | Two end hues, neutral midpoint; the midpoint must be meaningful in the data | `#C44E52` ↔ `#F2F2F2` ↔ `#4C72B0` |

Supplementary rules: use neutral gray for background and grid (`#E6E9ED`), so the data is the only source of color;
when highlighting one series, render all the others in gray rather than giving each a bright color;
for print, avoid large solid fills; use outlines with light fills instead.

## 7. Output specification checklist

When giving a chart-type recommendation, also give the following specs; missing one means an incomplete deliverable:

| Item | Requirement |
|---|---|
| Axes | Label units; whether the y-axis starts at 0 and why; category-axis ordering rule (descending by value or fixed order) |
| Legend | Position; number of entries; if >7, switch to direct labels |
| Annotations | Whether key points (peak, inflection, anomaly) need callouts; data source and time range |
| Number format | Thousands separators; large numbers in ten-thousand/hundred-million units (CN convention); consistent decimal places; no scientific notation |
| Missing handling | State explicitly whether "missing data is excluded" or treated as 0 |
| Alternatives | Give 2-3 options with each one's tradeoff, and let the user choose, rather than a single answer |
