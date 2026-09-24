# Model Types (modeling problem types and model-selection reference)

> Companion to model-formulator. `model_formulator.py` fixes five domains (`optimization` / `differential` / `statistical` / `stochastic` / `bayesian`), and `formulate()` uses keyword heuristics to fill `model_type` and `solver_hint`:
> - matches `minimize|maximize|cost|profit|time` → LP; contains `integer|assign` → MIP
> - matches `rate|flow|change|growth` → domain=differential, ODE
> - matches `probability|random|uncertain|risk` → domain=stochastic, monte_carlo
>
> In other words: **the script gives a starting point, not a conclusion**. It does not look at data or validate constraints; when no keyword matches, `model_type` simply takes the first item in that domain's list (optimization→LP, differential→ODE, statistical→regression, stochastic→markov_chain, bayesian→prior_posterior). You must manually review using this file.

## Table of Contents
- §1 Selection decision tree (from problem to model type)
- §2 Optimization (LP / ILP / MIP / NLP / convex optimization)
- §3 Prediction (regression / time series)
- §4 Classification
- §5 Graphs and networks
- §6 Queues and simulation
- §7 Decisions and games
- §8 Assumptions and failure-mode quick reference
- §9 Notes on filling in the model spec

## §1 Selection decision tree

```
Does the problem contain a "decision to make" (a quantity you choose)?
├─ Yes (decision-type)
│  ├─ Objective and constraints are both linear, variables continuous   → LP
│  ├─ Needs integer decisions like "yes/no" or "how many"               → ILP / MIP
│  ├─ Objective or constraints nonlinear
│  │   ├─ Can be written in convex form (provably convex)               → convex optimization (CVXPY)
│  │   └─ Nonconvex / multimodal                                        → local optimization + multi-start, or heuristics / metaheuristics
│  └─ Decisions are staged, the future is random and observable        → stochastic programming / MDP
└─ No (descriptive / predictive)
   ├─ Output is continuous
   │   ├─ Samples independent                                            → regression
   │   └─ Samples correlated over time                                 → time series
   ├─ Output is a discrete class                                       → classification
   └─ You want to describe the "mechanism" rather than fit
       ├─ Continuous state evolving over time                           → ODE / PDE
       ├─ Entities queue, resources are contested                       → queueing theory / discrete-event simulation
       └─ Multiple agents interact                                      → simulation / game theory
```
Key criterion: first ask what the **decision variables** are. If you cannot name a decision variable, it is not an optimization problem—don't force an LP onto it.

## §2 Optimization

| Type | Form | Typical assumptions | Failure conditions |
|---|---|---|---|
| LP | `min cᵀx, s.t. Ax ≤ b, x ≥ 0` | Proportionality, additivity, determinism, continuity | Fixed costs / setup costs exist (need 0-1 variables) |
| ILP / MIP | Same + `x ∈ ℤ` or `x ∈ {0,1}` | Discrete decisions | Solve time can explode at scale (NP-hard class; actual runtime is strongly data-dependent—**do not pre-commit to a solve time**) |
| Convex optimization | `min f(x)`, f and constraints convex | Objective/constraints satisfy convexity (CVXPY checks via DCP rules) | Writing it in nonconvex form gets rejected by the solver outright (DCPError) |
| NLP (nonconvex) | General nonlinear | Local optima acceptable | Sensitive to the initial guess; may only yield a local solution |

Tool entry points: LP → `scipy.optimize.linprog` (HiGHS); MIP → `scipy.optimize.milp` (HiGHS, SciPy ≥ 1.9, **VERIFY BEFORE USE**), PuLP(CBC), OR-Tools CP-SAT; convex → CVXPY; general nonlinear → `scipy.optimize.minimize`.
Note: `model_solver.py` currently also sends ILP/MIP into `solve_lp` (without integer constraints), yielding the **LP relaxation**—if you need integer solutions, you must switch to the tools above (see model-solver's `solver-options.md`).

## §3 Prediction

| Type | When to use | Key assumptions | Failure conditions |
|---|---|---|---|
| Linear regression | Relationship near-linear, interpretable coefficients needed | Linearity, i.i.d. errors, homoscedasticity | Strong nonlinearity, collinear features, heteroscedasticity |
| GLM / regularized (Lasso/Ridge) | High dimension, variable selection needed | Same + sparse or smooth prior | Feature scales not unified (penalty is unfair without standardization) |
| Tree models / GBDT | Tabular data, nonlinear, mixed types | Stable sample distribution | Poor extrapolation (predicting outside the training range) |
| Time series (ARIMA / exponential smoothing / state space) | Series with trend/seasonality | **Stationarity** (or stationarity after differencing), uniform time intervals | Structural breaks, missing periods, unmodeled external interventions |

For time series always do this first: plot the series → check for gaps and uniform spacing → run a stationarity test → then choose a model. The train/test split must be **by time** (a random split leaks future information).

## §4 Classification

| Type | When to use | Key assumptions | Failure conditions |
|---|---|---|---|
| Logistic regression | Interpretability needed, linear boundary, probability calibration | Linear log-odds, classes near-separable | Strongly nonlinear boundary; slow convergence due to unscaled features |
| Tree / random forest | Tabular baseline, robust | Same distribution | Tends to the majority class on extremely imbalanced data |
| GBDT | Tabular tasks where accuracy is the priority | Same distribution | Overfits on small data; needs early stopping |
| SVM / kernel methods | Small-to-medium scale, clear boundary | Consistent feature scale | Slow training on large-scale data (no specific magnitude given; no speed promise) |

Handling class imbalance: `class_weight="balanced"`, resampling (note: apply it only to the training fold), and switch to PR-AUC / F1 instead of accuracy (see ml-pipeline's `metrics-explained.md`).

## §5 Graphs and networks

- Shortest path (Dijkstra / Bellman-Ford; the latter supports negative weights), minimum spanning tree, max-flow/min-cut, matching, TSP/VRP.
- Typical assumptions: edge weights known and deterministic; graph structure fixed.
- Failure conditions: dynamic graphs (edges change over time), time windows and capacity constraints (VRPTW is NP-hard class), uncertain edge weights (→ stochastic / robust versions).
- Tools: `networkx` (teaching / small-to-medium scale, pure Python, slow at scale), OR-Tools (strong on routing/flow solving).
- Judgment: if the problem mentions "routes / connectivity / flow / dependency order / minimum traversal", draw the graph first, then decide whether it is a standard graph problem.

## §6 Queues and simulation

- Queueing theory (M/M/1 etc.) applies when: arrival and service processes can be modeled as stochastic processes and a steady state is solvable. **Spell out the letter meanings** (M = Poisson arrival / exponential service, D = deterministic, G = general distribution).
- Failure conditions: arrival rate near/above the service rate (system unstable, queue grows without bound), non-steady state (you only care about the first few hours of operation), complex routing rules that resist analytic solution.
- In that case switch to **discrete-event simulation** (`simpy` or a hand-rolled event loop), and repeat runs with Monte Carlo to get the distribution (see simulation-runner's `mc-theory.md`).
- Key output is not just the mean: the **p95/p99** of waiting time is often the actual measure of service level.

## §7 Decisions and games

- Decision trees / influence diagrams: single decision-maker, outcome probabilities known → maximize expected utility.
- Markov decision process (MDP): sequential decisions, known state transitions → value iteration / policy iteration; transitions unknown → reinforcement learning or simulation.
- Games: multiple parties' strategies interact → Nash equilibrium; **note** that equilibria need not be unique and need not be "optimal"; they describe rather than prescribe.
- Failure conditions: utility hard to quantify, opponent irrational, probabilities come from subjective estimates without sensitivity analysis → the conclusion is unreliable; you must do a sensitivity analysis (simulation-runner's OAT mode).

## §8 Assumptions and failure-mode quick reference

| Model | Most easily overlooked assumption | Symptom once violated |
|---|---|---|
| LP | Proportionality (no economies of scale / fixed costs) | Solution looks optimal but is actually infeasible |
| ILP/MIP | Solve time is controllable | Runs for a long time with no solution; only a feasible solution, no optimality proof |
| Convex optimization | Objective/constraints convex | Solver raises DCPError, or multi-start yields different solutions |
| Regression | Homoscedasticity, no strong collinearity | Unstable coefficients, distorted p-values |
| Time series | Stationarity, uniform spacing | Prediction lags one step or is offset overall |
| Queueing | Steady state, arrival rate < service rate | Queue length diverges |
| Simulation | Reproducible random numbers, enough runs | The conclusion flips when you change the seed |

## §9 Notes on filling in the model spec

Script output fields: `problem / domain / model_type / variables / objective / constraints / assumptions / knowns / unknowns / solver_hint / status / next_step`. When manually reviewing:

- `variables` use ASCII key names (e.g. `x[i,j]`), to make JSON transport and downstream code generation easier (notation conventions see `notation-guide.md`).
- `constraints` one per line, numbered (C1, C2…), so model-solver errors can point to a specific constraint.
- `assumptions` must be **testable** statements ("demand is constant over the cycle" rather than "simplified"); each assumption should be confirmable by data or by the business side, otherwise mark it as pending confirmation.
- `solver_hint` is only a hint: `model_solver.py` dispatches mainly by the `model_type` string (contains LP/ILP/MIP → LP branch; ODE/PDE → solve_ivp; MONTE/STOCHASTIC → random sampling); filling in the wrong type sends it down the wrong branch directly.
