---
name: lit-review
description: "Literature review helper: scan a topic across venues, build a citation relationship map, and produce a structured summary with research-gap callouts. Use at the start of a paper project or when the user asks for 文献综述 / 相关工作梳理 / 找参考文献 / 调研某方向论文 / 写相关工作. 当用户要求 综述某主题 / 生成 citation graph 时使用。Do NOT use for topic selection (use paper-topic-selector first)."
license: Apache-2.0
compatibility: Stdlib only. --arxiv makes a real HTTPS call to export.arxiv.org (20s timeout, one 429 backoff retry); on any network/parse failure it falls back to MOCK data and flags it via top-level data_source/warning. SKILLKIT_MOCK=1 forces mock (no network).
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Lit Review

围绕主题扫描文献，构建引用关系图，产出带研究空白标注的结构化综述骨架。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 主题 | 是 | `--topic "LLM agents"` |
| 限定 venue | 否 | `--venues "ACL,NeurIPS"`（**仅对 mock 生效**） |
| 最大条数 | 否 | `--max 20`（默认 10） |
| 真实检索 | 否 | `--arxiv` 调真实 arXiv API；否则用 mock 数据 |
| 输出路径 | 否 | `--output review.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 主题 `--topic` ② 是否真实检索 `--arxiv`（否则 mock）③ venue 限定 `--venues`（仅 mock 生效）④ 条数 `--max` ⑤ 是否落盘 `--output`。」

## 前置自检
```bash
python3 --version                       # 预期 >= 3.8，否则报错并 STOP
test -f scripts/lit_review.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
```
若 `--arxiv`：需联网到 `export.arxiv.org`；离线环境先 `export SKILLKIT_MOCK=1` 强制 mock，否则网络失败会自动回退 mock 并在 `warning` 标注。

## 工作流

### 步骤 1：检索并产出
```bash
python3 scripts/lit_review.py --topic "LLM agents" --venues "ACL,NeurIPS" --max 20
python3 scripts/lit_review.py --topic "diffusion models" --arxiv --output review.json
SKILLKIT_MOCK=1 python3 scripts/lit_review.py --topic "LLM agents" --output review.json
```
预期：输出 JSON 含 `topic`、`data_source`、`warning`、`papers[]`、`citation_graph`、`summary`。
若失败：非 `--arxiv` 却要真实数据 → 加 `--arxiv`；离线 → 设 `SKILLKIT_MOCK=1`。

### 步骤 2：判读 data_source（诚实标注）

- `data_source == "arxiv"` → 真实检索结果；`citations` 恒为 0（arXiv 不提供引用数）；`--venues` 过滤**不**生效（已在 `warning` 提示）。
- `data_source == "mock"` → 合成数据，**MUST 标注"模拟数据"**，勿当真实检索呈现。
预期：顶层 `data_source` 与 `warning` 明确指示来源可信度。
若失败：`warning` 提示"已回退为 MOCK" → 说明 `--arxiv` 网络/解析失败，结果实为 mock。

### 步骤 3：取用产物

预期：`papers[]` 可用于写作，`summary.gaps_identified` 交给正文，`citation_graph` 可可视化。
若失败：产物为空（`status: empty`）→ 放宽 `--topic`/`--venues` 或换关键词。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--topic` | 字符串 | 检索主题（必填） |
| `--venues` | 逗号分隔 | venue 过滤，**仅 mock 生效** |
| `--max` | 整数 | 最大条数，默认 10 |
| `--arxiv` | 标志 | 调真实 arXiv API（否则 mock） |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `warning` 含"已回退为 MOCK" | `--arxiv` 网络/解析失败 | 结果按 mock 标注；重试或离线用 `SKILLKIT_MOCK=1` |
| `data_source: mock` 但自称真实 | 误读来源 | 强制标注"模拟数据" |
| `status: empty` | 无命中 | 放宽主题/venue 后重试 |

## 交付标准

成功定义：输出 JSON 结构完整且顶层 `data_source` 与 `warning` 如实反映来源。
产物命名：`review.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['data_source'] in ('arxiv','mock')"` 通过。

## 参考

无外部 references 文件；检索与图谱逻辑内置在 `scripts/lit_review.py`（`search_papers` / `build_citation_graph` / `summarize`；真实调用见 `_fetch_arxiv`，超时 20s、429 退避 3s）。

## 链路位置

上游接 paper-topic-selector；跑完把 `summary.gaps_identified` 交给正文写作，图表需求移交 figure-maker 或 pub-plotter，LaTeX 组装移交 latex-formatter。
