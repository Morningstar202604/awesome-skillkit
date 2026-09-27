---
name: journal-adapt
description: "目标期刊格式、禁词与投稿模板适配工具。当用户已经锁定或正在挑选目标期刊/会议，需要把稿件改成该刊投稿格式、核对引用风格、排查该刊敏感词与选题禁区、准备投稿信时使用。适配 academic-format-guardian 与 academic-editor-liaison，输出期刊要素对照表、格式差异清单与投稿材料 checklist。内置 IEEE / ACM / NeurIPS / ACL / Nature 等 venue 规则表，做分栏感知页数估算（含参考文献页）、摘要上限、必填章节、禁词筛查、引用风格与双盲检查；触发词：投 IEEE / 改成 Nature 风格 / 期刊格式适配 / 换会议模板 / 适配 ACL 格式 / 按 venue 改稿 / 查禁词。Do NOT use for LaTeX 模板机制（交给 latex-formatter）。"
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

# Journal Adapt / 期刊格式与投稿适配

按目标 venue 的真实投稿规则校验草稿：页数（分栏感知）、摘要上限、必填章节、禁词、引用风格、双盲。本 skill 供「格式规范卫士」与「期刊联络官」使用：论文被拒，一半死于内容，一半死于"不对路"——篇幅超了、引用风格错了、图表分辨率不够、写了该刊不收的选题。本 skill 负责在投稿前把这些硬伤全排掉。

> 诚实声明：页数是**估算**——`words_per_page` 是分栏/字号下的社区经验值（NeurIPS 1 栏 ≈600 词/页；IEEE/ACM/ACL 2 栏 ≈950–1000 词/页），**正式投稿前 MUST 用 venue 官方模板编译确认**。`--template-year` 只替换类名里的年份串，不保证该年份模板存在。

## 这是什么

不是泛泛地"排版好看"，而是对着**具体某一本刊/某一个会议**的作者须知（Author Guidelines）逐条核对，并用脚本按 venue 规则表做静态检查：

- 篇幅与结构：正文字数、摘要词数、参考文献条数、图表数量上限、分栏感知页数（含参考文献页）。
- 格式模板：LaTeX/Word 模板、参考文献风格（APA/IEEE/Chicago/数字角标）、正文层级写法。
- 视觉规范：图表分辨率（常见 300/600 dpi）、色彩模式（RGB/CMYK）、单栏/双栏、图注位置。
- 选题与伦理：该刊近 2 年不收什么（如纯综述、纯方法无实证、某类敏感主题）、是否要求数据公开、伦理批件、利益冲突声明。
- 投稿材料：Cover Letter、Highlights、Graphical Abstract、盲审要求（是否匿名稿）。
- 硬性筛查：venue 必填章节（NeurIPS/ACL 的 Limitations）、禁词（如 Nature 不喜欢的 "In this paper we"、"Novel"）、双盲合规。

## 何时使用

- 用户说"我要投 X 刊 / X 会，帮我对一下格式"。
- 用户问"我这稿子适合投哪"，需要先建立要素对照表再做匹配。
- 用户要求 按 venue 改稿 / 查禁词，或点名 投 IEEE / 改成 Nature 风格 / 换会议模板 / 适配 ACL 格式。
- 团队 W5 投稿定稿阶段、W1 的 Phase 6/8。
- 一审被拒需要转投另一本刊时。
- 不用于：LaTeX 模板机制本身（类名、编译、宏包）→ `latex-formatter`。

## 方法论：核对核心步骤

1. **拿到目标刊全称**：中英文全称 + ISSN 或会议全称 + 年份；不确定时先与用户确认，避免把两个同名期刊搞混。
2. **抓取作者须知**：到期刊官网 Author Guidelines 页逐条记录关键参数（见下方模板）。官网打不开时用该刊近 2 期已发表文章反推格式。
3. **填期刊要素对照表**：
   - 摘要词数 / 正文字数 / 参考文献条数上限
   - 引用风格（角标数字 / 作者-年份）
   - 图表 dpi、是否接受彩色、图注中英文
   - 是否要求匿名审稿、是否要求数据存仓库
   - 投稿系统（ScholarOne / Editorial Manager / 自建）与文件格式
4. **逐段核对稿件**：把当前稿件与对照表逐项打勾，超篇幅的先砍，引用风格错的批量改。
5. **排禁词与选题雷区**：查该刊近 2 年拒稿声明 / Editor's Note，标出"本刊不接受纯 A 类、不接受 B 主题"等红线；核对是否触及伦理敏感（人类受试者、未公开数据、利益冲突未声明）。
6. **备齐投稿材料包**：Cover Letter（3 段：做了什么、为什么适合本刊、无一稿多投声明）、Highlights（3-5 条，每条 ≤85 字符）、Graphical Abstract（如要求）、匿名版与终版双份。

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

## 清单（投稿前逐项过）

- [ ] 目标刊全称/ISSN 已确认，作者须知原文已存档。
- [ ] 篇幅：摘要词数、正文字数、参考文献条数全部在限内；页数已用官方模板编译复核。
- [ ] 引用风格与该刊已发表文章一致，逐条抽查 10 条。
- [ ] 图表 dpi、色彩模式、图注位置符合要求。
- [ ] 盲审版已删除作者信息、致谢、自引可识别线索。
- [ ] 伦理批件号、利益冲突声明、数据可得性声明齐备。
- [ ] Cover Letter、Highlights、Graphical Abstract（如要求）已写好。
- [ ] 已查该刊近 2 年 Editor's Note，确认选题不在拒稿雷区。

## 易错点

- **只看模板不看须知**：模板是骨架，字数/伦理/数据公开要求写在 Author Guidelines 正文里，必须逐条读。
- **引用风格"差不多就行"**：APA 7 与 APA 6、IEEE 与 numbered style 在页码缩写、期刊名斜体上都有差别，审稿编辑一眼能看出。
- **图表按屏幕截图交**：屏幕截图 72 dpi，印刷出来全是马赛克；投稿图必须从原始数据重新导出矢量或 300 dpi 以上位图。
- **Cover Letter 写成摘要扩写**：Cover Letter 重点是"为什么这本刊的读者会关心"，不是复述论文。
- **忽视转刊沉没成本**：转投时上一本刊的审稿意见、补的实验数据要在新投稿里体现，但旧刊的篇幅/风格残留必须清干净。
- **把页数估算当编译实测**：估算只做早期预警，最终以官方模板编译结果为准。
