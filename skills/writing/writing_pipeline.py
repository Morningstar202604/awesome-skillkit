#!/usr/bin/env python3
"""Writing Domain Pipeline — 文章写作全流程编排。

独立领域，不使用编程/视频领域的 skill。

用法:
  python3 writing_pipeline.py --topic "FastAPI 性能优化" --platforms csdn wechat
  python3 writing_pipeline.py --topic "..." --dry-run
"""
import argparse
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
SCRIPTS = {
    "outliner": BASE / "article-outliner" / "scripts" / "outliner.py",
    "drafter": BASE / "article-drafter" / "scripts" / "drafter.py",
    "editor": BASE / "content-editor" / "scripts" / "editor.py",
    "seo": BASE / "seo-optimizer" / "scripts" / "seo_optimizer.py",
}


def run_step(name: str, cmd: list, dry_run: bool = False) -> dict:
    if dry_run:
        return {"step": name, "status": "planned", "cmd": " ".join(cmd[:3])}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        status = "success" if r.returncode == 0 else "error"
        data = {}
        if r.returncode == 0 and r.stdout:
            try:
                data = json.loads(r.stdout)
            except json.JSONDecodeError:
                data = {"raw": r.stdout[:500]}
        return {"step": name, "status": status, "data": data,
                "error": r.stderr[:300] if r.returncode != 0 else None}
    except Exception as e:
        return {"step": name, "status": "error", "error": str(e)}


def run_pipeline(topic: str, article_type: str = "technical",
                 platforms: list = None, dry_run: bool = False) -> dict:
    steps = []
    out_dir = Path(f"/tmp/article_{datetime.now().strftime('%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    platforms = platforms or ["csdn"]
    outline_file = out_dir / "outline.json"
    draft_file = out_dir / "draft.json"
    edited_file = out_dir / "edited.json"

    # Step 1: Outline
    cmd = [sys.executable, str(SCRIPTS["outliner"]),
           "--topic", topic, "--type", article_type,
           "--platforms"] + platforms + ["--output", str(outline_file)]
    steps.append(run_step("outline", cmd, dry_run))

    # Step 2: Draft
    cmd = [sys.executable, str(SCRIPTS["drafter"]),
           "--outline", str(outline_file), "--output", str(draft_file)]
    steps.append(run_step("draft", cmd, dry_run))

    # Step 3: Edit (产物落盘，下游 seo/publish 读编辑后稿)
    cmd = [sys.executable, str(SCRIPTS["editor"]),
           "--draft", str(draft_file), "--style", "technical",
           "--output", str(edited_file)]
    steps.append(run_step("edit", cmd, dry_run))

    # Step 4: SEO
    cmd = [sys.executable, str(SCRIPTS["seo"]),
           "--title", topic, "--content", str(edited_file),
           "--platform", platforms[0]]
    steps.append(run_step("seo", cmd, dry_run))

    # Step 5: Publish (requires credentials)
    for plat in platforms:
        cmd = [f"[{plat}-publisher]"]
        steps.append(run_step(f"publish_{plat}", cmd, dry_run or True))

    success = sum(1 for s in steps if s["status"] == "success")
    return {
        "topic": topic,
        "type": article_type,
        "platforms": platforms,
        "output_dir": str(out_dir),
        "steps": steps,
        "completed": success,
        "total": len(steps),
        "status": "complete" if success >= 4 else "partial",
    }


def main():
    parser = argparse.ArgumentParser(description="Writing production pipeline")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--type", default="technical")
    parser.add_argument("--platforms", nargs="*", default=["csdn"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.topic, args.type, args.platforms, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Writing Pipeline: {args.topic}")
        print(f"Type: {args.type} | Platforms: {', '.join(args.platforms)}")
        print()
        for s in result["steps"]:
            icon = {"success": "✓", "planned": "□", "error": "✗"}.get(s["status"], "?")
            err = f" — {s.get('error', '')[:40]}" if s.get("error") else ""
            print(f"  {icon} {s['step']}: {s['status']}{err}")
        print(f"\nCompleted: {result['completed']}/{result['total']}")
        print(f"Output: {result['output_dir']}")


if __name__ == "__main__":
    main()
