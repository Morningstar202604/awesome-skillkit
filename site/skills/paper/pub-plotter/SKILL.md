---
name: pub-plotter
description: "Publication-grade plots in SciencePlots style (IEEE / ACM / NeurIPS looks, single/double column) from a data JSON, output PDF/PNG. 学习自 garrettj403/SciencePlots (9.2k stars). Use when the user asks 期刊风格图 / IEEE 风格曲线图 / 论文绑图. Do NOT use for architecture diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: Requires matplotlib; data input is a JSON file.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Publication Plotter

Venue-styled figures without hand-tuning rcParams.

## When to Use

- Final camera-ready figures matching the venue's column width
- Consistent line/marker styling across all paper figures

## Quick Use

```bash
python3 scripts/pub_plotter.py --type line --style ieee --data data.json --output fig.pdf
python3 scripts/pub_plotter.py --type bar --style acm --data data.json --output fig.png
```

## Output

Styled PDF/PNG per call; data comes from a JSON file (experiment-runner
output works directly).

## Chain Position

与 figure-maker 并列的图源（本技能偏期刊风格定稿）；
产物统一进 latex-formatter 组装，tex-cleaner 收口提交。
