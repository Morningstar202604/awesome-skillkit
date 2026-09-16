---
name: memory-architect
description: "Use when designing a long-term memory architecture for an AI agent: layered memory (working/core/archival), storage selection, memory entry schema, read/write paths, and forgetting policy. Triggers on 设计记忆系统, 记忆架构, agent 长期记忆, memory design, memory schema, memory layering, storage selection, 遗忘机制, memory pressure. NOT for extraction/management/retrieval logic itself — use memory-extractor, memory-manager, or memory-retriever."
license: Apache-2.0
compatibility: Pure prompt-based; no scripts, no environment probing.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: memory
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-16"
---

# Memory Architect

给 agent 加记忆，多数人的做法是"往向量库一塞了事"，结果是检索噪声大、过期记忆污染上下文、隐私无处删。本技能先设计后动手：在写第一行存储代码之前，把记什么、放哪层、什么结构、谁能改、怎么忘这五个问题全部定下来，产出一份可执行的架构决策记录。

## 输入清单

开工前一次性收集。缺输入时用这句话向用户问一次："要设计记忆架构，请一次性提供：agent 的用途与主要任务、预期记忆规模（条数量级）、是否有向量库/数据库可用、隐私要求（是否涉及用户个人信息）、token 预算约束（记忆可占上下文的上限）。"

| 输入 | 必需 | 说明 |
|---|---|---|
| agent 用途与任务类型 | 是 | 决定记什么：客服记偏好、编码助手记项目状态、助理记事实与关系 |
| 记忆规模量级 | 是 | 百条 / 千条 / 十万条以上，直接决定存储选型 |
| 可用存储设施 | 是 | 纯文件 / SQLite / 向量库；没有向量库时设计必须走降级路径 |
| 隐私要求 | 是 | 是否存 PII、是否需要删除权支持；涉及即触发红线 2 |
| token 预算 | 否 | 每次会话可注入记忆的上限；缺省按经验值 2000 tokens 设计，可调 |
| 并发写入方 | 否 | 单 agent 还是多 agent 共写；多写方必须加时间戳与来源字段 |

## 前置自检

本技能为纯 prompt 技能，无需探测运行环境，只检查输入完备性：

- 六项输入中前四项（用途、规模、存储设施、隐私要求）是否全部明确？任一缺失 → 停止创作，用上面的问齐话术问一次，不要猜。
- 用户说"随便设计一个" → 规模按千条级、存储按纯文件降级路径设计，并在 ADR 中显式标注这两个假设。
- 用户只想要"聊天记录存档" → 这不是记忆系统，本技能不适用，直接告知。

## 红线

1. 不存敏感凭证：密码、API key、token、私钥一律不进记忆库，发现即拒绝写入并提示用户改用环境变量或密钥管理器。
2. PII 必须标注：记忆条目含个人身份信息时，schema 的 `pii` 字段必须为 true，且设计必须包含按 user_id 一键删除全部条目的能力。
3. 设计必须含遗忘机制：没有 TTL、没有淘汰策略的记忆系统是负债不是资产，交付物缺遗忘机制即返工。
4. 不为"以防万一"设计记录：每类记忆必须能回答"谁读、何时读、读了做什么"，答不上来就不记。
5. 隐私等级未确认时，一律按最高隐私级别设计（少记、加密意识、可删）。

## 工作流

### 步骤 1：需求画像

- **动作：** 把记忆需求拆成五类并逐类登记——事实（用户是谁）、偏好（用户喜欢什么）、决策（做过什么决定）、项目状态（进行到哪）、关系（和谁有什么联系）。每类记录：写入方、读取方、生命周期（会话内 / 周 / 永久）、隐私等级。
- **预期：** 一张五行需求表，每行四要素齐全。
- **失败时：** 用户答不出某类的读取方 → 该类从设计中移除，不要保留"可能有用"的记忆。

### 步骤 2：分层设计

- **动作：** 把每类需求映射到三层之一，并完成存储选型。
- **预期：** 分层表 + 选型结论，每层有明确存储介质。

| 层 | 放什么 | 生命周期 | 对应实现参照 |
|---|---|---|---|
| working | 当前任务中间状态 | 单次任务 | agent 运行时变量，不落盘 |
| core | 常驻上下文的少量关键事实 | 长期、可自更新 | letta 的 core memory（agent 可自编辑的常驻块）与 Claude memory tool 的 MEMORY.md 索引 |
| archival | 全量持久记忆，按需检索 | 永久到 TTL 到期 | letta 的 archival memory（向量库）或文件式主题记忆 |

存储选型表（三轴：数据量、检索延迟、运维成本）：

| 方案 | 适用数据量 | 检索延迟 | 运维成本 |
|---|---|---|---|
| 纯文件（MEMORY.md 索引 + 主题文件） | < 数千条 | 全文扫描，慢但可接受 | 零依赖，git 可版本化 |
| SQLite（FTS5 全文索引） | 千到十万条 | 毫秒级关键词检索 | 单文件，零服务 |
| 向量库（如 Qdrant / Chroma） | 万条以上或需语义检索 | 十毫秒级 | 需 embedding 管线与服务 |
| SQLite + 向量混合 | 十万条以上、高质量检索 | 最低（混合检索） | 最高，两套索引要同步 |

选型决策规则：条数 < 2000 → 纯文件；2000–100000 且只需关键词 → SQLite；需要语义相似检索 → 向量库；预算充足且规模大 → 混合。阈值均为经验值，可调。

### 步骤 3：Schema 设计

- **动作：** 按以下模板定死记忆条目结构，字段名英文、机器可解析：

```json
{
  "id": "mem_20260916_0001",
  "content": "用户偏好简洁的回复风格",
  "type": "preference",
  "user_id": "u_123",
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z",
  "confidence": 0.9,
  "ttl": "2027-09-16",
  "source": "conversation:2026-09-16",
  "pii": false,
  "tags": ["style"]
}
```

- **预期：** schema 冻结版；`id` 全局唯一，`type` 限定在 fact / preference / decision / project_status / relation 五类。
- **失败时：** 用户要求加字段 → 只允许加 optional 字段并写入 ADR 备忘；禁止改既有字段语义。

### 步骤 4：写读路径

- **动作：** 定三件事。写入时机（每轮对话后增量抽取，参照 memory-extractor；或会话结束批量写回，参照 Claude memory tool 的会话收尾写回模式）。载入预算（每次会话 core 层注入上限，默认经验值 2000 tokens，可调；archival 层按检索结果注入，参照 memory-retriever）。编辑权限（letta 式 agent 自编辑 core 层，还是受控式只允许管线写入——涉及 PII 的层一律受控）。
- **预期：** 写入时机、载入预算数值、各层编辑权限三项全部落进 ADR。
- **失败时：** 用户要求 agent 对 PII 条目有自编辑权 → 拒绝并引用红线 2，给出受控替代：agent 可发起删除请求，由管线执行。

### 步骤 5：交付 ADR 与初始化

- **动作：** 产出架构决策记录（JSON 风格），并给出存储初始化命令（如 `sqlite3 memory.db "CREATE TABLE memories (...)"` 或向量库建 collection 命令）。
- **预期：** ADR 每个决策有 id、决策内容、理由、备选项、放弃理由；初始化命令可直接执行。
- **失败时：** 决策理由写不出来 → 该决策没想清楚，退回对应步骤重做。

ADR 输出结构：

```json
{
  "project": "my-agent-memory",
  "date": "2026-09-16",
  "requirements": [{"kind": "preference", "lifespan": "long", "privacy": "pii-possible"}],
  "decisions": [
    {"id": "ADR-1", "decision": "archival 层用 SQLite FTS5", "why": "万条以内、无需语义检索", "alternatives": ["纯文件", "向量库"], "rejected_because": "文件扫描随规模劣化；向量库引入 embedding 运维成本"}
  ],
  "forgetting": {"ttl_enabled": true, "decay_rule": "90 天未命中且 confidence<0.7 降权"},
  "load_budget_tokens": 2000
}
```

## 参数速查表

| 参数 | 默认值 | 说明 |
|---|---|---|
| core 层载入预算 | 2000 tokens | 经验值，可调；超过说明 core 层塞了该进 archival 的东西 |
| 单条记忆 TTL | 180 天 | 经验值，可调；偏好类可设永久，项目状态类建议 30–90 天 |
| `confidence` 初值 | 显式事实 0.9 / 推断事实 0.6 | 与 memory-extractor 的打分规则对齐 |
| `type` 取值 | 5 类 | fact / preference / decision / project_status / relation |
| 遗忘检查频率 | 每次写入后顺带执行 | 也可定时批处理；与 memory-manager 的衰减规则对齐 |

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 用户坚持"全都存进向量库" | 未做需求画像 | 回步骤 1，用读取方追问逼出真实需求；仍坚持则记录异议后照做 |
| 分层后 core 层装不下 | 把检索型记忆错放 core | 移到 archival，core 只留身份与当前目标 |
| schema 字段被下游技能拒收 | 与 memory-extractor 产出不一致 | 以 memory-extractor 的 candidates.json 字段为准反向修订 schema |
| 无向量库但用户要语义检索 | 设施不足 | 设计降级路径：SQLite FTS5 + 关键词同义词表，并在 ADR 标注升级触发条件 |
| 初始化命令执行失败 | 环境缺少 SQLite 或向量库 | 按选型表降一级方案重出命令；不要现场安装重型依赖 |
| 隐私要求说不清 | 用户未评估数据敏感度 | 按红线 5 最高隐私级别设计，并在 ADR 标注"待确认" |

## 交付标准

- 五行需求表、分层映射表、存储选型结论三项齐全，每个决策可追溯到需求。
- schema 冻结版含全部必需字段（id、content、type、user_id、created_at、updated_at、confidence、ttl、source、pii），字段名全英文。
- ADR 为合法 JSON，含 decisions、forgetting、load_budget_tokens 三块。
- 遗忘机制明确：TTL 规则 + 降权规则各至少一条。
- 初始化命令用户可直接复制执行。
- PII 处理路径可验证：按 user_id 能列出并删除全部相关条目。

## 参考

- `references/sources-and-methodology.md` —— 需要向用户说明分层记忆、文件式记忆、条目化记忆等方法论出自哪些项目、如何署名时读；评审前核对方法论出处时也读。

## 链路位置

- 上游：`agent-designer`（agent 整体设计定稿后，记忆架构是其子设计）。
- 下游：`memory-extractor`（按本技能 schema 抽取条目）→ `memory-manager`（按本技能遗忘策略管生命周期）→ `memory-retriever`（按本技能载入预算注入）。
- 本技能是 memory-systems 链路的起点：schema 与遗忘策略在此定死，下游三个技能只执行不重新设计。
