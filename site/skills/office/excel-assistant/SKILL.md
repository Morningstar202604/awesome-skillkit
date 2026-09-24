---
name: excel-assistant
description: >-
  Clean, analyze, and summarize spreadsheet data: inspect structure, fix common
  defects (encoding, merged cells, dates-as-text), compute answers, and deliver
  a cleaned file plus findings. Use when the user asks to process Excel / clean
  data / analyze a spreadsheet / summarize this spreadsheet / fix my csv /
  summarize this table / spreadsheet analysis / data cleaning / pivot summary.
  Do NOT use for building presentations or writing reports.
license: Apache-2.0
compatibility: Works best with python3 + pandas + openpyxl; degrades to manual guidance.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Excel Assistant (Inspect → Clean → Answer)

Never modify the user's original file. Copy first, clean the copy, give
before/after evidence for every change, and attach a written findings note.

## Input Checklist

| Input | Required | Default | Notes |
|---|---|---|---|
| File path | yes | — | xlsx / xls / csv |
| Goal | yes | — | e.g. summarize monthly sales / find duplicate customers / plot trend |
| Constraints | no | — | columns that must not change, output format |

When required inputs are missing, ask once:

> Please provide: 1) spreadsheet file path; 2) what result you want (one
> sentence is enough). Optional: which columns must not change, xlsx or csv
> output.

## Pre-flight Checks

```bash
python -c "import pandas, openpyxl; print('xl-ok')"
```

- Prints `xl-ok` → proceed to automated path below.
- ImportError → clearly state which import failed, suggest `pip install pandas
  openpyxl`; without consent, enter pure guidance mode: give precise manual
  steps instead of executing code, and say so honestly.

## Workflow

### Step 1: Inspect First, Then Touch

```python
import pandas as pd
df = pd.read_csv(PATH, encoding="utf-8-sig")   # or read_excel(PATH)
print(df.shape); print(df.dtypes); print(df.head(3))
print(df.isna().sum())
```

Expected: row/column counts, field types, sample rows, null counts. Record
these numbers—they are the "before" evidence. CSV garbled? Try encodings in
order: utf-8-sig → gbk → gb18030.

### Step 2: One Fix Per Step

At most one fix per step; rerun inspection after each:
1) dedupe (`df.duplicated()` inspect first, then drop) → 2) fill/mark missing
(fill rule goes in delivery notes) → 3) date columns to datetime
(`pd.to_datetime(col, errors="coerce")`, then check NaT count) → 4) strip unit
characters from numeric columns before type conversion.

Expected per step: null/duplicate counts change exactly as predicted; if not,
roll back and investigate—never chain fixes blindly.

### Step 3: Answer the Goal

Compute the required aggregates/trends/sorts. Expected: a number or table that
directly answers the one-sentence goal from the input checklist, not irrelevant
side details.

### Step 4: Deliver

```python
df.to_excel(PATH_stem + "_cleaned.xlsx", index=False)
```

Attach a short `findings.md`: what was wrong, what changed, the answer, and
which rows were deleted (with counts).

## Failure Handling Table

| Symptom | Likely Cause | Action |
|---|---|---|
| csv raises UnicodeDecodeError | Non-UTF8 encoding | Try gbk, gb18030 in order; report which worked |
| Numbers read as object type | Cells contain units/spaces | Strip non-numeric chars then convert; count failures |
| Dates mostly become NaT | Ambiguous day/month order | Ask user which convention; add format string |
| xlsx has merged cells | Header spans columns | Unmerge with openpyxl, fill header row downward, confirm with user |
| Totals disagree with user expectation | Hidden filter/worksheet | State assumptions, list worksheets checked |

## Delivery Criteria

Success = `<name>_cleaned.xlsx` (or csv) with original file untouched +
`findings.md` containing before/after count comparison and the direct answer.
Missing any item means incomplete—say so honestly.

## References

None—the pandas snippets above are the whole toolkit.

## Pipeline Handoff

Usable independently; the cleaned, structured result can feed meeting-notes
(summarize) or resume-tailor (pull quantified bullets from the data).
