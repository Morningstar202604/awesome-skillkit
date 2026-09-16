---
name: experiment-runner
description: "Run repeatable experiments from a config, collect metrics across N runs with fixed seeds, and apply basic statistical checks. Use when the user asks 跑实验 / 多次运行取均值 / 实验统计检验 / 重复实验 / 固定 seed 跑 N 次. 当用户要求 复现实验 / 算 mean std 时使用。Do NOT use for drawing charts (hand results to figure-maker)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; executes experiment logic from the given config file, no network calls.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Experiment Runner

Run an experiment N times with a fixed seed, aggregate mean/std, run a basic significance check.

> 诚实声明：本技能脚本为**模拟实验**（mode: `simulated`）——不执行真实训练/评测。输出顶层带 `mode: "simulated"` 与 `simulation_notice`，结果 **MUST 标注"模拟数据"**，勿当真实实验结果写进论文。接入真实训练 harness 前此标注不会消失。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 实验配置 | 条件 | `--config exp_config.json`；或改用 `--n-runs`/`--seed` 内置默认配置 |
| 运行次数 | 否 | `--n-runs 5`（默认 3） |
| 随机种子 | 否 | `--seed 42`（默认 42） |
| 输出路径 | 否 | `--output results.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 配置文件路径（或确认用默认 n_runs=3/seed=42）② 运行次数 `--n-runs` ③ 随机种子 `--seed` ④ 是否落盘 `--output`。」

## 前置自检
```bash
python3 --version                          # 预期 >= 3.8，否则报错并 STOP
test -f scripts/experiment_runner.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
test -f exp_config.json && echo CFG_OK     # 仅当用 --config 时；缺失则 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示目录不完整；若 `--config` 文件不存在 → 报错并 STOP。

## 工作流

### 步骤 1：运行实验
```bash
python3 scripts/experiment_runner.py --config exp_config.json
python3 scripts/experiment_runner.py --config exp_config.json --n-runs 5 --seed 42
python3 scripts/experiment_runner.py --n-runs 5 --seed 42 --output results.json
```
预期：输出 JSON 含 `status: "complete"`、`n_runs`、`results[]`、`stats{mean,std,baseline,improvement,significant}`。
若失败：`--config` 文件无效 JSON → 报 JSON 解析错误，校验配置文件后重试。

### 步骤 2：读取统计结论

- `stats.significant == true` → 均值相对 baseline 超出阈值（`baseline + improvement_target*0.5`），可报"有统计差异趋势"。
- `stats.significant == false` → 未达阈值，勿宣称显著。
预期：字段齐全且数值可复核（`stats.mean` 与 `results[]` 一致）。
若失败：结果与预期矛盾 → 核对 `config`（baseline_metric / improvement_target）。

### 步骤 3：交接下游

预期：将 `results.json` 原样交给 figure-maker / pub-plotter 画图。
若失败：下游读不到字段 → 确认输出的是合法 JSON 而非报错文本。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--config` | 路径 | 实验配置 JSON（键：`n_runs`/`seed`/`baseline_metric`/`improvement_target`） |
| `--n-runs` | 整数 | 运行次数，默认 3 |
| `--seed` | 整数 | 随机种子，默认 42 |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 配置文件 JSON 解析错误 | `--config` 非合法 JSON | 用 `python3 -c "import json;json.load(open('<cfg>'))"` 校验 |
| `mode` 非 `simulated` | 误接入真实数据 | 本脚本恒为 simulated，确认勿当真实结果 |
| 输出非 JSON | 写入被中断 | 检查 `--output` 路径可写后重试 |

## 交付标准

成功定义：`status == "complete"` 且顶层 `mode == "simulated"`。
产物命名：`results.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['mode']=='simulated'"` 通过。

## 参考

无外部 references 文件；模拟逻辑与统计判定内置在 `scripts/experiment_runner.py` 的 `run_experiment`。

## 链路位置

上游接 lit-review 的 baseline 定义；产出 results.json 原样交给 figure-maker / pub-plotter 画图，随后进 latex-formatter 组装论文。
