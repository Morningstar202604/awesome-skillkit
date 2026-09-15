---
name: figure-maker
description: "Generate paper-ready charts (bar / line / boxplot) from a results JSON via matplotlib, saving PDF/PNG. Use when the user asks 画实验结果图 / 论文图表 / results plot. 当用户要求 把实验数据画成图 时使用。 heatmap is NOT implemented yet and returns an honest 'unsupported' status. Do NOT use for neural-network structure diagrams (use neural-net-draw)."
license: Apache-2.0
compatibility: Requires matplotlib (pre-installed in this repo's environment); input is a results JSON file.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Figure Maker

Turn an experiments results JSON into publication charts.

## When to Use

- Plotting bar/line/box comparisons from experiment-runner output
- Generating fig1.pdf style assets for a LaTeX draft

## Quick Use

```bash
python3 scripts/figure_maker.py --data results.json --type bar --output fig1.pdf
python3 scripts/figure_maker.py --data results.json --type line --output fig2.png
```

## Supported Types

`bar` / `line` / `boxplot` are implemented. `heatmap` is accepted by the CLI
but returns `status: unsupported` on purpose — do not force it.

## Chain Position

上游接 experiment-runner 的 results.json；同族图表任务也可走
pub-plotter（期刊风格更强）。图完成后进 latex-formatter 组装，
或用 arch-diagram 补架构图。
