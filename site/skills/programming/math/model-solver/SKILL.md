---
name: model-solver
description: "对数学模型做数值求解：LP/MIP（scipy/cvxpy）、ODE/PDE（scipy.integrate）、蒙特卡洛（numpy）。消费 model-formulator 输出的模型规格，返回解与收敛信息。何时使用：模型规格已就绪、需要最优解或积分/抽样结果时。触发场景（中/英）：求解模型 / 选求解器 / 优化问题求解 / solve a model / pick a solver / optimize the problem。排除项：不解释结果或制作展示材料（交给 result-visualizer）。"
license: Apache-2.0
compatibility: Requires scipy, numpy. Optional: cvxpy, pulp, ortools.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Model Solver

对数学模型做数值求解，返回解、目标值与求解器元数据。

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

| 模型类型 | 求解器 | 库 |
|-----------|--------|---------|
| LP | HiGHS / Simplex | scipy.optimize.linprog |
| MIP | CBC / Gurobi | pulp / cvxpy |
| ODE | RK45 / Radau | scipy.integrate.solve_ivp |
| Monte Carlo | 随机抽样 | numpy.random |

- 动作：LP/MIP 走 `scipy.optimize.linprog` 或 `pulp`；ODE 走 `scipy.integrate.solve_ivp`；蒙特卡洛走 `numpy.random`。
- 预期：求解器正常返回，无 `Optimization failed` / `Integration error`。
- 若失败：LP 不可行 → 检查约束是否过紧；ODE 不收敛 → 调 `method`（如 Radau）或 `rtol/atol`；依赖缺失（cvxpy/pulp）→ `pip install <pkg>`。

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
| `Optimization failed` / 不可行 | 约束过紧或冲突 | 放宽约束或检查 `model_type` |
| `Integration error` | ODE 不收敛 | 换 `method=Radau`，调 `rtol/atol` |
| `ModuleNotFoundError: cvxpy` | 可选依赖未装 | `pip install cvxpy pulp ortools` |

## 交付标准

- 成功定义：返回 JSON 中 `status == "success"`，`solution` 为有限数值数组。
- 产物命名：`solution.json`（或 `--output` 指定）。
- 保存位置：当前工作目录或 `--output` 路径。
- 验证完整性：`python3 -c "import json; d=json.load(open('solution.json')); assert d['status']=='success'"`；随后可交给 result-visualizer 作图。

## 参考

- references/solver-options.md — 选求解器、调 method/容差时读
