---
name: excel-assistant
description: >
  Clean, analyze, and summarize spreadsheet data: inspect structure, fix
  common defects (encoding, merged cells, dates-as-text), compute answers,
  and deliver a cleaned file plus findings. Use when the user asks to 处理Excel /
  清洗数据 / 表格分析 / 这个表怎么回事 / summarize this spreadsheet /
  fix my csv / 汇总统计. Do NOT use for building presentations or writing reports.
license: Apache-2.0
compatibility: Works best with python3 + pandas + openpyxl; degrades to manual guidance.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Excel Assistant (inspect → clean → answer)

Never modify the user's original file. Copy first, clean the copy, show
before/after evidence for every change, and end with a written findings note.

## Inputs

| Input | Required | Default | Notes |
|---|---|---|---|
| file path | yes | — | xlsx / xls / csv |
| goal | yes | — | e.g. 汇总各月销售额 / 找出重复客户 / 画趋势 |
| constraints | no | — | columns to preserve, output format |

If anything required is missing, ask ONCE:

> 请提供：① 表格文件路径；② 你想得到什么结果（一句话即可）。
> 可选：哪些列不能动、希望输出 xlsx 还是 csv。

## Preflight self-check

```bash
python -c "import pandas, openpyxl; print('xl-ok')"
```

- `xl-ok` → automated path below.
- ImportError → tell the user exactly which import failed and offer
  `pip install pandas openpyxl`; without consent, proceed in guide-only mode:
  give precise manual steps instead of running code, and say so plainly.

## Workflow

### Step 1: Inspect before touching anything

```python
import pandas as pd
df = pd.read_csv(PATH, encoding="utf-8-sig")   # or read_excel(PATH)
print(df.shape); print(df.dtypes); print(df.head(3))
print(df.isna().sum())
```

Expected: shape, dtypes, sample rows, null counts. Record these numbers —
they are your before-evidence. CSV garbled? Retry encodings in order:
utf-8-sig → gbk → gb18030.

### Step 2: Clean with one change per step

Apply at most one fix per step, re-running inspection after each:
①去重（`df.duplicated()` 先看再删）→ ②补/标缺失（填充规则要写进交付说明）
→ ③日期列转 datetime（`pd.to_datetime(col, errors="coerce")` 后检查 NaT 数）
→ ④数值列剥离单位字符再转类型。Each step's expected result: null/dup counts
move exactly as predicted; if not, undo and investigate — never chain blind fixes.

### Step 3: Answer the goal

Compute the requested aggregation/trend/ranking. Expected: a number-or-table
that directly answers the user's sentence from Inputs, not adjacent trivia.

### Step 4: Deliver

```python
df.to_excel(PATH_stem + "_cleaned.xlsx", index=False)
```

Plus a short `findings.md`: what was wrong, what you changed, the answer,
and any rows you had to drop (count them).

## Failure handling

| Symptom | Likely cause | Action |
|---|---|---|
| UnicodeDecodeError on csv | non-UTF8 encoding | try gbk then gb18030; report which worked |
| numbers read as object dtype | units/space in cells | strip non-numerics, coerce, count failures |
| dates become NaT en masse | ambiguous day/month order | ask user which convention; add format string |
| merged cells in xlsx | header spanning | openpyxl unmerge, forward-fill header rows, confirm with user |
| totals don't match user's expectation | hidden filters/sheets | state assumption, list sheets examined |

## Delivery standard

Success = `<name>_cleaned.xlsx` (or csv) untouched-original preserved +
`findings.md` containing before/after counts and the direct answer.
Anything else is not done — say so plainly.

## References

None — pandas snippets above are the toolkit.
