#!/usr/bin/env python3
"""Paper Domain Pipeline — 论文全流程编排。

topic → lit-review → experiment → figures → latex → self-review

用法:
  python3 paper_pipeline.py --topic "LLM agent coordination"
  python3 paper_pipeline.py --topic "..." --dry-run
"""
import argparse
import json
import sys
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPTS = {
    "topic": BASE / "paper-topic-selector" / "scripts" / "topic_selector.py",
    "lit": BASE / "lit-review" / "scripts" / "lit_review.py",
    "experiment": BASE / "experiment-runner" / "scripts" / "experiment_runner.py",
    "figures": BASE / "figure-maker" / "scripts" / "figure_maker.py",
    "latex": BASE / "latex-formatter" / "scripts" / "latex_formatter.py",
    "review": BASE / "self-reviewer" / "scripts" / "self_reviewer.py",
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


def run_pipeline(topic: str, dry_run: bool = False) -> dict:
    safe_name = topic.replace(" ", "_")[:20]
    out_dir = Path(tempfile.gettempdir()) / f"paper_{safe_name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    lit_file = out_dir / "lit_review.json"
    exp_file = out_dir / "experiment_results.json"

    steps = []

    # 1. Topic validation
    steps.append(run_step("topic", [sys.executable, str(SCRIPTS["topic"]),
                                     "--topic", topic], dry_run))

    # 2. Literature review
    steps.append(run_step("lit_review", [sys.executable, str(SCRIPTS["lit"]),
                                         "--topic", topic,
                                         "--output", str(lit_file)], dry_run))

    # 3. Run experiments
    steps.append(run_step("experiment", [sys.executable, str(SCRIPTS["experiment"]),
                                         "--n-runs", "5",
                                         "--output", str(exp_file)], dry_run))

    # 4. Make figures
    steps.append(run_step("figures", [sys.executable, str(SCRIPTS["figures"]),
                                      "--data", str(exp_file), "--type", "bar",
                                      "--output", str(out_dir / "fig1.pdf")], dry_run))

    # 5. LaTeX check
    tex_file = out_dir / "draft.tex"
    if not tex_file.exists() and not dry_run:
        tex_file.write_text(
            "\\documentclass{article}\\begin{document}\\title{Draft}\\begin{document}\\end{document}\n",
            encoding="utf-8")
    steps.append(run_step("latex", [sys.executable, str(SCRIPTS["latex"]),
                                    "--input", str(tex_file), "--template", "ieee"], dry_run))

    # 6. Self-review
    steps.append(run_step("self_review", [sys.executable, str(SCRIPTS["review"]),
                                          "--paper", str(tex_file)], dry_run))

    success = sum(1 for s in steps if s["status"] == "success")
    return {
        "topic": topic,
        "steps": steps,
        "completed": success,
        "total": len(steps),
        "output_dir": str(out_dir),
        "status": "complete" if success == len(steps) else "partial",
    }


def main():
    parser = argparse.ArgumentParser(description="Paper production pipeline")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.topic, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Paper Pipeline: {args.topic}")
        print()
        for s in result["steps"]:
            icon = {"success": "✓", "planned": "□", "error": "✗"}.get(s["status"], "?")
            err = f" — {s.get('error', '')[:40]}" if s.get("error") else ""
            print(f"  {icon} {s['step']}: {s['status']}{err}")
        print(f"\nCompleted: {result['completed']}/{result['total']}")
        print(f"Output: {result['output_dir']}")


if __name__ == "__main__":
    main()
