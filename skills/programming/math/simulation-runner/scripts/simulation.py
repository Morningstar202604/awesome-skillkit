#!/usr/bin/env python3
"""Simulation Runner — parameter sweep, sensitivity analysis, Monte Carlo simulation.

Usage:
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
    parser.add_argument("--sensitivity", nargs="*", help="Params for OAT (space- or comma-separated)")
    parser.add_argument("--perturbation", type=float, default=0.1,
                        help="Relative perturbation for OAT sensitivity (default 0.1 = 10%%)")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.monte_carlo:
        result = monte_carlo(args.n, args.mu, args.sigma, args.threshold)
    elif args.spec and args.param:
        spec_path = Path(args.spec)
        if not spec_path.exists():
            print(f"Error: spec file not found: {args.spec}", file=sys.stderr)
            return 1
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON in spec file: {e}", file=sys.stderr)
            return 1
        except OSError as e:
            print(f"Error: cannot read spec file: {e}", file=sys.stderr)
            return 1
        lo, hi = args.range if args.range else [0.1, 5.0]
        result = param_scan(spec, args.param, lo, hi, args.steps)
    elif args.sensitivity:
        # Normalize param list: accept space-separated (nargs="*") or
        # comma-separated tokens like "rate,noise,decay".
        raw_params = args.sensitivity
        params = []
        for token in raw_params:
            params.extend(p.strip() for p in token.split(","))
        params = [p for p in params if p]

        spec = {}
        base_values = {}
        if args.spec:
            spec_path = Path(args.spec)
            if not spec_path.exists():
                print(f"Error: spec file not found: {args.spec}", file=sys.stderr)
                return 1
            try:
                spec = json.loads(spec_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                print(f"Error: invalid JSON in spec file: {e}", file=sys.stderr)
                return 1
            except OSError as e:
                print(f"Error: cannot read spec file: {e}", file=sys.stderr)
                return 1
            # Pull numeric base values from spec where available.
            for p in params:
                if p in spec and isinstance(spec[p], (int, float)):
                    base_values[p] = float(spec[p])

        result = sensitivity(spec, params, base_values,
                            perturbation=args.perturbation)
    else:
        # nothing supplied -> demo run; label it honestly as demo so it is not cited as a real experiment
        result = monte_carlo()
        result["demo"] = True
        result["note"] = "No run parameters specified; this is the built-in demo distribution (mu=0, sigma=1, n=10000). " \
                         "Do not cite it as a real experimental result. For a real run, supply --n/--mu/--sigma/--threshold or --spec."

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        try:
            Path(args.output).write_text(output, encoding="utf-8")
        except OSError as e:
            print(f"Error: cannot write output file: {e}", file=sys.stderr)
            return 1
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
