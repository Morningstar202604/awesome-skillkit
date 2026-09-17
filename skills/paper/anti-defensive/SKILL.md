---
name: anti-defensive
description: "Detect and fix defensive academic writing: over-hedging (double 'may/might'), self-deprecating framing, vague attribution like 'some researchers'. Use when the user asks 论文语气太弱 / 去掉防御性表达 / 强化陈述 / 别太委婉 / de-hedge text. 当用户要求 把话说硬一点 / 去掉 may possibly 时使用。Do NOT use for removing AI-flavored clichés (use ai-humanizer) or LaTeX formatting (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; reads --text or --file, optional --output.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Anti-Defensive

检测学术文本中的防御性/对冲措辞，给出具体改写建议。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 待处理文本 | 是 | `--text "..."` 直接传文本，或 `--file draft.md` 读文件 |
| 输出路径 | 否 | `--output report.json` 保存 JSON，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 待处理文本（直接贴出或用文件路径）② 是否落盘（--output 路径）。其余用默认：输出 JSON 到 stdout。」

## 前置自检
```bash
python3 --version                          # 预期 >= 3.8，否则报错并 STOP
test -f scripts/anti_defensive.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示本技能目录不完整，勿继续。

## 工作流

### 步骤 1：加载并检测文本
```bash
python3 scripts/anti_defensive.py --file draft_section.md
python3 scripts/anti_defensive.py --text "Our results suggest that the method may possibly improve"
```
预期：输出 JSON，含 `score`、`status`、`issues`，每项 `issue`/`fix`/`examples` 可直接照改。
若失败：`Need --text or --file` → 未给输入，回到输入清单补齐。

### 步骤 2：判读 verdict 并改写

- `status == "clean"`（`score >= 80/100`）→ 通过，无需改写。
- `status == "rewrite_needed"`（`score < 80`）→ 按 `issues[].fix` 逐条改写。
预期：`issues` 列出每处防御腔的具体 `fix` 建议。
若失败：改写后仍 `rewrite_needed` → 复盘双重限定（"may possibly"）与自贬框架优先。

### 步骤 3：存档（可选）
```bash
python3 scripts/anti_defensive.py --file draft_section.md --output anti_defensive_report.json
```
预期：`anti_defensive_report.json` 存在且为合法 JSON。
若失败：路径不可写 → 换可写目录重试。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--text` | 字符串 | 直接传入待检测文本 |
| `--file` | 路径 | 读取文本 / .md 文件 |
| `--output` | 路径 | 将 JSON 结果写入文件 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `Need --text or --file` | 未提供输入 | 回到输入清单补齐 |
| 空 `issues` 但 score 偏低 | 命中未列规则 | 人工复核，必要时补 `DEFENSIVE_PATTERNS` |
| 文件读取失败 | 路径不存在 / 编码错误 | 校验 `--file` 路径真实存在 |
| 改写后语气过硬、像断言 | 把 double hedge 直接删成裸断言 | 保留一处限定条件（样本/范围），只删重复与自我贬低措辞 |
| 该保守的结论被改掉 | 'may' 本身是合理的统计限定 | 统计上不确定的结论必须保留限定语，只改语言性弱化 |
| 同一 `fix` 反复命中 | 改写文本未写回 `--file` 指向的原文件 | 确认改动落盘后重跑，避免对着旧文本重复改写 |

## 交付标准

成功定义：`status` 为 `clean`，或已据 `rewrite_needed` 的 `fix` 完成改写。
产物命名：`anti_defensive_report.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json; json.load(open('<output>'))"` 解析通过。

## 参考

检测规则内置在 `scripts/anti_defensive.py` 的 `DEFENSIVE_PATTERNS`，无需额外 reference 文件。

## 链路位置

本技能管"防御腔"，与 ai-humanizer（管"AI 腔"）并列；改完回灌 latex-formatter 复检，最后由 tex-cleaner 收口。
