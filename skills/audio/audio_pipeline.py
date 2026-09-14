#!/usr/bin/env python3
"""Audio Domain Pipeline — 播客/音频全流程编排。

独立领域，不使用编程/视频领域的 skill。链条：脚本 → 声音执导 → 发布件。

用法:
  python3 audio_pipeline.py --topic "AI 视频这一年" --duration 5 --dialogue
  python3 audio_pipeline.py --doc article.md --type document_to_podcast --dry-run
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
STEPS = {
    "script": ("podcast-producer", "钩子→三段→CTA 大纲，逐段纯口播词脚本（过 script_lint）"),
    "voice": ("tts-voice-director", "按气质→声音 ID 选角，定语速参数，排 ffmpeg 拼接计划"),
    "publish": ("episode-publisher", "shownotes + 时间戳章节 + 平台元数据 + AI 披露"),
}


def run_pipeline(topic: str = None, doc: str = None, episode_type: str = "narration",
                 duration: int = 5, dialogue: bool = False, dry_run: bool = False) -> dict:
    if not topic and not doc:
        raise SystemExit("need --topic or --doc")
    steps = []
    out_dir = Path(f"/tmp/audio_{datetime.now().strftime('%H%M%S')}")
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    source = f"doc={doc}" if doc else f"topic={topic}"
    lint_cmd = f"python3 podcast-producer/scripts/script_lint.py --file script.md" + (" --dialogue" if dialogue else "")

    plan = []
    for name, (skill, action) in STEPS.items():
        if name == "script":
            detail = f"{source} | {episode_type} | {duration}min | lint: {lint_cmd}"
        elif name == "voice":
            detail = "输入=步骤1分段脚本 | 查 voice-catalog.md 选角 | 逐段合成 ffmpeg concat"
        else:
            detail = "输入=脚本+合成计划 | shownotes/章节/元数据/AI 披露"
        plan.append({"step": name, "skill": skill, "action": action, "detail": detail})

    for s in plan:
        steps.append({
            "step": s["step"], "skill": s["skill"], "status": "planned",
            "action": s["action"], "detail": s["detail"],
        })

    return {
        "topic": topic, "doc": doc,
        "episode_type": episode_type,
        "duration_min": duration,
        "dialogue": dialogue,
        "output_dir": str(out_dir) if not dry_run else "(dry-run)",
        "steps": steps,
        "chain_note": "工件流转：script.md(过 lint) → 合成计划+音频段 → shownotes+chapters+元数据；"
                      "任一步不过按该技能失败处置表回流。",
    }


def main():
    parser = argparse.ArgumentParser(description="Audio production pipeline")
    parser.add_argument("--topic", help="选题一句话")
    parser.add_argument("--doc", help="源文档路径（文档转播客）")
    parser.add_argument("--type", default="narration",
                        choices=["narration", "document_to_podcast", "audiobook_chapter"])
    parser.add_argument("--duration", type=int, default=5, help="目标分钟数")
    parser.add_argument("--dialogue", action="store_true", help="双人对话形态")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_pipeline(args.topic, args.doc, args.type,
                          args.duration, args.dialogue, args.dry_run)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        src = args.doc or args.topic
        print(f"# Audio Pipeline: {src}")
        print(f"Type: {args.type} | Duration: {args.duration}min | Dialogue: {args.dialogue}")
        print()
        for s in result["steps"]:
            print(f"  □ {s['step']} [{s['skill']}] {s['action']}")
            print(f"      {s['detail']}")
        print(f"\nOutput: {result['output_dir']}")
        print(result["chain_note"])


if __name__ == "__main__":
    main()
