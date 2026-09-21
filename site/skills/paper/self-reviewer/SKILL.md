---
name: self-reviewer
description: "Simulate a peer review pass on your own draft: structural gates + ML reproducibility rubric (statistical significance, ablation, baselines, code/data/seeds), each check with reviewable evidence. Use before submitting or after finishing a draft. 当用户要求 模拟审稿 / 自查论文 / 投稿前检查 / 审稿人视角检查 / 论文结构自查 / paper self review / 检查够不够投稿 时使用。 Fails with rc=1 when the paper file does not exist. 何时使用：论文初稿写完、准备投稿或收到审稿意见需要自查时。触发场景（中/英）：模拟审稿 / 自查论文 / 投稿前检查 / 审稿人视角 / paper self review / pre-submission check. 排除项：不修正 LaTeX 格式与宏包问题（交给 latex-formatter），不换期刊模板（交给 journal-adapt）。Use when the user asks 模拟审稿 / 自查论文 / 投稿前检查 / 论文结构自查 / paper self review / pre-submission check. Do NOT use when the task is LaTeX formatting cleanup (use latex-formatter) or adapting to a journal template (use journal-adapt)."
license: Apache-2.0
compatibility: Stdlib only; reads .tex or plain-text drafts. Optional LLM evidence via --llm-evidence JSON.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Self Reviewer (SOTA)

投稿前先当自己的 reviewer #4：结构门槛 + ML 可复现性 rubric，每个检查项给出**可复核的 evidence 片段**（而非只给布尔），uncertain 项显式标注「需 LLM/人工复核」。

> 诚实声明：默认 `method=keyword-fallback`（纯字符串/词数统计，可离线复现）；提供 `--llm-evidence`（JSON：`{check: {evidence, confidence}}`）时切 `method=llm-evidence`，用模型给出的证据 + 置信度替代关键词命中。**无论哪种 method，`uncertain` 非空时 `status` 一律 `needs_work`，不得只凭 score 下结论。**

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 论文文件 | 是 | `--paper draft.tex`（.tex 或纯文本草稿）；不存在则 **rc=1** |
| LLM 证据 | 否 | `--llm-evidence llm_review.json`（`{check: {evidence, confidence}}`）；缺失则关键词回退 |
| 完整清单 | 否 | `--checklist` 只打印四类检查清单 JSON 后退出，不做评审 |
| 输出路径 | 否 | `--output review.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 论文文件路径 `--paper` ② 是否提供 `--llm-evidence`（否则关键词回退）③ 是否只要看检查清单 `--checklist` ④ 是否落盘 `--output`。」

## 前置自检
```bash
python3 --version                            # 预期 >= 3.8，否则报错并 STOP
test -f scripts/self_reviewer.py && echo OK  # 预期打印 OK，否则脚本缺失 STOP
test -f "$PAPER" && echo PAPER_OK            # 预期打印 PAPER_OK；缺失则脚本 rc=1，先 STOP
```

## 工作流

### 步骤 1：跑结构 + rubric 审查
```bash
# 关键词回退（离线可复现）
python3 scripts/self_reviewer.py --paper draft.tex
# LLM 证据增强
python3 scripts/self_reviewer.py --paper draft.tex --llm-evidence llm_review.json --output review.json
```
预期：输出 JSON 含 `word_count`、`score`（0-100）、`method`（`keyword-fallback`/`llm-evidence`）、`passed[]`、`failed[]`、`uncertain[]`、`evidence{}`、`status`、`next_steps[]`、`file`；文件不存在时 `{"error": "File not found: <path>"}` 且 **rc=1**。
若失败：rc=1 → 核对 `--paper` 路径后重试；输出非 JSON → 检查文件是否可读（编码非 UTF-8 会抛异常）。

### 步骤 2：判读判定
- **hard gate（failed 即 needs_work）**：abstract、`\section` ≥ 4、有 `\cite`/`\bibliography`、词数 ≥ 3000。
- **rubric 项（uncertain 即 needs_work）**：Statistical significance tested / Ablation / Baselines(2+) / Limitations / Reproducibility(seeds,code,data)——命中关键词或 LLM 置信度 ≥0.6 记 passed（附 `evidence`），否则进 `uncertain` 待复核。
- `status == "ready"`：`score ≥ 80` **且 `uncertain` 为空**。
- `status == "needs_work"`：`score < 80` 或 `uncertain` 非空；`failed[]`/`uncertain[]` 指明缺什么，`evidence{}` 给出命中片段。
若失败：`uncertain[]` 非空 → 逐条用 LLM/人工复核（补 `--llm-evidence` 或手改），切勿只信 `score` 定稿。

### 步骤 3：按清单补查语义项
```bash
python3 scripts/self_reviewer.py --paper draft.tex --checklist
```
预期：打印 `structure` / `content` / `writing` / `formatting` 四类清单 JSON（含脚本不自动查的项）。
若失败：无（纯打印）；清单中的语义项由模型对照原文逐条给出 pass/fail 与证据句。

### 步骤 4：交接下游
预期：`ready`（且 uncertain 空）→ 移交 journal-adapt 换目标模板，最后 tex-cleaner 收口；`needs_work` → 携带 `next_steps[]` 回正文修订，改完重跑步骤 1 复核分数上升。
若失败：修完重跑分数没变 → 确认改动真的写回了 `--paper` 指向的同一文件。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--paper` | 路径 | 论文文件（必填），.tex 或纯文本 |
| `--llm-evidence` | 路径(JSON) | `{check:{evidence,confidence}}`；缺失则关键词回退 |
| `--checklist` | 标志 | 只打印四类检查清单 JSON 并退出 |
| `--output` | 路径 | 结果 JSON 输出路径，缺省打印 stdout |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=1，`File not found` | `--paper` 路径不存在 | `ls` 确认路径后重试 |
| `uncertain` 非空但 score 高 | rubric 项未命中关键词 | 补 `--llm-evidence` 或人工确认，不得据此 `ready` |
| 词数远超预期 | 把 .bib/注释也算进了 split 计数 | 属静态统计口径，仅作下限检查；精确排版字数以编译后 PDF 为准 |
| 非 UTF-8 文件读入异常 | 老编码文件 | `iconv -f GBK -t UTF-8` 转码后重试 |

## 交付标准

成功定义：输出 JSON 判定字段齐全（`status`/`score`/`method`/`passed`/`failed`/`uncertain`/`evidence`/`next_steps`），且 `uncertain` 项均已人工/LLM 复核；`ready` 仅当 uncertain 为空。
产物命名：`review.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['status'] in ('ready','needs_work')"` 通过。

## 参考

无外部 references 文件；rubric 与四类清单内置在 `scripts/self_reviewer.py` 的 `review_paper` / `CHECKLIST` / `KEYWORDS`。可复现性检查对齐 papers-with-code 清单与 IMRaD 统计门槛。

## 链路位置

上游接 latex-formatter（格式先过关）。`needs_work` 时回到正文修订；`ready`（uncertain 空）后移交 journal-adapt 换目标模板，最后 tex-cleaner 收口。
