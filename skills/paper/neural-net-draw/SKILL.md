---
name: neural-net-draw
description: "Draw neural-network structure diagrams as compile-ready LaTeX TikZ from a layer-size list (e.g. 784,512,256,10). 学习自 PlotNeuralNet (25k stars). Use when the user asks 画网络结构图 / 画 CNN 层级图 / neural network diagram. Do NOT use for pipeline/block diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: Stdlib only; emits TikZ source for the PlotNeuralNet toolchain.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Neural Net Drawer

Neuron-level network diagrams in TikZ.

## When to Use

- Figure 1 of a deep-learning paper: input → hidden layers → output
- Annotating activations on a fixed topology

## Quick Use

```bash
python3 scripts/neural_net_draw.py --layers "784,512,256,10,1" --label "CNN+MLP" --output net.tex
python3 scripts/neural_net_draw.py --layers "3,8,8,2" --activation relu
```

## Output

Compile-ready TikZ source (requires the PlotNeuralNet style in your preamble).

## Chain Position

图源与 arch-diagram 互补：网络层级走本技能，模块流程走 arch-diagram。
产物统一进 latex-formatter 组装。
