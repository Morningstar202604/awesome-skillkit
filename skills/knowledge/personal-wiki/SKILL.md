---
name: personal-wiki
description: >
  Build and maintain a personal markdown wiki with a two-layer raw/notes
  layout, then index, full-text search, lint, and report on it. Turns loose
  clippings into a linked, tagged, searchable knowledge base and surfaces
  orphan notes, broken wiki links, and empty stubs. Use when the user asks to
  建个人知识库 / 搭个 wiki / 整理我的笔记 / 笔记之间建立双链 / 检索我的笔记库 /
  build a personal wiki / organize my notes / find orphan notes / search my
  note vault. Do NOT use for extracting durable facts into agent memory
  (use memory-extractor), for building an entity-relation graph with metrics
  (use knowledge-graph-builder), or for publishing notes as a website.
license: Apache-2.0
compatibility: 需要 python3 3.8+；本技能脚本只用标准库，无第三方依赖。
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: knowledge
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Personal Wiki（个人知识库构建）

把散落的剪藏与草稿收进一个**两层**的知识库：`raw/` 放原始资料（只进不改），
`notes/` 放你编译过的笔记（带 `[[双链]]` 与 `#标签`），再由一个 JSON 索引把两者串起来。
核心判断是：**原始资料与你的结论必须分开放**——混在一起，索引就无法区分
「作者说的」和「我想到的」，检索权重也失去意义。

本技能负责目录管理、索引、检索与体检，**不负责**把知识提炼进 agent 长期记忆
（那是 `memory-extractor`），也**不做**实体关系图与中心性分析（那是 `knowledge-graph-builder`）。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| wiki 根目录 | 是 | — | 不存在则创建；已初始化过则复用 |
| 资料源 | 是 | — | 剪藏/草稿所在位置，或「从零开始写」 |
| 已有笔记的命名习惯 | 否 | 文件名即 slug | 影响链接解析：按文件名还是按 H1 标题匹配 |
| 标签体系 | 否 | 自由标签 | 已有分类法则沿用，避免同义标签分裂 |
| 检索诉求 | 否 | 全文检索 | 需要「只看标题命中」时说明 |

缺输入时，一次性问齐（不要挤牙膏式追问）：

> 请提供：① wiki 放哪个目录？② 现有资料在哪（或者从零开始写）？
> ③ 你希望链接按文件名还是按 H1 标题解析？④ 有既定标签体系吗？
> ⑤ 检索时最常找什么（标题 / 标签 / 正文）？

## 前置自检

逐条执行，任一失败 → 按处置动作做：

```bash
# 1. Python 版本（脚本要求 3.8+，用到 pathlib.rglob 与 f-string）
python3 --version
# 预期：Python 3.8+。失败→STOP，本技能脚本无法运行。

# 2. 脚本在位且可执行
python3 scripts/wiki_build.py --help >/dev/null && echo "script ok"
# 预期：打印 script ok。失败→确认路径，脚本与 SKILL.md 同级放在 scripts/ 下。

# 3. 目标目录状态（区分「新建」与「复用」）
ls -d <wiki-dir> 2>/dev/null && ls <wiki-dir> || echo "OK-NEW"
# 预期：OK-NEW 走 init；已存在且含 notes/ 走 index，不要重新 init。
```

## 工作流

### 步骤 1：初始化目录骨架

```bash
python3 scripts/wiki_build.py init <wiki-dir>
```

产出 `raw/`、`notes/`、`index.json`、`README.md` 四件套，并立刻建立一次空索引。

- **预期**：输出 `initialized: <绝对路径>` 与四个条目；`find <wiki-dir>` 能看到 `raw/`、`notes/`。
- **若失败**：若报「目录非空」→ 这是防覆盖保护。先确认目标目录里有没有用户的既有笔记；
  确实要在此目录初始化时才加 `--force`，**空目录不要加**。

### 步骤 2：归置资料（raw / notes 分流）

这是本技能唯一需要人工判断的一步：

| 资料性质 | 去处 | 理由 |
|---|---|---|
| 网页剪藏、论文原文、别人说的话 | `raw/` | 只索引不参与 lint，允许零散、允许无链接 |
| 你自己的总结、结论、待办 | `notes/` | 参与孤儿/断链/空笔记检查 |
| 复制来的长文 + 你划的重点 | 拆两份 | 原文进 `raw/`，重点进 `notes/` 并链回原文 |

笔记写法约定（解析器按此工作）：

```markdown
# 向量检索                        <- 首个 H1 就是标题，检索权重最高

把文本编码成向量后找近邻，是 [[RAG 架构]] 的召回环节。   <- [[双链]] 建立关系

与 [[倒排索引]] 互补。           <- 目标可以是文件名，也可以是别人的 H1

#检索 #基础设施                    <- #标签 用于分类
```

- **预期**：`notes/` 下每篇都有唯一 H1；需要关联的地方写了 `[[目标]]`。
- **若失败**：笔记没有 H1 → 解析器退回文件名当标题，不报错但标题质量差；
  统一补 H1 后重跑步骤 3。

### 步骤 3：重建索引

```bash
python3 scripts/wiki_build.py index <wiki-dir>
```

扫描两个目录，抽取标题 / 标签 / 字数 / 链接关系，写回 `index.json`。
**每次改完笔记都要重跑**，检索与体检都读这份索引。

- **预期**：输出 `pages`（notes/raw 分列）、`tags` 数、`links` 的 resolved / unresolved 计数，
  以及逐页清单，每行形如 `- [notes] 向量检索 (98w, 2 tags, 2 out)`。
- **若失败**：`unresolved` 不为 0 是**正常**的（先写链接再补笔记很常见）；
  但若 resolved 为 0，说明链接语法写错了——检查是否用了全角方括号 `【【】】`。

### 步骤 4：检索

```bash
python3 scripts/wiki_build.py search <wiki-dir> "关键词"
```

排序权重：**标题命中 10 分 > 标签命中 5 分 > 正文命中 1 分**，同词出现多次按次数累加。
这个权重是刻意的：标题命中说明这篇笔记**主题就是**这个词，比正文里顺带提一句重要得多。

- **预期**：输出命中数与逐条得分，每条形如 `14  [notes] 向量检索` 加一行 `(title×1, body×4)`。
- **若失败**：命中为 0 → 先确认词是否已入库（跑 `index`）；
  中文检索是**子串匹配**，搜「向量」能命中「向量检索」，但搜「检索向量」不会命中。

### 步骤 5：体检

```bash
python3 scripts/wiki_build.py lint <wiki-dir>
```

检查四类问题：**孤儿笔记**（无入链，检索也走不到）、**断链**（`[[目标]]` 解析不到）、
**空笔记**（正文不足 5 词）、**无标签笔记**（提示级，不算错误）。

- **预期**：分节列出四类问题；全部干净时每节打印 `(无)`。
- **若失败**：退出码 1 表示**有发现**（不是脚本出错）——这是给 CI 用的信号，
  有人为误报时按下方失败处置表处理。

### 步骤 6：出统计并交付

```bash
python3 scripts/wiki_build.py stats <wiki-dir>
```

输出笔记数、总字数、平均每篇链接数（出入链合计）、标签分布 top 10（带条形图）。

交付时向用户说明三件事：wiki 绝对路径、当前笔记数与链接密度、
`lint` 里未修的每一类问题及原因。后续维护只需重复「改笔记 → `index` → `lint`」，
不需要重新 `init`。

## 交付标准

- 产物：一个已初始化的 wiki 目录 + 一份 `index.json`，索引与磁盘内容一致。
- 位置：用户指定目录；未指定时用当前目录下的 `wiki/`。
- 完整性验证（至少做前两条）：
  - `index` 输出的 `pages` 数等于 `find <dir>/notes <dir>/raw -name "*.md" | wc -l`；
  - `stats` 的 `generated_at` 是刚跑的时间戳；
  - `lint` 的每一类问题都有明确的「已修 / 待修 + 原因」交代。
- `index.json` 是生成物，交付说明中要提醒用户**不要手改**（下次 `index` 会覆盖）。

## 失败处置表

| 现象 / 错误 | 原因 | 处置 |
|---|---|---|
| `目录非空：...；确认要初始化请加 --force` | init 的防覆盖保护 | 确认目录里没有用户的既有笔记；是空壳再加 `--force` |
| `目录不存在：...（先跑 init）` | 对未初始化的路径跑了 index/search | 先 `init`，或核对路径拼写 |
| `索引不存在：...（先跑 index）` | 手工删了 index.json 后直接 search | 重跑 `index`；search 只读索引 |
| `索引损坏（...）` | index.json 被手工编辑或写入中断 | 删掉 `index.json` 后重跑 `index`，不要去修 JSON |
| resolved 为 0 但明明写了链接 | 用了全角括号 `【【】】` 或全角竖线 `｜` | 换成半角 `[[目标]]` / `[[目标\|别名]]` 后重跑 index |
| 大量笔记被判孤儿 | 链接方向写反（A 链了 B，但你以为 B 会链回 A） | 孤儿判定只看**入链**；在相关笔记里补出链，或接受它本就是独立笔记 |
| `#标签` 没被识别 | `#` 后紧跟数字（如 `#1`），或前面紧挨字母（`a#b`） | 标签须以字母或中文开头；数字开头的改用 `#v2` 这类形式 |
| 中文标签在 stats 里错位 | 早期版本用 `len()` 对齐全角字符 | 用显示宽度对齐的版本；若仍错位说明终端字体非等宽 |
| lint 退出码 1 让 CI 挂掉 | 退出码表示「有发现」而非「出错」 | 在 CI 里用 `\|\| true` 包裹，或先清零孤儿与断链 |

## 参考

- `references/sources-and-methodology.md` —— 方法论出处、Zettelkasten / 双链笔记的
  公开理念借鉴与原创性声明；被问「这套结构依据是什么」时读。
- `scripts/wiki_build.py --help` —— 五个子命令与其参数。
- 相关技能：`memory-extractor`（提炼长期记忆）、`knowledge-graph-builder`（实体关系图）。
