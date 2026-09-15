---
name: model-solver
description: "Solve mathematical models: LP/MIP (scipy/cvxpy), ODE/PDE (scipy.integrate), Monte Carlo (numpy). Takes model spec from model-formulator, returns solution + convergence info. Use after formulation is complete. 当用户要求 求解模型 / 选求解器 / 优化问题求解 时使用。 Do NOT use for interpreting results or preparing presentation materials."
license: Apache-2.0
compatibility: Requires scipy, numpy. Optional: cvxpy, pulp, ortools.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Model Solver

Execute numerical solution for a mathematical model.

## When to Use

- Model spec is ready (from model-formulator)
- Need to find optimal solution (LP/ILP)
- Need to integrate ODE/PDE
- Need to run stochastic simulation

## Input

```json
{
  "model_type": "LP | MIP | ODE | Monte_Carlo",
  "objective_coeffs": [1, 2, 3],
  "A_ub": [[1, 1], [1, 0]],
  "b_ub": [4, 2],
  "t_span": [0, 10],
  "y0": [1.0]
}
```

## Output

```json
{
  "status": "success",
  "solution": [0.5, 1.5],
  "objective_value": 3.5,
  "solver": "scipy.linprog (HiGHS)",
  "iterations": 12
}
```

## Solver Dispatch

| Model Type | Solver | Library |
|-----------|--------|---------|
| LP | HiGHS / Simplex | scipy.optimize.linprog |
| MIP | CBC / Gurobi | pulp / cvxpy |
| ODE | RK45 / Radau | scipy.integrate.solve_ivp |
| Monte Carlo | Random sampling | numpy.random |

## Workflow

1. Load model spec
2. Dispatch to appropriate solver
3. Run computation
4. Validate convergence
5. Output: solution + metadata

## References

- [references/solver-options.md](references/solver-options.md) — solver selection guide