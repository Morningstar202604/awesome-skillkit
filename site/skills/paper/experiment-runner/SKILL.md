---
name: experiment-runner
description: "Run repeatable experiments from a config, collect metrics across N runs with fixed seeds, and apply basic statistical checks. Use when the user asks 跑实验 / 多次运行取均值 / 实验统计检验. Do NOT use for drawing charts (hand results to figure-maker)."
license: Apache-2.0
compatibility: Stdlib only; executes experiment logic from the given config file, no network calls.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Experiment Runner

Repeat experiments N times, aggregate results, run basic stats.

## When to Use

- Need mean/std over multiple seeds before claiming a result
- Comparing a baseline vs your method under identical conditions
- Producing a results JSON that figure-maker can plot directly

## Quick Use

```bash
python3 scripts/experiment_runner.py --config exp_config.json
python3 scripts/experiment_runner.py --config exp_config.json --n-runs 5 --seed 42
```

## Output

JSON with per-run metrics, aggregate mean/std, and pass/fail statistical checks.

## Chain Position

上游接 lit-review 的 baseline 定义；产出结果 JSON 原样交给
figure-maker / pub-plotter 画图，随后进 latex-formatter 组装论文。

## Honesty Note

实验体默认是 mock 逻辑占位（不跑真实训练）。输出顶层带 `mode: "simulated"` 与
`simulation_notice` 字段做机器可读标注；接入真实训练 harness 前，输出 MUST 标注
模拟数据，勿当真实实验结果写进论文。
