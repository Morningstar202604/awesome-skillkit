---
name: chart-recommender
description: >
  Choose the right chart for a dataset before drawing anything: read the data
  shape and the analytical intent, look up the selection lexicon, compare two or
  three candidate chart types with their trade-offs, and emit a drawing spec
  covering axes, legend, annotations, and number formatting. Use when the user
  asks to what chart should this data use / how do I choose a chart type /
  help me pick a chart / is this pie chart appropriate / how best to visualize
  this data / which chart should I use / help me pick a visualization / is a pie chart ok here /
  data visualization / charts / matplotlib / D3 / reporting / dashboard. Do NOT use for actually building a
  dashboard file (use dashboard-designer), for publication figures (use
  pub-plotter), or for statistical analysis of the data.
license: Apache-2.0
compatibility: Prompt-only, no runtime required; the lexicon is a local Markdown file.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: dataviz
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Chart Recommender

Answer one question **before** touching a pen: which chart should this data use. The method is three steps —
read the data shape and the **analytical intent**, look up the lexicon to fix the chart type, give 2-3 options with their costs compared,
and finally output an executable **drawing spec** (how to label axes, where the legend goes, whether to annotate, how to format numbers).

Core judgment: **intent comes first, then the chart type**. "I have a sales dataset" is not enough to pick a chart;
"I want to show that revenue in East China is declining" is. If you cannot get the intent, ask — do not assume for the user.

This skill **only gives options and does not draw**. To produce a deliverable dashboard file, use `dashboard-designer`;
to produce paper-grade figures, use `pub-plotter`; to do statistical analysis on the data itself, that is a different job.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| **Analytical intent** | Yes | — | "what you want the reader to see," one sentence |
| Data shape | Yes | — | Column count and types (numeric / categorical / temporal / geographic), order-of-magnitude row count |
| Audience | No | General | Decides information density and whether explanatory annotations are needed |
| Output medium | No | On-screen document | Big screen / print / mobile affects color and label strategy |
| Known candidate chart type | No | Supplied by this skill | When the user already leans toward a type, focus on evaluating whether it fits |

When inputs are missing, ask for all at once:

> Please provide: ① what conclusion do you want the reader to draw after seeing the chart? ② what columns does the data have, what type is each,
> and roughly how many rows? ③ who is it for (peers / the boss / the public)? ④ print or on screen?
> ⑤ do you have a chart type in mind (if so, I'll focus on evaluating whether it fits)?

## Pre-flight Self-check

Run each item; on any failure → take the stated action:

```bash
# 1. The lexicon is in place (this skill's only dependency)
test -s references/chart-selection.md && echo "lexicon ok"
# expect: lexicon ok. Fail → restore the lexicon file first; recommending from memory without it will miss the taboo items.

# 2. Spot-check keyword coverage (confirm the lexicon content is complete)
grep -c "^|" references/chart-selection.md
# expect: >=40 lines of table content. Fail → the lexicon was truncated; complete it before running.

# 3. Is the intent clear (no command needed; ask yourself)
# 「Does the user want to compare / see a trend / see composition / see correlation / see distribution / see flow / see space」— which one?
# Cannot answer → go back to the input checklist and re-ask ①; do not start recommending.
```

## Workflow

### Step 1: Extract the Data Shape

Before looking at the data, look at its **structure**; normalize the user's description with this table:

| Element | What to ask | Example |
|---|---|---|
| Number of dimensions | How many columns carry the expression | time × numeric (2D) |
| Column types | Is each column numeric/categorical/temporal/geographic | date + region (cat) + revenue (num) |
| Cardinality | How many values in a categorical column | 6 regions, 480 stores (huge gap) |
| Sample size | How many rows | 200 rows vs 500k rows (decides the downsampling strategy) |
| Missingness | Are there holes | Revenue missing 6% → must note it on the chart |

- **Expected**: a small "dimensions × types × cardinality × sample size" table.
- **On failure**: the user only says "there's an Excel file" → ask via the input checklist in one go; do not guess.

### Step 2: Fix the Intent and Look Up the Lexicon

Classify the intent into one of seven types, then look up the mapping in section 2 of `references/chart-selection.md`:

| Intent | Look up in the lexicon | First choice |
|---|---|---|
| Compare magnitudes | Section 2, data-type mapping table | Bar chart |
| See a trend | Same table (time + numeric row) | Line chart |
| See composition | Same table (composition/hierarchy row) | Stacked bar / pie (≤5 categories) |
| See correlation | Same table (2 numeric row) | Scatter plot |
| See distribution | Same table (1 numeric row) | Histogram / box plot |
| See flow | Same table (process/conversion row) | Funnel / Sankey |
| See space | Same table (geographic row) | Choropleth map |

- **Expected**: hit a "recommended chart type" while also reading the same row's "taboo" column.
- **On failure**: the intent is not unique (wants both trend and composition) → split into two charts,
  or choose small multiples; **do not** force it with a dual Y axis (see lexicon section 5, item 2).

### Step 3: Give 2-3 Options and Compare Costs

At least two options, each with its **cost** spelled out:

```markdown
Option A: line chart (recommended)
- Pros: the time trend is clearest; the reader can read inflection points and slope changes
- Cost: more than 5 series tangle together; over 3 series, suggest small multiples
Option B: grouped bar chart
- Pros: the value at each time point can be compared directly by length, more precise than a line
- Cost: with >15 time points the bars are too dense and the trend line is broken
Option C: area chart
- Pros: emphasizes the cumulative feel of the total
- Cost: with multiple series the lower layers are occluded; only suits a single series
```

- **Expected**: 2-3 options, each with a pros and a cost column; clearly state which is recommended.
- **On failure**: cannot think of a third option → two is enough; do not pad;
  the options must be genuinely different, not "a line chart (with a different color)."

### Step 4: Emit the Drawing Spec

Settle each item per the lexicon's section 7 checklist; a missing item means the delivery is incomplete:

| Spec item | This run's value |
|---|---|
| Axes | X axis by date ascending; Y axis starts at 0 (required for bars; a line may truncate but must be labeled) |
| Units | Y axis labeled "ten-thousand yuan"; use a ten-thousands-unit shorthand for large numbers, not scientific notation |
| Legend | Direct on-chart labels (≤5 series); beyond that, switch to small multiples |
| Annotations | Mark the peak date and policy-change point (with a vertical reference line) |
| Sorting | Categorical axis descending by value (compare-magnitude case); time axis fixed ascending |
| Missingness | State "revenue missing 6%, excluded from the mean" |
| Color | Qualitative 5-color palette; color the emphasized series, the rest in gray |

- **Expected**: a spec table with a definite value for every item, not "it depends."
- **On failure**: an item cannot be settled (e.g. the medium is unknown) → write "TBD + two branches,"
  and explain how each branch changes.

## Delivery Standards

- Artifacts: a Markdown recommendation containing **restated intent + data-shape table + 2-3 option comparison + drawing spec table**.
- Location: usually replied directly in the conversation; when the user asks to keep a record, write a `.md` file.
- Integrity verification (three self-checks):
  - At least 2 options, each with a "cost" column;
  - The drawing spec table covers all six: axes / units / legend / annotations / missingness / color;
  - The recommendation does not touch the lexicon's section 5 error list (especially truncated Y axes, dual Y axes, 3D).
- If the recommended chart happens to be the user's known candidate, you must explicitly say "fits" or "does not fit + why,"
  and cannot skip it silently.

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| The user gives data but no intent | Missing the most critical input | Ask "what conclusion do you want the reader to draw"; if they cannot, produce two versions for the most common intents |
| The intent is "I want it all" | One chart carrying multiple intents | Split into a main chart + a side chart; say plainly that one chart cannot tell the whole story |
| The user insists on a 12-category pie chart | Pie chart mistaken for a general-purpose chart | Give a comparison chart; explain that comparing angles is less precise than comparing lengths, and a bar chart is more accurate |
| Huge categorical cardinality (e.g. 480 stores) | Showing every category is infeasible | Plot only the top 12 and fold the rest into "Other"; or switch to a distribution chart (histogram) |
| Two numeric measures with wildly different scales | Wants a dual Y axis | Prefer separate small-multiple charts; if they must share one chart, explicitly label both axes' units and colors |
| Too dense time points (>200) | Drawing point-by-point is unreadable | Aggregate to week/month; or use a line + sampled labels |
| Rows with 0 make all bars short | Scale dominated by extreme values | Point out the right skew, suggest a log axis or truncation with a label; do not silently alter the data |
| The user demands a 3D chart | Aesthetic preference | Explain that perspective magnifies near elements and produces systematic misreading; give a 2D alternative |
| Unsure whether a chart type applies | The lexicon does not cover the obscure type | Go back to visual-encoding priority reasoning: which channel does it encode with, and is the precision enough |

## References

- `references/chart-selection.md` — the chart-selection lexicon (about 137 lines):
  intent quick reference, type-mapping table, per-type suitable and counter examples, visual-encoding priority,
  12 common mistakes, three color schemes. **Steps 2, 3, and 4 all depend on it.**
- `references/sources-and-methodology.md` — the lexicon's methodology provenance and originality statement.
- Related skills: `dashboard-designer` (turns the plan into an HTML file),
  `pub-plotter` (paper-grade figures), `figure-maker` (general illustrations).
