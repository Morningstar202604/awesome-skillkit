# Solver Options (solver selection and infeasibility diagnosis)

> Companion to model-solver. **No performance benchmark numbers are given** (runtime is strongly tied to size, sparsity structure, and the machine; any number across environments is misleading). This guide only gives capability boundaries, integration methods, and diagnostic approaches; when you need a speed conclusion, measure it on your own data and machine.

## Table of Contents
- §0 What the current script can do (including one defect found by testing)
- §1 Problem type × library × entry-point reference table
- §2 Minimal runnable examples per library
- §3 Status codes and result fields
- §4 Diagnosing infeasible / unbounded problems
- §5 Relaxation localization (finding conflicting constraints)
- §6 Numerical and scale notes
- §7 Pre-delivery checklist

## §0 What the current script can do (including one defect found by testing)

`model_solver.py` dispatches on the `model_type` string; only three branches are actually implemented:

| Branch condition | Actual behavior |
|---|---|
| Contains `LP` / `ILP` / `MIP` | `solve_lp`: `scipy.optimize.linprog(..., method="highs")`. **No integer constraints are set** → ILP/MIP routed here yield the LP relaxation (may not be integral) |
| Contains `ODE` / `PDE` | `solve_ode`: `solve_ivp` solves a hard-coded exponential decay `dy/dt = -rate*y`, with `rate` from the spec, default 0.1; **not a general ODE solver** (function body is hard-coded) |
| Contains `MONTE` / `STOCHASTIC` | `solve_monte_carlo`: `random.gauss(mu, sigma)` sampling, outputs mean/std/p_exceed; no seed parameter |

Defect found by testing (on scipy 1.17.0 + Python 3.11 on this machine): `solve_lp` reads `result.iter`, but `linprog`'s `OptimizeResult` only has the `nit` field, so the LP branch always raises `AttributeError: iter` (traceback ends at `result.iter`). **Fix**: change `"iterations": result.iter` to `"iterations": getattr(result, "nit", None)`. If you must run the script as-is, first call `linprog` yourself externally (§2).

## §1 Problem type × library × entry-point reference table

| Problem type | First choice | Alternative | Notes |
|---|---|---|---|
| LP (linear programming) | `scipy.optimize.linprog` (HiGHS) | PuLP(CBC), OR-Tools | HiGHS ships with SciPy; no extra install needed |
| MILP (integer / mixed-integer) | `scipy.optimize.milp` (HiGHS, SciPy ≥ 1.9, **VERIFY BEFORE USE**) | PuLP(CBC), OR-Tools CP-SAT | Integer decisions must use this tier, not linprog |
| Convex optimization (DCP-representable) | CVXPY | SciPy | CVXPY checks convexity at modeling time and rejects nonconvex outright |
| General nonlinear (no convexity guarantee) | `scipy.optimize.minimize` | — | Local optimum, no global guarantee; needs multi-start |
| Constraint satisfaction / scheduling (integer-heavy) | OR-Tools CP-SAT | — | Continuous quantities must be scaled to integers first |
| ODE (non-stiff) | `solve_ivp` (default RK45) | — | For stiff problems switch to `Radau` / `BDF` |
| Stochastic / simulation | `numpy.random.Generator` | `simpy` (discrete event) | See simulation-runner's `mc-theory.md` |

Commercial solvers (Gurobi / CPLEX / FICO Xpress) support LP/MIP/(some) convex and nonconvex problems; academic licenses and terms are governed by the vendors (**VERIFY BEFORE USE**: licensing and feature scope change with versions; check the official site before use). If the open-source stack suffices, no need to introduce them.

## §2 Minimal runnable examples per library

### LP — scipy.optimize.linprog
```python
from scipy.optimize import linprog
# min x + y   s.t. x + y <= 10, x >= 0, y >= 0
r = linprog(c=[1, 1], A_ub=[[1, 1]], b_ub=[10], bounds=[(0, None), (0, None)], method="highs")
print(r.status, r.message)      # expected: 0 / Optimization terminated successfully.
print(r.x, r.fun)               # expected: x is the optimal solution vector, fun is the optimal value
print(r.nit)                    # iteration count (note: the field name is nit, not iter)
```

### MILP — scipy.optimize.milp (verified on this machine)
```python
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
# max x + y   s.t. x + y <= 1.5, x,y ∈ {0,1}
res = milp(c=np.array([-1.0, -1.0]),                       # maximize → minimize the negation
           constraints=LinearConstraint(np.array([[1.0, 1.0]]), -np.inf, 1.5),
           integrality=np.array([1, 1]),                   # 1=integer, 0=continuous
           bounds=Bounds([0, 0], [1, 1]))
print(res.status, res.message)   # expected: 0 / Optimization terminated successfully. (HiGHS Status 7: Optimal)
print(res.x, res.fun)            # measured output on this machine: [1. 0.] -1.0
```
Pitfalls: `integrality` length must equal the number of variables; each row of the constraint matrix is one constraint; `LinearConstraint(A, lb, ub)` means `lb <= A@x <= ub`, pad one-sided constraints with `±np.inf`.

### MIP — PuLP (CBC ships with PuLP)
```python
import pulp
prob = pulp.LpProblem("assign", pulp.LpMinimize)
x = pulp.LpVariable("x", lowBound=0, cat="Integer")
y = pulp.LpVariable("y", lowBound=0, cat="Integer")
prob += x + y                      # objective
prob += x + y >= 3                 # constraint (more can be added)
prob.solve(pulp.PULP_CBC_CMD(msg=False))
print(pulp.LpStatus[prob.status])  # expected: Optimal / Infeasible / Unbounded
print(x.value(), y.value())
```
Pitfalls: status must be looked up via `pulp.LpStatus[prob.status]` (a string); do not compare against a number directly; `x.value()` being `None` means no solution was found.

### Convex optimization — CVXPY
```python
import cvxpy as cp
x = cp.Variable(2)
prob = cp.Problem(cp.Minimize(cp.sum_squares(x - 1)), [x >= 0, cp.sum(x) == 1])
prob.solve()                        # default solver chosen automatically by CVXPY
print(prob.status, prob.value, x.value)
```
Expected: `prob.status` is `optimal`. If the model does not satisfy the DCP convexity rules, CVXPY raises `DCPError` at `solve()` time (this is a **guard**, not a bug; it means the model is nonconvex and needs restructuring or switching to the nonlinear branch in §1). To see which solver was actually used: add `verbose=True` or check `prob.solver_stats` (field names per your local CVXPY docs, **VERIFY BEFORE USE**).

### Nonlinear — scipy.optimize.minimize
```python
from scipy.optimize import minimize
r = minimize(lambda x: (x[0] - 1) ** 2 + (x[1] + 2) ** 2, x0=[0.0, 0.0], method="L-BFGS-B",
             bounds=[(-5, 5), (-5, 5)])
print(r.success, r.x, r.fun)        # expected: success True, x near [1, -2]
```
Pitfalls: local optimum, so results may differ with different initial guesses → try multiple starting points and compare; with constraints, `SLSQP` / `trust-constr` are more appropriate (choose by your constraint type, **VERIFY BEFORE USE**).

### ODE — scipy.integrate.solve_ivp
```python
from scipy.integrate import solve_ivp
sol = solve_ivp(lambda t, y: [-0.5 * y[0]], (0, 10), [1.0], t_eval=None, method="RK45")
print(sol.success, sol.message, sol.y[0][-1])
```
Stiff problems (common in decay / reaction kinetics): switch to `method="Radau"` or `"BDF"`; if solving fails, first shorten the interval or relax the tolerances `rtol` / `atol`.

## §3 Status codes and result fields

`scipy.optimize.linprog`'s `res.status` (measured on SciPy 1.17.0 on this machine):

| status | Meaning |
|---|---|
| 0 | Optimal solution found |
| 1 | Iteration limit reached |
| 2 | **Infeasible** |
| 3 | **Unbounded** |

Criterion: when `res.success` is False you must read `res.message` (HiGHS spells out infeasible / unbounded). `res.x` is `None` on failure—check `res.success` first, then take `.x`, otherwise you'll get `AttributeError`.
Common fields: `x` (solution), `fun` (objective value), `nit` (iteration count), `slack` (slack, to judge which constraints are tight), `message`.

## §4 Diagnosing infeasible / unbounded problems

Common causes of infeasibility (status 2), checked by frequency:
1. **Constraint direction reversed** (wrote `<=` instead of `>=`)—most frequent.
2. **Inconsistent units/scales** (one side in minutes, the other in hours) → see model-formulator's `notation-guide.md`.
3. **Contradictory bounds** (e.g. `x >= 10` and `x <= 5` coexist, or `bounds` conflicts with a constraint).
4. **NaN / inf in the data** → solver behaves oddly or errors out directly; check `np.isfinite(A).all()` first.
5. **Integerization causes infeasibility**: the LP relaxation is feasible but the MIP is infeasible (no integer point lands) → relax integer constraints or adjust bounds to verify.
6. **"Must equal exactly" is too strong**: replace `==` with a range (e.g. `>= target` and `<= target + tolerance`) to test whether a rigid equality is the cause.

Common causes of unboundedness (status 3): missing resource upper bounds / nonnegativity constraints, objective direction reversed (should minimize but written as maximize), missing variable lower bounds.
Diagnosis: read `res.message` → check each variable for finite bounds in both directions → negate the objective to verify the direction.

## §5 Relaxation localization (finding conflicting constraints)

Idea: introduce a slack variable `s_k ≥ 0` for each "hard constraint", change the objective to "minimize total slack", and after solving, see which `s_k > 0`—those are the constraints that cannot be satisfied simultaneously (IIS candidates).

```python
import numpy as np
from scipy.optimize import linprog
# original problem: A_ub @ x <= b_ub,  x >= 0
A, b = np.array([[1.0, 1.0], [-1.0, -1.0]]), np.array([1.0, -5.0])   # deliberately infeasible: x<=1 and x>=5
n_x, n_c = A.shape[1], A.shape[0]
# new variable z = [x, s]; constraint A@x - s <= b; objective min sum(s)
A_new = np.hstack([A, -np.eye(n_c)])
c_new = np.r_[np.zeros(n_x), np.ones(n_c)]
bounds = [(0, None)] * (n_x + n_c)
r = linprog(c_new, A_ub=A_new, b_ub=b, bounds=bounds, method="highs")
print(r.status, np.round(r.x[n_x:], 6))   # expected: status 0; the slack components >0 point to conflicting constraints
```
Expected: the nonzero slack components correspond to the original constraints that are the source of the contradiction; print them out and check each one with the business side.
Note: this is the generic "elastic mode" approach, implementable with any LP solver. Commercial solvers (e.g. Gurobi) have a built-in `computeIIS()` that directly returns the minimal conflict set (**VERIFY BEFORE USE**: commercial feature, varies with version and license); SciPy/PuLP have no built-in IIS—use the relaxation method above.

## §6 Numerical and scale notes

- Coefficients differing by too many orders of magnitude (e.g. `1e-9` and `1e9` in the same row) cause numerical difficulties (status 4 / abnormal `HiGHS Status`) → first do variable scaling (unify units); this is more effective than switching solvers.
- Whenever possible, pass sparse matrices (`scipy.sparse`) to large-scale LP/MIP; sparsity usually determines solvability (no specific size promised).
- The more integer variables, the less predictable the solve time; when you need a time guarantee, set `time_limit` (parameter names differ across libraries, **VERIFY BEFORE USE**) and accept "feasible solution + gap" rather than an optimality proof.
- Results must be **verified by back-substitution**: plug the solution into the original constraints and compute residuals, e.g. `np.max(A @ x - b)` should be ≤ a small tolerance (the tolerance value depends on scale, **VERIFY BEFORE USE**). The solver saying optimal does not mean the model was written correctly.

## §7 Pre-delivery checklist

- [ ] `model_type` matches the solving branch (integer decisions did not go through LP relaxation)
- [ ] `res.success` / `status` / `message` were all checked, not just one
- [ ] The residual of the solution back-substituted into constraints is within tolerance
- [ ] If infeasible: used the six checks in §4 + the relaxation method in §5 to localize the specific constraint
- [ ] Coefficients were unit-unified and scale-checked
- [ ] If an MIP was run: recorded the solver-returned bound/gap and termination reason, not just a single solution
- [ ] The report **does not** include timing numbers of dubious cross-machine reproducibility; if they must be given, note "measured on this machine, this data, this version"
