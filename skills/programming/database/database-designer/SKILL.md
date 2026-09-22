---
name: database-designer
description: "Use when the user asks to design database schemas, create ERD diagrams, normalize schemas, plan data migrations, add multi-tenancy or row-level security, generate seed data, optimize queries, choose between SQL and NoSQL, or model data relationships. 当用户要求 设计数据库表 / 表结构设计 / 建索引 时使用。 Do NOT use for executing schema changes against a live database."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: database
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# 数据库设计助手

用工具支撑 Schema 的设计与演进：自动化规范化分析、ERD 生成、基于真实查询模式的索引优化、零停机迁移规划。只做分析与方案生成——绝不对在线库执行 Schema 变更。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 当前 Schema | 必需 | SQL DDL 文件或 JSON Schema（样例在 `assets/sample_schema.sql` / `sample_schema.json`） |
| 热点查询模式 | 条件必需 | 查询模式 JSON，索引优化用（复制 `assets/sample_query_patterns.json`，填入用户查询） |
| 目标 Schema | 条件必需 | 生成迁移时的第二份 Schema JSON |
| 数据库引擎 | 可选 | PostgreSQL（SQL 示例默认按它写）、MySQL、SQLite、SQL Server |
| 多租户 / RLS / 种子数据需求 | 可选 | 触发 Schema 设计手册流程 |

输入缺失时一次性问齐："请提供：① 当前 Schema（DDL 文件或 JSON）② 最热的查询（做索引用）③ 若要迁移方案，给目标 Schema ④ 目标引擎及租户/RLS 要求。其余按默认处理。"

## 前置自检

逐条探测，任一失败 → 给出修复方法并 STOP：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
# 自检：python3 scripts/schema_analyzer.py --help / index_optimizer.py / migration_generator.py 均预期退出码 0；失败：脚本缺失 → 检查技能目录
test -f <schema-input>   # 预期退出码 0；失败：文件缺失 → 向用户要 DDL/JSON Schema
```

## 工作流

用工具跑，不要徒手分析 Schema。所有路径相对本技能目录；样例输入在 `assets/`。

### 步骤 1：分析 Schema

```bash
python3 scripts/schema_analyzer.py --input assets/sample_schema.sql --generate-erd --output-format json -o analysis.json   # 随包样例 DDL；你的真实 schema 换成 schema.sql
```

预期：`analysis.json` 含规范化发现、缺失约束、命名问题与 Mermaid ERD（`--erd-only` 只输出 ERD）。把 ERD 展示给用户，先修掉标记的问题再优化。若失败：DDL 解析报错 → 确认 SQL 方言受支持，或转成 JSON Schema；大 Schema 却零发现 → 确认 `--input` 指向 DDL，不是带数据的 dump。

### 步骤 2：基于真实查询模式优化索引

```bash
python3 scripts/index_optimizer.py --schema assets/sample_schema.json --queries assets/sample_query_patterns.json --analyze-existing --format json -o indexes.json
```

先把用户的热点查询写进查询模式 JSON（复制 `assets/sample_query_patterns.json`）。预期：按优先级排序的 CREATE INDEX 建议清单，外加冗余索引清理项。若失败：零建议 → 查询可能太少或太简单，向用户要真实负载；`--min-priority`（1=最高，4=最低，默认 4）控制截断线。

### 步骤 3：生成迁移

```bash
python3 scripts/migration_generator.py --current assets/sample_schema.json --target assets/target_schema_sample.json --zero-downtime --format sql -o migration.sql   # 随包样例（加列 diff）；你的真实场景换成两份 schema JSON
```

预期：`migration.sql` 含 ALTER 语句；`--zero-downtime` 输出 expand-contract 方案。若失败：两份 Schema JSON 与分析器输出结构不一致 → 用步骤 1 重新生成。

> **Boundary / 与 sql-database-assistant 的划界**：本技能的 `migration_generator.py` 做 **schema 对比迁移**——输入两份 schema JSON，输出 ALTER + 回滚 + 零停机计划。若需求是"用一句自然语言描述改动，生成 up/down 迁移模板"，请走 `sql-database-assistant` 的同名脚本（`--change "..."`），二者职责不同、互为上下游。

### 步骤 4：验证闭环

对 *目标* Schema 重跑步骤 1，断言第一轮发现的问题已消除；交付迁移前跑 `migration_generator.py --validate-only`。绝不执行迁移——把 SQL 交给用户。

## Schema 设计手册（多租户、RLS、种子数据）

→ 跨领域关注点（租户隔离、软删除、审计轨迹）、PostgreSQL RLS 策略、种子数据指南见 references/schema-design-playbook.md，完整示例 Schema 见 references/full-schema-examples.md

## 查询生成模式

### SELECT 与 JOIN

```sql
-- INNER JOIN：只保留匹配行
SELECT o.id, c.name, o.total
FROM orders o
INNER JOIN customers c ON c.id = o.customer_id;

-- LEFT JOIN：左表全保留，未匹配处填 NULL
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.name;

-- 自连接：层级数据（员工/经理）
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

### 公用表表达式（CTE）

```sql
-- 递归 CTE 查组织架构
WITH RECURSIVE org AS (
  SELECT id, name, manager_id, 1 AS depth
  FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.name, e.manager_id, o.depth + 1
  FROM employees e INNER JOIN org o ON o.id = e.manager_id
)
SELECT * FROM org ORDER BY depth, name;
```

### 窗口函数

```sql
-- ROW_NUMBER 做分页 / 去重
SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
FROM orders;

-- RANK 有并列空位，DENSE_RANK 没有
SELECT name, score, RANK() OVER (ORDER BY score DESC) AS rank FROM leaderboard;

-- LAG/LEAD 比较相邻行
SELECT date, revenue,
  revenue - LAG(revenue) OVER (ORDER BY date) AS daily_change
FROM daily_sales;
```

### 聚合模式

```sql
-- FILTER 子句（PostgreSQL）做条件聚合
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE status = 'active') AS active,
  AVG(amount) FILTER (WHERE amount > 0) AS avg_positive
FROM accounts;

-- GROUPING SETS 做多级汇总
SELECT region, product, SUM(revenue)
FROM sales
GROUP BY GROUPING SETS ((region, product), (region), ());
```

## 迁移模式

### Up/Down 迁移脚本

每个迁移必须有可逆的对应脚本。文件名加时间戳前缀保证顺序：

```text
migrations/
├── 20260101_000001_create_users.up.sql
├── 20260101_000001_create_users.down.sql
├── 20260115_000002_add_users_email_index.up.sql
└── 20260115_000002_add_users_email_index.down.sql
```

### 零停机迁移（Expand/Contract）

1. **扩展** — 加新列/新表（可空、带默认值）
2. **迁移数据** — 分批回填；应用侧双写
3. **切换** — 应用改读新列；停写旧列
4. **收缩** — 在后续迁移里删旧列

### 数据回填策略

```sql
-- 分批更新，避免长事务锁
UPDATE users SET email_normalized = LOWER(email)
WHERE id IN (SELECT id FROM users WHERE email_normalized IS NULL LIMIT 5000);
-- 循环重跑，直到影响 0 行
```

### 回滚流程

- 上生产前，先在 staging 测过 `down.sql`
- 回滚窗口要短——contract 步骤已执行的话，回滚只能靠新的正向迁移
- 不可逆变更（删有数据的列）先做逻辑备份

## 性能优化

### 索引策略

| 索引类型 | 适用场景 | 示例 |
|----------|----------|------|
| **B-tree**（默认） | 等值、范围、ORDER BY | `CREATE INDEX idx_users_email ON users(email);` |
| **GIN** | 全文检索、JSONB、数组 | `CREATE INDEX idx_docs_body ON docs USING gin(to_tsvector('english', body));` |
| **GiST** | 几何、范围类型、最近邻 | `CREATE INDEX idx_locations ON places USING gist(coords);` |
| **Partial** | 行子集（减小体积） | `CREATE INDEX idx_active ON users(email) WHERE active = true;` |
| **Covering** | 仅索引扫描 | `CREATE INDEX idx_cov ON orders(customer_id) INCLUDE (total, created_at);` |

### EXPLAIN 计划解读

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```

重点信号：

- 大表上的 **Seq Scan** — 缺索引
- 行数估算偏高的 **Nested Loop** — 考虑 hash/merge join 或加索引
- **Buffers shared read** 远高于 **hit** — 工作集超出内存

### N+1 查询检测

症状：应用逐行发查询（如在循环里取关联记录）。

修复：

- 用 `JOIN` 或子查询一趟取回
- ORM 预加载（`select_related` / `includes` / `with`）
- GraphQL resolver 用 DataLoader 模式

### 连接池

| 工具 | 协议 | 最适合 |
|------|------|--------|
| **PgBouncer** | PostgreSQL | 事务/语句级池化，开销低 |
| **ProxySQL** | MySQL | 查询路由、读写分离 |
| **内置池**（HikariCP、SQLAlchemy pool） | 任意 | 应用层池化 |

**经验法则：** 池大小设为 `(2 * CPU cores) + disk spindles`。云 SSD 从 `2 * vCPUs` 起步再调。

### 读副本与查询路由

- `SELECT` 全走副本；写入走主库
- 计入复制延迟（异步通常 <1s，同步为 0）
- 读关键数据前用 `pg_last_wal_replay_lsn()` 探测延迟

## 多数据库决策矩阵

| 维度 | PostgreSQL | MySQL | SQLite | SQL Server |
|------|-----------|-------|--------|------------|
| **最适合** | 复杂查询、JSONB、扩展 | Web 应用、读多写少 | 嵌入式、开发/测试、边缘 | 企业 .NET 技术栈 |
| **JSON 支持** | 优秀（JSONB + GIN） | 良好（JSON 类型） | 极少 | 良好（OPENJSON） |
| **复制** | 流复制、逻辑复制 | 组复制、InnoDB cluster | 不适用 | Always On AG |
| **许可** | 开源（PostgreSQL License） | 开源（GPL）/ 商业 | 公有领域 | 商业 |
| **实用上限** | 多 TB | 多 TB | ~1 TB（单写者） | 多 TB |

**选型建议：**

- **PostgreSQL** — 新项目默认选择；扩展性与标准兼容性最好
- **MySQL** — 已有 MySQL 生态；简单的读多写少 Web 应用
- **SQLite** — 移动应用、CLI 工具、单元测试库、IoT/边缘
- **SQL Server** — 企业政策强制；深度 .NET/Azure 集成

### NoSQL 考量

| 数据库 | 模型 | 适用时机 |
|--------|------|----------|
| **MongoDB** | 文档 | Schema 灵活、快速原型、内容管理 |
| **Redis** | 键值 / 缓存 | Session 存储、限流、排行榜、pub/sub |
| **DynamoDB** | 宽列 | Serverless AWS 应用，任意规模下个位数毫秒延迟 |

> 默认用 SQL。只有访问模式明显受益时才上 NoSQL。

## 分片与复制

### 垂直拆分 vs 水平拆分

- **垂直拆分**：按列拆到多张表（如拆出 BLOB 列）。收窄查询的 I/O。
- **水平拆分（分片）**：按行拆到多个库/多台服务器。单节点装不下数据或扛不住吞吐时必须做。

### 分片策略

| 策略 | 工作方式 | 优点 | 缺点 |
|------|----------|------|------|
| **Hash** | `shard = hash(key) % N` | 分布均匀 | 重分片代价高 |
| **Range** | 按日期或 ID 区间分 | 简单，适合时序 | 最新分片成热点 |
| **Geographic** | 按用户地域分 | 数据本地性、合规 | 跨区查询难 |

### 复制模式

| 模式 | 一致性 | 延迟 | 适用场景 |
|------|--------|------|----------|
| **同步** | 强 | 写延迟高 | 金融交易 |
| **异步** | 最终一致 | 写延迟低 | 读多写少的 Web 应用 |
| **半同步** | 至少一个副本确认 | 中等 | 安全与速度的平衡 |

## 失败处置表

| 症状 / 报错 | 原因 | 修复 |
|-------------|------|------|
| `schema_analyzer.py` DDL 解析报错 | 方言专属语法不支持 | 把 DDL 转成 JSON Schema 格式，用 `--input sample_schema.json` 重跑 |
| 大 Schema 上分析器零发现 | 输入是数据 dump，不是 DDL | 只喂 DDL 重跑（`pg_dump --schema-only`） |
| 索引优化器零建议 | 查询模式 JSON 为空或太简单 | 把用户真实热点查询填进 `assets/sample_query_patterns.json` |
| 迁移里意外出现破坏性 DROP | 当前/目标 Schema 不匹配 | 检查两份 JSON；用步骤 1 重新生成；交付前与用户确认 |
| `--validate-only` 报失败 | 迁移按当前方案不可行 | 修掉 Schema 冲突（类型变更、存量数据）后重新生成 |

## 交付标准

- 成功定义：带 Mermaid ERD 的分析 JSON、绑定真实查询模式的索引建议清单，以及（如有要求）通过校验、带回滚/零停机方案的迁移 SQL。
- 产物命名：`analysis.json`、`indexes.json`、`migration.sql`（或用户经 `-o` 指定的名字）。
- 保存位置：工作目录根，或项目 `migrations/` 目录（迁移 SQL 按上述时间戳命名）。
- 完整性核验：分析器每条发现要么在目标 Schema 里修掉，要么明确豁免；每条索引建议都注明服务的查询模式；`--validate-only` 通过。

## 安全红线

- 本技能绝不连接在线库、绝不对在线库执行任何操作——所有产物都是供用户评审的文件。
- 含 DROP/DELETE/TRUNCATE 的迁移，交付前必须向用户显式标出。
- `assets/` 里的样例文件是合成示例，不是真实生产 Schema。

## 参考

- `references/schema-design-playbook.md` — 设计多租户、RLS、软删除、审计轨迹或种子数据时读
- `references/full-schema-examples.md` — 需要完整示例 Schema 时读
- `references/database-design-reference.md` — 通用设计原则（命名、约束、类型）时读
- `references/normalization_guide.md` — 用户追问 Schema 为何如此（反）规范化时读
- `references/index_strategy_patterns.md` — 在索引类型或复合列序之间取舍时读
- `references/database_selection_decision_tree.md` — 用户还在选引擎（SQL vs NoSQL）时读

## 相关技能

- **sql-database-assistant** — 日常 SQL 的查询编写、优化与排障
- **migration-architect** — 跨数据库引擎的大规模迁移规划，或大型 Schema 改造
- **senior-backend** — 应用层模式（连接池、ORM 最佳实践）
- **senior-devops** — 数据库集群与副本的基础设施供给
