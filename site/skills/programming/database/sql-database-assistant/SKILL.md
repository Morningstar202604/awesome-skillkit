---
name: sql-database-assistant
description: "Use when the user asks to write SQL queries, optimize database performance, generate migrations, explore database schemas, or work with ORMs like Prisma, Drizzle, TypeORM, or SQLAlchemy. 当用户要求 写 SQL / 优化慢查询 / 生成表结构文档 时使用。 Do NOT use for provisioning database servers or managing replicas."
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

# SQL 数据库助手

database-designer 的日常操作搭档。**database-designer** 聚焦 Schema 架构、ERD 建模与多租户模式；本技能覆盖日常：写查询、优化性能、生成迁移、打通应用代码与数据库引擎之间的鸿沟。

## 工作流

本技能按以下主流程推进，各环节详细规则见后续对应章节：

1. **接需求**：区分是"写成 SQL"、"优化已有 SQL"还是"设计/迁移 schema"（见 自然语言转 SQL / 查询优化 / 迁移生成）
2. **摸 schema**：确认表结构与字段类型，不靠猜（见 Schema 探索）
3. **产出**：给出 SQL 或迁移脚本，并说明假设条件（见 交付标准）
4. **优化与校验**：有性能问题时走索引与执行计划分析（见 查询优化）
5. **自检**：对着 安全红线 与 失败处置表 过一遍再交付

> 目标数据库不同时，先按 多数据库支持 章节确认方言差异，避免语法不兼容。

## 核心能力

- **自然语言转 SQL** — 把需求翻译成正确且高效的查询
- **Schema 探索** — 内省 PostgreSQL、MySQL、SQLite、SQL Server 在线库
- **查询优化** — EXPLAIN 分析、索引建议、改写模式
- **迁移生成** — up/down 脚本、零停机策略、回滚预案
- **ORM 集成** — Prisma、Drizzle、TypeORM、SQLAlchemy 模式与逃生通道

### 工具

| 脚本 | 用途 |
|------|------|
| `scripts/query_optimizer.py` | 静态分析 SQL 查询的性能问题 |
| `scripts/migration_generator.py` | 从变更描述生成迁移文件模板 |
| `scripts/schema_explorer.py` | 把内省结果（或 SQLite 文件）转成 Schema 文档 |

> **Boundary / 与 database-designer 的划界**：本技能的 `migration_generator.py` 做 **自然语言 → 迁移模板**（`--change "add column ..." → up/down 文件`）。若需求是"对比两份 schema JSON、生成含回滚与零停机（expand-contract）的正式迁移 SQL"，请走 `database-designer` 的同名脚本（`--current/--target`），二者职责不同、互为上下游。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| SQL 查询或文件 | 条件必需 | 查询文本或 `.sql` 路径，优化请求用 |
| 变更描述 | 条件必需 | 自然语言的表结构变更，迁移请求用 |
| 内省数据源 | 条件必需 | 内省 JSON/CSV 文件，或 SQLite `.db` 文件，Schema 探索用 |
| 方言 | 可选 | `postgres`（默认）、`mysql`、`sqlite`、`sqlserver` |
| 输出格式 | 可选 | 默认 stdout；各工具支持 `--json` / `--output <file>` |

输入缺失时一次性问齐："请提供：① 查询 / 变更描述 / 内省数据（按任务取其一）② 目标方言（postgres/mysql/sqlite/sqlserver）③ 输出格式与目的地。其余按默认处理。"

## 前置自检

逐条探测，任一失败 → 给出修复方法并 STOP：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
# 自检：python3 scripts/query_optimizer.py --help / migration_generator.py / schema_explorer.py 均预期退出码 0；失败：脚本缺失 → 检查技能目录
```

按任务补充检查：优化只需查询文本；迁移生成只需变更描述；Schema 探索需要内省文件（或 SQLite 文件——传 `--sqlite` 前确认文件存在且可读）。

## 自然语言转 SQL

### 转换模式

把需求转成 SQL 时，按此顺序：

1. **识别实体** — 名词映射为表
2. **识别关系** — 动词映射为 JOIN 或子查询
3. **识别过滤条件** — 形容词/条件映射为 WHERE 子句
4. **识别聚合** — "总数""平均""计数"映射为 GROUP BY
5. **识别排序** — "前 N""最新""最高"映射为 ORDER BY + LIMIT

### 常用查询模板

**每组 Top-N（窗口函数）**

```sql
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
  FROM employees
) ranked WHERE rn <= 3;
```

**累计求和**

```sql
SELECT date, amount,
  SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM transactions;
```

**缺口检测**

```sql
SELECT curr.id, curr.seq_num, prev.seq_num AS prev_seq
FROM records curr
LEFT JOIN records prev ON prev.seq_num = curr.seq_num - 1
WHERE prev.id IS NULL AND curr.seq_num > 1;
```

**UPSERT（PostgreSQL）**

```sql
INSERT INTO settings (key, value, updated_at)
VALUES ('theme', 'dark', NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = EXCLUDED.updated_at;
```

**UPSERT（MySQL）**

```sql
INSERT INTO settings (key_name, value, updated_at)
VALUES ('theme', 'dark', NOW())
ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = VALUES(updated_at);
```

> JOIN、CTE、窗口函数、JSON 操作等更多模式见 references/query_patterns.md。

## Schema 探索

### 内省查询

**PostgreSQL — 列出表与列**

```sql
SELECT table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

**PostgreSQL — 外键**

```sql
SELECT tc.table_name, kcu.column_name,
  ccu.table_name AS foreign_table, ccu.column_name AS foreign_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

**MySQL — 表大小**

```sql
SELECT table_name, table_rows,
  ROUND(data_length / 1024 / 1024, 2) AS data_mb,
  ROUND(index_length / 1024 / 1024, 2) AS index_mb
FROM information_schema.tables
WHERE table_schema = DATABASE()
ORDER BY data_length DESC;
```

**SQLite — Schema 导出**

```sql
SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name;
```

**SQL Server — 列与类型**

```sql
SELECT t.name AS table_name, c.name AS column_name,
  ty.name AS data_type, c.max_length, c.is_nullable
FROM sys.columns c
JOIN sys.tables t ON c.object_id = t.object_id
JOIN sys.types ty ON c.user_type_id = ty.user_type_id
ORDER BY t.name, c.column_id;
```

### 从 Schema 生成文档

运行 `scripts/schema_explorer.py`——两个输入互斥，必填其一：

```bash
# 从 SQLite 数据库（只读打开）提取，单表过滤，JSON 输出
python3 scripts/schema_explorer.py --sqlite assets/sample.db --table users --json   # 随包样例库（users/orders 两表）；你的真实库换成 app.db

# 从内省结果文件（JSON/CSV；`-` 读 stdin）生成 Markdown 文档
python3 scripts/schema_explorer.py --input assets/introspection.json -o schema_doc.md   # 随包样例（行式内省：table_name/column_name/data_type 三列起）
```

预期：stdout 输出 Markdown Schema 文档，或写到 `-o` 指定路径；`--json` 切换为规范化 JSON。若失败：`--input` 与 `--sqlite` 都没给 → 脚本以用法错误退出，补一个数据源；内省文件格式损坏 → 先用上面的查询重新生成。

## 查询优化

### EXPLAIN 分析工作流

1. **跑 EXPLAIN ANALYZE**（PostgreSQL）或 **EXPLAIN FORMAT=JSON**（MySQL）
2. **定位最贵的节点** — 大表上的 Seq Scan、行数估算偏高的 Nested Loop
3. **检查缺失索引** — 过滤列上的顺序扫描
4. **留意估算偏差** — 计划行数与实际行数差异大，说明统计信息过期
5. **评估 JOIN 顺序** — 让最小结果集驱动连接

### 索引建议清单

- WHERE 子句中高选择性的列
- JOIN 条件中的列（外键）
- 与 LIMIT 组合使用的 ORDER BY 列
- 匹配多列 WHERE 谓词的复合索引（选择性最高的列放前面）
- 常量过滤查询的部分索引（如 `WHERE status = 'active'`）
- 读多写少场景用覆盖索引，避免回表

### 查询改写模式

| 反模式 | 改写 |
|--------|------|
| `SELECT * FROM orders` | `SELECT id, status, total FROM orders`（显式列出列） |
| `WHERE YEAR(created_at) = 2025` | `WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'`（可走索引） |
| SELECT 中的关联子查询 | LEFT JOIN + 聚合 |
| 带 NULL 的 `NOT IN (SELECT ...)` | `NOT EXISTS (SELECT 1 ...)` |
| 不需要去重却用 `UNION` | `UNION ALL` |
| `LIKE '%search%'` | 全文检索索引（GIN/FULLTEXT） |
| `ORDER BY RAND()` | 应用侧随机抽样或 `TABLESAMPLE` |

### 静态分析工具

```bash
python3 scripts/query_optimizer.py --query "SELECT * FROM orders WHERE status = 'pending'" --dialect postgres
python3 scripts/query_optimizer.py --query queries.sql --dialect mysql --json
```

预期：逐语句输出发现清单（反模式、索引提示）；`--json` 输出机器可读结果。若失败：`--query` 接受 SQL 字符串或 `.sql` 文件路径——路径按文件处理但不存在时会报错退出，核对路径。

> EXPLAIN 计划解读、索引类型、连接池见 references/optimization_guide.md。

## 迁移生成

### 零停机迁移模式

**加列（安全）**

```sql
-- Up
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Down
ALTER TABLE users DROP COLUMN phone;
```

**重命名列（expand-contract）**

```sql
-- 步骤 1：加新列
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
-- 步骤 2：回填
UPDATE users SET full_name = name;
-- 步骤 3：部署应用，读两列
-- 步骤 4：部署应用，只写新列
-- 步骤 5：删旧列
ALTER TABLE users DROP COLUMN name;
```

**加 NOT NULL 列（安全顺序）**

```sql
-- 步骤 1：加可空列
ALTER TABLE orders ADD COLUMN region VARCHAR(50);
-- 步骤 2：按默认值回填
UPDATE orders SET region = 'unknown' WHERE region IS NULL;
-- 步骤 3：加约束
ALTER TABLE orders ALTER COLUMN region SET NOT NULL;
ALTER TABLE orders ALTER COLUMN region SET DEFAULT 'unknown';
```

**建索引（不阻塞，PostgreSQL）**

```sql
CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);
```

### 回填与回滚策略

- **分批更新** — 每批 1000-10000 行，避免锁竞争；过渡期**双写**新旧两列；每批跑完核对行数
- 每个迁移必须有可逆的 down 脚本。不可逆变更：先 `pg_dump` 受影响表，用 feature flag 切换读路径，或窗口期保留影子表副本

### 迁移生成工具

```bash
python3 scripts/migration_generator.py --change "add email_verified boolean to users" --dialect postgres --format sql
python3 scripts/migration_generator.py --change "rename column name to full_name in customers" --dialect mysql --format alembic --json
```

预期：按 `--format`（`sql`/`prisma`/`alembic`）输出 up/down 迁移模板（SQL）或 Alembic/Prisma 模板；`--output` 写文件而非 stdout。若失败：变更措辞无法识别 → 改述为 "add/drop/rename column X to/in table Y"；方言不支持 → 从上述四种中选一。

## 多数据库支持与 ORM

不同引擎的方言差异（UPSERT / 布尔 / 自增 / JSON / 窗口函数等 9 项对照）与四大 ORM
（Prisma / SQLAlchemy / TypeORM / GORM）的 schema 定义、迁移命令与查询 API，
已整理到参考文件，需要时再读：

- [dialect_and_orm.md](references/dialect_and_orm.md) —— 方言对照表 + 兼容性要点 + ORM 模式
- [orm_patterns.md](references/orm_patterns.md) —— ORM 深度模式与关联查询
- [optimization_guide.md](references/optimization_guide.md) —— 索引与执行计划优化
- [query_patterns.md](references/query_patterns.md) —— 常用查询写法

> 跨引擎迁移前，先按方言对照表确认语法兼容；写 ORM 代码前，确认目标 ORM 的迁移命令形态。

## 数据完整性

### 约束策略

- **主键** — 每张表必须有；优先代理键（serial/UUID）
- **外键** — 强制引用完整性；显式定义 ON DELETE 行为
- **UNIQUE 约束** — 业务级唯一（email、slug、API key）
- **CHECK 约束** — 在数据库层校验范围、枚举与业务规则
- **NOT NULL** — 默认 NOT NULL；确实可空才放开

### 事务隔离级别

| 级别 | 脏读 | 不可重复读 | 幻读 | 适用场景 |
|------|------|-----------|------|----------|
| READ UNCOMMITTED | 有 | 有 | 有 | 不建议使用 |
| READ COMMITTED | 无 | 有 | 有 | PostgreSQL 默认，一般 OLTP |
| REPEATABLE READ | 无 | 无 | 有（InnoDB：无） | 财务计算 |
| SERIALIZABLE | 无 | 无 | 无 | 强一致性场景（计费、库存） |

### 死锁预防

1. **一致的加锁顺序** — 始终按相同顺序访问表/行
2. **短事务** — 压缩从第一次加锁到提交的时间
3. **咨询锁** — 用 `pg_advisory_lock()` 做应用层协调
4. **重试逻辑** — 捕获死锁错误，指数退避重试

## 备份与恢复

### PostgreSQL

```bash
# 全量备份
pg_dump -Fc --no-owner dbname > backup.dump
# 恢复
pg_restore -d dbname --clean --no-owner backup.dump
# 时间点恢复：配置 WAL 归档 + restore_command
```

### MySQL

```bash
# 全量备份
mysqldump --single-transaction --routines --triggers dbname > backup.sql
# 恢复
mysql dbname < backup.sql
# 用二进制日志做 PITR：mysqlbinlog --start-datetime="2025-01-01 00:00:00" binlog.000001
```

### SQLite

```bash
# 备份（并发读安全）
sqlite3 dbname ".backup backup.db"
```

备份纪律：自动化备份、定期演练恢复、异地留副本——没验证过恢复的备份不算备份。

## 反模式

| 反模式 | 问题 | 修复 |
|--------|------|------|
| `SELECT *` | 传输多余数据，Schema 变更即崩 | 显式列清单 |
| 外键列缺索引 | JOIN 慢、级联删除慢 | 给所有外键加索引 |
| N+1 查询 | 1 + N 次往返；ORM 循环懒加载表现为大量相同 SELECT | 预加载（`include`/`joinedload`）、`WHERE id IN (...)` 或 DataLoader |
| 隐式类型转换 | `WHERE id = '123'` 阻止走索引 | 谓词两侧类型一致 |
| 无连接池 | 高负载下连接耗尽 | PgBouncer、ProxySQL 或 ORM 池 |
| 无界查询 | 无 LIMIT 可能返回百万行 | 始终分页 |
| 用 FLOAT 存金额 | 舍入误差 | 用 `DECIMAL(19,4)` 或整数分 |
| 上帝表 | 一张表 50+ 列 | 规范化或垂直拆分 |
| 到处软删除 | 每条查询都要带 `WHERE deleted_at IS NULL` | 归档表或事件溯源 |
| 字符串拼接 SQL | SQL 注入 | 一律参数化查询 |

## 失败处置表

| 症状 / 报错 | 原因 | 修复 |
|-------------|------|------|
| `schema_explorer.py` 用法错误（缺数据源） | 未提供 `--input` 也未提供 `--sqlite` | 恰好提供一个；二者互斥 |
| `query_optimizer.py` 对 `--query` 报 file-not-found | 路径按文件处理但不存在 | 改传带引号的 SQL 字符串，或核对 `.sql` 路径 |
| 迁移模板不符合意图 | 变更措辞未被识别 | 改述为 "add/drop/rename column X in table Y" |
| 方言输出错误 | 未传 `--dialect`，默认 postgres | 始终传与用户引擎匹配的 `--dialect` |
| 生成的 SQL 在目标引擎上报错 | 共享代码用了方言专属语法 | 查上方方言差异表；方言特性用适配层封装 |

## 交付标准

- 成功定义：方言正确、附优化依据的 SQL，或带配套 down 脚本的迁移模板，或忠实反映真实数据源的 Schema 文档。
- 产物命名：迁移文件 `<timestamp>_<name>.up.sql` / `.down.sql`（或按 `--format` 用 Alembic/Prisma）；Schema 文档 `schema_doc.md` / `.json`。
- 保存位置：迁移存项目的 `migrations/` 目录；Schema 文档存 `docs/` 或项目根目录。
- 完整性核验：每条查询过优化器无反模式告警（或告警已被有意豁免）；每个迁移都有 down 脚本；Schema 文档覆盖内省数据源中的所有表。

## 安全红线

- 绝不把生成的 SQL 直接打到在线库上执行——产物是评审用的。破坏性 DDL（DROP/DELETE/TRUNCATE）必须向用户标出。
- 凭据放环境变量或连接配置，绝不内联进查询或文档。
- 上面的 `pg_dump`/`mysqldump` 命令供用户侧执行；仅在用户明确要求并提供凭据时运行。

## 参考

- `references/query_patterns.md` — 写 JOIN、CTE、窗口函数或 JSON 操作时读
- `references/optimization_guide.md` — 解读 EXPLAIN 计划或选索引类型时读
- `references/orm_patterns.md` — 任务落在 ORM 内（Prisma/Drizzle/TypeORM/SQLAlchemy）时读

## 相关技能

| 技能 | 关系 |
|------|------|
| **database-designer** | Schema 架构、规范化分析、ERD 生成、RLS/多租户模式 |
| **migration-architect** | 复杂多步迁移编排 |
| **api-design-reviewer** | 确保 API 端点与查询模式对齐 |
| **observability-platform** | 查询性能监控、慢查询告警 |
