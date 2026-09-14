# Hyperparameter Guide（调参优先级、搜索策略、泄漏陷阱）

> 配套 ml-pipeline。**不提供任何"最佳参数值"**——最优值取决于数据与任务，照抄别人的数字是常见错误。本文给的是：调哪些参数、按什么顺序、用多少预算、以及怎么避免调参过程本身引入泄漏。
> 代码片段在 scikit-learn 1.8 + Python 3.11 实测可运行。

## 目录
- §0 `ml_pipeline.py` 当前做了什么 / 没做什么
- §1 调参优先级：先调什么
- §2 搜索策略对照（网格 / 随机 / 贝叶斯）
- §3 交叉验证设置与泄漏陷阱（重点）
- §4 早停与过拟合监控
- §5 结果判读：均值 ± 标准差
- §6 复现与记录
- §7 检查清单

## §0 `ml_pipeline.py` 当前做了什么 / 没做什么

已实现（读源码确认）：
- 读 CSV/JSON → `train_test_split(X, y, test_size=0.2, random_state=42)`
- 三个模型**固定参数**：`RandomForestClassifier(n_estimators=100, random_state=42)`、`GradientBoostingClassifier(n_estimators=100, random_state=42)`、`LogisticRegression(max_iter=1000, random_state=42)`
- `cross_val_score(mdl, X, y, cv=min(cv, len(y)//10 or 2))`
- 输出 `train_accuracy` / `test_accuracy` / `f1`（`average="weighted"`）/ `cv_mean` / `cv_std` / `n_samples` / `n_features`

**未实现**（SKILL.md 的 description 或 workflow 提到，但代码里没有）：
- **没有任何调参**（无 GridSearchCV/RandomizedSearchCV）→ 需要按 §2 自己加
- 未计算 ROC-AUC、precision、recall、混淆矩阵
- 未保存模型（`workflow` 里的 save 步骤不存在）
- 未做标准化/编码；类别列处理有风险（见下）

三个必须知道的现状（本机 pandas 3.0.0 实测）：
1. **类别列会被压成 0**：脚本对含 object 的列做 `pd.to_numeric(errors="coerce").fillna(0)`，字符串类别（如 city="BJ"/"SH"）全部变成 `0.0`，**信息完全丢失**。有类别特征时必须先做 one-hot / 目标编码（见 feature-engineer 的 `feature-patterns.md`），或改用 `ColumnTransformer`。
2. **切分未分层**：`train_test_split` 没传 `stratify=y`，不平衡数据下训练/测试集的类别比例可能不同 → 传 `stratify=y`。
3. **CV 在全量数据上算**：`cross_val_score(mdl, X, y, ...)` 用的是完整 `X`（含测试集），且此时 `mdl` 已用训练集 fit 过。报告 CV 分数时说清它是"全量数据的交叉验证"，不要与测试集分数混为一谈。
   补充一点准确信息：传入整数 `cv` 且估计器是分类器时，sklearn 默认使用 `StratifiedKFold`（实测 `check_cv(3, y, classifier=True)` 返回 `StratifiedKFold`），所以 CV 部分是分层的；但 `train_test_split` 不是。

## §1 调参优先级：先调什么

原则：**先定模型族的"容量旋钮"，再调细节**。本节给方向，不给数值。

| 模型族 | 影响最大的参数（优先） | 次优先 | 通常可以不动 |
|---|---|---|---|
| 随机森林 | `max_depth`、`min_samples_leaf`（控制过拟合） | `max_features`、`n_estimators`（越多越稳、边际收益递减、耗时线性增长） | `bootstrap`、`criterion` |
| GBDT（`GradientBoostingClassifier`） | `learning_rate` 与 `n_estimators`（**必须一起调**，二者强耦合）、`max_depth`（常用浅树） | `subsample`、`min_samples_leaf` | `loss` |
| 逻辑回归 | 正则强度 `C`（与其倒数相关，越小正则越强）、`penalty` 与 `solver` 的匹配 | `class_weight`（不平衡时优先） | `max_iter`（不足时报 ConvergenceWarning，加大即可） |

方向性规则（不是数值）：
- 训练集分数远高于测试集 → 降容量（减 `max_depth`、增大 `min_samples_leaf`、加强正则）。
- 训练/测试都差 → 升容量或加特征。
- 树模型加 `n_estimators` 几乎总能改善或持平，但**不能修复过拟合**（过拟合要靠深度/叶子节点数控制）。
- 线性模型对量纲敏感：务必标准化，否则惩罚项不公平、还可能收敛缓慢。

## §2 搜索策略对照（网格 / 随机 / 贝叶斯）

| 策略 | 适合预算 | 优点 | 缺点 |
|---|---|---|---|
| 网格 `GridSearchCV` | 参数 ≤ 3 个、每个取值少（组合数几十） | 可复现、覆盖完整 | 组合爆炸；对不重要的参数浪费预算 |
| 随机 `RandomizedSearchCV` | 几十~几百次试验（默认推荐起点） | 同样预算覆盖更多取值；可指定试验次数 | 不保证找到全局最优 |
| 贝叶斯（Optuna 等） | 几百次以上、单次训练较贵 | 用历史结果指导采样，昂贵场景更省预算 | 需额外依赖；调参本身有随机性 |
| 逐次减半 `HalvingGridSearchCV` | 候选多、训练便宜 | 先用少量资源筛掉差候选 | sklearn 1.8 中仍属**实验性**，需 `from sklearn.experimental import enable_halving_search_cv` 才能导入（实测确认） |

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import randint

pipe = Pipeline([("sc", StandardScaler()),
                 ("rf", RandomForestClassifier(random_state=42))])
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ① 网格：参数少时用
gs = GridSearchCV(pipe, {"rf__max_depth": [3, 5, None],
                         "rf__min_samples_leaf": [1, 3]},
                  scoring="f1_macro", cv=cv, n_jobs=-1)
gs.fit(X_train, y_train)
print(gs.best_params_, round(gs.best_score_, 4))     # 预期：打印最优参数组合与 CV 分数

# ② 随机：给分布 + 试验次数预算
rs = RandomizedSearchCV(pipe, {"rf__max_depth": randint(2, 20)},
                        n_iter=20, scoring="f1_macro", cv=cv, random_state=42)
rs.fit(X_train, y_train)
```
要点：
- 参数名前缀用 `步骤名__` （如 `rf__max_depth`）——这是 `Pipeline` 的写法，写错会得到 `ValueError: Invalid parameter`。
- `scoring` 必须与业务指标一致（不平衡数据别用 `accuracy`，见 `metrics-explained.md`）。
- `n_jobs=-1` 用满 CPU；但**结果的可复现性依赖 `random_state`**，不依赖 `n_jobs`。
- 预算分配经验：先用随机搜索在大范围粗扫，再在最有希望的小范围做网格细化。

## §3 交叉验证设置与泄漏陷阱（重点）

CV 方案选择：

| 数据特点 | CV | 说明 |
|---|---|---|
| 分类、类别不平衡 | `StratifiedKFold` | 保持每折类别比例 |
| 时序 | `TimeSeriesSplit` | **不能**随机打乱，否则用未来预测过去 |
| 同组样本相关（同一用户/同一患者多次记录） | `GroupKFold(groups=...)` | 否则同组样本同时出现在训练与验证折 |
| 一般回归 | `KFold(shuffle=True, random_state=...)` | — |

泄漏陷阱（调参阶段最常犯）：
```python
# 错误：在全量数据上 fit 转换器，再做 CV → 验证折的信息泄进训练
scaler.fit(X)                      # 包含了验证折
X_s = scaler.transform(X)
cross_val_score(model, X_s, y, cv=5)

# 正确：把转换器放进 Pipeline，每折只在训练部分 fit
pipe = Pipeline([("sc", StandardScaler()), ("rf", RandomForestClassifier(random_state=42))])
cross_val_score(pipe, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
```
规则：**一切从数据里"学"出来的东西**（标准化参数、分箱边界、词表、填充值、特征选择、目标编码）都必须放进 `Pipeline`，或者在每折内部重新计算。
另外两层陷阱：① 用测试集反复挑参数 → 测试集实际上变成了验证集，泛化估计失真；正确做法是"训练/验证（CV 调参）+ 测试集只用一次"。② 调参轮数很多时，即使有 CV，最优分数也会乐观偏差；用独立的验证集或嵌套 CV 评估（`cross_val_score(GridSearchCV(...), ...)`）能减少这种偏差。

## §4 早停与过拟合监控

- 监控信号：`train_accuracy` 与 `test_accuracy` 的差距（脚本已同时输出两者）。差距持续扩大 = 过拟合。
- 学习曲线判断是否该加数据还是降容量：
```python
from sklearn.model_selection import learning_curve
sizes, tr, va = learning_curve(pipe, X, y, cv=cv, scoring="f1_macro",
                               train_sizes=[0.2, 0.4, 0.6, 0.8, 1.0])
print(va.mean(axis=1))     # 验证分数随样本量的变化
```
判读：两条曲线仍在上扬且间距大 → 加数据有效；曲线已平且间距大 → 降容量/加正则；都低 → 特征或模型族不合适。
- 迭代式模型（GBDT / XGBoost / LightGBM）的早停：需要留出验证集并通过 `eval_set` 传入，配 `early_stopping_rounds`（XGBoost/LightGBM 的原生 API；sklearn 的 `GradientBoostingClassifier` 另有 `n_iter_no_change` + `validation_fraction` 参数，行为与库版本相关，**VERIFY BEFORE USE**）。
- 早停的验证集不能与调参用的验证集是同一份，否则早停轮数本身也被"调"过拟合了。

## §5 结果判读：均值 ± 标准差

- 脚本输出的 `cv_std` 是 `scores.std()`（numpy 默认 `ddof=0`），表示各折分数的离散程度。
- 判据：两个模型 CV 均值之差**小于**折间标准差的量级时，不能断言谁更好（差异可能来自折的划分）。若要更可靠：增大 `n_splits`、重复 CV（`RepeatedStratifiedKFold`）、或做配对比较（同一批折上比较两个模型）。
- 报告格式：`f1_macro = 0.84 ± 0.03 (5-fold)`，而不是只写 0.84。
- 调参收益要对比基线：先记录默认参数的分数，再判断调参是否真的带来了超出 CV 噪声的提升。

## §6 复现与记录

- 固定所有随机源：模型的 `random_state`、CV 的 `random_state`（`shuffle=True` 时必须给）、搜索的 `random_state`。
- 记录：数据版本（行数/哈希）、代码版本、库版本（`python3 -m pip freeze > requirements.txt`）、参数与分数。
- 每次试验落成一行记录（参数 / cv_mean / cv_std / 耗时），比在脑子里比较可靠；`GridSearchCV` 的 `cv_results_` 可直接导出。

## §7 检查清单

- [ ] 类别特征已正确编码（不要让它们被 `to_numeric` 压成 0）
- [ ] 需要标准化的模型已用 `Pipeline` 包裹
- [ ] 切分用了 `stratify=y`（分类）/ `TimeSeriesSplit`（时序）/ `GroupKFold`（分组）
- [ ] 调参只在训练集/验证折内进行，测试集只评估一次
- [ ] `scoring` 与业务指标一致
- [ ] 报告了 `cv_mean ± cv_std`，并用它判断模型差异是否可信
- [ ] 记录了 seed、库版本与数据版本
- [ ] 调参收益与默认参数基线做过对比
