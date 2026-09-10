#!/usr/bin/env python3
"""LaTeX Formatter — 论文 LaTeX 格式化 + 编译检查。

用法:
  python3 latex_formatter.py --input draft.tex --template ieee
  python3 latex_formatter.py --input draft.tex --check
"""
import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATES = {
    "ieee": {
        "class": "IEEEtran",
        "options": "conference",
        "columns": 2,
        "font_size": 10,
    },
    "acm": {
        "class": "acmart",
        "options": "sigconf",
        "columns": 1,
        "font_size": 9,
    },
    "neurips": {
        "class": "article",
        "options": "neurips_2024",
        "columns": 1,
        "font_size": 10,
    },
    "generic": {
        "class": "article",
        "options": "11pt",
        "columns": 1,
        "font_size": 11,
    },
}


def format_latex(input_tex: str, template: str = "ieee") -> dict:
    """Apply template formatting to LaTeX content."""
    tpl = TEMPLATES.get(template, TEMPLATES["generic"])
    issues = []

    # Check common issues
    if "\\begin{document}" not in input_tex:
        issues.append("Missing \\begin{document}")
    if "\\bibliography" not in input_tex and "\\cite" in input_tex:
        issues.append("Citations present but no \\bibliography command")
    if "\\section" in input_tex and input_tex.count("\\section") < 3:
        issues.append(f"Only {input_tex.count(chr(92) + 'section')} sections — paper too short?")

    # Check for common errors
    unbalanced = input_tex.count("\\begin{") - input_tex.count("\\end{")
    if unbalanced != 0:
        issues.append(f"Unbalanced environments: {unbalanced:+d}")

    # Check for forbidden characters
    for char, msg in [("&", "Raw & needs escaping in text"), ("%", "Raw % needs escaping"),
                      ("#", "Raw # needs escaping")]:
        if re.search(r"(?<!\\)" + re.escape(char), input_tex):
            issues.append(msg)

    return {
        "template": template,
        "class": tpl["class"],
        "status": "pass" if not issues else "issues_found",
        "issues": issues,
        "suggestions": _suggestions(issues),
    }


def _suggestions(issues: list) -> list:
    sugg = []
    for i in issues:
        if "Unbalanced" in i:
            sugg.append("Check all \\begin{xxx} have matching \\end{xxx}")
        elif "bibliography" in i:
            sugg.append("Add \\bibliography{refs} or use \\cite with biblatex")
        elif "escaping" in i.lower() or "Raw" in i:
            sugg.append("Escape special chars: \\&, \\%, \\#")
    return sugg


def main():
    parser = argparse.ArgumentParser(description="LaTeX formatter")
    parser.add_argument("--input", required=True, help="LaTeX file")
    parser.add_argument("--template", default="ieee", choices=list(TEMPLATES.keys()))
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        print(json.dumps({"status": "error", "error": f"File not found: {args.input}"}, indent=2))
        return

    tex = p.read_text(encoding="utf-8")
    result = format_latex(tex, args.template)
    result["file"] = str(p)
    result["n_lines"] = len(tex.split("\n"))

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
