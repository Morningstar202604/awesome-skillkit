---
name: etl-builder
description: "Build data pipelines: extract from CSV/JSON/DB, apply transforms (clean, normalize, encode), load to target. Supports batch and incremental modes. Use when raw data needs cleaning before analysis or ML training. 当用户要求 写数据管道 / ETL 清洗 / 数据入库 时使用。 Do NOT use for running production ETL schedules (generation and local dry-run only)."
license: Apache-2.0
compatibility: Requires pandas or csv module. No external DB needed for basic mode.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/data
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# ETL Builder

Extract → Transform → Load data pipelines.

## When to Use

- Raw data is messy, needs cleaning before use
- Need to combine multiple sources
- Data type conversions, null handling, normalization
- Preparing data for feature-engineer or ML training

## Pipeline Stages

### Extract
- CSV, JSON, Parquet, SQLite
- API responses (JSON)
- Log files (line-by-line parse)

### Transform
| Operation | Description |
|-----------|-------------|
| dropna | Remove rows with missing values |
| fillna_median | Fill numeric gaps with median |
| fillna_mean | Fill numeric gaps with mean |
| normalize | Min-max scale to [0,1] |
| standardize | Z-score (mean=0, std=1) |
| encode_onehot | Categorical → binary columns |
| encode_target | Categorical → mean of target |
| clip_outliers | Cap at 1st/99th percentile |
| parse_dates | String → datetime |
| rename_cols | Standardize naming |

### Load
- CSV, Parquet, SQLite, JSON
- Schema validation on load

## Usage

```bash
python3 etl_builder.py --source data/raw.csv --target data/clean.csv \
  --transform "dropna,fillna_median,normalize"
```

## Output

```json
{
  "status": "complete",
  "rows_in": 10000,
  "rows_out": 9850,
  "transforms_applied": ["dropna", "fillna_median", "normalize"],
  "duration_sec": 1.2
}
```

## References

- [references/transform-recipes.md](references/transform-recipes.md) — common ETL patterns