#!/usr/bin/env python3
"""Anti-Defensive Writing — 检测防御性学术写作，并区分「该收紧」与「该保留」。

对标 anti-defensive-writing (771 stars)，补上旧版把「所有限定都当坏事」的缺陷：
  - **对冲密度**：hedges per 100 words（可量化、可跨稿对比）；
  - **retain / tighten 分类**：若限定语出现在**统计不确定语境**（置信区间、p 值、方差、
    样本量、分布漂移、估计量…）附近，则属**合理统计限定，必须保留**（action=retain）；
    只有语言性弱化（双重对冲、自贬、填充短语）才标 action=tighten；
  - **定位**：每处命中给 line:col。

诚实声明：分数只对 action=tighten 的命中扣分；`retain` 项不扣分——把统计限定删掉
换来的「语气更硬」是**学术错误**，不是改进。

用法:
  python3 anti_defensive.py --text "Our results suggest that the method may possibly improve"
  python3 anti_defensive.py --file draft_section.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFENSIVE_PATTERNS = [
    {
        "type": "double_hedge",
        "pattern": r"\b(may|might|could) (?:possibly|potentially|arguably)\b",
        "issue": "Double hedging — 'may possibly' is weaker than either alone",
        "fix": "Pick one hedge. If the result is statistical, keep 'may' and add the CI.",
        "severity": "high",
    },
    {
        "type": "vague_attribution",
        "pattern": r"\b(to the best of our knowledge|to our knowledge|as far as we know)\b",
        "issue": "Defensive qualifier that signals you have not checked",
        "fix": "Cite the survey/benchmark that establishes the gap instead.",
        "severity": "medium",
    },
    {
        "type": "filler_phrase",
        "pattern": r"\b(it should be noted that|we would like to point out|it is important to note)\b",
        "issue": "Filler phrase that weakens the claim",
        "fix": "Cut it. State the fact directly.",
        "severity": "medium",
    },
    {
        "type": "weak_self_criticism",
        "pattern": r"\b(some limitations exist|there are certain drawbacks|we acknowledge that)\b",
        "issue": "Weak self-criticism — a reviewer will criticize harder",
        "fix": "State the limitation with evidence: 'Accuracy drops 3% on X (Table 7)'",
        "severity": "medium",
    },
    {
        "type": "editorializing",
        "pattern": r"\b(not surprisingly|unfortunately|regrettably)\b",
        "issue": "Editorializing — inappropriate for academic voice",
        "fix": "Remove opinion. State the result neutrally.",
        "severity": "low",
    },
    {
        "type": "undersell",
        "pattern": r"\b(a minor|a small|a modest|negligible) (improvement|gain|degradation|effect)\b",
        "issue": "Underselling your own result",
        "fix": "Report the number: '1.2% improvement', not 'a minor improvement'",
        "severity": "low",
    },
]

# 统计不确定语境：限定语出现在其附近 → 视为合理统计限定，保留
LEGIT_CONTEXT = re.compile(
    r"(confidence interval|\bci\b|\bp\s*[=<>]\s*0?\.\d|\bp-value|\bvariance\b|std\.?\s*dev|"
    r"sample size|\bn\s*=\s*\d|distribution shift|out-of-distribution|\bood\b|hypothes|"
    r"estimate|correlation|statistical|\bseed\b|error bar|wider study|further data)",
    re.IGNORECASE,
)

# 用于密度统计的对冲词表（含未被上面 pattern 命中的单词对冲）
HEDGE_LEXICON = re.compile(
    r"\b(may|might|could|possibly|potentially|perhaps|likely|unlikely|suggest|suggests|"
    r"indicat\w+|appear\w*|seem\w*|tend\w*|arguably|presumably|roughly|approximately)\b",
    re.IGNORECASE,
)


def _pos(text: str, start: int) -> str:
    line = text.count("\n", 0, start) + 1
    col = start - (text.rfind("\n", 0, start) + 1) + 1
    return f"L{line}:C{col}"


def check(text: str, context_window: int = 80) -> dict:
    issues = []
    for p in DEFENSIVE_PATTERNS:
        hits = list(re.finditer(p["pattern"], text, re.IGNORECASE))
        if not hits:
            continue
        retained, tightened, positions, examples = 0, 0, [], []
        for m in hits:
            lo = max(0, m.start() - context_window)
            hi = min(len(text), m.end() + context_window)
            legit = bool(LEGIT_CONTEXT.search(text[lo:hi]))
            if legit:
                retained += 1
            else:
                tightened += 1
            if len(positions) < 5:
                positions.append(_pos(text, m.start()))
                examples.append(m.group(0))
        issues.append({
            "type": p["type"],
            "issue": p["issue"],
            "fix": p["fix"],
            "severity": p["severity"],
            "count": len(hits),
            "action": "retain" if tightened == 0 else "tighten",
            "retained": retained,
            "tightened": tightened,
            "positions": positions,
            "examples": examples,
        })

    words = max(len(text.split()), 1)
    hedge_hits = len(HEDGE_LEXICON.findall(text))
    hedge_density = round(hedge_hits / words * 100, 2)

    tighten_hits = sum(i["tightened"] for i in issues)
    retain_hits = sum(i["retained"] for i in issues)
    score = max(0, 100 - tighten_hits * 15)

    return {
        "score": score,
        "status": "clean" if score >= 80 else "rewrite_needed",
        "issues": issues,
        "n_flags": sum(1 for i in issues if i["tightened"] > 0),
        "n_retained_only": sum(1 for i in issues if i["tightened"] == 0),
        "hedge_density_per_100w": hedge_density,
        "hedges_total": hedge_hits,
        "words": words,
        "tighten_hits": tighten_hits,
        "retain_hits": retain_hits,
        "method": "pattern+context-classifier",
        "note": ("'retain' items sit next to statistical-uncertainty context (CI / p-value / "
                 "variance / sample size). Deleting them is an academic error, not a style fix."),
    }


def main():
    parser = argparse.ArgumentParser(description="Anti-defensive writing check (retain/tighten)")
    parser.add_argument("--text", help="Text to check")
    parser.add_argument("--file", help="File to check")
    parser.add_argument("--context-window", type=int, default=80,
                        help="Chars around a hit searched for statistical context")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(json.dumps({"status": "error", "error": f"File not found: {args.file}"}, indent=2))
            return 1
        text = p.read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        parser.error("Need --text or --file")
        return

    result = check(text, args.context_window)
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)


if __name__ == "__main__":
    sys.exit(main())
