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

# SQL Database Assistant

The operational companion to database design. While **database-designer** focuses on schema architecture, ERD modeling, and multi-tenancy patterns, this skill covers the day-to-day: writing queries, optimizing performance, generating migrations, and bridging the gap between application code and database engines.

## Core Capabilities

- **Natural Language to SQL** — translate requirements into correct, performant queries
- **Schema Exploration** — introspect live databases across PostgreSQL, MySQL, SQLite, SQL Server
- **Query Optimization** — EXPLAIN analysis, index recommendations, rewrite patterns
- **Migration Generation** — up/down scripts, zero-downtime strategies, rollback plans
- **ORM Integration** — Prisma, Drizzle, TypeORM, SQLAlchemy patterns and escape hatches

### Tools

| Script | Purpose |
|--------|---------|
| `scripts/query_optimizer.py` | Static analysis of SQL queries for performance issues |
| `scripts/migration_generator.py` | Generate migration file templates from change descriptions |
| `scripts/schema_explorer.py` | Turn introspection results (or a SQLite file) into schema documentation |

> **Boundary / 与 database-designer 的划界**：本技能的 `migration_generator.py` 做 **自然语言 → 迁移模板**（`--change "add column ..." → up/down 文件`）。若需求是"对比两份 schema JSON、生成含回滚与零停机（expand-contract）的正式迁移 SQL"，请走 `database-designer` 的同名脚本（`--current/--target`），二者职责不同、互为上下游。

## 输入清单

| Input | Required | Description |
|-------|----------|-------------|
| SQL query or file | Conditional | Query text or `.sql` path, for optimization requests |
| Change description | Conditional | Natural-language schema change, for migration requests |
| Introspection source | Conditional | Introspection JSON/CSV file, or a SQLite `.db` file, for schema exploration |
| Dialect | Optional | `postgres` (default), `mysql`, `sqlite`, `sqlserver` |
| Output format | Optional | stdout by default; `--json` / `--output <file>` per tool |

Collect missing inputs in one shot: "Please provide: ① the query / change description / introspection data (whichever fits the task) ② target dialect (postgres/mysql/sqlite/sqlserver) ③ output format and destination. Everything else I'll default."

## 前置自检

Probe before running; on any failure, give the fix and STOP:

```bash
python3 --version   # expect 3.8+; fail: install python3
python3 scripts/query_optimizer.py --help >/dev/null 2>&1       # expect exit 0; fail: script missing → check skill dir
python3 scripts/migration_generator.py --help >/dev/null 2>&1
python3 scripts/schema_explorer.py --help >/dev/null 2>&1
```

Additional checks per task: optimization needs only query text; migration generation needs only the change description; schema exploration needs an introspection file (or SQLite file — verify it exists and is readable before passing `--sqlite`).

## Natural Language to SQL

### Translation Patterns

When converting requirements to SQL, follow this sequence:

1. **Identify entities** — map nouns to tables
2. **Identify relationships** — map verbs to JOINs or subqueries
3. **Identify filters** — map adjectives/conditions to WHERE clauses
4. **Identify aggregations** — map "total", "average", "count" to GROUP BY
5. **Identify ordering** — map "top", "latest", "highest" to ORDER BY + LIMIT

### Common Query Templates

**Top-N per group (window function)**
```sql
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
  FROM employees
) ranked WHERE rn <= 3;
```

**Running totals**
```sql
SELECT date, amount,
  SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM transactions;
```

**Gap detection**
```sql
SELECT curr.id, curr.seq_num, prev.seq_num AS prev_seq
FROM records curr
LEFT JOIN records prev ON prev.seq_num = curr.seq_num - 1
WHERE prev.id IS NULL AND curr.seq_num > 1;
```

**UPSERT (PostgreSQL)**
```sql
INSERT INTO settings (key, value, updated_at)
VALUES ('theme', 'dark', NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = EXCLUDED.updated_at;
```

**UPSERT (MySQL)**
```sql
INSERT INTO settings (key_name, value, updated_at)
VALUES ('theme', 'dark', NOW())
ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = VALUES(updated_at);
```

> See references/query_patterns.md for JOINs, CTEs, window functions, JSON operations, and more.

## Schema Exploration

### Introspection Queries

**PostgreSQL — list tables and columns**
```sql
SELECT table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

**PostgreSQL — foreign keys**
```sql
SELECT tc.table_name, kcu.column_name,
  ccu.table_name AS foreign_table, ccu.column_name AS foreign_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

**MySQL — table sizes**
```sql
SELECT table_name, table_rows,
  ROUND(data_length / 1024 / 1024, 2) AS data_mb,
  ROUND(index_length / 1024 / 1024, 2) AS index_mb
FROM information_schema.tables
WHERE table_schema = DATABASE()
ORDER BY data_length DESC;
```

**SQLite — schema dump**
```sql
SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name;
```

**SQL Server — columns with types**
```sql
SELECT t.name AS table_name, c.name AS column_name,
  ty.name AS data_type, c.max_length, c.is_nullable
FROM sys.columns c
JOIN sys.tables t ON c.object_id = t.object_id
JOIN sys.types ty ON c.user_type_id = ty.user_type_id
ORDER BY t.name, c.column_id;
```

### Generating Documentation from Schema

Run `scripts/schema_explorer.py` — inputs are mutually exclusive and one is required:

```bash
# From a SQLite database (opened read-only), single table filter, JSON output
python3 scripts/schema_explorer.py --sqlite app.db --table users --json

# From an introspection result file (JSON/CSV; `-` reads stdin), write Markdown doc
python3 scripts/schema_explorer.py --input introspection.json -o schema_doc.md
```

Expected: Markdown schema doc on stdout, or at the `-o` path; `--json` switches to normalized JSON.
If it fails: neither `--input` nor `--sqlite` given → the script exits with a usage error; supply one source. Malformed introspection file → regenerate it with the queries above first.

## Query Optimization

### EXPLAIN Analysis Workflow

1. **Run EXPLAIN ANALYZE** (PostgreSQL) or **EXPLAIN FORMAT=JSON** (MySQL)
2. **Identify the costliest node** — Seq Scan on large tables, Nested Loop with high row estimates
3. **Check for missing indexes** — sequential scans on filtered columns
4. **Look for estimation errors** — planned vs actual rows divergence signals stale statistics
5. **Evaluate JOIN order** — ensure the smallest result set drives the join

### Index Recommendation Checklist

- Columns in WHERE clauses with high selectivity
- Columns in JOIN conditions (foreign keys)
- Columns in ORDER BY when combined with LIMIT
- Composite indexes matching multi-column WHERE predicates (most selective column first)
- Partial indexes for queries with constant filters (e.g., `WHERE status = 'active'`)
- Covering indexes to avoid table lookups for read-heavy queries

### Query Rewriting Patterns

| Anti-Pattern | Rewrite |
|-------------|---------|
| `SELECT * FROM orders` | `SELECT id, status, total FROM orders` (explicit columns) |
| `WHERE YEAR(created_at) = 2025` | `WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'` (sargable) |
| Correlated subquery in SELECT | LEFT JOIN with aggregation |
| `NOT IN (SELECT ...)` with NULLs | `NOT EXISTS (SELECT 1 ...)` |
| `UNION` (dedup) when not needed | `UNION ALL` |
| `LIKE '%search%'` | Full-text search index (GIN/FULLTEXT) |
| `ORDER BY RAND()` | Application-side random sampling or `TABLESAMPLE` |

### Static Analysis Tool

```bash
python3 scripts/query_optimizer.py --query "SELECT * FROM orders WHERE status = 'pending'" --dialect postgres
python3 scripts/query_optimizer.py --query queries.sql --dialect mysql --json
```

Expected: findings list per statement (anti-patterns, index hints); `--json` for machine-readable output.
If it fails: `--query` accepts a SQL string or a `.sql` file path — a missing file path exits with an error; verify the path.

> See references/optimization_guide.md for EXPLAIN plan reading, index types, and connection pooling.

## Migration Generation

### Zero-Downtime Migration Patterns

**Adding a column (safe)**
```sql
-- Up
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Down
ALTER TABLE users DROP COLUMN phone;
```

**Renaming a column (expand-contract)**
```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
-- Step 2: Backfill
UPDATE users SET full_name = name;
-- Step 3: Deploy app reading both columns
-- Step 4: Deploy app writing only new column
-- Step 5: Drop old column
ALTER TABLE users DROP COLUMN name;
```

**Adding a NOT NULL column (safe sequence)**
```sql
-- Step 1: Add nullable
ALTER TABLE orders ADD COLUMN region VARCHAR(50);
-- Step 2: Backfill with default
UPDATE orders SET region = 'unknown' WHERE region IS NULL;
-- Step 3: Add constraint
ALTER TABLE orders ALTER COLUMN region SET NOT NULL;
ALTER TABLE orders ALTER COLUMN region SET DEFAULT 'unknown';
```

**Index creation (non-blocking, PostgreSQL)**
```sql
CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);
```

### Backfill and Rollback Strategies

- **Batch updates** — chunks of 1000-10000 rows to avoid lock contention; **dual-write** old and new columns during transition; verify row counts after each batch
- Every migration must have a reversible down script. For irreversible changes: `pg_dump` the affected tables first, keep feature flags to switch reads, or hold a shadow-table copy during the window

### Migration Generator Tool

```bash
python3 scripts/migration_generator.py --change "add email_verified boolean to users" --dialect postgres --format sql
python3 scripts/migration_generator.py --change "rename column name to full_name in customers" --dialect mysql --format alembic --json
```

Expected: up/down migration template (SQL) or Alembic/Prisma template per `--format` (`sql`/`prisma`/`alembic`); `--output` writes to a file instead of stdout.
If it fails: unrecognized change phrasing → restate the change as "add/drop/rename column X to/in table Y"; unsupported dialect → one of the four choices above.

## Multi-Database Support

### Dialect Differences

| Feature | PostgreSQL | MySQL | SQLite | SQL Server |
|---------|-----------|-------|--------|------------|
| UPSERT | `ON CONFLICT DO UPDATE` | `ON DUPLICATE KEY UPDATE` | `ON CONFLICT DO UPDATE` | `MERGE` |
| Boolean | Native `BOOLEAN` | `TINYINT(1)` | `INTEGER` | `BIT` |
| Auto-increment | `SERIAL` / `GENERATED` | `AUTO_INCREMENT` | `INTEGER PRIMARY KEY` | `IDENTITY` |
| JSON | `JSONB` (indexed) | `JSON` | Text (ext) | `NVARCHAR(MAX)` |
| Array | Native `ARRAY` | Not supported | Not supported | Not supported |
| CTE (recursive) | Full support | 8.0+ | 3.8.3+ | Full support |
| Window functions | Full support | 8.0+ | 3.25.0+ | Full support |
| Full-text search | `tsvector` + GIN | `FULLTEXT` index | FTS5 extension | Full-text catalog |
| LIMIT/OFFSET | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `LIMIT n OFFSET m` | `OFFSET m ROWS FETCH NEXT n ROWS ONLY` |

### Compatibility Tips

- **Always use parameterized queries** — prevents SQL injection across all dialects
- **Avoid dialect-specific functions in shared code** — wrap in adapter layer
- **Test migrations on target engine** — `information_schema` varies between engines
- **Use ISO date format** — `'YYYY-MM-DD'` works everywhere
- **Quote identifiers** — use double quotes (SQL standard) or backticks (MySQL)

## ORM Patterns

### Prisma

**Schema definition**
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

**Migrations**: `npx prisma migrate dev --name add_user_email`
**Query API**: `prisma.user.findMany({ where: { email: { contains: '@' } }, include: { posts: true } })`
**Raw SQL escape hatch**: `prisma.$queryRaw\`SELECT * FROM users WHERE id = ${userId}\``

### Drizzle

**Schema-first definition**
```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
});
```

**Query builder**: `db.select().from(users).where(eq(users.email, email))`
**Migrations**: `npx drizzle-kit generate:pg` then `npx drizzle-kit push:pg`

### TypeORM

**Entity decorators**
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

**Repository pattern**: `userRepo.find({ where: { email }, relations: ['posts'] })`
**Migrations**: `npx typeorm migration:generate -n AddUserEmail`

### SQLAlchemy

**Declarative models**
```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    posts = relationship('Post', back_populates='author')
```

**Session management**: Always use `with Session() as session:` context manager
**Alembic migrations**: `alembic revision --autogenerate -m "add user email"`

> See references/orm_patterns.md for side-by-side comparisons and migration workflows per ORM.

## Data Integrity

### Constraint Strategy

- **Primary keys** — every table must have one; prefer surrogate keys (serial/UUID)
- **Foreign keys** — enforce referential integrity; define ON DELETE behavior explicitly
- **UNIQUE constraints** — for business-level uniqueness (email, slug, API key)
- **CHECK constraints** — validate ranges, enums, and business rules at the DB level
- **NOT NULL** — default to NOT NULL; make nullable only when genuinely optional

### Transaction Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Use Case |
|-------|-----------|-------------------|-------------|----------|
| READ UNCOMMITTED | Yes | Yes | Yes | Never recommended |
| READ COMMITTED | No | Yes | Yes | Default for PostgreSQL, general OLTP |
| REPEATABLE READ | No | No | Yes (InnoDB: No) | Financial calculations |
| SERIALIZABLE | No | No | No | Critical consistency (billing, inventory) |

### Deadlock Prevention

1. **Consistent lock ordering** — always acquire locks in the same table/row order
2. **Short transactions** — minimize time between first lock and commit
3. **Advisory locks** — use `pg_advisory_lock()` for application-level coordination
4. **Retry logic** — catch deadlock errors and retry with exponential backoff

## Backup & Restore

### PostgreSQL
```bash
# Full backup
pg_dump -Fc --no-owner dbname > backup.dump
# Restore
pg_restore -d dbname --clean --no-owner backup.dump
# Point-in-time recovery: configure WAL archiving + restore_command
```

### MySQL
```bash
# Full backup
mysqldump --single-transaction --routines --triggers dbname > backup.sql
# Restore
mysql dbname < backup.sql
# Binary log for PITR: mysqlbinlog --start-datetime="2025-01-01 00:00:00" binlog.000001
```

### SQLite
```bash
# Backup (safe with concurrent reads)
sqlite3 dbname ".backup backup.db"
```

Backup hygiene: automate backups, test restores regularly, keep offsite copies — an untested backup is not a backup.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| `SELECT *` | Transfers unnecessary data, breaks on schema changes | Explicit column list |
| Missing indexes on FK columns | Slow JOINs and cascading deletes | Add indexes on all foreign keys |
| N+1 queries | 1 + N round trips; ORM lazy-loading in loops shows as many identical SELECTs | Eager loading (`include`/`joinedload`), `WHERE id IN (...)`, or DataLoader |
| Implicit type coercion | `WHERE id = '123'` prevents index use | Match types in predicates |
| No connection pooling | Exhausts connections under load | PgBouncer, ProxySQL, or ORM pool |
| Unbounded queries | No LIMIT risks returning millions of rows | Always paginate |
| Storing money as FLOAT | Rounding errors | Use `DECIMAL(19,4)` or integer cents |
| God tables | One table with 50+ columns | Normalize or use vertical partitioning |
| Soft deletes everywhere | Complicates every query with `WHERE deleted_at IS NULL` | Archive tables or event sourcing |
| Raw string concatenation | SQL injection | Parameterized queries always |

## 失败处置表

| Symptom / Error | Cause | Fix |
|-----------------|-------|-----|
| `schema_explorer.py` usage error (missing source) | Neither `--input` nor `--sqlite` provided | Supply exactly one source; they are mutually exclusive |
| `query_optimizer.py` file-not-found on `--query` | Path treated as file but missing | Pass SQL as a quoted string, or verify the `.sql` path |
| Migration template misses the intent | Change phrasing not recognized | Restate as "add/drop/rename column X in table Y" |
| Wrong dialect output | `--dialect` not passed, default postgres | Always pass `--dialect` matching the user's engine |
| Generated SQL fails on target engine | Dialect-specific syntax in shared code | Check the Dialect Differences table; wrap dialect features in adapters |

## 交付标准

Success definition: correct, dialect-aware SQL with optimization rationale, or a migration template with a matching down script, or schema documentation reflecting the real source.
Artifact naming: migration files `<timestamp>_<name>.up.sql` / `.down.sql` (or Alembic/Prisma per `--format`); schema docs `schema_doc.md` / `.json`.
Save location: project's `migrations/` folder for migrations; `docs/` or project root for schema documentation.
Verify completeness: every query passes the optimizer without flagged anti-patterns (or flags are consciously waived); every migration has a down script; schema doc covers all tables in the introspection source.

## 安全红线

- Never execute generated SQL against a live database — outputs are review artifacts. Destructive DDL (DROP/DELETE/TRUNCATE) must be flagged to the user.
- Credentials belong in environment variables or connection configs, never inline in queries or docs.
- `pg_dump`/`mysqldump` commands above are for user-side execution; run them only at the user's explicit request with their credentials.

## 参考

- `references/query_patterns.md` — read when composing JOINs, CTEs, window functions, or JSON operations
- `references/optimization_guide.md` — read when interpreting EXPLAIN plans or choosing index types
- `references/orm_patterns.md` — read when the task lives inside an ORM (Prisma/Drizzle/TypeORM/SQLAlchemy)

## Cross-References

| Skill | Relationship |
|-------|-------------|
| **database-designer** | Schema architecture, normalization analysis, ERD generation, RLS/multi-tenancy patterns |
| **migration-architect** | Complex multi-step migration orchestration |
| **api-design-reviewer** | Ensuring API endpoints align with query patterns |
| **observability-platform** | Query performance monitoring, slow query alerts |
