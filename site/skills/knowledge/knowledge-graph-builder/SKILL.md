---
name: knowledge-graph-builder
description: >
  Turn a folder of markdown notes into an explicit knowledge graph: extract
  entities and relations into nodes plus edges, export as JSON, Graphviz DOT,
  or Mermaid, and compute structural metrics such as degree centrality,
  connected components, and isolated nodes. Use when the user asks to
  构建知识图谱 / 把笔记变成图 / 抽取实体关系 / 导出 graphviz 或 mermaid 图 /
  找出笔记里的孤立节点 / 分析笔记关联结构 / build a knowledge graph /
  extract entities and relations / map my notes / find isolated notes. Do NOT
  use for indexing or searching a note vault (use personal-wiki), for extracting
  durable facts into agent memory (use memory-extractor), or for drawing
  architecture diagrams (use arch-diagram).
license: Apache-2.0
compatibility: 需要 python3 3.8+；脚本纯标准库。渲染 DOT 需本地 graphviz（可选，校验用）。
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: knowledge
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Knowledge Graph Builder（知识图谱构建）

把一堆 Markdown 笔记变成一张**节点 + 边**的图：笔记是节点，`[[双链]]` 是边，
加粗词作为候选概念实体参与连边。产出三种可消费的形态——
JSON 给程序、DOT 给 graphviz、Mermaid 给文档——再配一组图指标
（度中心性、连通分量、孤立节点）回答问题：**这套笔记的骨架在哪，哪里断了**。

「抽取」这一步用的是**启发式规则**，不是 NLP：`[[链接]]` 即边、H1 即节点标题、
`**加粗**` 即候选实体。所以图的准确度取决于你笔记的书写规范程度——
写之前先读步骤 2 的抽取契约。

本技能**不做**检索与索引（那是 `personal-wiki`），**不做**实体消歧与知识融合
（需要 NLP 模型，本技能刻意不引入），**不画**架构图（那是 `arch-diagram`）。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| 笔记目录 | 是 | — | 递归扫描 `.md`/`.markdown`/`.txt` |
| 导出格式 | 否 | json | `json` / `dot` / `mermaid` 三选一 |
| 是否含候选实体 | 否 | 含 | 加 `--note-only` 只看笔记间的链接骨架 |
| 中心性统计范围 | 否 | 全部节点 | `--notes-only` 时忽略概念节点 |
| 输出路径 | 否 | stdout / `<dir>/graph.json` | 不指定则打到标准输出 |

缺输入时，一次性问齐：

> 请提供：① 笔记目录在哪？② 要什么格式（JSON 给程序 / DOT 给 graphviz /
> Mermaid 贴文档）？③ 只关心笔记之间的链接，还是也要把加粗概念纳进来？
> ④ 有没有已知的孤立笔记想优先排查？

## 前置自检

逐条执行，任一失败 → 按处置动作做：

```bash
# 1. Python 版本
python3 --version
# 预期：Python 3.8+。失败→STOP。

# 2. 脚本可用
# python3 scripts/graph_build.py --help >/dev/null && echo "script ok"
# 预期：script ok。失败→核对 scripts/ 路径。

# 3. 目录里有可解析的笔记
find <notes-dir> -name "*.md" -not -path "*/.*" | head -5
# 预期：至少 1 个文件。失败→脚本会报「没有找到 Markdown 笔记」，先确认路径。

# 4. 可选：graphviz 是否在本地（只影响 DOT 转图，不影响导出）
which dot >/dev/null && echo "graphviz ok" || echo "no graphviz（DOT 仍可导出，交给用户渲染）"
```

## 工作流

### 步骤 1：确认笔记的书写规范

图的形状完全由笔记的书写方式决定，抽取契约如下：

| 笔记里的写法 | 抽成什么 | 说明 |
|---|---|---|
| `# 标题`（首个 H1） | note 节点的 `label` | 没有 H1 则退回文件名 |
| 文件路径 | note 节点的 `id` | 唯一标识，相对目录 |
| `[[目标]]` / `[[目标\|显示]]` | note → note 的边（`rel=links`） | 目标按文件名或 H1 标题解析 |
| `**加粗词**` / `__加粗词__` | note → concept 的边（`rel=mentions`） | 跨笔记同名加粗词合并为同一概念中枢 |
| 代码块 / 行内代码里的内容 | **不抽取** | 避免把 `foo_bar()` 当概念 |

- **预期**：用户的笔记里至少有一处 `[[链接]]`，否则图会是全孤立节点。
- **若失败**：笔记完全没有链接 → 图仍然能出（只有 concept 边），
  但要如实告诉用户「这只反映了加粗词共现，不是笔记间关系」。

### 步骤 2：抽取图数据

```bash
python3 scripts/graph_build.py extract assets/sample-notes   # 随包样例笔记；你的库换成 notes/
```

产出 `<notes-dir>/graph.json`，含 `nodes` / `edges` / `meta` / `unresolved_links`。

- **预期**：输出 `nodes`（note / candidate 分列）、`edges`、`unresolved` 计数，
  并逐条打印节点与未解析链接。示例：`nodes: 13 (note 5 / candidate 8)`。
- **若失败**：`unresolved` 不为 0 说明有 `[[链接]]` 指向不存在的笔记——
  这是**内容问题不是脚本问题**，转述给用户决定「补笔记」还是「删链接」。

### 步骤 3：导出为目标格式

```bash
# 贴进 Markdown 文档（最常用）
python3 scripts/graph_build.py export assets/sample-notes --format mermaid --note-only

# 交给 graphviz 出矢量图
python3 scripts/graph_build.py export assets/sample-notes --format dot --out graph.dot   # 随包样例
dot -Tsvg graph.dot -o graph.svg

# 给下游程序
python3 scripts/graph_build.py export assets/sample-notes --format json --out graph.json
```

导出器已处理两个易踩的坑：Mermaid 的节点 id 一律重写为 `n0`、`n1`…
（路径里的 `/`、`.` 会破坏 Mermaid 语法），原始标题放在方括号里；
DOT 的标题做了引号转义。

- **预期**：Mermaid 输出以 ` ```mermaid ` 开头、`flowchart LR` 起图、` ``` ` 收尾，
  可直接贴进 Markdown 渲染；DOT 输出以 `digraph knowledge {` 开头。
- **若失败**：Mermaid 若超过 `--max-edges`（默认 200）会截断并插入
  `%% ... 已截断` 注释；图太大时改用 `--note-only` 或调高上限。

### 步骤 4：分析图指标

```bash
python3 scripts/graph_build.py analyze <notes-dir> --top 10
```

输出四组信息，并给一句**可执行的诊断结论**：

- **度中心性 top N**：`degree` 是连边数，`centrality = degree / (N-1)`（归一化）。
  排在前面的就是这套笔记的枢纽概念。
- **连通分量**：按规模降序。分量数 >1 说明笔记分成几块互不相通。
- **孤立节点**：度为 0，既不是任何笔记的邻居也没连出去。
- **诊断行**：三种结论之一（无任何连边 / 图分裂 N 块 / 单一连通分量）。

- **预期**：中心性列表带条形图与节点类型标注；诊断行给出下一步动作。
- **若失败**：概念节点挤占榜单 → 加 `--notes-only` 只看笔记；
  或 `--top 20` 扩大视野。

### 步骤 5：交付并给改进建议

交付时说明四件事：图文件路径与格式、节点/边规模、**中心性最高的 2-3 个节点**
（即这套笔记的主题骨架）、以及孤立节点清单与补救建议。

典型建议：孤立笔记要么补一条 `[[链接]]` 接进主图，
要么承认它确实是独立话题；两者都是合理结论，但要说清楚。

- **预期**：用户拿到图文件 + 一段能据以行动的结论（骨架节点、断裂处、补链清单）。
- **若失败**：`extract` 与 `analyze` 的 `nodes` 数不一致 → 两次扫描间笔记被改动，
  重跑一次对齐后再交付；`unresolved_links` 非空且用户不打算补笔记 → 在图里保留这些
  断边但在交付说明中逐条列出，不要静默丢弃。

## 交付标准

- 产物：至少一份 `graph.json`；按用户需要在 Mermaid / DOT 中再出一到两种。
- 位置：`extract` 默认写 `<notes-dir>/graph.json`；`export` 未给 `--out` 时打到 stdout。
- 完整性验证（至少做前两条）：
  - `analyze` 输出的 `nodes` 数等于 `extract` 的 `nodes` 数（两次扫描同一目录应一致）；
  - Mermaid 输出的节点声明数 + 边数等于 `analyze` 报的规模；
  - `meta.unresolved_links` 的每一条都在交付说明里被提及。
- `graph.json` 是生成物，提醒用户**不要手改**（重跑 `extract` 会覆盖）。

## 失败处置表

| 现象 / 错误 | 原因 | 处置 |
|---|---|---|
| `目录不存在：...` | 路径拼错或目录未建 | 核对路径；笔记目录不存在时不必先建空目录 |
| `... 下没有找到 Markdown 笔记` | 目录为空，或后缀不在白名单 | 确认有 `.md`；`.txt` 也在白名单内，其余后缀不支持 |
| 所有节点 degree=0 | 笔记之间没有任何 `[[链接]]` | 正常输出，但要说明「这不是关联分析，只是共现」 |
| 概念节点霸榜、看不到笔记 | 加粗词形成的 concept 节点度数天然偏高 | 用 `--notes-only` 把中心性限制在笔记上 |
| Mermaid 贴进文档不渲染 | 用了 `export --format json` 的输出，或截断注释位置异常 | 必须用 `--format mermaid`；确认首行是 ` ```mermaid ` |
| Mermaid 图太密看不清 | 边数上百，Mermaid 自动布局会糊成毛线团 | 加 `--note-only`，或 `--max-edges 30` 只看最相关的边 |
| 加粗词没被抽成实体 | 加粗跨行（`**` 与 `**` 不在同一行），或超过 40 字符 | 加粗限制在单行内且不超过 40 字符；代码块内的加粗被刻意忽略 |
| `[[链接]]` 明明写了却 unresolved | 目标名与「文件名 / H1 标题」都对不上（大小写不敏感，但错别字不认） | 修正链接文字，或在 `personal-wiki` 里先补出这篇笔记 |
| DOT 转 SVG 报语法错 | 标题含未转义字符（脚本已转义 `"` 与 `\`） | 若仍失败，用 `--note-only` 缩小图，把出错的 `.dot` 全文附给用户 |

## 参考

- `references/sources-and-methodology.md` —— 抽取启发式的设计理由、图指标的
  定义与出处、与既有工具（Zettelkasten 双链、图数据库导入格式）的借鉴关系。
- `scripts/graph_build.py --help` —— 三个子命令与全部参数。
- 相关技能：`personal-wiki`（先把知识库建起来，再来抽图）、
  `memory-extractor`（把稳定结论固化进 agent 记忆）。
