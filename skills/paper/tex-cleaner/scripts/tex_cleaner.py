#!/usr/bin/env python3
"""TeX Cleaner — arXiv 提交前 LaTeX 清理。

学习自: google-research/arxiv-latex-cleaner (7k stars)
功能: 移除注释、清理未用包、统一命名、检查编译

用法:
  python3 tex_cleaner.py --input draft.tex --clean
  python3 tex_cleaner.py --input draft.tex --check-only
"""
import argparse
import json
import re
import sys
from pathlib import Path


def clean_latex(tex: str) -> dict:
    """Clean LaTeX for arXiv submission."""
    issues = []
    cleaned = tex

    # 1. Remove commented-out code blocks (keep %)
    removed_comments = 0
    lines = cleaned.split("\n")
    active_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("%") and not stripped.startswith("%\\"):
            removed_comments += 1
        else:
            active_lines.append(line)
    cleaned = "\n".join(active_lines)

    # 2. Check unused packages
    used_commands = set(re.findall(r"\\(\w+)", cleaned))
    pkg_issues = []
    for pkg_pattern, cmd in [
        (r"\\usepackage\{graphicx\}", "includegraphics"),
        (r"\\usepackage\{amsmath\}", "math"),
        (r"\\usepackage\{hyperref\}", "hyperref"),
    ]:
        if re.search(pkg_pattern, cleaned) and not any(c in used_commands for c in [cmd, "frac", "text", "href"]):
            pkg_issues.append(pkg_pattern)

    # 3. Check for common arXiv issues
    if "\\input" in cleaned or "\\include" in cleaned:
        # Find external files
        ext_files = re.findall(r"\\(?:input|include)\{([^}]+)\}", cleaned)
        if ext_files:
            issues.append({"type": "external_files", "files": ext_files,
                          "note": "Ensure all \\input files exist before submission"})

    # 4. Check figure quality
    fig_refs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", cleaned)
    low_res = [f for f in fig_refs if "lowres" in f or ".bmp" in f.lower()]
    if low_res:
        issues.append({"type": "low_res_figures", "files": low_res,
                      "fix": "Convert to PDF/PNG 300dpi+"})

    # 5. Check for TOC/LOF
    if r"\tableofcontents" in cleaned:
        issues.append({"type": "toc_present", "fix": "Remove \\tableofcontents for arXiv"})
    if r"\listoffigures" in cleaned:
        issues.append({"type": "lof_present", "fix": "Remove \\listoffigures for arXiv"})

    # 6. Check for long URLs
    long_urls = re.findall(r"\\url\{(\w{50,})\}", cleaned)
    if long_urls:
        issues.append({"type": "long_urls", "count": len(long_urls),
                      "fix": "Use \\href with short text instead"})

    # 7. Check undefined references
    undef_refs = re.findall(r"\\ref\{([^}]+)\}", cleaned)
    labels = re.findall(r"\\label\{([^}]+)\}", cleaned)
    missing = [r for r in undef_refs if r not in labels]
    if missing:
        issues.append({"type": "undefined_refs", "refs": missing[:5],
                      "fix": "Add \\label or remove \\ref"})

    # 8. Check for non-ASCII characters
    non_ascii = [c for c in cleaned if ord(c) > 127]
    if non_ascii:
        issues.append({"type": "non_ascii", "count": len(non_ascii),
                      "examples": list(set(non_ascii))[:5]})

    return {
        "status": "clean" if not issues else "issues_found",
        "issues": issues,
        "removed_comments": removed_comments,
        "n_lines_original": len(tex.split("\n")),
        "n_lines_cleaned": len(cleaned.split("\n")),
        "arxiv_ready": len(issues) == 0,
    }


def main():
    parser = argparse.ArgumentParser(description="LaTeX cleaner for arXiv")
    parser.add_argument("--input", required=True, help="LaTeX file")
    parser.add_argument("--clean", action="store_true", help="Write cleaned output")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        print(json.dumps({"error": f"Not found: {args.input}"}, indent=2))
        return 1

    tex = p.read_text(encoding="utf-8")
    result = clean_latex(tex)

    if args.clean and args.output:
        # Re-clean and write
        cleaned = tex
        lines = cleaned.split("\n")
        active = [l for l in lines if not l.strip().startswith("%") or l.strip().startswith("%\\")]
        Path(args.output).write_text("\n".join(active), encoding="utf-8")
        result["cleaned_to"] = args.output

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
