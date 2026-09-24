# Model Types（建模问题类型与模型选择对照）

> 配套 model-formulator。`model_formulator.py` 的 `DOMAINS` 固定五个域（optimization / differential / statistical / stochastic / bayesian），`formulate()` 用关键词启发式覆盖 `model_type` 与 `solver_hint`：
> - 命中 `minimize|maximize|cost|profit|time` → LP，含 `integer|assign` → MIP
> - 命中 `rate|flow|change|growth` → domain=differential, ODE
> - 命中 `probability|random|uncertain|risk` → domain=stochastic, monte_carlo
>
> 即：**脚本给的是起点，不是结论**。它不看数据、不校验约束，未命中关键词时 `model_type` 直接取该域列表第一项（optimization→LP、differential→ODE、statistical→regression、stochastic→markov_chain、bayesian→prior_posterior）。必须用本文件人工复核。

## Table of Contents
- §1 选择决策树（从问题到模型类型）
- §2 优化类（LP / ILP / MIP / NLP / 凸优化）
- §3 预测类（回归 / 时序）
- §4 分类类
- §5 图与网络
- §6 排队与仿真
- §7 决策与博弈
- §8 假设与失效条件速查表
- §9 填写 model spec 的注意事项

## §1 选择决策树

```
问题里有没有"要做的决定"（可选择的量）？
├─ 有（决定型）
│  ├─ 目标与约束都是线性、变量连续        → LP
│  ├─ 需要"是/否""选几个"等整数决策        → ILP / MIP
│  ├─ 目标或约束非线性
│  │   ├─ 能写成凸形式（可证凸）          → 凸优化（CVXPY）
│  │   └─ 非凸 / 多峰                     → 局部优化 + 多起点，或启发式/元启发式
│  └─ 决策分阶段、未来有随机性且可观测     → 随机规划 / MDP
└─ 没有（描述/预测型）
   ├─ 输出是连续量
   │   ├─ 样本独立                         → 回归
   │   └─ 样本按时间相关                   → 时间序列
   ├─ 输出是离散类别                       → 分类
   └─ 想刻画"机制"而非拟合
       ├─ 连续状态随时间演化               → ODE / PDE
       ├─ 实体排队、资源竞争               → 排队论 / 离散事件仿真
       └─ 多智能体相互作用                 → 仿真 / 博弈
```
判据要点：先问**决策变量**是什么。说不出决策变量 → 不是优化问题，别硬套 LP。

## §2 优化类

| 类型 | 形式 | 典型假设 | 失效条件 |
|---|---|---|---|
| LP | `min cᵀx, s.t. Ax ≤ b, x ≥ 0` | 比例性、可加性、确定性、连续性 | 存在固定成本/启动成本（需 0-1 变量） |
| ILP / MIP | 同上 + `x ∈ ℤ` 或 `x ∈ {0,1}` | 决策离散 | 规模大时求解时间可能爆炸（NP-hard 类问题，实际耗时与数据强相关，**不要预先承诺求解时间**） |
| 凸优化 | `min f(x)`，f 与约束凸 | 目标/约束满足凸性（CVXPY 用 DCP 规则校验） | 写成非凸形式会被求解器直接拒绝（DCPError） |
| NLP（非凸） | 一般非线性 | 局部最优可接受 | 初值敏感、可能只得到局部解 |

工具入口：LP → `scipy.optimize.linprog`（HiGHS）；MIP → `scipy.optimize.milp`（HiGHS，SciPy ≥ 1.9，**VERIFY BEFORE USE**）、PuLP(CBC)、OR-Tools CP-SAT；凸 → CVXPY；通用非线性 → `scipy.optimize.minimize`。
注意：`model_solver.py` 目前把 ILP/MIP 也送进 `solve_lp`（无整数约束），得到的是 **LP 松弛解**——若需要整数解，必须改用上述工具（详见 model-solver 的 `solver-options.md`）。

## §3 预测类

| 类型 | 适用 | 关键假设 | 失效条件 |
|---|---|---|---|
| 线性回归 | 关系近似线性、需要可解释系数 | 线性、误差独立同分布、同方差 | 强非线性、特征共线、异方差 |
| 广义线性 / 正则化（Lasso/Ridge） | 高维、需变量筛选 | 同上 + 稀疏或平滑先验 | 特征量纲未统一（未标准化时惩罚不公平） |
| 树模型 / GBDT | 表格数据、非线性、混合类型 | 样本分布稳定 | 外推（预测超出训练值域）能力差 |
| 时序（ARIMA / 指数平滑 / 状态空间） | 有趋势/季节性的序列 | **平稳性**（或差分后平稳）、时间间隔均匀 | 结构性突变、缺失时段、外部干预未建模 |

时序务必先做：画序列图 → 检查缺失与等间隔 → 平稳性检验 → 再选模型。训练/测试切分必须**按时间切**（随机切会引入未来信息）。

## §4 分类类

| 类型 | 适用 | 关键假设 | 失效条件 |
|---|---|---|---|
| 逻辑回归 | 需可解释、线性边界、概率校准 | 线性对数几率、类别近似可分 | 强非线性边界、特征未标准化导致收敛慢 |
| 树 / 随机森林 | 表格数据基线、鲁棒 | 同分布 | 类别极不平衡时倾向多数类 |
| GBDT | 精度优先的表格任务 | 同分布 | 小数据易过拟合，需早停 |
| SVM / 核方法 | 中小规模、边界清晰 | 特征尺度一致 | 大规模数据训练慢（未给具体量级，不承诺速度） |

类别不平衡处理：`class_weight="balanced"`、重采样（注意只作用于训练折）、换用 PR-AUC / F1 而非 accuracy（见 ml-pipeline 的 `metrics-explained.md`）。

## §5 图与网络

- 最短路径（Dijkstra / Bellman-Ford，后者支持负权）、最小生成树、最大流/最小割、匹配、TSP/VRP。
- 典型假设：边权已知且确定；图结构固定。
- 失效条件：动态图（边随时间变化）、带时间窗与容量约束（VRPTW 属 NP-hard 类问题）、边权不确定（→ 随机/鲁棒版本）。
- 工具：`networkx`（教学/中小规模，纯 Python，大规模较慢）、OR-Tools（路径/流量类求解能力强）。
- 判定：问题里出现"路线/连通/流量/依赖顺序/最少经过" → 先画图，再判断是不是标准图问题。

## §6 排队与仿真

- 排队论（M/M/1 等）适用：到达与服务过程可建模为随机过程、稳态可求。**字母含义要写清**（M=泊松到达/指数服务，D=确定，G=一般分布）。
- 失效条件：到达率接近/超过服务率（系统不稳定，队列无限增长）、非稳态（只关心开张几小时）、复杂路由规则难以解析。
- 此时改用**离散事件仿真**（`simpy` 或自行实现事件循环），并用 Monte Carlo 重复运行取分布（见 simulation-runner 的 `mc-theory.md`）。
- 关键输出不只是均值：等待时间的 **p95/p99** 往往才是服务水平的度量。

## §7 决策与博弈

- 决策树/影响图：单决策者、结果概率已知 → 期望效用最大化。
- 马尔可夫决策过程（MDP）：序贯决策、状态转移已知 → 值迭代/策略迭代；转移未知 → 强化学习或仿真。
- 博弈：多方策略相互作用 → 纳什均衡；**注意**均衡不唯一、且均衡未必是"最优"，用于描述而非处方。
- 失效条件：效用难以量化、对手非理性、概率来自主观估计且未做敏感性分析 → 结论不可靠，必须做敏感性分析（simulation-runner 的 OAT 模式）。

## §8 假设与失效条件速查表

| 模型 | 最容易被忽略的假设 | 一旦违反的表现 |
|---|---|---|
| LP | 比例性（无规模经济/固定成本） | 解看似最优但实际不可执行 |
| ILP/MIP | 求解时间可控 | 长时间不出解，只有可行解无最优证明 |
| 凸优化 | 目标/约束凸 | 求解器报 DCPError，或多起点得到不同解 |
| 回归 | 同方差、无强共线 | 系数不稳、p 值失真 |
| 时序 | 平稳、等间隔 | 预测滞后一拍或整体偏移 |
| 排队 | 稳态、到达率 < 服务率 | 队列长度发散 |
| 仿真 | 随机数可复现、运行次数足够 | 换个 seed 结论就变 |

## §9 填写 model spec 的注意事项

脚本输出字段：`problem / domain / model_type / variables / objective / constraints / assumptions / knowns / unknowns / solver_hint / status / next_step`。人工复核时：

- `variables` 用 ASCII 键名（如 `x[i,j]`），便于 JSON 传输与后续代码生成（符号约定见 `notation-guide.md`）。
- `constraints` 每条一行、可编号（C1、C2…），便于 model-solver 报错时定位到具体约束。
- `assumptions` 必须写**可检验**的语句（"需求在周期内恒定"而非"简化处理"）；每条假设都应能用数据或业务方确认，否则标为待确认。
- `solver_hint` 只是提示：`model_solver.py` 主要按 `model_type` 字符串分派（含 LP/ILP/MIP → LP 分支；ODE/PDE → solve_ivp；MONTE/STOCHASTIC → 随机采样），填错类型会直接走错分支。
