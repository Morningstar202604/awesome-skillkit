---
name: experiment-runner
description: "Run reproducible experiments with fixed seeds, aggregate metrics across N runs, and apply REAL statistical tests (Welch t-test / p-value / Cohen's d / 95% CI) via scipy. Supports simulated (honest demo) and real (--metric module:func) modes; optional mlflow tracking. Use when the user asks to run experiments / run N times and average / statistical significance testing / repeat experiments / run N times with a fixed seed / reproduce an experiment / compute mean std / significance test / p-value. Do NOT use for drawing charts (hand results to figure-maker / pub-plotter)."
license: Apache-2.0
compatibility: Stdlib + scipy (falls back to pure-stdlib Welch t when scipy absent). numpy/torch seeded when installed. real mode imports user metrics via importlib. mlflow optional.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Experiment Runner

Run N times with a fixed seed, aggregate mean/std, and judge significance with **real statistical tests** (Welch t-test, p-value, Cohen's d, 95% CI).

> Honest disclosure: two modes —
> - **`--mode simulated`**: a built-in demo experiment (honestly tagged `mode: "simulated"` + `simulation_notice`); results **MUST be labeled "simulated data"**; don't write them into a paper as real results.
> - **`--mode real`**: runs the user's real metric function (`--metric module:func`, `func(seed:int)->float`) for a real two-group comparison. Only this mode yields statistical conclusions writable into a paper.
>
> Significance is always judged by `stats.p_value < alpha` (default 0.05); **no more faking a t-test with "mean exceeds a threshold"**. When `scipy` is absent it automatically falls back to pure-stdlib Welch t + normal-approximation p (still works offline), and `stats.method` honestly labels `scipy` / `stdlib-fallback`.

## Input Checklist

| Input | Required | Notes |
|------|------|------|
| mode | no | `--mode simulated` (default) / `--mode real` |
| experiment config | conditional | `--config exp_config.json` (keys `n_runs`/`seed`/`baseline_metric`/`improvement_target`) |
| metric function | real required | `--metric "mymodule:metric_fn"`, `metric_fn(seed:int)->float` |
| baseline function | real recommended | `--baseline "mymodule:baseline_fn"`; if omitted, use a fixed `--baseline-value` (single group, no comparison) |
| number of runs | no | `--n-runs 5` (default 5) |
| random seed | no | `--seed 42` (default 42) |
| output path | no | `--output results.json`; default prints to stdout |
| tracking | no | `--track` tries mlflow autolog (needs mlflow installed; silently degrades on failure) |

When missing, ask everything at once: "Please provide: ① mode (simulated/real) ② for real mode: the metric function `--metric module:func` (baseline `--baseline` or fixed value `--baseline-value`) ③ `--n-runs` ④ `--seed` ⑤ whether to save `--output` ⑥ whether to `--track` mlflow."

## Pre-flight Checks
```bash
python3 --version                                   # expect >= 3.8, else STOP
python3 -c "import scipy;print(scipy.__version__)"  # optional; if missing it uses stdlib-fallback (still works offline)
test -f scripts/experiment_runner.py && echo OK     # script missing STOP
```

## Workflow

### Step 1: Run the Experiment
```bash
# simulated (demo / offline / CI)
python3 scripts/experiment_runner.py --n-runs 8 --seed 42
# real metrics (writable into a paper)
python3 scripts/experiment_runner.py --mode real --metric "train:accuracy" \
       --baseline "baseline:accuracy" --n-runs 10 --seed 42 --output results.json
```
Expected: JSON with `mode`, `n_runs`, `results[]`, `stats{test,method,statistic,p_value,alpha,effect_size_cohens_d,ci95_diff,significant}`, `seed_backends[]`, `env`.
If it fails: `--metric` isn't in `module:func` form -> reports "real mode requires --metric module:func"; module/function doesn't exist -> ImportError; check the import path.

### Step 2: Read the Statistical Conclusion (Real Significance)
- `stats.significant == true` iff `stats.p_value < alpha`, **and you must report it together with the p-value / Cohen's d / 95% CI**; don't just write "significant".
- `stats.method == "scipy"` -> use scipy's exact result; `"stdlib-fallback"` -> pure-stdlib approximation (small-sample p is slightly conservative; note it honestly).
- Single group (no `--baseline`): only mean/std; `stats` has a `note` explaining no two-group comparison was done.
If it fails: results contradict expectations -> check `n_runs`/`seed`/the metric function's return value (it must be a float).

### Step 3: Reproducibility
Expected: `seed_backends` lists the backends actually applied (random/numpy/torch); same seed gives identical results across two runs (the script is built deterministically).
For hardware-level reproducibility, archive `env` (pip versions / CUDA availability) as well, or lock the environment with Docker/`uv`.

## Parameter Quick Reference

| Parameter | Value | Notes |
|------|------|------|
| `--mode` | `simulated` (default) / `real` | Demo / real metrics |
| `--metric` | `module:func` | required for real; `func(seed:int)->float` |
| `--baseline` | `module:func` | Baseline function; if omitted use `--baseline-value` |
| `--baseline-value` | float | Fixed baseline when no `--baseline` (single group) |
| `--config` | path | Experiment config JSON |
| `--n-runs` | int | default 5 |
| `--seed` | int | default 42 |
| `--track` | flag | Try mlflow autolog |
| `--output` | path | Results JSON output path |

## Failure Remediation Table

| Symptom / Error Code | Cause | Remedy |
|------------|------|------|
| "real mode requires --metric module:func" | real mode given no metric function | Add `--metric module:func` |
| `ModuleNotFoundError`/`AttributeError` | Wrong `--metric` import path or function name | Verify the module imports, the function is callable, and returns a float |
| `stats.method` is `stdlib-fallback` | No scipy | Acceptable offline; for precision `pip install scipy` |
| `significant` contradicts intuition | Small sample / high variance | Look at `p_value`/`cohens_d`/`ci95_diff` before judging; don't trust the boolean alone |
| Two runs with the same config disagree | Random backends weren't seeded consistently | Check whether `seed_backends` includes numpy/torch; lock the environment if needed |
| mlflow not taking effect | mlflow not installed | `--track` silently degrades with `tracking: null`; to track, first `pip install mlflow` |

## Delivery Standard

Success: `status == "complete"`; in real mode `stats.test == "welch_ttest"` and it contains `p_value`/`effect_size_cohens_d`/`ci95_diff`.
Artifact name: `results.json` (if `--output` is given).
Verification: `python3 -c "import json;d=json.load(open('<out>'));assert d['stats']['test']=='welch_ttest' and 'p_value' in d['stats']"` passes.

## References

Statistical logic is built into `scripts/experiment_runner.py`: `real_stats` (scipy -> stdlib fallback), `seed_all` (multi-backend seeding), `env_fingerprint`, `_welch_t`.

## Chain Position

Upstream connects to lit-review's baseline definitions; the produced `results.json` goes straight to pub-plotter (`--data results.json` to make figures), then into latex-formatter to assemble the paper.
