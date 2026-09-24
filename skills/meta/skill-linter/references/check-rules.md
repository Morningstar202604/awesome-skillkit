# 八项检查的判定口径与边界用例

本文件是 `scripts/lint_skill.py` 的行为说明书：SKILL.md 里只给了判定规则表，
这里给**实现细节、边界用例与误报排查**。对某条结论有疑问、或要把规则移植到别处时读。

## Table of Contents

- [检查执行顺序](#检查执行顺序)
- [逐项边界用例](#逐项边界用例)
  - [FM-FIELDS](#fm-fields) / [NAME-SYNC](#name-sync) / [DESC-ROUTE](#desc-route)
  - [BODY-SECTS](#body-sects) / [BODY-LINES](#body-lines) / [LANG-CJK](#lang-cjk)
  - [REF-EXISTS](#ref-exists) / [FAIL-TABLE](#fail-table)
- [退出码语义](#退出码语义)
- [扩展新检查项的接入点](#扩展新检查项的接入点)

## 检查执行顺序

脚本对每个 `SKILL.md` 固定按此顺序跑，八项互不依赖：

```
FM-FIELDS → NAME-SYNC → DESC-ROUTE → BODY-SECTS → BODY-LINES
          → LANG-CJK → REF-EXISTS → FAIL-TABLE
```

任一 `FAIL` 都使退出码为 1；`WARN` 不影响退出码。批量模式下统计各技能结论之和。

## 逐项边界用例

### FM-FIELDS

| Input form | Judgment |
|---|---|
| 首行是 `---` 但无闭合 `---` | FAIL（`split_frontmatter` 返回 None） |
| 首行是空行再 `---` | FAIL（要求行 1 恰好是 `---`） |
| `metadata:` 下没有缩进子键 | FAIL（解析结果为空 dict） |
| `description:` 用 `>` 折叠块 | 通过，多行被合并为一行再计长 |
| `description` 长度 39 / 1025 | WARN，仅长度越界报 |

解析器只实现最小 YAML 子集（标量 / 折叠块 / 字面块 / 一层嵌套 map），
**不支持列表、锚点、多行字符串拼接**——技能 frontmatter 用不到，也不该用。

### NAME-SYNC

| Input form | Judgment |
|---|---|
| `name: Skill-Linter` | FAIL：含大写 |
| `name: skill--linter` | FAIL：连续连字符 |
| `name: skill-linter` 但目录是 `skill_linter` | FAIL：目录名不一致 |
| `name: 视频生成` | FAIL：不匹配 kebab-case 正则 |

目录名比对用 `SKILL.md` 的直接父目录名。批量扫描时会跳过 `_common/`、`assets/`、
`templates/`、`__pycache__/` 下的 `SKILL.md`——这些位置的同名文件是示例或共享模块，不是技能本体。

### DESC-ROUTE

- 「何时使用」提示词：`use when` / `use this` / `when the user` / `当用户` / `何时使用` / `触发`。
- 「排除项」提示词：`do not use` / `don't use` / `not for` / `排除` / `不适用` / `不要用于`。
- 触发词计数：取上述「何时使用」引导语之后的文本，遇到排除项提示词或句末即截断；
  按 `/`、`、`、`,`、`，`、`;`、`；`、` or `、` and ` 切分；片段去空白与首尾标点后长度 >=2 才计数。

边界用例：

| description 片段 | 计数 |
|---|---|
| `Use when the user asks to 生成视频 / 做个短视频 / make a video` | 3 |
| `当用户要求 校验技能 / 检查技能合不合规 时使用` | 2 |
| `Use when needed.` | 0（片段 `needed` 只有 1 个词？—— 实际计入 1，缺 4 个） |
| 整段中文但没有 `当用户`/`触发` 引导语 | 0 |

**已知误报**：若把触发词写在 `触发词：` 这类中文引导语之后但用顿号分隔的整句里，
计数会偏高（把描述性短语也算作触发词）。判定以「>=5」为下限，偏高不产生假 FAIL，
故不做额外收紧。

### BODY-SECTS

硬性六项按 `startswith` 匹配 H2 标题，因此 `## 参考` 也能匹配 `## 参考资料`。
H2 总数 >=10 为推荐值，不足只 WARN。

### BODY-LINES

计的是**整个文件行数**（含 frontmatter 与代码块），不是正文字数。空行计入。
和仓库级校验器（仓库根 `tools/` 目录下的 `validate_skills.py`）的 500 行 ERROR 线并存：本脚本的 220 是自律线，
提前预警，避免技能膨胀后才在仓库门禁处被打回。

### LANG-CJK

去围栏代码块 → 去所有空白字符 → 用 `[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]` 计 CJK 字符数 →
除以剩余字符总数。阈值 0.15。

边界：纯英文技能正文占比约 0（必然 WARN）；中英混排且中文为叙述主体通常在 0.35 以上；
本仓库现有技能实测区间约 0.30-0.55。**该检查对纯代码型技能一定有误报**，
此时保留 WARN 并在交付说明里写明理由即可，不要为了消 WARN 去注水中文。

### REF-EXISTS

识别两种写法：反引号内的 `references/<文件名>.md`，以及以它为开头的列表项。
存在性判据是「该技能目录 / 相对路径」为文件。

边界：占位名（常见于写作模板或本节这类说明文字）会被当成真引用而报 FAIL。
**修法**：写成不含 `.md` 后缀的形态，或放进围栏代码块——本检查不看围栏内的内容。

### FAIL-TABLE

取 `## 失败处置表` 到下一个 H2 之间的行；对其中每张三列表格，统计「以 `|` 开头且以 `|` 结尾」的行，
扣掉分隔行与表头。要求数据行 >=4。

边界：表格里换行写的单元格（用 `<br>`）不额外计数；多个表格会分别计数后相加取总值。

## 退出码语义

| 码 | 含义 | CI 处理 |
|---|---|---|
| 0 | 无 FAIL（可能有 WARN） | 放行 |
| 1 | 存在 FAIL | 拦截，打印 `FIX:` 行作为评论 |
| 2 | 路径不存在 / 未找到任何 SKILL.md | 视为配置错误，不要当成技能不合格 |

## 扩展新检查项的接入点

新增一项检查只需三步：写一个 `check_xxx(skill_dir, meta, body_lines, raw)` 函数返回
`Finding` 列表 → 在 `lint_one()` 的检查链里追加 → 在 SKILL.md 的判定规则表里加一行。
`Finding` 的 `fix` 字段**必须非空**（除 PASS 外），否则使用者只能看到问题看不到修法。
