# Schema Design Playbook (multi-tenancy, RLS, seed data)

> Merged from the former `database-schema-designer` skill (same upstream source,
> alirezarezvani/claude-skills, MIT). That skill duplicated this skill's ERD /
> normalization / index-strategy duties, so its unique material lives here.

## Cross-cutting Schema Concerns

Add these to every production schema during design — retrofitting is expensive:

| Concern | Pattern |
|---------|---------|
| Multi-tenancy | `organization_id` on all tenant-scoped tables + composite indexes leading with it |
| Soft deletes | `deleted_at TIMESTAMPTZ` instead of hard deletes; partial index `WHERE deleted_at IS NULL` |
| Audit trail | `created_by`, `updated_by`, `created_at`, `updated_at` on every table; append-only `audit_log` for regulated domains |
| Optimistic locking | `version INTEGER` column; reject updates where `version` mismatches |

## Requirements → Entities Workflow

1. **Extract entities** from the requirement sentence ("Users can create projects.
   Each project has tasks. Tasks can have labels..."):
   `User, Project, Task, Label, TaskLabel (junction), TaskAssignment, AuditLog`
2. **Map relationships**: `User 1─* Project (owner)`, `Task *─* Label (via junction)`.
3. **Apply cross-cutting concerns** from the table above.
4. Generate the ERD with `schema_analyzer.py --generate-erd`, then validate
   normalization with the same tool before writing application code.

## Row-Level Security (RLS) — PostgreSQL

```sql
-- Enable RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE ROLE app_user;

-- Tenant isolation: users only see rows in their organization
CREATE POLICY tasks_org_isolation ON tasks
  FOR ALL TO app_user
  USING (
    project_id IN (
      SELECT p.id FROM projects p
      JOIN organization_members om ON om.organization_id = p.organization_id
      WHERE om.user_id = current_setting('app.current_user_id')::text
    )
  );

-- Soft delete: never show deleted records
CREATE POLICY tasks_no_deleted ON tasks
  FOR SELECT TO app_user
  USING (deleted_at IS NULL);

-- Set request context at the start of each transaction
SELECT set_config('app.current_user_id', $1, true);
```

**Always test RLS with a non-superuser role** — table owners and superusers
bypass policies silently.

## Seed Data

Generate realistic test data after the schema exists: one organization, a few
users per role, then fan out child rows with randomized statuses/priorities.
Use deterministic seeds in CI (`faker.seed(42)`) so tests are reproducible.
Key properties to cover:

- At least one row exercising every enum/status value
- Boundary data: empty tenant, tenant at plan limits, soft-deleted rows
- Referential spread so no FK points only at dead rows

## ERD Tooling Shortcuts

```bash
npx prisma-erd-generator                                   # Prisma schema -> diagram
npx @dbml/cli prisma2dbml -i schema.prisma | npx dbml-to-mermaid
python3 ../../schema_analyzer.py --input schema.sql --generate-erd   # this skill, DDL/JSON -> Mermaid
```

See `full-schema-examples.md` for a complete multi-tenant task-management SaaS
schema (organizations → projects → tasks → labels/assignments + audit log).
