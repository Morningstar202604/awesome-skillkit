#!/usr/bin/env python3
"""
job_scorer.py — 把一个 JD 文本 + 你的简历要点打分（0-5），并对逐条要求
标 A-F。纯文本、纯离线，不碰招聘网站登录态。

设计红线（仓库 SKILL-STANDARD-v2）：
- 默认 dry-run 打印评分与逐条匹配，不写文件
- --write 才落 JSON 报告（输出到新文件，源 JD/简历不动）
- 零网络、零拷贝、无凭证
"""
import argparse
import json
import os
import re
import sys
from collections import OrderedDict

DIMENSIONS = ["requirement_match", "level_fit", "comp_band", "domain_match", "stability"]
# 权重可被用户覆盖
DEFAULT_WEIGHTS = {"requirement_match": 0.35, "level_fit": 0.20,
                   "comp_band": 0.15, "domain_match": 0.20, "stability": 0.10}

LEVEL_KW = {
    "junior": ["junior", "j1", "0-2", "entry", "初级", "应届生"],
    "mid": ["mid", "intermediate", "3-5", "中级", "mid-level"],
    "senior": ["senior", "sr", "6+", "6-10", "高级", "资深"],
    "staff": ["staff", "principal", "staff+", "staff 级", "staff 及以上"],
}


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def split_requirements(jd_text: str) -> list[str]:
    """粗切 JD 的「要求」区：行内含 必须/要求/qualif/require/skill/experience 等关键词。"""
    out = []
    for raw in jd_text.splitlines():
        line = raw.strip().lstrip("-•* ").strip()
        low = line.lower()
        if not line:
            continue
        if re.search(r"(要求|必须|qualif|require|skill|experience|熟悉|掌握|具备|至少|优先)", low):
            out.append(line)
    # 去重保序
    seen = set(); uniq = []
    for x in out:
        k = x.lower()
        if k not in seen:
            seen.add(k); uniq.append(x)
    return uniq


def grade_requirement(req: str, resume_text: str) -> str:
    """A(完全命中) F(完全没提) 五级启发式：词面重合度。"""
    resume_low = resume_text.lower()
    # 抽需求里的实词（长度>=2 的连续字母/数字词 + 中文 2 字词）
    tokens = set(re.findall(r"[a-z0-9]{2,}", req.lower()))
    cn = set(re.findall(r"[\u4e00-\u9fff]{2,}", req))
    hit = 0
    for t in tokens:
        if t in resume_low:
            hit += 1
    for c in cn:
        if c in resume_text:
            hit += 1
    total = len(tokens) + len(cn)
    if total == 0:
        return "C"
    ratio = hit / total
    if ratio >= 0.85: return "A"
    if ratio >= 0.6: return "B"
    if ratio >= 0.35: return "C"
    if ratio >= 0.15: return "D"
    return "F"


def detect_level(jd_text: str) -> str | None:
    low = jd_text.lower()
    for lvl, kws in LEVEL_KW.items():
        for kw in kws:
            if kw in low:
                return lvl
    return None


def score(jd_text: str, resume_text: str) -> dict:
    reqs = split_requirements(jd_text)
    graded = OrderedDict()
    for r in reqs:
        graded[r] = grade_requirement(r, resume_text)
    grade_counts = {g: 0 for g in "ABCDF"}
    for g in graded.values():
        grade_counts[g] += 1

    # 维度分（0-1）
    dim = {}
    dim["requirement_match"] = round((grade_counts["A"] + 0.7 * grade_counts["B"] +
                                      0.4 * grade_counts["C"]) / max(1, len(reqs)), 3)
    dim["level_fit"] = 0.6 if detect_level(jd_text) else 0.4  # 无级别信号给中性 0.4
    dim["comp_band"] = 0.5  # 需人工补
    dim["domain_match"] = 0.5
    dim["stability"] = 0.5

    weights = dict(DEFAULT_WEIGHTS)
    overall = round(sum(weights[d] * dim[d] for d in DIMENSIONS), 3)
    # 0-5 分（映射：overall*5）
    score_5 = round(overall * 5, 2)

    return {
        "requirements": graded,
        "grade_counts": grade_counts,
        "level": detect_level(jd_text),
        "dimension_scores": dim,
        "weights": weights,
        "overall_0_1": overall,
        "score_5": score_5,
        "verdict": "STRONG" if score_5 >= 4 else ("OK" if score_5 >= 3 else "WEAK"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Score a JD against your resume (offline, dry-run by default)")
    ap.add_argument("--jd", required=True, help="path to JD text file")
    ap.add_argument("--resume", required=True, help="path to your resume text file")
    ap.add_argument("--weights", default="", help="optional JSON overriding dimension weights")
    ap.add_argument("-o", "--out", default="job_score.json", help="report path (only with --write)")
    ap.add_argument("--write", action="store_true", help="write JSON report; default dry-run")
    args = ap.parse_args()

    if not (os.path.isfile(args.jd) and os.path.isfile(args.resume)):
        print(f"[ERROR] jd/resume file(s) not found", file=sys.stderr)
        return 2

    jd_text = read_text(args.jd)
    resume_text = read_text(args.resume)
    result = score(jd_text, resume_text)

    if args.weights:
        try:
            result["weights"] = {**DEFAULT_WEIGHTS, **json.loads(read_text(args.weights))}
            # 重算 overall
            w = result["weights"]
            result["overall_0_1"] = round(sum(w[d] * result["dimension_scores"][d] for d in DIMENSIONS), 3)
            result["score_5"] = round(result["overall_0_1"] * 5, 2)
        except Exception as e:
            print(f"[WARN] bad --weights JSON ({e}); using defaults", file=sys.stderr)

    print(f"Level signal: {result['level'] or '(none detected)'}")
    print(f"Requirements extracted: {len(result['requirements'])}")
    for req, g in result["requirements"].items():
        print(f"  [{g}] {req[:80]}{'…' if len(req) > 80 else ''}")
    print(f"\nGrade counts: {result['grade_counts']}")
    print(f"Overall: {result['overall_0_1']:.3f}  =>  score/5: {result['score_5']}  ({result['verdict']})")

    if args.write:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[WRITE] report -> {args.out}")
    else:
        print(f"\n[DRY-RUN] no file written. Re-run with --write -o {args.out!r}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
