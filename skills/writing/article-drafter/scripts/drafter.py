#!/usr/bin/env python3
"""Article Drafter — 根据大纲生成文章初稿。

用法:
  python3 drafter.py --outline outline.json
  python3 drafter.py --topic "FastAPI" --section "缓存优化"
"""
import argparse
import json
import sys
from pathlib import Path


def draft_section(heading: str, points: list, audience: str = "intermediate",
                  word_target: int = 300) -> dict:
    """Draft a single section (LLM fills in production)."""
    paragraphs = []
    for point in (points or [heading]):
        p = f"{point}。\n\n"
        p += f"（{audience} 读者视角：解释为什么 + 怎么做 + 注意事项）\n"
        paragraphs.append(p)

    return {
        "heading": heading,
        "draft": "\n".join(paragraphs),
        "word_count": sum(len(p) for p in paragraphs),
        "target": word_target,
        "status": "draft_placeholder",
        "note": "Production: LLM generates full text based on outline + research",
    }


def draft_article(outline: dict) -> dict:
    """Draft full article from outline."""
    sections = []
    for sec in outline.get("sections", []):
        r = draft_section(
            sec.get("heading", ""),
            sec.get("points", []),
            outline.get("audience", "intermediate"),
            sec.get("word_count_target", 300),
        )
        r["id"] = sec.get("id")
        sections.append(r)

    article = {
        "title": outline.get("title", "Untitled"),
        "hook": outline.get("hook", ""),
        "sections": sections,
        "conclusion": outline.get("conclusion", ""),
        "total_words_target": outline.get("total_words_target", 2000),
        "status": "draft",
        "needs_review": True,
    }
    return article


def main():
    parser = argparse.ArgumentParser(description="Draft article from outline")
    parser.add_argument("--outline", help="Outline JSON file")
    parser.add_argument("--topic", help="Quick topic (no outline)")
    parser.add_argument("--section", help="Draft single section")
    parser.add_argument("--audience", default="intermediate")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.outline:
        path = Path(args.outline)
        if not path.is_file():
            print(f"[ERROR] 大纲文件不存在: {path}", file=sys.stderr)
            return 1
        outline = json.loads(path.read_text(encoding="utf-8"))
        article = draft_article(outline)
    elif args.topic:
        article = draft_article({"title": args.topic, "sections": []})
    elif args.section:
        article = draft_section(args.section, [], args.audience)
    else:
        parser.error("Need --outline, --topic, or --section")
        return

    output = json.dumps(article, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Draft written to: {args.output}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
