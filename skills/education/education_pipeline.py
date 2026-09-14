#!/usr/bin/env python3
"""Education Domain Pipeline — 教学全流程编排。

独立领域，不使用编程/视频领域的 skill。链条：课程骨架 → 习题 → 费曼补救。

用法:
  python3 education_pipeline.py --topic "深度学习入门" --level beginner
  python3 education_pipeline.py --topic "..." --mode full_course --dry-run
"""
import argparse
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
STEPS = {
    "course": ("course-designer", "学习契约(≤3问) + checkpoint 依赖排序 + 深度控制"),
    "exercise": ("exercise-generator", "每 checkpoint 开放题题库（禁选择题防蒙，附 rubric），过 exercise_lint"),
    "feynman": ("feynman-explainer", "未通过 checkpoint 的费曼六拍补救，通过后重测闭环"),
}

MODES = {
    "full_course": ["course", "exercise"],
    "topic_mastery": ["course", "exercise", "feynman"],
    "remedial_only": ["feynman"],
}


def run_pipeline(topic: str, mode: str = "full_course", level: str = "beginner",
                 dry_run: bool = False) -> dict:
    steps = []
    out_dir = Path(f"/tmp/edu_{datetime.now().strftime('%H%M%S')}")
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for name in MODES.get(mode, MODES["full_course"]):
        skill, action = STEPS[name]
        detail = {
            "course": f"topic={topic} | level={level} | checkpoint 只依赖已通过项",
            "exercise": "概念解释 2 + 应用 2 + 迁移 1 | 评分标准与题同出",
            "feynman": "六拍循环 + '不太聪明的学生'模式 | 通过后回 exercise 重测",
        }[name]
        steps.append({"step": name, "skill": skill, "status": "planned",
                      "action": action, "detail": detail})

    return {
        "topic": topic, "mode": mode, "level": level,
        "output_dir": str(out_dir) if not dry_run else "(dry-run)",
        "steps": steps,
        "chain_note": "掌握闭环：checkpoint 测不过 → feynman 六拍重教 → exercise 换角度重测，"
                      "直到通过为止；全通过则课程包交付。",
    }


def main():
    parser = argparse.ArgumentParser(description="Education pipeline")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--mode", default="full_course",
                        choices=["full_course", "topic_mastery", "remedial_only"])
    parser.add_argument("--level", default="beginner",
                        choices=["beginner", "intermediate", "advanced", "exam"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.topic, args.mode, args.level, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# Education Pipeline: {args.topic}")
        print(f"Mode: {args.mode} | Level: {args.level}")
        print()
        for s in result["steps"]:
            print(f"  □ {s['step']} [{s['skill']}] {s['action']}")
            print(f"      {s['detail']}")
        print(f"\nOutput: {result['output_dir']}")
        print(result["chain_note"])


if __name__ == "__main__":
    main()
