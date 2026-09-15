#!/usr/bin/env python3
"""Model Formulator — 把问题转化为数学模型规格。

用法:
  python3 model_formulator.py --problem "..." --domain optimization
  python3 model_formulator.py --json '{"problem":"...","domain":"stochastic"}'
"""
import argparse
import json
import sys
from pathlib import Path

DOMAINS = {
    "optimization": {
        "model_types": ["LP", "ILP", "NLP", "MIP", "VRP", "TSP"],
        "solvers": ["cvxpy", "scipy.optimize", "pulp", "ortools"],
    },
    "differential": {
        "model_types": ["ODE", "PDE", "DDE", "algebraic"],
        "solvers": ["scipy.integrate", "matplotlib", "finite_diff"],
    },
    "statistical": {
        "model_types": ["regression", "hypothesis_test", "time_series", "clustering"],
        "solvers": ["scipy.stats", "statsmodels", "sklearn"],
    },
    "stochastic": {
        "model_types": ["markov_chain", "monte_carlo", "queue", "random_walk"],
        "solvers": ["numpy.random", "simpy", "custom"],
    },
    "bayesian": {
        "model_types": ["prior_posterior", "mcmc", "variational"],
        "solvers": ["pymc", "bayesopt", "custom"],
    },
}


def formulate(problem: str, domain: str = "optimization",
              knowns: dict = None, unknowns: list = None) -> dict:
    """Generate model spec from problem description."""
    domain_conf = DOMAINS.get(domain, DOMAINS["optimization"])

    spec = {
        "problem": problem,
        "domain": domain,
        "model_type": domain_conf["model_types"][0],
        "variables": {},
        "objective": f"Define based on: {problem}",
        "constraints": [],
        "assumptions": ["Determined during formulation"],
        "knowns": knowns or {},
        "unknowns": unknowns or [],
        "solver_hint": domain_conf["solvers"][0],
        "status": "spec_ready",
        "next_step": "model-solver",
    }

    # Simple heuristic: if problem mentions "minimize" or "maximize", it's optimization
    if any(w in problem.lower() for w in ["minimize", "maximize", "cost", "profit", "time"]):
        spec["model_type"] = "MIP" if "integer" in problem.lower() or "assign" in problem.lower() else "LP"
    if any(w in problem.lower() for w in ["rate", "flow", "change", "growth"]):
        spec["domain"] = "differential"
        spec["model_type"] = "ODE"
    if any(w in problem.lower() for w in ["probability", "random", "uncertain", "risk"]):
        spec["domain"] = "stochastic"
        spec["model_type"] = "monte_carlo"

    return spec


def main():
    parser = argparse.ArgumentParser(description="Formulate math model")
    parser.add_argument("--problem", required=True)
    parser.add_argument("--domain", default="optimization", choices=list(DOMAINS.keys()))
    parser.add_argument("--knowns", help="JSON of known parameters")
    parser.add_argument("--unknowns", nargs="*", help="Unknown variables")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.knowns:
        try:
            knowns = json.loads(args.knowns)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON in --knowns: {e}", file=sys.stderr)
            return 1
    else:
        knowns = None
    spec = formulate(args.problem, args.domain, knowns, args.unknowns)

    output = json.dumps(spec, ensure_ascii=False, indent=2)
    if args.output:
        try:
            Path(args.output).write_text(output, encoding="utf-8")
        except OSError as e:
            print(f"Error: cannot write output file: {e}", file=sys.stderr)
            return 1
        print(f"Model spec written to: {args.output}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
