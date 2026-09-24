---
name: model-solver
description: "Numerically solve mathematical models: LP/MIP (scipy/cvxpy), ODE/PDE (scipy.integrate), Monte Carlo (numpy). Consumes the model spec produced by model-formulator and returns the solution plus convergence information. When to use: the model spec is ready and you need an optimal solution, an integral, or sampling results — e.g. solving a model, picking a solver, optimizing the problem, or computing a numerical solution. Do NOT use when the problem is still in prose and needs formalizing (use model-formulator), or when the ask is result interpretation and charts (use result-visualizer)."
license: Apache-2.0
compatibility: "Requires scipy, numpy. Optional: cvxpy, pulp, ortools."
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Model Solver

Numerically solves mathematical models, returning the solution, objective value, and solver metadata.

## Applicability Decision Table

| Situation | Use this skill? | Reason |
|------|------------|------|
| Continuous LP (linear objective + linear constraints, continuous variables) | ✅ script solves directly | linprog/HiGHS main path |
| ODE initial-value problem | ✅ script solves directly | solve_ivp; `ode_method` options RK45/Radau/BDF/DOP853 |
| Monte Carlo estimate (normal assumption) | ✅ script solves directly | Gaussian sampling + p_exceed |
| MIP / MILP / ILP (with integer constraints) | ⚠️ script honestly refuses (rc=2) | linprog silently ignores integer constraints and gives a "fake solution"; install `pulp` and have the agent write an integer-solving path |
| Nonlinear programming / quadratic programming | ❌ out of scope | scipy.optimize needs gradients and an initial guess; hand it to the agent to write on the spot |
| Prose problem not yet formalized | ❌ go to model-formulator first | This skill only consumes a spec JSON |

## Honesty Statement (read first)

- The script really covers **three classes: LP / ODE / Monte Carlo**. The cvxpy/pulp/ortools in `compatibility` are "ecosystems you might use", not built into the script: **the script never calls them**; for integer programming the agent must install pulp itself and write the solving code.
- The `--method` parameter is only a reserved slot for "which solver family to dispatch"; it **does not change** the internal LP algorithm (always HiGHS); the ODE integration method uses the spec's `ode_method` field.
- `elapsed_ms` is measured with `perf_counter` (since v1.1) and is fine for rough comparison, but when comparing solver performance you should fix the sample size/seed and run multiple times to take the median.
- A MIP-solving request gets `status:"unsupported"` + **exit code 2** — this is by design: better to fail honestly than hand over a continuous fake solution.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| spec | Yes | Path to the model-spec JSON file produced by model-formulator |
| method | No | Force a solving method (overrides auto-dispatch); default auto |
| output | No | Write the solution result to a file; default stdout |

When missing, ask all at once: "Please provide: (1) spec (the model-spec JSON path, usually produced by model-formulator). I'll handle method/output with defaults."

## Pre-flight Checks

```bash
python3 --version
python3 -c "import scipy, numpy; print('deps OK', scipy.__version__)"
test -f scripts/model_solver.py && echo "OK script present"
```

- Expected: version number printed; `deps OK` printed; the script exists.
- On failure: missing scipy/numpy → `pip install scipy numpy`; script missing → STOP and report.

## Workflow

### Step 1: Load and validate the spec

- Action: read the spec file and confirm `model_type` and input fields are present.

```bash
python3 scripts/model_solver.py --spec model_spec.json --output solution.json
```

- Expected: the script parses the JSON successfully and dispatches a solver by `model_type`.
- On failure: `JSON decode error` → the spec isn't valid JSON; send it back to model-formulator to regenerate; missing `model_type` → add the field.

### Step 2: Dispatch solving by type

| Model type | Solver | Library | Script support |
|-----------|--------|---------|---------|
| LP | HiGHS | scipy.optimize.linprog | ✅ |
| MIP/MILP/ILP | CBC / Gurobi | pulp / cvxpy | ⚠️ honestly refuses rc=2, see failure table |
| ODE | RK45/Radau/BDF | scipy.integrate.solve_ivp | ✅ (`ode_method` optional) |
| Monte Carlo | Random sampling | random.gauss | ✅ |

- Action: the script auto-dispatches by `model_type`; MIP is explicitly refused rather than silently degraded.
- Expected: the solver returns normally, `status=="success"`.
- On failure: LP infeasible → check whether constraints are too tight; ODE not converging → add `ode_method:"Radau"` to the spec; missing dependency → `pip install scipy numpy`.

## Solver Dark Knowledge (where it easily goes wrong)

1. **Integer constraints being silently ignored is the most dangerous failure mode of MIP.** scipy.linprog is a purely continuous solver; feeding it a MIP returns a "looks-successful" continuous solution — and the gap between the integer optimum and the continuous optimum depends on the problem structure; there's no universal number, but it can easily be large enough to invalidate the conclusion. Since v1.1 the script explicitly refuses, preferring rc=2 over a fake solution.
2. **Infeasible and unbounded are handled oppositely.** In linprog, status 2 = infeasible (constraints contradict each other → relax them), status 3 = unbounded (the objective direction lacks a constraint → add a constraint or check the sign of the objective coefficients). Treating unbounded as infeasible and "relaxing constraints" makes the problem worse. Since v1.1 the two are reported separately.
3. **Scale constraints with vastly different magnitudes before solving.** Constraint coefficients spanning 6 orders of magnitude (e.g. 0.001 mixed with 1e6) make HiGHS numerically unstable or even falsely report infeasible; first unify variable units to the same magnitude (thousand yuan → ten-thousand yuan), then convert back after solving.
4. **Monte Carlo p_exceed error converges at 1/√n.** With 10,000 samples, the standard error of a 5% tail probability is about ±0.2% (absolute); don't report precision beyond what n supports — "p=4.87%" is false precision and self-deception at n=10^4.

### Step 3: Verify convergence and output

- Action: check that the returned `status` is `success`, and read `solution` / `objective_value` / `iterations`.
- Expected: output contains `status: "success"` and a numerical solution.
- On failure: `status` not success → record the failure reason and go back to Step 2 to adjust method/parameters.

## Output Format

```json
{
  "status": "success",
  "solution": [0.5, 1.5],
  "objective_value": 3.5,
  "solver": "scipy.linprog (HiGHS)",
  "iterations": 12
}
```

## Parameter Cheat Sheet

| Parameter | Values | Description |
|------|------|------|
| --spec | file path | Required, the model-spec JSON |
| --method | solver method name | Optional, force-override auto-dispatch |
| --output | file path | Optional, write the solution result |

## Failure Handling Table

| Symptom / error code | Cause | Action |
|------------|------|------|
| `JSON decode error` | spec isn't valid JSON | Send it back to model-formulator to regenerate the spec |
| `status:"unsupported"` + exit code 2 | MIP/MILP/ILP (script honestly refuses) | `pip install pulp`, then have the agent write an integer-solving path; or confirm whether integer constraints are really needed |
| `status:"infeasible"` | Constraints too tight or contradictory | Relax constraints / check constraint signs; rescale magnitudes first and retry |
| `status:"unbounded"` | The objective direction lacks a constraint | Add a bound constraint; check whether the objective coefficients' signs are reversed |
| `status:"iteration_limit"` | Iteration cap (rare) | Rescale variable magnitudes and retry |
| `Integration error` / ODE not converging | Stiff system with an explicit method | Add `"ode_method": "Radau"` or `"BDF"` to the spec |
| `ModuleNotFoundError: scipy` | Dependency not installed | `pip install scipy numpy` |

## Delivery Criteria

- Definition of success: the returned JSON has `status == "success"` and `solution` is a finite numerical array.
- Artifact naming: `solution.json` (or the path specified by `--output`).
- Save location: current working directory or the `--output` path.
- Completeness verification: `python3 -c "import json; d=json.load(open('solution.json')); assert d['status']=='success'"`; then it can be handed to result-visualizer for plotting.

## References

- references/solver-options.md — read when choosing a solver or tuning method/tolerances
