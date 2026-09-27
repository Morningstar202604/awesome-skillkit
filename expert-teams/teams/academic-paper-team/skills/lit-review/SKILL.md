---
name: lit-review
description: "按 PRISMA 规范执行的系统文献综述工具。当用户需要\"写综述\"\"梳理这个方向研究现状\"\"定位我的研究在文献里的位置\"\"做一个可复现的文献检索\"时使用。适配 academic-literature-synthesizer 与 academic-topic-strategist，负责检索式设计、文献去重筛选、证据提取表、PRISMA 流程图与缺口矩阵输出。也用于 文献综述 / 相关工作梳理 / 找参考文献 / 调研某方向论文 / 综述某主题 / citation graph（共享引用图谱构建）。不用于选题打分（选题用 paper-topic-selector）。"
license: Apache-2.0
compatibility: Stdlib. --s2 hits api.semanticscholar.org, --arxiv hits export.arxiv.org (20s timeout, 429 backoff 3s). Any network/parse failure → honest mock fallback (data_source=mock + warning). SKILLKIT_MOCK=1 forces mock. LLM synthesis via skills/meta/_shared/model_route when SKILLKIT_MODEL_URL set; else keyword-cooccurrence (offline).
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Lit Review（多源真实检索 × PRISMA 系统文献综述）

围绕主题做**多源真实检索**，构建**基于共享引用的真实引用图**，并产出带研究空白标注的综述骨架（LLM 合成 + 关键词共现兜底）。

> 诚实声明：`data_source` 恒为 `s2` | `arxiv` | `mock`。任何回退都写进 `warning`；**`mock` 结果 MUST 标注「模拟数据」**，勿当真实检索呈现。`retrieval_date` 记录抓取日期（复现性要求「存 DOI 不存查询」，可据此重查）。

本 skill 供「文献综述师」（academic-literature-synthesizer）使用。文献综述不是把 20 篇摘要堆成"张三说…李四说…王五认为…"，而是一份**可复现的证据筛选工程**：别人拿你的检索式能复现你的文献集，拿你的提取表能复现你的结论。流程对齐 PRISMA 2020；脚本层负责把检索与引用图谱跑出来，方法论层负责把筛选、提取、综合做成可复现工程。

## 这是什么

PRISMA 四阶段：
1. **Identification（识别）**：在多个数据库用预先注册的检索式捞文献，记录各库命中数。
2. **Screening（筛选）**：去重后按标题/摘要初筛，再按全文复筛，全程记录每步剔除数量与原因。
3. **Eligibility（资格）**：对进入全文的文献按纳入/排除标准逐条判定。
4. **Included（纳入）**：最终纳入文献进入证据提取与综合。

配套 `references/prisma-checklist.md` 是 PRISMA 2020 27 项核对表与流程图骨架。脚本层产出 `papers[]`、`citation_graph`（共享引用边）与 `summary.gaps_identified` 综述骨架，二者配合：脚本管检索与图谱，PRISMA 流程管筛选与综合。

## 何时使用

- 用户说"帮我写一篇关于 X 的综述"。
- 选题阶段需要"定位我的研究在文献图谱里的位置"。
- 论文 Introduction / Related Work 需要有据可查的引用支撑。
- 需要写 systematic review / scoping review 投稿。
- 找参考文献 / 梳理相关工作 / 构建 citation graph。
- 不用于选题打分与缺口排序（那是 paper-topic-selector 的活；本 skill 反过来为其提供查证证据）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 主题 | 是 | `--topic "LLM agents"` |
| 数据源 | 否 | `--source s2\|arxiv\|mock`（默认 mock）；或快捷 `--s2` / `--arxiv` |
| 限定 venue | 否 | `--venues "ACL,NeurIPS"`（仅 s2/mock 生效；arXiv 无 venue 过滤） |
| 最大条数 | 否 | `--max 20`（默认 10） |
| LLM 合成 | 否 | 默认开（有 LLM 网关时）；`--no-llm` 强制关键词共现（离线/可复核） |
| 输出路径 | 否 | `--output review.json`，缺省打印 stdout |

缺失时一次性问齐：「请提供：① 主题 `--topic` ② 数据源 `--source`（s2 真实引用数 / arxiv / mock）③ venue 限定 `--venues`（仅 s2/mock）④ 条数 `--max` ⑤ 是否 `--no-llm` ⑥ 是否落盘 `--output`。」

## 前置自检
```bash
python3 --version                       # 预期 >= 3.8，否则 STOP
test -f scripts/lit_review.py && echo OK
# 若要真实检索需联网；离线先 export SKILLKIT_MOCK=1（强制 mock）
```

## 工作流：脚本检索与引用图谱产出

### 步骤 1：检索并产出
```bash
python3 scripts/lit_review.py --topic "LLM agents" --s2 --max 20 --output review.json   # 真实引用数/venue
python3 scripts/lit_review.py --topic "diffusion models" --arxiv --no-llm                # 真实检索，无引用数
SKILLKIT_MOCK=1 python3 scripts/lit_review.py --topic "LLM agents"                       # 离线/CI
```
预期：JSON 含 `topic`、`data_source`、`warning`、`retrieval_date`、`papers[]`、`citation_graph`、`summary`。
若失败：要真实数据却没加 `--s2`/`--arxiv` → 加上；离线 → `SKILLKIT_MOCK=1`。

### 步骤 2：判读 data_source（诚实标注）
- `data_source == "s2"` → Semantic Scholar 真实检索，`citations` 为**真实被引数**，`abstract` 截断 600 字符；引用图为 `co-cited`（共享引用）。
- `data_source == "arxiv"` → 真实检索但 `citations` 恒 0；`--venues` 不生效；引用图退化为 `same-venue-year`（低置信度）。
- `data_source == "mock"` → 合成数据，**MUST 标注模拟数据**。
若失败：`warning` 含「已回退为 MOCK」→ 说明所选网络源失败，结果实为 mock。

### 步骤 3：取用产物
预期：`papers[]` 写正文，`summary.gaps_identified` 入 Related Work，`citation_graph` 可视化（注意 `citation_graph.method` 说明边类型可信度）。`--no-llm` 时 `summary.synthesis_method == "keyword-cooccurrence"`，可复核。
若失败：产物 `status: empty` → 放宽主题/换关键词/换源。

## 核心步骤：PRISMA 检索与筛选方法论

1. **明确综述问题（PICO/SPIDER）**：Population、Intervention、Comparator、Outcome（定量）或 Sample、Phenomenon、Design、Evaluation、Research type（定性）；一句话写清，检索式才有靶子。
2. **定纳入/排除标准**：研究类型（实证/综述/会议）、时间窗（一般近 5-10 年）、语言、人群、发表类型；写成可判定的规则，例如"排除仅以摘要发表、无全文会议海报"。
3. **设计检索式**：每个数据库（Web of Science、Scopus、PubMed、ACM/IEEE Xplore、CNKI、万方）单独写式，用布尔运算 AND/OR、主题词+自由词组合；记录检索日期与命中条数。
4. **去重与筛选**：用 Zotero/EndNote 去重，标题摘要初筛（双人独立筛，不一致处讨论），再全文复筛；每一步留存剔除数与原因码。
5. **填证据提取表**：每篇纳入文献一行，列：作者年份、国家、研究类型、样本量、核心变量、方法、主要结论、局限。
6. **综合成述**：按主题/方法/结论分群，识别共识与争议；争议处单独成节，不强行和稀泥（脚本的 `summary.gaps_identified` 只是骨架，共识/争议判断须人工完成）。
7. **画 PRISMA 流程图**：识别→筛选→资格→纳入四框，标注各阶段数字。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--topic` | 字符串 | 检索主题（必填） |
| `--source` | `s2`/`arxiv`/`mock` | 数据源，默认 mock |
| `--s2` / `--arxiv` | 标志 | 等价 `--source s2/arxiv` |
| `--venues` | 逗号分隔 | venue 过滤，仅 s2/mock 生效 |
| `--max` | 整数 | 默认 10 |
| `--no-llm` | 标志 | 禁用 LLM 合成，强制关键词共现 |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `warning` 含「已回退为 MOCK」 | 所选网络源失败 | 按 mock 标注；重试或 `SKILLKIT_MOCK=1` |
| `data_source: mock` 但自称真实 | 误读来源 | 强制标注模拟数据 |
| `status: empty` | 无命中 | 放宽主题/venue/换源 |
| 图无 `co-cited` 边 | 无引用元数据（arxiv）或无共享引用 | 看 `citation_graph.method`，低置信度边勿当强关联 |
| `s2` 429/403 限流 | Semantic Scholar 共享出口配额 | 降 `--max`、稍后重试，或改用 `--arxiv` |
| 被引数与官方库对不上 | 数据源口径/抓取时间不同 | 用 `retrieval_date` + `doi` 重查，勿当权威统计 |

## 交付标准

成功定义：JSON 结构完整，顶层 `data_source` 与 `warning` 如实反映来源。
产物命名：`review.json`（若指定 `--output`）。
验证方法：`python3 -c "import json;d=json.load(open('<out>'));assert d['data_source'] in ('s2','arxiv','mock') and 'method' in d['citation_graph']"` 通过。

## 清单

- [ ] 综述问题已写成 PICO/SPIDER 一句话。
- [ ] 纳入/排除标准 ≥5 条，每条可客观判定。
- [ ] 每个数据库的检索式、检索日期、命中数已记录。
- [ ] 去重后总数、初筛剔除、全文复筛剔除、最终纳入数齐全。
- [ ] 证据提取表填满，每篇至少 8 个字段。
- [ ] 综述正文区分"共识 / 争议 / 空白"三部分。
- [ ] PRISMA 流程图四阶段数字闭环（输入=输出+剔除）。
- [ ] `data_source` 与 `warning` 如实标注，mock 结果已标「模拟数据」。
- [ ] 最终缺口能回链到 paper-topic-selector 的缺口矩阵。

## 易错点

- **只检一个数据库**：单库漏检率极高；综述至少跨 2 个英文库 + 1 个中文库（涉国内议题时）。
- **检索式写完不跑就写综述**：先跑一遍看命中量，命中 >2000 太泛、<20 太窄，要回调。
- **初筛不设剔除原因码**：最后写不出流程图，也说不清为什么剔。
- **综述写成流水账**：按作者逐篇罗列是综述大忌；要按"主题/方法/结论"聚类，作者只是证据。
- **纳入灰色文献不声明**：用了预印本、学位论文必须在方法里说明，否则被审稿人抓。
- **引用二手转引**：读到 A 引 B，必须找到 B 原文核对，不能直接引 B。
- **把 mock 检索当真实文献引用**：`data_source: mock` 的条目一旦进正文就是学术事故。
- **低置信度引用边当强关联**：arxiv 源的 `same-venue-year` 边不是共被引证据，别据此下"某某方向成体系"的结论。

## 参考

- [references/prisma-checklist.md](references/prisma-checklist.md) — PRISMA 2020 27 项核对表与流程图骨架，交付前逐项过。
- 多源检索/图/合成逻辑内置 `scripts/lit_review.py`：`_fetch_s2`/`_fetch_arxiv`/`search_papers`/`build_citation_graph`/`summarize`/`_keyword_fallback`。
- SOTA 工具链：Semantic Scholar Graph API（真实引用）、arXiv API、Scite（支持/反驳引用）、ResearchRabbit / Connected Papers（共同引用图谱）、Zotero + Better BibTeX（`.bib` 管理）。

## 链路位置

上游接 paper-topic-selector（用本 skill 查证其候选缺口是否真实）；`summary.gaps_identified` 交正文，图表交 pub-plotter，LaTeX 组装交 latex-formatter。
