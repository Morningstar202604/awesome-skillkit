#!/usr/bin/env python3
"""
Audit Skills — 全仓库技能批量审计

在 skill-tester 技能内部，把「校验 + 打分 + 安全检查」三个脚本串起来，
对一个目录下的全部技能跑一遍，输出汇总报告。

与 tools/validate_skills.py（仓库级门禁）的分工：
  - tools/validate_skills.py  —— awesome-skillkit 仓库自己的合规门禁，
                                 规则写死在本仓库的 SKILL-STANDARD-v2 上；
  - 本脚本                     —— 通用审计器，可指向任意技能目录，
                                 且额外跑安全评分，适合评审别人的技能仓库。

用法:
    python3 audit_skills.py /path/to/skills
    python3 audit_skills.py /path/to/skills --json
    python3 audit_skills.py /path/to/skills --min-score 75 --fail-under
    python3 audit_skills.py /path/to/skills --no-security

退出码: 0 全部通过 / 1 存在未达阈值项（仅 --fail-under 时）/ 2 参数错误
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "skill_validator.py"
SCORER = SCRIPT_DIR / "quality_scorer.py"
SECURITY = SCRIPT_DIR / "security_scorer.py"

# 每个子进程的超时（秒）。技能目录可能很大，但单技能不应卡死整个审计。
CALL_TIMEOUT = 60


def find_skills(root: Path):
    """找出 root 下所有技能目录（含 SKILL.md 的目录），按路径排序。"""
    if (root / "SKILL.md").is_file():
        return [root]
    return sorted({p.parent for p in root.rglob("SKILL.md")})


def run_json(script: Path, target: Path, extra=None):
    """调用一个子脚本并解析其 JSON 输出。

    返回 (data, error_message)。子脚本非 0 退出不算失败——validator 用
    退出码表示"不合规"，但 JSON 仍然有效，所以要读 stdout 而不是看退出码。
    """
    if not script.is_file():
        return None, f"缺脚本 {script.name}"
    cmd = [sys.executable, str(script), str(target), "--json"]
    if extra:
        cmd.extend(extra)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CALL_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None, f"{script.name} 超时 (>{CALL_TIMEOUT}s)"

    out = proc.stdout.strip()
    if not out:
        err = (proc.stderr or "").strip().splitlines()
        return None, f"{script.name} 无输出" + (f": {err[-1]}" if err else "")
    try:
        return json.loads(out), None
    except json.JSONDecodeError:
        return None, f"{script.name} 输出非 JSON（前 80 字符: {out[:80]}）"


def pick(data, *keys):
    """从子脚本输出里按优先级取第一个存在的键。"""
    if not isinstance(data, dict):
        return None
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return None


def audit_one(skill_dir: Path, with_security: bool):
    """审计单个技能，返回结果 dict。"""
    rec = {
        "name": skill_dir.name,
        "path": str(skill_dir),
        "quality_score": None,
        "letter_grade": None,
        "tier": None,
        "compliance_level": None,
        "security_score": None,
        "security_issues": [],
        "errors": [],
        "warnings": [],
    }

    vdata, verr = run_json(VALIDATOR, skill_dir)
    if verr:
        rec["errors"].append(verr)
    else:
        rec["compliance_level"] = pick(vdata, "compliance_level", "level", "status")
        # 子检验结果里可能含 error/warning 列表
        checks = pick(vdata, "checks")
        if isinstance(checks, dict):
            for cname, cval in checks.items():
                if isinstance(cval, dict):
                    if cval.get("status") in ("fail", "error", "FAIL"):
                        rec["errors"].append(f"{cname}: {cval.get('message', 'fail')}")
                    elif cval.get("status") in ("warn", "warning", "WARN"):
                        rec["warnings"].append(f"{cname}: {cval.get('message', 'warn')}")
        for key, bucket in (("errors", "errors"), ("warnings", "warnings")):
            v = pick(vdata, key)
            if isinstance(v, list):
                rec[bucket].extend(str(x) for x in v)

    sdata, serr = run_json(SCORER, skill_dir)
    if serr:
        rec["errors"].append(serr)
    else:
        rec["quality_score"] = pick(sdata, "overall_score", "score", "total_score")
        rec["letter_grade"] = pick(sdata, "letter_grade", "grade")
        rec["tier"] = pick(sdata, "tier_recommendation", "tier")

    if with_security:
        secdata, secerr = run_json(SECURITY, skill_dir)
        if secerr:
            rec["warnings"].append(secerr)
        else:
            rec["security_score"] = pick(secdata, "overall_score", "score")
            issues = pick(secdata, "issues", "findings")
            if isinstance(issues, list):
                rec["security_issues"] = [
                    (i.get("message") or i.get("description") or str(i))
                    if isinstance(i, dict)
                    else str(i)
                    for i in issues
                ]

    return rec


def fmt_score(v):
    if v is None:
        return "  n/a"
    return f"{v:>5.1f}" if isinstance(v, (int, float)) else f"{v:>5}"


def print_table(records, min_score):
    print("=" * 84)
    print(f"{'技能':<34}{'质量':>7}{'等级':>6}{'层级':>12}{'安全':>7}  状态")
    print("-" * 84)
    for r in sorted(records, key=lambda x: (x["quality_score"] is None, x["quality_score"] or 0)):
        q = r["quality_score"]
        below = min_score is not None and (q is None or q < min_score)
        if r["errors"]:
            status = "FAIL"
        elif below:
            status = f"BELOW<{min_score}"
        elif r["warnings"]:
            status = "warn"
        else:
            status = "ok"
        grade = r["letter_grade"] or "-"
        tier = (r["tier"] or "-")[:11]
        print(
            f"{r['name'][:33]:<34}{fmt_score(q)}{str(grade):>6}"
            f"{tier:>12}{fmt_score(r['security_score']):>7}  {status}"
        )
    print("-" * 84)

    total = len(records)
    failing = [r for r in records if r["errors"]]
    below = [
        r
        for r in records
        if min_score is not None
        and (r["quality_score"] is None or r["quality_score"] < min_score)
    ]
    scored = [r["quality_score"] for r in records if r["quality_score"] is not None]
    avg = sum(scored) / len(scored) if scored else 0
    print(f"技能总数: {total}   均分: {avg:.1f}   校验失败: {len(failing)}", end="")
    if min_score is not None:
        print(f"   低于 {min_score} 分: {len(below)}")
    else:
        print()

    for r in records:
        if r["errors"] or r["warnings"]:
            print(f"\n[{r['name']}]")
            for e in r["errors"]:
                print(f"  ERROR  {e}")
            for w in r["warnings"][:5]:
                print(f"  WARN   {w}")
            if len(r["warnings"]) > 5:
                print(f"  WARN   ... 另有 {len(r['warnings']) - 5} 条")
    print("=" * 84)
    return failing, below


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="对目录下全部技能批量审计（校验 + 打分 + 安全）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("root", help="技能根目录，或单个技能目录")
    ap.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    ap.add_argument("--min-score", type=float, default=None, help="质量分下限，用于标记未达标")
    ap.add_argument(
        "--fail-under",
        action="store_true",
        help="有项目低于 --min-score 或校验失败时以退出码 1 结束（供 CI 使用）",
    )
    ap.add_argument("--no-security", action="store_true", help="跳过安全评分（更快）")
    ap.add_argument("--limit", type=int, default=None, help="只审计前 N 个技能（调试用）")
    args = ap.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"错误：目录不存在: {root}", file=sys.stderr)
        return 2

    skills = find_skills(root)
    if args.limit:
        skills = skills[: args.limit]
    if not skills:
        print(f"错误：在 {root} 下未找到任何含 SKILL.md 的技能目录", file=sys.stderr)
        return 2

    records = [audit_one(d, not args.no_security) for d in skills]

    if args.json:
        scored = [r["quality_score"] for r in records if r["quality_score"] is not None]
        payload = {
            "root": str(root),
            "skill_count": len(records),
            "average_quality_score": round(sum(scored) / len(scored), 2) if scored else None,
            "validation_failures": sum(1 for r in records if r["errors"]),
            "min_score": args.min_score,
            "skills": records,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        failing = [r for r in records if r["errors"]]
        below = [
            r
            for r in records
            if args.min_score is not None
            and (r["quality_score"] is None or r["quality_score"] < args.min_score)
        ]
    else:
        failing, below = print_table(records, args.min_score)

    if args.fail_under and (failing or below):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
