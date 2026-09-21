基于您提供的五项输入，我现在为您设计这套长期记忆架构。由于输入完整，我将直接给出方案。

## 1. 需求画像（五类登记）

| 需求类型 | 具体内容 | 写入方 | 读取方 | 生命周期 | 隐私等级 |
|---|---|---|---|---|---|
| 事实 (Fact) | 开发环境、技术栈、本地路径 | Agent | Agent | 永久 | 低 |
| 偏好 (Preference) | 客户沟通风格、代码风格要求 | Memory Manager | Agent | 永久（直至显式删除） | **中 (PII)** |
| 决策 (Decision) | 架构选型、技术路线确认 | Agent | Agent | 永久 | 低 |
| 项目状态 (Project Status) | 各项目的当前进度、待办、代码位置 | Agent | Agent | 活跃期 + 30天缓冲 | 中 |
| 关系 (Relation) | 客户与项目的对应关系、团队成员 | Memory Manager | Agent | 永久 | **高 (PII)** |

**关键约束：** 凡是涉及具体客户名称、联系方式、邮箱、合同金额的记录，必须脱敏（映射为代号如 `client_A`）或排除在记忆库外。

## 2. 分层设计

| 层 | 存储介质 | 内容 | 检索方式 |
|---|---|---|---|
| **Working** | 运行时变量 | 当前会话正在处理的具体任务细节 | 不存盘，会话结束即焚 |
| **Core** | SQLite (`core_memories`) | 全局开发环境配置、多项目概览、活跃项目清单 | 全量注入上下文 |
| **Archival** | SQLite (`project_memories`) | 具体项目的详细状态、客户偏好详情、历史决策 | FTS5 关键词检索 |

**选型理由：**
千级条目规模 + 无向量库 + 需语义理解（代码/偏好），SQLite FTS5 是性价比最高的降级方案。它支持全文检索，虽不如向量库智能，但对结构化记忆足够且零运维成本。

## 3. Schema 设计（冻结版）

```json
{
  "id": "mem_20260916_projA_001",
  "content": "Project Alpha: 使用 Next.js 14，Tailwind CSS，数据库已迁移至 v3。",
  "type": "project_status",
  "project_id": "proj_A", 
  "client_id": "client_A", 
  "created_at": "2026-09-16T10:00:00Z",
  "updated_at": "2026-09-16T10:00:00Z",
  "confidence": 0.9,
  "ttl": "2027-09-16",
  "source": "code_review:2026-09-16",
  "pii": false,
  "pii_content_hash": null,
  "tags": ["tech_stack", "frontend"]
}
```

**字段说明：**
- `pii`: 标记该条目是否包含敏感信息。若为 true，`content` 中不得出现真实姓名/电话，只能保留脱敏代号。
- `pii_content_hash`: 对敏感字段的哈希，用于快速识别重复或变更。

## 4. 写读路径

### 写入时机
- **增量写入：** 每个任务节点结束时（如代码提交、会议记录生成后），由 `memory-extractor` 提取 1-3 条关键记忆。
- **批量写入：** 会话结束前，执行一次“记忆整理”，将 Working 层信息沉淀到 Archival 层。

### 载入预算（4000字符）
- **Core 层：** 每次会话加载所有 Core 记忆（预计约 1000-1500 字符）。
- **Archival 层：** 根据当前任务关键词，检索 Top-3 相关记忆（每条约 1000 字符，共 3000 字符）。
- **总上限：** 4000 字符。超出时优先保留高 `confidence` 的记忆。

### 编辑权限
- **Agent 自编辑 Core 层：** 允许 Agent 更新自己的状态（如“当前在项目 A”）。
- **受控写入 PII：** 任何含 `pii=true` 的条目，必须由管线（Pipeline）验证脱敏后方可写入，Agent 仅可发起请求。

## 5. 交付 ADR（架构决策记录）

```json
{
  "project": "multi-project-agent-memory",
  "date": "2026-09-16",
  "requirements": [
    {"kind": "preference", "lifespan": "long", "privacy": "pii-managed"},
    {"kind": "project_status", "lifespan": "active+buffer", "privacy": "low"}
  ],
  "decisions": [
    {"id": "ADR-1", "decision": "Archival 层采用 SQLite FTS5", "why": "千级规模，无向量库，需全文检索代码/文档上下文", "alternatives": ["纯文件", "向量库"], "rejected_because": "纯文件检索慢；向量库引入额外服务依赖"},
    {"id": "ADR-2", "decision": "PII 数据强制脱敏映射", "why": "私活客户信息属敏感数据，需符合隐私红线", "alternatives": ["加密存储", "完全排除"], "rejected_because": "加密增加复杂度；排除导致项目上下文丢失"}
  ],
  "forgetting": {
    "ttl_enabled": true,
    "decay_rule": "30天未命中且 confidence<0.7 的记忆标记为过期，下次清理时归档或删除",
    "purge_rule": "超过 TTL 且 90 天无访问记录的条目自动删除"
  },
  "load_budget_tokens": 4000
}
```

## 6. 初始化命令

```bash
# 创建 SQLite 数据库
sqlite3 memory.db "
CREATE TABLE core_memories (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  type TEXT,
  created_at DATETIME,
  updated_at DATETIME
);

CREATE TABLE project_memories (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  type TEXT,
  project_id TEXT,
  client_id TEXT,
  created_at DATETIME,
  updated_at DATETIME,
  confidence REAL,
  ttl DATETIME,
  pii BOOLEAN DEFAULT 0
);

-- 建立全文索引
CREATE VIRTUAL TABLE project_fts USING fts5(content, content=project_memories, content_rowid=id);
"
```

## 7. 清理机制（遗忘策略）

1. **TTL 检查：** 每次写入后，检查是否有条目 TTL 到期。
2. **降权规则：** 30 天无检索且置信度 < 0.7 的记忆，从 Archival 移至