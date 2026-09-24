---
name: ml-pipeline
description: "End-to-end training, evaluation, and tuning of ML models: supports RandomForest, GradientBoosting, and LogisticRegression, outputting accuracy/F1/ROC-AUC with cross-validation. Use when feature engineering is done and you need to train, evaluate, and compare tabular models — building an ML training pipeline, training a tabular model, tuning hyperparameters, or comparing models. Do NOT use for deep-learning research (tabular sklearn/XGBoost workflows only) or for feature engineering itself (use feature-engineer)."
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

Train → evaluate → tune → save the model.

## Input Checklist

| Input | Required | Description | Default |
|------|------|------|------|
| data | Yes | Path to training data (CSV, with feature and label columns) | — |
| target | No | Label column name | label |
| model | No | `random_forest` / `gradient_boosting` / `logistic` | random_forest |
| cv | No | Number of cross-validation folds | 5 |
| output | No | Write the report to a file | stdout |

When missing, ask for all at once: "Please provide: (1) data (a CSV path with features and labels). I'll run target/model/cv/output on defaults."

## Pre-flight Checks

```bash
python3 --version
python3 -c "import sklearn, pandas, numpy; print('deps OK')"
test -f scripts/ml_pipeline.py && echo "OK script present"
```

- Expected: a version number; `deps OK` prints; the script exists.
- On failure: missing dependencies → `pip install scikit-learn pandas numpy`; the script is missing → STOP and report.

## Workflow

### Step 1: Load and split the data

- Action: Read the CSV and split into train/test sets at 80/20.

```bash
python3 scripts/ml_pipeline.py --data data/clean.csv --target label --model random_forest --cv 5
```

- Expected: the script loads the data, completes the split, and proceeds to training.
- On failure: `FileNotFoundError` → wrong data path; `KeyError` → the target column doesn't exist.

### Step 2: Train and cross-validate

- Action: Train with `--model` and run `--cv`-fold cross-validation.
- Expected: training completes and outputs `cv_mean` / `cv_std`.
- On failure: data is empty or all-identical values → check the features; class imbalance → consider `logistic` or weighting.

### Step 3: Evaluate and compare

| Model | Best for | Speed |
|-------|----------|-------|
| random_forest | Tabular, mixed types | Medium |
| gradient_boosting | Tabular, accuracy-first | Slow |
| logistic | Binary classification, interpretable | Fast |

- Action: Output test metrics (accuracy / F1 / ROC-AUC); when multiple models are used, compare them side by side.
- Expected: the report contains `train_accuracy` / `test_accuracy` / `f1` / `cv_mean` / `cv_std`.
- On failure: metrics are suspiciously low → check for data leakage or feature quality; see metrics-explained.md.

### Step 4: Report and save

- Action: Write the results JSON to `--output` or stdout, and save the model artifact.
- Expected: the report contains `n_samples` / `n_features` and the various metrics.
- On failure: the write failed → check the output path permissions.

## Output Format

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

## Parameter Quick Reference

| Parameter | Values | Description |
|------|------|------|
| --data | file path | Required, CSV |
| --target | column name | Default label |
| --model | random_forest/gradient_boosting/logistic | Default random_forest |
| --cv | integer | Default 5 |
| --output | file path | Optional, report output |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| `FileNotFoundError` | Wrong data path | Check the path |
| `KeyError: '<target>'` | The label column is missing | Use `--target` to specify the correct column name |
| Test metrics far below train | Overfitting / data leakage | See metrics-explained.md to pick metrics and regularization |
| ROC-AUC error: only available for binary classification | `roc_auc` was specified in a multi-class task | Switch to accuracy/F1, or compute AUC after a one-vs-rest conversion |
| The training set is small, cross-validation is unstable | Sample size too small for the number of folds | Reduce the folds or use stratified sampling, and note the sample size in the report |
| Severe class imbalance, inflated accuracy | Predicting the majority class still yields high accuracy | Switch to F1/PR-AUC as the primary metric and set `class_weight` |

## Delivery Criteria

- Definition of success: the report contains finite values such as `test_accuracy` and `f1`, and the model artifact has been written to disk.
- Artifact naming: `ml_report.json` + model file (or per `--output`).
- Save location: current working directory or the `--output` path.
- Completeness verification: `python3 -c "import json; d=json.load(open('ml_report.json')); assert 0<=d['test_accuracy']<=1"`.

## References

- references/hyperparameter-guide.md — read when tuning hyperparameters or choosing a model
- references/metrics-explained.md — read when choosing evaluation metrics or interpreting scores
