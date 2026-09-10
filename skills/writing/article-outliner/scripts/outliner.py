#!/usr/bin/env python3
"""Article Outliner — 生成文章大纲。

用法:
  python3 outliner.py --topic "FastAPI 性能优化" --type technical
  python3 outliner.py --json '{"topic":"...","type":"listicle","key_points":["a","b"]}'
"""
import argparse
import json
import sys
from pathlib import Path

STRUCTURES = {
    "technical": {
        "sections": ["问题背景", "原因分析", "解决方案", "对比测试", "总结"],
        "pattern": "problem_solution",
    },
    "blog": {
        "sections": ["引言", "核心内容", "实操步骤", "踩坑记录", "总结"],
        "pattern": "narrative",
    },
    "news": {
        "sections": ["事件", "背景", "影响", "各方反应", "展望"],
        "pattern": "inverted_pyramid",
    },
    "listicle": {
        "sections": ["引言", "技巧 1", "技巧 2", "技巧 3", "技巧 4", "技巧 5", "总结"],
        "pattern": "list",
    },
    "tutorial": {
        "sections": ["前置要求", "步骤 1", "步骤 2", "步骤 3", "验证", "FAQ"],
        "pattern": "linear_steps",
    },
    "opinion": {
        "sections": ["论点", "论据 1", "论据 2", "反方观点", "结论"],
        "pattern": "argumentative",
    },
}


def generate_outline(topic: str, article_type: str = "technical",
                     target_length: str = "medium", audience: str = "intermediate",
                     key_points: list = None, platforms: list = None) -> dict:
    """Generate article outline."""
    structure = STRUCTURES.get(article_type, STRUCTURES["technical"])
    sections = []

    for i, sec_name in enumerate(structure["sections"]):
        points = []
        if key_points and i < len(key_points):
            points = [key_points[i]]
        sections.append({
            "id": i + 1,
            "heading": sec_name,
            "level": 2,
            "points": points,
        })

    target_words = {"short": 800, "medium": 2000, "long": 5000}.get(target_length, 2000)
    reading_time = target_words // 250

    outline = {
        "title": f"{topic}：从入门到精通",
        "hook": f"你遇到过{topic}相关的痛点吗？",
        "sections": sections,
        "conclusion": "总结要点 + CTA",
        "total_words_target": target_words,
        "reading_time_min": reading_time,
        "type": article_type,
        "audience": audience,
        "platforms": platforms or ["csdn"],
    }
    return outline


def main():
    parser = argparse.ArgumentParser(description="Generate article outline")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--type", default="technical", choices=list(STRUCTURES.keys()))
    parser.add_argument("--length", default="medium", choices=["short", "medium", "long"])
    parser.add_argument("--audience", default="intermediate")
    parser.add_argument("--points", nargs="*", help="Key points")
    parser.add_argument("--platforms", nargs="*", help="Target platforms")
    parser.add_argument("--json-input", help="Full JSON input")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.json_input:
        data = json.loads(args.json_input)
        outline = generate_outline(
            data.get("topic", args.topic),
            data.get("type", args.type),
            data.get("target_length", args.length),
            data.get("audience", args.audience),
            data.get("key_points", args.points),
            data.get("platforms", args.platforms),
        )
    else:
        outline = generate_outline(
            args.topic, args.type, args.length,
            args.audience, args.points, args.platforms
        )

    output = json.dumps(outline, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Outline written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
