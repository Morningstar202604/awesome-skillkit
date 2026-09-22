#!/usr/bin/env python3
"""campaign_inventory.py — "全部技能变高质量"战役的盘点器。

把两类客观证据交叉成带优先级的改造总账：
  A. 配方 v2 六要素评分（适用决策表 / 暗知识 / 红线 / 诚实声明 / 内置验证 / CLI 附录）——0~6 分
  B. 命令级场景门（real_scenario_test.py 全库扫描）的逐技能最差判定

优先级：
  P0 = 命令级扫描存在 fail/error（可运行性缺陷，用户可复现）
  P1 = no-example（SKILL.md 无可解析用法示例 = 文档债）
  P2 = 六要素 ≤2 分（配方缺失）
  P3 = 3~5 分（补齐即可）
  OK = 6 分

输出 tests/_effectiveness/campaign_inventory.{json,md}；重复批次可直接复跑跟踪进度。
Stdlib only.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
OUT_DIR = REPO / "tests" / "_effectiveness"

ELEMENTS = [
    ("decision-table", "适用决策表"),
    ("dark-knowledge", "暗知识"),
    ("red-lines", "红线"),
    ("honesty", "诚实声明"),
    ("built-in-verify", "内置验证"),
    ("cli-appendix", "附录"),
]

# 批次 4 已完成（本盘点基准 2026-09-22，v0.21.0）
DONE_SKILLS = {
    "writing/article-outliner", "video/video-script-writer",
    "video/storyboard-designer", "design/image-prompt-engineer",
    "education/own-voice-rewrite",
}


def score_skill(md: str) -> dict:
    found = {key: (pat in md) for key, pat in ELEMENTS}
    score = sum(found.values())
    return {"score": score, "elements": found}


def load_sweep() -> dict:
    """命令级扫描结果（优先全库扫描，其次跟踪的逐域记录）。聚合到技能级最差判定。"""
    for cand in (OUT_DIR / "real_scenario_fullsweep.json",
                 REPO / "tests/_full_test_artifacts/real_scenario_report.json"):
        if cand.exists():
            try:
                d = json.loads(cand.read_text(encoding="utf-8"))
            except Exception:
                continue
            per_skill = {}
            for r in d.get("results", []):
                sid, v = r["skill"], r.get("verdict", "?")
                cur = per_skill.get(sid)
                rank = {"error": 3, "fail": 2, "no-example": 0, "pass": -1,
                        "spec-error": 2}.get(v, 1)
                if cur is None or rank > cur[1]:
                    per_skill[sid] = (v, rank)
            return {"source": str(cand.relative_to(REPO)),
                    "generated": d.get("generated"),
                    "per_skill": {k: v[0] for k, v in per_skill.items()}}
    return {"source": None, "generated": None, "per_skill": {}}


def main() -> int:
    inventory = []
    for md_path in sorted(SKILLS.rglob("SKILL.md")):
        sid = md_path.parent.relative_to(SKILLS).as_posix()
        md = md_path.read_text(encoding="utf-8", errors="ignore")
        s = score_skill(md)
        inventory.append({"skill": sid, "score": s["score"], "elements": s["elements"]})

    sweep = load_sweep()
    for item in inventory:
        item["sweep"] = sweep["per_skill"].get(item["skill"], "n/a")
        item["done"] = item["skill"] in DONE_SKILLS

        if item["sweep"] in ("fail", "error", "spec-error"):
            item["priority"] = "P0"
        elif item["sweep"] == "no-example":
            item["priority"] = "P1"
        elif item["done"]:
            item["priority"] = "OK"
        elif item["score"] <= 2:
            item["priority"] = "P2"
        elif item["score"] <= 5:
            item["priority"] = "P3"
        else:
            item["priority"] = "OK"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"generated": datetime.now(timezone.utc).isoformat(),
               "sweep_source": sweep["source"], "skills": inventory}
    (OUT_DIR / "campaign_inventory.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- markdown 汇总 ----
    from collections import Counter
    pri = Counter(i["priority"] for i in inventory)
    scores = Counter(i["score"] for i in inventory)
    lines = [
        "# 全技能改造战役总账（六要素 × 命令级扫描）", "",
        f"> 生成：{payload['generated']} ｜ 扫描来源：`{sweep['source']}`（{sweep['generated']}）",
        f"> 优先级分布：{dict(sorted(pri.items()))}",
        f"> 六要素分布：{dict(sorted(scores.items()))}", "",
        "| 优先级 | 含义 | 数量 |",
        "|---|---|---|",
        f"| P0 | 命令级扫描 fail/error（可运行性缺陷） | {pri.get('P0', 0)} |",
        f"| P1 | SKILL.md 无可解析用法示例（文档债） | {pri.get('P1', 0)} |",
        f"| P2 | 六要素 ≤2 分（配方缺失） | {pri.get('P2', 0)} |",
        f"| P3 | 六要素 3~5 分（补齐即可） | {pri.get('P3', 0)} |",
        f"| OK | 已达标（6 分或本战役已完成） | {pri.get('OK', 0)} |", "",
    ]
    for p, title in (("P0", "P0 —— 命令级 FAIL（先修可运行性）"),
                     ("P1", "P1 —— 无用法示例（补文档债）"),
                     ("P2", "P2 —— 配方缺失（≤2 分）"),
                     ("P3", "P3 —— 3~5 分（补齐要素）")):
        rows = [i for i in inventory if i["priority"] == p]
        rows.sort(key=lambda x: (x["score"], x["skill"]))
        lines += [f"## {title}（{len(rows)}）", "",
                  "| 技能 | 六要素分 | 扫描判定 |", "|---|---|---|"]
        for i in rows:
            lines.append(f"| {i['skill']} | {i['score']} | {i['sweep']} |")
        lines.append("")
    done = [i for i in inventory if i["done"]]
    lines += [f"## 本战役已完成（{len(done)}）", ""]
    for i in sorted(done, key=lambda x: x["skill"]):
        lines.append(f"- {i['skill']}（六要素 {i['score']} 分，批次 4）")
    (OUT_DIR / "campaign_inventory.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"total={len(inventory)} priorities={dict(sorted(pri.items()))}")
    print(f"inventory -> {OUT_DIR / 'campaign_inventory.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
