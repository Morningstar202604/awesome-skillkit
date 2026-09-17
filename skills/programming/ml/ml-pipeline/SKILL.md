---
name: ml-pipeline
description: "端到端训练、评估与调优 ML 模型：支持 RandomForest、GradientBoosting、LogisticRegression，输出 accuracy/F1/ROC-AUC 与交叉验证。何时使用：特征工程已完成、需要训练与对比模型时。触发场景（中/英）：搭 ML 训练流水线 / 模型训练流程 / 调超参 / train an ML model / build a training pipeline / tune hyperparameters。排除项：不用于深度学习研究（仅表格 sklearn/XGBoost 工作流）。 何时使用：特征工程已完成、需要训练、评估与调优表格模型时。触发场景（中/英）：搭 ML 训练流水线 / 训练表格模型 / 调超参 / 模型对比 / train an ML model / build a training pipeline / tune hyperparameters.排除项：不做深度学习研究（仅表格 sklearn/XGBoost），不做特征工程本身（交给 feature-engineer）。Use when the user asks 搭 ML 训练流水线 / 训练表格模型 / 调超参 / 模型对比 / train an ML model / build a training pipeline / tune hyperparameters. Do NOT use when the ask is deep-learning research or feature engineering itself (use feature-engineer)."
license: Apache-2.0
compatibility: Requires scikit-learn, pandas, numpy. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/ml
  pattern: workflow
  tier: powerful
  verified-date: "2026-09-09"
---

# ML Pipeline

训练 → 评估 → 调优 → 保存模型。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| data | 是 | 训练数据路径（CSV，含特征与标签列） |
| target | 否 | 标签列名 | label |
| model | 否 | `random_forest` / `gradient_boosting` / `logistic` | random_forest |
| cv | 否 | 交叉验证折数 | 5 |
| output | 否 | 报告写入文件 | 标准输出 |

缺失时一次性问齐：「请提供：① data（CSV 路径，含特征与标签）。target/model/cv/output 我按默认处理。」

## 前置自检

```bash
python3 --version
python3 -c "import sklearn, pandas, numpy; print('deps OK')"
test -f scripts/ml_pipeline.py && echo "OK script present"
```

- 预期：版本号输出；`deps OK` 打印；脚本存在。
- 若失败：缺依赖 → `pip install scikit-learn pandas numpy`；脚本缺失 → STOP 回报。

## 工作流

### 步骤 1：加载并切分数据

- 动作：读取 CSV，按 80/20 切分训练/测试集。

```bash
python3 scripts/ml_pipeline.py --data data/clean.csv --target label --model random_forest --cv 5
```

- 预期：脚本加载数据、完成切分，进入训练。
- 若失败：`FileNotFoundError` → data 路径错；`KeyError` → target 列不存在。

### 步骤 2：训练与交叉验证

- 动作：用 `--model` 训练，`--cv` 折交叉验证。
- 预期：训练完成，输出 `cv_mean` / `cv_std`。
- 若失败：数据为空/全同值 → 检查特征；类别不平衡 → 考虑 `logistic` 或加权。

### 步骤 3：评估与对比

| 模型 | 最适合 | 速度 |
|-------|----------|-------|
| random_forest | 表格、混合类型 | 中 |
| gradient_boosting | 表格、精度优先 | 慢 |
| logistic | 二分类、可解释 | 快 |

- 动作：输出 test 指标（accuracy / F1 / ROC-AUC），多模型时横向对比。
- 预期：报告含 `train_accuracy` / `test_accuracy` / `f1` / `cv_mean` / `cv_std`。
- 若失败：指标异常低 → 查数据泄漏或特征质量，参考 metrics-explained.md。

### 步骤 4：报告与保存

- 动作：将结果 JSON 写入 `--output` 或标准输出，保存模型产物。
- 预期：报告含 `n_samples` / `n_features` 与各项指标。
- 若失败：写入失败 → 检查 output 路径权限。

## 输出格式

```json
{
  "model": "random_forest",
  "train_accuracy": 0.92,
  "test_accuracy": 0.85,
  "f1": 0.82,
  "cv_mean": 0.84,
  "cv_std": 0.02,
  "n_samples": 5000,
  "n_features": 12
}
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| --data | 文件路径 | 必需，CSV |
| --target | 列名 | 默认 label |
| --model | random_forest/gradient_boosting/logistic | 默认 random_forest |
| --cv | 整数 | 默认 5 |
| --output | 文件路径 | 可选，报告输出 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `FileNotFoundError` | data 路径错 | 核对路径 |
| `KeyError: '<target>'` | 标签列缺失 | 用 `--target` 指定正确列名 |
| test 指标远低于 train | 过拟合/数据泄漏 | 参考 metrics-explained.md 选指标与正则 |
| ROC-AUC 报错只在二分类可用 | 多分类任务里指定了 `roc_auc` | 改选 accuracy/F1，或转成 one-vs-rest 后再算 AUC |
| 训练集很小，交叉验证不稳 | 样本量不足而折数过大 | 减小折数或改分层抽样，并在报告里标注样本量 |
| 类别极不平衡，准确率虚高 | 全预测多数类也有高准确率 | 改用 F1/PR-AUC 作为主指标，并设 `class_weight` |

## 交付标准

- 成功定义：报告含 `test_accuracy` 与 `f1` 等有限数值，模型产物已落盘。
- 产物命名：`ml_report.json` + 模型文件（或 `--output` 指定）。
- 保存位置：当前工作目录或 `--output` 路径。
- 验证完整性：`python3 -c "import json; d=json.load(open('ml_report.json')); assert 0<=d['test_accuracy']<=1"`。

## 参考

- references/hyperparameter-guide.md — 调超参、选模型时读
- references/metrics-explained.md — 选评估指标、解读分数时读
