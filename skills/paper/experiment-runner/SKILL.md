---
name: experiment-runner
description: "Run reproducible experiments with fixed seeds, aggregate metrics across N runs, and apply REAL statistical tests (Welch t-test / p-value / Cohen's d / 95% CI) via scipy. Supports simulated (honest demo) and real (--metric module:func) modes; optional mlflow tracking. Use when the user asks 跑实验 / 多次运行取均值 / 实验统计检验 / 重复实验 / 固定 seed 跑 N 次 / 复现实验 / 算 mean std / 显著性检验 / p 值. Do NOT use for drawing charts (hand results to figure-maker / pub-plotter)."
license: Apache-2.0
compatibility: Stdlib + scipy (falls back to pure-stdlib Welch t when scipy absent). numpy/torch seeded when installed. real mode imports user metrics via importlib. mlflow optional.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Experiment Runner

以固定 seed 跑 N 次，聚合 mean/std，并用**真实统计检验**（Welch t-test、p 值、Cohen's d、95% CI）判定显著性。

> 诚实声明：两种模式——
> - **`--mode simulated`**：内置演示实验（诚实标 `mode: "simulated"` + `simulation_notice`），结果 **MUST 标注「模拟数据」**，勿当真实结果写进论文。
> - **`--mode real`**：跑用户真实指标函数（`--metric module:func`，`func(seed:int)->float`），做真实两组比较。此模式才有可写进论文的统计结论。
>
> 显著性一律以 `stats.p_value < alpha`（默认 0.05）判定，**不再用「均值超阈值」冒充 t-test**；`scipy` 缺失时自动回退纯标准库 Welch t + 正态近似 p（离线仍可用），`stats.method` 如实标注 `scipy` / `stdlib-fallback`。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 模式 | 否 | `--mode simulated`（默认）/ `--mode real` |
| 实验配置 | 条件 | `--config exp_config.json`（键 `n_runs`/`seed`/`baseline_metric`/`improvement_target`） |
| 指标函数 | real 必需 | `--metric "mymodule:metric_fn"`，`metric_fn(seed:int)->float` |
| 基线函数 | real 建议 | `--baseline "mymodule:baseline_fn"`；缺省用 `--baseline-value` 固定值（单组，不做比较） |
| 运行次数 | 否 | `--n-runs 5`（默认 5） |
| 随机种子 | 否 | `--seed 42`（默认 42） |
| 输出路径 | 否 | `--output results.json`，缺省打印到 stdout |
| 追踪 | 否 | `--track` 尝试 mlflow autolog（需装 mlflow，失败静默降级） |

缺失时一次性问齐：「请提供：① 模式（simulated/real）② real 模式：指标函数 `--metric module:func`（基线 `--baseline` 或固定值 `--baseline-value`）③ `--n-runs` ④ `--seed` ⑤ 是否落盘 `--output` ⑥ 是否 `--track` mlflow。」

## 前置自检
```bash
python3 --version                                   # 预期 >= 3.8，否则 STOP
python3 -c "import scipy;print(scipy.__version__)"  # 可选；缺失则走 stdlib-fallback（离线仍可用）
test -f scripts/experiment_runner.py && echo OK     # 脚本缺失 STOP
```

## 工作流

### 步骤 1：运行实验
```bash
# 模拟（演示/离线/CI）
python3 scripts/experiment_runner.py --n-runs 8 --seed 42
# 真实指标（可写进论文）
python3 scripts/experiment_runner.py --mode real --metric "train:accuracy" \
       --baseline "baseline:accuracy" --n-runs 10 --seed 42 --output results.json
```
预期：JSON 含 `mode`、`n_runs`、`results[]`、`stats{test,method,statistic,p_value,alpha,effect_size_cohens_d,ci95_diff,significant}`、`seed_backends[]`、`env`。
若失败：`--metric` 非 `module:func` 形式 → 报 `real 模式需要 --metric module:func`；模块/函数不存在 → ImportError，核对导入路径。

### 步骤 2：读统计结论（真显著性）
- `stats.significant == true` ⇔ `stats.p_value < alpha`，**且必须连同 p 值 / Cohen's d / 95% CI 一起报告**，勿只写「显著」。
- `stats.method == "scipy"` → 用 scipy 精确结果；`"stdlib-fallback"` → 纯标准库近似（小样本 p 略保守，如实注明）。
- 单组（无 `--baseline`）：只有 mean/std，`stats` 含 `note` 说明未做两组比较。
若失败：结果与预期矛盾 → 核对 `n_runs`/`seed`/指标函数返回值（必须是 float）。

### 步骤 3：复现性
预期：`seed_backends` 列出实际生效的后端（random/numpy/torch）；同 seed 两次结果一致（脚本内置确定性）。
若要硬件级复现，把 `env`（pip 版本/CUDA 可用性）一并存档，或用 Docker/`uv` 锁环境。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--mode` | `simulated`（默认）/ `real` | 演示 / 真实指标 |
| `--metric` | `module:func` | real 必填；`func(seed:int)->float` |
| `--baseline` | `module:func` | 基线函数；缺省用 `--baseline-value` |
| `--baseline-value` | 浮点 | 无 `--baseline` 时的固定基线值（单组） |
| `--config` | 路径 | 实验配置 JSON |
| `--n-runs` | 整数 | 默认 5 |
| `--seed` | 整数 | 默认 42 |
| `--track` | 标志 | 尝试 mlflow autolog |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `real 模式需要 --metric module:func` | real 未给指标函数 | 补 `--metric module:func` |
| `ModuleNotFoundError`/`AttributeError` | `--metric` 导入路径或函数名错 | 核对模块可 import、函数可调用且返 float |
| `stats.method` 为 `stdlib-fallback` | 无 scipy | 离线可接受；要精确装 `pip install scipy` |
| `significant` 与直觉不符 | 样本量小 / 方差大 | 看 `p_value`/`cohens_d`/`ci95_diff` 再判断，勿只看布尔 |
| 同 config 两次结果不一致 | 随机后端未统一 seed | 检查 `seed_backends` 是否含 numpy/torch；必要时锁环境 |
| mlflow 未生效 | 未装 mlflow | `--track` 失败静默降级，`tracking: null`；要追踪先 `pip install mlflow` |

## 交付标准

成功定义：`status == "complete"`；real 模式 `stats.test == "welch_ttest"` 且含 `p_value`/`effect_size_cohens_d`/`ci95_diff`。
产物命名：`results.json`（若指定 `--output`）。
验证方法：`python3 -c "import json;d=json.load(open('<out>'));assert d['stats']['test']=='welch_ttest' and 'p_value' in d['stats']"` 通过。

## 参考

统计逻辑内置 `scripts/experiment_runner.py`：`real_stats`（scipy→stdlib 回退）、`seed_all`（多后端种子）、`env_fingerprint`、`_welch_t`。

## 链路位置

上游接 lit-review 的 baseline 定义；产出 `results.json` 原样交给 pub-plotter（`--data results.json` 出图），再进 latex-formatter 组装论文。
