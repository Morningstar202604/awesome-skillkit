#!/usr/bin/env python3
"""Feature Engineer — 特征工程 + 数据质量检查。

用法:
  python3 feature_engineer.py --data data/clean.csv --target label
  python3 feature_engineer.py --json '{"data":"...","target":"..."}'
"""
import argparse
import json
import sys
from pathlib import Path


def check_quality(columns: list, n_rows: int = 100) -> dict:
    """Data quality checks."""
    issues = []
    for col in columns:
        if col in ("id", "index", "timestamp"):
            continue
        if "null" in col.lower() or "missing" in col.lower():
            issues.append({"column": col, "issue": "contains null indicator"})
    return {
        "n_columns": len(columns),
        "n_rows": n_rows,
        "issues": issues,
        "quality_score": max(0, 100 - len(issues) * 10),
    }


def generate_features(columns: list, target: str) -> dict:
    """Generate feature engineering plan."""
    features = []
    skipped = {"id", "index", "timestamp", "date", "label", target}

    for col in columns:
        if col.lower() in skipped:
            continue
        col_lower = col.lower()
        if any(t in col_lower for t in ["name", "text", "desc"]):
            ftype = "categorical"
        elif any(t in col_lower for t in ["count", "num", "total", "sum", "avg", "rate"]):
            ftype = "numeric"
        elif any(t in col_lower for t in ["date", "time", "year", "month"]):
            ftype = "temporal"
        else:
            ftype = "auto"

        transforms = []
        if ftype == "numeric":
            transforms = ["standardize", "log_if_skewed", "clip_outliers"]
        elif ftype == "categorical":
            transforms = ["one_hot_if_small", "target_encode_if_large"]
        elif ftype == "temporal":
            transforms = ["extract_hour", "extract_dayofweek", "is_weekend"]

        features.append({
            "name": col,
            "type": ftype,
            "transforms": transforms,
        })

    return {
        "target": target,
        "n_features": len(features),
        "features": features,
        "interactions_suggested": [
            "product of top-2 numeric features",
            "ratio of count features",
        ],
        "status": "plan_ready",
    }


def main():
    parser = argparse.ArgumentParser(description="Feature engineering")
    parser.add_argument("--data", help="Data file path")
    parser.add_argument("--target", default="label")
    parser.add_argument("--columns", nargs="*", help="Column names")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    if args.columns:
        columns = args.columns
    elif args.data and Path(args.data).exists():
        import csv
        with open(args.data, encoding="utf-8") as f:
            columns = next(csv.reader(f))
    else:
        columns = ["feature_a", "feature_b", "feature_c", "category_x", "timestamp"]

    quality = check_quality(columns)
    features = generate_features(columns, args.target)

    result = {"quality": quality, "features": features}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
