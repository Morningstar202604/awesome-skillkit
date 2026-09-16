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

# Database Designer

Design and evolve database schemas with tool support: automated normalization analysis, ERD generation, index optimization against real query patterns, and zero-downtime migration planning. Analysis and plan generation only — never executes schema changes against a live database.

## 输入清单

| Input | Required | Description |
|-------|----------|-------------|
| Current schema | Required | SQL DDL file or JSON schema (samples in `assets/sample_schema.sql` / `sample_schema.json`) |
| Hot query patterns | Conditional | Query-patterns JSON for index optimization (copy `assets/sample_query_patterns.json` and fill with the user's queries) |
| Target schema | Conditional | Second schema JSON when generating a migration |
| Database engine | Optional | PostgreSQL (default assumption for SQL examples), MySQL, SQLite, SQL Server |
| Multi-tenancy / RLS / seed-data needs | Optional | Triggers the schema-design playbook flow |

Collect missing inputs in one shot: "Please provide: ① the current schema (DDL file or JSON) ② your hottest queries (for index work) ③ the target schema if you want a migration plan ④ target engine and any tenancy/RLS requirements. Everything else I'll default."

## 前置自检

Probe before running; on any failure, give the fix and STOP:

```bash
python3 --version   # expect 3.8+; fail: install python3
python3 scripts/schema_analyzer.py --help >/dev/null 2>&1     # expect exit 0; fail: script missing → check skill dir
python3 scripts/index_optimizer.py --help >/dev/null 2>&1
python3 scripts/migration_generator.py --help >/dev/null 2>&1
test -f <schema-input>   # expect exit 0; fail: file missing → ask user for the DDL/JSON schema
```

## 工作流

Run the tools — do not analyze schemas by hand. All paths relative to this skill folder; sample inputs in `assets/`.

### 步骤 1: Analyze the schema

```bash
python3 scripts/schema_analyzer.py --input schema.sql --generate-erd --output-format json -o analysis.json
```

Expected: `analysis.json` contains normalization findings, missing constraints, naming issues, and a Mermaid ERD (`--erd-only` outputs just the ERD). Show the ERD to the user and fix flagged issues before optimizing.
If it fails: parse errors on the DDL → check the SQL dialect is supported or convert to JSON schema; empty findings on a big schema → confirm `--input` pointed at DDL, not a dump with data.

### 步骤 2: Optimize indexes against real query patterns

```bash
python3 scripts/index_optimizer.py --schema assets/sample_schema.json --queries assets/sample_query_patterns.json --analyze-existing --format json -o indexes.json
```

Write the user's hot queries into a query-patterns JSON first (copy `assets/sample_query_patterns.json`). Expected: a priority-ordered list of CREATE INDEX recommendations plus redundant-index removals.
If it fails: no recommendations → queries may be too few or trivial; ask for the real workload. `--min-priority` (1=highest, 4=lowest, default 4) controls cutoff.

### 步骤 3: Generate the migration

```bash
python3 scripts/migration_generator.py --current current_schema.json --target target_schema.json --zero-downtime --format sql -o migration.sql
```

Expected: `migration.sql` with ALTERs; `--zero-downtime` emits an expand-contract plan.
If it fails: schema JSONs structurally different from analyzer output → regenerate both via 步骤 1.

> **Boundary / 与 sql-database-assistant 的划界**：本技能的 `migration_generator.py` 做 **schema 对比迁移**——输入两份 schema JSON，输出 ALTER + 回滚 + 零停机计划。若需求是"用一句自然语言描述改动，生成 up/down 迁移模板"，请走 `sql-database-assistant` 的同名脚本（`--change "..."`），二者职责不同、互为上下游。

### 步骤 4: Verification loop

Re-run 步骤 1 on the *target* schema and assert the issues found in the first pass are gone; run `migration_generator.py --validate-only` before handing over the migration. Never execute the migration — hand the SQL to the user.

## Schema Design Playbook (multi-tenancy, RLS, seed data)

→ See references/schema-design-playbook.md for cross-cutting concerns (tenant isolation, soft deletes, audit trails), PostgreSQL RLS policies, seed-data guidance, and a full example schema in references/full-schema-examples.md

## Query Generation Patterns

### SELECT with JOINs

```sql
-- INNER JOIN: only matching rows
SELECT o.id, c.name, o.total
FROM orders o
INNER JOIN customers c ON c.id = o.customer_id;

-- LEFT JOIN: all left rows, NULLs for non-matches
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.name;

-- Self-join: hierarchical data (employees/managers)
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

### Common Table Expressions (CTEs)

```sql
-- Recursive CTE for org chart
WITH RECURSIVE org AS (
  SELECT id, name, manager_id, 1 AS depth
  FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.name, e.manager_id, o.depth + 1
  FROM employees e INNER JOIN org o ON o.id = e.manager_id
)
SELECT * FROM org ORDER BY depth, name;
```

### Window Functions

```sql
-- ROW_NUMBER for pagination / dedup
SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
FROM orders;

-- RANK with gaps, DENSE_RANK without gaps
SELECT name, score, RANK() OVER (ORDER BY score DESC) AS rank FROM leaderboard;

-- LAG/LEAD for comparing adjacent rows
SELECT date, revenue,
  revenue - LAG(revenue) OVER (ORDER BY date) AS daily_change
FROM daily_sales;
```

### Aggregation Patterns

```sql
-- FILTER clause (PostgreSQL) for conditional aggregation
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE status = 'active') AS active,
  AVG(amount) FILTER (WHERE amount > 0) AS avg_positive
FROM accounts;

-- GROUPING SETS for multi-level rollups
SELECT region, product, SUM(revenue)
FROM sales
GROUP BY GROUPING SETS ((region, product), (region), ());
```

## Migration Patterns

### Up/Down Migration Scripts

Every migration must have a reversible counterpart. Name files with a timestamp prefix for ordering:

```text
migrations/
├── 20260101_000001_create_users.up.sql
├── 20260101_000001_create_users.down.sql
├── 20260115_000002_add_users_email_index.up.sql
└── 20260115_000002_add_users_email_index.down.sql
```

### Zero-Downtime Migrations (Expand/Contract)

1. **Expand** — add the new column/table (nullable, with default)
2. **Migrate data** — backfill in batches; dual-write from application
3. **Transition** — application reads from new column; stop writing to old
4. **Contract** — drop old column in a follow-up migration

### Data Backfill Strategies

```sql
-- Batch update to avoid long-running locks
UPDATE users SET email_normalized = LOWER(email)
WHERE id IN (SELECT id FROM users WHERE email_normalized IS NULL LIMIT 5000);
-- Repeat in a loop until 0 rows affected
```

### Rollback Procedures

- Always test the `down.sql` in staging before deploying `up.sql` to production
- Keep rollback window short — if the contract step has run, rollback requires a new forward migration
- For irreversible changes (dropping columns with data), take a logical backup first

## Performance Optimization

### Indexing Strategies

| Index Type | Use Case | Example |
|------------|----------|---------|
| **B-tree** (default) | Equality, range, ORDER BY | `CREATE INDEX idx_users_email ON users(email);` |
| **GIN** | Full-text search, JSONB, arrays | `CREATE INDEX idx_docs_body ON docs USING gin(to_tsvector('english', body));` |
| **GiST** | Geometry, range types, nearest-neighbor | `CREATE INDEX idx_locations ON places USING gist(coords);` |
| **Partial** | Subset of rows (reduce size) | `CREATE INDEX idx_active ON users(email) WHERE active = true;` |
| **Covering** | Index-only scans | `CREATE INDEX idx_cov ON orders(customer_id) INCLUDE (total, created_at);` |

### EXPLAIN Plan Reading

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```

Key signals to watch:
- **Seq Scan** on large tables — missing index
- **Nested Loop** with high row estimates — consider hash/merge join or add index
- **Buffers shared read** much higher than **hit** — working set exceeds memory

### N+1 Query Detection

Symptoms: application issues one query per row (e.g., fetching related records in a loop).

Fixes:
- Use `JOIN` or subquery to fetch in one round-trip
- ORM eager loading (`select_related` / `includes` / `with`)
- DataLoader pattern for GraphQL resolvers

### Connection Pooling

| Tool | Protocol | Best For |
|------|----------|----------|
| **PgBouncer** | PostgreSQL | Transaction/statement pooling, low overhead |
| **ProxySQL** | MySQL | Query routing, read/write splitting |
| **Built-in pool** (HikariCP, SQLAlchemy pool) | Any | Application-level pooling |

**Rule of thumb:** Set pool size to `(2 * CPU cores) + disk spindles`. For cloud SSDs, start with `2 * vCPUs` and tune.

### Read Replicas and Query Routing

- Route all `SELECT` queries to replicas; writes to primary
- Account for replication lag (typically <1s for async, 0 for sync)
- Use `pg_last_wal_replay_lsn()` to detect lag before reading critical data

## Multi-Database Decision Matrix

| Criteria | PostgreSQL | MySQL | SQLite | SQL Server |
|----------|-----------|-------|--------|------------|
| **Best for** | Complex queries, JSONB, extensions | Web apps, read-heavy workloads | Embedded, dev/test, edge | Enterprise .NET stacks |
| **JSON support** | Excellent (JSONB + GIN) | Good (JSON type) | Minimal | Good (OPENJSON) |
| **Replication** | Streaming, logical | Group replication, InnoDB cluster | N/A | Always On AG |
| **Licensing** | Open source (PostgreSQL License) | Open source (GPL) / commercial | Public domain | Commercial |
| **Max practical size** | Multi-TB | Multi-TB | ~1 TB (single-writer) | Multi-TB |

**When to choose:**
- **PostgreSQL** — default choice for new projects; best extensibility and standards compliance
- **MySQL** — existing MySQL ecosystem; simple read-heavy web applications
- **SQLite** — mobile apps, CLI tools, unit test databases, IoT/edge
- **SQL Server** — mandated by enterprise policy; deep .NET/Azure integration

### NoSQL Considerations

| Database | Model | Use When |
|----------|-------|----------|
| **MongoDB** | Document | Schema flexibility, rapid prototyping, content management |
| **Redis** | Key-value / cache | Session store, rate limiting, leaderboards, pub/sub |
| **DynamoDB** | Wide-column | Serverless AWS apps, single-digit-ms latency at any scale |

> Use SQL as default. Reach for NoSQL only when the access pattern clearly benefits from it.

## Sharding & Replication

### Horizontal vs Vertical Partitioning

- **Vertical partitioning**: Split columns across tables (e.g., separate BLOB columns). Reduces I/O for narrow queries.
- **Horizontal partitioning (sharding)**: Split rows across databases/servers. Required when a single node cannot hold the dataset or handle the throughput.

### Sharding Strategies

| Strategy | How It Works | Pros | Cons |
|----------|-------------|------|------|
| **Hash** | `shard = hash(key) % N` | Even distribution | Resharding is expensive |
| **Range** | Shard by date or ID range | Simple, good for time-series | Hot spots on latest shard |
| **Geographic** | Shard by user region | Data locality, compliance | Cross-region queries are hard |

### Replication Patterns

| Pattern | Consistency | Latency | Use Case |
|---------|------------|---------|----------|
| **Synchronous** | Strong | Higher write latency | Financial transactions |
| **Asynchronous** | Eventual | Low write latency | Read-heavy web apps |
| **Semi-synchronous** | At-least-one replica confirmed | Moderate | Balance of safety and speed |

## 失败处置表

| Symptom / Error | Cause | Fix |
|-----------------|-------|-----|
| `schema_analyzer.py` DDL parse errors | Dialect-specific syntax unsupported | Convert the DDL to JSON schema format, then re-run with `--input sample_schema.json` |
| Analyzer finds nothing on a large schema | Input was a data dump, not DDL | Re-run with DDL-only input (`pg_dump --schema-only`) |
| Index optimizer returns no recommendations | Query-patterns JSON empty or trivial | Fill `assets/sample_query_patterns.json` with the user's real hot queries |
| Migration contains destructive DROPs unexpectedly | Current/target schema mismatch | Inspect both JSONs; regenerate via 步骤 1; confirm with user before delivering |
| `--validate-only` reports failures | Migration infeasible as planned | Fix schema conflicts (type changes, existing data) and regenerate |

## 交付标准

Success definition: analysis JSON with a Mermaid ERD, an index recommendation list tied to real query patterns, and (when requested) a validated migration SQL with rollback/zero-downtime plan.
Artifact naming: `analysis.json`, `indexes.json`, `migration.sql` (or user-specified names via `-o`).
Save location: working directory root, or the project's `migrations/` folder for migration SQL following the timestamp naming above.
Verify completeness: every analyzer finding is either fixed in the target schema or explicitly waived; every index recommendation cites the query pattern it serves; `--validate-only` passes on the migration.

## 安全红线

- Never connect to or execute against a live database from this skill — all outputs are files for user review.
- Migrations containing DROP/DELETE/TRUNCATE must be called out explicitly to the user before handover.
- Sample files in `assets/` are synthetic examples, not real production schemas.

## 参考

- `references/schema-design-playbook.md` — read when designing for multi-tenancy, RLS, soft deletes, audit trails, or seed data
- `references/full-schema-examples.md` — read when you need a complete worked example schema
- `references/database-design-reference.md` — read for general design principles (naming, constraints, types)
- `references/normalization_guide.md` — read when the user asks why a schema is (de)normalized a certain way
- `references/index_strategy_patterns.md` — read when choosing between index types or composite orderings
- `references/database_selection_decision_tree.md` — read when the user is still choosing an engine (SQL vs NoSQL)

## Cross-References

- **sql-database-assistant** — query writing, optimization, and debugging for day-to-day SQL work
- **migration-architect** — large-scale migration planning across database engines or major schema overhauls
- **senior-backend** — application-layer patterns (connection pooling, ORM best practices)
- **senior-devops** — infrastructure provisioning for database clusters and replicas
