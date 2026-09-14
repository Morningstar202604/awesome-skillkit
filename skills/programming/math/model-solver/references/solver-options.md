# Solver Options（求解器选型与不可行诊断）

> 配套 model-solver。**不提供性能基准数字**（耗时与规模、稀疏结构、机器强相关，任何跨环境的数字都是误导）。本文只给能力边界、接入方式与诊断方法；需要速度结论时请在你自己的数据与机器上实测。

## 目录
- §0 当前脚本能做什么（含实测到的一处缺陷）
- §1 问题类型 × 库 × 入口对照表
- §2 各库最小可运行示例
- §3 状态码与结果字段
- §4 不可行 / 无界的诊断思路
- §5 松弛定位法（找冲突约束）
- §6 数值与规模注意事项
- §7 交付前检查表

## §0 当前脚本能做什么（含实测到的一处缺陷）

`model_solver.py` 按 `model_type` 字符串分派，实际实现只有三支：

| 分支条件 | 实际行为 |
|---|---|
| 含 `LP` / `ILP` / `MIP` | `solve_lp`：`scipy.optimize.linprog(..., method="highs")`。**不设置整数约束** → ILP/MIP 走到这里得到的是 LP 松弛解（可能不是整数） |
| 含 `ODE` / `PDE` | `solve_ode`：`solve_ivp` 解固定的指数衰减 `dy/dt = -rate*y`，`rate` 取自 spec，默认 0.1；**不是通用 ODE 求解器**（函数体写死） |
| 含 `MONTE` / `STOCHASTIC` | `solve_monte_carlo`：`random.gauss(mu, sigma)` 采样，输出 mean/std/p_exceed；无 seed 参数 |

实测缺陷（本机 scipy 1.17.0 + Python 3.11）：`solve_lp` 读取 `result.iter`，但 `linprog` 的 `OptimizeResult` 只有 `nit` 字段，因此 LP 分支必然抛 `AttributeError: iter`（traceback 终止于 `result.iter`）。**修复**：把 `"iterations": result.iter` 改为 `"iterations": getattr(result, "nit", None)`。若你必须原样运行脚本，先在外部自己调 `linprog`（§2）。

## §1 问题类型 × 库 × 入口对照表

| 问题类型 | 首选 | 备选 | 说明 |
|---|---|---|---|
| LP（线性规划） | `scipy.optimize.linprog`（HiGHS） | PuLP(CBC)、OR-Tools | HiGHS 随 SciPy 分发，无需额外安装 |
| MILP（整数/混合整数） | `scipy.optimize.milp`（HiGHS，SciPy ≥ 1.9，**VERIFY BEFORE USE**） | PuLP(CBC)、OR-Tools CP-SAT | 整数决策必须用这一档，不能用 linprog |
| 凸优化（DCP 可表达） | CVXPY | SciPy | CVXPY 在建模时校验凸性，非凸直接拒绝 |
| 通用非线性（无凸性保证） | `scipy.optimize.minimize` | — | 局部最优，无全局保证；需多起点 |
| 约束满足 / 调度（整数为主） | OR-Tools CP-SAT | — | 连续量需先缩放为整数 |
| ODE（非刚性） | `solve_ivp`（默认 RK45） | — | 刚性问题换 `Radau` / `BDF` |
| 随机/仿真 | `numpy.random.Generator` | `simpy`（离散事件） | 见 simulation-runner 的 `mc-theory.md` |

商业求解器（Gurobi / CPLEX / FICO Xpress）支持 LP/MIP/(部分)凸与非凸，学术许可与授权条款以官方为准（**VERIFY BEFORE USE**：授权与功能范围随版本变化，用前查官网）。开源栈够用时不必引入。

## §2 各库最小可运行示例

### LP — scipy.optimize.linprog
```python
from scipy.optimize import linprog
# min x + y   s.t. x + y <= 10, x >= 0, y >= 0
r = linprog(c=[1, 1], A_ub=[[1, 1]], b_ub=[10], bounds=[(0, None), (0, None)], method="highs")
print(r.status, r.message)      # 预期：0 / Optimization terminated successfully.
print(r.x, r.fun)               # 预期：x 为最优解向量，fun 为最优值
print(r.nit)                    # 迭代数（注意：字段名是 nit，不是 iter）
```

### MILP — scipy.optimize.milp（已在本机验证）
```python
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
# max x + y   s.t. x + y <= 1.5, x,y ∈ {0,1}
res = milp(c=np.array([-1.0, -1.0]),                       # 求最大 → 最小化相反数
           constraints=LinearConstraint(np.array([[1.0, 1.0]]), -np.inf, 1.5),
           integrality=np.array([1, 1]),                   # 1=整数, 0=连续
           bounds=Bounds([0, 0], [1, 1]))
print(res.status, res.message)   # 预期：0 / Optimization terminated successfully. (HiGHS Status 7: Optimal)
print(res.x, res.fun)            # 本机实测输出：[1. 0.] -1.0
```
坑：`integrality` 长度必须等于变量数；约束矩阵每行一条约束；`LinearConstraint(A, lb, ub)` 表示 `lb <= A@x <= ub`，单边约束用 `±np.inf` 补齐。

### MIP — PuLP（CBC 随 PuLP 分发）
```python
import pulp
prob = pulp.LpProblem("assign", pulp.LpMinimize)
x = pulp.LpVariable("x", lowBound=0, cat="Integer")
y = pulp.LpVariable("y", lowBound=0, cat="Integer")
prob += x + y                      # 目标
prob += x + y >= 3                 # 约束（可累加多条）
prob.solve(pulp.PULP_CBC_CMD(msg=False))
print(pulp.LpStatus[prob.status])  # 预期：Optimal / Infeasible / Unbounded
print(x.value(), y.value())
```
坑：状态必须查 `pulp.LpStatus[prob.status]`（字符串），不能直接比较数字；`x.value()` 为 `None` 表示未求出解。

### 凸优化 — CVXPY
```python
import cvxpy as cp
x = cp.Variable(2)
prob = cp.Problem(cp.Minimize(cp.sum_squares(x - 1)), [x >= 0, cp.sum(x) == 1])
prob.solve()                        # 默认求解器由 CVXPY 自动选择
print(prob.status, prob.value, x.value)
```
预期：`prob.status` 为 `optimal`。若模型不满足 DCP 凸性规则，CVXPY 在 `solve()` 时抛 `DCPError`（这是**保护**而非 bug，说明模型非凸，需重构或换 §1 的非线性分支）。想看实际用了哪个求解器：加 `verbose=True` 或查 `prob.solver_stats`（字段名以你本地 CVXPY 文档为准，**VERIFY BEFORE USE**）。

### 非线性 — scipy.optimize.minimize
```python
from scipy.optimize import minimize
r = minimize(lambda x: (x[0] - 1) ** 2 + (x[1] + 2) ** 2, x0=[0.0, 0.0], method="L-BFGS-B",
             bounds=[(-5, 5), (-5, 5)])
print(r.success, r.x, r.fun)        # 预期：success True，x 接近 [1, -2]
```
坑：局部最优，初值不同结果可能不同 → 换多个初值比较；带约束时 `SLSQP` / `trust-constr` 更合适（按你的约束类型选，**VERIFY BEFORE USE**）。

### ODE — scipy.integrate.solve_ivp
```python
from scipy.integrate import solve_ivp
sol = solve_ivp(lambda t, y: [-0.5 * y[0]], (0, 10), [1.0], t_eval=None, method="RK45")
print(sol.success, sol.message, sol.y[0][-1])
```
刚性问题（衰减/反应动力学常见）：换 `method="Radau"` 或 `"BDF"`；若报求解失败先缩短区间或放宽容差 `rtol` / `atol`。

## §3 状态码与结果字段

`scipy.optimize.linprog` 的 `res.status`（本机 SciPy 1.17.0 实测）：

| status | 含义 |
|---|---|
| 0 | 求到最优解 |
| 1 | 达到迭代上限 |
| 2 | **不可行（infeasible）** |
| 3 | **无界（unbounded）** |

判据：`res.success` 为 False 时必须读 `res.message`（HiGHS 会写明 infeasible / unbounded）。`res.x` 在失败时为 `None`——先判 `res.success`，再取 `.x`，否则 `AttributeError`。
常用字段：`x`（解）、`fun`（目标值）、`nit`（迭代数）、`slack`（松弛量，判断哪些约束紧）、`message`。

## §4 不可行 / 无界的诊断思路

不可行（status 2）常见成因，按出现频率排查：
1. **约束方向写反**（`>=` 写成 `<=`）——最高频。
2. **单位/量纲不一致**（一边是分钟，一边是小时）→ 见 model-formulator 的 `notation-guide.md`。
3. **上下界矛盾**（如 `x >= 10` 与 `x <= 5` 同时存在，或 `bounds` 与约束冲突）。
4. **数据里有 NaN / inf** → 求解器行为异常或直接报错；先 `np.isfinite(A).all()` 检查。
5. **整数化导致不可行**：LP 松弛可行但 MIP 不可行（整数点落空）→ 放宽整数约束或调整边界验证。
6. **"必须恰好等于"过强**：把 `==` 换成区间（如 `>= 目标` 且 `<= 目标 + 容差`）验证是不是刚性等式造成。

无界（status 3）常见成因：漏了资源上限/非负约束、目标方向写反（该 minimize 写成 maximize）、变量下界缺失。
排查：`res.message` → 逐个变量检查是否有有限上下界 → 把目标取反验证方向。

## §5 松弛定位法（找冲突约束）

思路：给每条"硬约束"引入松弛变量 `s_k ≥ 0`，把目标改成"最小化总松弛量"，求解后看哪些 `s_k > 0`——它们就是无法同时满足的约束（即 IIS 的候选）。

```python
import numpy as np
from scipy.optimize import linprog
# 原问题: A_ub @ x <= b_ub,  x >= 0
A, b = np.array([[1.0, 1.0], [-1.0, -1.0]]), np.array([1.0, -5.0])   # 人为不可行：x<=1 且 x>=5
n_x, n_c = A.shape[1], A.shape[0]
# 新变量 z = [x, s]；约束 A@x - s <= b；目标 min sum(s)
A_new = np.hstack([A, -np.eye(n_c)])
c_new = np.r_[np.zeros(n_x), np.ones(n_c)]
bounds = [(0, None)] * (n_x + n_c)
r = linprog(c_new, A_ub=A_new, b_ub=b, bounds=bounds, method="highs")
print(r.status, np.round(r.x[n_x:], 6))   # 预期：status 0，松弛量 >0 的分量即冲突约束
```
预期：松弛向量中非零分量对应的原始约束就是矛盾来源；把它们打印出来逐条与业务方核对。
说明：这是"弹性规划（elastic mode）"的通用做法，任何 LP 求解器都能实现。商用求解器（如 Gurobi）内置 `computeIIS()` 可直接给出最小冲突集（**VERIFY BEFORE USE**：商业功能，随版本与授权而变）；SciPy/PuLP 无内置 IIS，用上面的松弛法。

## §6 数值与规模注意事项

- 系数数量级差异过大（如 `1e-9` 与 `1e9` 同在一行）会引发数值困难（status 4 / `HiGHS Status` 异常）→ 先做变量缩放（统一单位），这比换求解器有效。
- 尽量传稀疏矩阵（`scipy.sparse`）给大规模 LP/MIP；稀疏度通常决定能否求解（不承诺具体规模）。
- 整数变量越多，求解时间越不可预测；需要时间保证时设 `time_limit`（各库参数名不同，**VERIFY BEFORE USE**）并接受"可行解 + gap"而非最优证明。
- 结果必须**回代校验**：把解代入原始约束计算残差，例如 `np.max(A @ x - b)` 应 ≤ 小容差（容差取值取决于量纲，**VERIFY BEFORE USE**）。求解器说 optimal 不等于模型写对了。

## §7 交付前检查表

- [ ] `model_type` 与求解分支匹配（整数决策没有走 LP 松弛）
- [ ] `res.success` / `status` / `message` 三者都检查过，不只信一个
- [ ] 解回代约束的残差在容差内
- [ ] 若不可行：已用 §4 六条排查 + §5 松弛法定位到具体约束
- [ ] 系数已做单位统一与量纲检查
- [ ] 若跑了 MIP：记录了求解器返回的界/gap 与终止原因，而非只记录一个解
- [ ] 报告里**不写**跨机器可复现性存疑的耗时数字；如必须给出，注明"本机、本数据、本版本实测"
