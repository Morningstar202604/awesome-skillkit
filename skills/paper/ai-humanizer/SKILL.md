---
name: ai-humanizer
description: "Strip AI-flavored writing from academic text: clichés ('delve'/'leverage'/'state-of-the-art' spam), empty intensifiers, over-qualification, repetitive openers — keeping the academic register. Use when the user asks 去 AI 味 / 降低 AI 痕迹 / 学术文本去套路 / 去掉 AI 腔 / humanize text. 当用户要求 改写去掉机器味 / 降 AI 率 时使用。Do NOT use for defensive/hedging tone (use anti-defensive) or pure LaTeX formatting (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; reads --text or --file, optional --report / --output.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# AI Humanizer

检测并标记学术文本中的 AI 腔措辞，保持学术语域。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 待处理文本 | 是 | `--text "..."` 直接传文本，或 `--file draft.tex` 读文件 |
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
```
预期：输出 JSON（无 `--report`）或人读摘要（有 `--report`），含 `score`、`status`、`issues`。
若失败：`Need --text or --file` → 未给输入，回到输入清单补齐。

### 步骤 2：判读 verdict 并改写

- `status == "clean"`（`score >= 85/100`）→ 通过，无需改写。
- `status == "needs_edit"`（`score < 85`）→ 按 `issues[].fix_hint` 逐条改写。
预期：`issues` 每项含 `type`/`matches`/`severity`/`fix_hint`，可直接照改。
若失败：改写后仍 `needs_edit` → 优先复检 `severity: high` 项（如 buzzwords / template_phrases）。

### 步骤 3：存档（可选）
```bash
python3 scripts/ai_humanizer.py --file draft.tex --output humanize_report.json
```
预期：`humanize_report.json` 存在且为合法 JSON。
若失败：路径不可写 → 换可写目录重试。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--text` | 字符串 | 直接传入待检测文本 |
| `--file` | 路径 | 读取文本 / .tex 文件 |
| `--report` | 标志 | 打印人读摘要而非 JSON |
| `--output` | 路径 | 将 JSON 结果写入文件 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `Need --text or --file` | 未提供输入 | 回到输入清单补齐 |
| 空 `issues` 但 score 偏低 | 命中未列规则 | 人工复核，必要时补 `AI_PATTERNS` |
| 文件读取失败 | 路径不存在 / 编码错误 | 校验 `--file` 路径真实存在 |
| 改写后分数不升反降 | 删掉旧措辞又引入了新的模板句式 | 重新跑检测，重点看新出现的 high severity 项，别只看总分 |
| 中文段落被误报 | 词表以英文 AI 高频词为主，中文规则较粗 | 人工判断中文命中项，确属误报则在报告中标注忽略理由 |
| score 正常但读起来仍像 AI 写的 | 静态词表查不出句式节奏与信息密度问题 | 本工具只负责词面层；交人工做结构调整，不要只信分数 |

## 交付标准

成功定义：`status` 为 `clean`，或已据 `needs_edit` 的 `fix_hint` 完成改写。
产物命名：`humanize_report.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json; json.load(open('<output>'))"` 解析通过。

## 参考

检测规则内置在 `scripts/ai_humanizer.py` 的 `AI_PATTERNS`，无需额外 reference 文件。

## 链路位置

本技能管"AI 腔"，与 anti-defensive（管"防御腔"）并列；改完统一交 tex-cleaner 收口。
