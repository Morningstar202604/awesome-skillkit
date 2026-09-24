---
name: simulation-runner
description: "Run simulations: parameter sweeps, Monte Carlo, one-at-a-time (OAT) sensitivity analysis, and stress-testing of a model's solution. When to use: the model is solved and you need to test robustness under varying conditions — e.g. running a simulation, Monte Carlo simulation, sensitivity analysis, or a parameter sweep. Do NOT use for deterministic solving (use model-solver) or for production-grade load testing."
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

## Input Checklist

| Input | Required | Description |
|------|------|------|
| spec | No | Model-spec JSON (read by parameter sweep / sensitivity) |
| mode | No | `sweep` / `monte-carlo` / `sensitivity` (determined by parameters); default auto |
| output | No | Write results to a file; default stdout |

When missing, ask all at once: "Please provide: (1) the model or parameters to test (spec path, or give parameters directly in the command). Everything else uses defaults."

## Pre-flight Checks

```bash
python3 --version
python3 -c "import numpy; print('numpy', numpy.__version__)"
test -f scripts/simulation.py && echo "OK script present"
```

- Expected: version number printed; `numpy <version>` printed; the script exists.
- On failure: missing numpy → `pip install numpy`; script missing → STOP and report.

## Workflow

### Step 1: Parameter Sweep

```bash
python3 scripts/simulation.py --spec model.json --param rate --range 0.1 5.0 --steps 10
```

- Action: sample `--steps` points along `--param` between `--range LO HI`, recording the objective value.
- Expected: output a sequence of objective values corresponding to each sampled point.
- On failure: `--range` needs two floats → supply LO HI; the spec lacks the `--param` field → confirm the field name.

### Step 2: Monte Carlo

```bash
python3 scripts/simulation.py --monte-carlo --n 10000 --mu 0 --sigma 1 --threshold 2
```

- Action: generate `--n` random samples (mean `--mu`, std `--sigma`), and compute P(exceeding threshold) and quantiles.
- Expected: output `mean` / `std` / `p95` / `p_exceed` / `threshold`.
- On failure: anomalous result (e.g. p_exceed not in 0~1) → check the `--sigma`/`--threshold` magnitudes.

### Step 3: Sensitivity Analysis (OAT)

```bash
python3 scripts/simulation.py --sensitivity rate,noise,decay --perturbation 0.1
```

- Action: perturb each parameter individually by ±`--perturbation` (default 0.1 = 10%) and measure the output change.
- Expected: output a sensitivity ranking of each parameter.
- On failure: a parameter name isn't in the spec → align the `--sensitivity` list with the spec fields.

## Output Format

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

## Parameter Cheat Sheet

| Parameter | Values | Description |
|------|------|------|
| --spec | file path | Model-spec JSON |
| --param | name | Target parameter to sweep |
| --range | LO HI | Two floats, the sweep interval |
| --steps | integer | Number of sample points, default 10 |
| --monte-carlo | flag | Enable Monte Carlo |
| --n | integer | Number of samples, default 10000 |
| --mu / --sigma | float | Default 0 / 1 |
| --threshold | float | Threshold, default 0 |
| --sensitivity | list of names | OAT parameters |
| --output | file path | Optional, write results |

## Failure Handling Table

| Symptom / error code | Cause | Action |
|------------|------|------|
| Wrong number of `--range` arguments | LO HI not given | Supply two floats |
| `p_exceed` out of range | Magnitudes don't match | Re-check `--sigma`/`--threshold` |
| Parameter not in spec | Name misspelled | Align `--sensitivity` with the spec fields |
| Repeated simulation results aren't reproducible | Random seed not fixed | Explicitly fix the seed and record it in the output; rerun twice and compare |
| Too many sweep points to finish | The parameter grid has no step cap | First use a coarse grid to locate sensitive regions, then refine around them |
| `p_exceed` is constantly 0 or 1 | The threshold is far from the distribution's support | First look at the distribution range, then set the threshold accordingly and rerun |

## Delivery Criteria

- Definition of success: the output JSON contains `mode` and the corresponding statistics, with finite numerical values.
- Artifact naming: `sim_<mode>.json` (or specified by `--output`).
- Save location: current working directory or the `--output` path.
- Completeness verification: `python3 -c "import json; json.load(open('sim_monte_carlo.json'))"` confirms it parses and has all fields.

## References

- references/mc-theory.md — read for variance reduction, convergence rates, and OAT theory
