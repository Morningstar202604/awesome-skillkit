# Metrics Explained（评估指标速查与选择判据）

> 配套 ml-pipeline。公式与代码在 scikit-learn 1.8 + Python 3.11 实测；文中所有**具体数值都标注了"实测"**并给出复现用的数据设定，不要把它们当成普适结论。

## 目录
- §0 `ml_pipeline.py` 实际输出哪些指标
- §1 分类指标（公式 / 直觉 / 不适用 / 调用）
- §2 多分类 averaging：macro / micro / weighted（含实测对比）
- §3 阈值不是默认 0.5
- §4 回归指标（MAE / RMSE / R² / MAPE）
- §5 排序与推荐指标
- §6 指标选择决策表
- §7 报告规范与检查清单

## §0 `ml_pipeline.py` 实际输出哪些指标

输出字段（读源码确认）：`train_accuracy`（`accuracy_score(y_train, mdl.predict(X_train))`）、`test_accuracy`、`f1`（`f1_score(y_test, pred, average="weighted")`）、`cv_mean` / `cv_std`、`n_samples`、`n_features`。
**未计算**：ROC-AUC、precision、recall、混淆矩阵、回归指标——尽管 SKILL.md 的 description 提到了 ROC-AUC。需要时按本文 §1 自行补充。
注意 `f1` 用的是 `average="weighted"`：在类别不平衡时它会被大类主导，看起来"还不错"。**不平衡任务应改用 macro 或针对正类的 F1**，见 §2。

## §1 分类指标

记 TP / FP / FN / TN，正类为先验定义的少数/关注类。

| 指标 | 公式 | 直觉 | 不适用 / 陷阱 |
|---|---|---|---|
| Accuracy | `(TP+TN)/N` | 整体猜对的比例 | **类别不平衡时失效**（见 §2 实测：accuracy 0.93 但少数类几乎没被识别） |
| Precision | `TP/(TP+FP)` | 报出来的是否可信 | 不看漏检；单独用可被"只报最确定的几个"刷高 |
| Recall | `TP/(TP+FN)` | 该抓的是否抓到 | 单独用可被"全报正类"刷满 |
| F1 | `2PR/(P+R)` | P 与 R 的调和平均 | 对 P/R 等权；业务代价不等时改用加权 F-beta（`fbeta_score`, `beta` 参数） |
| ROC-AUC | `P(score(正) > score(负))` | 随机正例排在随机负例前的概率 | 极度不平衡时曲线过于乐观（大量负例容易排后）→ 优先看 PR-AUC |
| PR-AUC（average precision） | 精确率-召回率曲线下面积 | 关注正类的整体表现 | 正类定义变化时不可跨任务比较 |

```python
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, classification_report)
print(accuracy_score(y_test, pred))
print(precision_score(y_test, pred, zero_division=0))      # 无正例预测时避免除零警告
print(recall_score(y_test, pred, zero_division=0))
print(f1_score(y_test, pred, average="macro"))
print(roc_auc_score(y_test, proba_pos))                    # 传入正类概率/得分，不是硬标签
print(average_precision_score(y_test, proba_pos))          # PR-AUC
print(classification_report(y_test, pred, digits=3, zero_division=0))
```
坑：`roc_auc_score` 传硬标签也能算（等价于把 0/1 当得分），结果无意义——**必须传概率或决策分数**。
坑：`precision_score` 在没有任何正例预测时会警告并把结果置 0，显式传 `zero_division=0` 消除歧义。

## §2 多分类 averaging：macro / micro / weighted

- **macro**：先算每个类的指标再**等权平均**，与类规模无关 → 稀有类表现会显著影响结果。想"每个类都重要"时用它。
- **micro**：汇总所有类的 TP/FP/FN 后计算 → 在**单标签多分类**下 micro-F1 = accuracy（实测确认，见下）。
- **weighted**：按每个类的**样本数**加权 → 大类主导，数值上常接近 accuracy。
- **samples**（多标签任务）：按样本求平均。

实测对比（三分类，真实分布 90/7/3；预测几乎全为多数类）：

| 指标 | 实测值 |
|---|---|
| accuracy | 0.93 |
| F1 macro | 0.6122 |
| F1 micro | 0.93 |
| F1 weighted | 0.9161 |

判读：accuracy 与 micro-F1 都给出 0.93 的"好看"数字，但 macro-F1 只有 0.61——**少数类基本没被识别**。
选择判据：① 关心每个类（尤其稀有类）→ macro；② 关心整体样本层面的正确率 → micro（此时它就是 accuracy，直接用 accuracy 更直白）；③ 想让指标反映"对多数用户的影响"→ weighted，但要在报告里说明它被大类主导。

## §3 阈值不是默认 0.5

`predict()` 用 0.5 阈值，这在两类代价不等或不平衡时几乎不是最优。
```python
from sklearn.metrics import precision_recall_curve
prec, rec, thr = precision_recall_curve(y_test, proba_pos)
# thr 比 prec/rec 少一个元素，注意对齐
f1s = 2 * prec * rec / (prec + rec + 1e-12)
best = f1s[:-1].argmax()
print("best threshold:", thr[best], "F1:", f1s[best])
```
预期：输出使 F1 最大的阈值。业务上更常见的是"给定召回率下限求最大精确率"或"给定误报上限"——把约束写成代码筛选 `thr` 即可。
阈值必须在**验证集**上选，不能在测试集上选（否则测试分数失真）。

## §4 回归指标

| 指标 | 公式 | 单位 | 不适用 / 陷阱 |
|---|---|---|---|
| MAE | `mean(|y - ŷ|)` | 与目标同单位 | 对所有误差线性加权；不看相对大小 |
| RMSE | `sqrt(mean((y - ŷ)²))` | 与目标同单位 | **对离群点敏感**（平方项放大），少数大误差会主导结果 |
| R² | `1 - SS_res/SS_tot` | 无量纲 | 表示"相对于预测均值"的解释力；**可以为负**（模型不如均值） |
| MAPE | `mean(|y-ŷ|/|y|)×100%` | 百分比 | **y 含 0 或接近 0 时爆炸/不可用**；对负误差与正误差不对称 |

```python
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                             root_mean_squared_error, r2_score,
                             mean_absolute_percentage_error)
print(mean_absolute_error(y_true, y_pred))
print(root_mean_squared_error(y_true, y_pred))       # sklearn 1.4+ 引入，1.8 实测可用
print(r2_score(y_true, y_pred))
print(mean_absolute_percentage_error(y_true, y_pred))
```
API 变更（sklearn 1.8 实测）：`mean_squared_error(..., squared=False)` **已移除**，调用会抛 `TypeError: got an unexpected keyword argument 'squared'`；改用 `root_mean_squared_error`。
实测示例（y=[3, -0.5, 2, 7]，ŷ=[2.5, 0, 2, 8]）：MAE 0.5、RMSE 0.612、R² 0.9486、MAPE 0.3274。
选择建议：想看典型误差 → MAE；大误差代价高 → RMSE；需要跨数据集比较 → R²（但必须说明基准是"预测均值"）；业务按百分比考核且 y 远离 0 → MAPE，否则用 sMAPE 或 MAE/均值。

## §5 排序与推荐指标

| 指标 | 直觉 | sklearn |
|---|---|---|
| Precision@K | 前 K 个推荐里相关项的比例 | 自行实现，或用 `top_k_accuracy_score`（多分类的 Top-K 命中率） |
| Recall@K | 前 K 个覆盖了全部相关项的比例 | 自行实现 |
| MAP | 各用户 AP（精确率-召回率曲线下面积）的平均 | `label_ranking_average_precision_score`（排序版，与推荐场景的 AP 定义不完全相同，**VERIFY BEFORE USE**） |
| MRR | 第一个相关项排名的倒数，再取平均 | 自行实现 |
| NDCG@K | 考虑相关度等级的排序质量，DCG/IDCG，折扣 `1/log2(i+1)` | `ndcg_score(y_true, y_score, k=K)` |

```python
from sklearn.metrics import ndcg_score, top_k_accuracy_score
print(ndcg_score(y_true_matrix, y_score_matrix, k=10))
print(top_k_accuracy_score(y_true, proba, k=3))
```
实测：`ndcg_score([[1,0,0]], [[0.9,0.5,0.1]])` = 1.0（相关项排第一 → 满分，符合预期）。
注意：排序指标依赖"相关度"定义（二值还是多级），换定义后数值不可比；报告时必须写明 K 与相关度定义。

## §6 指标选择决策表

| 场景 | 首选 | 辅助 |
|---|---|---|
| 平衡二分类 | accuracy（可解释） | F1、ROC-AUC |
| 不平衡二分类（欺诈、故障） | PR-AUC、正类 F1 / recall | 混淆矩阵、阈值分析；**不要只报 accuracy** |
| 多分类且关心稀有类 | macro-F1 | 每类的 precision/recall 表 |
| 多分类关注整体正确率 | accuracy（= micro-F1） | weighted-F1 |
| 回归、需直观误差 | MAE | RMSE（同时报，差距大说明有离群点） |
| 回归、需跨数据集可比 | R² | MAE |
| 推荐/搜索 | NDCG@K、Recall@K | MRR、Precision@K |
| 概率质量（风控定价） | 对数损失 + 校准曲线 | Brier score |

## §7 报告规范与检查清单

- 报告格式：指标名 + 数值 + 设定，例如 `f1_macro = 0.61 ± 0.04 (5-fold, test set)`。
- 分类任务**附上混淆矩阵**，它比任何单一数字都能说明问题类型。
- 同时报 MAE 与 RMSE：二者差距大 = 存在少数大误差，需检查离群点。
- 报告 ROC-AUC 时一并报 PR-AUC（尤其不平衡时）。
- 所有指标都在**同一份未参与训练/调参的测试集**上计算。

检查清单：
- [ ] 指标与业务代价一致（漏检与误报的代价是否反映在指标里）
- [ ] 不平衡数据没有只报 accuracy
- [ ] `roc_auc_score` 传的是概率/得分而非硬标签
- [ ] 多分类明确了 averaging 方式并说明理由
- [ ] 阈值在验证集上选择，不是测试集
- [ ] 回归任务目标不含 0 才用 MAPE
- [ ] 报告了均值 ± 标准差（CV）或置信来源，而非单个数字
