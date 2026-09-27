---
name: model-solver
description: "数学模型数值求解与统计推断工具。当模型已由 model-formulator 形式化完成，需要选择求解算法、跑数值解、做参数估计、检验模型假设、报告收敛性与稳健性时使用。适配 academic-statistical-methodologist，负责求解路径选择、收敛与误差诊断、敏感性/稳健性分析、可复现代码与结果表格输出。也用于 求解模型 / 选求解器 / 优化问题求解 / 算数值解 / solve a model / pick a solver / optimize the problem。不把文字问题形式化成模型（交给 model-formulator），不解释结果或制作图表（交给 result-visualizer）。"
license: Apache-2.0
compatibility: "Requires scipy, numpy. Optional: cvxpy, pulp, ortools."
metadata:
  version: "1.1"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Model Solver（数学模型数值求解）

对数学模型做数值求解，返回解、目标值与求解器元数据。

本 skill 供「统计方法师」（academic-statistical-methodologist）使用。承接 model-formulator 输出的形式化模型，把"纸面模型"跑成"可信数值结果"。审稿人质疑最多的不是答案错，而是：解没收敛你就报数、方法选择没理由、没做稳健性、结果全靠一个随机种子。

## 这是什么

求解四段：
1. **选方法**：根据模型类型（线性/非线性优化、微分方程、概率估计、机器学习）选成熟算法，不自己造轮子。
2. **跑通并诊断**：收敛性、稳定性、数值误差、初值依赖逐项排查。
3. **做检验**：假设检验、多重比较校正、效应量、灵敏度/稳健性分析。
4. **出可复现结果**：固定随机种子、记录环境、代码与数据可追溯。

## 何时使用

- model-formulator 已交付变量表、假设集、目标与约束。
- 用户给了模型问"这个怎么解 / 用什么方法 / 结果对不对"。
- 论文 Results 部分需要数值表、收敛报告、稳健性检验。
- 团队 W1 的 Phase 3 方法分支、Phase 4 结果产出。
- 模型规格已就绪，需要最优解、积分或抽样结果时。
- 不用于文字问题形式化（→ model-formulator）与结果解释/作图（→ result-visualizer）。

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

## 核心步骤：求解方法论

1. **先解析解后数值解**：能推闭式解就不黑箱数值；必须数值化时，说明为什么（非线性耦合/高维/无解析形式）。
2. **方法选型有据**：
   - 线性规划 → 单纯形/内点法（Gurobi/CPLEX/scipy.linprog）。
   - 非线性规划 → 先试 SLSQP/信赖域，非凸问题多初值多跑。
   - 微分方程 → 刚性方程用隐式格式（BDF/Radau），非刚性用 RK45。
   - 统计估计 → 极大似然/贝叶斯，报告标准误与置信区间。
   - 方法选择必须写"为什么不是更简单的替代方法"。
3. **收敛诊断**：
   - 优化：KKT 残差、梯度范数、多次初值是否落到同一解。
   - 迭代法：容差设置、收敛曲线、是否震荡。
   - 随机方法：固定种子 + ≥3 个种子重跑，报均值与标准差。
4. **误差与量纲检查**：残差数量级、单位换算、边界解（解贴在约束上要说明是真最优还是约束太紧）。
5. **稳健性三件套**：
   - 灵敏度：关键参数 ±10%/±20% 扰动，结果方向是否反转。
   - 替代方法：换一种求解/估计方法，结论是否一致。
   - 样本/数据扰动：留一法、bootstrap、剔除异常值后结论是否站住。
6. **可复现打包**：随机种子、依赖版本、随机数据生成脚本、参数表一并交付。

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

## 清单

- [ ] 求解方法与模型类型匹配，且写清"为什么不用更简单的方法"。
- [ ] 收敛证据齐：KKT/梯度/收敛曲线/多初值结果。
- [ ] 随机过程固定种子，并至少 3 个种子重跑报波动。
- [ ] 数值结果与变量量纲核对，无单位错误。
- [ ] 边界解已检查：解贴约束处已讨论是否人为造成。
- [ ] 灵敏度分析完成，参数扰动下结论方向稳定。
- [ ] 至少一种替代方法/数据扰动的稳健性对照。
- [ ] 标准误/置信区间/效应量已报告，不只报 p 值。
- [ ] 代码、数据、环境、种子可一键复现。

## 易错点

- **没收敛就报数**：求解器 warning 没看，迭代未到容差就把结果当最优解。
- **单初值定全局最优**：非凸问题一个初值找到的只是局部最优；必须多初值或启发式全局搜索。
- **只报 p 值不报效应量**：p<0.05 在大样本下毫无意义，必须给效应量与置信区间。
- **多重比较不校正**：跑 20 组检验总有 1 组 p<0.05，必须 Bonferroni/FDR 校正。
- **稳健性走形式**：扰动幅度设成 ±1%，当然"稳健"；要用到参数真实不确定范围内。
- **随机种子玄学**：换个种子结论反转，说明结果本身不稳定，必须在论文里坦白而不是藏起来。
- **自写数值算法**：数值线性代数/ODE 求解自己实现基本必错，直接用成熟库（scipy、CVXPY、Pyomo、stan）。

## 参考

- [references/solver-options.md](references/solver-options.md) — 选求解器、调 method/容差时读
