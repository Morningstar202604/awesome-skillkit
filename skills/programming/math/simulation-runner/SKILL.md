---
name: simulation-runner
description: "Run simulations: parameter sweeps, Monte Carlo, sensitivity analysis (OAT), and stress testing of model solutions. Use after model is solved, to test robustness under varying conditions. 当用户要求 跑仿真 / 蒙特卡洛模拟 / 敏感性分析 时使用。"
license: Apache-2.0
compatibility: Requires numpy, random. No external solver needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Simulation Runner

Parameter sweeps, Monte Carlo, and sensitivity analysis.

## When to Use

- Model is solved, need to test robustness
- Want to see how output changes when input varies (parametric study)
- Need probability distributions (Monte Carlo)
- Identify which parameters matter most (sensitivity)

## Three Modes

### 1. Parameter Sweep
```bash
python3 simulation.py --spec model.json --param rate --range 0.1 5.0 --steps 10
```
Sweeps one parameter across a range, records objective values.

### 2. Monte Carlo
```bash
python3 simulation.py --monte-carlo --n 10000 --mu 0 --sigma 1 --threshold 2
```
Generates N random samples, computes P(exceed threshold), quantiles.

### 3. Sensitivity (OAT)
```bash
python3 simulation.py --sensitivity rate,noise,decay --perturbation 0.1
```
One-at-a-time: perturb each param ±10%, measure output change.

## Output

```json
{
  "mode": "monte_carlo",
  "n": 10000,
  "mean": 0.0012,
  "std": 0.9987,
  "p95": 1.6449,
  "p_exceed": 0.0228,
  "threshold": 2.0
}
```

## References

- [references/mc-theory.md](references/mc-theory.md) — variance reduction, convergence rates