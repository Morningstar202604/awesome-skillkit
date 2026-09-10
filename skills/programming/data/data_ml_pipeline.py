#!/usr/bin/env python3
"""Data + ML Pipeline — 数据→特征→模型 一键流程。

etl-builder → feature-engineer → ml-pipeline

用法:
  python3 data_ml_pipeline.py --data data/raw.csv --target label
  python3 data_ml_pipeline.py --data ... --model gradient_boosting
"""
import argparse
import json
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROG = BASE.parent
SCRIPTS = {
    "etl": BASE / "etl-builder" / "scripts" / "etl_builder.py",
    "features": BASE / "feature-engineer" / "scripts" / "feature_engineer.py",
    "ml": PROG / "ml" / "pipeline" / "scripts" / "ml_pipeline.py",
}


def run_step(name: str, cmd: list, dry_run: bool = False) -> dict:
    if dry_run:
        return {"step": name, "status": "planned"}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
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


def run_pipeline(data: str, target: str = "label",
                 model: str = "random_forest", dry_run: bool = False) -> dict:
    out_dir = Path("/tmp") / f"data_ml_{Path(data).stem}"
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_data = out_dir / "clean.csv"
    feature_plan = out_dir / "features.json"

    steps = []

    # 1. ETL
    cmd = [sys.executable, str(SCRIPTS["etl"]),
           "--source", data, "--target", str(clean_data),
           "--transform", "dropna,fillna_median,normalize"]
    steps.append(run_step("etl", cmd, dry_run))

    # 2. Feature Engineering
    cmd = [sys.executable, str(SCRIPTS["features"]),
           "--data", str(clean_data), "--target", target,
           "--output", str(feature_plan)]
    steps.append(run_step("features", cmd, dry_run))

    # 3. ML Training
    cmd = [sys.executable, str(SCRIPTS["ml"]),
           "--data", str(clean_data), "--target", target,
           "--model", model]
    steps.append(run_step("ml_train", cmd, dry_run))

    success = sum(1 for s in steps if s["status"] == "success")
    return {
        "data": data,
        "target": target,
        "model": model,
        "steps": steps,
        "completed": success,
        "total": len(steps),
        "output_dir": str(out_dir),
        "status": "complete" if success == len(steps) else "partial",
    }


def main():
    parser = argparse.ArgumentParser(description="Data + ML pipeline")
    parser.add_argument("--data", required=True)
    parser.add_argument("--target", default="label")
    parser.add_argument("--model", default="random_forest",
                        choices=["random_forest", "gradient_boosting", "logistic"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.data, args.target, args.model, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Data+ML Pipeline: {args.data}")
        print(f"Model: {args.model} | Target: {args.target}")
        print()
        for s in result["steps"]:
            icon = {"success": "✓", "planned": "□", "error": "✗"}.get(s["status"], "?")
            err = f" — {s.get('error', '')[:40]}" if s.get("error") else ""
            print(f"  {icon} {s['step']}: {s['status']}{err}")
        print(f"\nCompleted: {result['completed']}/{result['total']}")


if __name__ == "__main__":
    main()
