#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""effectiveness_ab.py — 技能效能对照台架（A/B 盲评）

问题：SKILL.md 改写后"更有暗知识"是写作者的判断，不是证据。
本台架给出**方向性证据**：同一任务，分别以旧版 / 新版 SKILL.md 作为
system prompt 让模型生成交付物，再用「二元 rubric 清单 + 成对盲评 +
顺序互换」比较两版产物，用产物质量差异回答"改写是否真的有效"。

方法依据（外部，采信纪律见 tools/effectiveness_tasks.json 头注释）：
- 成对比较（pairwise）是主观质量评测可靠度最高的形式；位置偏差用
  "每对跑两次、交换顺序、不一致记平局"消解（LLM-as-judge 通行实践）。
- 二元 rubric 清单（逐条"哪边更满足"）优于 1-5 绝对打分——数字看着
  精确实则不可靠；且清单锚定可观察条目，压制"整体感觉"式漂移。
- 诚实边界：单一评委、与生成方同模型家族（自偏好偏差）、样本量小
  （每技能 3 任务 × 1 样本 × 2 换序 = 6 次判定，属 smoke 级信号，
  非统计结论）。报告如实标注，不夸大为"证明"。

用法：
  python tools/effectiveness_ab.py --skill writing/article-outliner \
      --tasks tools/effectiveness_tasks.json --old-ref HEAD --samples 1
  python tools/effectiveness_ab.py --all --tasks tools/effectiveness_tasks.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenario_harness import (  # noqa: E402
    load_llm_candidates, llm_chat, gate_prompt_output,
)

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "tests" / "_effectiveness"
MODELS_JSON = os.environ.get(
    "SCENARIO_MODELS_JSON", str(Path.home() / ".workbuddy" / "models.json"))


def skill_path(skill_id: str) -> Path:
    p = REPO / "skills" / skill_id / "SKILL.md"
    if not p.is_file():
        # 允许传完整相对路径
        p2 = REPO / skill_id
        if p2.is_file():
            return p2
        raise FileNotFoundError(f"SKILL.md not found: {p}")
    return p


def read_old_doc(skill_id: str, old_ref: str) -> str:
    """旧版技能文档：git show <ref>:<path>；ref='file:<path>' 时读文件。"""
    if old_ref.startswith("file:"):
        return Path(old_ref[5:]).read_text(encoding="utf-8")
    rel = str(skill_path(skill_id).relative_to(REPO)).replace("\\", "/")
    out = subprocess.run(
        ["git", "show", f"{old_ref}:{rel}"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    if out.returncode != 0:
        raise RuntimeError(f"git show failed: {out.stderr.strip()[:200]}")
    return out.stdout


def build_system(doc: str) -> str:
    return (
        "你是正在执行一个技能的 AI agent。以下是你被加载的技能文档，"
        "请严格按它的指引完成用户任务。若文档中有决策表、红线、诚实声明，"
        "必须遵守。\n\n===== 技能文档开始 =====\n" + doc +
        "\n===== 技能文档结束 =====\n\n"
        "完成用户任务时直接输出交付物本身（不要解释你如何理解技能文档）。"
    )


def extract_json(text: str):
    """从评委输出中稳健提取 JSON 对象。"""
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        # 去掉尾逗号再试一次
        try:
            return json.loads(re.sub(r",\s*([}\]])", r"\1", m.group(0)))
        except json.JSONDecodeError:
            return None


JUDGE_SYSTEM = (
    "你是严格的内容评审员。你会看到同一任务的两位候选交付物（匿名 A/B）"
    "以及一份评审清单。对清单的**每一条**，独立判断哪一位更满足该条"
    "（A 更好 / B 更好 / 平手），然后给出总体胜者。\n"
    "纪律：\n"
    "1. 只按清单条目判断，不要引入清单外的偏好；\n"
    "2. 不因篇幅长而加分——除非清单条目明确要求更完整；\n"
    "3. 先写理由再给结论（reasoning 在前，结论在后）；\n"
    "4. 输出严格 JSON：{\"items\": [{\"id\": \"D1\", \"better\": \"A|B|tie\", "
    "\"why\": \"...\"}], \"winner\": \"A|B|tie\", \"reasoning\": \"...\"}\n"
    "5. 无法区分时如实判 tie，不要强行分胜负。"
)


def judge_once(cands, rubric, out_a, out_b):
    """单次盲评：rubric 为 [(id, criterion)]。返回 (winner, items_detail, meta)。"""
    items_txt = "\n".join(f"{i}. [{i}] {c}" for i, c in rubric)
    user = (
        f"评审清单（逐条判断，哪一位更满足）：\n{items_txt}\n\n"
        f"===== 候选 A =====\n{out_a[:6000]}\n\n"
        f"===== 候选 B =====\n{out_b[:6000]}\n\n"
        "请输出 JSON（items + winner + reasoning）。"
    )
    text, meta = llm_chat(cands, JUDGE_SYSTEM, user, max_tokens=1200, timeout=180)
    data = extract_json(text)
    if not data or "winner" not in data:
        # 评委偶发输出非 JSON（实测约 1/6 概率）→ 重试一次再放弃，
        # 避免把「评委格式事故」误记为新旧差异。
        text, meta = llm_chat(cands, JUDGE_SYSTEM, user, max_tokens=1200, timeout=180)
        data = extract_json(text)
    if not data or "winner" not in data:
        return None, [], meta
    return str(data.get("winner", "tie")).strip(), data.get("items", []), meta


def ab_for_task(cands, task, doc_old, doc_new, samples=1):
    """一个任务的全套对照。返回 dict（含每次 sample 的判定与最终裁决）。"""
    sys_old, sys_new = build_system(doc_old), build_system(doc_new)
    results = []
    for s in range(samples):
        # 1) 双方生成（同模型、同参数、同一任务）
        out_old, gen_old_meta = llm_chat(cands, sys_old, task["prompt"],
                                         max_tokens=1800, timeout=240)
        out_new, gen_new_meta = llm_chat(cands, sys_new, task["prompt"],
                                         max_tokens=1800, timeout=240)
        gate_old = gate_prompt_output(out_old, task.get("min_chars", 250))
        gate_new = gate_prompt_output(out_new, task.get("min_chars", 250))
        # 2) 盲评 ×2（顺序互换）→ 规整到 old/new
        w1, items1, _ = judge_once(cands, task["rubric"], out_old, out_new)   # A=old
        w2, items2, _ = judge_once(cands, task["rubric"], out_new, out_old)   # A=new
        norm = {"A_B": lambda w: {"A": "old", "B": "new"}.get(w, "tie"),
                "B_A": lambda w: {"A": "new", "B": "old"}.get(w, "tie")}
        n1 = norm["A_B"](w1) if w1 is not None else "invalid"
        n2 = norm["B_A"](w2) if w2 is not None else "invalid"
        if n1 == n2 and n1 in ("old", "new"):
            verdict = n1
        elif "invalid" in (n1, n2):
            verdict = "invalid"
        else:
            verdict = "tie"          # 换序不一致 → 诚实记平局
        results.append({
            "sample": s + 1, "verdict": verdict,
            "run1_winner_raw": w1, "run2_winner_raw": w2,
            "normalized": [n1, n2],
            "gate_old": gate_old, "gate_new": gate_new,
            "gen_seconds": [gen_old_meta.get("seconds"), gen_new_meta.get("seconds")],
            "chars": [len(out_old), len(out_new)],
            "items_run1": items1, "items_run2": items2,
            # 产物原文（截断保存）：负结果时用于复盘"为什么输"，没有它就没有诊断
            "out_old": out_old[:4000], "out_new": out_new[:4000],
        })
    tally = {"old": 0, "new": 0, "tie": 0, "invalid": 0}
    for r in results:
        tally[r["verdict"]] += 1
    if tally["new"] > tally["old"]:
        final = "new"
    elif tally["old"] > tally["new"]:
        final = "old"
    elif tally["new"] == 0 and tally["old"] == 0:
        # 没有任何有效判定：区分"全是无效"与"全是平局"，不要把 invalid 折叠成 tie
        final = "invalid" if tally["invalid"] else "tie"
    else:
        final = "tie"
    return {"task": task["id"], "final": final, "tally": tally, "runs": results}


def render_report(skill_id, data, old_ref):
    lines = [
        f"# 效能对照报告 — {skill_id}",
        f"",
        f"- 旧版来源：`{old_ref}` ｜ 新版来源：工作区 SKILL.md",
        f"- 判定法：二元 rubric 清单 + 成对盲评（顺序互换，不一致记平局）",
        f"- 诚实边界：单一评委模型、与生成方同家族（自偏好偏差）、样本量小 —— 方向性信号，非统计结论",
    ]
    # 长度混淆：评委指令已禁止按篇幅加分，但"新版更长"本身是已知混淆项，必须披露
    pairs = [r for t in data["tasks"] for r in t["runs"]]
    if pairs:
        longer_new = sum(1 for r in pairs if r["chars"][1] > r["chars"][0])
        med_old = sorted(r["chars"][0] for r in pairs)[len(pairs) // 2]
        med_new = sorted(r["chars"][1] for r in pairs)[len(pairs) // 2]
        lines.append(
            f"- 长度混淆：新版在 {longer_new}/{len(pairs)} 个样本上更长"
            f"（中位 {med_old} vs {med_new} 字符）——评委指令禁止按篇幅加分，但该混淆不可完全排除")
    lines += [
        f"",
        f"| 任务 | 最终裁决 | old/new/tie/invalid |",
        f"|---|---|---|",
    ]
    agg = {"old": 0, "new": 0, "tie": 0, "invalid": 0}
    for t in data["tasks"]:
        tally = t["tally"]
        for k in agg:
            agg[k] += tally[k]
        lines.append(f"| {t['task']} | **{t['final']}** | "
                     f"{tally['old']}/{tally['new']}/{tally['tie']}/{tally['invalid']} |")
    lines.append("")
    lines.append(f"**汇总：新版胜 {agg['new']} ｜ 旧版胜 {agg['old']} ｜ "
                 f"平局 {agg['tie']} ｜ 无效 {agg['invalid']}**")
    lines.append("")
    if agg["new"] > agg["old"] and agg["new"] > 0:
        lines.append("结论：新版在多数任务上占优（方向性证据支持改写有效）。")
    elif agg["old"] > agg["new"]:
        lines.append("结论：⚠️ 旧版占优——改写效果未兑现，需复盘（不许粉饰）。")
    else:
        lines.append("结论：无显著差异或数据不足，需扩大样本或检查 rubric。")
    lines.append("")
    lines.append("## 明细")
    for t in data["tasks"]:
        lines.append(f"### 任务 {t['task']}")
        for r in t["runs"]:
            g = (f"gate old={r['gate_old'] or 'OK'} / new={r['gate_new'] or 'OK'}")
            lines.append(f"- sample {r['sample']}: verdict=**{r['verdict']}** "
                         f"(换序 {r['normalized']}) ｜ {g} ｜ chars={r['chars']}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Skill effectiveness A/B harness")
    ap.add_argument("--skill", help="技能 id，如 writing/article-outliner")
    ap.add_argument("--all", action="store_true", help="跑配置里全部技能")
    ap.add_argument("--tasks", default=str(REPO / "tools" / "effectiveness_tasks.json"))
    ap.add_argument("--old-ref", default="HEAD", help="旧版来源 git ref（或 file:<path>）")
    ap.add_argument("--samples", type=int, default=1)
    args = ap.parse_args()

    cfg = json.loads(Path(args.tasks).read_text(encoding="utf-8"))
    targets = [k for k in cfg if not k.startswith("_")]
    if args.skill:
        targets = [args.skill]
    cands = load_llm_candidates(str(MODELS_JSON))
    if not cands:
        print("ERROR: no LLM candidates (check models.json)", file=sys.stderr)
        return 2
    print(f"LLM candidates: {[c['name'] for c in cands]}", file=sys.stderr)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {}
    for skill_id in targets:
        spec = cfg[skill_id]
        print(f"\n=== {skill_id} ===", file=sys.stderr)
        doc_old = read_old_doc(skill_id, args.old_ref)
        doc_new = skill_path(skill_id).read_text(encoding="utf-8")
        data = {"skill": skill_id, "old_ref": args.old_ref, "tasks": []}
        for task in spec["tasks"]:
            t0 = time.time()
            r = ab_for_task(cands, task, doc_old, doc_new, samples=args.samples)
            r["seconds"] = round(time.time() - t0, 1)
            data["tasks"].append(r)
            print(f"  task {task['id']}: {r['final']} "
                  f"({r['tally']}) {r['seconds']}s", file=sys.stderr)
        (OUT_DIR / f"{skill_id.replace('/', '_')}_report.md").write_text(
            render_report(skill_id, data, args.old_ref), encoding="utf-8")
        (OUT_DIR / f"{skill_id.replace('/', '_')}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        summary[skill_id] = {
            "tasks": {t["task"]: t["final"] for t in data["tasks"]},
            "tally": {k: sum(t["tally"][k] for t in data["tasks"])
                      for k in ("old", "new", "tie", "invalid")},
        }

    # 汇总页
    lines = ["# 效能对照汇总（批次 4）", "",
             "判定：二元 rubric + 成对盲评（顺序互换）。信号级别：smoke 级，非统计结论。", "",
             "| 技能 | new 胜 | old 胜 | tie | invalid | 任务裁决 |",
             "|---|---|---|---|---|---|"]
    for k, v in summary.items():
        t = v["tally"]
        lines.append(f"| {k} | {t['new']} | {t['old']} | {t['tie']} | "
                     f"{t['invalid']} | {v['tasks']} |")
    (OUT_DIR / "effectiveness_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\nsummary -> " + str(OUT_DIR / "effectiveness_summary.md"), file=sys.stderr)
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
