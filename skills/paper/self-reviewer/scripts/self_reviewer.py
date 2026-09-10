#!/usr/bin/env python3
"""Self Reviewer — 模拟审稿 + 质量检查清单。

用法:
  python3 self_reviewer.py --paper draft.tex
  python3 self_reviewer.py --paper draft.tex --checklist
"""
import argparse
import json
import re
import sys
from pathlib import Path

CHECKLIST = {
    "structure": [
        "Has abstract (150-300 words)",
        "Has introduction with 3+ contributions listed",
        "Has related work section",
        "Has methodology section",
        "Has experiments/results section",
        "Has conclusion/limitations",
        "Has references (10+)",
    ],
    "content": [
        "Clear research question stated",
        "Baseline methods compared (2+)",
        "Statistical significance tested",
        "Ablation study included",
        "Limitations discussed",
        "Reproducibility info present (code, data, seeds)",
    ],
    "writing": [
        "No first-person 'we' abuse (max 2/page)",
        "Claim supported by evidence",
        "No unsupported superlatives ('best', 'state-of-the-art')",
        "Figures/tables have captions",
        "Math notation consistent",
    ],
    "formatting": [
        "Within page limit for venue",
        "Font size correct",
        "Figures not clipped",
        "References in correct style",
    ],
}


def review_paper(tex: str) -> dict:
    """Run self-review checklist on paper."""
    words = len(tex.split())
    checks = {"passed": [], "failed": [], "uncertain": []}

    # Structure checks
    if "abstract" in tex.lower() or "Abstract" in tex:
        checks["passed"].append("Has abstract")
    else:
        checks["failed"].append("Missing abstract")

    if tex.count(r"\section") >= 4:
        checks["passed"].append("Sufficient sections")
    else:
        checks["failed"].append(f"Only {tex.count(chr(92) + 'section')} sections")

    if r"\cite" in tex or r"\bibliography" in tex:
        checks["passed"].append("Has citations")
    else:
        checks["failed"].append("No citations found")

    if words < 3000:
        checks["failed"].append(f"Too short: {words} words (min ~4000)")

    # Content checks
    if any(w in tex for w in ["baseline", "compare", "ablation", "state-of-the-art", "SOTA"]):
        checks["passed"].append("Mentions baselines/comparisons")
    else:
        checks["uncertain"].append("No baseline mentioned?")

    if "limitation" in tex.lower():
        checks["passed"].append("Limitations discussed")
    else:
        checks["uncertain"].append("Limitations not found")

    # Score
    total = len(checks["passed"]) + len(checks["failed"]) + len(checks["uncertain"])
    score = int(100 * len(checks["passed"]) / max(total, 1))

    return {
        "word_count": words,
        "score": score,
        "passed": checks["passed"],
        "failed": checks["failed"],
        "uncertain": checks["uncertain"],
        "status": "ready" if score >= 80 else "needs_work",
        "next_steps": _next_steps(checks),
    }


def _next_steps(checks: dict) -> list:
    steps = []
    if "Missing abstract" in checks["failed"]:
        steps.append("Write abstract (150-250 words, 4-part: context/method/result/impact)")
    if any("section" in f for f in checks["failed"]):
        steps.append("Add missing sections")
    if "No citations found" in checks["failed"]:
        steps.append("Add 10+ references in \\bibliography")
    if "Too short" in " ".join(checks["failed"]):
        steps.append("Expand results section with more experiments")
    if not steps:
        steps.append("Review uncertain items, polish writing")
    return steps


def main():
    parser = argparse.ArgumentParser(description="Paper self-review")
    parser.add_argument("--paper", required=True, help="LaTeX/markdown file")
    parser.add_argument("--checklist", action="store_true", help="Print full checklist")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    p = Path(args.paper)
    if not p.exists():
        print(json.dumps({"error": f"File not found: {args.paper}"}, indent=2))
        return

    content = p.read_text(encoding="utf-8")

    if args.checklist:
        print(json.dumps(CHECKLIST, ensure_ascii=False, indent=2))
        return

    result = review_paper(content)
    result["file"] = str(p)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
