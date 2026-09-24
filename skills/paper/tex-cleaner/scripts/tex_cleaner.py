#!/usr/bin/env python3
"""TeX Cleaner -- LaTeX cleanup before an arXiv submission.

Matching the real semantics of google-research/arxiv-latex-cleaner (7k stars):
  - **Comment stripping**: recognize unescaped `%` (`\\%` does not count) and skip
    verbatim/lstlisting/minted environments; remove a leading comment line in full and only
    truncate trailing comments. The old version only recognized a "leading %" and missed many
    trailing comments.
  - **Unused packages**: decided via a "command -> package" map (whether commands from
    graphicx/amsmath/booktabs/xcolor/... appear), rather than the old hard-coded 3 ifs.
  - **Asset manifest**: list \\input/\\include/\\bibliography/\\includegraphics/custom .sty, and
    when a base dir is given, verify the files actually exist (these are the easiest things to
    leave out of a submission package).

Usage:
  python3 tex_cleaner.py --input draft.tex
  python3 tex_cleaner.py --input draft.tex --clean --output draft_clean.tex
"""
import argparse
import json
import re
import sys
from pathlib import Path

# environments skipped wholesale (their internal % is not a comment)
VERBATIM_ENVS = ("verbatim", "Verbatim", "lstlisting", "lstlisting*", "minted", "comment")

# command -> package map (the basis for deciding "installed but unused")
PACKAGE_COMMANDS = {
    "graphicx": ["includegraphics", "rotatebox", "resizebox", "scalebox"],
    "amsmath": ["align", "aligned", "gather", "split", "operatorname", "text", "frac", "mathbb"],
    "amssymb": ["mathbb", "mathfrak", "leqslant", "geqslant", "nmid"],
    "booktabs": ["toprule", "midrule", "bottomrule", "cmidrule", "addlinespace"],
    "xcolor": ["textcolor", "color", "definecolor", "colorbox"],
    "subcaption": ["subcaptionbox", "subref", "subtable"],
    "subfig": ["subfloat"],
    "algorithm": ["algorithm", "algocf", "listofalgorithms"],
    "algorithmic": ["STATE", "ENDFOR", "ENDIF", "ENSURE", "REQUIRE"],
    "algorithm2e": ["SetKw", "KwIn", "KwOut", "DontPrintSemicolon"],
    "tikz": ["tikzpicture", "tikzset"],
    "pgfplots": ["addplot", "pgfplotsset", "axis"],
    "natbib": ["citep", "citet", "citeauthor", "citeyear"],
    "biblatex": ["autocite", "parencite", "textcite", "printbibliography", "addbibresource"],
    "multirow": ["multirow"],
    "makecell": ["makecell", "thead"],
    "url": ["url"],
    "ulem": ["uline", "sout", "uwave"],
    "enumitem": ["setlist"],
    "threeparttable": ["tnote", "tablenotes"],
}

# these packages count as "used" even when no command appears (implicit effect / pure config)
NEVER_UNUSED = {
    "inputenc", "fontenc", "babel", "ctex", "xeCJK", "lmodern", "microtype",
    "times", "mathptmx", "geometry", "fancyhdr", "titlesec", "setspace",
    "hyperref", "cleveref", "float", "caption", "array", "tabularx",
}


def strip_comments(tex: str) -> tuple:
    """Return (de-commented text, stats). Safe for verbatim and escaped \\%."""
    out_lines, removed, verbatim_only = [], 0, 0
    in_verb = None
    for line in tex.split("\n"):
        m = re.match(r"\s*\\begin\{([^}]+)\}", line)
        if in_verb is None and m and m.group(1) in VERBATIM_ENVS:
            in_verb = m.group(1)
            out_lines.append(line)
            continue
        if in_verb is not None:
            out_lines.append(line)
            if re.match(r"\s*\\end\{" + re.escape(in_verb) + r"\}", line):
                in_verb = None
            continue
        # find the first % that is not escaped by a backslash
        cut = None
        for i, ch in enumerate(line):
            if ch != "%":
                continue
            bs = 0
            j = i - 1
            while j >= 0 and line[j] == "\\":
                bs += 1
                j -= 1
            if bs % 2 == 0:  # even number of backslashes -> a real comment
                cut = i
                break
        if cut is None:
            out_lines.append(line)
        else:
            removed += 1
            head = line[:cut].rstrip()
            if head:
                out_lines.append(head)
            else:
                verbatim_only += 1  # the whole line is a comment -> remove the line
    return "\n".join(out_lines), {
        "removed_comments": removed,
        "full_line_comments_removed": verbatim_only,
    }


def find_unused_packages(tex: str) -> list:
    """Find packages that are installed but never used, via the "command -> package" map."""
    used_cmds = set(re.findall(r"\\([A-Za-z]+)", tex))
    unused = []
    for m in re.finditer(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", tex):
        for pkg in m.group(1).split(","):
            pkg = pkg.strip()
            if not pkg or pkg in NEVER_UNUSED:
                continue
            cmds = PACKAGE_COMMANDS.get(pkg)
            if cmds and not (set(cmds) & used_cmds):
                unused.append(pkg)
    return sorted(set(unused))


def collect_assets(tex: str, base_dir: Path = None) -> dict:
    """List the external assets the submission package must carry, and verify their existence."""
    groups = {
        "inputs": [f"{f}.tex" if not f.endswith(".tex") else f
                   for f in re.findall(r"\\(?:input|include)\{([^}]+)\}", tex)],
        "bibliography": [f"{f}.bib" if not f.endswith(".bib") else f
                         for f in re.findall(r"\\bibliography\{([^}]+)\}", tex)],
        "bibliography_add": re.findall(r"\\addbibresource\{([^}]+)\}", tex),
        "figures": re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex),
        "custom_style": [f"{p.strip()}.sty" for m in
                         re.findall(r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}", tex)
                         for p in m.split(",") if p.strip() not in NEVER_UNUSED],
    }
    # only check existence for assets we can definitely locate (figures/bib/input); .sty cannot be
    # determined without a TeX distribution
    checkable = (groups["inputs"] + groups["bibliography"]
                 + groups["bibliography_add"] + groups["figures"])
    manifest = {"groups": {k: sorted(set(v)) for k, v in groups.items() if v}}
    if base_dir is not None:
        def exists(name: str) -> bool:
            p = base_dir / name
            if p.exists():
                return True
            if not p.suffix:  # no extension -> try common image formats
                return any((base_dir / f"{name}{e}").exists()
                           for e in (".pdf", ".png", ".jpg", ".jpeg", ".eps"))
            return False
        manifest["missing"] = sorted({a for a in checkable if not exists(a)})
    return manifest


def clean_latex(tex: str, base_dir: Path = None) -> dict:
    """Static scan + cleanup (does not modify the original file)."""
    issues = []
    cleaned, cstats = strip_comments(tex)

    unused = find_unused_packages(cleaned)
    if unused:
        issues.append({"type": "unused_packages", "packages": unused,
                       "fix": "Remove \\usepackage for packages never invoked"})

    assets = collect_assets(cleaned, base_dir)
    if assets.get("groups", {}).get("inputs"):
        issues.append({"type": "external_files",
                       "files": assets["groups"]["inputs"],
                       "note": "Ensure all \\input/\\include files ship in the submission"})
    if assets.get("missing"):
        issues.append({"type": "missing_assets", "files": assets["missing"],
                       "fix": "Reference exists but file not found next to the .tex"})

    fig_refs = assets.get("groups", {}).get("figures", [])
    low_res = [f for f in fig_refs if "lowres" in f.lower() or f.lower().endswith(".bmp")]
    if low_res:
        issues.append({"type": "low_res_figures", "files": low_res,
                       "fix": "Convert to PDF/PNG at >=300dpi"})

    if r"\tableofcontents" in cleaned:
        issues.append({"type": "toc_present", "fix": "Remove \\tableofcontents for arXiv"})
    if r"\listoffigures" in cleaned:
        issues.append({"type": "lof_present", "fix": "Remove \\listoffigures for arXiv"})

    long_urls = re.findall(r"\\url\{([^}]{50,})\}", cleaned)
    if long_urls:
        issues.append({"type": "long_urls", "count": len(long_urls),
                       "fix": "Use \\href{url}{short text} instead"})

    refs = set(re.findall(r"\\(?:ref|eqref|autoref|cref)\{([^}]+)\}", cleaned))
    labels = set(re.findall(r"\\label\{([^}]+)\}", cleaned))
    missing_refs = sorted(refs - labels)
    if missing_refs:
        issues.append({"type": "undefined_refs", "refs": missing_refs[:10],
                       "fix": "Add \\label or remove the \\ref"})

    non_ascii = sorted({c for c in cleaned if ord(c) > 127})
    if non_ascii:
        issues.append({"type": "non_ascii", "count": sum(
            1 for c in cleaned if ord(c) > 127),
            "examples": non_ascii[:10],
            "fix": "Replace with LaTeX commands or remove"})

    return {
        "status": "clean" if not issues else "issues_found",
        "issues": issues,
        "unused_packages": unused,
        "assets": assets,
        "removed_comments": cstats["removed_comments"],
        "full_line_comments_removed": cstats["full_line_comments_removed"],
        "n_lines_original": len(tex.split("\n")),
        "n_lines_cleaned": len(cleaned.split("\n")),
        "arxiv_ready": len(issues) == 0,
        "cleaned_text": cleaned,
    }


def main():
    parser = argparse.ArgumentParser(description="LaTeX cleaner for arXiv (SOTA)")
    parser.add_argument("--input", required=True, help="LaTeX file")
    parser.add_argument("--clean", action="store_true",
                        help="Write cleaned output (requires --output; never edits input)")
    parser.add_argument("--output", help="Output file for cleaned source")
    parser.add_argument("--dir", help="Base dir for asset existence check (default: input's dir)")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        print(json.dumps({"status": "error", "error": f"Not found: {args.input}"}, indent=2))
        return 1
    if args.clean and not args.output:
        print(json.dumps({"status": "error",
                          "error": "--clean requires --output (dry-run otherwise); "
                                   "input file is never modified"},
                         indent=2))
        return 1

    tex = p.read_text(encoding="utf-8")
    base = Path(args.dir) if args.dir else p.parent
    result = clean_latex(tex, base)

    if args.clean:
        Path(args.output).write_text(result.pop("cleaned_text"), encoding="utf-8")
        result["cleaned_to"] = args.output
    else:
        result.pop("cleaned_text", None)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
