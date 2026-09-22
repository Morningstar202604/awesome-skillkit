---
name: skill-linter
description: >
  Check a single SKILL.md or a whole skills directory against the
  awesome-skillkit spec and print a PASS/WARN/FAIL report with an explicit
  fix line per problem: frontmatter blocks, name/directory sync, description
  routing, the ten-section skeleton, line count, CJK body ratio, reference
  existence, and failure-table depth. Use when the user asks to 校验技能 /
  检查技能合不合规 / lint 这个 SKILL.md / 技能体检 / lint a skill /
  validate skill spec / check if my skill is compliant. Do NOT use for
  creating a new skill (that is skill-author) or for grading documentation
  quality beyond spec compliance.
license: Apache-2.0
compatibility: Requires python3 (stdlib only); run from the repository root.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: meta
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Skill Linter（技能规范校验）

对 SKILL.md 做八项静态检查，把「这份技能合不合规范」变成一条退出码：有 FAIL 时返回 1，可直接挂进 CI 或 pre-commit。只报告、给出修法，**不代改文件**。

与同包技能的边界：`skill-author` 负责从零生成，`skill-finder` 负责检索装配；本技能只判定规范符合性。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 检查目标 | 是 | — | `SKILL.md` 路径 / 单个技能目录 / 含多个技能的父目录 |
| 输出格式 | 否 | 文本 | 加 `--json` 得机器可读报告 |
| 是否看 PASS 明细 | 否 | 只看 WARN+FAIL | 加 `--verbose` 打印全部八项结论 |

必需输入缺失时一次性问齐：

> 请提供：① 要检查的路径（可以是 `skills/meta/skill-linter` 这样的目录，也可以直接给
> `SKILL.md`）。可选告知：② 是否需要 JSON 输出（默认否）、③ 是否需要看到通过的检查项（默认否）。

## 前置自检

逐条执行，任一失败 → 按处置动作做，然后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。失败→安装 Python 3 后重试；本脚本不用任何第三方库。

# 2. 脚本存在
ls skills/meta/skill-linter/scripts/lint_skill.py
# 预期：打印该路径。失败→确认当前在仓库根目录，路径用仓库相对路径。

# 3. 目标路径存在
ls <目标路径>
# 预期：列出文件或目录。失败→脚本会以退出码 2 结束并打印「路径不存在」，向用户确认路径后 STOP。
```

## 工作流

### 步骤 1：单技能体检

```bash
python3 skills/meta/skill-linter/scripts/lint_skill.py .   # 单技能自检（在技能目录内运行）：预期 RESULT: PASS、退出码 0
```

- **动作**：`python3 skills/meta/skill-linter/scripts/lint_skill.py <技能目录> --verbose`
- **预期**：八行 `PASS/WARN/FAIL` 结论 + 末行 `RESULT: PASS`；退出码 0。
- **若失败**：末行 `RESULT: FAIL` 或退出码 1 → 逐条读 `FIX:` 行，按修法改文件；**必须在同一目标上复跑到 0 FAIL 才算完成**。

### 步骤 2：目录树批量体检

- **动作**：`python3 skills/meta/skill-linter/scripts/lint_skill.py skills/ > lint-report.txt`
- **预期**：报告列出仓库内全部技能，末行给出 `skills: N  FAIL: X  WARN: Y`；退出码在 X=0 时为 0。
- **若失败**：退出码 2 且提示「未找到任何 SKILL.md」→ 目标路径写错了，或传入的目录下没有技能；用 `ls <目标>` 复核。

### 步骤 3：CI 门禁接入

- **动作**：把退出码当判据，只对变更的技能跑：
  ```bash
  for d in $changed_skill_dirs; do
#     python3 skills/meta/skill-linter/scripts/lint_skill.py "$d" --json > /dev/null || exit 1
  done
  ```
- **预期**：任一技能有 FAIL 时该步骤退出码非 0，CI 失败。
- **若失败**：`--json` 输出的 `skills[].findings[]` 中 `level == "FAIL"` 的条目即门禁拦截原因；打印它们作为 PR 评论。

### 步骤 4：解读报告

- **动作**：按检查项分类归因，`FAIL` 必须修，`WARN` 由作者判断。
- **预期**：每个非 PASS 项都有对应 `FIX:` 行。
- **若失败**：无 `FIX:` 行 → 属脚本缺陷，记录目标路径与检查项名反馈给 `skill-author` 的维护者，不要静默忽略。

## 检查项与判定规则

| 检查项 | 判定规则（怎么算过） | 不过时报什么 | 建议修法 |
|---|---|---|---|
| `FM-FIELDS` | frontmatter 由 `---` 起止且可解析，含 name/description/license/metadata 四块；description 长度 40-1024 | 缺项报 FAIL，长度越界报 WARN | 按 `skill-template.md` 补字段 |
| `NAME-SYNC` | `name` 与目录名逐字相同、全小写、匹配 `^[a-z0-9]+(-[a-z0-9]+)*$` | FAIL | 改名或改目录名，二者必须一致 |
| `DESC-ROUTE` | description 含 `Use when`（或「当用户/何时使用/触发」）与 `Do NOT`（或「排除/不适用」），且触发词 >=5 个 | FAIL，并报实际触发词数 | 在引导语后用 `/` 补中英触发短语 |
| `BODY-SECTS` | 六个硬性 H2 齐全（输入清单/前置自检/工作流/交付标准/失败处置表/参考）；H2 总数 10 为推荐 | 缺硬性项 FAIL；总数 <10 WARN | 按骨架补章节 |
| `BODY-LINES` | 总行数 < 220 | WARN | 领域知识移入 `references/` |
| `LANG-CJK` | 正文去掉围栏代码块后，CJK 字符数 / 非空白字符数 >= 0.15 | WARN「正文疑似应为中文」 | 叙述段落改中文，frontmatter 与代码保持英文 |
| `REF-EXISTS` | 正文中每个 `references/<文件名>.md` 在该技能目录下真实存在 | 断链报 FAIL | 建文件或删引用 |
| `FAIL-TABLE` | `## 失败处置表` 下表格数据行 >= 4（已扣表头与分隔行） | FAIL，并报实际行数 | 补真实失败场景与错误原文 |

触发词计数口径：取 `Use when` / `当用户` / `触发` 之后的片段，到排除项或句末截断，按 `/`、`、`、逗号或 `or` 切分，片段长度 >=2 计入。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `<target>` | 文件或目录路径 | 位置参数；给 `SKILL.md`、技能目录、或父目录均可 |
| `--json` | 布尔 | 输出含 `skills[].findings[]` 与 `summary` 的 JSON |
| `--verbose` | 布尔 | 文本模式也打印 PASS 行，共八项 |
| 退出码 | 0 / 1 / 2 | 0 无 FAIL；1 有 FAIL；2 路径不存在或未找到 SKILL.md |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| 退出码 2 + 「路径不存在」 | target 写错或不在当前工作目录 | 用 `ls` 复核路径；仓库内一律用仓库相对路径 |
| 退出码 2 + 「未找到任何 SKILL.md」 | 目标目录下确实没有技能 | 确认是否写成了技能目录的父级之上的层；重跑一次带 `--verbose` 定位 |
| `FM-FIELDS` 全红 | 文件首行不是 `---`，或 YAML 缩进被破坏 | 用 `skill-template.md` 前 15 行替换 frontmatter |
| `NAME-SYNC` 报目录名不一致 | 技能被改名但只改了目录或只改了字段 | 二者取其一统一：建议改目录名（引用路径随之更新） |
| `LANG-CJK` 报占比过低 | 正文是英文或几乎全是代码 | 正文改中文；若确为纯代码技能，在交付说明里保留该 WARN 并说明 |
| `REF-EXISTS` 报断链 | 引用了尚未创建的参考文档 | 建 `references/<name>.md`，或从 `## 参考` 删除该行 |
| `FAIL-TABLE` 行数不足 | 只写了表头或两条泛泛之谈 | 补到 4 条以上，每条含错误原文与具体处置动作 |
| 报告与仓库门禁 `validate_skills.py` 结论冲突 | 两者检查集不同（仓库门禁查 pack 一致性与 500 行硬限） | 以仓库门禁为合并判据，本技能为技能级自律线；两者都跑 |

## 交付标准

- 成功定义：目标技能上 `FAIL` 数为 0；批量模式下 `RESULT: PASS`。
- 产物：默认把报告打到 stdout；需留档时重定向为 `lint-report-<YYYYMMDD>.txt`，或 `--json` 输出重定向为 `lint-report-<YYYYMMDD>.json`。
- 存放位置：仓库外或用户指定路径，不要污染技能目录（`skills/**` 下只放技能自身文件）。
- 完整性验证：报告末行必须含 `skills:` / `FAIL:` / `WARN:` 三个计数；缺一说明输出被截断。

## 与仓库门禁的关系

本技能是**技能级自律线**，仓库根 `tools/` 下的仓库级校验器是**合并门禁**，两者检查集不同，都要跑：

| 维度 | 本技能（skill-linter） | 仓库级校验器 |
|---|---|---|
| 行数上限 | 220 行报 WARN | 500 行报 ERROR |
| 检查粒度 | 单技能，可离线自测 | 全仓 + pack ↔ 磁盘一致性 |
| 触发词计数 | 有（>=5） | 只查是否含触发语提示词 |
| 骨架章节 | 检查六个硬性 H2 | 不检查 |
| 输出 | PASS/WARN/FAIL + FIX 行 | `[ OK ]` / `[ERR ]` 表格 |

结论冲突时以仓库门禁为合并判据；本技能的价值在于**在提交前**给出更细的修法提示与更严的行数自律线。

## 常见错误

| 现象 | 原因 | 处置 |
|---|---|---|
| NAME-SYNC FAIL 且目录名显示为空 | 目标写成了 `.` 而未 resolve | 传具体技能目录，或升级到已修复版脚本 |
| BODY-SECTS WARN 差 1 个 H2 | 只写了六个硬性章节 | 补参数速查表 / 常见错误等可选章节 |
| DESC-ROUTE FAIL 触发词不足 | description 缺 Use when 列表 | 补 ≥5 个触发词与 Do NOT 排除项 |

## 参考

- `references/check-rules.md` —— 八项检查的完整判定口径与边界用例（含误报排查）；对某条结论有疑问时读。
- `references/sources-and-methodology.md` —— 方法论出处与原创性声明；被问「规则哪来的」时读。
