#!/usr/bin/env python3
"""Self Reviewer — 模拟审稿 + 质量检查清单。

对标 2026 ML 可复现性审查标准（papers-with-code 清单 + IMRaD + 统计门槛）：
  - 每个 check 给出 evidence（原文命中片段，可复核）而非只给布尔；
  - 区分 hard gate（必须）与 soft gate（建议），uncertain 项显式标注"需人工/LLM 复核"；
  - --llm 标记：若提供 --llm-evidence（JSON 文件），则用模型给出的 evidence/confidence
    替代关键词命中；缺失时回退关键词（method=keyword-fallback，如实标注）。

用法:
  python3 self_reviewer.py --paper draft.tex
  python3 self_reviewer.py --paper draft.tex --llm-evidence llm_review.json --output review.json
  python3 self_reviewer.py --paper draft.tex --checklist
"""
import argparse
import json
import re
import sys
from pathlib import Path

# 四类清单（结构/内容/写作/格式），语义项脚本不自动判定 → 进 uncertain + 需 LLM/人工
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

# 关键词映射：check → 可命中的关键词集合（命中=自动 pass，否则进 uncertain 需复核）
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
    """Run self-review. llm_evidence: {check: {evidence, confidence}}，缺失用关键词回退。"""
    words = len(tex.split())
    checks = {"passed": [], "failed": [], "uncertain": []}
    evidence = {}
    method = "llm-evidence" if llm_evidence else "keyword-fallback"

    # 结构 hard gate
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

    # 内容 soft gate（可关键词或 LLM 命中）
    for check, kws in KEYWORDS.items():
        hit = None
        if llm_evidence and check in llm_evidence:
            hit = llm_evidence[check]
            conf = float(hit.get("confidence", 0.0))
            if conf >= 0.6 and hit.get("evidence"):
                evidence[check] = {"source": "llm", "evidence": hit["evidence"], "confidence": conf}
                checks["passed"].append(f"{check} (LLM)")
            else:
                checks["uncertain"].append(f"{check} — LLM 置信度不足 ({conf}), 需人工复核")
        else:
            for kw in kws:
                if kw in tex.lower():
                    evidence[check] = {"source": "keyword", "evidence": _evidence_snippet(tex, kw)}
                    checks["passed"].append(check)
                    hit = True
                    break
            if not hit:
                checks["uncertain"].append(f"{check} — 未命中关键词, 需 LLM/人工复核")

    # Score
    total = len(checks["passed"]) + len(checks["failed"]) + len(checks["uncertain"])
    # uncertain 不计入分母（避免"没检查到"拉低分），但 ready 必须无 uncertain
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
        steps.append("Resolve uncertain items (LLM/人工): " + "; ".join(checks["uncertain"]))
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
