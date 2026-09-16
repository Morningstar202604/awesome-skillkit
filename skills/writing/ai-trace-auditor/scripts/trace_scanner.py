#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""trace_scanner.py — AI 痕迹统计扫描器（纯标准库，无第三方依赖）。

用法:
    python3 scripts/trace_scanner.py <file>    # 扫描文本文件（utf-8）
    cat draft.md | python3 scripts/trace_scanner.py -   # 从 stdin 读入

输出（stdout 打印单个 JSON 对象；正常退出码恒为 0）:
    {
      "stats": {
        "sentences": 12,              # 句子数（< 3 时 cv 不可判定）
        "mean_sentence_len": 38.2,    # 平均句长（有效字符，去标点空白）
        "std_sentence_len": 9.1,      # 句长总体标准差
        "cv": 0.24,                   # 句长方差比 = std/mean，< 0.5 判定"句长过均匀"
        "cv_threshold": 0.5,
        "list_lines": 8,              # 列表项行数（- * 数字. 等开头）
        "total_lines": 19,            # 非空行总数
        "list_ratio": 0.42,           # 列表密度 = list_lines/total_lines，> 0.4 报警
        "enumerator_count": 3,        # 首先/其次/最后/第一… 等枚举词总数
        "ai_word_hits": 6,            # AI 高频词命中总次数
        "score": 34,                  # 综合分 0-100，越高越像人写
        "verdict": "heavy_ai_style"
      },
      "findings": [
        {"pos": "L3", "type": "ai_word",
         "evidence": "……值得注意的是，……",
         "fix_hint": "删除或改为直接陈述"}
      ]
    }

findings[].type 取值:
    ai_word                 AI 高频词命中（词表内置，中英双语）
    uniform_sentence_length 句长方差比 cv < 0.5（经验阈值，可调）
    parallelism             同句内 >= 3 个分句以相同二字开头（排比滥用启发式）
    enumerator_chain        首先…其次 / 其次…最后 / 第一…第二 连招
    list_density            列表行占比 > 0.4

评分规则（经验值，可调）:
    score 初始 100；每个 ai_word 命中 -6；cv < 0.5 再 -20；
    list_ratio > 0.4 再 -15；每处排比 -10；每处 enumerator_chain -8；下限 0。
    verdict 分段: >= 80 human_like | >= 60 light_ai_traces |
                 >= 40 obvious_ai_style | < 40 heavy_ai_style

启发式边界（诚实声明）: 本工具基于词表与统计特征，不使用语言模型，
不能替代官方 AI 检测器；命中不等于抄袭，未命中不等于人写。
"""

import json
import math
import re
import sys

CV_THRESHOLD = 0.5        # 句长方差比报警线（经验值，可调）
LIST_RATIO_THRESHOLD = 0.4  # 列表密度报警线（经验值，可调）
SCORE_PER_AI_WORD = 6
SCORE_PENALTY_CV = 20
SCORE_PENALTY_LIST = 15
SCORE_PENALTY_PARALLELISM = 10
SCORE_PENALTY_CHAIN = 8

# AI 高频词表（内置，可按需增删）。每项: (正则, 修改建议)。英文用 \b 词边界、忽略大小写。
AI_PATTERNS = [
    # --- 中文 ---
    (r"在当今[^，。！？]{0,12}(?:时代|背景|浪潮|语境)", "删掉空泛开场，直接从具体事实或场景切入"),
    (r"值得注意的是", "删除或改为直接陈述；真正重要的内容自己会立起来"),
    (r"综上所述", "总结改成一个具体结论，不用公文套话"),
    (r"总而言之", "同上；或直接删除，让最后一段自己收尾"),
    (r"不仅[^。！？]{1,40}而且", "拆成两句，或只保留信息量更大的一半"),
    (r"深入(?:探讨|剖析|解析)", "换成具体动作：分析了什么、得出什么"),
    (r"赋能", "写出到底帮谁做了什么，删掉抽象动词"),
    (r"抓手", "说明具体载体或动作，不要用黑话命名"),
    (r"闭环", "描述流程本身，或直接删掉"),
    (r"底层逻辑", "直接讲机制，不要给机制起名"),
    (r"助力", "换成具体因果：谁用它完成了什么"),
    (r"一站式", "列出到底覆盖了哪些环节"),
    (r"众所周知|毋庸置疑|毫无疑问", "删除；断言的强度靠证据不靠口号"),
    (r"至关重要", "说明为什么重要，或降低语气"),
    (r"全方位", "列举具体维度"),
    # --- 英文 ---
    (r"\bdelv(?:e|es|ed|ing)(?:\s+into)?\b", "replace with a concrete verb: examined, read, tested"),
    (r"\btapestry\b", "drop the metaphor; name the elements directly"),
    (r"\bcrucial\b", "state why it matters instead of rating it"),
    (r"\b(?:moreover|furthermore)\b", "cut it; let sentence order carry the logic"),
    (r"\bit'?s\s+important\s+to\s+note\b", "delete the hedge and say the thing"),
    (r"\bin\s+today'?s\s+(?:fast-?paced\s+)?world\b", "open with a concrete fact instead"),
    (r"\b(?:ever|rapidly)-evolving\b", "name the actual change and its rate"),
    (r"\bin\s+the\s+realm\s+of\b", "use 'in' or name the field directly"),
    (r"\b(?:unlock|elevate|embark|harness)\b", "replace with the literal action performed"),
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
ENUMERATOR_RE = re.compile(r"首先|其次|再次|再者|最后|第一[，、,]|第二[，、,]|第三[，、,]|一方面|另一方面")


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

    # 1) 词表扫描（逐行、逐命中）
    for lineno, line in enumerate(lines, 1):
        for pattern, hint in AI_PATTERNS:
            for m in re.finditer(pattern, line, re.IGNORECASE):
                findings.append({
                    "pos": "L%d" % lineno,
                    "type": "ai_word",
                    "evidence": context(line, m.start(), m.end()),
                    "fix_hint": hint,
                })

    # 2) 句子切分与统计
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

    # 3) 结构套路检查（逐句）
    enum_total = 0
    for lineno, s in sentences:
        enum_total += len(ENUMERATOR_RE.findall(s))
        if detect_parallelism(s):
            findings.append({
                "pos": "L%d" % lineno,
                "type": "parallelism",
                "evidence": s[:40] + ("…" if len(s) > 40 else ""),
                "fix_hint": "同句内 3 个以上分句同头开头是排比套路；拆句或删掉重复结构",
            })
        if (re.search(r"首先.{0,50}其次", s) or re.search(r"其次.{0,50}最后", s)
                or re.search(r"第一.{0,50}第二", s)):
            findings.append({
                "pos": "L%d" % lineno,
                "type": "enumerator_chain",
                "evidence": s[:40] + ("…" if len(s) > 40 else ""),
                "fix_hint": "首先/其次/最后 连招是模板痕迹；按逻辑关系改用小标题或直接展开",
            })

    # 4) 列表密度
    nonempty = [l for l in lines if l.strip()]
    list_lines = sum(1 for l in nonempty if LIST_LINE_RE.match(l))
    list_ratio = (list_lines / len(nonempty)) if nonempty else 0.0

    # 5) 统计型 findings
    if cv_evaluable and cv < CV_THRESHOLD:
        findings.append({
            "pos": "L1",
            "type": "uniform_sentence_length",
            "evidence": "std/mean=%.2f (n=%d, mean=%.1f)" % (cv, n, mean),
            "fix_hint": "句长过均匀是机器腔核心特征；连续两个长句后接一个 <=8 字短句",
        })
    if nonempty and list_ratio > LIST_RATIO_THRESHOLD:
        findings.append({
            "pos": "L1",
            "type": "list_density",
            "evidence": "%d/%d 行是列表项 (%.0f%%)" % (list_lines, len(nonempty), list_ratio * 100),
            "fix_hint": "列表占比过高是 PPT 腔；把非并列内容改写成连贯段落",
        })

    # 6) 评分
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
