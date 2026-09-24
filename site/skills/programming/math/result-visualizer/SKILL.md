---
name: result-visualizer
description: "Plot model results into charts (line, scatter, histogram) as PNG/SVG for reports and presentations. When to use: the model is solved or the simulation is complete and you need a visualization — e.g. plotting results, data visualization, making a chart, or drawing line/scatter/histogram charts. Do NOT use for statistical inference beyond the given results, for numerical solving (use model-solver), for formalizing the model (use model-formulator), or for heatmap/bar charts not implemented by the bundled script (build those directly with matplotlib)."
license: Apache-2.0
compatibility: Requires matplotlib. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# Result Visualizer

Turns numerical results into publication-ready figures.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| data | Yes | Path to the results JSON file (containing the series to plot) |
| type | No | `line` / `scatter` / `histogram`; default line |
| x | No | x field name for scatter plots; default t |
| y | No | y field name for scatter plots; default y |
| output | No | Output image path; default stdout path |

When missing, ask all at once: "Please provide: (1) data (results JSON path). I'll handle type/x/y/output with defaults."

## Pre-flight Checks

```bash
python3 --version
python3 -c "import matplotlib; print('matplotlib', matplotlib.__version__)"
test -f scripts/visualizer.py && echo "OK script present"
```

- Expected: version number printed; `matplotlib <version>` printed; the script exists.
- On failure: missing matplotlib → `pip install matplotlib`; script missing → STOP and report.

## Workflow

### Step 1: Choose the chart type

The script implements exactly three chart types (pass one via `--type`):

| Type | Use Case | Required input fields |
|------|----------|-----------------------|
| `line` (default) | Time series, convergence curves | `t[]`, `y[]` |
| `scatter` | Correlation, distribution | `x[]`, `y[]` (set `--x`/`--y`) |
| `histogram` | Distribution, Monte-Carlo results | `samples[]` |

> Heatmap, bar, and multi-panel subplots are NOT implemented by `visualizer.py`.
> If the user needs one of those, build it directly with matplotlib following
> `references/matplotlib-cheatsheet.md` instead of passing an unsupported `--type`.

- Action: pick the supported `type` whose fields match the data; scatter needs both `--x` and `--y`.
- Expected: a single `type` and the corresponding fields are selected.
- On failure: data non-numeric / fields missing → return to data validation; an unsupported type like `heatmap` → fall back to hand-rolled matplotlib per the note above.

### Step 2: Run the plotting script

```bash
python3 scripts/visualizer.py --data results.json --type line --output fig1.png
python3 scripts/visualizer.py --data results.json --type scatter --x t --y y
```

- Expected: an image file is generated (when `--output` is given), or stdout prints `{"output": "...", "type": "...", "rendered": true}`.
- On failure: `FileNotFoundError` → wrong data path; `KeyError` → the x/y field isn't in the JSON; missing backend → set `MPLBACKEND=Agg`.

### Step 3: Apply publication-grade styling

- Action: check the output figure against the styling conventions below.
- Expected: DPI, font size, color scheme, and grid conform to the spec.
- On failure: styling doesn't match → adjust script parameters or redraw per the cheatsheet.

| Style item | Value |
|--------|------|
| Resolution | 150 DPI for print / 72 DPI for web |
| Font size | ≥ 12 |
| Color scheme | Colorblind-safe (default tab10) |
| Grid | alpha=0.3 |
| Layout | tight_layout, no overlapping labels |

## Output Format

```json
{
  "output": "/tmp/fig1.png",
  "type": "line",
  "rendered": true
}
```

## Parameter Cheat Sheet

| Parameter | Values | Description |
|------|------|------|
| --data | file path | Required, results JSON |
| --type | line/scatter/histogram | Default line |
| --x | field name | Default t |
| --y | field name | Default y |
| --output | image path | Optional, output file |

## Failure Handling Table

| Symptom / error code | Cause | Action |
|------------|------|------|
| `FileNotFoundError` | Wrong data path | Double-check the path or return to the input checklist |
| `KeyError: 'x'` | Scatter field missing | Explicitly specify `--x`/`--y` |
| `no display / backend` | No GUI environment | Set `MPLBACKEND=Agg` and rerun |
| Non-ASCII labels render as boxes (tofu) | matplotlib's default font lacks the glyphs | Switch to English labels, or explicitly specify a system font file with the needed glyphs |
| Passing `--type heatmap` (or `bar`/`subplot`) errors out | Those types are not implemented by the bundled script | Build the chart directly with matplotlib per references/matplotlib-cheatsheet.md |
| Legend overlaps curves and is unreadable | Legend position left at default | Move the legend outside the axes or adjust `loc` and margins |

## Delivery Criteria

- Definition of success: produce a PNG/SVG and the JSON report says `rendered: true`.
- Artifact naming: `fig1.png` (or specified by `--output`; recommended to include a sequence number and type).
- Save location: `/tmp/` or a user-specified directory.
- Completeness verification: confirm with an image viewer / by reading the file header that it's non-zero bytes; check that the four style items are correct.

## References

- references/matplotlib-cheatsheet.md — read when choosing chart type, colors, and styling
