#!/usr/bin/env python3
"""Article Outliner — generate an article outline.

Usage:
  python3 outliner.py --topic "FastAPI performance tuning" --type technical
  python3 outliner.py --json '{"topic":"...","type":"listicle","key_points":["a","b"]}'
"""
import argparse
import json
import sys
from pathlib import Path

STRUCTURES = {
    "technical": {
        "sections": ["Problem context", "Root-cause analysis", "Solution", "Comparison tests", "Summary"],
        "pattern": "problem_solution",
    },
    "blog": {
        "sections": ["Introduction", "Core content", "Practical steps", "Pitfalls", "Summary"],
        "pattern": "narrative",
    },
    "news": {
        "sections": ["Event", "Background", "Impact", "Reactions", "Outlook"],
        "pattern": "inverted_pyramid",
    },
    "listicle": {
        "sections": ["Introduction", "Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5", "Summary"],
        "pattern": "list",
    },
    "tutorial": {
        "sections": ["Prerequisites", "Step 1", "Step 2", "Step 3", "Verification", "FAQ"],
        "pattern": "linear_steps",
    },
    "opinion": {
        "sections": ["Claim", "Evidence 1", "Evidence 2", "Counterarguments", "Conclusion"],
        "pattern": "argumentative",
    },
}


def generate_outline(topic: str, article_type: str = "technical",
                     target_length: str = "medium", audience: str = "intermediate",
                     key_points: list = None, platforms: list = None) -> dict:
    """Generate article outline."""
    structure = STRUCTURES.get(article_type, STRUCTURES["technical"])
    sections = []

    n_sec = len(structure["sections"])
    target_words = {"short": 800, "medium": 2000, "long": 5000}.get(target_length, 2000)
    reading_time = target_words // 250
    base, extra = divmod(target_words, n_sec)  # divide evenly; push the remainder into the first `extra` sections so the sum stays exact

    for i, sec_name in enumerate(structure["sections"]):
        # round-robin point assignment: point k goes to section (k % n_sec).
        # The old loop `i < len(key_points)` silently dropped trailing points when
        # key_points outnumbered sections.
        points = [kp for k, kp in enumerate(key_points or []) if k % n_sec == i]
        sections.append({
            "id": i + 1,
            "heading": sec_name,
            "level": 2,
            "points": points,
            "word_count_target": base + (1 if i < extra else 0),
        })

    outline = {
        "title": f"{topic}: from beginner to expert",
        "hook": f"Ever run into {topic}-related pain points?",
        "sections": sections,
        "conclusion": "Summarize key points + CTA",
        "total_words_target": target_words,
        "reading_time_min": reading_time,
        "type": article_type,
        "audience": audience,
        "platforms": platforms or ["csdn"],
        # placeholder marker: the fields below are template skeleton text and must be
        # rewritten before delivery (SKILL.md honest-disclaimer items 1-2)
        "placeholders": ["title", "hook", "conclusion", "sections[].heading"],
        "placeholder_note": "The above fields are template skeleton text, not a finished piece; rewrite them per SKILL.md workflow A step 6 and the reference templates",
    }
    return outline


def main():
    parser = argparse.ArgumentParser(description="Generate article outline")
    parser.add_argument("--topic", required=False,
                        help="Article topic (mutually exclusive with --json-input; optional when --json-input is given)")
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
        if not data.get("topic") and not args.topic:
            parser.error("Provide --topic or a topic field in --json-input")
        outline = generate_outline(
            data.get("topic", args.topic),
            data.get("type", args.type),
            data.get("target_length", args.length),
            data.get("audience", args.audience),
            data.get("key_points", args.points),
            data.get("platforms", args.platforms),
        )
    else:
        if not args.topic:
            parser.error("Provide --topic or --json-input")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
