---
name: migration-architect
description: "Zero-downtime migration planning, compatibility validation, and rollback strategy generation. Tools for system, database, and infrastructure migrations with minimal business impact. Use when planning a database migration, infrastructure cutover, system replacement, or any high-risk transition that needs explicit rollback paths. 当用户要求 规划零停机迁移 / 数据迁移方案 / 双写切换 时使用。 Do NOT use for executing the data migration itself (it produces the plan and scripts)."
license: Apache-2.0
compatibility: Requires network access. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: architecture
  pattern: architecture
  tier: powerful
  verified-date: "2026-09-09"
---

# Migration Architect

用三件工具规划零停机迁移、校验 schema/API 兼容性、生成回滚手册——产出分阶段计划、兼容性报告和逐阶段回滚步骤。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 迁移规格 JSON | 是 | 描述迁移内容的 spec 文件；无现成文件时从 `assets/sample_database_migration.json` 复制改写 |
| 迁移类型 | 是 | database / service / infrastructure（决定兼容性检查 `--type`） |
| 前后 schema/API 文件 | 兼容性检查必需 | `--before` 旧版、`--after` 新版 JSON；样例在 `assets/` |
| 输出目录 | 否 | 三个产物的落盘位置，缺省当前目录 |

输入缺失时一次性问齐："请提供：① 迁移规格 JSON 路径（没有的话我基于 assets 样例帮你起草，需你确认迁移内容）；② 迁移类型（database/service/infrastructure）；③ 做兼容性检查所需的旧/新 schema 文件路径。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。

# 2. 三个工具脚本存在
ls scripts/migration_planner.py scripts/compatibility_checker.py scripts/rollback_generator.py
# 预期：三个文件名（在技能目录内执行）。失败→cd 到技能目录；仍缺→STOP 回报。

# 3. 迁移规格可解析：python3 -c "import json; json.load(open('<migration_spec.json>'))" → 预期 OK；失败→确认 spec 文件，或改用 assets 样例起草，STOP。

# 4. 样例资产在位
ls assets/sample_database_migration.json assets/database_schema_before.json assets/database_schema_after.json
# 预期：三个文件名。缺失→确认仓库完整性后 STOP。
```

## 工作流

命令在技能目录（`skills/programming/architecture/migration-architect/`）内执行。

### 步骤 1：生成迁移计划

```bash
python3 scripts/migration_planner.py --input assets/sample_database_migration.json --format json -o migration_plan.json   # 随包样例 spec；你的真实场景换成 migration_spec.json
```

- **动作**：从迁移规格生成分阶段计划（`phases`）、风险清单（`risks`）、预估时长（`estimated_duration_hours`）。
- **预期**：`migration_plan.json` 生成且含 `phases` 数组（非空）。
- **若失败**：`--validate` 复跑可检查 spec 结构；仍失败 → spec 字段缺失，对照 `assets/sample_database_migration.json` 修正字段后重试。

### 步骤 2：兼容性检查

```bash
python3 scripts/compatibility_checker.py --before assets/database_schema_before.json --after assets/database_schema_compatible.json --type database --format json -o compatibility.json   # 随包样例（相同 schema → 兼容 rc=0）；换成 database_schema_after.json 可演示不兼容报告（rc=1 语义）
```

- **动作**：对比前后 schema/API（`--type database|api`），输出 `overall_compatibility` 与 `breaking_changes_count` / `potentially_breaking_count`。
- **预期**：退出码 0 且 `overall_compatibility: compatible`。
- **若失败**：非 compatible → 列出每个 breaking/potentially-breaking 项交用户决策：修复 schema 重跑，或所有者书面明确接受。**门禁**：两项之一满足前迁移不批准。

### 步骤 3：生成回滚手册

```bash
python3 scripts/rollback_generator.py --input assets/sample_migration_plan.json --format both -o rollback_runbook   # 随包样例 plan（由 migration_planner 对样例 spec 生成）
```

- **动作**：从步骤 1 的计划生成回滚 runbook（json + text 两种格式）。
- **预期**：生成 `rollback_runbook.json` 与 `rollback_runbook.txt`；手册覆盖计划中的每一个 phase。
- **若失败**：报告 `input file missing phases` 类错误 → 说明步骤 1 产物损坏，重跑步骤 1。

### 步骤 4：交付与执行前门禁

- **动作**：交付三产物，并逐项核对执行前门禁：① 兼容性通过（步骤 2）；② 每个 phase 有回滚手册（步骤 3）；③ 回滚步骤已在 staging 演练过；④ 监控与告警就位。
- **预期**：门禁四项全部满足，向用户明确声明"计划就绪，尚未执行迁移"（本技能只产出计划与脚本，不执行迁移）。
- **若失败**：任一门禁不满足 → 列出缺口，STOP；schema 修订后从步骤 1 重跑全部检查。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `--input, -i` | JSON 文件 | migration_planner 读迁移规格；rollback_generator 读迁移计划 |
| `--before / --after` | JSON 文件 | compatibility_checker 的旧/新版本文件 |
| `--type` | database / api | 兼容性检查对象类型 |
| `--format` | json / text / both | 三脚本通用 |
| `--output, -o` | 文件路径前缀 | 产物落盘位置 |
| `--validate` | 布尔 | migration_planner 校验 spec 结构 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| compatibility 退出码非 0 | 检出 breaking changes | 交用户决策：修 schema 重跑或书面接受；不得静默放行 |
| rollback 手册缺 phase | 步骤 1 计划产物损坏 | 重跑步骤 1 再生成手册 |
| `--validate` 报错 | 迁移 spec 字段缺失 | 对照 `assets/sample_database_migration.json` 逐字段补齐 |
| `FileNotFoundError` | 不在技能目录执行 | `cd` 到技能目录或改用脚本绝对路径 |

## 迁移模式速查（选型用）

| 场景 | 模式 | 关键动作 |
|---|---|---|
| 加列/加表 | Expand-Contract | 先加新结构 → 双写 → 回填 → 验证后删旧结构 |
| 大数据集零停机 | CDC / Incremental Sync | 流式捕获变更到目标库，最终一致 |
| 服务替换 | Strangler Fig | 网关分流 → 新服务增量实现 → 旧组件退役 |
| 新旧并行验证 | Parallel Run | 双执行 + 结果比对 → 按置信度切流 |
| 渐进发布 | Canary | 小流量起步 → 盯延迟/错误率/KPI → 分级放量 |
| 新系统劣化自动兜底 | Circuit Breaker | 失败超阈值即回落旧系统，半开探测恢复 |

详细说明与数据对账（行数校验、checksum、delta SQL）见参考文件。

## 交付标准

- 成功定义：`migration_plan.json`（含非空 `phases`/`risks`）、`compatibility.json`（`overall_compatibility` 为 compatible 或破坏项被书面接受）、`rollback_runbook.json` + `.txt`（覆盖全部 phase）三者齐备，且执行前门禁四项满足。
- 产物命名：`migration_plan.json`、`compatibility.json`、`rollback_runbook.{json,txt}`（或用户指定前缀）。
- 保存位置：当前目录或用户指定目录。
- 完整性验证：三个 JSON 均可被 `json.load` 解析；plan 的 phase 列表与 runbook 覆盖的 phase 一一对应。

## 参考

- `references/data_reconciliation_strategies.md` — 数据对账策略（行数、checksum、delta 查询、自动修复）；生成计划后设计验证/对账环节时读。
- `assets/sample_database_migration.json`、`assets/sample_service_migration.json` — 迁移 spec 样例；用户无现成 spec 时复制改写。
- `assets/database_schema_before.json` / `database_schema_after.json` — 兼容性检查样例输入。
- `expected_outputs/` — 各工具样例输出的正确形态，用于核对产物格式。

## CI/CD 集成

```yaml
# 迁移流水线阶段示例
migration_validation:
  stage: test
  script:
    - run_compat_check && run_migration_planner   # 完整命令见上文工作流（compat 用 --before/--after，planner 用 --input）
  artifacts:
    reports:
      - compatibility_report.json
      - migration_plan.json
```
