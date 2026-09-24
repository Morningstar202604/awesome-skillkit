#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""trace_scanner.py -- AI-tone statistics scanner (pure stdlib, no third-party deps).

Usage:
    python3 scripts/trace_scanner.py <file>    # scan a text file (utf-8)
    cat draft.md | python3 scripts/trace_scanner.py -   # read from stdin

Output (a single JSON object on stdout; normal exit code is always 0):
    {
      "stats": {
        "sentences": 12,              # sentence count (cv is undecidable when < 3)
        "mean_sentence_len": 38.2,    # mean sentence length (effective chars, minus punctuation/whitespace)
        "std_sentence_len": 9.1,      # population std dev of sentence length
        "cv": 0.24,                   # length variation ratio = std/mean; < 0.5 flags "too-uniform length"
        "cv_threshold": 0.5,
        "list_lines": 8,              # list-item lines (starting with - * digit. etc.)
        "total_lines": 19,            # total non-empty lines
        "list_ratio": 0.42,           # list density = list_lines/total_lines; > 0.4 warns
        "enumerator_count": 3,        # total enumerator words (firstly/secondly/lastly/...)
        "ai_word_hits": 6,            # total AI-cliche hits
        "score": 34,                  # overall score 0-100; higher = more human-like
        "verdict": "heavy_ai_style"
      },
      "findings": [
        {"pos": "L3", "type": "ai_word",
         "evidence": "...it is important to note that...",
         "fix_hint": "delete it or make it a direct statement"}
      ]
    }

findings[].type values:
    ai_word                 AI cliche hit (built-in word list, English)
    uniform_sentence_length length variation ratio cv < 0.5 (empirical threshold, tunable)
    parallelism             >= 3 clauses in one sentence opening with the same head (over-parallelism heuristic)
    enumerator_chain        firstly...secondly / secondly...lastly / first...second chains
    list_density            list-line ratio > 0.4

Scoring rules (empirical, tunable):
    score starts at 100; each ai_word hit -6; cv < 0.5 another -20;
    list_ratio > 0.4 another -15; each parallelism -10; each enumerator_chain -8; floor 0.
    verdict bands: >= 80 human_like | >= 60 light_ai_traces |
                 >= 40 obvious_ai_style | < 40 heavy_ai_style

Heuristic caveat (honest disclaimer): this tool is based on a word list and statistical
features, does not use a language model, and cannot replace an official AI detector; a hit is
not plagiarism, and a miss is not proof of human authorship.
"""

import json
import math
import re
import sys

CV_THRESHOLD = 0.5        # length-variation alarm line (empirical, tunable)
LIST_RATIO_THRESHOLD = 0.4  # list-density alarm line (empirical, tunable)
SCORE_PER_AI_WORD = 6
SCORE_PENALTY_CV = 20
SCORE_PENALTY_LIST = 15
SCORE_PENALTY_PARALLELISM = 10
SCORE_PENALTY_CHAIN = 8

# AI-cliche word list (built-in, extend as needed). Each entry: (regex, fix hint).
# English uses \b word boundaries, case-insensitive.
AI_PATTERNS = [
    (r"\b(in\s+conclusion|to\s+summarize)\b", "end on a concrete conclusion, not boilerplate"),
    (r"\b(it'?s\s+(?:worth\s+)?noting\s+that)\b", "delete the hedge and state the point directly"),
    (r"\b(leverage|leveraging)\b", "replace with the literal action performed"),
    (r"\b(in\s+the\s+world\s+of|in\s+the\s+realm\s+of)\b", "use 'in' or name the field directly"),
    (r"\b(paradigm|synergy|holistic|robust\s+ecosystem)\b", "name the concrete thing instead of jargon"),
    (r"\b(cutting-edge|state-of-the-art|groundbreaking)\b", "name the actual technique and its improvement"),
    (r"\b(unlock|elevate|embark|harness|foster)\b", "replace with the literal action performed"),
    (r"\bseamless(?:ly)?\b", "describe the actual workflow; smoothness is a claim"),
    (r"\ba\s+testament\s+to\b", "state the evidence directly"),
    (r"\bdelve(?:s|ed|ing)?\b", "replace with a concrete verb: examined, read, tested"),
    (r"\btapestry\b", "drop the metaphor; name the elements directly"),
    (r"\bcrucial\b", "state why it matters instead of rating it"),
    (r"\b(?:moreover|furthermore)\b", "cut it; let sentence order carry the logic"),
    (r"\bit'?s\s+important\s+to\s+note\b", "delete the hedge and say the thing"),
    (r"\bin\s+today'?s\s+(?:fast-?paced\s+)?world\b", "open with a concrete fact instead"),
    (r"\b(?:ever|rapidly)-evolving\b", "name the actual change and its rate"),
    (r"\bin\s+the\s+realm\s+of\b", "use 'in' or name the field directly"),
    (r"\bseamless(?:ly)?\b", "describe the actual workflow; smoothness is a claim"),
    (r"\ba\s+testament\s+to\b", "state the evidence directly"),
    (r"\bfoster(?:s|ed|ing)?\b", "name who did what to whom"),
    (r"\blandscape\b", "name the market/field concretely or drop the word"),
    (r"\brobust\b", "say which failure modes it survives"),
]

SENT_SPLIT_RE = re.compile(r"[。！？!?…]+")
EN_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])(?=\s+[A-Z0-9\"'(“])")
LIST_LINE_RE = re.compile(r"^\s*(?:[-*+]\s+|\d{1,2}[.、)）]\s*)")
PUNCT_RE = re.compile(
    r"[\s，。！？；：、,.!?;:\"'“”‘’（）()\[\]{}…—·\-*/#>`~=|]"
)
ENUMERATOR_RE = re.compile(r"\b(firstly|secondly|thirdly|lastly|finally|first\b|second\b|third\b|on\s+one\s+hand|on\s+the\s+other\s+hand)")


def context(line, start, end, pad=12):
    a = max(0, start - pad)
    b = min(len(line), end + pad)
    frag = line[a:b].replace("\t", " ").strip()
    if a > 0:
        frag = "…" + frag
    if b < len(line):
        frag = frag + "…"
    return frag


def split_line_sentences(line):
    parts = []
    for chunk in SENT_SPLIT_RE.split(line):
        parts.extend(p for p in EN_SENT_SPLIT_RE.split(chunk) if p and p.strip())
    return [p.strip() for p in parts if p and p.strip()]


def effective_len(sentence):
    return len(PUNCT_RE.sub("", sentence))


def detect_parallelism(sentence):
    clauses = [c.strip() for c in re.split(r"[，、,;；]", sentence)]
    clauses = [c for c in clauses if len(c) >= 2]
    if len(clauses) < 3:
        return False
    heads = {}
    for c in clauses:
        heads[c[:2]] = heads.get(c[:2], 0) + 1
    return any(v >= 3 for v in heads.values())


def scan(text):
    lines = text.splitlines()
    findings = []

    # 1) word-list scan (line by line, hit by hit)
    for lineno, line in enumerate(lines, 1):
        for pattern, hint in AI_PATTERNS:
            for m in re.finditer(pattern, line, re.IGNORECASE):
                findings.append({
                    "pos": "L%d" % lineno,
                    "type": "ai_word",
                    "evidence": context(line, m.start(), m.end()),
                    "fix_hint": hint,
                })

    # 2) sentence splitting and statistics
    sentences = []
    for lineno, line in enumerate(lines, 1):
        for s in split_line_sentences(line):
            sentences.append((lineno, s))
    lens = [effective_len(s) for _, s in sentences]
    lens = [n for n in lens if n >= 2]
    n = len(lens)
    mean = sum(lens) / n if n else 0.0
    std = math.sqrt(sum((x - mean) ** 2 for x in lens) / n) if n else 0.0
    cv_evaluable = n >= 3 and mean > 0
    cv = (std / mean) if cv_evaluable else None

    # 3) structural-pattern checks (sentence by sentence)
    enum_total = 0
    for lineno, s in sentences:
        enum_total += len(ENUMERATOR_RE.findall(s))
        if detect_parallelism(s):
            findings.append({
                "pos": "L%d" % lineno,
                "type": "parallelism",
                "evidence": s[:40] + ("…" if len(s) > 40 else ""),
                "fix_hint": "3+ clauses opening with the same head in one sentence is a parallelism cliche; split the sentence or drop the repeated structure",
            })
        if (re.search(r"firstly.{0,50}secondly", s) or re.search(r"secondly.{0,50}lastly", s)
                or re.search(r"\bfirst\b.{0,50}\bsecond\b", s)):
            findings.append({
                "pos": "L%d" % lineno,
                "type": "enumerator_chain",
                "evidence": s[:40] + ("..." if len(s) > 40 else ""),
                "fix_hint": "a firstly/secondly/lastly chain is a template trace; use subheadings or expand directly by logical relation",
            })

    # 4) list density
    nonempty = [l for l in lines if l.strip()]
    list_lines = sum(1 for l in nonempty if LIST_LINE_RE.match(l))
    list_ratio = (list_lines / len(nonempty)) if nonempty else 0.0

    # 5) statistical findings
    if cv_evaluable and cv < CV_THRESHOLD:
        findings.append({
            "pos": "L1",
            "type": "uniform_sentence_length",
            "evidence": "std/mean=%.2f (n=%d, mean=%.1f)" % (cv, n, mean),
            "fix_hint": "over-uniform sentence length is the core machine-tone feature; follow two long sentences with one short (<=8 word) one",
        })
    if nonempty and list_ratio > LIST_RATIO_THRESHOLD:
        findings.append({
            "pos": "L1",
            "type": "list_density",
            "evidence": "%d/%d lines are list items (%.0f%%)" % (list_lines, len(nonempty), list_ratio * 100),
            "fix_hint": "an over-high list ratio is PPT-tone; rewrite non-parallel content into flowing paragraphs",
        })

    # 6) scoring
    type_count = {}
    for f in findings:
        type_count[f["type"]] = type_count.get(f["type"], 0) + 1
    score = 100
    score -= SCORE_PER_AI_WORD * type_count.get("ai_word", 0)
    if cv_evaluable and cv is not None and cv < CV_THRESHOLD:
        score -= SCORE_PENALTY_CV
    if nonempty and list_ratio > LIST_RATIO_THRESHOLD:
        score -= SCORE_PENALTY_LIST
    score -= SCORE_PENALTY_PARALLELISM * type_count.get("parallelism", 0)
    score -= SCORE_PENALTY_CHAIN * type_count.get("enumerator_chain", 0)
    score = max(0, score)
    if score >= 80:
        verdict = "human_like"
    elif score >= 60:
        verdict = "light_ai_traces"
    elif score >= 40:
        verdict = "obvious_ai_style"
    else:
        verdict = "heavy_ai_style"

    findings.sort(key=lambda f: int(f["pos"][1:]))
    return {
        "stats": {
            "sentences": n,
            "mean_sentence_len": round(mean, 1),
            "std_sentence_len": round(std, 1),
            "cv": round(cv, 3) if cv is not None else None,
            "cv_threshold": CV_THRESHOLD,
            "list_lines": list_lines,
            "total_lines": len(nonempty),
            "list_ratio": round(list_ratio, 3),
            "enumerator_count": enum_total,
            "ai_word_hits": type_count.get("ai_word", 0),
            "score": score,
            "verdict": verdict,
        },
        "findings": findings,
    }


def main(argv):
    if len(argv) >= 2 and argv[1] != "-":
        path = argv[1]
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print("error: cannot read %s: %s" % (path, exc), file=sys.stderr)
            return 1
    else:
        if len(argv) < 2 and sys.stdin.isatty():
            print("usage: python3 scripts/trace_scanner.py <file>  (or pipe text via stdin '-')",
                  file=sys.stderr)
            return 2
        text = sys.stdin.read()
    print(json.dumps(scan(text), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
