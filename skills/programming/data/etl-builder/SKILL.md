---
name: etl-builder
description: "Build data pipelines: extract from CSV/JSON/DB, apply transforms (clean, normalize, encode), load to target. Supports batch and incremental modes. Use when writing a data pipeline, ETL cleaning, loading data into a database, or raw data needs cleaning before analysis or ML training. Do NOT use for running production ETL schedules (generation and local dry-run only)."
license: Apache-2.0
compatibility: Pure Python standard library (argparse/json/csv). No pandas or external DB required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/data
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# ETL Builder

Builds Extract → Transform → Load data pipelines: the script runs a local dry-run of extraction, transformation, and loading, and emits a structured JSON report. It only does generation and local rehearsal; it doesn't schedule production ETL.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| `--source` | Required | Input data path; supports `.csv` (counted row by row) and `.json` (must be a list); other extensions are treated as "non-standard format". Defaults to data/raw.csv |
| `--target` | Optional | Output path, defaults to data/clean.csv. Note: the script writes a JSON status summary, not the data itself |
| `--transform` | Optional | A comma-separated transform chain, e.g. `dropna,fillna_median,normalize`; defaults to `dropna` |
| `--output` | Optional | Where the report is written; defaults to printing to stdout |

When inputs are missing, ask for all at once: "Please provide: (1) input data path and format (CSV/JSON), (2) output target path, (3) the transform chain you need (default dropna). Everything else I run on defaults: the report prints to the terminal."

## Pre-flight Checks

Probe the environment before running; on any failure → give the fix and STOP:

```bash
python3 --version   # expected 3.8+; on failure: install python3
python3 scripts/etl_builder.py --help >/dev/null 2>&1   # expected exit code 0; on failure: script missing → check the skill directory
test -f <the --source path the user gave>   # expected exit code 0; on failure: file doesn't exist → ask the user for the correct path
```

## Workflow

### Step 1: Confirm the source-data format

```bash
test -f data/raw.csv && head -2 data/raw.csv
```

Expected: the file exists and the first row is a header. On failure: `.json` input must be a list (`python3 -c "import json;print(type(json.load(open('data/raw.json'))))"` should be list); other extensions produce a `Non-standard format, read raw` hint → convert to CSV first, then continue.

### Step 2: Run the pipeline

```bash
python3 scripts/etl_builder.py --source data/raw.csv --target data/clean.csv \
  --transform "dropna,fillna_median,normalize"
```

Expected: stdout emits JSON with `status` = `complete`, containing the three sections `extract.rows`, `transform.transforms_applied`, and `load.status=loaded`. data/clean.csv gets a `{"status": "loaded", ...}` status summary (a skeleton implementation, not the data itself).
On failure: see the failure table below.

### Step 3: Verify the transform chain was recognized correctly

Expected: each name in `transforms_applied` maps to a description (e.g. `dropna` → `Removed null values`). The script recognizes by keyword: `dropna`, `fillna*`, `normalize`, `*scale*`, `encode*`; names outside the set are recorded verbatim as `Applied: <name>` → check the spelling or use a supported transform.

### Step 4: Hand off downstream

Once the cleaned result is ready, report rows_in/rows_out and the applied transforms to the user, then hand off to feature-engineer for feature engineering as needed.

## Transform Quick Reference

| Transform | Script recognizes it | Description |
|------|----------|------|
| `dropna` | Yes (keyword) | Remove rows with missing values |
| `fillna_median` / `fillna_mean` | Yes (`fillna` prefix) | Median/mean imputation |
| `normalize` | Yes (keyword) | Min-max scaling to [0,1] |
| `standardize` | No (recorded as Applied) | Z-score; the script side uses the `scale` keyword |
| `encode_onehot` / `encode_target` | Yes (`encode` prefix) | Categorical encoding |
| `clip_outliers` / `parse_dates` / `rename_cols` | No (recorded as Applied) | Must be implemented in downstream code; the script only records it |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| `status: error`, `Source not found: <path>` | The `--source` path doesn't exist | Check the path and rerun; still failing → ask the user for the correct path |
| `Non-standard format, read raw` | The input isn't a `.csv`/`.json` extension | Convert to CSV first, then run |
| `.json` input parse error | The JSON top level isn't a list | Save it as a list or convert to CSV |
| `transforms_applied` shows `Applied: <name>` | The transform name isn't recognized by keyword | Use a name with a supported prefix per the table above |
| The report wasn't written to a file | `--output` wasn't passed | Expected behavior (prints stdout); add `--output report.json` if you want a file |

## Delivery Criteria

Definition of success: output JSON `status=complete`, with all three extract/transform/load sections present, and the transform chain matching the user's request.
Artifact naming: status summary `<target>` (defaulting to clean.csv in the data directory); report with the name `--output` specifies (suggest `etl_report.json`).
Save location: same directory level as the user's data; the report goes in the working-directory root.
Completeness verification: rerunning the same command gives identical output (pure-function dry-run); `extract.rows` matches the source row count (minus the header).

## Safety Red Lines

- This skill only does a local dry-run; it doesn't touch production scheduling systems or connect to external databases.
- `--target` overwrites a same-named file; if the target path already exists, confirm with the user first.
- The script auto-creates the output directory (`parents=True`); confirm the write location matches the user's expectation.

## References

- [references/transform-recipes.md](references/transform-recipes.md) — read when you need common recipes for combining transforms or handling specific data shapes

After cleaning and loading, **then say: "The clean data is ready; next, call feature-engineer to do feature engineering" — the chain unfolds automatically**.
