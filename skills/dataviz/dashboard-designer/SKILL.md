---
name: dashboard-designer
description: >
  Profile a CSV, then recommend and generate a dashboard: infer column types
  and distributions, propose a KPI-plus-chart layout with reasons, and build a
  self-contained single-file HTML dashboard whose charts are inline SVG with no
  CDN or network dependency. Use when the user asks to build a dashboard /
  data board / visualize this CSV / analyze data into charts / generate an HTML report /
  build a dashboard / visualize this CSV / make a data report / create an HTML dashboard /
  data visualization / dashboard / charts / reporting. Do NOT use
  for choosing a single chart type without building anything (use
  chart-recommender), for academic publication figures (use pub-plotter), or for
  statistical modeling.
license: Apache-2.0
compatibility: Requires Python 3.8+; the script is stdlib-only. The HTML output has zero external dependencies and works offline.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: dataviz
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Dashboard Designer

Given a CSV, walk the three stages "**profile → design → generate**": first map out each column's type, missingness, and distribution,
then recommend how many KPI cards, which charts to draw, and why, and finally produce a
**self-contained single-file HTML** — the charts are inline SVG with server-computed coordinates hardcoded,
so it opens fine offline, on an intranet, or in an offline delivery.

Core judgment: **profile before drawing**. Skipping `inspect` and going straight to `build` is
choosing chart types from columns of unknown type and unknown missingness — the most common failure point of dashboards.

This skill **does not** decide individual chart types for you (use `chart-recommender` to look up the lexicon),
**does not** do statistical modeling, and **does not** produce paper-grade figures (use `pub-plotter`).

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| CSV file | Yes | — | Auto-detects delimiter (`,` `;` `\t` `\|`) and encoding |
| Dashboard title | No | `<filename> data dashboard` | Shown in the page H1 |
| Output path | No | `dashboard.html` | Single file, opens on double-click |
| Audience and scenario | No | General | Decides the KPI card count and first-screen information density |
| Color preference | No | Built-in qualitative palette | Say so if you already have brand colors |

When inputs are missing, ask for all at once:

> Please provide: ① where is the CSV? ② who is this board for, and what question does it answer (the more specific the better)?
> ③ the output file name (defaults to dashboard.html)? ④ are there KPIs that must appear?

## Pre-flight Self-check

Run each item; on any failure → take the stated action:

```bash
# 1. Python version
python3 --version
# expect: Python 3.8+ (uses statistics.fmean and modern syntax beyond walrus). Fail → STOP.

# 2. The script is available
# python3 scripts/dashboard.py --help >/dev/null && echo "script ok"
# expect: script ok. Fail → check the scripts/ path.

# 3. The CSV is readable and non-empty
head -3 <data.csv> && wc -l <data.csv>
# expect: to see the header and data rows; 0 rows → the script reports "empty file"; ask the user for the data first.

# 4. The output directory is writable
ls -d "$(dirname <out.html>)" >/dev/null && echo "outdir ok"
# expect: outdir ok. Fail → create the directory or change the path; do not write to a read-only location.
```

## Workflow

### Step 1: Profile the CSV

```bash
python3 scripts/dashboard.py inspect assets/sample.csv   # bundled sample CSV; replace with your real data.csv
```

Outputs each column's **type inference** (numeric / date / categorical / text), missingness rate, and unique-value count;
numeric columns carry min / max / mean / median / q1 / q3, date columns carry the value range,
and categorical columns carry the top 3 frequencies.

- **Expected**: one profile line per column, like
  `revenue  numeric  5.7%  1019  min=-747.13 max=9.3w mean=4.9w …`.
- **On failure**: reports "cannot decode" → have the user re-save as UTF-8;
  all columns are `text` → the data may not be comma-separated; confirm the delimiter.

### Step 2: Read the Recommendation

```bash
python3 scripts/dashboard.py recommend assets/sample.csv
```

Outputs a Markdown design plan: **KPI card table** + **chart plan table** (with priority and reasons) +
**ASCII layout diagram** + **data caveats**.

The recommendation rules are explainable; do not treat them as a black box:

| Column feature | Recommendation | Why |
|---|---|---|
| Date column + numeric column | Line chart (main chart) | Trend is the first expression of a time series |
| Categorical column + numeric column | Bar chart (side chart) | Compare magnitudes; switch to horizontal bars for long labels or many categories |
| Two or more numeric columns | Scatter plot (optional) | Correlation preserves the raw distribution, beating any aggregation |
| Categorical columns only | Bar chart (count) | Frequency is the only informative aggregation |
| No usable columns | Detail table | State honestly that no chart can be produced; do not force it |

**Data caveats** are the key output of this section and proactively flag three traps:
missingness ≥1% (state that aggregation excluded empty rows; must be labeled),
>20 categorical values (plot only the top 12, fold the rest into "Other"),
and a max value over 20× the median (right-skewed; plotting directly gets squashed by outliers — suggest a log axis or truncation with a label).

- **Expected**: tabular output, every row with "why this choice."
- **On failure**: you disagree with a recommendation → keep the script's conclusion but explain your adjustment and reason at delivery;
  do not silently change what the user sees.

### Step 3: Generate the HTML

```bash
python3 scripts/dashboard.py build assets/sample.csv --out dashboard.html --title "Quarterly sales board"   # bundled sample
```

Produces a single-file HTML: KPI cards + grid-layout charts + a top-200-row detail table + a data-notes section.

- **Expected**: outputs `bytes` / `rows` / `kpis` / `charts`, and
  **`external: 0 external references`** — this line is the self-containedness assertion, not decoration.
- **On failure**: if `external` is not 0, an external resource was pulled in,
  violating this skill's offline guarantee, and must be rolled back.

### Step 4: Render Verification (do not just look at the exit code)

```bash
# when a browser is available, screenshot or at least check for no console errors
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1200,'height':1400})
    pg.goto('file://$PWD/dashboard.html')
    print('svg:', pg.evaluate('()=>document.querySelectorAll(\"svg\").length'))
    pg.screenshot(path='preview.png', full_page=False)
    b.close()
"
```

- **Expected**: the `svg` count equals the `charts` count reported by `build`; in the screenshot, titles do not overlap the
  tick marks, and axis labels are not scientific notation like `8e+06`.
- **On failure**: no browser → fall back to checking the count of `<svg` in the HTML and
  `external: 0`; still report these two items — do not just say "generated successfully."

### Step 5: Deliver

Explain four things: the file's **absolute path**, the data scale and column-type distribution,
the `external: 0` reported by `build` (offline-ready), and every item in the **data caveats**.
Remind the user: changing the data requires re-running `build`; the HTML itself contains no data source and is a pure snapshot.

- **Expected**: the delivery note covers the four items above, and `external: 0` and the data caveats are relayed item by item.
- **On failure**: the absolute path is unavailable (the user's environment differs from the generation environment) → use `python3 -c
  "import os;print(os.path.abspath('<out>'))"` to print it, then give it; `external` is not 0 →
  do not deliver; return to step 3 to hunt down the external reference source (this skill promises zero external dependencies).

## Delivery Standards

- Artifacts: a self-contained `dashboard.html` that opens on double-click.
- Location: the user-specified `--out` path; defaults to `dashboard.html` in the current directory.
- Integrity verification (do at least the first two):
  - `build` outputs `external: 0`;
  - the count of `<svg` in the HTML equals the `charts` count;
  - with a browser, screenshot to confirm titles do not overlap ticks and numeric formatting is readable.
- The delivery note must relay the full "data caveats"; missing or right-skewed data left unsaid counts as incomplete.

## Failure Handling Table

| Symptom / error | Cause | Action |
|---|---|---|
| `CSV does not exist: ...` | The path is mistyped or the file was not uploaded | Check the path; do not treat `.xlsx` as CSV directly |
| `cannot decode ...; please re-save as UTF-8` | Non-UTF-8/GBK encoding (e.g. UTF-16) | Have the user re-save as UTF-8; this script already tries utf-8-sig/utf-8/gbk/latin-1 |
| `... is an empty file` | Zero bytes or only newlines | Confirm the data source with the user |
| All columns judged `text` | The delimiter is not a comma and sniffing failed | Convert to standard CSV (comma-separated); single-column data should not produce a dashboard anyway |
| A numeric column misjudged as text | The column mixes units (`1,200 yuan`) or has odd thousands separators | Clean out the units and rerun; `to_float` only handles thousands separators and percent signs |
| The chart area is blank | SVG height set to 0, or all data filtered out | Run `inspect` to confirm the column has valid values; empty columns render as a "no valid data" placeholder |
| Axis labels show `8e+06` | Scientific-notation formatting was used | Use `fmt_num`'s "ten-thousand / hundred-million" abbreviation; if it recurs, the formatting was broken |
| The title overlaps the ticks | The title is at the same height as the Y axis's top tick | The title must own the top color band (`PAD_T` leaves headroom); this is a known pitfall |
| All bars are nearly the same height | The numeric difference between categories is <25%, so height carries no information | The script adds a "read the values" note; if needed, switch to a table or add a difference column |
| The user's machine cannot open the charts | It once referenced a CDN, which fails offline | This skill forbids external dependencies; confirm `external: 0`; inline SVG is unaffected by the network |

## References

- `references/sources-and-methodology.md` — the type-inference thresholds, the trade-offs in formatting and self-contained
  design, and the public sources for the grammar of graphics and the palette.
- `scripts/dashboard.py --help` — the three subcommands inspect / recommend / build.
- Related skills: `chart-recommender` (the deep lexicon for chart-type choice),
  `pub-plotter` (paper-grade figures), `excel-assistant` (table cleaning).
