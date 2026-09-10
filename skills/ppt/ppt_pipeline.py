#!/usr/bin/env python3
"""PPT Domain Pipeline — 演示文稿制作全流程。

独立领域。调用 ppt-builder 子 skills 完成完整 PPT 制作。

用法:
  python3 ppt_pipeline.py --topic "项目汇报" --audience "高管" --slides 15
  python3 ppt_pipeline.py --topic "..." --dry-run
"""
import argparse
import json
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
PPT_BUILDER = BASE / "ppt-builder" / "scripts"


def run_ppt_step(step: str, args: list, dry_run: bool = False) -> dict:
    if dry_run:
        return {"step": step, "status": "planned"}
    script = PPT_BUILDER / f"{step}.py"
    if not script.exists():
        return {"step": step, "status": "skipped", "reason": "script not found"}
    cmd = [sys.executable, str(script)] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        status = "success" if r.returncode == 0 else "error"
        data = {}
        if r.returncode == 0 and r.stdout:
            try:
                data = json.loads(r.stdout)
            except json.JSONDecodeError:
                data = {"raw": r.stdout[:300]}
        return {"step": step, "status": status, "data": data,
                "error": r.stderr[:200] if r.returncode != 0 else None}
    except Exception as e:
        return {"step": step, "status": "error", "error": str(e)}


def run_pipeline(topic: str, audience: str = "同行", slides: int = 12,
                 dry_run: bool = False) -> dict:
    steps = []
    out = Path(f"/tmp/ppt_{topic[:10]}")
    out.mkdir(parents=True, exist_ok=True)

    # 1. Outline
    steps.append(run_ppt_step("outline", ["--topic", topic, "--audience", audience,
                                          "--slides", str(slides)], dry_run))

    # 2. Visual design
    steps.append(run_ppt_step("visual", ["--spec", str(out / "spec.json")], dry_run))

    # 3. Assets
    steps.append(run_ppt_step("assets", ["--spec", str(out / "spec.json")], dry_run))

    # 4. Rehearsal notes
    steps.append(run_ppt_step("rehearsal", ["--spec", str(out / "spec.json")], dry_run))

    # 5. Render
    steps.append(run_ppt_step("render", ["--spec", str(out / "spec.json"),
                                          "--output", str(out / "final.pptx")], dry_run))

    success = sum(1 for s in steps if s["status"] == "success")
    return {
        "topic": topic, "audience": audience, "slides": slides,
        "steps": steps, "completed": success, "total": len(steps),
        "output_dir": str(out),
        "status": "complete" if success == len(steps) else "partial",
    }


def main():
    parser = argparse.ArgumentParser(description="PPT production pipeline")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--audience", default="同行")
    parser.add_argument("--slides", type=int, default=12)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.topic, args.audience, args.slides, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# PPT Pipeline: {args.topic}")
        print(f"Audience: {args.audience} | Slides: {args.slides}")
        print()
        for s in result["steps"]:
            icon = {"success": "✓", "planned": "□", "skipped": "○", "error": "✗"}.get(s["status"], "?")
            print(f"  {icon} {s['step']}: {s['status']}")
        print(f"\nCompleted: {result['completed']}/{result['total']}")


if __name__ == "__main__":
    main()
