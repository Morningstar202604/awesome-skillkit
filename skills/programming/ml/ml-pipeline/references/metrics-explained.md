# Metrics Explained (evaluation-metric quick reference and selection criteria)

> Companion to ml-pipeline. Formulas and code were tested on scikit-learn 1.8 + Python 3.11; all **specific numbers** in this guide are marked "measured" and come with the reproducing data setup—do not treat them as universal conclusions.

## Table of Contents
- §0 Which metrics `ml_pipeline.py` actually outputs
- §1 Classification metrics (formula / intuition / when not to use / how to call)
- §2 Multiclass averaging: macro / micro / weighted (with measured comparison)
- §3 The threshold is not the default 0.5
- §4 Regression metrics (MAE / RMSE / R² / MAPE)
- §5 Ranking and recommendation metrics
- §6 Metric selection decision table
- §7 Reporting conventions and checklist

## §0 Which metrics `ml_pipeline.py` actually outputs

Output fields (confirmed by reading the source): `train_accuracy` (`accuracy_score(y_train, mdl.predict(X_train))`), `test_accuracy`, `f1` (`f1_score(y_test, pred, average="weighted")`), `cv_mean` / `cv_std`, `n_samples`, `n_features`.
**Not computed**: ROC-AUC, precision, recall, confusion matrix, regression metrics—even though the SKILL.md description mentions ROC-AUC. Add them yourself per §1 when needed.
Note that `f1` uses `average="weighted"`: on imbalanced data it is dominated by the majority class and looks "decent". **Imbalanced tasks should switch to macro or the positive-class F1**; see §2.

## §1 Classification metrics

Notate TP / FP / FN / TN; the positive class is the minority / class of interest defined a priori.

| Metric | Formula | Intuition | When not to use / pitfalls |
|---|---|---|---|
| Accuracy | `(TP+TN)/N` | Overall fraction guessed right | **Fails on class imbalance** (see the measurement in §2: accuracy 0.93 but the minority class is barely detected) |
| Precision | `TP/(TP+FP)` | Are the flagged cases credible? | Ignores misses; used alone it can be gamed by "only flagging the few most certain" |
| Recall | `TP/(TP+FN)` | Did we catch what we should? | Used alone it can be gamed to 100% by "flagging everything positive" |
| F1 | `2PR/(P+R)` | Harmonic mean of P and R | Equal weights on P/R; when business costs are unequal, use weighted F-beta (`fbeta_score`, `beta` parameter) |
| ROC-AUC | `P(score(positive) > score(negative))` | Probability a random positive ranks above a random negative | On extreme imbalance the curve is overly optimistic (many negatives are easy to rank below) → prefer PR-AUC |
| PR-AUC (average precision) | Area under the precision-recall curve | Overall performance on the positive class | Not comparable across tasks when the positive-class definition changes |

```python
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, classification_report)
print(accuracy_score(y_test, pred))
print(precision_score(y_test, pred, zero_division=0))      # avoid divide-by-zero warning when no positives are predicted
print(recall_score(y_test, pred, zero_division=0))
print(f1_score(y_test, pred, average="macro"))
print(roc_auc_score(y_test, proba_pos))                    # pass probabilities/scores for the positive class, not hard labels
print(average_precision_score(y_test, proba_pos))          # PR-AUC
print(classification_report(y_test, pred, digits=3, zero_division=0))
```
Pitfall: `roc_auc_score` also runs if you pass hard labels (treating 0/1 as scores), but the result is meaningless—**you must pass probabilities or decision scores**.
Pitfall: `precision_score` warns and sets the result to 0 when no positives are predicted; explicitly pass `zero_division=0` to remove ambiguity.

## §2 Multiclass averaging: macro / micro / weighted

- **macro**: compute each class's metric first, then **equal-weight average**—independent of class size → rare-class performance strongly affects the result. Use it when "every class matters".
- **micro**: aggregate TP/FP/FN across all classes first, then compute → under **single-label multiclass**, micro-F1 = accuracy (confirmed by measurement, see below).
- **weighted**: weight by each class's **sample count** → majority class dominates; numerically close to accuracy.
- **samples** (multilabel tasks): average over samples.

Measured comparison (three-class, true distribution 90/7/3; predictions almost all the majority class):

| Metric | Measured value |
|---|---|
| accuracy | 0.93 |
| F1 macro | 0.6122 |
| F1 micro | 0.93 |
| F1 weighted | 0.9161 |

Interpretation: accuracy and micro-F1 both give a "nice" 0.93, but macro-F1 is only 0.61—the **minority class is basically undetected**.
Selection criteria: ① you care about every class (especially rare ones) → macro; ② you care about overall sample-level correctness → micro (at which point it is accuracy, so accuracy itself is more direct); ③ you want the metric to reflect "impact on most users" → weighted, but state in the report that it is dominated by the majority class.

## §3 The threshold is not the default 0.5

`predict()` uses a 0.5 threshold, which is almost never optimal when the two class costs are unequal or the data is imbalanced.
```python
from sklearn.metrics import precision_recall_curve
prec, rec, thr = precision_recall_curve(y_test, proba_pos)
# thr has one fewer element than prec/rec; mind the alignment
f1s = 2 * prec * rec / (prec + rec + 1e-12)
best = f1s[:-1].argmax()
print("best threshold:", thr[best], "F1:", f1s[best])
```
Expected: outputs the threshold that maximizes F1. In practice it is more common to "maximize precision given a recall floor" or "given a false-alarm cap"—write the constraint as code and filter `thr`.
The threshold must be chosen on the **validation set**, not the test set (otherwise the test score is distorted).

## §4 Regression metrics

| Metric | Formula | Unit | When not to use / pitfalls |
|---|---|---|---|
| MAE | `mean(|y - ŷ|)` | Same unit as target | Linear weighting of all errors; ignores relative size |
| RMSE | `sqrt(mean((y - ŷ)²))` | Same unit as target | **Sensitive to outliers** (the square amplifies them); a few large errors dominate |
| R² | `1 - SS_res/SS_tot` | Dimensionless | Expresses explanatory power "relative to predicting the mean"; **can be negative** (model worse than the mean) |
| MAPE | `mean(|y-ŷ|/|y|)×100%` | Percentage | **Explodes / unusable when y contains 0 or near-0**; asymmetric in negative vs. positive errors |

```python
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             root_mean_squared_error, r2_score,
                             mean_absolute_percentage_error)
print(mean_absolute_error(y_true, y_pred))
print(root_mean_squared_error(y_true, y_pred))       # introduced in sklearn 1.4+, works on 1.8
print(r2_score(y_true, y_pred))
print(mean_absolute_percentage_error(y_true, y_pred))
```
API change (measured on sklearn 1.8): `mean_squared_error(..., squared=False)` has been **removed**; calling it raises `TypeError: got an unexpected keyword argument 'squared'`; use `root_mean_squared_error` instead.
Measured example (y=[3, -0.5, 2, 7], ŷ=[2.5, 0, 2, 8]): MAE 0.5, RMSE 0.612, R² 0.9486, MAPE 0.3274.
Selection: want the typical error → MAE; large errors are costly → RMSE; need cross-dataset comparison → R² (but state that the baseline is "predicting the mean"); the business is scored as a percentage and y is far from 0 → MAPE, otherwise use sMAPE or MAE/mean.

## §5 Ranking and recommendation metrics

| Metric | Intuition | sklearn |
|---|---|---|
| Precision@K | Fraction of relevant items among the top-K recommendations | Implement yourself, or use `top_k_accuracy_score` (multiclass Top-K hit rate) |
| Recall@K | Fraction of all relevant items covered by the top-K | Implement yourself |
| MAP | Mean of each user's AP (area under the precision-recall curve) | `label_ranking_average_precision_score` (the ranking version; not exactly the same as the recommender AP definition, **VERIFY BEFORE USE**) |
| MRR | Reciprocal rank of the first relevant item, then averaged | Implement yourself |
| NDCG@K | Ranking quality accounting for graded relevance, DCG/IDCG, discount `1/log2(i+1)` | `ndcg_score(y_true, y_score, k=K)` |

```python
from sklearn.metrics import ndcg_score, top_k_accuracy_score
print(ndcg_score(y_true_matrix, y_score_matrix, k=10))
print(top_k_accuracy_score(y_true, proba, k=3))
```
Measured: `ndcg_score([[1,0,0]], [[0.9,0.5,0.1]])` = 1.0 (the relevant item ranks first → full score, as expected).
Note: ranking metrics depend on the "relevance" definition (binary or graded); numbers are not comparable across definitions; state K and the relevance definition in the report.

## §6 Metric selection decision table

| Scenario | First choice | Auxiliary |
|---|---|---|
| Balanced binary classification | accuracy (interpretable) | F1, ROC-AUC |
| Imbalanced binary classification (fraud, faults) | PR-AUC, positive-class F1 / recall | confusion matrix, threshold analysis; **do not report accuracy alone** |
| Multiclass where rare classes matter | macro-F1 | per-class precision/recall table |
| Multiclass focused on overall correctness | accuracy (= micro-F1) | weighted-F1 |
| Regression, want an intuitive error | MAE | RMSE (report both; a large gap signals outliers) |
| Regression, need cross-dataset comparability | R² | MAE |
| Recommendation / search | NDCG@K, Recall@K | MRR, Precision@K |
| Probability quality (risk pricing) | log loss + calibration curve | Brier score |

## §7 Reporting conventions and checklist

- Report format: metric name + value + setup, e.g. `f1_macro = 0.61 ± 0.04 (5-fold, test set)`.
- For classification tasks **attach the confusion matrix**; it tells you more about the error type than any single number.
- Report MAE and RMSE together: a large gap = a few large errors exist; check for outliers.
- When reporting ROC-AUC, also report PR-AUC (especially when imbalanced).
- All metrics are computed on **the same held-out test set that did not participate in training/tuning**.

Checklist:
- [ ] The metric matches the business cost (are the costs of misses vs. false alarms reflected in the metric?)
- [ ] Imbalanced data is not reported as accuracy alone
- [ ] `roc_auc_score` receives probabilities/scores, not hard labels
- [ ] Multiclass averaging method is specified with a justification
- [ ] The threshold was chosen on the validation set, not the test set
- [ ] MAPE is used only when the regression target does not contain 0
- [ ] Reported mean ± std (CV) or the source of confidence, not a single number
