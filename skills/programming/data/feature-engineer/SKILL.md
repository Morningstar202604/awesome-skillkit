---
name: feature-engineer
description: "Design feature engineering plans: identify feature types, suggest transforms, detect data quality issues, plan interactions. Outputs a feature spec for ML training. Use after ETL, before model training. Use when doing feature engineering, designing features, feature design, feature transformation, a feature transformation plan, a data quality check, a feature spec, or feature transformation. Do NOT use for model training or hyperparameter tuning."
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

Designs ML feature-engineering plans: identify feature types, suggest transforms, check data quality, and plan interaction features, producing a feature-spec JSON for training. It only does plan design; it doesn't train models.

## Input Checklist

| Input | Required | Description |
|------|------|------|
| `--data` | One of two | CSV path; the script reads the first-row header as column names |
| `--columns` | One of two | An explicit list of column names (space-separated), taking precedence over `--data` |
| `--target` | Optional | Target column name, defaults to `label`; this column and `id/index/timestamp/date` are skipped and not planned |
| `--output` | Optional | Where results are written; defaults to stdout |

When inputs are missing, ask for all at once: "Please provide: (1) the cleaned data file path, or list the feature column names directly; (2) the target column name (default label). Everything else I run on defaults: results print to the terminal."

## Pre-flight Checks

Probe the environment before running; on any failure → give the fix and STOP:

```bash
python3 --version   # expected 3.8+; on failure: install python3
python3 scripts/feature_engineer.py --help >/dev/null 2>&1   # expected exit code 0; on failure: script missing → check the skill directory
test -f <the --data path the user gave>   # expected exit code 0; on failure: file doesn't exist → pass column names explicitly with --columns, or ask the user for the correct path
```

## Workflow

### Step 1: Get the column names

```bash
head -1 data/clean.csv   # expected to print the comma-separated header, consistent with the user's understanding
```

On failure: the file doesn't exist or the header is empty → pass columns explicitly with `--columns col1 col2 ...`; if neither is given, the script falls back to built-in demo columns (`feature_a`, etc.), which are not the user's data and must be avoided.

### Step 2: Generate the feature plan

```bash
python3 scripts/feature_engineer.py --data data/clean.csv --target label
```

Expected: stdout emits JSON with top level `{"quality": {...}, "features": {...}}`; `features.n_features` equals the number of non-skipped columns, and `features.status` is `plan_ready`.

### Step 3: Verify type inference

Expected: each column's `type` matches keyword inference — column name contains `name/text/desc` → `categorical`; contains `count/num/total/sum/avg/rate` → `numeric`; contains `date/time/year/month` → `temporal`; everything else → `auto` (empty `transforms`, needs a manual plan).
On failure: too many `auto` columns → confirm each column's semantics with the user, then adjust manually using `--columns`, or fill in the types directly on the plan JSON.

### Step 4: Check the quality score and report

Expected: `quality.issues` lists detected problems (the current skeleton implementation recognizes them by column names containing `null`/`missing`), and `quality.quality_score = 100 - 10×number of issues`. Report the score and problem columns to the user, then hand off to ml-pipeline for training.

## Feature Type Quick Reference

| Type | Inference keywords (lowercased column name contains) | Default suggested transforms |
|------|---------------------------|--------------|
| numeric | count, num, total, sum, avg, rate | `standardize`, `log_if_skewed`, `clip_outliers` |
| categorical | name, text, desc | `one_hot_if_small`, `target_encode_if_large` |
| temporal | date, time, year, month | `extract_hour`, `extract_dayofweek`, `is_weekend` |
| auto | (everything else) | None — confirm semantics manually, then fill in |

## Failure Handling Table

| Symptom / error code | Cause | Fix |
|------------|------|------|
| Demo columns like `feature_a/feature_b` appear in the output | `--data`/`--columns` wasn't passed; the script fell back to built-in demos | Stop using that output, supply the real column names and rerun |
| `n_features` doesn't match the expected column count | The target column or `id/index/timestamp/date` was skipped | Expected behavior; if the target column has a different name, specify it with `--target` |
| All columns are `auto` | Column names contain no type keyword | Manually confirm column semantics, and directly edit the plan JSON to fill in types and transforms |
| `quality_score` is low | Column names contain `null`/`missing` indicators | First go back to etl-builder to add cleaning, then regenerate the plan |
| The output wasn't written to a file | `--output` wasn't passed | Expected (prints stdout); add `--output feature_plan.json` if you want a file |

## Delivery Criteria

Definition of success: output JSON contains both `quality` and `features` sections, `features.status=plan_ready`, no demo columns, and the target column is correctly skipped.
Artifact naming: feature plan `feature_plan.json` (when written via `--output`).
Save location: same directory as the data file or the working-directory root.
Completeness verification: `n_features` matches the input column count (minus skipped columns); every column has a `type`; `auto` columns are either manually filled in or explained to the user.

## Safety Red Lines

- This skill only produces plans; it doesn't run training or modify data files.
- `--output` overwrites a same-named file; if the target path already exists, confirm with the user first.
- Type inference is based on column-name keywords and can misjudge; review `auto` and suspicious classifications before delivering to the user.

## References

- [references/feature-patterns.md](references/feature-patterns.md) — read when you need domain-specific feature-construction patterns (time series, text, interactions)

Once the feature plan is ready, **then say: "Features are generated; next, call ml-pipeline to train and evaluate the model" — the chain unfolds automatically**.
