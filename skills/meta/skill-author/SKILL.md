---
name: skill-author
description: >
  Draft a new agent skill from scratch: clarify the need in one batch of five
  questions, name it as a searchable kebab-case action phrase, write a
  trigger-rich description, generate the ten-section SKILL.md skeleton, and
  design its scripts with argparse subcommands and a dry-run default. Use when
  the user asks to 写一个技能 / 做个技能 / 新建 skill / 帮我写 SKILL.md /
  author a skill / create a new skill / scaffold a skill. Do NOT use for
  checking an existing skill against the spec (that is skill-linter) or for
  finding a skill in this repo (that is skill-finder).
license: Apache-2.0
compatibility: Pure prompt-based; optional python3 for the self-check step.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Skill Author（技能生成器）

把一个模糊的「我想让 agent 会做某件事」变成一份可直接提交的 SKILL.md：先一次性问清边界，再定名与触发词，再套骨架落字，最后自检。产出物是技能文件本身，不是关于技能的散文。

本技能**不写脚本逻辑**（只给 argparse 子命令与 dry-run 设计），**不做合规判定**（那交给 `skill-linter`）。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 技能要解决的问题 | 是 | — | 一句话，含使用场景；不是「做个工具」这种层级 |
| 归属场景包 / 目录 | 否 | 推断 | 如 `skills/meta/`、`skills/writing/blog/` |
| 是否含脚本 | 否 | 无脚本 | 有则须给出子命令与依赖清单 |
| 产物形态 | 否 | 文本交付 | 文件命名与保存位置要写死 |
| 创作者署名 | 否 | 仓库默认 | `metadata.author` 填谁 |

必需项缺失时**在一次提问里问齐 5 个问题**，不要来回追问：

> 请提供：① 这个技能解决什么具体问题（举一个真实触发场景）？② 什么时候该触发、
> 什么时候绝对不该？③ 需要脚本吗（有则说明输入输出）？④ 产出物长什么样（文件名+
> 存放位置）？⑤ 失败了怎么办（重试 / 降级 / 停下问人）？

## 前置自检

逐条执行，任一失败 → 按处置动作做，然后 STOP：

```bash
# 1. Python 3 可用（仅含脚本的技能需要）
python3 --version
# 预期：Python 3.8+。失败→纯提示型技能可继续；脚本型技能 STOP。

# 2. 目标目录尚不存在（避免覆盖别人的技能）
ls skills/<category>/<skill-name> 2>/dev/null || echo "OK-NEW"
# 预期：打印 OK-NEW。失败→目录已存在，问用户是「改名新建」还是「改造现有」，不要直接覆盖。

# 3. 名称未被仓库占用
grep -rn "^name: <skill-name>$" skills/ | head
# 预期：无输出。失败→换名，避免与既有技能同名（同名会导致 pack 引用二义）。
```

## 工作流

### 步骤 1：需求澄清（一次性问齐 5 问）

- **动作**：把上表「输入清单」的 5 问模板原样发出。用户答不全时，对缺项**自行给出带标记的默认值**（写成 `[待确认] 默认 X`），不要阻塞。
- **预期**：得到 5 个答案或带标记的默认值。
- **若失败**：用户只说了「做个技能」而无内容 → 复述模板并明确「没有 ① 我无法动笔」，STOP。

判定「值得做成技能」的三条：能被多次复用、有明确触发语、有可观察的完成态。缺任一条，建议改为写进现有技能的 `references/`。

命名自检的口诀：**读一遍名称，能猜出触发语才算合格**。`excel-merger` 会被「合并这几个表格」触发；`data-helper` 不会，因为没有模型会去检索这个词。

### 步骤 2：命名与描述

- **动作**：名称用 kebab-case 的**可检索动作短语**（`pdf-table-extractor` ✓、`helper` ✗、`utils` ✗）。description 写全四段：做什么 + 英文 `Use when` + 中文触发 + `Do NOT use for` 排除项；中英双语触发词 **≥5 个**。
- **预期**：名称匹配 `^[a-z0-9]+(-[a-z0-9]+)*$` 且与目录名逐字相同；description ≥40 且 ≤1024 字符。
- **若失败**：自检命令 `python3 skills/meta/skill-linter/scripts/lint_skill.py <技能目录>` → 按输出的 `FIX:` 行逐条改。

### 步骤 3：骨架生成

- **动作**：复制 `references/skill-template.md`，填空。10 个 H2 标题必须齐全且用中文：`## 输入清单`、`## 前置自检`、`## 工作流`、`## 交付标准`、`## 失败处置表`、`## 参考`（其余按模板）。frontmatter 机器层字段用英文，正文用中文。
- **预期**：文件行数 150-190；每个步骤含「动作 / 预期 / 若失败」三件套。
- **若失败**：不足 150 行通常是步骤缺失败分支；超过 190 行通常是把知识塞进正文——把细节移入 `references/`。

常见的四种骨架变体（选一个，不要自创第七节）：

| 变体 | 追加章节 | 适用 |
|---|---|---|
| 平台发布型 | `## 参数速查表` + `## 平台特化 Prompt` | 一平台一技能，有凭据与限流 |
| 工具封装型 | `## 命令速查表` | 包一个 CLI，纯执行 |
| 审计评分型 | `## 评分维度表` | 只报告不修改，如 skill-linter |
| 编排型 | `## 依赖技能表` | 串起多个技能，本身不干活 |

### 步骤 4：脚本设计（仅脚本型技能）

- **动作**：为脚本定 argparse 子命令，且**默认 dry-run**（真正写盘/发布/删除必须显式 `--execute` 或 `--confirm`）；启动时检测依赖并给出安装提示；纯函数与 I/O 分离，便于单测。
- **预期**：`python3 scripts/<name>.py --help` 能列出全部子命令；每个子命令都有 `--dry-run`。
- **若失败**：脚本引入非 stdlib 依赖 → 优先改回 stdlib；确需依赖则在 `compatibility` 里写明并加检测。

### 步骤 5：自检

- **动作**：跑 `python3 skills/meta/skill-linter/scripts/lint_skill.py <技能目录>`，并逐条过下面的十诫。
- **预期**：`RESULT: PASS（无 FAIL）`；FAIL 数为 0。
- **若失败**：有 FAIL → 按 `FIX:` 行改完再跑，未清零前不得称「完成」；只有 WARN → 在交付说明里列出并解释保留原因。

## 十诫（正文写作，硬性）

| # | 诫条 | 判据（怎么算违反） |
|---|---|---|
| 1 | **零隐性假设** | 出现「显然 / 众所周知 / 常规操作」，或没写错误原文长相 |
| 2 | **一次性问齐** | 输入清单存在必需项，却没有一次问齐的追问模板 |
| 3 | **红线内联** | 有写操作却没写「默认 dry-run」或「不可逆操作先确认」 |
| 4 | **每步给动作+预期+若失败** | 任一步骤缺三者之一 |
| 5 | **正文 <200 行** | 行数超限，说明该拆技能或该移入 references |
| 6 | **正文全中文** | 正文出现成段英文说明（术语、frontmatter、代码除外） |
| 7 | **frontmatter 机器层英文** | `name` 或 `description` 整段中文，模型路由会退化 |
| 8 | **参考资料署名** | `references/` 有文件但无 `sources-and-methodology.md` |
| 9 | **dry-run 默认** | 脚本型技能里写操作是默认行为 |
| 10 | **可验证产出** | 交付标准没写文件名格式、存放位置、完整性判据 |

第 3、9 诫是安全红线，允许用硬禁令，其余以「讲 why」为主：写清原因，模型才能在未预见的边缘情况下自行判断。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| 用户给的是一类需求（「做所有事」） | 技能粒度过大 | 拆成 2-3 个单场景技能，先写触发最明确的那个 |
| 名称被仓库占用 | 同名会导致 pack 引用二义 | 加限定词（`pdf-table-extractor`→`pdf-invoice-table-extractor`） |
| 描述写不出排除项 | 触发边界还没想清 | 问「什么请求看着像但不该走这个技能」，答案就是排除项 |
| 步骤写了却没有可观察预期 | 违反诫 2/4 | 把预期改成可执行判据（退出码 / 文件存在 / 字段值） |
| 行数 >190 | 知识塞进了正文 | 移入 `references/<topic>.md`，正文只留一句「何时读它」 |
| 脚本需非 stdlib 依赖 | 换环境即坏 | 改回 stdlib；确需则写入 `compatibility` 并加启动检测 |
| linter 报 DESCRIPTION-SHORT | 描述不足以路由 | 补触发词与排除项，凑到 ≥40 字符且含 `Use when` |

## 交付标准

- 成功定义：目标目录内 `SKILL.md` 存在，linter 无 FAIL，十诫自查逐条通过。
- 产物命名：`skills/<category>/<skill-name>/SKILL.md`；脚本放同目录 `scripts/`；引用文档放 `references/`。
- 完整性验证：`wc -l SKILL.md` 落在 150-190；`grep -c "^## " SKILL.md` ≥6；`ls references/sources-and-methodology.md` 非空。
- 交付说明里必须显式列出：路径、行数、linter 结论、保留的 WARN 及理由。

写完后不要顺手去改 `manifest.json` 或 `packs/*/pack.json`——装载关系属于发布流程，与技能本体分开提交，避免一个 PR 里混入两种变更意图。

一个合格产出示例：需求「把表格截图转成 CSV」→ 名称 `table-image-to-csv` → description 含 `Use when` + 「表格转 CSV / 图片转表格」+ 排除「手写 CSV 解析」→ 骨架用工具封装型 → 脚本 `table_convert.py` 带 `--dry-run` 默认 → linter 无 FAIL。

## 参考

- references/skill-template.md —— 可直接填空的 SKILL.md 模板（含 frontmatter 全字段与十诫骨架）；步骤 3 落字前先读。
- references/sources-and-methodology.md —— 本技能方法论出处与原创性声明；被问「依据是什么」时读。
