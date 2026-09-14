#!/usr/bin/env python3
"""script_lint.py — lint a podcast script for TTS-safe spoken words only.

TTS reads EVERYTHING verbatim: stage directions, bracketed asides, markdown
debris all become audio. This linter enforces the spoken-words-only rule.

Checks:
  1. stage directions: [pause] [停顿] （笑） (laughs) etc.
  2. bracketed asides: any [...] or （...）/ (...)-style insertion
  3. markdown debris: heading/bold/italic/bullets inside body lines
  4. overlong lines: a single speaker line > 240 chars (three-sentence rule)
  5. speaker labels: dialogue mode expects HOST/GUEST prefixes per line

Output: JSON report. Exit codes: 0 = clean; 1 = violations; 2 = usage error.
"""
import argparse
import json
import re
import sys

STAGE_DIRECTION_RE = re.compile(
    r"\[(?:pause|breath|laugh|音乐|音效|停顿|笑声|掌声)[^\]]*\]|（(?:笑|叹气|停顿|音乐|音效)[^）]*\)"
    r"|\((?:laughs|sighs|pause|music)\)",
    re.I,
)
BRACKET_ASIDE_RE = re.compile(r"【[^】]*】|（[^（）]{1,}）|\([^()]{1,}?\)")
MARKDOWN_DEBRIS_RE = re.compile(r"^#{1,6}\s|\*\*|^\s*[-*]\s+|^\s*\d+\.\s|`[^`]+`")
SPEAKER_LABEL_RE = re.compile(r"^(HOST|GUEST|HOST-A|HOST-B)\s*[:：]")
MAX_LINE_CHARS = 90  # ~3 spoken Chinese sentences; TTS prosody degrades beyond


def lint(text, dialogue=False):
    violations = []
    lines = text.splitlines()
    in_code_block = False
    for no, raw in enumerate(lines, 1):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            # headings allowed as structural separators (never fed to TTS)
            continue
        body = line
        m = SPEAKER_LABEL_RE.match(line.strip())
        if dialogue and not m and line.strip():
            violations.append({"line": no, "rule": "speaker_label",
                               "detail": "dialogue mode: missing HOST/GUEST prefix"})
        if m:
            body = SPEAKER_LABEL_RE.sub("", line.strip())
        if STAGE_DIRECTION_RE.search(body):
            violations.append({"line": no, "rule": "stage_direction",
                               "detail": "TTS will read this aloud — remove it"})
        elif BRACKET_ASIDE_RE.search(body):
            violations.append({"line": no, "rule": "bracketed_aside",
                               "detail": "bracketed content gets spoken — rewrite as spoken words"})
        if MARKDOWN_DEBRIS_RE.search(body):
            violations.append({"line": no, "rule": "markdown_debris",
                               "detail": "markdown markers will be read aloud"})
        if len(body.strip()) > MAX_LINE_CHARS:
            violations.append({"line": no, "rule": "overlong_line",
                               "detail": f"{len(body.strip())} chars > {MAX_LINE_CHARS}: split into shorter lines"})
    rules_hit = sorted({v["rule"] for v in violations})
    return {
        "lines": len(lines),
        "violations": violations,
        "count": len(violations),
        "rules": rules_hit,
        "status": "clean" if not violations else "violation",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="TTS-safety lint for podcast scripts.")
    ap.add_argument("--file", help="script file (markdown/txt)")
    ap.add_argument("--text", help="script text inline")
    ap.add_argument("--dialogue", action="store_true",
                    help="enforce HOST/GUEST line prefixes")
    args = ap.parse_args(argv)

    if args.file:
        text = open(args.file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    if not text.strip():
        print(json.dumps({"error": "empty script"}))
        return 2
    report = lint(text, dialogue=args.dialogue)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["violations"] else 0


if __name__ == "__main__":
    sys.exit(main())
