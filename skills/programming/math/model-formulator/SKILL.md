---
name: model-formulator
description: "Formalize a natural-language problem into a mathematical model: identify variables, constraints, objective function, and model type (ODE/ILP/stochastic/Bayesian), and output a model spec consumable by model-solver. When to use: the problem is already described in prose but lacks mathematical structure — e.g. math modeling, turning a problem into a model, defining variables and constraints, formalizing a problem, or writing a math model. Do NOT use when a formal model already exists and only numerical solving (use model-solver) or plotting results (use result-visualizer) is needed."
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

Turns a prose problem into a structured mathematical-model spec (variables / constraints / objective function / model type), serving as the input to model-solver.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| problem | Yes | Natural-language problem description, including entities, quantities, and relationships |
| domain | No | `optimization` / `differential` / `statistical` / `stochastic` / `bayesian`; default optimization |
| knowns | No | JSON of known quantities, e.g. `{"routes": 50, "trucks": 5}` |
| unknowns | No | List of variable names to solve for, e.g. `route_assignment truck_schedule` |

When missing, ask all at once: "Please provide: (1) problem (prose description). I'll use defaults or auto-infer domain / knowns / unknowns."

## Pre-flight Checks

```bash
# 1. Python available
python3 --version
# 2. Script exists
test -f scripts/model_formulator.py && echo "OK script present"
```

- Expected: `python3 --version` prints a version number; the script exists and prints `OK script present`.
- On failure: Python not installed → install Python 3.10+ and retry; script missing → STOP and report the script wasn't shipped with the skill.

## Workflow

### Step 1: Parse and classify the problem

- Action: extract entities, quantities, and relationships from the problem, and determine the domain (deterministic vs stochastic, continuous vs discrete).
- Expected: get a `domain` and an initial candidate model type (see the decision tree).
- On failure: the description is too vague → return to the input checklist to request more problem detail; don't guess.

### Step 2: Define variables and constraints

- Action: list decision variables, state variables, the objective function, and all physical/logical constraints.
- Expected: every variable has an explicit type (e.g. binary / continuous) and meaning.
- On failure: conflicting constraints → flag as an assumption, or go back to Step 1 to reclassify.

### Step 3: Choose a model type and generate the spec

- Action: run the script to generate a structured spec.

```bash
python3 scripts/model_formulator.py \
  --problem "Minimize delivery cost for 50 routes, 5 trucks, time windows 8-18h" \
  --domain optimization \
  --knowns '{"routes": 50, "deliveries": 200, "trucks": 5}' \
  --unknowns route_assignment truck_schedule total_cost \
  --output model_spec.json
```

- Expected: stdout prints a JSON blob with `model_type`, `variables`, `objective`, `constraints`, `assumptions`, `solver_hint`; if `--output` is given, it is also written to that file.
- On failure: an argparse error (e.g. domain not in choices) → check valid values with `--help`; a network/file error → fix the path and retry.

### Step 4: Model-type decision

```text
Deterministic?
├── Yes → Continuous? → ODE/PDE or nonlinear optimization
│        └ No → ILP / combinatorial optimization
└── No → Time-series? → Markov chain / MDP / simulation
          └ No → Bayesian / statistical
```

- Action: confirm `model_type` against the decision tree and write `solver_hint` (`cvxpy | scipy.optimize | pulp | ortools`).
- Expected: `solver_hint` is consistent with `model_type`.
- On failure: the type is uncertain → explicitly flag the simplifying assumption in `assumptions`.

## Output Format

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

## Parameter Cheat Sheet

| Parameter | Values | Description |
|------|------|------|
| --problem | string | Required, the prose problem |
| --domain | optimization/differential/statistical/stochastic/bayesian | Default optimization |
| --knowns | JSON string | Known quantities |
| --unknowns | multiple strings | Variable names to solve for |
| --output | file path | Optional, write the spec JSON |

## Failure Handling Table

| Symptom / error code | Cause | Action |
|------------|------|------|
| `error: argument --domain: invalid choice` | domain misspelled | Check the 5 valid values with `--help` |
| Output lacks `constraints` | The problem statement has no boundary conditions | Return to the input checklist to complete the constraint description |
| `solver_hint` doesn't match `model_type` | Wrong decision-tree judgment | Hand-check the decision tree and rewrite the spec |
| The problem description is ambiguous, variables can't be set | Input has only a desired outcome, no data and no decision objects | Go back to the user to complete decision variables, value ranges, and constraint sources, then formalize |
| `objective` direction reversed | min/max opposite to business semantics | Re-check the direction against the goal description and regenerate the spec |
| Model type chosen as LP but contains integer variables | Subscript or count-type variables were ignored | Re-judge as ILP/MIP and add an `integrality` field |

## Delivery Criteria

- Definition of success: output JSON containing `model_type` + non-empty `variables` + `objective` + at least 1 `constraints`.
- Artifact naming: `model_spec.json` (or a user-specified path).
- Save location: current working directory, or the path specified by `--output`.
- Completeness verification: confirm with `python3 -c "import json,sys; json.load(open('<path>'))"` that the JSON parses and contains the fields above; then hand it to model-solver.

## References

- references/model-types.md — read when choosing a model type or browsing examples of each
- references/notation-guide.md — read for symbol conventions when writing variables/objectives
