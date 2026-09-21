#!/usr/bin/env python3
"""AI Humanizer — 检测学术文本中的 AI 腔措辞与「过度平滑」的结构特征。

对标 academic-humanizer，但补上旧版完全缺失的**结构维度**：
  - burstiness（句长方差 / 均值）：人类写作句长起伏大，LLM 输出往往偏均匀；
  - 句首重复：连续 ≥3 句用同一个开头词（Furthermore/Moreover…）；
  - 词汇多样性 TTR（去停用词后 unique/total）；
  - 重复 5-gram：同一串连续词反复出现。

诚实声明（重要）：**AI 文本检测器在 2026 年依然不可靠**（高误报率，OpenAI 已于 2023 年
关停其 classifier；学术机构明确指出检测器分数不可作为学术不端的证据）。本工具测的是
「文风痕迹」，不是「作者身份」——输出只能用于**改写建议**，MUST NOT 用于指控。

用法:
  python3 ai_humanizer.py --file draft.tex --report
  python3 ai_humanizer.py --text "Our novel framework leverages state-of-the-art methods"
"""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

AI_PATTERNS = {
    "buzzwords": {
        "pattern": r"\b(novel|pioneering|state-of-the-art|groundbreaking|revolutionary|unprecedented)\b",
        "replace_with": "Be specific: what's new? What SOTA does it beat? By how much?",
        "severity": "high",
    },
    "hedging_overuse": {
        "pattern": r"\b(we believe|we argue|it is worth noting|it should be noted|notably|interestingly)\b",
        "replace_with": "State the claim directly: 'X works (Table 2: 94% F1)'",
        "severity": "medium",
    },
    "empty_adjectives": {
        "pattern": r"\b(effective|efficient|robust|scalable|flexible)\s+(and|,|or)\s+\w+",
        "replace_with": "Pick one adjective backed by evidence; 'effective and efficient' needs two numbers",
        "severity": "medium",
    },
    "template_phrases": {
        "pattern": r"\b(in this paper|in this work|in the present study|we present|we propose a (?:novel|new))\b",
        "replace_with": "Cut it. Start with the contribution: 'Our method achieves X by doing Y'",
        "severity": "high",
    },
    "excessive_qualifiers": {
        "pattern": r"\b(somewhat|fairly|quite|very|extremely|particularly|especially|substantially|significantly)\b",
        "replace_with": "Use numbers instead: 'extremely fast' -> '2.3x faster (Table 3)'",
        "severity": "low",
    },
    "repeated_transitions": {
        "pattern": r"\b(Furthermore|Moreover|Additionally|In addition)\b",
        "replace_with": "Vary transitions; don't open 3+ sentences the same way",
        "severity": "medium",
    },
    "passive_excess": {
        "pattern": r"\b(was (?:performed|conducted|carried|executed)|were (?:performed|conducted|collected))\b",
        "replace_with": "Active voice: 'We performed X' > 'X was performed'",
        "severity": "low",
    },
    "llm_verb_spam": {  # 2024+ LLM 高频动词
        "pattern": r"\b(delve|leverage|underscore|showcase|foster|garner|bolster|pivotal|crucial|intricate)\b",
        "replace_with": "Plain verbs win: 'use' not 'leverage', 'show' not 'showcase'",
        "severity": "high",
    },
}

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are",
    "was", "were", "we", "our", "this", "that", "it", "as", "by", "be", "at", "from",
    "which", "can", "has", "have", "not", "but", "than", "then", "its", "their",
}


def _positions(text: str, pattern: str, limit: int = 5) -> list:
    """返回命中的 line:col 位置，便于人工定位。"""
    out = []
    for m in re.finditer(pattern, text, re.IGNORECASE):
        line = text.count("\n", 0, m.start()) + 1
        col = m.start() - (text.rfind("\n", 0, m.start()) + 1) + 1
        out.append(f"L{line}:C{col}")
        if len(out) >= limit:
            break
    return out


def _sentences(text: str) -> list:
    stripped = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", text)  # 去掉环境标记
    parts = re.split(r"(?<=[.!?])\s+", stripped)
    return [p.strip() for p in parts if len(p.strip().split()) >= 3]


def structural_metrics(text: str) -> dict:
    """句长起伏 / 句首重复 / 词汇多样性 / 重复 n-gram。"""
    sents = _sentences(text)
    lengths = [len(s.split()) for s in sents]
    if len(lengths) >= 3:
        mean = statistics.mean(lengths)
        sd = statistics.pstdev(lengths)
        burstiness = round(sd / mean, 3) if mean else 0.0
    else:
        mean, burstiness = (statistics.mean(lengths) if lengths else 0), None

    # 句首重复：最长连续同开头词
    openers = [re.match(r"[\w']+", s.lower()).group(0) for s in sents if re.match(r"[\w']+", s)]
    max_run, run, prev = 0, 0, None
    for w in openers:
        run = run + 1 if w == prev else 1
        max_run = max(max_run, run)
        prev = w

    tokens = [t for t in re.findall(r"[A-Za-z']+", text.lower()) if t not in STOPWORDS]
    ttr = round(len(set(tokens)) / len(tokens), 3) if tokens else None

    grams = [" ".join(tokens[i:i + 5]) for i in range(max(0, len(tokens) - 4))]
    repeats = {}
    for g in grams:
        repeats[g] = repeats.get(g, 0) + 1
    repeated = sorted({g: c for g, c in repeats.items() if c >= 2}.items(),
                      key=lambda kv: -kv[1])[:5]

    return {
        "n_sentences": len(sents),
        "mean_sentence_len": round(mean, 1) if lengths else 0,
        "burstiness": burstiness,
        "max_opener_run": max_run,
        "type_token_ratio": ttr,
        "repeated_5grams": [{"gram": g, "count": c} for g, c in repeated],
    }


def humanize(text: str) -> dict:
    issues = []
    for name, rule in AI_PATTERNS.items():
        matches = re.findall(rule["pattern"], text, re.IGNORECASE)
        if matches:
            issues.append({
                "type": name,
                "matches": matches[:5],
                "count": len(matches),
                "positions": _positions(text, rule["pattern"]),
                "severity": rule["severity"],
                "fix_hint": rule["replace_with"],
            })

    metrics = structural_metrics(text)
    structural = []
    b = metrics["burstiness"]
    if b is not None and b < 0.35:
        structural.append({"type": "low_burstiness", "value": b,
                           "fix_hint": "Sentence lengths too uniform — vary short/long, "
                                       "lead with a short claim sentence"})
    if metrics["max_opener_run"] >= 3:
        structural.append({"type": "opener_repetition",
                           "value": metrics["max_opener_run"],
                           "fix_hint": f"{metrics['max_opener_run']} consecutive sentences share "
                                       "the same opener — rotate transitions"})
    if metrics["type_token_ratio"] is not None and metrics["n_sentences"] >= 20 \
            and metrics["type_token_ratio"] < 0.35:
        structural.append({"type": "low_lexical_diversity",
                           "value": metrics["type_token_ratio"],
                           "fix_hint": "Narrow vocabulary for this length — check for "
                                       "repeated sentence templates"})
    for r in metrics["repeated_5grams"]:
        structural.append({"type": "repeated_ngram", "value": r["gram"], "count": r["count"],
                           "fix_hint": "Same 5-gram recurs — deduplicate or merge those sentences"})

    weight = sum(i["count"] * {"high": 3, "medium": 2, "low": 1}[i["severity"]] for i in issues)
    score = 100 - weight * 3
    score -= 12 * sum(1 for s in structural if s["type"] == "low_burstiness")
    score -= 8 * sum(1 for s in structural if s["type"] == "opener_repetition")
    score -= 6 * sum(1 for s in structural if s["type"] == "low_lexical_diversity")
    score -= min(9, 3 * sum(1 for s in structural if s["type"] == "repeated_ngram"))
    score = max(0, score)

    return {
        "score": score,
        "status": "clean" if score >= 85 else "needs_edit",
        "issues": issues,
        "structural": structural,
        "metrics": metrics,
        "n_flags": len(issues) + len(structural),
        "method": "lexical+structural",
        "detector_note": ("AI-text detectors are unreliable (high false-positive rates; OpenAI "
                          "retired its classifier in 2023). This tool measures style tells, not "
                          "authorship. Use for revision only — never for misconduct claims."),
        "summary": f"{len(issues)} lexical + {len(structural)} structural findings, {score}/100",
    }


def main():
    parser = argparse.ArgumentParser(description="AI writing humanizer (lexical + structural)")
    parser.add_argument("--text", help="Text to check")
    parser.add_argument("--file", help="File to check")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--output", help="Output JSON")
    args = parser.parse_args()

    if args.file and Path(args.file).exists():
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        parser.error("Need --text or --file (or --file path does not exist)")
        return

    result = humanize(text)

    if args.report:
        print(f"AI-Humanize Score: {result['score']}/100  [{result['method']}]")
        print(f"Status: {result['status']}")
        m = result["metrics"]
        print(f"Sentences: {m['n_sentences']}  burstiness: {m['burstiness']}  "
              f"max opener run: {m['max_opener_run']}  TTR: {m['type_token_ratio']}")
        print(f"\nLexical issues ({len(result['issues'])}):")
        for i in result["issues"]:
            print(f"  [{i['severity'].upper()}] {i['type']}: {i['count']} hits {i['positions']}")
            print(f"    Fix: {i['fix_hint'][:70]}")
        print(f"\nStructural issues ({len(result['structural'])}):")
        for s in result["structural"]:
            print(f"  [{s['type']}] value={s['value']}")
            print(f"    Fix: {s['fix_hint'][:70]}")
        print(f"\nNote: {result['detector_note']}")
    else:
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output)


if __name__ == "__main__":
    sys.exit(main())
