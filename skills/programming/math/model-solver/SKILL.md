---
name: model-solver
description: "对数学模型做数值求解：LP/MIP（scipy/cvxpy）、ODE/PDE（scipy.integrate）、蒙特卡洛（numpy）。消费 model-formulator 输出的模型规格，返回解与收敛信息。何时使用：模型规格已就绪、需要最优解或积分/抽样结果时。触发场景（中/英）：求解模型 / 选求解器 / 优化问题求解 / solve a model / pick a solver / optimize the problem。排除项：不解释结果或制作展示材料（交给 result-visualizer）。 何时使用：模型规格已就绪，需要最优解、积分或抽样结果时。触发场景（中/英）：求解模型 / 选求解器 / 优化问题求解 / 算数值解 / solve a model / pick a solver / optimize the problem.排除项：不把文字问题形式化成模型（交给 model-formulator），不解释结果或出图表（交给 result-visualizer）。Use when the user asks 求解模型 / 选求解器 / 优化问题求解 / 算数值解 / solve a model / pick a solver / optimize the problem. Do NOT use when the problem is still in prose and needs formalizing (use model-formulator) or when the ask is result interpretation and charts (use result-visualizer)."
license: Apache-2.0
compatibility: Requires scipy, numpy. Optional: cvxpy, pulp, ortools.
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Model Solver

对数学模型做数值求解，返回解、目标值与求解器元数据。

## 适用决策表

| 情况 | 用不用本技能 | 原因 |
|------|------------|------|
| 连续 LP（目标+线性约束，变量连续） | ✅ 脚本直解 | linprog/HiGHS 主路径 |
| ODE 初值问题 | ✅ 脚本直解 | solve_ivp，`ode_method` 可选 RK45/Radau/BDF/DOP853 |
| 蒙特卡洛估计（正态假设） | ✅ 脚本直解 | 高斯抽样 + p_exceed |
| MIP / MILP / ILP（含整数约束） | ⚠️ 脚本诚实拒绝（rc=2） | linprog 会静默忽略整数约束给出"假解"；装 `pulp` 由 agent 写整数求解路径 |
| 非线性规划 / 二次规划 | ❌ 超出范围 | scipy.optimize 需要梯度与初值，交给 agent 现场写 |
| 文字题还没形式化 | ❌ 先走 model-formulator | 本技能只吃规格 JSON |

## 诚实声明（先读）

- 脚本真实覆盖 **LP / ODE / Monte Carlo 三类**。`compatibility` 里的 cvxpy/pulp/ortools 是"可能用到的生态"而非脚本内置：**脚本从不调用它们**，整数规划需要 agent 自行安装 pulp 并写求解代码。
- `--method` 参数只影响"分派哪个 solver 族"的预留位，**不改变** LP 内部算法（恒 HiGHS）；ODE 的积分方法用 spec 的 `ode_method` 字段。
- `elapsed_ms` 为 `perf_counter` 实测（v1.1 起），可用于粗略对比，但对比求解器性能时应固定样本量/种子并多跑取中位数。
- MIP 求解需求会得到 `status:"unsupported"` + **退出码 2**——这是设计行为：宁可诚实失败，不给连续假解。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| spec | 是 | model-formulator 产出的模型规格 JSON 文件路径 |
| method | 否 | 强制指定求解方法（覆盖自动分派） | 自动 |
| output | 否 | 解结果写入文件 | 标准输出 |

缺失时一次性问齐：「请提供：① spec（模型规格 JSON 路径，通常由 model-formulator 产出）。method/output 我按默认处理。」

## 前置自检

```bash
python3 --version
python3 -c "import scipy, numpy; print('deps OK', scipy.__version__)"
test -f scripts/model_solver.py && echo "OK script present"
```

- 预期：版本号输出；`deps OK` 打印；脚本存在。
- 若失败：缺 scipy/numpy → `pip install scipy numpy`；脚本缺失 → STOP 回报。

## 工作流

### 步骤 1：载入并校验规格

- 动作：读取 spec 文件，确认 `model_type` 与输入字段齐全。

```bash
python3 scripts/model_solver.py --spec model_spec.json --output solution.json
```

- 预期：脚本解析 JSON 成功，按 `model_type` 分派求解器。
- 若失败：`JSON decode error` → spec 不是合法 JSON，退回 model-formulator 重产；缺 `model_type` → 补字段。

### 步骤 2：按类型分派求解

| 模型类型 | 求解器 | 库 | 脚本支持 |
|-----------|--------|---------|---------|
| LP | HiGHS | scipy.optimize.linprog | ✅ |
| MIP/MILP/ILP | CBC / Gurobi | pulp / cvxpy | ⚠️ 诚实拒绝 rc=2，见失败处置表 |
| ODE | RK45/Radau/BDF | scipy.integrate.solve_ivp | ✅（`ode_method` 可选） |
| Monte Carlo | 随机抽样 | random.gauss | ✅ |

- 动作：脚本按 `model_type` 自动分派；MIP 明确拒绝而非静默降级。
- 预期：求解器正常返回，`status=="success"`。
- 若失败：LP 不可行 → 检查约束是否过紧；ODE 不收敛 → spec 加 `ode_method:"Radau"`；依赖缺失 → `pip install scipy numpy`。

## 求解器暗知识（容易翻车的地方）

1. **整数约束被静默忽略是 MIP 最危险的故障模式**。scipy.linprog 是纯连续求解器，喂给它 MIP 会返回一个"看似成功"的连续解——而整数最优与连续最优的差距取决于问题结构，没有普适数字，但完全可能大到让结论失效。v1.1 起脚本显式拒绝，宁可 rc=2 也不交假解。
2. **不可行（infeasible）与无界（unbounded）处置相反**。linprog 的 status 2=不可行（约束互相矛盾→放宽约束），3=无界（目标方向缺约束→补约束或查目标系数符号）。把无界当不可行去"放宽约束"会让问题更糟。v1.1 起两者分开报告。
3. **量级悬殊的约束先缩放再求解**。约束系数跨 6 个数量级（如 0.001 与 1e6 混排）会让 HiGHS 数值不稳定甚至误报不可行；先把变量单位统一到同一量级（千元→万元），解完再换算回去。
4. **蒙特卡洛的 p_exceed 误差按 1/√n 收敛**。1 万次抽样下 5% 尾部概率的标准误约 ±0.2%（绝对值），报告精度别超过 n 支撑的位数——"p=4.87%"这种假精度在 n=10⁴ 时是自欺。

### 步骤 3：校验收敛并输出

- 动作：检查返回 `status` 为 `success`，读取 `solution` / `objective_value` / `iterations`。
- 预期：输出含 `status: "success"` 与数值解。
- 若失败：`status` 非 success → 记录失败原因，回到步骤 2 调整 method/参数。

## 输出格式

```json
{
  "status": "success",
  "solution": [0.5, 1.5],
  "objective_value": 3.5,
  "solver": "scipy.linprog (HiGHS)",
  "iterations": 12
}
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| --spec | 文件路径 | 必需，模型规格 JSON |
| --method | 求解方法名 | 可选，强制覆盖自动分派 |
| --output | 文件路径 | 可选，写入解结果 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `JSON decode error` | spec 非合法 JSON | 退回 model-formulator 重产规格 |
| `status:"unsupported"` + 退出码 2 | MIP/MILP/ILP（脚本诚实拒绝） | `pip install pulp` 后由 agent 写整数求解路径；或确认是否真的需要整数约束 |
| `status:"infeasible"` | 约束过紧或互相矛盾 | 放宽约束 / 检查约束符号；先缩放量级再重试 |
| `status:"unbounded"` | 目标方向缺少约束 | 补上界约束；检查目标系数正负号是否写反 |
| `status:"iteration_limit"` | 迭代上限（罕见） | 缩放变量量级后重试 |
| `Integration error` / ODE 不收敛 | 刚性系统用显式法 | spec 加 `"ode_method": "Radau"` 或 `"BDF"` |
| `ModuleNotFoundError: scipy` | 依赖未装 | `pip install scipy numpy` |

## 交付标准

- 成功定义：返回 JSON 中 `status == "success"`，`solution` 为有限数值数组。
- 产物命名：`solution.json`（或 `--output` 指定）。
- 保存位置：当前工作目录或 `--output` 路径。
- 验证完整性：`python3 -c "import json; d=json.load(open('solution.json')); assert d['status']=='success'"`；随后可交给 result-visualizer 作图。

## 参考

- references/solver-options.md — 选求解器、调 method/容差时读
