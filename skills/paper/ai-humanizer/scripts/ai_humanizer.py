#!/usr/bin/env python3
"""AI Humanizer — 去除 AI 写作痕迹，保持学术声音。

学习自: academic-humanizer (1.5k stars)
检测: 套话、空洞表达、过度限定词、重复模式

用法:
  python3 ai_humanizer.py --text "Our novel framework leverages state-of-the-art..."
  python3 ai_humanizer.py --file draft.tex --report
"""
import argparse
import json
import re
import sys
from pathlib import Path

# AI-tell patterns (things LLMs overuse)
AI_PATTERNS = {
    "buzzwords": {
        "pattern": r"\b(novel|pioneering|state-of-the-art|groundbreaking|revolutionary|unprecedented)\b",
        "replace_with": "Be specific: what's new? What SOTA does it beat? By how much?",
        "severity": "high",
    },
    "hedging_overuse": {
        "pattern": r"\b(we believe|we argue|it is worth noting|it should be noted|notably|interestingly)\b",
        "replace_with": "State the claim directly. 'We believe X works' → 'X works (Table 2: 94% F1)'",
        "severity": "medium",
    },
    "empty_adjectives": {
        "pattern": r"\b(effective|efficient|robust|scalable|flexible)\s+(and|,|or)\s+\w+",
        "replace_with": "Pick one adjective with evidence. 'effective and efficient' shows both numbers",
        "severity": "medium",
    },
    "template_phrases": {
        "pattern": r"\b(in this paper|in this work|in the present study|we present|we propose a (?:novel|new))\b",
        "replace_with": "Cut it. Start with the contribution: 'Our method achieves X by doing Y'",
        "severity": "high",
    },
    "excessive_qualifiers": {
        "pattern": r"\b(somewhat|fairly|quite|very|extremely|particularly|especially|substantially|significantly)\b",
        "replace_with": "Use numbers instead: 'extremely fast' → '2.3x faster (Table 3)'",
        "severity": "low",
    },
    "repeated_structure": {
        "pattern": r"(Furthermore|Moreover|Additionally|In addition|Moreover,)",
        "replace_with": "Vary transitions. Don't start 3+ sentences the same way.",
        "severity": "medium",
    },
    "passive_excess": {
        "pattern": r"\b(was (?:performed|conducted|carried|executed)|were (?:performed|conducted|collected))\b",
        "replace_with": "Active voice: 'We performed X' > 'X was performed'",
        "severity": "low",
    },
}


def humanize(text: str) -> dict:
    """Detect and suggest fixes for AI writing tells."""
    issues = []
    for name, rule in AI_PATTERNS.items():
        matches = re.findall(rule["pattern"], text, re.IGNORECASE)
        if matches:
            issues.append({
                "type": name,
                "matches": matches[:5],
                "count": len(matches),
                "severity": rule["severity"],
                "fix_hint": rule["replace_with"],
            })

    # Score
    total_weight = sum(
        len(i["matches"]) * ({"high": 3, "medium": 2, "low": 1}[i["severity"]])
        for i in issues
    )
    score = max(0, 100 - total_weight * 3)

    return {
        "score": score,
        "status": "clean" if score >= 85 else "needs_edit",
        "issues": issues,
        "n_flags": len(issues),
        "summary": f"{len(issues)} AI-tell patterns found, {score}/100 human-likeness",
    }


def main():
    parser = argparse.ArgumentParser(description="AI writing humanizer")
    parser.add_argument("--text", help="Text to check")
    parser.add_argument("--file", help="File to check")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    text = ""
    if args.file and Path(args.file).exists():
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        parser.error("Need --text or --file")
        return

    result = humanize(text)

    if args.report:
        print(f"AI-Humanize Score: {result['score']}/100")
        print(f"Status: {result['status']}")
        print(f"\nIssues ({result['n_flags']}):")
        for i in result["issues"]:
            print(f"  [{i['severity'].upper()}] {i['type']}: {i['count']} hits")
            print(f"    Examples: {i['matches'][:3]}")
            print(f"    Fix: {i['fix_hint'][:60]}")
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output)


if __name__ == "__main__":
    sys.exit(main())
