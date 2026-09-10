#!/usr/bin/env python3
"""Math Pipeline — 数学建模全流程。

formulator → solver → simulation → visualizer

用法:
  python3 math_pipeline.py --problem "最小化配送成本" --domain optimization
  python3 math_pipeline.py --problem "..." --monte-carlo
"""
import argparse
import json
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPTS = {
    "formulator": BASE / "model-formulator" / "scripts" / "model_formulator.py",
    "solver": BASE / "model-solver" / "scripts" / "model_solver.py",
    "simulation": BASE / "simulation" / "scripts" / "simulation.py",
    "visualizer": BASE / "visualizer" / "scripts" / "visualizer.py",
}


def run_step(name: str, cmd: list, dry_run: bool = False) -> dict:
    if dry_run:
        return {"step": name, "status": "planned"}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        status = "success" if r.returncode == 0 else "error"
        data = {}
        if r.returncode == 0 and r.stdout:
            try:
                data = json.loads(r.stdout)
            except json.JSONDecodeError:
                data = {"raw": r.stdout[:300]}
        return {"step": name, "status": status, "data": data,
                "error": r.stderr[:300] if r.returncode != 0 else None}
    except Exception as e:
        return {"step": name, "status": "error", "error": str(e)}


def run_pipeline(problem: str, domain: str = "optimization",
                 monte_carlo: bool = False, dry_run: bool = False) -> dict:
    out_dir = Path(f"/tmp/math_{int(Path(__file__).stat().st_mtime)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    spec_file = out_dir / "model_spec.json"
    result_file = out_dir / "results.json"

    steps = []

    # 1. Formulate
    cmd = [sys.executable, str(SCRIPTS["formulator"]),
           "--problem", problem, "--domain", domain,
           "--output", str(spec_file)]
    steps.append(run_step("formulate", cmd, dry_run))

    # 2. Solve
    if monte_carlo:
        cmd = [sys.executable, str(SCRIPTS["simulation"]),
               "--monte-carlo", "--n", "10000",
               "--output", str(result_file)]
    else:
        cmd = [sys.executable, str(SCRIPTS["solver"]),
               "--spec", str(spec_file),
               "--output", str(result_file)]
    steps.append(run_step("solve", cmd, dry_run))

    # 3. Simulate / Sensitivity
    cmd = [sys.executable, str(SCRIPTS["simulation"]),
           "--spec", str(spec_file),
           "--param", "rate", "--range", "0.1", "5.0", "--steps", "5"]
    steps.append(run_step("simulate", cmd, dry_run))

    # 4. Visualize
    cmd = [sys.executable, str(SCRIPTS["visualizer"]),
           "--data", str(result_file), "--type", "line",
           "--output", str(out_dir / "plot.png")]
    steps.append(run_step("visualize", cmd, dry_run))

    success = sum(1 for s in steps if s["status"] == "success")
    return {
        "problem": problem,
        "domain": domain,
        "steps": steps,
        "completed": success,
        "total": len(steps),
        "output_dir": str(out_dir),
        "status": "complete" if success == len(steps) else "partial",
    }


def main():
    parser = argparse.ArgumentParser(description="Math modeling pipeline")
    parser.add_argument("--problem", required=True)
    parser.add_argument("--domain", default="optimization",
                        choices=["optimization", "differential", "statistical", "stochastic", "bayesian"])
    parser.add_argument("--monte-carlo", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.problem, args.domain, args.monte_carlo, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Math Pipeline: {args.problem}")
        print(f"Domain: {args.domain}")
        print()
        for s in result["steps"]:
            icon = {"success": "✓", "planned": "□", "error": "✗"}.get(s["status"], "?")
            err = f" — {s.get('error', '')[:40]}" if s.get("error") else ""
            print(f"  {icon} {s['step']}: {s['status']}{err}")
        print(f"\nCompleted: {result['completed']}/{result['total']}")


if __name__ == "__main__":
    main()
