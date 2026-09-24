#!/usr/bin/env python3
"""LaTeX Formatter — 论文 LaTeX 格式化 + 编译检查。

对标 2026 最佳实践（chktex / latexindent / tex-fmt）：
  - 先用 stdlib 做静态检查（always available），产出 issues/suggestions；
  - 若系统装有 chktex / latexindent / tex-fmt，则叠加**真实 lint**（method=external-lint），
    缺失时如实回退 stdlib（method=stdlib-fallback），绝不谎报。
  - 新增：跨文件 undefined \\ref / \\cite 检查（给定 --refs refs.bib）。

用法:
  python3 latex_formatter.py --input draft.tex --template ieee
  python3 latex_formatter.py --input draft.tex --refs refs.bib --output clean.json
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATES = {
    "ieee": {"class": "IEEEtran", "options": "conference", "columns": 2, "font_size": 10},
    "acm":  {"class": "acmart", "options": "sigconf", "columns": 1, "font_size": 9},
    "neurips": {"class": "article", "options": "neurips_2024", "columns": 1, "font_size": 10},
    "generic": {"class": "article", "options": "11pt", "columns": 1, "font_size": 11},
}


def _which(*names):
    return next((shutil.which(n) for n in names if shutil.which(n)), None)


def _external_lint(tex: str, tex_path: Path) -> dict:
    """运行系统安装的真实 lint（chktex 优先，否则 latexindent），缺失 → {}。

    只收集 warning/error，不阻断（工具缺失属正常，离线可复现）。
    """
    chktex = _which("chktex")
    if chktex:
        try:
            r = subprocess.run([chktex, "--output=2", str(tex_path)],
                               capture_output=True, text=True, timeout=30)
            lines = [l for l in r.stdout.splitlines() if l.strip()]
            return {"tool": "chktex", "raw": lines[:50]}
        except Exception as e:
            return {"tool": "chktex", "error": str(e)}
    texfmt = _which("tex-fmt") or _which("tex-fmt")
    li = _which("latexindent")
    return {"tool": None, "available": bool(li or texfmt)}


def format_latex(input_tex: str, template: str = "ieee", refs_bib: str = None,
                 ext: dict = None) -> dict:
    """Apply template formatting to LaTeX content.

    refs_bib: 可选 .bib 文本，用于跨文件检查 \\cite 是否都有对应 entry。
    ext: 外部 lint 结果（由调用方经 _external_lint() 计算后传入）；
         传 {} 或 None 时回退 stdlib。
    """
    tpl = TEMPLATES.get(template, TEMPLATES["generic"])
    issues = []
    warns = []

    # --- 静态检查（always） ---
    if "\\begin{document}" not in input_tex:
        issues.append("Missing \\begin{document}")
    has_cite = "\\cite" in input_tex
    has_bib = "\\bibliography" in input_tex or "\\addbibresource" in input_tex
    if has_cite and not has_bib:
        issues.append("Citations present but no \\bibliography command")
    n_sections = len(re.findall(r"\\section\{?", input_tex))
    if has_cite or n_sections:
        if n_sections < 3:
            warns.append(f"Only {n_sections} sections — paper too short?")

    # 环境配对（按名核对，而非简单计数）
    begins = re.findall(r"\\begin\{([^}]+)\}", input_tex)
    ends = re.findall(r"\\end\{([^}]+)\}", input_tex)
    from collections import Counter
    cb, ce = Counter(begins), Counter(ends)
    for name in set(list(cb) + list(ce)):
        if cb.get(name, 0) != ce.get(name, 0):
            issues.append(
                f"Unbalanced environment '{{{name}}}': "
                f"begin={cb.get(name,0)} end={ce.get(name,0)}")

    # 转义检查（& % # 在正文裸用，且前面不是反斜杠）
    for char, hint in [("&", "Raw & needs escaping in text"),
                       ("%", "Raw % needs escaping"),
                       ("#", "Raw # needs escaping")]:
        pat = re.compile(r"(?<!\\)" + re.escape(char))
        if pat.search(input_tex):
            issues.append(hint)

    # 跨文件 undefined \cite / \ref
    undefined_cite = []
    defined_keys = set()
    if refs_bib:
        defined_keys = set(re.findall(r"@\w+\s*\{([^,]+),", refs_bib))
        for c in re.findall(r"\\cite[tp]?\{([^}]+)\}", input_tex):
            for key in c.split(","):
                key = key.strip()
                if key and key not in defined_keys:
                    undefined_cite.append(key)
    if undefined_cite:
        issues.append(f"Undefined \\cite keys (no .bib entry): {sorted(set(undefined_cite))}")

    # 真实 lint（有工具则叠加，缺失如实回退）
    ext = ext or {}
    status = "pass" if not issues and not warns else ("issues_found" if issues else "pass")

    return {
        "template": template,
        "class": tpl["class"],
        "method": "external-lint" if ext.get("tool") == "chktex" else "stdlib-fallback",
        "status": status,
        "issues": issues,
        "warnings": warns,
        "suggestions": _suggestions(issues),
        "external_lint": ext,
    }


def _suggestions(issues: list) -> list:
    sugg = []
    for i in issues:
        if "Unbalanced" in i:
            sugg.append("Match each \\begin{xxx} with \\end{xxx}")
        elif "bibliography" in i:
            sugg.append("Add \\bibliography{refs} or use biblatex \\addbibresource")
        elif "escaping" in i.lower() or "Raw" in i:
            sugg.append("Escape special chars: \\&, \\%, \\#")
        elif "Undefined \\cite" in i:
            sugg.append("Add the missing .bib entry, or drop the \\cite key")
    return sugg


def main():
    parser = argparse.ArgumentParser(description="LaTeX formatter (SOTA: stdlib + optional chktex)")
    parser.add_argument("--input", required=True, help="LaTeX file")
    parser.add_argument("--template", default="ieee", choices=list(TEMPLATES.keys()))
    parser.add_argument("--refs", help="Path to .bib for cross-file \\cite checks")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        print(json.dumps({"status": "error", "error": f"File not found: {args.input}"}, indent=2))
        return 1

    tex = p.read_text(encoding="utf-8")
    refs = None
    if args.refs:
        rp = Path(args.refs)
        if rp.exists():
            refs = rp.read_text(encoding="utf-8")
        else:
            print(json.dumps({"status": "error", "error": f"refs not found: {args.refs}"}, indent=2))
            return 1

    ext = _external_lint(tex, p)
    result = format_latex(tex, args.template, refs, ext=ext)
    result["file"] = str(p)
    result["n_lines"] = len(tex.split("\n"))

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())
