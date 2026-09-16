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
python3 scripts/query_optimizer.py --help >/dev/null 2>&1       # 预期退出码 0；失败：脚本缺失 → 检查技能目录
python3 scripts/migration_generator.py --help >/dev/null 2>&1
python3 scripts/schema_explorer.py --help >/dev/null 2>&1
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
python3 scripts/schema_explorer.py --sqlite app.db --table users --json

# 从内省结果文件（JSON/CSV；`-` 读 stdin）生成 Markdown 文档
python3 scripts/schema_explorer.py --input introspection.json -o schema_doc.md
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

## 多数据库支持

### 方言差异

| 特性 | PostgreSQL | MySQL | SQLite | SQL Server |
|------|-----------|-------|--------|------------|
| UPSERT | `ON CONFLICT DO UPDATE` | `ON DUPLICATE KEY UPDATE` | `ON CONFLICT DO UPDATE` | `MERGE` |
| 布尔 | 原生 `BOOLEAN` | `TINYINT(1)` | `INTEGER` | `BIT` |
| 自增 | `SERIAL` / `GENERATED` | `AUTO_INCREMENT` | `INTEGER PRIMARY KEY` | `IDENTITY` |
| JSON | `JSONB`（可索引） | `JSON` | 文本（扩展） | `NVARCHAR(MAX)` |
| 数组 | 原生 `ARRAY` | 不支持 | 不支持 | 不支持 |
| CTE（递归） | 完整支持 | 8.0+ | 3.8.3+ | 完整支持 |
| 窗口函数 | 完整支持 | 8.0+ | 3.25.0+ | 完整支持 |
| 全文检索 | `tsvector` + GIN | `FULLTEXT` 索引 | FTS5 扩展 | 全文目录 |
| LIMIT/OFFSET | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `OFFSET m ROWS FETCH NEXT n ROWS ONLY` |

### 兼容性要点

- **始终用参数化查询** — 所有方言下防 SQL 注入
- **共享代码避免方言专属函数** — 用适配层封装
- **在目标引擎上测迁移** — `information_schema` 各引擎不同
- **用 ISO 日期格式** — `'YYYY-MM-DD'` 到处可用
- **给标识符加引号** — 双引号（SQL 标准）或反引号（MySQL）

## ORM 模式

### Prisma

**Schema 定义**

```prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id       Int    @id @default(autoincrement())
  title    String
  author   User   @relation(fields: [authorId], references: [id])
  authorId Int
}
```

**迁移**：`npx prisma migrate dev --name add_user_email`

**查询 API**：`prisma.user.findMany({ where: { email: { contains: '@' } }, include: { posts: true } })`

**原生 SQL 逃生通道**：`prisma.$queryRaw\`SELECT * FROM users WHERE id = ${userId}\``

### Drizzle

**Schema 优先定义**

```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
});
```

**查询构造器**：`db.select().from(users).where(eq(users.email, email))`

**迁移**：`npx drizzle-kit generate:pg` 后接 `npx drizzle-kit push:pg`

### TypeORM

**实体装饰器**

```typescript
@Entity()
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ unique: true })
  email: string;

  @OneToMany(() => Post, post => post.author)
  posts: Post[];
}
```

**Repository 模式**：`userRepo.find({ where: { email }, relations: ['posts'] })`

**迁移**：`npx typeorm migration:generate -n AddUserEmail`

### SQLAlchemy

**声明式模型**

```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    posts = relationship('Post', back_populates='author')
```

**Session 管理**：始终用 `with Session() as session:` 上下文管理器

**Alembic 迁移**：`alembic revision --autogenerate -m "add user email"`

> 各 ORM 并排对比与迁移工作流见 references/orm_patterns.md。

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
