#!/usr/bin/env python3
"""Self Reviewer — simulated review + quality checklist.

Targets 2026 ML reproducibility review standards (papers-with-code checklist + IMRaD +
statistical thresholds):
  - each check gives evidence (a snippet from the source, verifiable) rather than just a boolean;
  - distinguishes hard gates (required) from soft gates (recommended); uncertain items are
    explicitly marked "needs human/LLM review";
  - --llm mode: if --llm-evidence (a JSON file) is supplied, use the model's evidence/confidence
    instead of keyword hits; if missing, fall back to keywords (method=keyword-fallback, labeled honestly).

Usage:
  python3 self_reviewer.py --paper draft.tex
  python3 self_reviewer.py --paper draft.tex --llm-evidence llm_review.json --output review.json
  python3 self_reviewer.py --paper draft.tex --checklist
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Four checklist categories (structure/content/writing/format); semantic items the script
# cannot auto-judge -> go into uncertain + need LLM/human review
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
        "No first-person 'we' abuse",
        "Claim supported by evidence",
        "No unsupported superlatives ('best','state-of-the-art')",
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

# Keyword map: check -> set of matchable keywords (a hit = auto pass, otherwise goes to uncertain for review)
KEYWORDS = {
    "Statistical significance tested": ["p-value", "p < ", "significance", "paired t-test", "wilcoxon", "95% ci", "confidence interval"],
    "Ablation study included": ["ablation"],
    "Baseline methods compared (2+)": ["baseline", "compared against", "compared with", "state-of-the-art", "sota"],
    "Limitations discussed": ["limitation", "limit of", "caveat", "threat to validity"],
    "Reproducibility info present (code, data, seeds)": ["seed", "reproducib", "release code", "github", "open-source", "data availab"],
}


def _evidence_snippet(tex: str, kw: str, width: int = 60) -> str:
    m = re.search(re.escape(kw), tex, re.I)
    if not m:
        return ""
    s = max(0, m.start() - width)
    e = min(len(tex), m.end() + width)
    return tex[s:e].replace("\n", " ").strip()


def review_paper(tex: str, llm_evidence: dict = None) -> dict:
    """Run self-review. llm_evidence: {check: {evidence, confidence}}; falls back to keywords when missing."""
    words = len(tex.split())
    checks = {"passed": [], "failed": [], "uncertain": []}
    evidence = {}
    method = "llm-evidence" if llm_evidence else "keyword-fallback"

    # structure hard gate
    has_abstract = bool(re.search(r"\\(section|subsection)\{?[ {]?Abstract", tex)) or "abstract" in tex[:2000].lower()
    if has_abstract:
        checks["passed"].append("Has abstract")
    else:
        checks["failed"].append("Missing abstract")

    n_sections = len(re.findall(r"\\section\{?", tex))
    if n_sections >= 4:
        checks["passed"].append(f"Sufficient sections ({n_sections})")
    else:
        checks["failed"].append(f"Only {n_sections} sections")

    if "\\cite" in tex or "\\bibliography" in tex:
        checks["passed"].append("Has citations")
    else:
        checks["failed"].append("No citations found")

    if words < 3000:
        checks["failed"].append(f"Too short: {words} words (min ~4000)")
    else:
        checks["passed"].append(f"Adequate length ({words} words)")

    # content soft gate (keyword or LLM hit)
    for check, kws in KEYWORDS.items():
        hit = None
        if llm_evidence and check in llm_evidence:
            hit = llm_evidence[check]
            conf = float(hit.get("confidence", 0.0))
            if conf >= 0.6 and hit.get("evidence"):
                evidence[check] = {"source": "llm", "evidence": hit["evidence"], "confidence": conf}
                checks["passed"].append(f"{check} (LLM)")
            else:
                checks["uncertain"].append(f"{check} - LLM confidence too low ({conf}), needs human review")
        else:
            for kw in kws:
                if kw in tex.lower():
                    evidence[check] = {"source": "keyword", "evidence": _evidence_snippet(tex, kw)}
                    checks["passed"].append(check)
                    hit = True
                    break
            if not hit:
                checks["uncertain"].append(f"{check} - no keyword hit, needs LLM/human review")

    # Score
    total = len(checks["passed"]) + len(checks["failed"]) + len(checks["uncertain"])
    # uncertain items are not counted in the denominator (so "not checked" does not drag the
    # score down), but ready requires zero uncertain items
    denom = max(len(checks["passed"]) + len(checks["failed"]), 1)
    score = int(100 * len(checks["passed"]) / denom)
    status = "ready" if (score >= 80 and not checks["uncertain"]) else "needs_work"

    return {
        "word_count": words,
        "score": score,
        "method": method,
        "passed": checks["passed"],
        "failed": checks["failed"],
        "uncertain": checks["uncertain"],
        "evidence": evidence,
        "status": status,
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
    if any("Too short" in f for f in checks["failed"]):
        steps.append("Expand results section with more experiments")
    if checks["uncertain"]:
        steps.append("Resolve uncertain items (LLM/human): " + "; ".join(checks["uncertain"]))
    if not steps:
        steps.append("All gates pass — ready for downstream (journal-adapt / tex-cleaner)")
    return steps


def main():
    parser = argparse.ArgumentParser(description="Paper self-review (SOTA reproducibility rubric)")
    parser.add_argument("--paper", required=True, help="LaTeX/markdown file")
    parser.add_argument("--checklist", action="store_true", help="Print full checklist")
    parser.add_argument("--llm-evidence", help="JSON: {check: {evidence, confidence}}")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    p = Path(args.paper)
    if not p.exists():
        print(json.dumps({"error": f"File not found: {args.paper}"}, indent=2))
        return 1

    content = p.read_text(encoding="utf-8")

    if args.checklist:
        print(json.dumps(CHECKLIST, ensure_ascii=False, indent=2))
        return

    llm = None
    if args.llm_evidence:
        lp = Path(args.llm_evidence)
        if lp.exists():
            llm = json.loads(lp.read_text(encoding="utf-8"))

    result = review_paper(content, llm)
    result["file"] = str(p)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())
