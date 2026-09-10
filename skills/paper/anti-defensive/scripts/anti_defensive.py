#!/usr/bin/env python3
"""Anti-Defensive Writing — 检测并修复防御性学术写作。

学习自: anti-defensive-writing (771 stars)
检测: 过度限定、自贬、模糊归因

用法:
  python3 anti_defensive.py --text "Our results suggest that the method may possibly..."
"""
import argparse
import json
import re
import sys

DEFENSIVE_PATTERNS = [
    {
        "pattern": r"\b(may|might|could) (?:possibly|potentially|arguably)\b",
        "issue": "Double hedging — 'may possibly' is weak",
        "fix": "Pick one: 'may' OR 'possibly'. Or better: show the number.",
    },
    {
        "pattern": r"\b(to the best of our knowledge|to our knowledge|as far as we know)\b",
        "issue": "Defensive qualifier — implies you haven't checked",
        "fix": "Cite the survey that establishes this gap instead.",
    },
    {
        "pattern": r"\b(it should be noted that|we would like to point out|it is important to note)\b",
        "issue": "Filler phrase that weakens the claim",
        "fix": "Cut it. Just state the fact directly.",
    },
    {
        "pattern": r"\b(some limitations exist|there are certain drawbacks|we acknowledge that)\b",
        "issue": "Weak self-criticism — reviewer will criticize harder anyway",
        "fix": "State limitation with evidence: 'Accuracy drops 3% on X (Table 7)'",
    },
    {
        "pattern": r"\b(not surprisingly|unfortunately|regrettably)\b",
        "issue": "Editorializing — inappropriate for academic voice",
        "fix": "Remove opinion. State the result neutrally.",
    },
    {
        "pattern": r"\b(a minor|a small|a modest|negligible) (improvement|gain|degradation|effect)\b",
        "issue": "Underselling your own result",
        "fix": "Report the number: '1.2% improvement' not 'a minor improvement'",
    },
]


def check(text: str) -> dict:
    issues = []
    for p in DEFENSIVE_PATTERNS:
        matches = re.findall(p["pattern"], text, re.IGNORECASE)
        if matches:
            issues.append({
                "pattern": p["pattern"][:50],
                "issue": p["issue"],
                "fix": p["fix"],
                "count": len(matches),
                "examples": matches[:3],
            })

    score = max(0, 100 - len(issues) * 15)
    return {
        "score": score,
        "status": "clean" if score >= 80 else "rewrite_needed",
        "issues": issues,
        "n_flags": len(issues),
    }


def main():
    parser = argparse.ArgumentParser(description="Anti-defensive writing check")
    parser.add_argument("--text", help="Text to check")
    parser.add_argument("--file", help="File to check")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    text = ""
    if args.file:
        from pathlib import Path
        text = Path(args.file).read_text(encoding="utf-8") if Path(args.file).exists() else ""
    elif args.text:
        text = args.text
    else:
        parser.error("Need --text or --file")
        return

    result = check(text)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    main()
