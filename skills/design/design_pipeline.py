#!/usr/bin/env python3
"""Design Domain Pipeline — 视觉设计全流程编排。

独立领域，不使用编程/视频领域的 skill。链条：规格单 → prompt → 规格审计。

用法:
  python3 design_pipeline.py --brief "公众号封面：AI 视频这一年" --platform wechat-header
  python3 design_pipeline.py --brief "..." --type poster --dry-run
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
STEPS = {
    "spec": ("design-brief-interpreter", "把粗需求翻译成 7 字段设计规格单（platform 字段锁定画布）"),
    "prompt": ("image-prompt-engineer", "按规格单写五段式 prompt，文字逐字引号包裹"),
    "audit": ("layout-spec-auditor", "产出图后跑平台规格审计（比例/分辨率/安全区/文字预算）"),
}


def run_pipeline(brief: str, design_type: str = "cover", platform: str = None,
                 model: str = None, dry_run: bool = False) -> dict:
    steps = []
    out_dir = Path(f"/tmp/design_{datetime.now().strftime('%H%M%S')}")
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    plan = []
    for name, (skill, action) in STEPS.items():
        if name == "spec":
            detail = f"{brief} | type={design_type}" + (f" | platform={platform}" if platform else "")
        elif name == "prompt":
            detail = f"输入=步骤1规格单" + (f" | model={model}" if model else " | 通用结构")
        else:
            detail = f"按规格单 platform 字段审计（有产出图后执行）"
        plan.append({"step": name, "skill": skill, "action": action, "detail": detail})

    for s in plan:
        steps.append({
            "step": s["step"], "skill": s["skill"], "status": "planned",
            "action": s["action"], "detail": s["detail"],
        })

    return {
        "brief": brief,
        "design_type": design_type,
        "platform": platform,
        "model": model,
        "output_dir": str(out_dir) if not dry_run else "(dry-run)",
        "steps": steps,
        "chain_note": "每步产出的工件自动作为下一步输入：spec → prompt → audit；"
                      "audit 不过则按失败处置表回流对应步骤。",
    }


def main():
    parser = argparse.ArgumentParser(description="Visual design pipeline")
    parser.add_argument("--brief", required=True, help="粗需求一句话")
    parser.add_argument("--type", default="cover",
                        choices=["cover", "poster", "infographic", "thumbnail", "banner"])
    parser.add_argument("--platform", default=None,
                        help="wechat-header / xhs-portrait / bilibili-cover / ...")
    parser.add_argument("--model", default=None, help="目标生图模型方言")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.brief, args.type, args.platform, args.model, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Design Pipeline: {args.brief}")
        print(f"Type: {args.type} | Platform: {args.platform or '(未定, 步骤1询问)'}")
        print()
        for s in result["steps"]:
            print(f"  □ {s['step']} [{s['skill']}] {s['action']}")
            print(f"      {s['detail']}")
        print(f"\nOutput: {result['output_dir']}")
        print(result["chain_note"])


if __name__ == "__main__":
    main()
