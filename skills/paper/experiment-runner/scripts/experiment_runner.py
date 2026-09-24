#!/usr/bin/env python3
"""Experiment Runner -- reproducible experiments + real statistical testing (SOTA upgrade).

Aligned with 2026 best practices:
  - Statistics: scipy.stats.ttest_ind (Welch) / mannwhitneyu + p-value + Cohen's d + 95% CI
    (when scipy is missing, fall back to a pure-stdlib Welch t-test + normal-approximation
    p-value, so it still works offline)
  - Reproducibility: consistently fix the python / numpy / (torch) random seeds; export the
    resolved config + environment fingerprint
  - Tracking hooks: optionally plug into mlflow / wandb (detect = autolog, no hard dependency)

Two modes:
  --mode simulated  built-in demo experiment (honestly tagged mode=simulated; MUST be labeled
                    "simulated data")
  --mode real --metric <module:func> --baseline <module:func>
                    runs the user's real metric function (func(seed:int)->float) and does a
                    real two-group comparison

Honest disclaimer: simulated mode is never treated as a real experimental result; significance
in real mode is decided by the p-value, `significant = p_value < alpha` (default 0.05) -- no
more faking a t-test with "mean above a threshold".
"""
import argparse
import importlib
import json
import math
import os
import random
import statistics
import sys
from pathlib import Path

ALPHA = 0.05


# ----------------------------------------------------------------------------
# Random seeds (reproducibility)
# ----------------------------------------------------------------------------
def seed_all(base: int):
    """Fix the python / numpy / (torch) seeds; return the list of backends used."""
    random.seed(base)
    backends = ["random"]
    try:
        import numpy as np
        np.random.seed(base)
        backends.append(f"numpy {np.__version__}")
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(base)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(base)
        backends.append(f"torch {torch.__version__}")
    except Exception:
        pass
    return backends


def env_fingerprint() -> dict:
    """Export the environment fingerprint for reproducibility auditing (no forced installs)."""
    fp = {"python": sys.version.split()[0]}
    try:
        import numpy as np
        fp["numpy"] = np.__version__
    except Exception:
        pass
    try:
        import scipy
        fp["scipy"] = scipy.__version__
    except Exception:
        fp["scipy"] = None
    try:
        import sklearn
        fp["sklearn"] = sklearn.__version__
    except Exception:
        pass
    fp["cuda_available"] = False
    try:
        import torch
        fp["torch"] = torch.__version__
        fp["cuda_available"] = torch.cuda.is_available()
    except Exception:
        pass
    return fp


# ----------------------------------------------------------------------------
# Real statistics (prefer scipy, fall back to pure stdlib)
# ----------------------------------------------------------------------------
def _mean(xs):
    return sum(xs) / len(xs)


def _var(xs, ddof=1):
    m = _mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - ddof)


def _welch_t(a, b):
    """Pure-stdlib Welch t-test: returns (t, df, p_two_sided)."""
    ma, mb = _mean(a), _mean(b)
    va, vb = _var(a, 1), _var(b, 1)
    na, nb = len(a), len(b)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return 0.0, na + nb - 2, 1.0
    t = (ma - mb) / se
    # Welch-Satterthwaite degrees of freedom
    df = (va / na + vb / nb) ** 2 / (
        (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    )
    # two-sided p-value (normal approximation; adequate for large samples; the t distribution
    # is more accurate for small samples but the stdlib has no inverse erf)
    z = abs(t)
    # approximate the standard-normal two-sided p with the error function
    p = math.erfc(z / math.sqrt(2))
    return t, df, p


def cohens_d(a, b):
    na, nb = len(a), len(b)
    sp = math.sqrt(((na - 1) * _var(a, 1) + (nb - 1) * _var(b, 1)) / (na + nb - 2))
    if sp == 0:
        return 0.0
    return (_mean(a) - _mean(b)) / sp


def real_stats(ours, baseline, alpha=ALPHA):
    """Two-group comparison, returning a real statistical conclusion. Prefer scipy; otherwise fall back to pure stdlib."""
    method = "scipy"
    try:
        from scipy import stats
        res = stats.ttest_ind(ours, baseline, equal_var=False)
        t = float(res.statistic)
        p = float(res.pvalue)
        df = (len(ours) + len(baseline) - 2)
        # 95% CI of the difference (Welch)
        diff = _mean(ours) - _mean(baseline)
        se = math.sqrt(_var(ours, 1) / len(ours) + _var(baseline, 1) / len(baseline))
        tc = stats.t.ppf(1 - alpha / 2, df)
        ci_low, ci_high = diff - tc * se, diff + tc * se
    except Exception:
        method = "stdlib-fallback"
        t, df, p = _welch_t(ours, baseline)
        diff = _mean(ours) - _mean(baseline)
        se = math.sqrt(_var(ours, 1) / len(ours) + _var(baseline, 1) / len(baseline))
        zc = 1.959963984540054  # normal 95% critical value
        ci_low, ci_high = diff - zc * se, diff + zc * se

    d = cohens_d(ours, baseline)
    return {
        "test": "welch_ttest",
        "method": method,
        "statistic": round(t, 4),
        "df": round(df, 2),
        "p_value": round(p, 6),
        "alpha": alpha,
        "effect_size_cohens_d": round(d, 4),
        "ci95_diff": [round(ci_low, 4), round(ci_high, 4)],
        "significant": bool(p < alpha),
    }


# ----------------------------------------------------------------------------
# Two run modes
# ----------------------------------------------------------------------------
def run_simulated(config: dict) -> dict:
    n_runs = int(config.get("n_runs", 3))
    seed = int(config.get("seed", 42))
    baseline = float(config.get("baseline_metric", 0.80))
    improvement_target = float(config.get("improvement_target", 0.05))
    backends = seed_all(seed)

    random.seed(seed)
    results = []
    ours_vals, base_vals = [], []
    for i in range(n_runs):
        ours = baseline + random.gauss(improvement_target * 0.8, 0.02)
        base = baseline + random.gauss(0.0, 0.02)
        ours_vals.append(ours)
        base_vals.append(base)
        results.append({
            "run_id": i + 1,
            "ours": round(ours, 4),
            "baseline": round(base, 4),
            "seed_used": seed + i,
        })
    st = real_stats(ours_vals, base_vals)
    return {
        "status": "complete",
        "mode": "simulated",
        "simulation_notice": "Simulated experiment data (no real training run); MUST be labeled simulated data; significance comes from a real Welch t-test",
        "n_runs": n_runs,
        "results": results,
        "stats": st,
        "config": config,
        "seed_backends": backends,
        "env": env_fingerprint(),
    }


def _load_callable(spec: str):
    """module:func -> callable."""
    mod_name, _, fn_name = spec.partition(":")
    if not fn_name:
        raise ValueError(f"--metric/--baseline must be of the form 'module:func'; got: {spec}")
    mod = importlib.import_module(mod_name)
    return getattr(mod, fn_name)


def run_real(metric_spec, baseline_spec, config: dict) -> dict:
    n_runs = int(config.get("n_runs", 5))
    seed = int(config.get("seed", 42))
    backends = seed_all(seed)
    ours_fn = _load_callable(metric_spec)
    base_fn = _load_callable(baseline_spec) if baseline_spec else None

    ours_vals, base_vals = [], []
    results = []
    for i in range(n_runs):
        s = seed + i
        ov = float(ours_fn(s))
        ours_vals.append(ov)
        if base_fn:
            bv = float(base_fn(s))
            base_vals.append(bv)
        else:
            bv = float(config.get("baseline_value", 0.0))
            base_vals.append(bv)
        results.append({"run_id": i + 1, "ours": round(ov, 6),
                        "baseline": round(bv, 6), "seed_used": s})

    if not base_fn:
        # single group: report descriptive stats only, no two-group comparison
        return {
            "status": "complete",
            "mode": "real",
            "n_runs": n_runs,
            "results": results,
            "stats": {"mean": round(_mean(ours_vals), 6),
                      "std": round(_var(ours_vals, 1) ** 0.5, 6),
                      "note": "Single-group mode: no --baseline given; no two-group comparison performed"},
            "config": config,
            "seed_backends": backends,
            "env": env_fingerprint(),
        }
    st = real_stats(ours_vals, base_vals)
    return {
        "status": "complete",
        "mode": "real",
        "metric": metric_spec,
        "baseline": baseline_spec,
        "n_runs": n_runs,
        "results": results,
        "stats": st,
        "config": config,
        "seed_backends": backends,
        "env": env_fingerprint(),
    }


# ----------------------------------------------------------------------------
# Optional tracking (detect = autolog, no hard dependency)
# ----------------------------------------------------------------------------
def _maybe_track(run: dict):
    try:
        import mlflow
        with mlflow.start_run(run_name="skillkit-exp"):
            mlflow.log_param("mode", run.get("mode"))
            mlflow.log_param("n_runs", run.get("n_runs"))
            st = run.get("stats", {})
            if "p_value" in st:
                mlflow.log_metric("p_value", st["p_value"])
                mlflow.log_metric("cohens_d", st.get("effect_size_cohens_d", 0))
        run["tracking"] = "mlflow"
    except Exception:
        run["tracking"] = None
    return run


def main():
    ap = argparse.ArgumentParser(description="Reproducible experiment runner (SOTA stats)")
    ap.add_argument("--mode", default="simulated", choices=["simulated", "real"])
    ap.add_argument("--config", help="experiment config JSON (keys n_runs/seed/baseline_metric/improvement_target)")
    ap.add_argument("--n-runs", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--metric", help="real mode: metric function module:func (func(seed:int)->float)")
    ap.add_argument("--baseline", help="real mode: baseline function module:func")
    ap.add_argument("--baseline-value", type=float, default=0.0, help="fixed baseline value when no --baseline is given")
    ap.add_argument("--track", action="store_true", help="try mlflow autolog (requires mlflow installed)")
    ap.add_argument("--output", help="output JSON path")
    args = ap.parse_args()

    if args.config:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    else:
        config = {"n_runs": args.n_runs, "seed": args.seed,
                  "baseline_metric": 0.80, "improvement_target": 0.05}

    if args.mode == "real":
        if not args.metric:
            print(json.dumps({"status": "error",
                              "error": "real mode requires --metric module:func"}, ensure_ascii=False))
            return 2
        try:
            run = run_real(args.metric, args.baseline, config)
        except ModuleNotFoundError as e:
            # the user's module:func cannot be loaded -> fail cleanly with troubleshooting
            # guidance; a bare traceback is not allowed (the old version crashed outright,
            # and the orchestration layer only saw rc=1 with no JSON)
            print(json.dumps({"status": "error",
                              "error": f"Failed to load the module pointed to by --metric/--baseline: {e}; "
                                       f"make sure the module is on sys.path (run it from the same directory as --config, or set PYTHONPATH)",
                              "hint": "First verify it in isolation: python3 -c \"import <module>; print(<module>.<func>)\""},
                             ensure_ascii=False))
            return 2
        except (ValueError, AttributeError, TypeError) as e:
            print(json.dumps({"status": "error",
                              "error": f"--metric/--baseline is invalid: {e}"},
                             ensure_ascii=False))
            return 2
    else:
        run = run_simulated(config)

    if args.track:
        run = _maybe_track(run)

    out = json.dumps(run, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Results written to: {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
