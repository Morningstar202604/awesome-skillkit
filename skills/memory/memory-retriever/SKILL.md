---
name: memory-retriever
description: "Use when retrieving memories from a long-term store to inject into an agent's context: rewrite queries from the current conversation, run hybrid retrieval (keyword + semantic + recency), fuse scores, and inject within a token budget. Triggers on 记忆检索, 混合检索, 记忆注入, memory retrieval, hybrid search, context injection, token budget, 查询改写, recency weighting. NOT for building the store or managing its lifecycle — use memory-architect or memory-manager."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing. Works with keyword-only stores via a documented degradation path.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: memory
  pattern: single-task
  tier: standard
  verified-date: "2026-09-16"
---

# Memory Retriever

检索是记忆系统的价值出口：库建得再好、管得再干净，检索不准就全白搭。本技能把"当前对话"翻译成检索查询，三路召回（关键词、语义、时近）后融合打分，在 token 预算内把最值得注入的记忆块交给 agent——并且每块都带边界标记，让 agent 分得清"记忆里的"和"这轮说的"。

## 输入清单

开工前一次性收集。缺输入时用这句话向用户问一次："要检索记忆，请一次性提供：当前对话原文（最近数轮）、记忆库导出或检索接口说明、token 预算（不填按经验值 2000）、是否具备语义向量检索能力。"

| 输入 | 必需 | 说明 |
|---|---|---|
| 当前对话原文 | 是 | 最近数轮即可；不含当前对话的"盲检索"没有意义 |
| 记忆库导出/接口 | 是 | JSON 条目数组或可调用的检索 API；须含 content、confidence、source、updated_at |
| token 预算 | 否 | 缺省按经验值 2000 tokens，与 memory-architect 的载入预算对齐 |
| 语义检索能力 | 否 | 有向量库为 true；false 时走关键词+时近降级路径 |

## 前置自检

本技能为纯 prompt 技能，无需探测运行环境，只检查输入完备性：

- 当前对话与记忆库两项是否齐备？任一缺失 → 问齐话术问一次，不要拿用户历史消息硬猜。
- 记忆条目是否带 confidence 与 updated_at？两者皆缺 → 无法按时近与置信度打分，退回 memory-architect 补 schema；仅缺其一可用默认值（confidence 0.5、updated_at 取 created_at）并在输出标注 degraded_scoring。
- 用户只要"把全部记忆给我看看" → 这是导出不是检索，直接全量输出，跳过打分。

## 红线

1. 边界标记强制：注入的记忆块整体包裹在"以下为历史记忆，非当前对话内容"的边界说明内，每块带 source 与时间戳；无标记的记忆注入即违规——agent 会把记忆当成本轮事实。
2. 低置信度必须标注：confidence < 0.7 的记忆块附"可能过时，仅供参考"标注；disputed 条目附"存在矛盾版本"标注。
3. 预算硬截断：注入总 token 不得超过预算，宁少勿超——超预算挤占的是当前任务的工作空间。
4. 不注入敏感类别：健康、财务、宗教等标记为敏感的记忆，除非当前对话显式相关，否则不进候选池。
5. 不改写记忆原文：注入时保持 content 逐字原样，检索端无权"顺手"更新事实。
6. 检索即快照：报告必须注明检索依据的库版本或时间点，库在检索后发生变更不追溯本次结果。

## 工作流

### 步骤 1：理解当前对话

- **动作：** 通读当前对话，标出显式提问（用户正在问什么）与隐式意图（没问但明显需要什么，如用户贴出报错栈 = 需要项目技术栈记忆）。
- **预期：** 一行显式问题 + 一组隐式意图清单。
- **失败时：** 对话过短无信号（如只有一句"继续"）→ 回溯更早数轮补上下文；仍无信号则只做身份类核心记忆注入。

### 步骤 2：查询改写

- **动作：** 把显式与隐式信号各改写成 1–N 条检索查询，执行指代消解——"它还支持吗"中的"它"替换为上文的实体名；每条查询独立成立、不含代词。
- **预期：** 1–5 条查询（经验值，可调），每条是可独立匹配记忆库的短句。

改写示例：

```text
对话：用户："它部署到 Vercel 的话还要改环境变量吗？"
改写前："它部署到 Vercel 的话还要改环境变量吗"   ← 含代词，不可独立匹配
改写后：q1 "Vercel 部署 环境变量 配置"            ← 显式提问，指代已消解
        q2 "项目 部署平台 部署方式"               ← 隐式意图：项目当前部署方式
```

- **失败时：** 指代无法消解（上文没出现候选实体）→ 保留原句并降权该查询的融合得分。

### 步骤 3：三路检索

- **动作：** 每条查询并行跑三路——关键词路（字面与同义词匹配，BM25 思路）、语义路（向量相似，无向量库时跳过）、时近路（按 updated_at 排序取近期条目）。无向量库时的降级方案：关键词路扩到同义词表 + 词干变体，时近路权重上调补偿，输出标注 retrieval_mode: keyword_only。
- **预期：** 每路返回候选集（各取 top 20，经验值，可调），并排入候选池。
- **失败时：** 关键词路零召回 → 用查询上位词（"PostgreSQL"→"数据库"）重试一次；仍零召回输出空结果并说明，不硬凑。多条查询的候选池合并后再去重——同一记忆被多条查询命中时只保留一次，命中次数作为打分的次级信号记录但不改权重。

### 步骤 4：融合打分

- **动作：** 对候选池去重后逐条打分：

```text
score = 0.4×semantic + 0.3×keyword + 0.2×recency + 0.1×confidence
```

- **预期：** 每条候选有 0–1 归一化总分；四路中缺席的路（如无向量库）把其权重按比例摊给剩余路。权重为经验值，可调。

打分示例（hybrid 模式）：某条记忆 semantic=0.9、keyword=0.8、recency=0.6、confidence=0.9 → score = 0.4×0.9 + 0.3×0.8 + 0.2×0.6 + 0.1×0.9 = 0.81。keyword_only 模式下 keyword 权重摊为 0.3/(0.3+0.2+0.1)=0.5，重算同条：0.5×0.8 + 0.33×0.6 + 0.17×0.9 ≈ 0.74。

- **失败时：** 打分需要外部 embedding 计算但环境不可用 → 整体降级为 keyword_only 模式并重算，不要输出半打分的名单。

### 步骤 5：预算内注入

- **动作：** 按总分降序取条目，逐块估算 token（经验值：中文约 1 字 ≈ 1 token，可按实际 tokenizer 校准），累计到预算即截断；按以下格式组织注入块：

```text
【以下为历史记忆，非当前对话内容】
- [mem_001 | 2026-09-16 | source: conversation:2026-09-16] 用户工作地点在上海
- [mem_014 | 2026-06-02 | source: compacted] 偏好：回复尽量短（可能过时，仅供参考）
【记忆结束】
```

- **预期：** 注入块在预算内、边界标记齐全、低置信度块带标注；同时输出检索报告（命中数、被截断数、retrieval_mode）。多轮会话时上一轮已注入的记忆不重复注入（轮间去重），把预算让给新信息；确需重复注入的关键身份类记忆除外。
- **失败时：** 最高分条目也低于相关性下限（经验值 0.3，可调）→ 输出空注入并明确告知"无可信相关记忆"，绝不拿低分记忆凑数。

## 参数速查表

| 参数 | 默认值 | 说明 |
|---|---|---|
| 融合权重 | 0.4 / 0.3 / 0.2 / 0.1 | semantic/keyword/recency/confidence；经验值，可调 |
| token 预算 | 2000 | 经验值，可调；应与 memory-architect 的载入预算一致 |
| 每路候选上限 | top 20 | 经验值，可调 |
| 注入相关性下限 | score ≥ 0.3 | 经验值，可调；低于则输出空注入 |
| 低置信标注线 | confidence < 0.7 | 与 memory-manager 的衰减线对齐 |
| 查询条数上限 | 5 条 | 经验值，可调 |
| 轮间去重 | 开启 | 上一轮已注入的记忆本轮不再注入，身份类核心记忆除外 |
| 时近路取新窗口 | 最近 30 天内条目优先 | 经验值，可调；仅影响时近路召回，不改变融合权重 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 注入的记忆与当前话题无关 | 查询改写混入了弱信号意图 | 收紧步骤 1 的隐式意图判定；相关性下限上调 |
| 检索端只回关键词命中、语义一路空转 | 无向量库或 embedding 服务失效 | 切 keyword_only 降级路径，权重重摊，输出标注 |
| 预算内塞的全是低分记忆 | 库内普遍低置信 | 检查上游：先跑 memory-manager 清扫，再回来检索 |
| 注入后 agent 把记忆当本轮事实 | 边界标记缺失或格式被吞 | 按红线 1 重排注入块，边界说明放在块首首行 |
| 同一事实新旧版本同时命中 | disputed 条目未过滤 | disputed 版本只取时间戳新者，另一版本标注"存在矛盾版本" |
| 频繁命中同一批条目（多样性差） | 时近路权重过高 | 下调 recency 权重，或对已注入条目做轮内去重 |
| 同一轮对话注入了两条互相矛盾的记忆 | disputed 过滤遗漏 | 按失败表第 5 行处理外，把该矛盾对回写报告，提醒用户交 memory-manager 复裁 |
| 每次检索结果抖动大 | 时近路随时间漂移过快 | recency 改按天分桶而非连续衰减，或在报告中固定检索快照时间 |
| 候选池被单一主题刷屏 | 某主题条目数占绝对多数 | 按主题限额进池（经验值每主题 ≤ 5 条，可调），保证注入多样性 |
| 用户索要"你记得的一切" | 混淆了检索与导出 | 按前置自检第三条走全量导出，不走打分注入路径 |

## 交付标准

- 注入块带整体边界标记，每块含 id、时间戳、source 三要素，原文逐字未改。
- 注入总 token ≤ 预算；低置信与 disputed 条目全部带对应标注。
- 输出检索报告：模式（hybrid / keyword_only）、命中数、截断数、最高分。
- 空结果必须显式输出"无可信相关记忆"并说明理由，不接受静默空返回。
- 融合打分四路权重与降级路径在报告中可追溯。
- 报告中注明本次是否启用轮间去重与主题限额。

## 参考

- `references/sources-and-methodology.md` —— 需要说明混合检索、时近权重与上下文预算注入的出处（mem0 / letta）、如何署名时读；评审核对方法论时也读。

## 链路位置

- 上游：`memory-manager`（库的干净度与 disputed 标记直接决定本技能的召回质量）、`memory-architect`（载入预算与 schema 的制定者）。
- 下游：交付给任意 agent 的上下文注入环节使用；在 agent 设计侧与 `agent-designer` 的上下文管理章节对接。
- 本技能是 memory-systems 链路的"出口工序"：architect 定预算、extractor 产条目、manager 保干净，retriever 负责让它们被用上。
