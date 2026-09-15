---
name: model-formulator
description: "Formalize a real-world problem into a mathematical model: identify variables, constraints, objective function, and model type (ODE/ILP/stochastic/Bayesian). Outputs a structured model spec that model-solver can consume. Use when the problem is defined in words but needs mathematical structure. 当用户要求 数学建模 / 把问题写成模型 / 定义变量与约束 时使用。 Do NOT use for numerically solving the formulated model (use model-solver)."
license: Apache-2.0
compatibility: Pure Python + LLM assistance. No external solver needed at this step.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Model Formulator

Turn a word problem into a structured mathematical model specification.

## When to Use

- Problem is described in natural language, need math structure
- Before calling model-solver (this is step 1 of math pipeline)
- Need to identify variables, constraints, objective
- Choosing model type (deterministic vs stochastic, linear vs nonlinear)

## Input

```json
{
  "problem": "Minimize delivery cost for 50 routes with 200 deliveries, 5 trucks, time windows 8-18h",
  "domain": "optimization | differential | statistical | stochastic | bayesian",
  "knowns": {"routes": 50, "deliveries": 200, "trucks": 5, "time_window": "8-18"},
  "unknowns": ["route_assignment", "truck_schedule", "total_cost"]
}
```

## Output

```json
{
  "model_type": "ILP",
  "variables": {
    "x[i,j]": "truck i assigned to delivery j (binary)",
    "y[i]": "truck i used (binary)"
  },
  "objective": "min Σ cost[i,j] * x[i,j] + fixed_cost * y[i]",
  "constraints": [
    "each delivery assigned to exactly 1 truck: Σ_i x[i,j] = 1 ∀j",
    "time window: start_time[j] + service_time[j] + travel_time[i,j] ≤ end_time[j]",
    "truck capacity: Σ_j demand[j] * x[i,j] ≤ capacity[i] ∀i"
  ],
  "assumptions": ["travel time is constant", "no traffic variability"],
  "solver_hint": "cvxpy | scipy.optimize | pulp | ortools",
  "complexity": "NP-hard (VRPTW), MIP solve < 5min expected"
}
```

## Workflow

1. **Parse problem** — extract entities, quantities, relationships
2. **Classify domain** — optimization? differential? statistical?
3. **Define variables** — decision variables, state variables
4. **Write objective** — what to minimize/maximize
5. **Write constraints** — all physical/logical bounds
6. **State assumptions** — what we're simplifying
7. **Pick solver** — which tool fits (scipy/cvxpy/pulp/ortools)
8. **Output spec JSON** — consumable by model-solver

## Model Type Decision Tree

```text
Is it deterministic?
├── Yes → Is it continuous?
│   ├── Yes → ODE/PDE or nonlinear optimization
│   └── No  → ILP / Combinatorial
└── No  → Is it sequential?
    ├── Yes → Markov Chain / MDP / Simulation
    └── No  → Bayesian / Statistical
```

## References

- [references/model-types.md](references/model-types.md) — model catalog with examples
- [references/notation-guide.md](references/notation-guide.md) — standard math notation