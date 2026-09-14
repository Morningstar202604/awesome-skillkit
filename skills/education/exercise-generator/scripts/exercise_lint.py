#!/usr/bin/env python3
"""exercise_lint.py — lint a generated exercise bank for mastery format.

Checks per question block:
  1. five fields present: 题干 / 参考答案 / 评分标准 / 常见陷阱 / 关联
  2. difficulty tag in [recall|apply|transfer]
  3. checkpoint reference pattern CP<n>
  4. --no-mcq: multiple-choice markers (A. B. C. D. / 选择题) banned

Output: JSON report. Exit codes: 0 = clean; 1 = violations; 2 = usage error.
"""
import argparse
import json
import re
import sys

REQUIRED_FIELDS = ["题干", "参考答案", "评分标准", "常见陷阱", "关联"]
DIFFICULTY_RE = re.compile(r"^###\s*Q(\d+)\s*\[(recall|apply|transfer)\]", re.M)
CHECKPOINT_RE = re.compile(r"CP\d+")
MCQ_RE = re.compile(r"^\s*[A-D][.、．]\s*\S", re.M)


def lint(text, no_mcq=True):
    violations = []
    blocks = re.split(r"(?=^###\s*Q\d+)", text, flags=re.M)
    blocks = [b for b in blocks if DIFFICULTY_RE.search(b)]
    if not blocks:
        return {"error": "no question blocks found (expect '### Q1 [recall]' headers)"}, 2

    for block in blocks:
        qid = DIFFICULTY_RE.search(block).group(1)
        for field in REQUIRED_FIELDS:
            if field + ("：" if field != "关联" else "") not in block and f"{field}:" not in block and f"{field}：" not in block:
                violations.append({"q": qid, "rule": "missing_field",
                                   "detail": f"missing field: {field}"})
        if not CHECKPOINT_RE.search(block):
            violations.append({"q": qid, "rule": "missing_checkpoint",
                               "detail": "no CP<n> reference found"})
        if no_mcq and MCQ_RE.search(block):
            violations.append({"q": qid, "rule": "mcq_banned",
                               "detail": "multiple-choice markers found — open-ended only (prevents guessing)"})

    rules_hit = sorted({v["rule"] for v in violations})
    return {
        "questions": len(blocks),
        "violations": violations,
        "count": len(violations),
        "rules": rules_hit,
        "status": "clean" if not violations else "violation",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Mastery-format lint for exercise banks.")
    ap.add_argument("--file", help="exercise bank file (markdown)")
    ap.add_argument("--text", help="exercise bank inline")
    ap.add_argument("--allow-mcq", action="store_true",
                    help="permit multiple-choice questions (default: banned)")
    args = ap.parse_args(argv)

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text is not None:
        text = args.text
    else:
        text = sys.stdin.read()
    if not text.strip():
        print(json.dumps({"error": "empty bank"}))
        return 2
    report = lint(text, no_mcq=not args.allow_mcq)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if "error" in report:
        return 2
    return 1 if report["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
