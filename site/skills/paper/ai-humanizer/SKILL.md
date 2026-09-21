---
name: ai-humanizer
description: "Strip AI-flavored writing from academic text on two axes: lexical tells (clichés 'delve'/'leverage'/'state-of-the-art' spam, empty intensifiers, over-qualification, repetitive openers) AND structural tells (low sentence-length burstiness, consecutive same openers, low lexical diversity, repeated 5-grams), each hit located by line:col. Use when the user asks 去 AI 味 / 降低 AI 痕迹 / 学术文本去套路 / 去掉 AI 腔 / humanize text. 当用户要求 改写去掉机器味 / 降 AI 率 时使用。Do NOT use for defensive/hedging tone (use anti-defensive) or pure LaTeX formatting (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; reads --text or --file, optional --report / --output.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# AI Humanizer (SOTA)

检测并标记学术文本的 AI 腔——**词面层**（`AI_PATTERNS`）+ **结构层**（句长起伏、句首重复、词汇多样性、n-gram 重复），每条命中带 `line:col` 定位。

> **诚实声明（务必读）**：AI 文本检测器在 2026 年依然**不可靠**（误报率高；OpenAI 已于 2023 年关停其 classifier；多所高校明确检测器分数不能作为学术不端证据）。本工具测的是**文风痕迹**，不是**作者身份**——输出只能用于**改写建议**，MUST NOT 用于指控。输出 JSON 的 `detector_note` 字段固化了这条声明，`--report` 也会打印。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 待处理文本 | 是 | `--text "..."` 直接传，或 `--file draft.tex` 读文件（`--file` 路径不存在会走 `--text` 分支，都没有则 rc≠0） |
| 报告模式 | 否 | `--report` 打印人读摘要；否则输出 JSON |
| 输出路径 | 否 | `--output report.json` 保存 JSON，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 待处理文本（直接贴出或用文件路径）② 是否需要人读报告（--report）③ 是否落盘（--output 路径）。其余用默认：仅输出 JSON 到 stdout。」

## 前置自检
```bash
python3 --version                       # 预期 >= 3.8，否则报错并 STOP
test -f scripts/ai_humanizer.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示本技能目录不完整，勿继续。

## 工作流

### 步骤 1：加载并检测文本
```bash
python3 scripts/ai_humanizer.py --file draft.tex --report
python3 scripts/ai_humanizer.py --text "Our novel framework leverages state-of-the-art methods"
python3 scripts/ai_humanizer.py --file draft.tex --output humanize_report.json
```
预期：输出 JSON（无 `--report`）或人读摘要（有 `--report`），含 `score`、`status`、`method`（`lexical+structural`）、`issues[]`（词面，带 `positions`）、`structural[]`（结构）、`metrics{}`（`burstiness`/`max_opener_run`/`type_token_ratio`/`repeated_5grams`/`n_sentences`）、`detector_note`。
若失败：`Need --text or --file` → 未给输入或文件不存在，回到输入清单补齐。

### 步骤 2：判读 verdict 并改写

- `status == "clean"`（`score >= 85`）→ 通过；`needs_edit` → 按 `issues[].fix_hint` + `structural[].fix_hint` 逐条改。
- 优先清 **high**（`buzzwords` / `template_phrases` / `llm_verb_spam`），再清结构项：

| 结构项 | 阈值 | 含义 | 处置 |
|--------|------|------|------|
| `low_burstiness` | burstiness < 0.35 | 句长过于均匀（LLM 典型特征） | 长短句交替，用短句起头下结论 |
| `opener_repetition` | 连续 ≥3 句同开头词 | 过渡词机械轮转 | 换过渡方式或直接删过渡词 |
| `low_lexical_diversity` | TTR < 0.35 且 ≥20 句 | 词汇面过窄/句式模板化 | 检查重复句式，合并或改写 |
| `repeated_ngram` | 同一 5-gram ≥2 次 | 原句反复出现 | 去重或合并那些句子 |

预期：`issues` 每项含 `type`/`matches`/`severity`/`positions`/`fix_hint`，可直接照改。
若失败：改写后仍 `needs_edit` → 复检 high 项与新出现的结构项，别只看总分。

### 步骤 3：存档（可选）
预期：`humanize_report.json` 存在且为合法 JSON。
若失败：路径不可写 → 换可写目录重试。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--text` | 字符串 | 直接传入待检测文本 |
| `--file` | 路径 | 读取文本 / .tex 文件 |
| `--report` | 标志 | 打印人读摘要（含结构指标与诚实声明）而非 JSON |
| `--output` | 路径 | 将 JSON 结果写入文件 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `Need --text or --file` | 未提供输入 | 回到输入清单补齐 |
| 空 `issues` 但 score 偏低 | 扣分来自 `structural`（结构层） | 看 `structural[]` 与 `metrics{}`，不是词表漏了 |
| `burstiness` 为 `null` | 句子 < 3 句（无法算方差） | 属正常；短文本不做句长分析 |
| 文件读取失败 | 路径不存在 / 编码错误 | 校验 `--file` 路径真实存在 |
| 改写后分数不升反降 | 删掉旧措辞又引入了新的模板句式 | 重跑检测，重点看新出现的 high 项，别只看总分 |
| 中文段落被误报 | 词表以英文 AI 高频词为主，中文规则较粗 | 人工判断中文命中项，确属误报则标注忽略理由 |
| score 正常但读起来仍像 AI 写的 | 静态分析查不出论证逻辑与信息密度问题 | 本工具只覆盖词面+浅结构层；深度问题交人工，不要只信分数 |

## 交付标准

成功定义：`status` 为 `clean`，或已据 `needs_edit` 的 `fix_hint` 完成改写。
产物命名：`humanize_report.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['method']=='lexical+structural'"` 通过。
诚实口径：任何场景下都不得把本工具输出当作「判定作者是 AI」的依据。

## 参考

检测规则（`AI_PATTERNS`）、结构指标（`structural_metrics`）、定位工具（`_positions`）内置在 `scripts/ai_humanizer.py`，无需额外 reference 文件。停用词表见 `STOPWORDS`。

## 链路位置

本技能管"AI 腔"，与 anti-defensive（管"防御腔"）并列；改完统一交 tex-cleaner 收口。
