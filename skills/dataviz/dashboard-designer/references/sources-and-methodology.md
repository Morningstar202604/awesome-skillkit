# Sources & Methodology

- Skill: `dashboard-designer` (authored from scratch by awesome-skillkit, Apache-2.0).
- Positioning: the generation-side skill of the `dataviz` scenario pack. Complementary to `chart-recommender` (the selection side, pure lexicon consultation):
  this skill lands "what should be drawn" as "a deliverable file that's actually drawn."

## Methodology borrowed (ideas and taxonomy only; no text or code copied)

| Source | License | Methodology points borrowed |
|---|---|---|
| Leland Wilkinson's public concepts in *The Grammar of Graphics* | See the original book | Graphics = data + mapping + scale + geometric object + faceting; the order of "fix dimensions and measures first, then pick the geometry" |
| Grammar-of-graphics practice in general data-viz knowledge (ggplot2 / Vega-Lite public docs) | MIT / BSD | The mapping intuition of "data feature → geometric object"; how category count and label length affect geometry orientation |
| Descriptive-statistics common knowledge (quartiles, IQR, robust statistics) | Textbook-level public knowledge | Using median and quartiles to resist outliers; reporting mean and median together to expose skew |
| Public material on accessible and colorblind-friendly palettes | CC BY-SA etc. | Qualitative-palette contrast and color-vision-deficiency distinguishability requirements |
| This repo's existing skill conventions (SKILL-STANDARD-v2 under docs/) | Apache-2.0 | Skeleton sections, failure-handling tables, script subcommandization, and fallback-path requirements |

All the above sources were re-expressed as a **methodology skeleton**. `scripts/dashboard.py`'s type-inference thresholds,
the `fmt_num` number-abbreviation rules, the `nice_ticks` tick algorithm (1/2/2.5/5 × 10^k),
the inline SVG generator, and the HTML assembly template were all written from scratch.
No upstream passage, example, or code was translated, rewritten, or excerpted.

## Key design decisions (why this way)

1. **Forbid any CDN dependency; charts use server-rendered pure SVG**: the most common dashboard failure is
   opening it in an intranet/offline environment, or the page going white when some CDN happens to be down. So this skill **doesn't use** a runtime charting library like Chart.js — chart coordinates are computed on the Python side and hard-coded as SVG elements,
   making `external: 0` an assertable delivery standard.
2. **`fmt_num` uses ten-thousand/hundred-million units (CN convention) rather than scientific notation**: `8000000` via `{:g}` becomes `8e+06`,
   forcing the reader to mentally convert the order of magnitude and breaking the axis's comparison function.
3. **`PAD_T = 52` gives the title headroom**: the title and the y-axis's top tick easily stick together visually,
   a problem that only surfaced in live screenshots — reserving a 26px band at the top for the title.
4. **Alert when missingness ≥1%**: aggregate values (especially totals and means) get systematically underestimated by missingness,
   which is completely invisible on the chart and must be stated in the delivery notes.
5. **Right-skew detection (max > median × 20)**: plotting directly gets squashed into a line by outliers;
   suggest a log axis or truncate with a label; don't silently handle it, because either treatment changes the reader's interpretation.
6. **Unified number formatting**: the KPI card's main value and sub-info use the same format,
   avoiding the two-precision mismatch of "49K" next to "48990.39".

## Limitations and boundaries

- **No data cleaning**: when it finds mixed units or mixed types, it only reports, doesn't rewrite the user's raw data.
- **No statistical modeling**: only descriptive summaries and correlation scatters; doesn't compute correlation-significance or make predictions.
- **Detail tables truncated to 200 rows**: full data is delivered as CSV; HTML is only a snapshot and view.
- **Time aggregation is by day**: multiple rows on the same date take the mean; for weekly/monthly aggregation, preprocess externally.
- **Single-file size grows with row count**: `MAX_SCAN_ROWS = 50000`; very large datasets must be aggregated before being passed in.
- **Pure SVG, no interaction**: no tooltips, zoom, or drill-down; for an interactive dashboard, use
  Plotly/Dash instead (accepting their dependency and networking cost at that point).

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
