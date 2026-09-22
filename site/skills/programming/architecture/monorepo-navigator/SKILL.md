---
name: monorepo-navigator
description: "Navigate, manage, and optimize monorepos. Covers Turborepo, Nx, pnpm workspaces, and Lerna. Cross-package impact analysis, selective builds/tests on affected packages, remote caching, dependency graph visualization, and structured multi-repo to monorepo migrations. Use when setting up a new monorepo, optimizing CI for a large workspace, debugging cross-package dependency issues, or planning a multi-repo consolidation. 当用户要求 梳理 monorepo / 大仓导航 / 包依赖关系 时使用。 Do NOT use for building or publishing packages (navigation and impact analysis only)."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: architecture
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Monorepo Navigator

导航、管理与优化 monorepo（Turborepo、Nx、pnpm workspaces、Lerna）：跨包影响面分析、只构建/测试受影响包、依赖图可视化、多仓库 → monorepo 迁移规划。

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| monorepo 根目录 | 是 | 待分析的工作区路径，如 `.` 或 `/path/to/monorepo` |
| 任务意图 | 是 | 梳理结构 / 影响面分析 / CI 优化 / 迁移规划 / 发布编排之一 |
| 变更范围 | 影响面分析必需 | 与哪个基线比较，如 `origin/main` |
| 输出格式 | 否 | 分析报告默认文本，`--json` 供机器消费 |

输入缺失时一次性问齐："请提供：① monorepo 根目录；② 本次要做什么（梳理/影响分析/CI 优化/迁移/发布）；③ 若做影响分析，与哪个分支或提交比较。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. 目标目录存在
ls <monorepo根目录> > /dev/null && echo OK
# 预期：OK。失败→向用户确认路径，STOP。

# 2. 识别工作区类型（至少一种信号命中）
ls <monorepo根目录>/turbo.json <monorepo根目录>/nx.json <monorepo根目录>/pnpm-workspace.yaml <monorepo根目录>/lerna.json <monorepo根目录>/package.json 2>/dev/null
# 预期：至少列出一个文件。全空→不是标准 monorepo，向用户确认意图后 STOP。

# 3. 分析脚本可用
ls scripts/monorepo_analyzer.py
# 预期：文件名（在技能目录内执行）。失败→cd 到技能目录；仍缺→STOP 回报。
```

## 工作流

### 步骤 1：分析工作区

```bash
python3 scripts/monorepo_analyzer.py examples/sample-monorepo   # 随包样例 monorepo（npm workspaces 三包）；你的真实项目换成仓库根
python3 scripts/monorepo_analyzer.py examples/sample-monorepo --json
```

- **动作**：判定 monorepo 类型（Turborepo/Nx/pnpm/Lerna）、workspace 成员、内部依赖图。
- **预期**：输出包清单与依赖关系；`--json` 时含结构化包列表。
- **若失败**：输出为空/报错 → 该目录无可识别 workspace，向用户确认根目录后 STOP。

### 步骤 2：回答任务意图（按意图分派）

- **影响面分析**：基于步骤 1 的依赖图，对共享包 P 回答"改 P 会破坏哪些 app"——遍历反向依赖；命令行场景用 `pnpm -r --filter ...[origin/main] exec test` 或 `npx turbo run build --filter=...[origin/main]` 只跑受影响包。
- **CI 优化**：核对 CI 是否用 `--filter` 限定范围、是否配置 remote cache（`TURBO_TOKEN`/`TURBO_TEAM`）、turbo.json `inputs` 是否把无关文件排除出缓存键。
- **依赖图可视化**：把步骤 1 的依赖关系转成 Mermaid `graph TD` 图。
- **迁移规划**：产出分阶段计划（含 `git filter-repo --to-subdirectory-filter` 保留历史，禁止手工挪文件）。
- **预期**：每个意图产出一份含具体命令的结论，命令与检测到的工具匹配（turbo 项目用 turbo 命令，pnpm 项目用 pnpm 命令）。
- **若失败**：检测到的工具与用户预期不符 → 以检测结果为准并说明依据。

### 步骤 3：给出行动清单

- **动作**：按失败处置表核对现状，把命中的 pitfall 转为带修复命令的行动项；发布编排用 Changesets（`pnpm changeset` + `pnpm changeset publish` 自动替换 `workspace:*`）。
- **预期**：行动清单每项含：改哪个文件、跑什么命令、如何验证。
- **若失败**：某项修复超出"导航与分析"边界（实际构建/发包）→ 声明这是本技能范围外，交回用户或其他技能执行。

## 工具选型速查

| 工具 | 最适合 | 关键特性 |
|---|---|---|
| **Turborepo** | JS/TS monorepo、流水线配置简单 | 一流的远程缓存，配置极简 |
| **Nx** | 大型企业、插件生态 | 项目图、代码生成、affected 命令 |
| **pnpm workspaces** | workspace 协议、磁盘高效 | `workspace:*` 引用本地包 |
| **Lerna** | npm 发布、版本管理 | 批量发布、conventional commits |
| **Changesets** | 现代版本管理（优于 Lerna） | 变更日志生成、预发布通道 |

多数现代组合：**pnpm workspaces + Turborepo + Changesets**

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| PR 上每次全量构建 | `turbo run build` 未加 `--filter` | CI 中一律 `--filter=...[origin/main]` |
| 发布失败：`workspace:*` 残留 | 直接 `npm publish` | 用 `pnpm changeset publish`，自动替换为真实版本号 |
| 无关改动触发全部重建 | turbo.json `inputs` 缓存键过宽 | 把 docs、配置文件排除出 `inputs` |
| 一个包改动拖垮所有类型检查 | 共享 tsconfig 未分层 | 每个包 `extends` 根配置并覆写 `rootDir`/`outDir` |
| 迁移后 git 历史丢失 | 手工移动文件合并 | 改用 `git filter-repo --to-subdirectory-filter` 后再合并 |
| CI 中 remote cache 不生效 | `TURBO_TOKEN`/`TURBO_TEAM` 未配置 | 配好环境变量后用 `turbo run build --summarize` 验证 |
| AI 助手改错包的文件 | CLAUDE.md 过于笼统 | 每个包的 CLAUDE.md 写明 "When working on X, only touch files in apps/X" |

## 最佳实践

1. **根 CLAUDE.md 定义地图** — 记录每个包、用途与依赖规则
2. **每包 CLAUDE.md 定义规则** — 允许什么、禁止什么、测试命令
3. **命令一律用 --filter 限定范围** — 每次变更都全量跑就失去意义了
4. **远程缓存不是可选项** — 没有它，monorepo CI 比多仓库还慢
5. **用 Changesets 而非手工管版本** — 绝不在 monorepo 里手改 package.json 版本号
6. **共享配置放根目录，包内 extends** — tsconfig.base.json、.eslintrc.base.js、jest.base.config.js
7. **合并共享包改动前先做影响分析** — 跑受影响检查，通报爆炸半径
8. **packages/types 保持纯 TypeScript** — 无运行时代码、无依赖，构建与类型检查都快

## 交付标准

- 成功定义：步骤 1 的分析报告覆盖全部 workspace 包与内部依赖；步骤 2/3 的结论引用了报告中的具体包名与命令。
- 产物命名：分析留档 `monorepo-analysis.{txt,json}`（用 `--json` 时）；迁移计划 `monorepo-migration-plan.md`；Mermaid 图内嵌于报告。
- 保存位置：默认对话内交付；留档文件放用户指定目录（不要写入目标 monorepo 除非用户要求）。
- 完整性验证：报告中的每条命令都能在目标仓库上下文中原样执行；影响面清单与依赖图一致。

## 参考

- `references/monorepo-patterns.md` — 常见架构与 CI 模式；做迁移规划或 CI 优化方案时读。
- `references/monorepo-tooling-reference.md` — Turborepo 等工具的详细用法；需要超出速查表的工具细节时读。
