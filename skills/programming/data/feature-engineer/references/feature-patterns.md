# Feature Patterns（特征工程模式库）

> 配套 feature-engineer。`feature_engineer.py` 只做**规划**：它按列名关键词（name/text/desc → categorical；count/num/total/sum/avg/rate → numeric；date/time/year/month → temporal）猜类型并给出建议变换列表，**不读取数据、不实际构造特征、也不计算相关性**。SKILL.md 里列出的"目标泄漏检测（相关性 > 0.99）"在脚本中未实现（`check_quality` 只检查列名里是否含 null/missing）。因此：脚本给出的是待办清单，本文件给出**落地代码**和**必须人工执行的泄漏检查**。

## 目录
- §0 通用前置检查
- §1 数值型：分箱 / 缩放 / 对数 / 多项式
- §2 类别型：one-hot / 高频截断 / target encoding
- §3 时间型：周期编码 / 滞后 / 窗口统计
- §4 文本型：TF-IDF / 长度统计
- §5 特征交互
- §6 泄漏风险清单（重点）
- §7 交付前检查表

## §0 通用前置检查

任何特征构造前先跑一遍，输出即"能不能放心做特征"的依据：

```python
import pandas as pd, numpy as np
n = len(df)
null_rate = df.isna().mean()
const_cols = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
dup_rows = int(df.duplicated().sum())
imbalance = df[target].value_counts(normalize=True)   # 分类任务
print(null_rate.sort_values(ascending=False).head(10))
print("常量列:", const_cols, "| 重复行:", dup_rows)
```
判据：常量列直接删；缺失率 > 60% 先回到 etl-builder 处理；少数类占比 < 5% 时**不要用 accuracy**评估（见 ml-pipeline 的 `metrics-explained.md`）。

## §1 数值型

| 变换 | 适用场景 | 代码要点 | 注意 |
|---|---|---|---|
| 分箱（等宽） | 边界有业务含义（年龄段） | `pd.cut(x, bins=[0,18,35,60,200])` | 区间外得到 NaN |
| 分箱（等频） | 分布长尾、只关心排序 | `pd.qcut(x, q=10, duplicates="drop")` | 重复分位点需 `duplicates="drop"` |
| 标准化 | 距离/正则/梯度类模型 | `(x - mean) / std`，落地用 `StandardScaler` | 对离群点敏感 |
| min-max | 神经网络、需有界输入 | `(x - min) / (max - min)` | 新数据超出原范围会越界 |
| 对数 | 右偏、跨数量级（金额、人口） | `np.log1p(x)` | 要求 `x > -1`；含零用 log1p |
| 多项式 | 线性模型捕捉非线性 | `PolynomialFeatures(degree=2)` | 特征数爆炸，先筛变量 |

```python
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
df["age_bin"] = pd.cut(df["age"], bins=[0, 18, 35, 60, 200], labels=["<18", "18-35", "35-60", "60+"])
df["income_log"] = np.log1p(df["income"].clip(lower=0))       # 先截断负值再取对数
num_cols = ["income_log", "age"]
df[num_cols] = StandardScaler().fit_transform(df[num_cols])   # 见 §6：须在 Pipeline 内
```
预期：`pd.cut` 返回 Categorical；分箱后 `df["age_bin"].isna().sum()` > 0 说明有值落在 bins 之外（如 age=250）。
坑：`fit_transform` 全量调用会把测试集信息泄进训练过程 → 只在训练集 `fit`，再 `transform` 测试集（或用 `Pipeline`，见 §6）。

## §2 类别型

**one-hot**：类别数少（经验阈值 < 20，SKILL.md 也用 20 作判据）且树/线性模型均可。
```python
df = pd.get_dummies(df, columns=["city"], prefix="city", dtype="int8")
```
**高频截断**：类别数多（如商品 ID 上千）时，只保留覆盖 ~95% 样本的头部类别，其余并入 `"OTHER"`。
```python
top = df["sku"].value_counts(normalize=True).cumsum()
keep = top[top <= 0.95].index
df["sku_c"] = df["sku"].where(df["sku"].isin(keep), "OTHER")
```
预期：`df["sku_c"].nunique()` 明显下降；用 `top.iloc[0] > 0.5` 判断是否存在单一巨型类别。

**target encoding（高风险，必读）**：类别基数大且树模型表现不足时用；**必须在折内计算**。
```python
from sklearn.model_selection import KFold
df["city_te"] = np.nan
for tr, va in KFold(n_splits=5, shuffle=True, random_state=42).split(df):
    m = df.iloc[tr].groupby("city")[target].mean()
    df.iloc[va, df.columns.get_loc("city_te")] = df.iloc[va]["city"].map(m)
df["city_te"] = df["city_te"].fillna(df[target].mean())   # 未见类别 → 全局均值
```
关键点：① 编码值**只用训练折的标签**；② 对测试集必须使用**全训练集**算出的映射（不是折内）；③ 稀有类别（该类别样本数 < 20）编码值极不稳定，建议加平滑：`(sum + prior*alpha) / (count + alpha)`，alpha 取 10–50 量级起步（**需按数据规模验证，VERIFY BEFORE USE**）。
泄漏后果：若直接对全量数据算 `groupby(city)[target].mean()` 再训练，模型会拿到答案本身，交叉验证/测试分数虚高、上线即崩。

## §3 时间型

```python
df = df.sort_values(["user_id", "ts"])            # ① 必须先排序，否则 shift 取到"未来"
df["hour_sin"] = np.sin(2 * np.pi * df["ts"].dt.hour / 24)   # 周期编码：23 点与 0 点相邻
df["hour_cos"] = np.cos(2 * np.pi * df["ts"].dt.hour / 24)
g = df.groupby("user_id")["amount"]
df["lag_1"]  = g.shift(1)                          # 上一笔
df["roll3"]  = g.shift(1).rolling(3).mean()        # 前 3 笔均值（shift(1) 排除当前行）
df["since_last"] = df.groupby("user_id")["ts"].diff().dt.total_seconds()
```
预期：`lag_1` 首行（每个用户）为 NaN；`roll3` 前 3 行为 NaN。
坑（泄漏）：`rolling(n).mean()` **默认包含当前行**，直接用会把当前值（往往与标签相关）泄进特征 → 先 `.shift(1)`，或用 `rolling(window="3D", closed="left")` 这类时间窗口（需 datetime 索引）。
坑（泄漏）：窗口统计必须按实体分组（`groupby("user_id")`），否则跨用户串味。
坑：按时间切分训练/测试集时（时序任务），特征里的统计量只能用**该时间点之前**的窗口；做"全历史均值"等于引入未来信息。

## §4 文本型

```python
from sklearn.feature_extraction.text import TfidfVectorizer
tf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
X_text = tf.fit_transform(df["review"].fillna(""))      # 稀疏矩阵，别 toarray() 大表
df["len_chars"] = df["review"].str.len()
df["len_words"] = df["review"].str.split().str.len()
df["n_digits"]  = df["review"].str.count(r"\d")
```
预期：`X_text.shape == (n_rows, <= 5000)`，稀疏度 > 99%。
坑：`min_df` 与 `max_features` 都是**从语料学到的参数**，只能在训练集拟合后 `transform` 测试集；在切分前对全量 `fit_transform` 就是泄漏（测试集词表进入模型）。
坑：中文需分词（`jieba`）或改用 `analyzer="char"` 的字符 n-gram，否则以空格切词得到整句单一 token。

## §5 特征交互

```python
df["income_per_age"] = df["income"] / df["age"].clip(lower=1)      # 比值
df["amt_x_freq"]     = df["amount"] * df["visit_count"]            # 乘积
df["is_weekend_x_cat"] = df["is_weekend"].astype(str) + "_" + df["category"].astype(str)  # 组合类别
```
适用：线性模型/浅模型需要人工交互；树模型（GBDT/RF）能自行学到低阶交互，加交互主要收益在**业务可解释**的场景。
坑：交互使特征数按组合爆炸；先按重要性筛选 Top-N 再做交互，并监控 CV 标准差是否变大（变大 = 不稳定）。

## §6 泄漏风险清单（重点）

| 特征/做法 | 泄漏途径 | 正确做法 |
|---|---|---|
| target encoding | 用全量标签算类别均值 | 折内计算（KFold / `TargetEncoder` 置于 Pipeline） |
| 滞后/窗口统计 | 未 `shift`、未按实体分组、用了全历史 | `groupby(ent).shift(k).rolling(w)` |
| 标准化 / 分箱边界 / 词表 | 在全量数据 `fit` | `Pipeline` 内 `fit` 只作用于训练折 |
| 缺失值填充值（均值/中位数） | 用全量算 | 同上，归入 Pipeline |
| 特征选择（按相关性筛变量） | 在全量数据上筛 | 每折内重新筛 |
| ID / 时间戳 / 自增序号 | 与目标偶然相关 | 直接剔除（脚本已把 id/index/timestamp/date 列入 skipped） |
| 标签的衍生列（如"退款时间"预测"是否退款"） | 未来信息 | 只用事件发生**前**可得的字段 |

自检（脚本未实现，需你手动执行）：
```python
corr = df.select_dtypes("number").corrwith(df[target]).abs().sort_values(ascending=False)
print(corr.head(10))     # 出现 |corr| > 0.99 → 高度怀疑泄漏
```
另做"时间旅行检查"：把训练集限定为早期数据、测试集为后期数据，若指标断崖式下降，说明存在时序泄漏。

## §7 交付前检查表

- [ ] 每个特征都能回答"这个值在预测时刻**已知**吗？"
- [ ] 所有 `fit`（缩放/编码/词表/填充值/特征选择）都在 Pipeline 或折内
- [ ] `|corr| > 0.99` 的特征已逐个排查
- [ ] 类别型未见值（unseen category）有兜底：`OTHER` / 全局均值
- [ ] 特征数量 ≤ 样本量 / 10（粗略量级，非硬规则），否则先降维或筛选
- [ ] 输出 feature spec（脚本 `generate_features` 的 JSON）与**实际执行**的变换一致，避免文档与代码脱节
