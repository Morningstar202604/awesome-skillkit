# Hyperparameter Guide (tuning priorities, search strategies, leakage pitfalls)

> Companion to ml-pipeline. **Do not expect any "best parameter values" here**—the optimal values depend on the data and the task, and copying someone else's numbers is a common mistake. What this guide gives you is: which parameters to tune, in what order, how much budget to spend, and how to avoid the tuning process itself introducing leakage.
> Code snippets are tested to run on scikit-learn 1.8 + Python 3.11.

## Table of Contents
- §0 What `ml_pipeline.py` currently does / does not do
- §1 Tuning priorities: what to tune first
- §2 Search strategy comparison (grid / random / Bayesian)
- §3 Cross-validation setup and leakage pitfalls (key)
- §4 Early stopping and overfitting monitoring
- §5 Interpreting results: mean ± std
- §6 Reproducibility and record-keeping
- §7 Checklist

## §0 What `ml_pipeline.py` currently does / does not do

Implemented (confirmed by reading the source):
- Reads CSV/JSON → `train_test_split(X, y, test_size=0.2, random_state=42)`
- Three models with **fixed parameters**: `RandomForestClassifier(n_estimators=100, random_state=42)`, `GradientBoostingClassifier(n_estimators=100, random_state=42)`, `LogisticRegression(max_iter=1000, random_state=42)`
- `cross_val_score(mdl, X, y, cv=min(cv, len(y)//10 or 2))`
- Outputs `train_accuracy` / `test_accuracy` / `f1` (`average="weighted"`) / `cv_mean` / `cv_std` / `n_samples` / `n_features`

**Not implemented** (mentioned in the SKILL.md description or workflow, but absent from the code):
- **No hyperparameter tuning at all** (no GridSearchCV/RandomizedSearchCV) → you must add it yourself per §2
- Does not compute ROC-AUC, precision, recall, or the confusion matrix
- Does not save the model (the save step in `workflow` does not exist)
- Does no scaling/encoding; categorical column handling is risky (see below)

Three things you must know about the current state (tested on pandas 3.0.0 on this machine):
1. **Categorical columns get squashed to 0**: the script applies `pd.to_numeric(errors="coerce").fillna(0)` to columns containing object dtype, so string categories (e.g. city="BJ"/"SH") all become `0.0`, and **the information is completely lost**. If you have categorical features, you must first do one-hot / target encoding (see feature-engineer's `feature-patterns.md`), or use `ColumnTransformer` instead.
2. **The split is not stratified**: `train_test_split` does not pass `stratify=y`, so on imbalanced data the train/test class proportions may differ → pass `stratify=y`.
3. **CV is computed on the full data**: `cross_val_score(mdl, X, y, ...)` uses the complete `X` (including the test set), and by then `mdl` has already been fit on the training set. When reporting the CV score, make clear that it is "cross-validation on the full dataset"; do not conflate it with the test-set score.
   One accurate clarification: when you pass an integer `cv` and the estimator is a classifier, sklearn defaults to `StratifiedKFold` (tested: `check_cv(3, y, classifier=True)` returns `StratifiedKFold`), so the CV part is stratified; but `train_test_split` is not.

## §1 Tuning priorities: what to tune first

Principle: **first set the "capacity knobs" of the model family, then tune the details**. This section gives direction, not numbers.

| Model family | Highest-impact parameters (priority) | Next priority | Usually left alone |
|---|---|---|---|
| Random forest | `max_depth`, `min_samples_leaf` (control overfitting) | `max_features`, `n_estimators` (more is more stable, diminishing returns, linear runtime growth) | `bootstrap`, `criterion` |
| GBDT (`GradientBoostingClassifier`) | `learning_rate` and `n_estimators` (**must be tuned together**, strongly coupled), `max_depth` (shallow trees commonly used) | `subsample`, `min_samples_leaf` | `loss` |
| Logistic regression | regularization strength `C` (inverse of the penalty strength; smaller = stronger regularization), matching `penalty` to `solver` | `class_weight` (priority when imbalanced) | `max_iter` (raises ConvergenceWarning if too low; just raise it) |

Directional rules (not numbers):
- Training score far above test score → reduce capacity (decrease `max_depth`, increase `min_samples_leaf`, strengthen regularization).
- Both train and test scores are poor → increase capacity or add features.
- Adding `n_estimators` to tree models almost always helps or holds steady, but **cannot fix overfitting** (overfitting must be controlled via depth / leaf count).
- Linear models are sensitive to scale: always standardize, otherwise the penalty term is unfair and convergence may be slow.

## §2 Search strategy comparison (grid / random / Bayesian)

| Strategy | Suitable budget | Pros | Cons |
|---|---|---|---|
| Grid `GridSearchCV` | ≤ 3 parameters, few values each (dozens of combinations) | Reproducible, complete coverage | Combinatorial explosion; wastes budget on unimportant parameters |
| Random `RandomizedSearchCV` | dozens to hundreds of trials (default recommended starting point) | Covers more values at the same budget; you can set the trial count | Does not guarantee the global optimum |
| Bayesian (Optuna etc.) | hundreds+ trials, expensive per training run | Uses past results to guide sampling; saves budget in expensive settings | Extra dependency; tuning itself is stochastic |
| Successive halving `HalvingGridSearchCV` | Many candidates, cheap training | Sifts out poor candidates with few resources first | Still **experimental** in sklearn 1.8; requires `from sklearn.experimental import enable_halving_search_cv` to import (confirmed by testing) |

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import randint

pipe = Pipeline([("sc", StandardScaler()),
                 ("rf", RandomForestClassifier(random_state=42))])
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ① Grid: use when there are few parameters
gs = GridSearchCV(pipe, {"rf__max_depth": [3, 5, None],
                         "rf__min_samples_leaf": [1, 3]},
                  scoring="f1_macro", cv=cv, n_jobs=-1)
gs.fit(X_train, y_train)
print(gs.best_params_, round(gs.best_score_, 4))     # expected: prints the best parameter combo and CV score

# ② Random: give a distribution + a trial-count budget
rs = RandomizedSearchCV(pipe, {"rf__max_depth": randint(2, 20)},
                        n_iter=20, scoring="f1_macro", cv=cv, random_state=42)
rs.fit(X_train, y_train)
```
Key points:
- Parameter names use the `stepname__` prefix (e.g. `rf__max_depth`)—this is the `Pipeline` convention; getting it wrong gives `ValueError: Invalid parameter`.
- `scoring` must match the business metric (don't use `accuracy` on imbalanced data; see `metrics-explained.md`).
- `n_jobs=-1` uses all CPU cores; but **result reproducibility depends on `random_state`, not on `n_jobs`**.
- Rule of thumb for budget allocation: first do a broad random search, then do a fine grid refinement in the most promising small region.

## §3 Cross-validation setup and leakage pitfalls (key)

Choosing a CV scheme:

| Data characteristic | CV | Notes |
|---|---|---|
| Classification, class imbalance | `StratifiedKFold` | Preserves class ratio per fold |
| Time series | `TimeSeriesSplit` | **Do not** shuffle, or you'll be predicting the past with the future |
| Correlated samples in groups (same user / same patient, multiple records) | `GroupKFold(groups=...)` | Otherwise samples from the same group land in both train and validation folds |
| General regression | `KFold(shuffle=True, random_state=...)` | — |

Leakage pitfalls (most common during tuning):
```python
# Wrong: fit the transformer on the full data, then do CV → validation-fold info leaks into training
scaler.fit(X)                      # includes the validation fold
X_s = scaler.transform(X)
cross_val_score(model, X_s, y, cv=5)

# Correct: put the transformer in a Pipeline so it is fit only on the training portion per fold
pipe = Pipeline([("sc", StandardScaler()), ("rf", RandomForestClassifier(random_state=42))])
cross_val_score(pipe, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
```
Rule: **everything "learned" from the data** (scaler parameters, bin edges, vocabularies, fill values, feature selection, target encoding) must go into the `Pipeline`, or be recomputed inside each fold.
Two more layers of pitfalls: ① repeatedly picking parameters on the test set → the test set effectively becomes a validation set, and the generalization estimate is distorted; the correct approach is "train/validate (CV tuning) + use the test set only once". ② when there are many tuning rounds, even with CV the best score is optimistically biased; evaluating with an independent validation set or nested CV (`cross_val_score(GridSearchCV(...), ...)`) reduces this bias.

## §4 Early stopping and overfitting monitoring

- Monitoring signal: the gap between `train_accuracy` and `test_accuracy` (the script outputs both). A steadily widening gap = overfitting.
- Use a learning curve to decide whether to add data or reduce capacity:
```python
from sklearn.model_selection import learning_curve
sizes, tr, va = learning_curve(pipe, X, y, cv=cv, scoring="f1_macro",
                               train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0])
print(va.mean(axis=1))     # how the validation score changes with sample size
```
Interpretation: both curves still rising and a large gap → adding data helps; curves have flattened and a large gap → reduce capacity / add regularization; both low → the features or model family are unsuitable.
- Early stopping for iterative models (GBDT / XGBoost / LightGBM): you need to hold out a validation set and pass it via `eval_set`, together with `early_stopping_rounds` (the native API of XGBoost/LightGBM; sklearn's `GradientBoostingClassifier` instead has `n_iter_no_change` + `validation_fraction` parameters, whose behavior depends on the library version—**VERIFY BEFORE USE**).
- The validation set used for early stopping must not be the same one used for tuning, otherwise the early-stopping round count itself gets "tuned" to overfit.

## §5 Interpreting results: mean ± std

- The script's `cv_std` is `scores.std()` (numpy default `ddof=0`), i.e. the dispersion of the per-fold scores.
- Criterion: when the difference between two models' CV means is **smaller than** the order of magnitude of the between-fold std, you cannot claim one is better (the difference may come from fold partitioning). For more reliability: increase `n_splits`, repeat CV (`RepeatedStratifiedKFold`), or do a paired comparison (compare the two models on the same folds).
- Report format: `f1_macro = 0.84 ± 0.03 (5-fold)`, rather than writing only 0.84.
- Compare tuning gains against a baseline: first record the score with default parameters, then judge whether tuning truly brought an improvement beyond the CV noise.

## §6 Reproducibility and record-keeping

- Fix all random sources: the model's `random_state`, the CV's `random_state` (required when `shuffle=True`), and the search's `random_state`.
- Record: data version (row count / hash), code version, library versions (`python3 -m pip freeze > requirements.txt`), parameters and scores.
- Log each trial as one row (parameters / cv_mean / cv_std / runtime); this is more reliable than comparing in your head. `GridSearchCV`'s `cv_results_` can be exported directly.

## §7 Checklist

- [ ] Categorical features are encoded correctly (don't let them get squashed to 0 by `to_numeric`)
- [ ] Models that need scaling are wrapped in a `Pipeline`
- [ ] The split uses `stratify=y` (classification) / `TimeSeriesSplit` (time series) / `GroupKFold` (grouped)
- [ ] Tuning is done only within the training/validation folds; the test set is evaluated once
- [ ] `scoring` matches the business metric
- [ ] Reported `cv_mean ± cv_std`, and used it to judge whether model differences are credible
- [ ] Recorded the seed, library versions, and data version
- [ ] Tuning gains were compared against the default-parameter baseline
