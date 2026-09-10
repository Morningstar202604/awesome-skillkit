#!/usr/bin/env python3
"""Simulation Runner — 参数扫描、敏感性分析、蒙特卡洛仿真。

用法:
  python3 simulation.py --spec model_spec.json --param rate --range 0.1 5.0 --steps 10
  python3 simulation.py --monte-carlo --n 10000 --mu 0 --sigma 1
"""
import argparse
import json
import random
import statistics
import sys
from pathlib import Path


def param_scan(spec: dict, param: str, lo: float, hi: float,
               steps: int = 10) -> dict:
    """Sweep a parameter and record objective values."""
    import copy
    results = []
    step_size = (hi - lo) / steps

    for i in range(steps + 1):
        val = lo + i * step_size
        s = copy.deepcopy(spec)
        s[param] = val
        s.setdefault("n_samples", 1000)
        # Quick proxy: just record the parameter value
        results.append({"param": round(val, 4), "value": val,
                        "note": "run model-solver for actual result"})

    return {
        "param": param,
        "range": [lo, hi],
        "steps": steps,
        "sweep": results,
        "status": "scan_ready",
        "next": "feed each into model-solver",
    }


def monte_carlo(n: int = 10000, mu: float = 0, sigma: float = 1,
                threshold: float = 0, quantile: float = 0.95) -> dict:
    """Run Monte Carlo simulation with statistics."""
    samples = [random.gauss(mu, sigma) for _ in range(n)]
    samples_sorted = sorted(samples)

    p50 = samples_sorted[n // 2]
    p95 = samples_sorted[int(n * quantile)]
    exceed = sum(1 for s in samples if s > threshold)

    return {
        "status": "success",
        "n": n,
        "mean": round(statistics.mean(samples), 4),
        "std": round(statistics.stdev(samples), 4),
        "p50": round(p50, 4),
        f"p{int(quantile*100)}": round(p95, 4),
        "p_exceed_threshold": round(exceed / n, 4),
        "threshold": threshold,
        "min": round(min(samples), 4),
        "max": round(max(samples), 4),
    }


def sensitivity(spec: dict, params: list, base_values: dict,
                perturbation: float = 0.1) -> dict:
    """One-at-a-time sensitivity analysis."""
    results = {}
    for p in params:
        base = base_values.get(p, 1.0)
        low = base * (1 - perturbation)
        high = base * (1 + perturbation)
        results[p] = {
            "base": base,
            "low": low,
            "high": high,
            "delta_low": "run model-solver with base_low",
            "delta_high": "run model-solver with base_high",
        }
    return {"status": "sensitivity_ready", "params": results}


def main():
    parser = argparse.ArgumentParser(description="Run simulations")
    parser.add_argument("--spec", help="Model spec JSON")
    parser.add_argument("--param", help="Parameter to sweep")
    parser.add_argument("--range", nargs=2, type=float, metavar=("LO", "HI"))
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--monte-carlo", action="store_true")
    parser.add_argument("--n", type=int, default=10000)
    parser.add_argument("--mu", type=float, default=0)
    parser.add_argument("--sigma", type=float, default=1)
    parser.add_argument("--threshold", type=float, default=0)
    parser.add_argument("--sensitivity", nargs="*", help="Params for OAT")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.monte_carlo:
        result = monte_carlo(args.n, args.mu, args.sigma, args.threshold)
    elif args.spec and args.param:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        lo, hi = args.range if args.range else [0.1, 5.0]
        result = param_scan(spec, args.param, lo, hi, args.steps)
    elif args.sensitivity:
        result = sensitivity({}, args.sensitivity, {})
    else:
        result = monte_carlo()

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
