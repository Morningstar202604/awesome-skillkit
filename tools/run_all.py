#!/usr/bin/env python3
"""run_all.py — 跑全部 18 域任务 + 生成全量报告 report.md。"""
import os, sys, json, subprocess, glob

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
ART = os.path.join(REPO, "tests", "_full_test_artifacts")
PY = sys.executable

# 18 域任务映射（domain -> task module 文件名（去 .py））
TASKS = {
    "video": "video_task",
    "design": "design_task",
    "image": "image_task",
    "office": "office_task",
    "data-ml": "dataml_task",
    "dataviz": "dataviz_task",
    "programming": "programming_task",
    "paper": "paper_task",
    "writing": "writing_task",
    "education": "education_task",
    "tools": "tools_task",
    "meta": "meta_task",
    "memory": "memory_task",
    "knowledge": "knowledge_task",
    "marketing": "marketing_task",
    "audio": "audio_task",
    "chat": "chat_task",
    "music": "music_task",
    "ppt": "ppt_task",
    "integrations": "integrations_task",
}


def run_one(domain: str, task: str) -> dict:
    p = subprocess.run([PY, os.path.join(TOOLS, "full_skill_test.py"),
                       "--task", task, "--domain", domain],
                      capture_output=True, text=True, cwd=TOOLS, timeout=300)
    # 解析最后一段 JSON（找**最后**一个顶层 '{'，而非第一个）
    out = p.stdout.strip()
    try:
        # 从后往前找最后一个 '{'，取到结尾解析
        candidates = [i for i, c in enumerate(out) if c == "{"]
        payload = None
        for start in reversed(candidates):
            try:
                payload = json.loads(out[start:])
                break
            except Exception:
                continue
        if payload is None:
            raise ValueError("no JSON object found in stdout")
        return payload
    except Exception:
        return {"skill": task, "domain": domain, "verdict": "error",
                "problems": [out[-500:]], "better": [], "artifacts": []}


def main():
    os.makedirs(ART, exist_ok=True)
    results = []
    for domain, task in TASKS.items():
        print(f"\n### 跑 {domain} / {task} ...")
        r = run_one(domain, task)
        r["_task"] = task
        results.append(r)
        print(f"  verdict={r.get('verdict'):<6} problems={len(r.get('problems', []))} better={len(r.get('better', []))} artifacts={r.get('artifacts')}")

    # ---- 生成 report.md ----
    verdicts = {}
    for r in results:
        verdicts[r.get("verdict", "?")] = verdicts.get(r.get("verdict", "?"), 0) + 1
    lines = [
        "# 第一代全量测试报告",
        "",
        "> 口径：18 个领域各挑 1 个最具「复杂度+创新」代表性的 skill，跑**真实任务**，"
        "产出**真实可验证交付物**（视频/图片/可运行程序/成文文章/设计方案/可播放音频）。",
        "交付物**全部保留不删**（迭代记录），每个 skill 的 `process_log.md` 全量记录思维链/过程/问题/更优方案。",
        "",
        "## 总览",
        f"- 总任务数：{len(results)}（18 域 + 1 跨域）",
        f"- 判定分布：{verdicts}",
        "",
        "## 逐域结果",
        "",
        "| 域 | skill | 判定 | 交付物 | 问题数 | 更优方案 |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        arts = ", ".join(f"`{a}`" for a in r.get("artifacts", [])) or "—"
        lines.append(
            f"| {r['domain']} | `{r['skill']}` | {r.get('verdict','?')} | {arts} "
            f"| {len(r.get('problems',[]))} | {len(r.get('better',[]))} |"
        )
    # 问题与更优方案汇总
    lines += ["", "## 全量问题记录（缺失/遗漏）", ""]
    any_p = False
    for r in results:
        for p in r.get("problems", []):
            lines.append(f"- **{r['domain']}/{r['skill']}**: {p}")
            any_p = True
    if not any_p:
        lines.append("- （无）")
    lines += ["", "## 全量更优方案备忘", ""]
    any_b = False
    for r in results:
        for b in r.get("better", []):
            lines.append(f"- **{r['domain']}/{r['skill']}**: {b}")
            any_b = True
    if not any_b:
        lines.append("- （无）")
    lines += ["", "## 交付物清单（保留，供团队迭代参考）", ""]
    for r in results:
        for a in r.get("artifacts", []):
            lines.append(f"- `{r['domain']}/{r['skill']}/` → `{a}`")
    lines += ["", "## 全量过程记录位置", "",
              "每个域的完整思维链 + 执行命令 + stdout/stderr + 问题 + 更优方案在：",
              "`tests/_full_test_artifacts/<domain>/<skill>/process_log.md`"]
    out = os.path.join(ART, "report.md")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))
    print(f"\n=== report -> {out} ===")
    print(f"判定分布: {verdicts}")


if __name__ == "__main__":
    main()
