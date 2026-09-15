#!/usr/bin/env python3
"""Journal Adapt — 期刊/会议格式适配。

学习自: Awesome-Journal-Skills (1.1k stars, 200+ journals)
支持: IEEE, ACM, NeurIPS, ACL, Nature, Cell

用法:
  python3 journal_adapt.py --input draft.tex --target ieee_conf
"""
import argparse
import json
import re
import sys
from pathlib import Path

JOURNAL_SPECS = {
    "ieee_conf": {
        "name": "IEEE Conference",
        "class": "IEEEtran", "columns": 2, "font_size": 9, "page_limit": 8,
        "section_order": ["Introduction", "Related Work", "Method", "Experiments", "Conclusion"],
        "ban": [],
    },
    "acm": {
        "name": "ACM SIGCONF",
        "class": "acmart", "columns": 1, "font_size": 9, "page_limit": 12,
        "section_order": ["Abstract", "Introduction", "Method", "Evaluation", "Discussion", "Conclusion"],
        "ban": [],
    },
    "neurips": {
        "name": "NeurIPS",
        "class": "neurips_2024", "columns": 1, "font_size": 10, "page_limit": 9,
        "section_order": ["Abstract", "Introduction", "Method", "Experiments", "Broader Impact", "Conclusion"],
        "ban": [],
    },
    "acl": {
        "name": "ACL/EMNLP",
        "class": "acl2023", "columns": 1, "font_size": 10, "page_limit": 8,
        "section_order": ["Abstract", "Introduction", "Method", "Experiments", "Analysis", "Conclusion"],
        "ban": [],
    },
    "nature": {
        "name": "Nature",
        "class": "nature", "columns": 1, "font_size": 9, "page_limit": 5,
        "section_order": ["Introduction", "Results", "Discussion", "Methods"],
        "ban": ["In this paper we", "Novel"],
    },
}


def adapt(text: str, target: str) -> dict:
    spec = JOURNAL_SPECS.get(target, JOURNAL_SPECS["ieee_conf"])
    issues = []
    words = len(text.split())
    est_pages = words / 500

    if est_pages > spec["page_limit"]:
        issues.append({"type": "page_limit", "message": f"{est_pages:.1f}p > {spec['page_limit']}p limit"})

    for banned in spec.get("ban", []):
        if banned.lower() in text.lower():
            issues.append({"type": "banned", "phrase": banned})

    for section in spec["section_order"]:
        if section.lower() not in text.lower():
            issues.append({"type": "missing_section", "section": section})

    score = max(0, 100 - len(issues) * 10)
    return {
        "target": spec["name"], "score": score,
        "status": "pass" if not issues else "adjust_needed",
        "issues": issues, "words": words, "est_pages": round(est_pages, 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Journal format check")
    parser.add_argument("--input", required=True)
    parser.add_argument("--target", default="ieee_conf", choices=list(JOURNAL_SPECS.keys()))
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    p = Path(args.input)
    text = p.read_text(encoding="utf-8") if p.exists() else args.input
    result = adapt(text, args.target)

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    sys.exit(main())
