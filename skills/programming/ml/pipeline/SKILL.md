---
name: ml-pipeline
description: "Train, evaluate, and tune ML models end-to-end. Supports RandomForest, GradientBoosting, LogisticRegression. Outputs accuracy/F1/ROC-AUC + cross-validation. Use after feature engineering is complete."
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

Train → Evaluate → Tune → Save model.

## When to Use

- Features are engineered, ready for training
- Need baseline model + cross-validation
- Compare multiple algorithms
- Generate model report for stakeholders

## Supported Models

| Model | Best For | Speed |
|-------|----------|-------|
| random_forest | Tabular, mixed types | Medium |
| gradient_boosting | Tabular, accuracy | Slow |
| logistic | Binary, interpretability | Fast |

## Workflow

1. Load data (from ETL output)
2. Split train/test (80/20)
3. Train model
4. Evaluate: accuracy, F1, cross-validation
5. Compare models (if multiple specified)
6. Output report JSON

## Usage

```bash
python3 ml_pipeline.py --data data/clean.csv --target label --model random_forest --cv 5
```

## Output

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

## References

- [references/hyperparameter-guide.md](references/hyperparameter-guide.md) — tuning tips
- [references/metrics-explained.md](references/metrics-explained.md) — when to use which metric
