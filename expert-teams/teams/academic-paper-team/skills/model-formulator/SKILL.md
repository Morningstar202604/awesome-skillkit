---
name: model-formulator
description: "把自然语言研究问题转写成严格数学模型的工具。当用户用大白话描述一个要研究的现象/决策问题（\"想知道哪些因素影响 Y\"\"要在资源约束下求最优分配\"\"想预测未来 X\"），需要抽象成变量、目标函数、约束、假设并明确模型边界时使用。适配 academic-research-designer，输出变量表、假设集、目标与约束的完整数学表述，供后续求解。也用于 数学建模 / 把问题写成模型 / 形式化问题 / 定义变量与约束 / formalize a problem / write a math model / define variables and constraints。不做数值求解（交给 model-solver），不画结果图（交给 result-visualizer）。"
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

# Model Formulator（文字问题 → 数学模型规格）

把文字问题转成结构化数学模型规格（变量 / 约束 / 目标函数 / 模型类型），作为 model-solver 的输入。

本 skill 供「研究设计师」（academic-research-designer）使用。建模最容易翻车的不是算不出来，而是**一开始就把问题抽象错了**：变量定义含糊、假设写不出来、目标函数和研究问题对不上。本 skill 负责把一句大白话逼成一份可求解、可审的数学表述。

## 这是什么

建模五步走：
1. **抽实体**：把自然语言里的对象、因素、关系挑出来。
2. **定变量**：决策变量、外生参数、状态变量、输出变量各归其位，量纲写清。
3. **写假设**：哪些是为了可解而人为简化的，必须显式列出并讨论放宽后果。
4. **立目标与约束**：优化问题写 min/max + 约束；统计问题写待估参数 + 似然/结构；预测问题写输入输出映射。
5. **边界与退化**：极端参数下模型会怎样，哪种情况模型直接失效。

## 何时使用

- 用户说"我想建个模型研究 X"但只给了现象描述。
- 选题确定后、动手写代码前的设计阶段。
- 论文 Method 部分需要把研究问题严格形式化。
- 团队 W1 的 Phase 2 研究设计环节。
- 问题已用文字描述但缺乏数学结构，需要先定变量与目标再求解时。
- 不用于数值求解（已有形式化模型 → model-solver）与结果作图（→ result-visualizer）。

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

## 核心步骤：形式化方法论

1. **复述研究问题**：用"在___条件下，决策/估计/预测___，目标是___"句式写一句；用户确认无误再往下。
2. **列变量表**：
   | 符号 | 含义 | 类型(决策/参数/状态/输出) | 量纲/取值域 |
   |------|------|----------------------------|-------------|
   每个符号全论文唯一，禁止同一符号两义。
3. **区分三类问题**：
   - **优化类**：目标函数 + 等式/不等式约束 + 可行域。
   - **统计/因果类**：结构方程/回归式 + 待估参数 + 识别假设（独立性、外生性、平行趋势等）。
   - **动力/仿真类**：状态转移方程 + 初始条件 + 参数集。
4. **写假设集**：每条假设标注"为什么需要"和"不成立会怎样"；可检验假设 vs 不可检验假设分开。
5. **写完整形式化**：目标函数、全部约束、定义域、边界条件、随机项分布（如随机模型）。
6. **退化检查**：参数取 0、取无穷、样本量极小时模型行为是否合理；不合理处补约束或说明。

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
| 问题描述有歧义，无法定变量 | 输入只有结论诉求，没有数据与决策对象 | 退回用户补齐决策变量、取值范围与约束来源，再形式化 |
| `objective` 方向写反 | min/max 与业务语义相反 | 对照目标描述重核方向，改后重新生成规格 |
| 模型类型选成 LP 但含整数变量 | 忽略了下标或计数型变量 | 改判为 ILP/MIP 并补 `integrality` 字段 |

## 交付标准

- 成功定义：输出含 `model_type` + 非空 `variables` + `objective` + 至少 1 条 `constraints` 的 JSON。
- 产物命名：`model_spec.json`（或用户指定路径）。
- 保存位置：当前工作目录，或 `--output` 指定路径。
- 验证完整性：用 `python3 -c "import json,sys; json.load(open('<path>'))"` 确认 JSON 可解析且含上述字段；随后交给 model-solver。

## 清单

- [ ] 研究问题已用"条件-对象-目标"句式锁定并经用户确认。
- [ ] 变量表填满，每个符号唯一、量纲明确、取值域写清。
- [ ] 问题类型已归类（优化/统计因果/动力仿真），目标与对应形式一致。
- [ ] 假设集 ≥3 条，每条都写了"不成立会怎样"。
- [ ] 目标函数/估计式与研究问题逐词对应，没有多出来的项。
- [ ] 约束完整：定义域、非负性、整数性、耦合关系不漏。
- [ ] 符号在全文（含后续求解脚本）中一致。
- [ ] 极端情形退化已检查，无明显数学矛盾。

## 易错点

- **变量定义口语化**："满意度"必须写成可观测/可操作化的度量（量表均值？复购率？），不能作为裸变量进模型。
- **假设藏在脑子里**："假设市场是完全竞争的"必须写出来；审稿人会追问这条假设不成立怎么办。
- **目标函数偷换问题**：研究问题是"最小化社会成本"，模型里写成"最大化企业利润"，两者差一个外部性项。
- **忽略量纲**：金额和人数直接相加、时间单位混用，求解时才发现对不上；变量表必须带量纲。
- **过度建模**：能线性解决的问题上深度学习；模型复杂度要和数据量匹配，参数比样本多直接过拟合。
- **不留识别假设**：因果类模型不写"无混淆变量""工具变量外生"，结论就只能是相关不是因果。

## 参考

- [references/model-types.md](references/model-types.md) — 选模型类型、看各类示例时读
- [references/notation-guide.md](references/notation-guide.md) — 写变量/目标函数符号约定时读
