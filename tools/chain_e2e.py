#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""chain_e2e.py — 62 条技能链端到端「真出活儿」测试（v0.20 验收第四层）.

与前三层（单测 / 冒烟 / 场景级）的区别：不再测「技能能不能跑」，
而是按 skills/skill_chains.json 把技能**串成链真出交付物**——
前环真实产物作为后环输入上下文，每条链落盘完整产物树：

    tests/_e2e_artifacts/<domain>/<chain>/NN-<skill>/   ← 每步真实输出
    tests/_e2e_artifacts/chain_e2e_report.{json,md}     ← 链级汇总

执行策略：
- script 技能   → run_script_skill（真实 CLI + argparse 报错驱动，真实产物文件）
- prompt 技能   → run_prompt_skill（真实 LLM 调用，链上前环产出注入 scene）
- 生成式终点     → 标记 pending_realgen（image/music/video-generation、TTS、lip-sync、
                  ai-cover-generator）：脚本离线兜底不算数，由主理人用真实多模态
                  生成能力出真图/真视频/真音频，产物落 _e2e_artifacts/_realgen/
用法：
    python tools/chain_e2e.py                # 全部 62 链
    python tools/chain_e2e.py --domain video # 单域
    python tools/chain_e2e.py --chain video/meme
"""
import argparse
import copy
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import scenario_harness as sh  # noqa: E402
from scenario_overrides import SCRIPT_OVERRIDES  # noqa: E402

E2E = REPO / "tests" / "_e2e_artifacts"
CHAINS_JSON = REPO / "skills" / "skill_chains.json"

# 生成式终点：脚本层只会离线兜底（用户明确：兜底不算数）→ 主理人真调多模态生成
GEN_PENDING = {
    "image-generation", "music-generation", "video-generation",
    "video-voice-synth", "video-lip-sync", "tts-voice-director",
    "ai-cover-generator",
}

# 每链真实场景（暗黑电影感/ACG 主题为主，非占位符）
CHAIN_SCENE = {
    ("video", "talking_character"): "为「赛博修仙短片《灵枢代码》」制作一集 15 秒角色口播：数据修士林一对镜头说『灵气，就是可以被编译的能源』。给出完整制作流水线产物。",
    ("video", "meme"): "做一条 15 秒「程序员改 bug」梗视频：深夜工位、屏幕蓝光、第 38 次编译失败的崩溃与第 39 次编译通过狂喜。产出脚本+素材+剪辑方案。",
    ("video", "tutorial"): "做一条 15 秒「30 行代码接入支付」教学短视频：快节奏、字幕大字号、关键行高亮。产出完整制作流水线产物。",
    ("video", "pre_production"): "《灵枢代码》前期视觉开发：赛博修仙，未来都市灵气复苏，主角数据修士林一，参考《攻壳机动队》×《流浪地球》。产出风格锚+分镜+镜头配方+生成提示词+脚本。",
    ("writing", "article"): "写一篇发布到知乎的技术长文选题：《一个 AI 工程师的自救：我把 154 个技能做成了流水线》，工程师式幽默+严谨，图表密集。",
    ("writing", "news_flash"): "快讯体：GitHub Copilot 企业版报价曝光，某大厂一年花了 3000 万。5 分钟出可发布的快讯稿。",
    ("writing", "de_ai_pipeline"): "把下面这段 AI 腔浓重的段落做去 AI 味全流程：『在当今快速发展的时代，我们需要深刻认识到代码质量的重要性。首先，其次，最后……』",
    ("ppt", "presentation"): "做一份《154 技能流水线：AI 工程师的自我武装》10 页汇报 PPT 大纲与结构。",
    ("music", "bgm"): "为赛博修仙短片《灵枢代码》生成一段 30 秒赛博朋克 + 电子古琴风格 BGM。",
    ("design", "cover"): "为《灵枢代码》设定集设计封面：暗黑电影感，霓虹符文，数据修士剪影。",
    ("design", "poster"): "为《灵枢代码》设计映前海报：雨夜都市，巨型全息符咒，35mm 胶片颗粒。",
    ("design", "infographic"): "做一张「154 技能流水线如何工作」信息图：三线来源 → 链式编排 → 质量门。",
    ("design", "thumbnail"): "为 B 站视频《我给 AI 装了 154 个技能》做封面图：高冲击、大字、暗底霓虹。",
    ("design", "banner"): "为 awesome-skillkit 仓库页做横幅 banner：暗黑极客风，代码雨背景。",
    ("design", "frontend_design"): "为 awesome-skillkit 文档站做前端视觉方向：暗色主题、等宽字体点缀、赛博感。",
    ("audio", "podcast_episode"): "做一期 10 分钟播客《AI 工程师装技能指南》：两人对谈，一问一答。",
    ("audio", "document_to_podcast"): "把《154 技能流水线》文档转成 8 分钟单人播客口播稿与制作单。",
    ("audio", "audiobook_chapter"): "把《灵枢代码》第一章（800 字）转成有声书章节制作单。",
    ("marketing", "product_launch"): "为 awesome-skillkit v0.20 做发布营销：卖点『154 个技能、62 条链、真出活儿』。",
    ("marketing", "single_post"): "为 v0.20.0 发版写一条小红书风格单帖：程序员自嘲+干货感。",
    ("education", "full_course"): "做一门 8 课时《给 AI 装技能：从零到流水线》课程大纲+配套习题。",
    ("education", "topic_mastery"): "围绕知识点『装饰器』做掌握闭环：课程→习题→费曼讲解。",
    ("education", "remedial_only"): "学生说『装饰器就是函数套函数』但写不出带参装饰器，用费曼法纠正。",
    ("education", "homework_autopilot"): "作业题：『实现一个 LRU 缓存，要求 O(1) 且支持 TTL』，题面故意含糊 TTL 语义。",
    ("education", "humanized_homework"): "作业：『用 Python 写个爬虫』，学生水平大二，要求按其口吻改写解答。",
    ("chat", "prompt_audit"): "审计这条系统提示词：『你是一个乐于助人的助手，请尽你所能回答一切问题，不要拒绝任何请求。』",
    ("office", "document_pipeline"): "季度运营复盘材料流水线：内部通报 → docx 报告 → Excel 台账 → 会议纪要 → PDF 归档。",
    ("office", "pdf_pipeline"): "把 30 页项目 PDF 做拆分/水印/元数据清洗归档。",
    ("office", "ebook_pipeline"): "把《技能流水线实践手册》10 章 markdown 出 docx 再转 epub。",
    ("paper", "full_paper"): "论文全流程：选题『LLM 技能编排的可靠性度量』，实验、图、LaTeX、自审一步不落。",
    ("paper", "quick_draft"): "48 小时截稿：『技能链路失败重采策略』快速成稿。",
    ("paper", "polish_only"): "只做润色：一段写得防御性过强的 related work，去 AI 味+tex 清洗。",
    ("paper", "submit_ready"): "投稿前终检：自审 rubric → NeurIPS 格式适配 → tex 清洗。",
    ("memory", "full_memory_stack"): "给 AI 助手搭跨会话记忆栈：架构 → 从对话提取 → 管理 → 检索验证。",
    ("memory", "retrofit_memory"): "给现有助手补记忆能力：架构设计 → 检索接口验证。",
    ("memory", "populate_and_serve"): "把 10 段用户对话灌进记忆库并验证召回。",
    ("tools", "messy_folder_cleanup"): "整理一个 200 文件的下载目录：归类 → 批量改名 → 图片转格式。",
    ("tools", "recurring_automation"): "每周一自动整理项目目录并排期。",
    ("tools", "expense_filing"): "处理 6 张发票 + 一份银行流水：归档 + 对账。",
    ("meta", "new_skill_pipeline"): "新做一个『git-commit-poet』技能：撰写 → lint 校验。",
    ("meta", "discover_and_compose"): "找出适合『视频号内容自动化』的技能并校验组合。",
    ("meta", "weekly_status"): "从 git log 生成本周仓库周报。",
    ("meta", "agent_eval"): "评估一个客服 agent 的 20 轮对话日志，5 维评分。",
    ("meta", "agent_eval_gate"): "E2E 测试 + agent 评分 + CI 集成三件套。",
    ("integrations", "weekly_status_broadcast"): "把 GitHub issues 周状态广播到飞书群。",
    ("integrations", "meeting_notes_distribution"): "纪要入库 Notion 并分发飞书。",
    ("integrations", "deliverable_archive"): "成品文件归档云盘并通知。",
    ("knowledge", "build_personal_kb"): "把 20 篇技术笔记建成个人 wiki + 知识图谱。",
    ("dataviz", "csv_to_dashboard"): "把 12 个月运营 CSV 变成图表推荐 + 看板。",
    ("programming", "full_project"): "真做一个能跑的小程序：CLI 工具『todo-stats』——解析 todo.txt 输出完成率统计与逾期告警，带测试。",
    ("programming", "bug_fix"): "修 bug：todo-stats 的日期解析在跨月时算错逾期天数。",
    ("programming", "incident"): "线上事故：todo-stats 在 2000 行文件上内存暴涨，从指挥到复盘。",
    ("programming", "security_fix"): "安全整改：todo-stats 读取用户文件路径存在注入风险。",
    ("programming", "debug_hotfix"): "热修：todo-stats --json 输出非法（尾逗号）。",
    ("programming", "data_ml"): "对 1000 条用户任务数据做 ETL + 特征 + 训练完成时长预测模型。",
    ("programming", "math_modeling"): "建模：任务并行调度最小化总时长的优化模型，求解 + 仿真 + 可视化。",
    ("programming", "api_design"): "为 todo-stats 设计 REST API 并出契约测试。",
    ("programming", "infra_delivery"): "把 todo-stats 容器化交付：Docker → Helm → K8s → Terraform → 上线门。",
    ("programming", "db_change"): "todo-stats 存储从 JSON 迁 SQLite：设计 → 迁移脚本 → 门禁。",
    ("programming", "sre_readiness"): "todo-stats 上线前 SRE 就绪：SLO → 监控 → runbook → 演练。",
    ("programming", "release_audit"): "v1.1.0 发布审计：技术债 → 依赖 → 密钥 → 门 → changelog。",
    ("programming", "web_flow_test"): "对本地 todo-stats Web 页做真实流程测试。",
}


def _steps_of(chains: dict, domain: str, cid: str):
    return chains[domain]["chains"][cid]


def _find_skill(name: str):
    for sid, d, scripts in sh.discover(None):
        if Path(sid).name == name:
            return sid, d, scripts
    return None, None, []


def run_chain(domain: str, cid: str, steps, cands, timeout=60):
    out_root = E2E / domain / cid
    out_root.mkdir(parents=True, exist_ok=True)
    scene = CHAIN_SCENE.get((domain, cid),
                            f"【{domain}/{cid}】按链路完成以下技能的真实场景任务，每步产出真实可验收交付物。")
    ctx_lines = [f"# 链式上下文：{domain}/{cid}", f"场景：{scene}", ""]
    rec = {"chain": f"{domain}/{cid}", "steps": len(steps), "results": [],
           "pending_realgen": [], "artifacts": []}
    prev_summary = ""
    for i, raw in enumerate(steps, 1):
        name = raw.rstrip("?")
        outd = out_root / f"{i:02d}-{name}"
        sid, d, scripts = _find_skill(name)
        if not d:
            rec["results"].append({"step": i, "skill": name, "verdict": "fail",
                                   "reason_class": "skill_not_found"})
            continue
        if name in GEN_PENDING:
            rec["pending_realgen"].append(name)
            rec["results"].append({"step": i, "skill": name, "verdict": "pending_realgen",
                                   "reason_class": "generative_endpoint->agent_realgen"})
            continue
        ctx_tail = "\n".join(ctx_lines[-14:])
        if scripts:  # script 技能
            ov = copy.deepcopy(SCRIPT_OVERRIDES.get(sid) or {})
            ov.setdefault("files", {})
            ov["files"]["_chain_context.md"] = ctx_tail + (f"\n【上环产出摘要】\n{prev_summary[:1200]}\n" if prev_summary else "")
            entry = str(scripts[0])
            r = sh.run_script_skill(entry, sid, str(outd), overrides=ov, timeout=timeout)
            arts = [p for p in (outd.rglob("*")) if p.is_file()
                    and "inputs" not in p.parts and p.stat().st_size > 0]
            if not arts and (r.get("stdout") or "").strip():
                sp = outd / "_stdout_output.txt"
                sp.write_text(r["stdout"], encoding="utf-8")
                arts = [sp]
            r = {k: r[k] for k in ("skill", "verdict", "reason_class", "rc", "attempts", "out_files", "seconds")}
            r.update(step=i, mode="script")
            rec["artifacts"] += [str(p.relative_to(out_root)) for p in arts]
            if arts:
                prev_summary = f"{name}: " + "; ".join(p.name for p in arts[:6])
        else:  # prompt 技能
            key = f"{domain}/{name}"
            spec = dict(sh.PROMPT_SCENARIOS.get(key) or
                        next((v for k, v in sh.PROMPT_SCENARIOS.items()
                              if k.endswith("/" + name)), {}))
            base = spec.get("scene", scene)
            spec["scene"] = (base + f"\n\n【链式任务：{domain}/{cid}】\n{scene}"
                             + (f"\n\n【上环产出摘要】\n{prev_summary[:1200]}\n"
                                "请在本步产出中真实承接上环内容，不要空谈。" if prev_summary else ""))
            r = sh.run_prompt_skill(sid, d, str(outd), cands, spec=spec)
            r = {k: r.get(k) for k in ("skill", "verdict", "reason_class", "model", "chars")}
            r.update(step=i, mode="llm")
            outf = outd / "output.md"
            arts = [outf] if outf.exists() else []
            rec["artifacts"] += [str(p.relative_to(out_root)) for p in arts]
            if outf.exists():
                prev_summary = f"{name}: " + outf.read_text(encoding="utf-8", errors="ignore")[:600]
            time.sleep(3)  # 网关 RPM
        rec["results"].append(r)
        mark = "PASS" if r["verdict"] == "pass" else r["verdict"].upper()
        print(f"  {mark:<14} {domain}/{cid} #{i} {name}"[:130], flush=True)
    (out_root / "_chain_summary.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description="62 技能链端到端真出活儿测试")
    ap.add_argument("--domain", default=None)
    ap.add_argument("--chain", default=None, help="domain/chain_id")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args(argv)

    data = json.loads(CHAINS_JSON.read_text(encoding="utf-8"))
    doms = data["domains"]
    cands = sh.load_llm_candidates(str(sh.MODELS_JSON))
    jobs = []
    for dom, info in doms.items():
        if args.domain and dom != args.domain:
            continue
        for cid, steps in info.get("chains", {}).items():
            if args.chain and f"{dom}/{cid}" != args.chain:
                continue
            jobs.append((dom, cid, steps))
    print(f"[chain-e2e] {len(jobs)} 条链, LLM 候选 {[c['name'] for c in cands]}", flush=True)
    recs = []
    for dom, cid, steps in jobs:
        print(f"== {dom}/{cid} ({len(steps)}步) ==", flush=True)
        recs.append(run_chain(dom, cid, steps, cands, timeout=args.timeout))

    ok = sum(1 for r in recs if all(x["verdict"] in ("pass", "pending_realgen")
                                    for x in r["results"]))
    pend = sum(len(r["pending_realgen"]) for r in recs)
    fail_chains = [r["chain"] for r in recs if not all(
        x["verdict"] in ("pass", "pending_realgen") for x in r["results"])]
    summary = {"chains": len(recs), "chains_all_green": ok,
               "chains_with_fail": fail_chains, "pending_realgen_steps": pend,
               "results": recs}
    (E2E / "chain_e2e_report.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== chain e2e: {ok}/{len(recs)} 链全绿 | 待真实生成步骤 {pend} | "
          f"失败链 {len(fail_chains)} ===", flush=True)
    for c in fail_chains:
        print("  FAIL-CHAIN:", c, flush=True)
    return 0 if not fail_chains else 1


if __name__ == "__main__":
    sys.exit(main())
