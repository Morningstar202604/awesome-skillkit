---
name: supabase-postgres-best-practices
description: Supabase + Postgres 性能与工程最佳实践。当需要设计表结构、建索引、排查慢查询、配置行级安全(RLS)、写迁移、管理连接池与分区、做 Vacuum 与约束治理时，由 fullstack-database-engineer 加载执行。
license: MIT
compatibility: universal
---

# Supabase / Postgres 最佳实践

本 skill 面向 fullstack-database-engineer，聚焦 Supabase 托管 Postgres 的日常建模、性能与安全。

## 何时使用
- 新建表/迁移、加索引、写 RLS 策略；
- 慢查询、连接打满、RLS 拖慢查询；
- 评估分区、约束、vacuum、pg_stat_statements 调优。

## 核心原则
1. **迁移即代码**：所有 DDL 走 migration 工具（Supabase CLI / Flyway），禁止在控制台手改结构。
2. **先看计划再建索引**：用 `EXPLAIN (ANALYZE, BUFFERS)` 确认全表扫描，再决定索引。
3. **RLS 默认开**：public 表必须开 Row Level Security，不依赖"前端不发请求"。
4. **连接池**：Supabase 用 pgbouncer 事务池，应用连 pooler 端口，不直连 5432。
5. **约束兜底**：外键、check、unique、not null 在数据库层，不只靠应用。

## 索引实践
- **覆盖高频 WHERE/JOIN/ORDER BY**：单列 btree 起步，多列按**等值在前、排序在后**排列。
- **部分索引**：`CREATE INDEX ON orders(user_id) WHERE status = 'pending';` 减小索引体积。
- **表达式索引**：对 `lower(email)`、`(json->>'field')` 建表达式索引，不要对整列建。
- **不要过度索引**：每个索引都拖慢写入，先量测再加。
- 查看未用索引：`SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;`

## RLS 模板
```sql
alter table public.profiles enable row level security;

create policy "用户只能看自己的资料"
  on public.profiles for select
  using (auth.uid() = id);

create policy "用户只能更新自己的资料"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);
```
- Service key 绕过 RLS，**绝不能下发到浏览器/客户端**。
- RLS 策略里避免逐行子查询，必要时把关联表也索引好。

## 慢查询排查流程
1. 开 `pg_stat_statements`（Supabase 已默认启用）。
2. 按 `mean_exec_time * calls` 找总成本最高的查询。
3. 对目标 SQL 跑 `EXPLAIN (ANALYZE, BUFFERS)`，看 Seq Scan / 行数估算偏差。
4. 加索引或改写 SQL（避免 `select *`、避免在索引列上包函数）。
5. 复核是否命中索引，观察 `pg_stat_statements` 改善。

## 连接与迁移
- 应用用 Supabase 连接池（port 6543，transaction mode），长连接/事务批量才用直接连接。
- 迁移大表加列/加默认值用在线方式（`ADD COLUMN ... DEFAULT ...` 在 PG11+ 是元数据操作；重写表要锁表，避开高峰）。
- 大表分区：按时间 range（按月/周），老分区 detach 归档。

## 清单（交付前逐项过）
- [ ] 新表默认 `enable row level security`，并写好 select/insert/update 策略。
- [ ] 外键、`not null`、`unique`、`check` 约束齐全。
- [ ] 高频查询有 `EXPLAIN ANALYZE` 证据，索引不是拍脑袋加的。
- [ ] Service key 只在服务端使用，前端只用 anon key + RLS。
- [ ] 所有 DDL 进 migration 文件，可回滚、可审查。
- [ ] 连接走 pooler，未在应用里维持大量长连接。
- [ ] 大表/归档策略已评估分区或 detach。
- [ ] 敏感列（密码 hash、PII）有注释与脱敏约定。

## 易错点
- **在浏览器用 service_role key**：等于把数据库管理员钥匙交给用户，RLS 直接失效。
- **索引列上包函数**：`WHERE lower(email) = ...` 普通索引失效，要建表达式索引。
- **RLS 策略里 N+1 子查询**：每行都查一次，列表接口直接慢百倍；把条件改成 join 或把权限冗余进本表。
- **过度索引**：写入密集表堆了七八个索引，insert/update 变慢；定期清未用索引。
- **迁移在生产手工执行**：环境漂移，必须 CLI migration 可重复。
- **忘记 vacuum 统计信息**：分析信息过旧导致计划走错，autovacuum 正常运行即可，别手动关。
