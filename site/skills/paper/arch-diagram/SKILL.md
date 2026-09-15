---
name: arch-diagram
description: "Generate paper-style architecture/framework diagrams as TikZ (LaTeX) plus editable SVG: pipelines, block stacks, layer stacks. 学习自 torchdiagram / archscope / PlotNeuralNet. Use when the user asks 画架构图 / 方法总览图 / framework diagram. Do NOT use for data charts (use figure-maker)."
license: Apache-2.0
compatibility: Stdlib only; outputs TikZ source and SVG, no LaTeX compile required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Arch Diagram

Method-overview diagrams for the "Model Architecture" figure.

## When to Use

- Drawing the pipeline figure for section 2 of a paper
- Block/stack diagrams with labeled arrows

## Quick Use

```bash
python3 scripts/arch_diagram.py --type pipeline --blocks "Encoder,Decoder,Head" --output arch
python3 scripts/arch_diagram.py --type layers --layers "768,3072,768" --format tikz
```

## Output

TikZ code (paste into LaTeX) and an editable SVG.

## Chain Position

与 figure-maker / pub-plotter 并列的图源之一；产物统一进
latex-formatter 组装。网络结构图（神经元级）移交 neural-net-draw。
