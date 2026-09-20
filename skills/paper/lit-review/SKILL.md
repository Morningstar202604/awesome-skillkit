---
name: lit-review
description: "Multi-source literature review: real retrieval via Semantic Scholar Graph API (--s2, with true citations/venue/year/abstract) or arXiv (--arxiv), honest mock fallback for offline/CI; builds a REAL co-citation graph (shared references) instead of sequential links; synthesizes trends/gaps via LLM (model_route) with keyword-cooccurrence fallback. Use for 文献综述 / 相关工作梳理 / 找参考文献 / 调研某方向论文 / 综述某主题 / citation graph. Do NOT use for topic selection (use paper-topic-selector first)."
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

# Lit Review

围绕主题做**多源真实检索**，构建**基于共享引用的真实引用图**，并产出带研究空白标注的综述骨架（LLM 合成 + 关键词共现兜底）。

> 诚实声明：`data_source` 恒为 `s2` | `arxiv` | `mock`。任何回退都写进 `warning`；**`mock` 结果 MUST 标注「模拟数据」**，勿当真实检索呈现。`retrieval_date` 记录抓取日期（复现性要求「存 DOI 不存查询」，可据此重查）。

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

## 工作流

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

## 参考

多源检索/图/合成逻辑内置 `scripts/lit_review.py`：`_fetch_s2`/`_fetch_arxiv`/`search_papers`/`build_citation_graph`/`summarize`/`_keyword_fallback`。
SOTA 工具链：Semantic Scholar Graph API（真实引用）、arXiv API、Scite（支持/反驳引用）、ResearchRabbit / Connected Papers（共同引用图谱）、Zotero + Better BibTeX（`.bib` 管理）。

## 链路位置

上游接 paper-topic-selector；`summary.gaps_identified` 交正文，图表交 pub-plotter，LaTeX 组装交 latex-formatter。
