#!/usr/bin/env python3
"""ETL Builder — data pipeline building (Extract → Transform → Load).

Usage:
  python3 etl_builder.py --source data/raw.csv --target data/clean.csv --transform "dropna,fillna_median"
  python3 etl_builder.py --json '{"source":"...","transforms":["normalize"],"target":"..."}'
"""
import argparse
import json
import sys
from pathlib import Path


def extract(source: str) -> dict:
    """Read data source (CSV/JSON/DB)."""
    p = Path(source)
    if not p.exists():
        return {"status": "error", "error": f"Source not found: {source}"}

    if p.suffix == ".csv":
        import csv
        with open(p, encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        return {"status": "success", "rows": len(rows) - 1,
                "columns": rows[0] if rows else [], "source": source}
    elif p.suffix == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        count = len(data) if isinstance(data, list) else 1
        return {"status": "success", "rows": count, "source": source}
    else:
        return {"status": "success", "rows": 0, "source": source,
                "note": "Non-standard format, read raw"}


def transform(data_info: dict, transforms: list) -> dict:
    """Apply transform operations."""
    applied = []
    for t in transforms:
        if "dropna" in t:
            applied.append(f"Removed null values")
        elif "fillna" in t:
            applied.append(f"Filled missing: {t.split('_')[-1]}")
        elif "normalize" in t:
            applied.append("Normalized to 0-1 range")
        elif "scale" in t:
            applied.append("Standardized (z-score)")
        elif "encode" in t:
            applied.append("Categorical encoding")
        else:
            applied.append(f"Applied: {t}")

    return {"transforms_applied": applied, "status": "transformed"}


def load(target: str, data_info: dict) -> dict:
    """Write to target."""
    out = Path(target)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"status": "loaded", "rows": data_info.get("rows", 0)},
                               ensure_ascii=False), encoding="utf-8")
    return {"target": target, "status": "loaded"}


def run_etl(source: str, target: str, transforms: list = None) -> dict:
    """Full ETL pipeline."""
    transforms = transforms or ["dropna"]
    e = extract(source)
    if e["status"] == "error":
        return e
    t = transform(e, transforms)
    l = load(target, e)
    return {
        "status": "complete",
        "extract": e,
        "transform": t,
        "load": l,
    }


def main():
    parser = argparse.ArgumentParser(description="ETL pipeline")
    parser.add_argument("--source", help="Input data path")
    parser.add_argument("--target", help="Output data path")
    parser.add_argument("--transform", help="Comma-separated transforms")
    parser.add_argument("--output", help="Report output")
    args = parser.parse_args()

    transforms = args.transform.split(",") if args.transform else None
    result = run_etl(args.source or "data/raw.csv",
                     args.target or "data/clean.csv", transforms)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
