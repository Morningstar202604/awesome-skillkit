---
name: result-visualizer
description: "Plot model results: line charts, scatter plots, histograms, heatmaps. Outputs PNG/SVG for reports and presentations. Use after solving/simulating to visualize findings. 当用户要求 画结果图 / 数据可视化 / 出图表 时使用。"
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

Turn numeric results into publication-ready plots.

## When to Use

- Model is solved, need to show results visually
- Simulation output needs to be charted
- Report/PPT needs figures
- Compare multiple scenarios side-by-side

## Supported Chart Types

| Type | Use Case | Input |
|------|----------|-------|
| line | Time series, convergence | t[], y[] |
| scatter | Correlation, distributions | x[], y[] |
| histogram | Distributions, MC results | samples[] |
| heatmap | 2D parameter space | matrix[][] |
| bar | Category comparison | labels[], values[] |
| subplot | Multi-panel reports | multiple series |

## Usage

```bash
python3 visualizer.py --data results.json --type line --output fig1.png
python3 visualizer.py --data results.json --type scatter --x t --y y
```

## Output

```json
{
  "output": "/tmp/fig1.png",
  "type": "line",
  "rendered": true
}
```

## Plot Style

- 150 DPI for print, 72 DPI for web
- Font size 12+ for readability
- Colorblind-safe palette (default: tab10)
- Grid with alpha=0.3
- Tight layout, no overlapping labels

## References

- [references/matplotlib-cheatsheet.md](references/matplotlib-cheatsheet.md) — quick recipes