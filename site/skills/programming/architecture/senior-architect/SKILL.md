---
name: senior-architect
description: "This skill should be used when the user asks to "design system architecture", "evaluate microservices vs monolith", "create architecture diagrams", "analyze dependencies", "choose a database", "plan for scalability", "make technical decisions", or "review system design". Use for architecture decision records (ADRs), tech stack evaluation, system design reviews, dependency analysis, and generating architecture diagrams in Mermaid, PlantUML, or ASCII format. 当用户要求 设计系统架构 / 技术选型 / 架构评审 时使用。 Do NOT use for writing detailed implementation code (output stays at architecture level)."
license: Apache-2.0
compatibility: Pure prompt-based; runs Python stdlib scripts via Bash. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: architecture
  pattern: architecture
  tier: powerful
  verified-date: "2026-09-09"
---

# Senior Architect

Architecture design and analysis: generate diagrams (Mermaid/PlantUML/ASCII), analyze dependencies for coupling and circular imports, assess project structure, and work through decision workflows (database, pattern, monolith-vs-microservices) — output stays at architecture level, no implementation code.

## 输入清单

| 输入 | 必需 | 说明 |
|---|---|---|
| 项目目录 | 是 | 待分析项目路径，如 `./my-project` |
| 任务意图 | 是 | 画架构图 / 依赖分析 / 架构评估 / 技术选型 / 评审之一 |
| 图类型 | 画图时必需 | component / layer / deployment |
| 输出格式 | 否 | mermaid（默认）/ plantuml / ascii；分析报告可选 json |

输入缺失时一次性问齐："请提供：① 项目目录；② 本次要做什么（画图/依赖分析/架构评估/选型/评审）；③ 若画图，图类型与格式。"

## 前置自检

逐条执行，任一失败 → 按修复处置后 STOP：

```bash
# 1. Python 3 可用
python3 --version
# 预期：Python 3.8+。

# 2. 三个工具脚本存在
ls scripts/architecture_diagram_generator.py scripts/dependency_analyzer.py scripts/project_architect.py
# 预期：三个文件名（在技能目录内执行）。失败→cd 到技能目录；仍缺→STOP 回报。

# 3. 目标项目目录存在
ls <项目目录> > /dev/null && echo OK
# 预期：OK。失败→向用户确认路径，STOP。
```

## 工作流

### 步骤 1：生成架构图

```bash
python3 scripts/architecture_diagram_generator.py ./my-project --format mermaid --type component
# PlantUML:   --format plantuml --type layer
# ASCII:      --format ascii
# 保存到文件: --output architecture.md（或 -o）
```

- **动作**：从项目结构生成图，类型 `component`（模块关系）/ `layer`（分层）/ `deployment`（部署拓扑）。
- **预期**：stdout 输出对应格式的图代码；Mermaid 输出可被 `graph TD` 等关键字识别。
- **若失败**：空输出或报错 → 项目目录无源码文件，向用户确认目录后 STOP。

### 步骤 2：依赖分析

```bash
python3 scripts/dependency_analyzer.py ./my-project --output json
# 仅查循环依赖: --check circular
# 带建议的详细模式: --verbose
```

- **动作**：解析直接与传递依赖、模块间循环依赖、耦合分（0-100）、过时包；支持 npm/yarn、requirements.txt/pyproject.toml、go.mod、Cargo.toml。
- **预期**：报告含 CIRCULAR/OUTDATED 条目与 Recommendations（或无问题的干净报告）。
- **若失败**：不支持的包管理器 → 报告"该栈不在支持列表"，STOP；JSON 无法解析 → 用 `--verbose` 文本模式重跑。

### 步骤 3：架构评估

```bash
python3 scripts/project_architect.py ./my-project --verbose
# 只查分层违规: --check layers
```

- **动作**：检测架构模式（MVC/layered/hexagonal/microservices 指标及置信度）、god class、混合关注点、分层违规、缺失组件。
- **预期**：报告含 detected pattern + 置信度 + 分层检查结果 + Recommendations。
- **若失败**：检测不到模式 → 项目过小或结构非典型，如实报告置信度低，不编造结论。

### 步骤 4：决策工作流（按意图选一）

**数据库选型**：
1. 数据特征打分：结构化+关系/需 ACID → SQL；schema 灵活/文档型/时序 → NoSQL。
2. 规模：<1M 记录单区域 → PostgreSQL/MySQL；1M-100M 读多 → PostgreSQL+读副本；>100M 全球分布 → CockroachDB/Spanner/DynamoDB；高写吞吐 >10K/sec → Cassandra/ScyllaDB。
3. 一致性：强一致 → SQL 或 CockroachDB；最终一致可接受 → DynamoDB/Cassandra/MongoDB。
4. 用 ADR 记录：背景、备选项、决策与理由、接受的权衡。

**架构模式选型**：团队 1-3 人 → modular monolith；4-10 人 → modular monolith 或 service-oriented；10+ 人 → 考虑 microservices。需独立部署 → microservices；复杂领域逻辑 → DDD；读写比悬殊 → CQRS；需审计轨迹 → Event Sourcing；三方集成多 → Hexagonal。

**Monolith vs Microservices**：团队 <10 人、领域边界不清、要快速迭代、共享库可接受 → monolith。团队可端到端负责、必须独立部署、各组件伸缩需求不同、领域边界清晰 → microservices。默认从 modular monolith 起步，仅当模块伸缩需求显著不同 / 团队需独立部署 / 技术栈约束强制分离时才拆服务。

- **预期**：产出一条明确的推荐 + 依据（引用上述判据），并落成 ADR。
- **若失败**：判据互相冲突（如小团队但要求独立部署）→ 列出冲突点请用户定优先级，STOP。

### 步骤 5：汇总交付

- **动作**：把图、依赖分析、评估、决策汇总为一份评审报告；每项发现附文件/模块定位。
- **预期**：报告引用了各工具的真实输出原文（分数、置信度、条目），不含臆测。
- **若失败**：某工具无结果 → 在报告中标注 "N/A — 工具无输出"，不得补造。

## 参数速查表

| 参数 | 取值 | 说明 |
|---|---|---|
| `--format` | mermaid / plantuml / ascii | 图输出格式（diagram generator） |
| `--type` | component / layer / deployment | 图类型 |
| `--output` | 文件路径 | 写文件，缺省 stdout（diagram generator） |
| `--output` | text / json | 报告格式（dependency_analyzer / project_architect） |
| `--check` | circular / layers | 只跑单项检查（两分析脚本各一） |
| `--verbose` | 布尔 | 详细模式，含建议 |
| `--json` | 布尔 | 机器可读输出 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|---|---|---|
| `unrecognized arguments` | 参数拼写/取值不在速查表内 | 对照 `--help` 输出修正 |
| 图输出为空 | 项目目录无可分析源码 | 确认目录含代码后重跑 |
| 依赖分析报不支持的栈 | 包管理器不在支持列表 | 如实报告限制，STOP |
| 模式检测置信度 < 50% | 项目结构非典型 | 报告低置信度并列出检测到的线索，不硬下结论 |
| `FileNotFoundError` | 不在技能目录执行 | `cd` 到技能目录或用脚本绝对路径 |

## 交付标准

- 成功定义：意图对应的产物齐备（图代码 / 依赖报告 / 评估报告 / ADR），且每项结论可追溯到工具输出或判据表。
- 产物命名：图 `architecture.md`（或 `--output` 指定）；ADR `adr-NNN-<slug>.md`。
- 保存位置：项目根 `docs/` 或用户指定目录；默认对话内交付。
- 完整性验证：Mermaid/PlantUML 代码语法可被对应渲染器解析（可用 `npx -y @mermaid-js/mermaid-cli -i in.mmd -o out.svg` 抽查）；ADR 含背景/备选/决策/权衡四要素。

## 参考

- `references/architecture_patterns.md` — 9 种架构模式的权衡与示例；用户问 "which pattern?"、"microservices vs monolith"、"CQRS"、"event-driven" 时读。
- `references/system_design_workflows.md` — 6 个系统设计分步工作流；用户问 "how to design?"、容量规划、API 设计、迁移时读。
- `references/tech_decision_guide.md` — 技术选型决策矩阵；用户问 "which database/framework/cloud/cache?" 时读。
