---
name: agent-designer
description: "Use when the user asks to design a multi-agent system, pick an orchestration pattern (supervisor/swarm/pipeline/sequential/parallel/router/orchestrator/evaluator), scaffold a multi-step agent workflow config, choose between single-agent vs multi-agent approaches, generate tool schemas for agents, or evaluate agent execution logs for cost, latency, and failure bottlenecks. Examples: 'design an agent architecture for research automation', 'scaffold a content-pipeline workflow', 'generate Anthropic tool schemas from these tool descriptions', 'analyze these agent run logs for bottlenecks'. 当用户要求 设计 AI Agent / 多智能体工作流 / 定义工具与角色 时使用。 Do NOT use for scaffolding or writing agent framework config files itself."
license: Apache-2.0
compatibility: Pure prompt-based; may read project structure via Bash.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: workflow
  pattern: single-task
  tier: powerful
  verified-date: "2026-09-09"
---

# Agent Designer — 多智能体系统架构设计

用三个确定性工具（planner / schema generator / evaluator）完成多智能体系统的设计、Schema 生成与运行评估。脚本是工作流本身——planner 能从需求打分选出模式时，不要凭感觉手画架构。
所有命令均在技能目录（本文件所在目录）下执行。

## 何时使用 / 不适用

适用：
- 从需求设计新的多智能体系统（模式选择、角色划分、通信链路）
- 从纯文本工具描述生成可直接接供应商的 tool schema（Anthropic + OpenAI 双格式）
- 评估执行日志：成功率、延迟分布、成本、瓶颈

不适用：Claude Code Workflow-tool 自动化 → `workflow-builder`；运行时多智能体 fan-out → `agenthub`。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| requirements.json | 设计架构时必需 | 复制 `assets/sample_system_requirements.json` 改写；键：`goal`、`tasks[]`、`constraints{max_response_time, budget_per_task, concurrent_tasks}`、`team_size` |
| tool_descriptions.json | 生成 schema 时必需 | 复制 `assets/sample_tool_descriptions.json` 改写；每个 agent 的工具用纯 JSON 描述 |
| execution_logs.json | 评估时必需 | 真实运行日志；dry-run 可直接用 `assets/sample_execution_logs.json` |
| workflow pattern + name | 快速脚手架时必需 | pattern 取 `sequential` / `parallel` / `router` / `orchestrator` / `evaluator` |

缺失时一次性问齐：「请提供：① 你要做的阶段（设计架构 / 生成 schema / 评估日志 / 脚手架）；② 对应的输入 JSON 文件（或让我从 assets/ 样例复制改写）。」

## 前置自检

依次执行；致命项失败 → 修复后 STOP。

```bash
# 1. Python 可用（致命）
python3 --version                                            # 预期：Python 3.x

# 2. 四个脚本就位（致命；必须在技能目录执行）
test -f scripts/agent_planner.py && test -f scripts/tool_schema_generator.py \
  && test -f scripts/agent_evaluator.py && test -f scripts/workflow_scaffolder.py && echo OK
# 预期：OK；失败 → cd 到技能目录重试，仍失败 STOP

# 3. 样例资产就位（致命；步骤输入的模板来源）
test -f assets/sample_system_requirements.json && test -f assets/sample_tool_descriptions.json \
  && test -f assets/sample_execution_logs.json && echo OK
# 预期：OK
```

## 模式决策表

planner 按此表确定性打分选模式——跑它，不要凭感觉挑。

| 选择 | 何时 | 注意 |
|---|---|---|
| Single agent | 单一有界任务，< ~5 个工具 | 不要画蛇添足加 agent |
| Supervisor | 中心拆解任务，专家回报 | Supervisor 会成为瓶颈 |
| Pipeline | 严格顺序阶段 + 交接 | 顺序僵化；最慢阶段卡吞吐 |
| Hierarchical | 多层组织，> ~8 个 agent | 每层都有通信开销 |
| Swarm | 并行对等节点，容错优先于可预测 | 难调试；需共识规则 |

## 参数速查表

| 脚本（run） | 关键参数 | 说明 |
|------|------|------|
| scripts/agent_planner.py | `input_file`；`--format {json,yaml,both}`；`-o` 输出前缀（默认 agent_architecture） | 需求 → 架构 |
| scripts/tool_schema_generator.py | `input_file`；`--validate`；`--format {json,both}`；`-o` 输出前缀 | 工具描述 → 三方 schema |
| scripts/agent_evaluator.py | `input_file`；`--detailed`；`--format {json,both}`；`-o` 输出前缀（默认 evaluation_report） | 日志 → 评估报告 |
| scripts/workflow_scaffolder.py | `pattern {sequential,parallel,router,orchestrator,evaluator}`；`--name`；`--output` | 生成工作流骨架 JSON |

## 工作流

每一步的 JSON 输出即下一步的设计输入。所有路径相对技能目录。

### 步骤 1：设计架构

动作（run）：写 requirements.json（复制 `assets/sample_system_requirements.json` 改写），然后：

```bash
python3 scripts/agent_planner.py requirements.json --format json -o arch
```

预期：生成 `arch.json`，含 `architecture_design`（pattern、agents、communication links）、`mermaid_diagram`、`implementation_roadmap`。读 `architecture_design.pattern` 与每个 agent 的角色清单，并把 mermaid 图呈现给用户。
若失败：输入缺键（如缺 `team_size`）→ 对照样例补齐后重跑。

### 步骤 2：生成工具 Schema

动作（run）：写 tool_descriptions.json（复制 `assets/sample_tool_descriptions.json` 改写），然后：

```bash
python3 scripts/tool_schema_generator.py tool_descriptions.json --validate -o tools
```

预期：生成 `tools.json`（`tool_schemas`、`validation_summary`）及供应商专用 `tools_anthropic.json` / `tools_openai.json`；**门禁：每个工具必须打印 `✓ Valid`**。
若失败：任一 schema 无效 → 修正工具描述后重跑；未经校验的 schema 绝不交给 agent。

### 步骤 3：评估执行日志

动作（run）：系统跑起来后用真实日志评估；dry-run 直接用 `assets/sample_execution_logs.json`：

```bash
python3 scripts/agent_evaluator.py execution_logs.json --detailed -o eval
```

预期：生成 `eval.json`，含 `summary`、`agent_metrics`、`bottleneck_analysis`、`error_analysis`、`cost_breakdown`、`sla_compliance`、`optimization_recommendations`，另有拆分文件 `eval_errors.json`、`eval_recommendations.json`。
若失败：日志 JSON 格式不符 → 对照 `assets/sample_execution_logs.json` 修正字段后重跑。

### 步骤 4：快速脚手架（可选）

动作（run）：在全流程前先拿骨架时：

```bash
# sequential / parallel / router / orchestrator / evaluator 骨架
python3 scripts/workflow_scaffolder.py sequential --name content-pipeline
python3 scripts/workflow_scaffolder.py orchestrator --name incident-triage --output workflows/incident-triage.json
```

预期：生成对应 pattern 的工作流骨架 JSON；`--output` 缺省时打印到 stdout。
若失败：pattern 拼写不在五个枚举值内 → CLI 报错并列出合法值，改正后重跑。

模式模板与最小交接契约（`workflow_id`、`step_id`、`task`、`constraints`、`upstream_artifacts`、`budget_tokens`、`timeout_seconds`）→ 见 references/workflow_patterns.md。

工作流纪律：从满足需求的最小 pattern 起步；交接负载显式且有界；每次外部模型调用都配 retry/timeout 策略；fan-in 汇总前先校验中间输出；放大规模前先用小上下文预算 dry-run。

### 步骤 5：验证闭环

设计未完成，直到全部满足：

1. `tool_schema_generator.py --validate` 报告 0 个无效 schema。
2. `agent_evaluator.py` 对试运行报告 **0 critical issues**（工具发现问题时打印 `CRITICAL: N critical issues`）。若 N > 0：应用 `eval_recommendations.json` 顶部建议，重跑试运行并重新评估。
3. 将输出与 `expected_outputs/` 对照，确认你消费的 schema 形状未漂移。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------|------|------|
| 任一工具打印 `✗ Invalid` / 非全 `✓ Valid` | 工具描述不符合 schema 约束 | 修正 tool_descriptions.json 后重跑步骤 2；未过门禁不进下一步 |
| `CRITICAL: N critical issues`（N>0） | 试运行暴露失败/成本/延迟问题 | 应用 `eval_recommendations.json` 首条建议 → 重跑试运行 → 重新评估 |
| planner 输出缺 `architecture_design` | requirements.json 缺键 | 对照 `assets/sample_system_requirements.json` 补齐重跑 |
| 输出形状与 `expected_outputs/` 不一致 | 脚本版本演进出 schema 漂移 | 以 expected_outputs/ 为准更新消费方，并读 references/ 对应文档 |
| scaffolder 报 pattern 非法 | pattern 不在五个枚举值内 | 从 `sequential/parallel/router/orchestrator/evaluator` 中选 |

## 交付标准

- 成功定义：通过步骤 5 三条门禁（0 无效 schema、0 critical issues、无 schema 漂移），且 mermaid 架构图已呈现给用户。
- 产物命名（由 `-o` 前缀决定）：`arch.json`、`tools.json` + `tools_anthropic.json` + `tools_openai.json`、`eval.json` + `eval_errors.json` + `eval_recommendations.json`；脚手架按 `--output` 指定。
- 保存位置：当前工作目录；建议归档到项目 `design/` 或 `workflows/` 目录。
- 完整性验证：所有产物 `python3 -m json.tool <file>` 可解析；`arch.json` 含 pattern + agent 角色清单；schema 三件套（通用/Anthropic/OpenAI）同时存在且内容一致。

## 参考

- references/agent_architecture_patterns.md —— 步骤 1 选型存疑时读（各模式权衡详解）
- references/workflow_patterns.md —— 步骤 4 用脚手架时读（骨架模板 + 交接契约；合并自 agent-workflow-designer）
- references/tool_design_best_practices.md —— 步骤 2 设计工具时读（schema、幂等性、错误处理规则）
- references/evaluation_methodology.md —— 步骤 3 解读指标时读（评估器实现的指标定义）
