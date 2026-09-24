# Monte Carlo 实用指南（收敛、方差缩减、可复现性）

> 配套 simulation-runner。本文所有**数值均在本机 Python 3.11 + numpy 实测**（numpy 版本见执行环境），可复现；未实测的性能/耗时数字一律不写。

## Table of Contents
- §0 与 `simulation.py` 的实际对应关系
- §1 基本思想：把待求量写成期望
- §2 大数定律与 1/√n 收敛速度
- §3 可运行示例：估计带标准误与置信区间
- §4 样本量够不够：判据与反推公式
- §5 方差缩减（对偶 / 控制变量 / 重要性采样 / 分层）
- §6 随机数与可复现性
- §7 检查清单与常见坑

## §0 与 `simulation.py` 的实际对应关系

`simulation.py` 的 `--monte-carlo` 模式行为（读源码确认）：
- 采样用标准库 `random.gauss(mu, sigma)`，**不是** numpy。
- 输出字段：`n` / `mean` / `std` / `p50` / `p95`（键名由 `f"p{int(quantile*100)}"` 生成，默认 quantile=0.95）/ `p_exceed_threshold` / `min` / `max` / `threshold` / `status`。
  注意：SKILL.md 示例里写的是 `p_exceed`，**实际键名是 `p_exceed_threshold`**；model-solver 的同名功能返回的键是 `p_exceed`，两者不一致，写下游代码时要按实际键取值。
- `std` 用 `statistics.stdev`，即**样本标准差（ddof=1）**。
- 分位数是排序后按下标 `int(n*quantile)` 取值，属**经验分位数**（非插值法），与 `np.quantile` 的线性插值结果可能有微小差异。
- **脚本没有 `--seed` 参数**，每次运行结果都不同 → 需要复现时用 §6 的包装方式，或改用 numpy 版（§3）。
- `param_scan` 与 `sensitivity` 目前只输出"计划"（`note: run model-solver for actual result`），不真正调用模型；要得到真实数值需自己把每个参数点喂给 model-solver。

## §1 基本思想：把待求量写成期望

三步：① 待求量 θ 写成 `θ = E[g(X)]`；② 从 X 的分布抽 n 个独立样本；③ 用样本均值 `θ̂ = (1/n)Σ g(Xᵢ)` 估计 θ。
- 定积分、概率、期望、分位数、风险指标（VaR/超过阈值的概率）都能写成这种形式。
- 例：π/4 = P(点落在单位圆内) = E[1{x²+y² ≤ 1}]，x,y ~ U(0,1)。

## §2 大数定律与 1/√n 收敛速度

- 大数定律：n → ∞ 时 θ̂ → θ（几乎必然/依概率）。
- 中心极限定理给出误差尺度：**标准误 SE = σ/√n**（σ 是 g(X) 的标准差，用样本标准差 s 估计）。
- 1/√n 的含义（最重要的一条）：**精度提高 10 倍需要 100 倍样本**；误差减半需要 4 倍样本。靠堆样本换精度很快就不划算 → 优先考虑 §5 的方差缩减。
- 相对误差视角（稀有事件）：估计概率 p 时，相对误差 ≈ `1/√(n·p)`。p 越小，需要的样本越多：p = 1e-5、想让相对误差 10%，量级上需要 n ≈ 1/(p·0.01) = 1e7 次（**这是量级结论，不是承诺**）。这就是为什么尾部风险要用重要性采样（§5）。

## §3 可运行示例：估计带标准误与置信区间

```python
import numpy as np

rng = np.random.default_rng(20260914)      # 固定 seed → 可复现
n = 100_000
x = rng.normal(0, 1, size=n)
g = (x > 2).astype(float)                  # 示性函数：估计 P(X > 2)

mean = g.mean()
se = g.std(ddof=1) / np.sqrt(n)            # ddof=1：样本标准差
print(f"p_hat={mean:.6f}  se={se:.6f}  CI95=[{mean-1.96*se:.6f}, {mean+1.96*se:.6f}]")
```
本机实测输出（seed=20260914, n=100000）：
`p_hat=0.022120  se=0.000465  CI95=[0.021208, 0.023032]`
判据：理论值 P(X>2) ≈ 0.0228 落在 CI 内 → 结果可信；若真值不在 CI 内，先查样本是否独立、seed 是否被复用、g 是否写错。
`1.96` 是正态分布 95% 分位点的常用近似值；CI 公式依赖中心极限定理，对比例估计的经验规则是 `n·p` 与 `n·(1-p)` 都不少于 10（**VERIFY BEFORE USE**：小概率事件下正态近似失效，改用更大样本或精确方法）。

## §4 样本量够不够：判据与反推公式

不要凭感觉定 n，按目标精度反推：
```
目标：相对误差 ≤ ε（例如 ε = 0.05，即 5%）
n ≈ (1.96 · s / (ε · |θ̂|))²
```
先用小样本（如 n₀ = 1000）估计出 s 与 θ̂，代入算出 n，再跑全量，最后用全量的 s 复核一次。

实测示例（估计 P(X>2)，取 ε = 0.05）：小样本估出 s 与 θ̂ 后算得 `n ≈ 6.5e4`，与 §3 用 1e5 得到的相对误差（se/mean ≈ 2.1%）一致。

流程化判据：
1. 固定 seed，用 n 与 4n 各跑一次 → 若两个估计之差远小于各自的 SE，说明已进入稳定区。
2. 报告时**必须同时给出 SE 或 CI**，只报 `mean` 的蒙特卡洛结果无法判断可信度。
3. 相对误差达不到目标且样本已很大 → 换方差缩减（§5），而不是继续加样本。

## §5 方差缩减（四种思路与适用条件）

### 5.1 对偶变量（Antithetic Variates）
思路：每个样本 `u` 配一个"镜像"样本（标准正态用 `-u`，均匀用 `1-u`），取 `g(u)` 与 `g(mirror)` 的平均。
适用：`g` 对输入**单调**时，两个估计负相关，方差下降。
```python
m = 100_000
u = rng.standard_normal(m)
pair = (np.exp(u) + np.exp(-u)) / 2                  # 估计 E[e^X]，真值 e^0.5=1.648721
print(pair.mean(), pair.std(ddof=1) / np.sqrt(m))    # SE 必须用"对平均"算，不能用 2m 个原始值
```
实测：`anti mean=1.646170 se=3.80e-03`；同规模普通采样 `mean=1.649599 se=4.79e-03` → SE 降低约 21%。
坑：SE 必须从**配对后的平均值**序列计算（`pair.std(ddof=1)/sqrt(m)`）；直接对 2m 个原始值用 `std/sqrt(2m)` 会因样本不独立而算错（实测会得出"没有收益"的错误结论）。
不适用：g 非单调（如示性函数 1{x>2} 上实测收益极小）。

### 5.2 控制变量（Control Variates）
思路：找一个与 g 强相关、且**期望已知**的量 c（如 c = X，E[X] = 0），用 `g - β(c - E[c])` 代替 g，β 取 `Cov(g,c)/Var(c)`（可由样本估计）。
```python
z = rng.standard_normal(200_000)
g, c = np.exp(z), z
cov = np.cov(g, c, ddof=1)
beta = cov[0, 1] / cov[1, 1]
adj = g - beta * (c - 0.0)
print(adj.mean(), adj.std(ddof=1) / np.sqrt(len(g)))
```
实测：`beta=1.6483`、`se` 由 4.78e-03 降到 3.05e-03（约降 36%）。
适用条件：能找到期望**解析已知**的对照量，且相关性高。β 用样本估计会带来轻微偏差，样本很小时慎用。

### 5.3 重要性采样（Importance Sampling）
思路：从另一个分布 q 采样（把采样集中到"重要区域"，如尾部），用似然比 `w = p(x)/q(x)` 加权：`θ̂ = mean(w · g(x))`。
适用：稀有事件 / 尾部概率。
```python
from scipy.stats import norm
n, shift = 200_000, 4.0
y = rng.standard_normal(n) + shift          # 从 N(shift, 1) 采
w = np.exp(-shift * y + 0.5 * shift ** 2)   # 似然比 f0(y)/f1(y)
est = (w * (y > 4)).mean()                  # 估计 P(X > 4)
se = (w * (y > 4)).std(ddof=1) / np.sqrt(n)
print(f"est={est:.3e}  se={se:.1e}  rel={se/est*100:.2f}%")
```
实测（多个 shift / seed）：`shift=3/4/5`、`seed=11/12` 下估计值 3.15e-5 ~ 3.19e-5，真值 3.167e-5，相对误差 **0.47% ~ 0.68%**；同样 n 的朴素采样实测只命中 9 次（估计 4.5e-5，相对误差约 **40%**）。
坑（必须检查）：权重可能退化。实测该例 `max(w)/mean(w)` 在 1e3 ~ 1e5 量级——权重右偏严重。检验方法：换 shift（3/4/5）与换 seed 各跑几次，估计值应稳定（本例稳定）；若换参后估计剧烈变化，说明方差实际很大，结论不可信。

### 5.4 分层采样（Stratified Sampling）
思路：把输入空间分层（如按分位数切 k 段），每层独立抽 n/k 个样本再加权汇总。
适用：低维输入（维数高时分层数爆炸）、且你知道各层概率质量。
实现要点：层内样本数可按层方差分配（方差大的层多抽），但层概率权重必须正确归一化。

## §6 随机数与可复现性

- 优先用 numpy 新接口：`rng = np.random.default_rng(seed)`；避免全局 `np.random.seed()`（会污染其他库）。
- 标准库 `random` 用 `random.seed(seed)`；`simulation.py` 用的是标准库 `random` 且**未暴露 seed → 两次运行结果不同**。可复现的临时办法：
```bash
python3 -c "import random, runpy, sys; random.seed(42); sys.argv=['simulation.py','--monte-carlo','--n','10000']; runpy.run_path('simulation.py', run_name='__main__')"
```
（更稳的做法是给脚本加 `--seed` 参数并调用 `random.seed(args.seed)`。）
- 并行/多进程：不要用同一 seed 起多个子进程（会得到相同序列）。用 `np.random.SeedSequence(seed).spawn(k)` 给每个子进程一条独立流。
- 记录三要素：**seed + 库版本 + 代码版本**。缺任何一个，结果都无法复现。
- 报告里注明 seed；对比两个方案时用**同一 seed 与同一批随机数**（配对比较能显著降低比较的方差）。

## §7 检查清单与常见坑

- [ ] 待求量已写成 `E[g(X)]` 的形式
- [ ] 使用了固定 seed，并在报告中写明
- [ ] 输出里包含 SE 或 CI，而不只是均值
- [ ] 样本量按 §4 反推，而非随手取 10000
- [ ] 用 n 与 4n 复核过稳定性
- [ ] 稀有事件优先用重要性采样，并检查权重是否退化（换 shift / seed 复跑）
- [ ] 分位数类指标（`p95` 等）的误差比均值更大，样本量要相应上调
- [ ] 下游取值按脚本**实际键名**（`p_exceed_threshold`，不是 `p_exceed`）

常见坑：① 复用了同一个 rng 对象的流导致前后两次实验"巧合"相关；② 把样本标准差 `ddof=1` 与总体标准差混用（SE 公式要求用样本标准差估计 σ，样本量大时差异可忽略）；③ 用 `std/sqrt(n)` 估计相关样本（如对偶、MCMC 链）的 SE，会严重低估误差。
