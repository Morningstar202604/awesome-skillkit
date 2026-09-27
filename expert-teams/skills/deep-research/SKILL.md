---
name: deep-research
description: "Multi-round search with information synthesis and structured report generation. Query decomposition, quality scoring, trustworthiness assessment, deduplication. Use when the user asks to research a topic in depth and needs a comprehensive report with sources. 当用户要求 深度调研 / 多轮检索出报告 / 帮我研究这个主题 时使用。 Do NOT use for casual single-question lookups (use web-search)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: planning
  pattern: web-search
  tier: powerful
  verified-date: "2026-09-09"
---

# Deep Research — 深度调研Agent

多轮搜索 + 信息综合 + 结构化报告生成。
所有命令均在技能目录（本文件所在目录）下执行。

## 核心能力

| 能力 | 说明 |
|------|------|
| **多轮搜索** | 自动拆分查询，多轮迭代深化 |
| **信息去重** | URL 去重 + 域名配额过滤 |
| **来源验证** | 域名可信度打分（官方/博客/论坛分级） |
| **引用追踪** | 每个结论都有来源链接 |
| **报告生成** | Markdown + JSON 双格式输出 |

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| topic | 是 | 研究主题 |
| depth | 否 | 搜索深度：`basic` / `standard` / `deep`（默认 standard） |
| max_rounds | 否 | 最大搜索轮次（默认 3，对应 CLI `--rounds`） |
| min_sources | 否 | 最小信源数量（默认 5） |
| output_format | 否 | 输出格式：`markdown` / `json` / `both`（默认 markdown，对应 CLI `--format`） |
| focus_areas | 否 | 重点关注领域（默认全部） |

缺失时一次性问齐：「请提供：① 研究主题。其余我将使用默认值。」
说明：CLI 直接暴露 topic / `--rounds` / `--format` / `--no-cache`；depth、min_sources、focus_areas 由代理在综合与报告阶段执行。

## 前置自检

依次执行；致命项失败 → 修复后 STOP。

```bash
# 1. Python 可用（致命）
python3 --version                                            # 预期：Python 3.x

# 2. web-search 技能就位（致命；本技能复用其搜索客户端）
test -f ../web-search/scripts/search_client.py && echo OK    # 预期：OK；失败 → 确认同级目录存在 web-search 技能

# 3. 导入链验证（免网络）
PYTHONPATH=../web-search/scripts python3 -c "from search_client import search; print('search_client OK')"
# 预期输出：search_client OK；失败 → PYTHONPATH 未指向 ../web-search/scripts
```

- 网络可达（真实搜索必需）：任一公共 SearXNG 实例可达即可；实例失效由脚本自动降级 DuckDuckGo，全失败见失败处置表。
- `BRAVE_API_KEY` 仅底层引擎选 brave 时需要，凭据只走环境变量。

## 参数速查表

`python3 scripts/research_agent.py`（run）：

| 参数 | 取值 | 说明 |
|------|------|------|
| topic（位置参数） | 研究主题文本 | 必需 |
| --rounds / -r | 整数 | 最大搜索轮次，默认 3 |
| --format / -f | markdown / json / both | 报告格式，默认 markdown |
| --no-cache | 开关 | 禁用搜索缓存 |
| 环境变量 PYTHONPATH | `../web-search/scripts` | 必须设置，否则搜索客户端加载失败 |

## 工作流

### 步骤 1：查询分析与子问题拆解（脚本自动执行）

动作（read 内部逻辑）：QueryAnalyzer 按模式拆解子查询（"A和B" → 对比/vs；"最佳X" → 最佳实践/优缺点；"如何X" → 方法/教程/示例），追加年份维度与英文查询，去重后最多 10 个子查询，并选择策略：

| 主题类型 | 策略 | 引擎 | 深度 |
|---------|------|------|------|
| 技术文档 | 精准搜索 | SearXNG | standard |
| 新闻事件 | 多源验证 | SearXNG + DDG | deep |
| 比较分析 | 对比搜索 | SearXNG + DDG | deep |
| 入门教程 | 基础搜索 | SearXNG | standard |

预期：子查询列表非空（至少含原主题）。
若失败（topic 为空）→ CLI 报参数错误，回到输入清单。

### 步骤 2：多轮搜索与自动降级

动作（run）：

```bash
PYTHONPATH=../web-search/scripts python3 scripts/research_agent.py "FastAPI vs Flask 该选哪个" --rounds 3 --format both
```

预期：stdout 输出报告；第 1 轮用前 5 个子查询，后续轮基于已有结果标题生成追问（每轮最多 5 个）；结果 < 5 条且未达轮次上限时自动续搜。
若失败：stderr/结果出现 `web-search skill not found` → PYTHONPATH 未设置或路径错，回前置自检第 3 步。

### 步骤 3：去重与质量/可信度评估（脚本自动执行）

去重策略：

| 去重级别 | 方法 | 阈值 |
|---------|------|------|
| URL 去重 | 完全匹配 | 100% |
| 域名去重 | 同一域名最多取3条 | 3条 |
| 内容去重 | 相似度 > 0.8 合并 | 0.8 |
| 观点去重 | 相同结论合并引用 | - |

质量评分权重（脚本实现，满分 1.0）：域名可信度 40% + 内容完整性 20% + 标题相关性 20% + 引擎权威性 10% + 新鲜度 10%。域名可信度基准见 `scripts/research_agent.py` 的 `DOMAIN_TRUSTWORTHINESS`（官方文档 1.0、github.com 0.9、stackoverflow.com 0.85、技术博客 0.55-0.7、论坛 0.5）。
预期：结果列表按 `quality_score` 降序，`trust_scores` 按 URL 给分。
若失败（全部结果得分为默认值 0.5）→ 域名解析失败，检查 URL 合法性。

### 步骤 4：深度分析（可选，代理执行）

- 多视角：从结果中分拣 技术实现 / 性能对比 / 最佳实践 / 社区反馈 四类视角，写入报告"多方观点"表。
- 冲突检测：同一子话题下来源观点不一致时，如实并列写入"争议与分歧"，不强行统一。
- 信息缺口：对照主题应有关注点，未覆盖项写入"信息缺口"，必要时补一轮搜索（回到步骤 2）。

预期：报告相应小节内容与信源一一对应（每个结论可回溯 URL）。
若失败（某视角无结果）→ 该小节如实标注"未找到相关信息"。

### 步骤 5：生成并保存报告

动作（run，脚本自动落盘）：按 `--format` 输出；同时写 `research_<md5(topic)前8位>.json`（全量结果，含 `markdown_report`/`json_report` 字段）。
预期：stderr 提示 `结果已保存到: research_*.json`；报告含 摘要 / 核心发现 / 完整来源 三节。
若失败：写文件报权限错 → 换可写目录执行，或事后移动文件。

## 报告结构

### Markdown 报告模板

```markdown
# 研究报告：{topic}

**生成时间：** {timestamp}
**搜索轮次：** {rounds}
**信源数量：** {source_count}
**整体可信度：** {trust_score}/1.0

---

## 摘要

{2-3句话的核心发现}

---

## 核心发现

### 1. {发现标题}
{详细描述}

**来源：**
- [来源1](url) (可信度: ★★★★★)
- [来源2](url) (可信度: ★★★★)

---

## 多方观点

| 视角 | 主要观点 | 支持度 |
|------|---------|--------|
| 技术实现 | {观点} | ★★★★ |
| 社区反馈 | {观点} | ★★★★★ |

---

## 争议与分歧

{如有冲突信息，在此列出}

---

## 信息缺口

{如有未覆盖点，在此列出}

---

## 完整来源

| # | 标题 | URL | 可信度 |
|---|------|-----|--------|
| 1 | {title} | [link](url) | ★★★★★ |
```

### JSON 报告结构

```json
{
  "topic": "研究主题",
  "generated_at": "2026-09-09T10:00:00Z",
  "search_stats": {
    "rounds": 3,
    "queries": 12,
    "sources": 25,
    "deduped_sources": 18
  },
  "summary": "核心发现摘要",
  "findings": [
    {
      "title": "发现标题",
      "content": "详细描述",
      "evidence": [
        {"source": "url", "title": "标题", "trust": 0.95}
      ],
      "confidence": 0.88
    }
  ],
  "perspectives": {
    "technical": {},
    "performance": {},
    "community": {}
  },
  "conflicts": [],
  "gaps": [],
  "sources": []
}
```

## 与 code-intent-planner 的协作

研究主题涉及技术选型时，把结论转交规划：deep-research 输出的推荐（如"推荐 FastAPI"）拼进 code-intent-planner 的输入，即 `raw_input: "使用 FastAPI 实现用户认证模块"`、`context: "根据调研，FastAPI 更适合此场景"`，由后者产出 intent_type 与 sub_tasks。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------|------|------|
| `web-search skill not found` | search_client 导入失败 | 设置 `PYTHONPATH=../web-search/scripts` 后重跑 |
| 所有搜索引擎超时 | 网络问题 | 提示用户检查网络 |
| 结果不足 | 查询过于具体 | 扩展查询词，增加 `--rounds` |
| 可信度低 | 来源多为博客/论坛 | 标注低可信度，建议人工验证 |
| 冲突严重 | 观点分歧大 | 如实呈现，不强行统一 |
| `research_*.json` 未生成 | 当前目录不可写 | 换可写目录执行 |

## 交付标准

- 成功定义：报告生成且信源数 ≥ min_sources（默认 5）；不足时报告必须如实标注缺口，不得虚构来源或编造引用。
- 产物命名：`research_<md5(topic)前8位>.json`（脚本自动落盘）；如需交付 Markdown，另存 `research_<YYYYMMDD>_<slug>.md`。
- 保存位置：默认当前工作目录；建议统一移入 `reports/` 并随报告保留 URL 原文。
- 完整性验证：`python3 -m json.tool research_*.json` 可解析；报告三节齐全（摘要/核心发现/完整来源）；每条发现至少 1 个可点击来源链接；可信度以 ★ 标注。

## 参考

- references/search-strategies.md —— 步骤 1 策略选择拿不准时读（搜索策略详解）
- references/report-templates.md —— 生成报告前读（报告模板与措辞规范）
- references/examples.md —— 校准报告质量时读（真实调研案例）
