---
name: feature-engineer
description: "Design feature engineering plans: identify feature types, suggest transforms, detect data quality issues, plan interactions. Outputs a feature spec for ML training. Use after ETL, before model training. 当用户要求 做特征工程 / 设计特征 / 特征变换 时使用。"
license: Apache-2.0
compatibility: Pure Python analysis. No sklearn required for planning.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/data
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Feature Engineer

Design feature plans for ML models.

## When to Use

- Data is cleaned (ETL done), need to design features
- Which columns to use, how to transform them
- Detect data quality issues
- Plan feature interactions
- Before calling ml-pipeline for training

## Feature Type Detection

| Type | Detection | Transform |
|------|-----------|-----------|
| Numeric | int/float, range > 10 | standardize, log_if_skewed, clip |
| Categorical | < 20 unique, string | one_hot / target_encode |
| Temporal | date/time/datetime | extract hour, dayofweek, is_weekend |
| Text | string, length > 50 | TF-IDF / embeddings |
| Binary | 0/1 only | use as-is |

## Data Quality Checks

- Null percentage per column
- Duplicated rows
- Constant columns (zero variance)
- Target leakage detection (feature correlated > 0.99 with target)
- Class imbalance ratio

## Output

```json
{
  "target": "label",
  "n_features": 12,
  "features": [
    {"name": "age", "type": "numeric", "transforms": ["standardize"]},
    {"name": "city", "type": "categorical", "transforms": ["one_hot_if_small"]}
  ],
  "quality_score": 82,
  "issues": ["3 columns have >20% nulls"],
  "interactions_suggested": ["age × income", "is_weekend × category"]
}
```

## Usage

```bash
python3 feature_engineer.py --data data/clean.csv --target label
```

## References

- [references/feature-patterns.md](references/feature-patterns.md) — domain-specific patterns