---
name: database-designer
description: "Use when the user asks to design database schemas, design database tables, design table structure, create ERD diagrams, add indexes, normalize schemas, plan data migrations, add multi-tenancy or row-level security, generate seed data, optimize queries, choose between SQL and NoSQL, or model data relationships. Do NOT use for executing schema changes against a live database."
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

# Database Design Assistant

Uses tools to support schema design and evolution: automated normalization analysis, ERD generation, index optimization based on real query patterns, and zero-downtime migration planning. It only does analysis and plan generation — it never executes schema changes against a live database.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| Current schema | Required | SQL DDL file or JSON schema (samples in `assets/sample_schema.sql` / `sample_schema.json`) |
| Hot query patterns | Conditionally required | Query-pattern JSON for index optimization (copy `assets/sample_query_patterns.json`, fill in the user's queries) |
| Target schema | Conditionally required | The second schema JSON when generating a migration |
| Database engine | Optional | PostgreSQL (SQL samples default to it), MySQL, SQLite, SQL Server |
| Multi-tenancy / RLS / seed-data needs | Optional | Triggers the schema-design-playbook workflow |

When inputs are missing, ask for all at once: "Please provide: (1) current schema (DDL file or JSON), (2) the hottest queries (for indexing), (3) the target schema if you want a migration plan, (4) target engine and tenant/RLS requirements. Everything else runs on defaults."

## Pre-flight Checks

Probe one by one; on any failure → give the fix and STOP:

```bash
python3 --version   # expected 3.8+; on failure: install python3
# Self-check: python3 scripts/schema_analyzer.py --help / index_optimizer.py / migration_generator.py should all exit 0; on failure: script missing → check the skill directory
test -f <schema-input>   # expected exit code 0; on failure: file missing → ask the user for the DDL/JSON schema
```

## Workflow

Use the tools; don't analyze schemas by hand. All paths are relative to this skill directory; sample inputs are in `assets/`.

### Step 1: Analyze the schema

```bash
python3 scripts/schema_analyzer.py --input assets/sample_schema.sql --generate-erd --output-format json -o analysis.json   # bundled sample DDL; swap in schema.sql for your real schema
```

Expected: `analysis.json` contains normalization findings, missing constraints, naming issues, and a Mermaid ERD (`--erd-only` outputs just the ERD). Show the ERD to the user; fix the flagged issues before optimizing. On failure: a DDL parse error → confirm the SQL dialect is supported, or convert to a JSON schema; a large schema with zero findings → confirm `--input` points at DDL, not a data-bearing dump.

### Step 2: Optimize indexes based on real query patterns

```bash
python3 scripts/index_optimizer.py --schema assets/sample_schema.json --queries assets/sample_query_patterns.json --analyze-existing --format json -o indexes.json
```

First write the user's hot queries into the query-pattern JSON (copy `assets/sample_query_patterns.json`). Expected: a priority-ordered list of CREATE INDEX recommendations, plus redundant-index cleanup items. On failure: zero recommendations → the queries may be too few or too simple; ask the user for the real workload; `--min-priority` (1=highest, 4=lowest, default 4) controls the cutoff.

### Step 3: Generate the migration

```bash
python3 scripts/migration_generator.py --current assets/sample_schema.json --target assets/target_schema_sample.json --zero-downtime --format sql -o migration.sql   # bundled sample (add-column diff); swap in two schema JSONs for your real scenario
```

Expected: `migration.sql` contains ALTER statements; `--zero-downtime` emits an expand-contract plan. On failure: the two schema JSONs don't match the analyzer's output structure → regenerate with Step 1.

> **Boundary / split with sql-database-assistant**: this skill's `migration_generator.py` does **schema-diff migrations** — it takes two schema JSONs and outputs ALTER + rollback + zero-downtime plans. If the need is "describe the change in one natural-language sentence and generate an up/down migration template", use `sql-database-assistant`'s same-name script (`--change "..."`); the two have different responsibilities and sit upstream/downstream of each other.

### Step 4: Verify the closed loop

Rerun Step 1 against the *target* schema and assert the first round's findings are gone; run `migration_generator.py --validate-only` before delivering the migration. Never execute the migration — hand the SQL to the user.

## Schema Design Playbook (Multi-tenancy, RLS, Seed Data)

→ Cross-cutting concerns (tenant isolation, soft deletes, audit trails), PostgreSQL RLS policies, and seed-data guidance are in references/schema-design-playbook.md; full example schemas are in references/full-schema-examples.md

## Query Generation Patterns

### SELECT and JOINs

```sql
-- INNER JOIN: keep only matching rows
SELECT o.id, c.name, o.total
FROM orders o
INNER JOIN customers c ON c.id = o.customer_id;

-- LEFT JOIN: keep the whole left table, fill NULL where unmatched
SELECT c.name, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.name;

-- Self-join: hierarchical data (employee/manager)
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id;
```

### Common Table Expressions (CTE)

```sql
-- Recursive CTE to walk the org chart
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

-- RANK leaves gaps on ties; DENSE_RANK doesn't
SELECT name, score, RANK() OVER (ORDER BY score DESC) AS rank FROM leaderboard;

-- LAG/LEAD to compare adjacent rows
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

Every migration must have a reversible counterpart. Timestamp-prefixed filenames guarantee ordering:

```text
migrations/
├── 20260101_000001_create_users.up.sql
├── 20260101_000001_create_users.down.sql
├── 20260115_000002_add_users_email_index.up.sql
└── 20260115_000002_add_users_email_index.down.sql
```

### Zero-Downtime Migration (Expand/Contract)

1. **Expand** — add the new column/table (nullable, with a default)
2. **Migrate data** — backfill in batches; dual-write on the app side
3. **Switch** — the app switches reads to the new column; stop writing the old column
4. **Contract** — drop the old column in a later migration

### Data Backfill Strategy

```sql
-- Update in batches to avoid long-transaction locks
UPDATE users SET email_normalized = LOWER(email)
WHERE id IN (SELECT id FROM users WHERE email_normalized IS NULL LIMIT 5000);
-- Loop until it affects 0 rows
```

### Rollback Procedure

- Before going to production, test `down.sql` on staging
- Keep the rollback window short — once the contract step has run, rollback can only be via a new forward migration
- For irreversible changes (dropping a column with data), take a logical backup first

## Performance Optimization

### Index Strategy

| Index type | Use case | Example |
|----------|----------|------|
| **B-tree** (default) | Equality, ranges, ORDER BY | `CREATE INDEX idx_users_email ON users(email);` |
| **GIN** | Full-text, JSONB, arrays | `CREATE INDEX idx_docs_body ON docs USING gin(to_tsvector('english', body));` |
| **GiST** | Geometric, range types, nearest-neighbor | `CREATE INDEX idx_locations ON places USING gist(coords);` |
| **Partial** | Row subsets (smaller size) | `CREATE INDEX idx_active ON users(email) WHERE active = true;` |
| **Covering** | Index-only scans | `CREATE INDEX idx_cov ON orders(customer_id) INCLUDE (total, created_at);` |

### Reading EXPLAIN Plans

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```

Key signals:

- A **Seq Scan** on a large table — missing index
- A **Nested Loop** with over-estimated row counts — consider a hash/merge join or add an index
- **Buffers shared read** far above **hit** — the working set exceeds memory

### N+1 Query Detection

Symptom: the app fires queries row by row (e.g. fetching related records inside a loop).

Fixes:

- Fetch it in one trip with a `JOIN` or subquery
- ORM eager loading (`select_related` / `includes` / `with`)
- GraphQL resolvers using the DataLoader pattern

### Connection Pooling

| Tool | Protocol | Best for |
|------|------|--------|
| **PgBouncer** | PostgreSQL | Transaction/statement-level pooling, low overhead |
| **ProxySQL** | MySQL | Query routing, read/write splitting |
| **Built-in pools** (HikariCP, SQLAlchemy pool) | Any | App-level pooling |

**Rule of thumb:** size the pool as `(2 * CPU cores) + disk spindles`. For cloud SSDs, start at `2 * vCPUs` and tune.

### Read Replicas and Query Routing

- Route all `SELECT` to replicas; writes go to the primary
- Account for replication lag (async usually <1s; sync is 0)
- Probe lag with `pg_last_wal_replay_lsn()` before reading critical data

## Multi-Database Decision Matrix

| Dimension | PostgreSQL | MySQL | SQLite | SQL Server |
|------|-----------|-------|--------|------------|
| **Best for** | Complex queries, JSONB, extensions | Web apps, read-heavy | Embedded, dev/test, edge | Enterprise .NET stacks |
| **JSON support** | Excellent (JSONB + GIN) | Good (JSON type) | Minimal | Good (OPENJSON) |
| **Replication** | Streaming, logical | Group replication, InnoDB cluster | N/A | Always On AG |
| **License** | Open source (PostgreSQL License) | Open source (GPL) / commercial | Public domain | Commercial |
| **Practical limit** | Multi-TB | Multi-TB | ~1 TB (single writer) | Multi-TB |

**Selection guidance:**

- **PostgreSQL** — default choice for new projects; best extensibility and standards compliance
- **MySQL** — existing MySQL ecosystem; simple read-heavy web apps
- **SQLite** — mobile apps, CLI tools, unit-test databases, IoT/edge
- **SQL Server** — enterprise policy mandates it; deep .NET/Azure integration

### NoSQL Considerations

| Database | Model | When to use |
|--------|------|----------|
| **MongoDB** | Document | Flexible schema, rapid prototyping, content management |
| **Redis** | Key-value / cache | Session stores, rate limiting, leaderboards, pub/sub |
| **DynamoDB** | Wide-column | Serverless AWS apps, single-digit-ms latency at any scale |

> Default to SQL. Adopt NoSQL only when the access pattern clearly benefits.

## Sharding and Replication

### Vertical vs Horizontal Splitting

- **Vertical split**: split columns across multiple tables (e.g. extract BLOB columns). Narrows query I/O.
- **Horizontal split (sharding)**: split rows across multiple databases/servers. Required when a single node can't hold the data or can't keep up with throughput.

### Sharding Strategies

| Strategy | How it works | Pros | Cons |
|------|----------|------|------|
| **Hash** | `shard = hash(key) % N` | Even distribution | Resharding is expensive |
| **Range** | Split by date or ID ranges | Simple, good for time series | The latest shard becomes a hot spot |
| **Geographic** | Split by user region | Data locality, compliance | Cross-region queries are hard |

### Replication Modes

| Mode | Consistency | Latency | Use case |
|------|--------|------|----------|
| **Synchronous** | Strong | High write latency | Financial transactions |
| **Async** | Eventual | Low write latency | Read-heavy web apps |
| **Semi-sync** | At least one replica confirms | Medium | Balance of safety and speed |

## Failure Handling Table

| Symptom / error | Cause | Fix |
|-------------|------|------|
| `schema_analyzer.py` DDL parse error | Dialect-specific syntax unsupported | Convert the DDL to JSON schema format and rerun with `--input sample_schema.json` |
| Analyzer finds zero issues on a large schema | The input is a data dump, not DDL | Feed DDL only (`pg_dump --schema-only`) and rerun |
| Index optimizer gives zero recommendations | The query-pattern JSON is empty or too simple | Fill the user's real hot queries into `assets/sample_query_patterns.json` |
| An unexpected destructive DROP appears in the migration | Current/target schemas don't match | Check both JSONs; regenerate with Step 1; confirm with the user before delivery |
| `--validate-only` reports failure | The migration isn't feasible as planned | Fix the schema conflicts (type changes, existing data) and regenerate |

## Delivery Criteria

- Definition of success: an analysis JSON with a Mermaid ERD, a priority list of index recommendations bound to real query patterns, and (if requested) migration SQL that passes validation with rollback/zero-downtime plans.
- Artifact naming: `analysis.json`, `indexes.json`, `migration.sql` (or the name the user specifies via `-o`).
- Save location: working-directory root, or the project's `migrations/` directory (migration SQL timestamp-named as above).
- Completeness verification: every analyzer finding is either fixed in the target schema or explicitly waived; every index recommendation notes the query pattern it serves; `--validate-only` passes.

## Safety Red Lines

- This skill never connects to a live database or performs any operation on one — all artifacts are files for the user to review.
- Migrations containing DROP/DELETE/TRUNCATE must be explicitly flagged to the user before delivery.
- The sample files in `assets/` are synthetic examples, not real production schemas.

## References

- `references/schema-design-playbook.md` — read when designing multi-tenancy, RLS, soft deletes, audit trails, or seed data
- `references/full-schema-examples.md` — read when you need a complete example schema
- `references/database-design-reference.md` — read for general design principles (naming, constraints, types)
- `references/normalization_guide.md` — read when the user asks why the schema is (de)normalized this way
- `references/index_strategy_patterns.md` — read when choosing between index types or composite column order
- `references/database_selection_decision_tree.md` — read when the user is still choosing an engine (SQL vs NoSQL)

## Related Skills

- **sql-database-assistant** — everyday SQL query writing, optimization, and troubleshooting
- **migration-architect** — large-scale cross-engine migration planning, or big schema overhauls
- **senior-backend** — app-layer patterns (connection pooling, ORM best practices)
- **senior-devops** — infrastructure provisioning for database clusters and replicas
