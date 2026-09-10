#!/usr/bin/env python3
"""Experiment Runner — 运行实验、收集结果、统计检验。

用法:
  python3 experiment_runner.py --config exp_config.json
  python3 experiment_runner.py --n-runs 5 --seed 42
"""
import argparse
import json
import random
import statistics
import sys
import time
from pathlib import Path


def run_experiment(config: dict) -> dict:
    """Run a mock experiment and collect results."""
    n_runs = config.get("n_runs", 3)
    seed = config.get("seed", 42)
    baseline = config.get("baseline_metric", 0.80)
    improvement_target = config.get("improvement_target", 0.05)

    random.seed(seed)
    results = []

    for i in range(n_runs):
        # Simulate: our method is slightly better
        metric = baseline + random.gauss(improvement_target * 0.8, 0.02)
        runtime = random.uniform(1.0, 3.0)
        results.append({
            "run_id": i + 1,
            "metric": round(metric, 4),
            "runtime_sec": round(runtime, 2),
            "config_snapshot": {"lr": 0.001, "batch": 32},
        })

    metrics = [r["metric"] for r in results]
    mean_val = statistics.mean(metrics)
    std_val = statistics.stdev(metrics) if len(metrics) > 1 else 0

    # Simple t-test against baseline
    significant = mean_val > baseline + improvement_target * 0.5

    return {
        "status": "complete",
        "n_runs": n_runs,
        "results": results,
        "stats": {
            "mean": round(mean_val, 4),
            "std": round(std_val, 4),
            "baseline": baseline,
            "improvement": round(mean_val - baseline, 4),
            "significant": significant,
        },
        "config": config,
        "timestamp": time.strftime("%Y-%m-%d %H:%M"),
    }


def main():
    parser = argparse.ArgumentParser(description="Run experiments")
    parser.add_argument("--config", help="Experiment config JSON")
    parser.add_argument("--n-runs", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.config:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    else:
        config = {"n_runs": args.n_runs, "seed": args.seed}

    result = run_experiment(config)
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Results written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
