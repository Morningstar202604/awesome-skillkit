# Transform Recipes (pandas cleaning/transform recipe collection)

> Companion to etl-builder. The SKILL.md Transform table lists 10 operation names (dropna / fillna_median / normalize / encode_onehot …), but `etl_builder.py` currently only **records** the transforms to run and writes back the row count; it does not actually modify the data. This file gives **actionable pandas implementations** of those operation names, for you to run directly or backfill into the script.

## Table of Contents
- §1 Missing values: deletion / imputation / interpolation selection criteria
- §2 Type coercion (numeric, boolean, categorical, nullable integer)
- §3 Deduplication
- §4 String normalization
- §5 Time parsing and time zones
- §6 Wide/long reshaping (melt / pivot)
- §7 Grouped aggregation
- §8 Chunked reading of large datasets
- §9 Normalization and encoding (normalize / one-hot / target)
- §10 Common pitfalls (chained assignment, silent dtype changes, time zones)
- §11 Acceptance checks required after every step

## §1 Missing values: deletion / imputation / interpolation selection criteria

| Criterion | Choice | Reasoning |
|---|---|---|
| Missing rate > 60% and no business meaning | Drop column `drop(columns=...)` | Imputing only injects noise |
| Missing rate < 5% and rows are important | Drop rows `dropna(subset=[...])` | Few samples lost |
| Numeric, skewed distribution | Median imputation | Robust to outliers |
| Numeric, roughly symmetric | Mean imputation | Keeps the mean unchanged |
| Categorical | Mode or explicit `"UNKNOWN"` | The missingness itself may be a signal |
| Time series, ordered | Time interpolation `interpolate(method="time")` | Leverages adjacent observations |
| The missingness itself is meaningful (blank / not applicable) | Add an indicator column `is_missing`, then impute | Preserves information |

```python
import pandas as pd
miss = df.isna().mean().sort_values(ascending=False)      # missing rate per column
print(miss[miss > 0])
df2 = df.drop(columns=miss[miss > 0.6].index)             # drop high-missing columns
df2 = df2.dropna(subset=["order_id", "amount"])           # drop rows missing key columns
num = df2.select_dtypes("number").columns
df2[num] = df2[num].fillna(df2[num].median())             # numeric → median
df2["city"] = df2["city"].fillna("UNKNOWN")               # categorical → explicit value
```
Expected: `miss` is a 0–1 Series; after `fillna`, `df2.isna().sum().sum() == 0` (if still > 0, some column is entirely NaN and needs separate handling).
Pitfall: imputation does not "convert back" columns that have become float—an int column into which NaN was introduced is already float64 when read, and remains float64 after median imputation (tested on pandas 3.0: a nullable `Int64` column stays `Int64` after imputation, but a plain float column does not revert). Re-check `df2.dtypes` after every transform.

Time interpolation requires the index or a parameter column to be datetime:

```python
s = df.set_index("ts")["temperature"]
s_itp = s.interpolate(method="time")      # requires the index to be a DatetimeIndex
```
Expected: endpoint NaNs are not filled (`interpolate` does not extrapolate forward/backward); add `.ffill().bfill()`.
If you get `ValueError: time-weighted interpolation only works on Series or DataFrames with a DatetimeIndex` → first `df["ts"] = pd.to_datetime(df["ts"])`, then `set_index`.

## §2 Type coercion

```python
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")   # invalid values → NaN, no exception
df["age"]    = pd.to_numeric(df["age"], errors="coerce").astype("Int64")  # nullable integer
df["flag"]   = df["flag"].map({"True": True, "False": False}).astype("boolean")
df["city"]   = df["city"].astype("category")
```
Expected: after `errors="coerce"`, invalid values become NaN **silently**—you must immediately check whether `df["amount"].isna().sum()` increased versus before conversion, otherwise dirty values are swallowed quietly.
Pitfall: `astype(int)` raises `IntCastingNaNError` on NaN; use `astype("Int64")` first (capital I, pandas nullable integer).
Pitfall: after `astype("category")`, `value_counts` lists categories that never appear (count 0); run `remove_unused_categories()` before plotting.

## §3 Deduplication

```python
dup_all  = df.duplicated().sum()                       # fully duplicated rows
dup_key  = df.duplicated(subset=["user_id"], keep="last").sum()   # by business key
df = df.drop_duplicates(subset=["user_id"], keep="last")          # keep the latest row
```
Expected: `duplicated()` returns a bool Series, first occurrence is False. Before `keep="last"` takes effect, you must have sorted by time, otherwise "latest" is wrong:
```python
df = df.sort_values("updated_at").drop_duplicates("user_id", keep="last")
```

## §4 String normalization

```python
c = df["name"]
c = (c.str.strip()                            # strip leading/trailing whitespace (full-width spaces need extra handling)
       .str.replace(r"\s+", " ", regex=True)  # collapse internal runs of whitespace into one
       .str.lower()
       .replace({"": None}))                  # empty string → missing
df["name"] = c
```
Expected: after merging whitespace/case differences, `df["name"].nunique()` should **decrease or stay flat**; if it rises, you have accidentally altered data.
Pitfall: the `.str` accessor returns NaN (rather than raising) on non-string elements (e.g. NaN), so outliers survive chained operations.
Pitfall: the full-width space `\u3000` is not guaranteed to match the ASCII semantics of `\s+`; for Chinese data, explicitly handle it with `.str.replace("\u3000", " ")`.

## §5 Time parsing and time zones

```python
df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
df["ts_utc"]   = pd.to_datetime(df["ts"], utc=True)                 # unify to UTC
df["ts_local"] = df["ts_utc"].dt.tz_convert("Asia/Shanghai")        # then convert to local for display
df["date"] = df["ts_local"].dt.date
df["hour"] = df["ts_local"].dt.hour
```
Expected: the `dt` accessor is only available on datetime64 columns; on an object column it raises `AttributeError: Can only use .dt accessor with datetimelike values` → meaning the previous line's parsing failed (usually `errors="coerce"` produced NaN).
Pitfall: mixed time-zone strings raise `ValueError: Tz-aware datetime.datetime cannot be converted to datetime64 unless utc=True` on pandas 2.0+ → add `utc=True`.
Pitfall: `tz_convert` only works on columns that are **already time-zone-aware**; for naive columns use `tz_localize("Asia/Shanghai")`, and calling `tz_localize` on an already-aware column raises `TypeError: Already tz-aware`.
Supplying `format=` significantly speeds things up and avoids the "is 01/02 January 2nd or February 1st?" ambiguity; without a format, pandas infers it, and mixed formats may fail (VERIFY BEFORE USE: test against your local pandas version).

## §6 Wide/long reshaping

```python
long = df.melt(id_vars=["user_id", "date"], value_vars=["a", "b", "c"],
               var_name="metric", value_name="value")
wide = long.pivot_table(index="date", columns="metric", values="value",
                        aggfunc="mean")          # aggfunc is required when keys are duplicated
wide = wide.reset_index()                        # turn the index back into a column
```
Expected: after `melt`, row count ≈ original rows × len(value_vars), column names fixed as `metric` / `value`.
Pitfall: `pivot` (without aggfunc) raises `ValueError: Index contains duplicate entries, cannot reshape` on duplicate (index, columns) pairs → use `pivot_table` or dedupe first.
Pitfall: `pivot_table` defaults to `dropna=True`, so missing combinations disappear entirely as columns; pass `dropna=False` to keep them.

## §7 Grouped aggregation

```python
g = (df.groupby("city", observed=True)                     # observed=True uses only category combos that appear
       .agg(n=("user_id", "size"),
            avg_amount=("amount", "mean"),
            p95=("amount", lambda s: s.quantile(0.95)))
       .reset_index())
```
Expected: result row count = number of unique `city` values; column names are exactly `n / avg_amount / p95` (named aggregation).
Pitfall: `groupby` defaults to `sort=True`, so results are sorted by the group key—if downstream code depends on original order, use `sort=False`.
Pitfall: groupby on a category column produces all category combinations by default (including empty groups); add `observed=True` to suppress.
Pitfall: lambda aggregation runs a Python loop and is slow on large data; prefer built-in strings (`"mean"`, `"quantile"`, etc.).

## §8 Chunked reading of large datasets

```python
total, parts = 0, []
for chunk in pd.read_csv("raw.csv", chunksize=200_000, usecols=["a", "b", "c"],
                         dtype={"a": "int32", "b": "category"}):
    chunk = chunk[chunk["c"] > 0]        # filter early to reduce resident memory
    parts.append(chunk.groupby("b")["a"].sum())
    total += len(chunk)
result = pd.concat(parts).groupby(level=0).sum()
```
Expected: `chunksize` makes `read_csv` return an iterable TextFileReader (not a DataFrame); memory footprint is roughly constant.
Criterion: first use `wc -l` and a single-row sample to determine columns and dtypes, then write the full script; `usecols` + `dtype` noticeably reduce peak memory (the exact amount depends on column count and dtypes; measure).
Pitfall: `groupby(...).sum()` must be **re-aggregated across chunks** (as in the `groupby(level=0).sum()` above); otherwise concatenated chunk results still have duplicate group keys—quantile-type metrics cannot be simply summed, so keep the raw data and compute afterward.

## §9 Normalization and encoding

```python
# min-max → [0,1]
df["x_norm"] = (df["x"] - df["x"].min()) / (df["x"].max() - df["x"].min())
# z-score (when std is 0, all values become NaN/inf; guard against empty)
sd = df["x"].std(ddof=0)
df["x_z"] = (df["x"] - df["x"].mean()) / sd if sd > 0 else 0.0
# one-hot
df = pd.get_dummies(df, columns=["city"], prefix="city", drop_first=False, dtype="int8")
```
Expected: after one-hot, the number of new columns = number of unique `city` values; with `drop_first=True` there is one fewer column (to avoid collinearity in linear models).
Pitfall: calling `get_dummies` **separately on the train/test sets** yields different columns → at runtime, use the train columns as the reference and `reindex(columns=train_cols, fill_value=0)`.
Target encoding (category → target mean) must be computed **within the training fold only**; see the leakage discussion in feature-engineer's `feature-patterns.md`. When etl-builder runs standalone it does not know the target, so `encode_target` needs the target column and fold id passed in separately.

## §10 Common pitfalls

1. **Chained assignment**: `df[df.x > 1]["y"] = 0` may not take effect and raises `SettingWithCopyWarning` (common in pandas 1.x/2.x). Use `df.loc[df.x > 1, "y"] = 0` instead; if the intermediate came from a slice, `.copy()` first. As of pandas 3.0, Copy-on-Write is on by default and this warning no longer appears (VERIFY BEFORE USE: check your local `pd.__version__`).
2. **Silent dtype changes**: `fillna` introducing NaN turns int→float; `replace` introducing strings turns numeric→object. Run `df.dtypes` after each transform to compare.
3. **Time zones**: when exporting CSV across systems, `to_csv` writes offset-aware strings (`2026-09-09 10:00:00+08:00`), which read back as object, not datetime. On disk, prefer unifying to UTC and passing an explicit `format`.
4. **The `inplace` parameter**: `inplace=True` behaves unintuitively when `df` is a view of another object, and as of pandas 3.0 some methods discourage it; write uniformly as `df = df.xxx(...)`.

## §11 Acceptance checks required after every step

```python
def audit(df, step):
    print(step, "| rows:", len(df), "| cols:", df.shape[1],
          "| nulls:", int(df.isna().sum().sum()),
          "| dup:", int(df.duplicated().sum()))
    print(df.dtypes.to_string())
```
Call `audit(df, "after_fillna")` once after each category of transform. If anything does not match expectations → revert to the previous step's copy and redo; do not keep stacking transforms on a dirty result.
