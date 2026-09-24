# Feature Patterns (feature engineering pattern library)

> Companion to feature-engineer. `feature_engineer.py` only does **planning**: it guesses types from column-name keywords (name/text/desc → categorical; count/num/total/sum/avg/rate → numeric; date/time/year/month → temporal) and gives a suggested transform list, **without reading the data, actually constructing features, or computing correlations**. The "target leakage detection (correlation > 0.99)" listed in SKILL.md is not implemented in the script (`check_quality` only checks whether column names contain null/missing). Therefore: the script gives a to-do list, and this file gives **runnable code** and **leakage checks that must be done manually**.

## Table of Contents
- §0 General pre-checks
- §1 Numeric: binning / scaling / log / polynomial
- §2 Categorical: one-hot / high-frequency truncation / target encoding
- §3 Temporal: cyclic encoding / lags / window statistics
- §4 Text: TF-IDF / length statistics
- §5 Feature interactions
- §6 Leakage risk checklist (key)
- §7 Pre-delivery checklist

## §0 General pre-checks

Run this before any feature construction; the output is the basis for "whether it's safe to engineer features":

```python
import pandas as pd, numpy as np
n = len(df)
null_rate = df.isna().mean()
const_cols = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
dup_rows = int(df.duplicated().sum())
imbalance = df[target].value_counts(normalize=True)   # classification task
print(null_rate.sort_values(ascending=False).head(10))
print("constant columns:", const_cols, "| duplicate rows:", dup_rows)
```
Criteria: drop constant columns outright; for a missing rate > 60%, go back to etl-builder first; when the minority class share is < 5%, **do not evaluate with accuracy** (see ml-pipeline's `metrics-explained.md`).

## §1 Numeric

| Transform | When to use | Code key points | Notes |
|---|---|---|---|
| Binning (equal-width) | Boundaries have business meaning (age groups) | `pd.cut(x, bins=[0,18,35,60,200])` | Values outside the range become NaN |
| Binning (equal-frequency) | Long-tailed distribution, only the order matters | `pd.qcut(x, q=10, duplicates="drop")` | Duplicate quantiles need `duplicates="drop"` |
| Standardization | Distance/regularization/gradient-based models | `(x - mean) / std`; use `StandardScaler` at runtime | Sensitive to outliers |
| min-max | Neural networks, bounded inputs needed | `(x - min) / (max - min)` | New data outside the original range goes out of bounds |
| Log | Right-skewed, across magnitudes (amounts, populations) | `np.log1p(x)` | Requires `x > -1`; use log1p when zeros are present |
| Polynomial | Linear model capturing nonlinearity | `PolynomialFeatures(degree=2)` | Feature count explodes; filter variables first |

```python
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
df["age_bin"] = pd.cut(df["age"], bins=[0, 18, 35, 60, 200], labels=["<18", "18-35", "35-60", "60+"])
df["income_log"] = np.log1p(df["income"].clip(lower=0))       # clip negatives before taking the log
num_cols = ["income_log", "age"]
df[num_cols] = StandardScaler().fit_transform(df[num_cols])   # see §6: must be inside a Pipeline
```
Expected: `pd.cut` returns a Categorical; after binning, if `df["age_bin"].isna().sum()` > 0, some values fell outside the bins (e.g. age=250).
Pitfall: calling `fit_transform` on the full set leaks test-set information into training → `fit` only on the training set, then `transform` the test set (or use a `Pipeline`, see §6).

## §2 Categorical

**one-hot**: when there are few categories (rule of thumb < 20; SKILL.md also uses 20 as the threshold) and either tree or linear models work.
```python
df = pd.get_dummies(df, columns=["city"], prefix="city", dtype="int8")
```
**High-frequency truncation**: when there are many categories (e.g. thousands of product IDs), keep only the head categories covering ~95% of samples and merge the rest into `"OTHER"`.
```python
top = df["sku"].value_counts(normalize=True).cumsum()
keep = top[top <= 0.95].index
df["sku_c"] = df["sku"].where(df["sku"].isin(keep), "OTHER")
```
Expected: `df["sku_c"].nunique()` drops markedly; use `top.iloc[0] > 0.5` to judge whether a single giant category exists.

**Target encoding (high risk, must read)**: use when cardinality is high and tree models underperform; **must be computed within folds**.
```python
from sklearn.model_selection import KFold
df["city_te"] = np.nan
for tr, va in KFold(n_splits=5, shuffle=True, random_state=42).split(df):
    m = df.iloc[tr].groupby("city")[target].mean()
    df.iloc[va, df.columns.get_loc("city_te")] = df.iloc[va]["city"].map(m)
df["city_te"] = df["city_te"].fillna(df[target].mean())   # unseen category → global mean
```
Key points: ① the encoded value uses **only the training fold's labels**; ② for the test set you must use the mapping computed on the **full training set** (not within a fold); ③ rare categories (fewer than 20 samples in that category) have very unstable encoded values—add smoothing: `(sum + prior*alpha) / (count + alpha)`, starting alpha around 10–50 (**must be validated against your data scale, VERIFY BEFORE USE**).
Leakage consequence: if you directly compute `groupby(city)[target].mean()` on the full data and then train, the model gets the answer itself; cross-validation/test scores are inflated and it crashes in production.

## §3 Temporal

```python
df = df.sort_values(["user_id", "ts"])            # ① must sort first, otherwise shift picks up the "future"
df["hour_sin"] = np.sin(2 * np.pi * df["ts"].dt.hour / 24)   # cyclic encoding: 23:00 and 0:00 are adjacent
df["hour_cos"] = np.cos(2 * np.pi * df["ts"].dt.hour / 24)
g = df.groupby("user_id")["amount"]
df["lag_1"]  = g.shift(1)                          # previous transaction
df["roll3"]  = g.shift(1).rolling(3).mean()        # mean of the previous 3 (shift(1) excludes the current row)
df["since_last"] = df.groupby("user_id")["ts"].diff().dt.total_seconds()
```
Expected: `lag_1`'s first row (per user) is NaN; `roll3`'s first 3 rows are NaN.
Pitfall (leakage): `rolling(n).mean()` **includes the current row by default**; using it directly leaks the current value (often correlated with the label) into the features → first `.shift(1)`, or use a time window like `rolling(window="3D", closed="left")` (requires a datetime index).
Pitfall (leakage): window statistics must be grouped by entity (`groupby("user_id")`), otherwise information leaks across users.
Pitfall: when splitting train/test by time (time-series tasks), the statistics in the features may only use windows **before that point in time**; doing a "full-history mean" is equivalent to introducing future information.

## §4 Text

```python
from sklearn.feature_extraction.text import TfidfVectorizer
tf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
X_text = tf.fit_transform(df["review"].fillna(""))      # sparse matrix; don't toarray() a big table
df["len_chars"] = df["review"].str.len()
df["len_words"] = df["review"].str.split().str.len()
df["n_digits"]  = df["review"].str.count(r"\d")
```
Expected: `X_text.shape == (n_rows, <= 5000)`, sparsity > 99%.
Pitfall: `min_df` and `max_features` are both **parameters learned from the corpus**; you may only `transform` the test set after fitting on the training set; calling `fit_transform` on the full data before the split is leakage (the test vocabulary enters the model).
Pitfall: Chinese needs tokenization (`jieba`) or switch to character n-grams with `analyzer="char"`; otherwise whitespace splitting gives the whole sentence as a single token.

## §5 Feature interactions

```python
df["income_per_age"] = df["income"] / df["age"].clip(lower=1)      # ratio
df["amt_x_freq"]     = df["amount"] * df["visit_count"]            # product
df["is_weekend_x_cat"] = df["is_weekend"].astype(str) + "_" + df["category"].astype(str)  # combined category
```
When to use: linear/shallow models need manual interactions; tree models (GBDT/RF) can learn low-order interactions themselves—the main payoff from interactions is in **business-interpretable** scenarios.
Pitfall: interactions make the feature count explode combinatorially; first select Top-N by importance before interacting, and monitor whether the CV std grows (growth = instability).

## §6 Leakage risk checklist (key)

| Feature / practice | Leakage path | Correct practice |
|---|---|---|
| Target encoding | Computing category means on full labels | Within-fold computation (KFold / put `TargetEncoder` in the Pipeline) |
| Lag / window statistics | No `shift`, not grouped by entity, using full history | `groupby(ent).shift(k).rolling(w)` |
| Scaling / bin edges / vocabulary | `fit` on the full data | `fit` inside the Pipeline, applied only to the training fold |
| Missing-value imputation (mean/median) | Computed on the full set | Same as above; fold it into the Pipeline |
| Feature selection (filtering variables by correlation) | Filtering on the full data | Re-filter inside each fold |
| ID / timestamp / auto-increment index | Coincidentally correlated with the target | Drop outright (the script already lists id/index/timestamp/date as skipped) |
| Derived columns of the label (e.g. "refund time" predicting "whether refunded") | Future information | Only use fields available **before** the event |

Self-check (not implemented by the script; do it manually):
```python
corr = df.select_dtypes("number").corrwith(df[target]).abs().sort_values(ascending=False)
print(corr.head(10))     # any |corr| > 0.99 → strongly suspect leakage
```
Also do a "time-travel check": restrict the training set to early data and the test set to later data; if the metric drops off a cliff, there is temporal leakage.

## §7 Pre-delivery checklist

- [ ] Every feature can answer "is this value **known** at prediction time?"
- [ ] All `fit`s (scaling/encoding/vocabulary/imputation/feature selection) are in the Pipeline or within folds
- [ ] Features with `|corr| > 0.99` were investigated one by one
- [ ] Categorical unseen values have a fallback: `OTHER` / global mean
- [ ] Feature count ≤ samples / 10 (rough order of magnitude, not a hard rule); otherwise reduce dimensions or filter first
- [ ] The output feature spec (the JSON from the script's `generate_features`) matches the **actually executed** transforms, so the docs don't drift from the code
