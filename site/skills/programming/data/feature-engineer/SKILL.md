---
name: feature-engineer
description: "Design feature engineering plans: identify feature types, suggest transforms, detect data quality issues, plan interactions. Outputs a feature spec for ML training. Use after ETL, before model training. 当用户要求 做特征工程 / 设计特征 / 特征变换 时使用。 Do NOT use for model training or hyperparameter tuning."
license: Apache-2.0
compatibility: Pure Python standard library. No sklearn required for planning.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/data
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Feature Engineer

设计 ML 特征工程方案：识别特征类型、建议变换、检查数据质量、规划交互特征，产出供训练使用的特征规格 JSON。只做方案设计，不训练模型。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `--data` | 二选一 | CSV 路径；脚本读取首行表头作为列名 |
| `--columns` | 二选一 | 显式列名列表（空格分隔），优先于 `--data` |
| `--target` | 可选 | 目标列名，缺省 `label`；该列与 `id/index/timestamp/date` 会被跳过不出方案 |
| `--output` | 可选 | 结果落盘路径；缺省打印 stdout |

缺失输入时一次性问齐：「请提供：①清洗后的数据文件路径，或直接列出特征列名 ②目标列名（默认 label）。其余我采用默认值：结果打印到终端。」

## 前置自检

运行前探测环境，任一失败→给出修复并 STOP：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
python3 scripts/feature_engineer.py --help >/dev/null 2>&1   # 预期退出码 0；失败：脚本缺失 → 核对技能目录
test -f <用户给的 --data 路径>   # 预期退出码 0；失败：文件不存在 → 改用 --columns 显式传列名，或向用户要正确路径
```

## 工作流

### 步骤 1：取列名

```bash
head -1 data/clean.csv   # 预期输出逗号分隔的表头，与用户认知一致
```

若失败：文件不存在或表头为空 → 用 `--columns col1 col2 ...` 显式传入；都不给时脚本会退回内置演示列（`feature_a` 等），那不是用户数据，必须避免。

### 步骤 2：生成特征方案

```bash
python3 scripts/feature_engineer.py --data data/clean.csv --target label
```

预期：stdout 输出 JSON，顶层 `{"quality": {...}, "features": {...}}`；`features.n_features` 等于非跳过列数，`features.status` 为 `plan_ready`。

### 步骤 3：核验类型推断

预期：每列的 `type` 符合关键词推断——列名含 `name/text/desc` → `categorical`；含 `count/num/total/sum/avg/rate` → `numeric`；含 `date/time/year/month` → `temporal`；其余 → `auto`（`transforms` 为空，需人工补方案）。
若失败：`auto` 列过多 → 向用户确认各列语义后，用 `--columns` 配合人工调整，或直接在方案 JSON 上补全类型。

### 步骤 4：检查质量评分并报告

预期：`quality.issues` 列出检测到的问题（当前骨架实现按列名含 `null`/`missing` 识别），`quality.quality_score = 100 - 10×issue数`。向用户报告评分与问题列，再交接 ml-pipeline 训练。

## 特征类型速查表

| 类型 | 推断关键词（列名小写包含） | 默认建议变换 |
|------|---------------------------|--------------|
| numeric | count, num, total, sum, avg, rate | `standardize`, `log_if_skewed`, `clip_outliers` |
| categorical | name, text, desc | `one_hot_if_small`, `target_encode_if_large` |
| temporal | date, time, year, month | `extract_hour`, `extract_dayofweek`, `is_weekend` |
| auto | （其余） | 无——需人工确认语义后补 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 输出里出现 `feature_a/feature_b` 等演示列 | 未传 `--data`/`--columns`，脚本退回内置演示 | 停止使用该输出，补传真实列名重跑 |
| `n_features` 与预期列数不符 | 目标列或 `id/index/timestamp/date` 被跳过 | 属预期行为；若目标列名不同，用 `--target` 指定 |
| 所有列都是 `auto` | 列名不含任何类型关键词 | 人工确认列语义，直接编辑方案 JSON 补类型与变换 |
| `quality_score` 偏低 | 列名含 `null`/`missing` 指示词 | 先回 etl-builder 补清洗，再重新生成方案 |
| 输出未落盘 | 未传 `--output` | 属预期（打印 stdout）；需落盘时加 `--output feature_plan.json` |

## 交付标准

成功定义：输出 JSON 含 `quality` 与 `features` 两段，`features.status=plan_ready`，无演示列，目标列正确跳过。
产物命名：特征方案 `feature_plan.json`（经 `--output` 落盘时）。
保存位置：与数据文件同目录或工作目录根。
验证完整性：`n_features` 与输入列数（减去跳过列）一致；每列有 `type`；`auto` 列已人工补全或已向用户说明。

## 安全红线

- 本技能只产出方案，不执行训练、不修改数据文件。
- `--output` 会覆盖同名文件；目标路径已存在时先向用户确认。
- 类型推断基于列名关键词，可能误判；向用户交付前必须复核 `auto` 与可疑分类。

## 参考

- [references/feature-patterns.md](references/feature-patterns.md) —— 需要领域特定的特征构造模式（时序、文本、交互）时读

特征方案就绪，**接着说："特征已生成，继续调用 ml-pipeline 训练与评估模型"——链条自动展开**。
