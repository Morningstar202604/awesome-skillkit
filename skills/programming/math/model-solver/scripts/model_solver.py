#!/usr/bin/env python3
"""Model Solver — 求解数学模型 (LP/ODE/Monte Carlo)。

用法:
  python3 model_solver.py --spec model_spec.json
  python3 model_solver.py --spec model_spec.json --method scipy
"""
import argparse
import json
import sys
import time
from pathlib import Path


def solve_lp(spec: dict) -> dict:
    """Solve linear programming problem."""
    try:
        from scipy.optimize import linprog
    except ImportError:
        return {"status": "error", "error": "scipy not installed"}

    # Extract from spec (simplified)
    c = spec.get("objective_coeffs", [1, 1])
    A_ub = spec.get("A_ub", [[1, 1]])
    b_ub = spec.get("b_ub", [10])
    bounds = spec.get("bounds", [(0, None)] * len(c))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
    return {
        "status": "success" if result.success else "infeasible",
        "solution": result.x.tolist() if result.x is not None else None,
        "objective_value": float(result.fun) if result.fun else None,
        "iterations": result.iter,
        "solver": "scipy.linprog (HiGHS)",
    }


def solve_ode(spec: dict) -> dict:
    """Solve ODE system."""
    try:
        from scipy.integrate import solve_ivp
        import numpy as np
    except ImportError:
        return {"status": "error", "error": "scipy/numpy not installed"}

    # Default: simple exponential decay if no specifics
    def ode_func(t, y):
        rate = spec.get("rate", 0.1)
        return [-rate * y[0]]

    t_span = spec.get("t_span", [0, 10])
    y0 = spec.get("y0", [1.0])
    t_eval = np.linspace(t_span[0], t_span[1], 100)

    sol = solve_ivp(ode_func, t_span, y0, t_eval=t_eval)
    return {
        "status": "success" if sol.success else "error",
        "t": sol.t.tolist(),
        "y": sol.y[0].tolist() if sol.y.size > 0 else [],
        "solver": "scipy.solve_ivp (RK45)",
    }


def solve_monte_carlo(spec: dict) -> dict:
    """Monte Carlo simulation."""
    import random
    import statistics

    n = spec.get("n_samples", 10000)
    mu = spec.get("mu", 0)
    sigma = spec.get("sigma", 1)
    threshold = spec.get("threshold", 0)

    samples = [random.gauss(mu, sigma) for _ in range(n)]
    exceed = sum(1 for s in samples if s > threshold)

    return {
        "status": "success",
        "n_samples": n,
        "mean": round(statistics.mean(samples), 4),
        "std": round(statistics.stdev(samples), 4),
        "p_exceed": round(exceed / n, 4),
        "threshold": threshold,
        "solver": "monte_carlo",
    }


def solve(spec: dict, method: str = None) -> dict:
    """Dispatch to appropriate solver."""
    method = method or spec.get("solver_hint", "scipy")
    model_type = spec.get("model_type", "LP").upper()

    if "LP" in model_type or "ILP" in model_type or "MIP" in model_type:
        result = solve_lp(spec)
    elif "ODE" in model_type or "PDE" in model_type:
        result = solve_ode(spec)
    elif "MONTE" in model_type or "STOCHASTIC" in model_type:
        result = solve_monte_carlo(spec)
    else:
        result = {"status": "unsupported", "model_type": model_type,
                  "note": "Add solver for this model type"}

    result["model_type"] = model_type
    result["elapsed_ms"] = 0
    return result


def main():
    parser = argparse.ArgumentParser(description="Solve math model")
    parser.add_argument("--spec", required=True, help="Model spec JSON file")
    parser.add_argument("--method", help="Force solver method")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    result = solve(spec, args.method)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
