#!/usr/bin/env python3
"""Journal Adapt — venue format adaptation (venue rule validation).

Targets 2026 venue rules (IEEE / ACM / NeurIPS / ACL / Nature). It replaces the old
"words/500 across-the-board" heuristic with a **column-aware + references-page-deduction**
page model, and adds abstract limits, required sections, citation style, and double-blind checks.

Usage:
  python3 journal_adapt.py --input draft.tex --target ieee_conf
  python3 journal_adapt.py --input draft.tex --target neurips --template-year 2025

Honest disclaimer: page counts are **estimates** (words_per_page is a community rule of
thumb for columns/font size). Before real submission you MUST compile with the venue's
official template to confirm; `--template-year` only changes the year string in the class
name and does not guarantee the template exists.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

# Per-venue rule table (words_per_page is a rule of thumb for columns/font size;
# refs_included = whether the body page count includes references)
JOURNAL_SPECS = {
    "ieee_conf": dict(
        name="IEEE Conference", cls="IEEEtran", options="conference",
        columns=2, font_size=10, page_limit=8, refs_included=True,
        words_per_page=950, abstract_max_words=250, anonymous=False, ref_style="numeric",
        required_sections=["Introduction", "Related Work", "Method", "Experiments", "Conclusion"],
        banned=["In this paper, we", "very novel"],
        notes="8 pages incl. references; extra pages require overlength charge."),
    "acm": dict(
        name="ACM SIGCONF", cls="acmart", options="sigconf",
        columns=2, font_size=9, page_limit=12, refs_included=True,
        words_per_page=1000, abstract_max_words=250, anonymous=True, ref_style="numeric",
        required_sections=["Introduction", "Related Work", "Method", "Evaluation", "Conclusion"],
        banned=[],
        notes="Double-blind: no author names / affiliations / acknowledgements in submission."),
    "neurips": dict(
        name="NeurIPS", cls="neurips_2025", options="",
        columns=1, font_size=10, page_limit=9, refs_included=False,
        words_per_page=600, abstract_max_words=200, anonymous=True, ref_style="numeric",
        required_sections=["Introduction", "Method", "Experiments", "Limitations", "Conclusion"],
        banned=[],
        notes="9 pages excl. references; a Limitations section is REQUIRED; paper checklist mandated."),
    "acl": dict(
        name="ACL/EMNLP", cls="acl", options="",
        columns=2, font_size=10, page_limit=8, refs_included=False,
        words_per_page=950, abstract_max_words=200, anonymous=True, ref_style="numeric",
        required_sections=["Introduction", "Related Work", "Method", "Experiments", "Conclusion"],
        banned=["state-of-the-art performance"],
        notes="8 pages excl. references; Limitations section required; double-blind."),
    "nature": dict(
        name="Nature", cls="nature", options="",
        columns=2, font_size=9, page_limit=5, refs_included=True,
        words_per_page=600, abstract_max_words=200, anonymous=False, ref_style="numeric",
        required_sections=["Introduction", "Results", "Discussion", "Methods"],
        banned=["In this paper we", "Novel", "in this paper"],
        notes="Articles ~5 pages / main text ~3000 words; abstract is an unnumbered first paragraph."),
}

# common aliases
ALIASES = {"ieee": "ieee_conf", "ieee_journal": "ieee_conf", "emnlp": "acl", "naacl": "acl",
           "sigconf": "acm", "nips": "neurips"}


def _extract_abstract(text: str) -> str:
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", text, re.S)
    if m:
        return m.group(1)
    m = re.search(r"\\abstract\{(.*?)\}\s*(?:\n|$)", text, re.S)
    return m.group(1) if m else ""


def _split_bibliography(text: str) -> tuple:
    """Return (body, bibliography block). Supports \\bibliography and the thebibliography environment."""
    m = re.search(r"\\begin\{thebibliography\}(?:\{[^}]*\})?.*?\\end\{thebibliography\}",
                  text, re.S)
    if m:
        return text[:m.start()] + text[m.end():], m.group(0)
    m = re.search(r"\\bibliography\{", text)
    if m:
        return text[:m.start()], text[m.start():]
    m = re.search(r"\\printbibliography|\\addbibresource", text)
    if m:
        return text[:m.start()], text[m.start():]
    return text, ""


def adapt(text: str, target: str, template_year: str = None) -> dict:
    key = ALIASES.get(target, target)
    spec = JOURNAL_SPECS.get(key)
    if spec is None:
        raise ValueError(f"unknown target '{target}' (options: {', '.join(JOURNAL_SPECS)})")

    issues = []
    body, bib = _split_bibliography(text)
    words = len(text.split())
    body_words = len(body.split())
    n_bibitems = len(re.findall(r"\\bibitem", bib))
    ref_pages = math.ceil(n_bibitems / 45) if n_bibitems else 0

    body_pages = body_words / spec["words_per_page"]
    total_pages = body_pages + ref_pages
    billable = total_pages if spec["refs_included"] else body_pages

    if billable > spec["page_limit"]:
        issues.append({"type": "page_limit", "severity": "high",
                       "message": f"{billable:.1f} billable pages > {spec['page_limit']} "
                                  f"(refs {'included' if spec['refs_included'] else 'excluded'}, "
                                  f"{ref_pages} ref pages)",
                       "fix": "Trim body text or move proofs to the appendix"})

    # abstract word limit
    abstract = _extract_abstract(text)
    abstract_words = len(abstract.split()) if abstract.strip() else 0
    if not abstract.strip():
        issues.append({"type": "missing_abstract", "severity": "high",
                       "fix": "Add \\begin{abstract}...\\end{abstract}"})
    elif abstract_words > spec["abstract_max_words"]:
        issues.append({"type": "abstract_too_long", "severity": "medium",
                       "message": f"abstract {abstract_words} words > {spec['abstract_max_words']}",
                       "fix": "Cut modifiers, not results"})

    # required sections
    low = text.lower()
    for sec in spec["required_sections"]:
        if sec.lower() not in low:
            issues.append({"type": "missing_section", "severity": "high", "section": sec,
                           "fix": f"Add a '{sec}' section (venue requires it)"})

    # banned phrases
    for banned in spec.get("banned", []):
        if banned.lower() in low:
            issues.append({"type": "banned", "severity": "medium", "phrase": banned,
                           "fix": "Replace with a specific, evidence-backed claim"})

    # citation style
    has_author_year = bool(re.search(r"\\cite[pt]\{", text)) or bool(re.search(r"\\textcite", text))
    detected_style = "author-year" if has_author_year else "numeric"
    if detected_style != spec["ref_style"]:
        issues.append({"type": "ref_style", "severity": "low",
                       "message": f"detected {detected_style}, venue expects {spec['ref_style']}",
                       "fix": "Regenerate the bibliography with the venue's .bst/.bbx style"})

    # double-blind
    anonymous_ok = True
    if spec["anonymous"]:
        author_hits = re.findall(r"\\author\{([^}]*)\}", text)
        named = [a for a in author_hits if a.strip() and "anonym" not in a.lower()]
        ack = bool(re.search(r"\\section\*?\{Acknowledge?ments?\}", text, re.I))
        if named or ack:
            anonymous_ok = False
            issues.append({"type": "anonymity", "severity": "high",
                           "evidence": (named[:2] or []) + (["Acknowledgements"] if ack else []),
                           "fix": "Remove author block / acknowledgements for double-blind review"})

    cls = spec["cls"]
    if template_year and re.search(r"_\d{4}$", cls):
        cls = re.sub(r"_\d{4}$", f"_{template_year}", cls)

    score = max(0, 100 - sum({"high": 25, "medium": 12, "low": 5}[i["severity"]]
                             for i in issues))
    return {
        "target": spec["name"],
        "class": cls,
        "columns": spec["columns"],
        "score": score,
        "status": "pass" if not issues else "adjust_needed",
        "issues": issues,
        "words": words,
        "body_words": body_words,
        "est_pages": round(total_pages, 1),
        "est_billable_pages": round(billable, 1),
        "page_limit": spec["page_limit"],
        "refs_included": spec["refs_included"],
        "ref_pages": ref_pages,
        "abstract_words": abstract_words,
        "abstract_limit": spec["abstract_max_words"],
        "ref_style_detected": detected_style,
        "anonymous_ok": anonymous_ok,
        "method": "column-aware-estimate",
        "notes": spec["notes"],
    }


def main():
    parser = argparse.ArgumentParser(description="Journal/venue format check (SOTA)")
    parser.add_argument("--input", required=True, help="Draft file (.tex or plain text)")
    parser.add_argument("--target", default="ieee_conf",
                        choices=sorted(list(JOURNAL_SPECS) + list(ALIASES)))
    parser.add_argument("--template-year", help="Override year token in template class name")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    p = Path(args.input)
    if not p.exists():
        print(json.dumps({"status": "error", "error": f"File not found: {args.input}"}, indent=2))
        return 1

    text = p.read_text(encoding="utf-8")
    try:
        result = adapt(text, args.target, args.template_year)
    except ValueError as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False, indent=2))
        return 2
    result["file"] = str(p)

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    sys.exit(main())
