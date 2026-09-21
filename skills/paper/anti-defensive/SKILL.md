---
name: anti-defensive
description: "Detect defensive academic writing and classify each hit as tighten vs retain: over-hedging (double 'may/might'), self-deprecating framing, vague attribution 'to the best of our knowledge', filler phrases — but hedges sitting next to statistical-uncertainty context (confidence interval / p-value / variance / sample size) are marked retain and never penalized. Reports hedge density per 100 words with line:col locations. Use when the user asks 论文语气太弱 / 去掉防御性表达 / 强化陈述 / 别太委婉 / de-hedge text. 当用户要求 把话说硬一点 / 去掉 may possibly 时使用。Do NOT use for removing AI-flavored clichés (use ai-humanizer) or LaTeX formatting (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; reads --text or --file, optional --output.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Anti-Defensive (SOTA)

检测学术文本中的防御性/对冲措辞，并**区分该收紧与该保留**——旧版把「所有限定都当坏事」，会让统计结论被错误地改成裸断言。

> **诚实声明**：只有 `action == "tighten"` 的命中扣分；`action == "retain"` 表示该限定语出现在**统计不确定语境**（置信区间 / p 值 / 方差 / 样本量 / 分布漂移 / 估计量）附近，属**合理统计限定**——删掉它是学术错误，不是风格改进。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 待处理文本 | 是 | `--text "..."` 直接传，或 `--file draft.md` 读文件；`--file` 不存在则 rc=1 |
| 语境窗口 | 否 | `--context-window 80`（默认 80 字符）：命中前后各查这么多字符找统计语境 |
| 输出路径 | 否 | `--output report.json` 保存 JSON，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 待处理文本（直接贴出或用文件路径）② 是否落盘（--output 路径）。其余用默认：输出 JSON 到 stdout。」

## 前置自检
```bash
python3 --version                          # 预期 >= 3.8，否则报错并 STOP
test -f scripts/anti_defensive.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
test -f "$FILE" && echo FILE_OK            # 仅当用 --file；缺失则 rc=1，先 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示本技能目录不完整，勿继续。

## 工作流

### 步骤 1：加载并检测文本
```bash
python3 scripts/anti_defensive.py --file draft_section.md
python3 scripts/anti_defensive.py --text "Our results suggest that the method may possibly improve"
```
预期：输出 JSON，含 `score`、`status`、`method`（`pattern+context-classifier`）、`issues[]`、`n_flags`（需收紧的类别数）、`n_retained_only`、`hedge_density_per_100w`、`hedges_total`、`words`、`tighten_hits`、`retain_hits`、`note`。每条 `issues[]` 含 `type`/`issue`/`fix`/`severity`/`count`/`action`（`tighten`/`retain`）/`retained`/`tightened`/`positions`/`examples`。
若失败：`Need --text or --file` → 未给输入，回到输入清单补齐；rc=1 → `--file` 路径不存在。

### 步骤 2：判读 verdict 并改写

- `status == "clean"`（`score >= 80`）→ 通过。
- `status == "rewrite_needed"` → **只改 `action == "tighten"` 的项**，按 `issues[].fix` 执行：

| type | 含义 | 处置 |
|------|------|------|
| `double_hedge` | "may possibly" 双重对冲 | 留一个限定；若结论是统计性的，保留 `may` 并补 CI |
| `vague_attribution` | "to the best of our knowledge" | 改成引用某综述/benchmark 建立空白 |
| `filler_phrase` | "it should be noted that" | 直接删，陈述事实 |
| `weak_self_criticism` | "some limitations exist" | 带证据写具体：`Accuracy drops 3% on X (Table 7)` |
| `editorializing` | "unfortunately" / "not surprisingly" | 去主观，中立陈述结果 |
| `undersell` | "a minor improvement" | 报数字：`1.2% improvement` |

预期：`issues` 每项可直接照改，且 `retain` 项明确标注为不可删。
若失败：改写后仍 `rewrite_needed` → 复盘 `double_hedge` 与 `weak_self_criticism`（扣分权重最高的两类）。

### 步骤 3：存档（可选）
预期：`anti_defensive_report.json` 存在且为合法 JSON。
若失败：路径不可写 → 换可写目录重试。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--text` | 字符串 | 直接传入待检测文本 |
| `--file` | 路径 | 读取文本 / .md / .tex 文件；不存在则 rc=1 |
| `--context-window` | 整数 | 命中前后各查多少字符找统计语境，默认 80 |
| `--output` | 路径 | 将 JSON 结果写入文件 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=1，`File not found` | `--file` 路径不存在 | 核对路径后重试 |
| `Need --text or --file` | 未提供输入 | 回到输入清单补齐 |
| 改写后语气过硬、像断言 | 把限定直接删成裸断言 | 只删 `action=tighten` 的项；`retain` 项必须保留 |
| 该保守的结论被改掉 | 'may' 本身是合理的统计限定 | 调大 `--context-window` 让它被识别为 `retain`，或人工保留 |
| 空 `issues` 但 score 偏低 | 不可能（score 只由 tighten_hits 扣） | 检查是否误读 `hedge_density_per_100w`——它是**指标**，不扣分 |
| 同一 `fix` 反复命中 | 改写文本未写回 `--file` 指向的原文件 | 确认改动落盘后重跑，避免对着旧文本重复改写 |

## 交付标准

成功定义：`status` 为 `clean`，或已据 `rewrite_needed` 的 `fix` 完成改写（且所有 `retain` 项原样保留）。
产物命名：`anti_defensive_report.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['method']=='pattern+context-classifier'"` 通过。

## 参考

检测规则（`DEFENSIVE_PATTERNS`）、统计语境判定（`LEGIT_CONTEXT`）、对冲词表（`HEDGE_LEXICON`）内置在 `scripts/anti_defensive.py`，无需额外 reference 文件。

## 链路位置

本技能管"防御腔"，与 ai-humanizer（管"AI 腔"）并列；改完回灌 latex-formatter 复检，最后由 tex-cleaner 收口。
