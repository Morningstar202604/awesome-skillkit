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
    # status: 0=success 1=iteration limit 2=infeasible 3=unbounded —— 不可行与无界不可混报
    status_map = {0: "success", 1: "iteration_limit", 2: "infeasible", 3: "unbounded"}
    return {
        "status": status_map.get(result.status, "failed"),
        "solution": result.x.tolist() if result.x is not None else None,
        "objective_value": float(result.fun) if result.fun is not None else None,
        "iterations": result.nit,
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
    # 积分方法可按 spec 指定：刚性系统用 Radau/BDF，高精度用 DOP853
    ode_method = spec.get("ode_method", "RK45")

    sol = solve_ivp(ode_func, t_span, y0, t_eval=t_eval, method=ode_method)
    return {
        "status": "success" if sol.success else "error",
        "t": sol.t.tolist(),
        "y": sol.y[0].tolist() if sol.y.size > 0 else [],
        "solver": "scipy.solve_ivp (%s)" % ode_method,
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
    t0 = time.perf_counter()
    method = method or spec.get("solver_hint", "scipy")
    model_type = spec.get("model_type", "LP").upper()

    # 整数约束必须最先判定：linprog 是纯连续 LP 求解器，会把 MIP 当 LP 解出
    # 一个"看似成功"的连续解——整数最优常常与连续最优不同，这是最危险的静默误解。
    if any(k in model_type for k in ("MIP", "MILP", "ILP")):
        result = {
            "status": "unsupported",
            "model_type": model_type,
            "error": "integer constraints (MIP/MILP/ILP) not supported by scipy.linprog",
            "note": "install a MILP solver and provide an integer-capable path: "
                    "pip install pulp  (or ortools / mip); see SKILL.md failure table",
        }
    elif "LP" in model_type:
        result = solve_lp(spec)
    elif "ODE" in model_type or "PDE" in model_type:
        result = solve_ode(spec)
    elif "MONTE" in model_type or "STOCHASTIC" in model_type:
        result = solve_monte_carlo(spec)
    else:
        result = {"status": "unsupported", "model_type": model_type,
                  "note": "Add solver for this model type"}

    result["model_type"] = model_type
    result["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return result


def main():
    parser = argparse.ArgumentParser(description="Solve math model")
    parser.add_argument("--spec", required=True, help="Model spec JSON file")
    parser.add_argument("--method", help="Force solver method")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

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

    result = solve(spec, args.method)
    if result.get("status") == "error":
        print(f"Error: {result.get('error')}", file=sys.stderr)
        return 1
    if result.get("status") == "unsupported":
        # 诚实失败：打印完整 JSON 便于人工排查，但用非零码让流水线感知
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("Error: model type unsupported — see 'note' in JSON above", file=sys.stderr)
        return 2

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
