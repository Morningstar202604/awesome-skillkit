#!/usr/bin/env python3
"""benchmark.py — measure skill-router accuracy over benchmark_tasks.json.

Metrics:
  top1  : expected skill ranked #1
  top3  : any expected skill in top-3
  noneFP: none-tasks (should be NO SKILL) that came back USE
Prints every miss with its ranking so tuning is evidence-driven.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import skill_router  # noqa: E402


def main(argv: list[str]) -> int:
    skills_dir = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[3] / "skills"
    cases = json.loads((Path(__file__).parent / "benchmark_tasks.json").read_text(encoding="utf-8"))["cases"]
    index = skill_router.build_index(skills_dir)

    n_use = top1 = top3 = 0
    n_none = fp = 0
    misses = []
    for c in cases:
        r = skill_router.route(c["task"], index, top=3)
        got = [x["skill"] for x in r["results"]]
        if c.get("none"):
            n_none += 1
            if r["verdict"] == "USE SKILLS":
                fp += 1
                misses.append(f"[none 误报 USE] {c['task']} -> {got}")
        else:
            n_use += 1
            exp = set(c["expect"])
            if got and got[0] in exp:
                top1 += 1
                top3 += 1
            elif got and exp & set(got):
                top3 += 1
                misses.append(f"[top3] {c['task']} -> {got} (期望 {c['expect']})")
            else:
                misses.append(f"[MISS] {c['task']} -> {got} (期望 {c['expect']})")

    print(f"use-tasks: {n_use}  top1={top1} ({top1/n_use:.0%})  top3={top3} ({top3/n_use:.0%})")
    print(f"none-tasks: {n_none}  误报 USE={fp} ({fp/n_none:.0%})")
    print("--- misses ---")
    for m in misses:
        print(" ", m)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
