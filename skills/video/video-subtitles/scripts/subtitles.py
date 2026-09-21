#!/usr/bin/env python3
"""Subtitles Generator — 为视频生成字幕/标题。

用法:
  python3 subtitles.py --script script.json --output subs.srt
  python3 subtitles.py --text "你好世界" --start 0 --end 3
"""
import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict


def format_timestamp(sec: float) -> str:
    """Format seconds to SRT timestamp: HH:MM:SS,mmm"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(scenes: List[Dict], output: str = None) -> Dict:
    """Generate SRT file from script scenes."""
    lines = []
    t = 0.0
    for i, scene in enumerate(scenes, 1):
        start = t
        end = t + scene.get("duration_sec", 2)
        dialogue = scene.get("dialogue", "").strip()
        if dialogue:
            lines.append(f"{i}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{dialogue}\n")
        t = end

    srt_content = "\n".join(lines)
    out = Path(output or "/tmp/subtitles.srt")
    out.write_text(srt_content, encoding="utf-8")

    return {
        "output_path": str(out),
        "total_cues": len([l for l in srt_content.split("\n\n") if l.strip()]),
        "total_duration": round(t, 1),
        "srt": srt_content,
    }


def generate_captions(text: str, platform: str = "douyin") -> Dict:
    """Generate platform-optimized caption (title + hashtags)."""
    if platform == "douyin":
        caption = f"{text[:20]}\n\n#视频 #内容 #{text[:8]}"
    elif platform == "bilibili":
        caption = f"【{text}】"
    else:
        caption = f"{text}\n\n#video #content"

    return {"caption": caption, "platform": platform, "length": len(caption)}


def main():
    parser = argparse.ArgumentParser(description="Generate subtitles/captions")
    parser.add_argument("--script", help="Script JSON file")
    parser.add_argument("--text", help="Single text for caption")
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--end", type=float, default=3)
    parser.add_argument("--output", help="Output SRT file")
    parser.add_argument("--platform", default="douyin")
    args = parser.parse_args()

    if args.script:
        p = Path(args.script)
        if not p.exists():
            print(json.dumps({"status": "error",
                              "error": f"--script 文件不存在: {args.script}"},
                             ensure_ascii=False))
            return 2
        try:
            script = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(json.dumps({"status": "error", "error": f"--script 不是合法 JSON: {e}"},
                             ensure_ascii=False))
            return 2
        result = generate_srt(script.get("scenes", []), args.output)
        result["caption"] = script.get("caption", "")
        result["status"] = "success"
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.text:
        result = generate_captions(args.text, args.platform)
        result["status"] = "success"
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.error("Need --script or --text")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
