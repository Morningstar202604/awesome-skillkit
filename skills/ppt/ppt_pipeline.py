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
from datetime import datetime

BASE = Path(__file__).resolve().parent
PPT_BUILDER = BASE / "ppt-builder" / "scripts"


def run_ppt_step(step: str, cmd: list, dry_run: bool = False) -> dict:
    """执行一步；cmd 为完整命令 [python, script, ...]，脚本存在性以 cmd[1] 为准。"""
    if dry_run:
        return {"step": step, "status": "planned"}
    script = Path(cmd[1]) if len(cmd) > 1 else None
    if script is None or not script.exists():
        return {"step": step, "status": "skipped", "reason": "script not found"}
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


def build_spec(topic: str, audience: str, slides: int) -> dict:
    """生成 make_pptx.py 可消费的最小合法 spec 骨架。

    bullets 为占位要点，正文由 LLM 依 ppt-builder SKILL.md 填充。
    """
    content_slides = max(1, slides - 1)  # 封面由 make_pptx 自动生成
    return {
        "deck_title": topic,
        "slides": [
            {"title": f"{topic} · 第{i}节（{audience}向）",
             "bullets": ["（要点待 LLM 填充——参照 ppt-builder SKILL.md 叙事线）"],
             "notes": ""}
            for i in range(1, content_slides + 1)
        ],
    }


def run_pipeline(topic: str, audience: str = "同行", slides: int = 12,
                 dry_run: bool = False) -> dict:
    steps = []
    out = Path(f"/tmp/ppt_{datetime.now().strftime('%H%M%S')}")
    out.mkdir(parents=True, exist_ok=True)
    spec_file = out / "spec.json"

    # 1. Outline：编排器生成合法 spec 骨架落盘
    spec = build_spec(topic, audience, slides)
    steps.append({"step": "outline", "status": "planned" if dry_run else "success",
                  "data": {"content_slides": len(spec["slides"]),
                           "note": "spec 骨架已生成，bullets 待 LLM 填充"}})
    if not dry_run:
        spec_file.write_text(json.dumps(spec, ensure_ascii=False, indent=2),
                             encoding="utf-8")

    # 2. Visual / assets / rehearsal 属 LLM 职责，不做假脚本调用
    steps.append({"step": "visual_assets_rehearsal", "status": "manual",
                  "note": "视觉设计/素材清单/彩排笔记由 LLM 依 ppt-builder 技能完成"})

    # 3. Render：真实调用 make_pptx.py（位置参数 spec out）
    cmd = [sys.executable, str(PPT_BUILDER / "make_pptx.py"),
           str(spec_file), str(out / "final.pptx")]
    steps.append(run_ppt_step("render", cmd, dry_run))

    automated = [s for s in steps if s["status"] != "manual"]
    success = sum(1 for s in automated if s["status"] == "success")
    return {
        "topic": topic, "audience": audience, "slides": slides,
        "steps": steps, "completed": success, "total": len(steps),
        "output_dir": str(out),
        "status": "complete" if success == len(automated) else "partial",
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
