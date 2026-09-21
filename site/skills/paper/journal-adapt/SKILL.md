---
name: journal-adapt
description: "Adapt a draft to a target venue's submission rules: IEEE / ACM / NeurIPS / ACL / Nature — column-aware page estimate with reference-page accounting, abstract word limit, venue-required sections (incl. NeurIPS/ACL Limitations), banned-phrase screening (e.g. Nature dislikes 'In this paper we' / 'Novel'), citation-style and double-blind checks. Use when the user asks 投 IEEE / 改成 Nature 风格 / 期刊格式适配 / 换会议模板 / 适配 ACL 格式. 当用户要求 按 venue 改稿 / 查禁词 时使用。Fails with rc=1 when the input file does not exist. Do NOT use for LaTeX template mechanics (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; static text checks against per-venue rule tables. Page counts are estimates — always confirm with the official venue template.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Journal Adapt (SOTA)

按目标 venue 的真实投稿规则校验草稿：页数（分栏感知）、摘要上限、必填章节、禁词、引用风格、双盲。

> 诚实声明：页数是**估算**——`words_per_page` 是分栏/字号下的社区经验值（NeurIPS 1 栏 ≈600 词/页；IEEE/ACM/ACL 2 栏 ≈950–1000 词/页），**正式投稿前 MUST 用 venue 官方模板编译确认**。`--template-year` 只替换类名里的年份串，不保证该年份模板存在。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 草稿文件 | 是 | `--input draft.tex`（.tex / 纯文本均可）；不存在则 rc=1 |
| 目标 venue | 否 | `--target ieee_conf`/`acm`/`neurips`/`acl`/`nature`（别名 `ieee`/`nips`/`emnlp`…），默认 `ieee_conf` |
| 模板年份 | 否 | `--template-year 2026`：把类名 `xxx_2025` 的年份替换掉 |
| 输出路径 | 否 | `--output report.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 草稿文件路径 `--input` ② 目标 venue ③ 目标年份的模板是否已发布 ④ 是否落盘 `--output`。其余用默认：target=ieee_conf，输出 JSON 到 stdout。」

## 前置自检
```bash
python3 --version                          # 预期 >= 3.8，否则报错并 STOP
test -f scripts/journal_adapt.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
test -f draft.tex && echo SRC_OK            # 预期 SRC_OK；缺失则脚本 rc=1，先 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示目录不完整；若 `--input` 文件不存在 → rc=1。

## 工作流

### 步骤 1：按目标 venue 检测
```bash
python3 scripts/journal_adapt.py --input draft.tex --target ieee_conf
python3 scripts/journal_adapt.py --input draft.tex --target neurips --template-year 2026
python3 scripts/journal_adapt.py --input draft.tex --target nature --output adapt_report.json
```
预期：输出 JSON 含 `target`、`class`、`columns`、`score`、`status`、`issues[]`、`words`、`body_words`、`est_pages`、`est_billable_pages`、`page_limit`、`refs_included`、`ref_pages`、`abstract_words`、`abstract_limit`、`ref_style_detected`、`anonymous_ok`、`method`、`notes`。
若失败：`rc=2` + `unknown target` → `--target` 取值不在规则表内，核对取值。

### 步骤 2：判读 verdict 并改稿

- `status == "pass"`（`issues` 为空）→ 通过。
- `status == "adjust_needed"` → 按 `issues[].severity` 优先级处置（high → medium → low）：

| type | 含义 | 处置 |
|------|------|------|
| `page_limit` | `est_billable_pages` 超限（已扣/含参考文献页） | 精简正文或把证明挪附录 |
| `missing_abstract` / `abstract_too_long` | 缺摘要 / 摘要超 venue 上限 | 补摘要；压缩时删修饰不删结论 |
| `missing_section` | 缺 venue 必填章节（NeurIPS/ACL 的 Limitations 常被漏） | 补章节 |
| `banned` | 命中 venue 禁词（如 Nature 的 "Novel"、"In this paper we"） | 换成有具体证据的表述 |
| `ref_style` | 检测到的引用风格与 venue 不符 | 用 venue 的 `.bst`/`.bbx` 重新生成参考文献 |
| `anonymity` | 双盲 venue 里出现作者块/致谢 | 投稿版删除作者与致谢 |

预期：每条 issue 给出 `type`/`severity` 与可定位信息（具体禁词、缺失章节、billable 页数）。
若失败：改稿后仍 `adjust_needed` → 先清 high，再清 medium/low。

### 步骤 3：存档（可选）
预期：`--output` 指向的 JSON 文件存在且合法。
若失败：路径不可写 → 换可写目录重试。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--input` | 路径 | 草稿文件（必填） |
| `--target` | ieee_conf / acm / neurips / acl / nature（+别名） | 目标 venue，默认 ieee_conf |
| `--template-year` | 4 位年份 | 替换类名年份串，如 `neurips_2025` → `neurips_2026` |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=1，File not found | `--input` 不存在 | 核对路径后重试 |
| rc=2，`unknown target` | `--target` 非法 | 改用规则表内 venue 或别名 |
| 页数估算与模板编译结果不符 | 估算是经验值，未含图/表占位 | 以官方模板编译结果为准；本工具只做早期预警 |
| `missing_section` 误报 | 章节标题本地化（写成中文或改名） | 用 venue 要求的英文标题 |
| `anonymity` 误报 | `\author{Anonymous Submission}` 之类匿名写法 | 该写法不会触发；若仍报，检查是否有致谢或正文提及单位 |
| 参考文献格式被标不合规 | bib 仍是上一套风格（编号 vs 作者年） | 改用目标 venue 的 style 文件重新生成参考文献 |

## 交付标准

成功定义：`status == "pass"`，或已据 `adjust_needed` 的 `issues[]` 完成改稿。
产物命名：`adapt_report.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['status'] in ('pass','adjust_needed')"` 通过。
诚实口径：`method: "column-aware-estimate"` 表示页数为分栏经验值估算，非编译实测。

## 参考

无外部 references 文件；venue 规则表内置在 `scripts/journal_adapt.py` 的 `JOURNAL_SPECS`（含 cls/options/columns/font_size/page_limit/refs_included/words_per_page/abstract_max_words/anonymous/ref_style/required_sections/banned/notes）。页数模型见 `adapt()`，参考文献切分见 `_split_bibliography()`。

## 链路位置

上游接 self-reviewer 的 ready 判定；语气打磨可续接 anti-defensive 与 ai-humanizer，最终 tex-cleaner 收口提交包。
