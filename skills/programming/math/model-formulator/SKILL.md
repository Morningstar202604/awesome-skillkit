---
name: model-formulator
description: "将自然语言问题形式化为数学模型：识别变量、约束、目标函数与模型类型（ODE/ILP/随机/Bayesian），输出可供 model-solver 消费的模型规格。何时使用：问题已用文字描述但缺乏数学结构时。触发场景（中/英）：数学建模 / 把问题写成模型 / 定义变量与约束 / formalize a problem / write a math model / define variables and constraints。排除项：不对已形式化模型做数值求解（交给 model-solver）。"
license: Apache-2.0
compatibility: Pure Python + LLM assistance. No external solver needed at this step.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Model Formulator

把文字问题转成结构化数学模型规格（变量 / 约束 / 目标函数 / 模型类型），作为 model-solver 的输入。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| problem | 是 | 自然语言问题描述，含实体、数量、关系 |
| domain | 否 | `optimization` / `differential` / `statistical` / `stochastic` / `bayesian` | optimization |
| knowns | 否 | 已知量 JSON，如 `{"routes": 50, "trucks": 5}` | — |
| unknowns | 否 | 待求变量名列表，如 `route_assignment truck_schedule` | — |

缺失时一次性问齐：「请提供：① problem（文字描述）。domain / knowns / unknowns 我会按缺省或自动推断。」

## 前置自检

```bash
# 1. Python 可用
python3 --version
# 2. 脚本存在
test -f scripts/model_formulator.py && echo "OK script present"
```

- 预期：`python3 --version` 输出版本号；脚本存在打印 `OK script present`。
- 若失败：未装 Python → 安装 Python 3.10+ 后重试；脚本缺失 → STOP，回报脚本未随技能分发。

## 工作流

### 步骤 1：解析并分类问题

- 动作：从 problem 抽取实体、数量、关系，判定 domain（确定性 vs 随机、连续 vs 离散）。
- 预期：得到 `domain` 与一个初步模型类型候选（见决策树）。
- 若失败：描述过于模糊 → 回到输入清单要求补充 problem 细节，不要臆测。

### 步骤 2：定义变量与约束

- 动作：列出决策变量、状态变量、目标函数与全部物理/逻辑约束。
- 预期：每个变量有明确类型（如 binary / continuous）与含义。
- 若失败：约束冲突 → 标注为假设或退回步骤 1 重新分类。

### 步骤 3：选择模型类型并生成规格

- 动作：运行脚本生成结构化规格。

```bash
python3 scripts/model_formulator.py \
  --problem "Minimize delivery cost for 50 routes, 5 trucks, time windows 8-18h" \
  --domain optimization \
  --knowns '{"routes": 50, "deliveries": 200, "trucks": 5}' \
  --unknowns route_assignment truck_schedule total_cost \
  --output model_spec.json
```

- 预期：标准输出一段 JSON，含 `model_type`、`variables`、`objective`、`constraints`、`assumptions`、`solver_hint`。若给 `--output` 则同时写入该文件。
- 若失败：argparse 报错（如 domain 不在 choices）→ 用 `--help` 核对取值；网络/文件错误 → 修正路径后重试。

### 步骤 4：模型类型决策

```text
确定性？
├── 是 → 连续？→ ODE/PDE 或非线性优化
│        └ 否 → ILP / 组合优化
└── 否 → 时序？→ 马尔可夫链 / MDP / 仿真
          └ 否 → Bayesian / 统计
```

- 动作：对照决策树确认 `model_type`，写入 `solver_hint`（`cvxpy | scipy.optimize | pulp | ortools`）。
- 预期：`solver_hint` 与 `model_type` 一致。
- 若失败：类型不确定 → 在 `assumptions` 中明确标注简化假设。

## 输出格式

```json
{
  "model_type": "ILP",
  "variables": {
    "x[i,j]": "truck i assigned to delivery j (binary)",
    "y[i]": "truck i used (binary)"
  },
  "objective": "min Σ cost[i,j] * x[i,j] + fixed_cost * y[i]",
  "constraints": [
    "each delivery assigned to exactly 1 truck: Σ_i x[i,j] = 1 ∀j",
    "time window: start_time[j] + service_time[j] + travel_time[i,j] ≤ end_time[j]",
    "truck capacity: Σ_j demand[j] * x[i,j] ≤ capacity[i] ∀i"
  ],
  "assumptions": ["travel time is constant", "no traffic variability"],
  "solver_hint": "cvxpy | scipy.optimize | pulp | ortools",
  "complexity": "NP-hard (VRPTW), MIP solve < 5min expected"
}
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| --problem | 字符串 | 必需，文字问题 |
| --domain | optimization/differential/statistical/stochastic/bayesian | 默认 optimization |
| --knowns | JSON 字符串 | 已知量 |
| --unknowns | 多个字符串 | 待求变量名 |
| --output | 文件路径 | 可选，写入规格 JSON |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `error: argument --domain: invalid choice` | domain 拼写错 | 用 `--help` 核对 5 个合法值 |
| 输出缺少 `constraints` | 问题表述无边界条件 | 退回输入清单补齐约束描述 |
| `solver_hint` 与 `model_type` 不符 | 决策树判定错 | 手动核对决策树并重写规格 |

## 交付标准

- 成功定义：输出含 `model_type` + 非空 `variables` + `objective` + 至少 1 条 `constraints` 的 JSON。
- 产物命名：`model_spec.json`（或用户指定路径）。
- 保存位置：当前工作目录，或 `--output` 指定路径。
- 验证完整性：用 `python3 -c "import json,sys; json.load(open('<path>'))"` 确认 JSON 可解析且含上述字段；随后交给 model-solver。

## 参考

- references/model-types.md — 选模型类型、看各类示例时读
- references/notation-guide.md — 写变量/目标函数符号约定时读
