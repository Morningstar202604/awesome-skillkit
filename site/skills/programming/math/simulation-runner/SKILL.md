---
name: simulation-runner
description: "运行仿真：参数扫描、蒙特卡洛、敏感性分析（OAT）与模型解的压测。何时使用：模型已求解、需要在变化条件下测试鲁棒性时。触发场景（中/英）：跑仿真 / 蒙特卡洛模拟 / 敏感性分析 / run a simulation / Monte Carlo / sensitivity analysis。排除项：不用于生产级仿真负载（仅本地实验运行）。"
license: Apache-2.0
compatibility: Requires numpy, random. No external solver needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Simulation Runner

参数扫描、蒙特卡洛与敏感性分析。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| spec | 否 | 模型规格 JSON（参数扫描/敏感性读取） | — |
| mode | 否 | `sweep` / `monte-carlo` / `sensitivity`（由参数决定） | 自动 |
| output | 否 | 结果写入文件 | 标准输出 |

缺失时一次性问齐：「请提供：① 要测的模型或参数（spec 路径，或直接在命令中给参数）。其余按默认。」

## 前置自检

```bash
python3 --version
python3 -c "import numpy; print('numpy', numpy.__version__)"
test -f scripts/simulation.py && echo "OK script present"
```

- 预期：版本号输出；`numpy <版本>` 打印；脚本存在。
- 若失败：缺 numpy → `pip install numpy`；脚本缺失 → STOP 回报。

## 工作流

### 步骤 1：参数扫描（Parameter Sweep）

```bash
python3 scripts/simulation.py --spec model.json --param rate --range 0.1 5.0 --steps 10
```

- 动作：沿 `--param` 在 `--range LO HI` 间取 `--steps` 个点，记录目标值。
- 预期：输出每个采样点对应的目标值序列。
- 若失败：`--range` 需两个浮点 → 补齐 LO HI；spec 缺 `--param` 字段 → 确认字段名。

### 步骤 2：蒙特卡洛（Monte Carlo）

```bash
python3 scripts/simulation.py --monte-carlo --n 10000 --mu 0 --sigma 1 --threshold 2
```

- 动作：生成 `--n` 个随机样本（均值 `--mu`、标准差 `--sigma`），计算 P(超阈) 与分位数。
- 预期：输出 `mean` / `std` / `p95` / `p_exceed` / `threshold`。
- 若失败：结果异常（如 p_exceed 非 0~1）→ 检查 `--sigma`/`--threshold` 量级。

### 步骤 3：敏感性分析（OAT）

```bash
python3 scripts/simulation.py --sensitivity rate,noise,decay --perturbation 0.1
```

- 动作：对每个参数单独 ±`--perturbation`（默认 0.1=10%）扰动，测输出变化。
- 预期：输出各参数敏感度排序。
- 若失败：参数名不在 spec → 对齐 `--sensitivity` 列表与 spec 字段。

## 输出格式

```json
{
  "mode": "monte_carlo",
  "n": 10000,
  "mean": 0.0012,
  "std": 0.9987,
  "p95": 1.6449,
  "p_exceed": 0.0228,
  "threshold": 2.0
}
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| --spec | 文件路径 | 模型规格 JSON |
| --param | 名称 | 扫描目标参数 |
| --range | LO HI | 两个浮点，扫描区间 |
| --steps | 整数 | 采样点数，默认 10 |
| --monte-carlo | 标志 | 启用蒙特卡洛 |
| --n | 整数 | 样本数，默认 10000 |
| --mu / --sigma | 浮点 | 默认 0 / 1 |
| --threshold | 浮点 | 阈值，默认 0 |
| --sensitivity | 名称列表 | OAT 参数 |
| --output | 文件路径 | 可选，写入结果 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `--range` 参数数量错 | 未给 LO HI | 补两个浮点 |
| `p_exceed` 越界 | 量级不匹配 | 复核 `--sigma`/`--threshold` |
| 参数不在 spec | 名称拼写错 | 对齐 `--sensitivity` 与 spec 字段 |

## 交付标准

- 成功定义：输出 JSON 含 `mode` 与对应统计量，且数值有限。
- 产物命名：`sim_<mode>.json`（或 `--output` 指定）。
- 保存位置：当前工作目录或 `--output` 路径。
- 验证完整性：`python3 -c "import json; json.load(open('sim_monte_carlo.json'))"` 确认可解析且字段齐全。

## 参考

- references/mc-theory.md — 方差缩减、收敛速率、OAT 理论时读
