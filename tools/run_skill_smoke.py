#!/usr/bin/env python3
"""
run_skill_smoke.py — 真实技能冒烟测试全量驱动器（第二代测试，取代第一代代理重实现）。

关键纠正（自审结论）：
  第一代 full_skill_test.py 手搓了 20 个「合成技能名」的代理 task，与仓库里 117 个
  真实技能脱钩——19/20 pass 只能证明「代理实现能跑」，不能证明「技能包能跑」。
  本驱动器改为**直接运行真实技能自带的 test_smoke_*.py**（已有 28 个技能 ship 了冒烟测试），
  用 pytest 跑真实技能入口，是真正意义上的「技能质量门禁」。

发现规则：skills/**/scripts/test_smoke_*.py
判定：pytest 退出 0 且 failed==0 且 error==0 → pass；否则 fail（记录失败原因/缺失依赖）。

输出：
  tests/_full_test_artifacts/skill_smoke_report.md   全量报告
  （同时 stdout 打印 JSON 汇总）
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(REPO, "tests", "_full_test_artifacts")
PY = sys.executable
TIMEOUT = 180


def discover():
    out = []
    for root, _, files in os.walk(os.path.join(REPO, "skills")):
        for f in files:
            if f.startswith("test_smoke_") and f.endswith(".py"):
                fp = os.path.join(root, f)
                # skill id = skills/<domain>/<skill>
                rel = os.path.relpath(fp, REPO)
                parts = rel.split(os.sep)
                skill = os.path.join(parts[1], parts[2])  # domain/skill
                out.append((skill, fp))
    return sorted(out)


def parse_summary(out: str):
    passed = failed = error = skipped = 0
    m = re.search(r"(\d+)\s+passed", out)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", out)
    if m:
        failed = int(m.group(1))
    m = re.search(r"(\d+)\s+error", out)
    if m:
        error = int(m.group(1))
    m = re.search(r"(\d+)\s+skipped", out)
    if m:
        skipped = int(m.group(1))
    return passed, failed, error, skipped


def run_one(skill: str, fp: str):
    try:
        r = subprocess.run(
            [PY, "-m", "pytest", fp, "-q", "--tb=short", "-p", "no:cacheprovider"],
            capture_output=True, text=True, cwd=REPO, timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {"skill": skill, "file": fp, "rc": -1, "passed": 0,
                "failed": 0, "error": 1, "skipped": 0,
                "tail": "TIMEOUT after %ds" % TIMEOUT}
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    passed, failed, error, skipped = parse_summary(out)
    tail = out.strip()[-1500:] if (failed or error or r.returncode != 0) else out.strip()[-400:]
    # 缺失依赖/网络特征，便于分类失败原因
    reason = ""
    if "ModuleNotFoundError" in out:
        mm = re.search(r"ModuleNotFoundError: (.*)", out)
        reason = "缺失依赖: " + (mm.group(1).strip() if mm else "?")
    elif "ConnectionError" in out or "ENOTFOUND" in out or "TimeoutError" in out or "timed out" in out.lower():
        reason = "需网络/API（离线不可测）"
    elif r.returncode == 4:
        reason = "pytest 收集失败（语法/导入错误）"
    return {"skill": skill, "file": fp, "rc": r.returncode, "passed": passed,
            "failed": failed, "error": error, "skipped": skipped,
            "tail": tail, "reason": reason}


def main():
    os.makedirs(ART, exist_ok=True)
    items = discover()
    print(f"发现 {len(items)} 个真实技能冒烟测试", flush=True)
    results = []
    for skill, fp in items:
        res = run_one(skill, fp)
        verdict = "pass" if (res["rc"] == 0 and res["failed"] == 0 and res["error"] == 0) else "fail"
        res["verdict"] = verdict
        results.append(res)
        print(f"  {verdict:<4} {skill:<42} passed={res['passed']} failed={res['failed']} error={res['error']} {res.get('reason','')}", flush=True)

    total = len(results)
    n_pass = sum(1 for r in results if r["verdict"] == "pass")
    n_fail = total - n_pass
    fails_offline = sum(1 for r in results if r["verdict"] == "fail" and "网络" in r.get("reason", ""))
    fails_dep = sum(1 for r in results if r["verdict"] == "fail" and "依赖" in r.get("reason", ""))

    lines = [
        "# 第二代 · 真实技能冒烟测试全量报告",
        "",
        f"> 生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "> 口径：**直接运行真实技能自带的 `test_smoke_*.py`**（pytest），取代第一代手搓代理 task。",
        "> 这是真正意义上的「技能质量门禁」——测的是仓库里 117 个真实技能中 ship 了冒烟测试的 28 个。",
        "",
        "## 总览",
        f"- 真实技能目录总数（skills/ 下）：117",
        f"- 带可执行脚本的技能：56（其中 ship 冒烟测试的：{total}）",
        f"- 本轮跑冒烟测试的技能数：**{total}**",
        f"- 判定分布：**pass={n_pass} / fail={n_fail}**",
        f"- 失败分类：需网络/API（离线不可测）={fails_offline}，缺失依赖={fails_dep}，其它={n_fail-fails_offline-fails_dep}",
        "",
        "## 与第一代测试的关系（重要纠正）",
        "- 第一代 `full_skill_test.py`：20 个**合成技能名**的代理实现 → 19 pass/1 warn。**它不测真实技能。**",
        "- 第二代 `run_skill_smoke.py`：28 个**真实技能自带冒烟测试** → 见上。这才是技能包质量的真指标。",
        "- 结论：第一代的高 pass 率有「自嗨」成分；第二代才是硬指标。两者互补：第一代验证「交付物可生成」，第二代验证「技能脚本真能跑」。",
        "",
        "## 逐技能结果",
        "",
        "| 技能 | 判定 | passed | failed | error | skipped | 失败原因 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| `{r['skill']}` | {r['verdict']} | {r['passed']} | {r['failed']} "
            f"| {r['error']} | {r['skipped']} | {r.get('reason','') or '—'} |"
        )
    lines += ["", "## 失败明细（供修复排期）", ""]
    any_f = False
    for r in results:
        if r["verdict"] == "fail":
            any_f = True
            lines.append(f"### `{r['skill']}`  ({r.get('reason','') or '未知'})")
            lines.append(f"```\n{r['tail']}\n```")
    if not any_f:
        lines.append("- （无失败）")
    lines += ["", "## 改进清单（对应自审 P0/P1）",
               "- P0：未 ship 冒烟测试的 28 个脚本化技能，补 `test_smoke_*.py`（复用本驱动器）。",
               "- P0：失败中「缺失依赖」类 → 补进 CI 依赖清单（如 scikit-learn 已补）。",
               "- P1：失败中「需网络/API」类 → 为生成式/外部调用技能加离线兜底（model_route 模式），使其离线可冒烟。",
               "- P2：61 个纯 prompt 型技能（无脚本）→ 设计 LLM 沙箱冒烟（需网关恢复）。"]
    out_path = os.path.join(ART, "skill_smoke_report.md")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print(f"\n=== report -> {out_path} ===")
    print(f"pass={n_pass} fail={n_fail} (offline={fails_offline} dep={fails_dep})")
    # JSON 汇总供其他工具消费
    print(json.dumps({"total": total, "pass": n_pass, "fail": n_fail,
                      "offline_blocked": fails_offline, "dep_missing": fails_dep,
                      "results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
