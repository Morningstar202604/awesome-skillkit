# Transform Recipes（pandas 清洗/变换配方集）

> 配套 etl-builder。SKILL.md 的 Transform 表列出 10 个操作名（dropna / fillna_median / normalize / encode_onehot …），但 `etl_builder.py` 当前只**记录**将要执行的变换并回写行数，并不真正改动数据。本文件给出这些操作名的**可落地 pandas 实现**，供你直接执行或回填脚本。

## Table of Contents
- §1 缺失值：删除 / 填充 / 插值的选择判据
- §2 类型 coercion（数值、布尔、类别、可空整型）
- §3 去重
- §4 字符串规整
- §5 时间解析与时区
- §6 长宽表转换（melt / pivot）
- §7 分组聚合
- §8 大数据集分块读取
- §9 归一化与编码（normalize / one-hot / target）
- §10 常见坑（链式赋值、dtype 静默变化、时区）
- §11 每步必做的验收检查

## §1 缺失值：删除 / 填充 / 插值的选择判据

| 判据 | 选择 | 理由 |
|---|---|---|
| 缺失率 > 60% 且无业务含义 | 删列 `drop(columns=...)` | 填充只会注入噪声 |
| 缺失率 < 5% 且行重要 | 删行 `dropna(subset=[...])` | 损失样本少 |
| 数值型、分布偏斜 | 中位数填充 | 对离群点稳健 |
| 数值型、近似对称 | 均值填充 | 保持均值不变 |
| 类别型 | 众数或显式 `"UNKNOWN"` | 缺失本身可能是信号 |
| 时间序列、有顺序 | 时间插值 `interpolate(method="time")` | 利用相邻观测 |
| 缺失本身有含义（未填写/不适用） | 加指示列 `is_missing` 后再填 | 保留信息 |

```python
import pandas as pd
miss = df.isna().mean().sort_values(ascending=False)      # 每列缺失率
print(miss[miss > 0])
df2 = df.drop(columns=miss[miss > 0.6].index)             # 删高缺失列
df2 = df2.dropna(subset=["order_id", "amount"])           # 关键列缺失则删行
num = df2.select_dtypes("number").columns
df2[num] = df2[num].fillna(df2[num].median())             # 数值→中位数
df2["city"] = df2["city"].fillna("UNKNOWN")               # 类别→显式值
```
预期：`miss` 是 0–1 的 Series；`fillna` 后 `df2.isna().sum().sum() == 0`（若仍 >0，说明有整列全 NaN，需单独处理）。
坑：填充不会把已经变成 float 的列"变回"整型——引入了 NaN 的 int 列在读取时就已经是 float64，用中位数填充后仍是 float64（pandas 3.0 实测：`Int64` 可空整型列填充后保持 `Int64`，普通 float 列不会回退）。每个变换后 `df2.dtypes` 复核。

时间插值要求索引或参数列是 datetime：

```python
s = df.set_index("ts")["temperature"]
s_itp = s.interpolate(method="time")      # 要求 index 为 DatetimeIndex
```
预期：端点 NaN 不会被填充（`interpolate` 不向前/向后外推），需补 `.ffill().bfill()`。
若报 `ValueError: time-weighted interpolation only works on Series or DataFrames with a DatetimeIndex` → 先 `df["ts"] = pd.to_datetime(df["ts"])` 再 `set_index`。

## §2 类型 coercion

```python
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")   # 非法值→NaN，不抛异常
df["age"]    = pd.to_numeric(df["age"], errors="coerce").astype("Int64")  # 可空整型
df["flag"]   = df["flag"].map({"True": True, "False": False}).astype("boolean")
df["city"]   = df["city"].astype("category")
```
预期：`errors="coerce"` 后非法值变 NaN，**静默发生**——必须立刻查 `df["amount"].isna().sum()` 是否比转换前增加，否则脏值被悄悄吞掉。
坑：`astype(int)` 遇到 NaN 直接抛 `IntCastingNaNError`；先用 `astype("Int64")`（大写 I，pandas 可空整型）。
坑：`astype("category")` 后 `value_counts` 会列出未出现的类别（计数 0），绘图前需 `remove_unused_categories()`。

## §3 去重

```python
dup_all  = df.duplicated().sum()                       # 全行重复
dup_key  = df.duplicated(subset=["user_id"], keep="last").sum()   # 按业务主键
df = df.drop_duplicates(subset=["user_id"], keep="last")          # 保留最新一条
```
预期：`duplicated()` 返回 bool Series，首现为 False。`keep="last"` 生效前需已按时间排序，否则"最新"是错的：
```python
df = df.sort_values("updated_at").drop_duplicates("user_id", keep="last")
```

## §4 字符串规整

```python
c = df["name"]
c = (c.str.strip()                            # 去首尾空白（含全角空格需另加）
       .str.replace(r"\s+", " ", regex=True)  # 内部连续空白压缩为一个
       .str.lower()
       .replace({"": None}))                  # 空串→缺失
df["name"] = c
```
预期：空白/大小写差异被合并后，`df["name"].nunique()` 应**下降或持平**；若上升说明误改了数据。
坑：`.str` 访问器遇到非字符串元素（如 NaN）返回 NaN 而非报错，链式操作后异常值被保留。
坑：全角空格 `\u3000` 不被 `\s+` 的 ASCII 语义保证匹配，中文数据建议 `.str.replace("\u3000", " ")` 显式处理。

## §5 时间解析与时区

```python
df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
df["ts_utc"]   = pd.to_datetime(df["ts"], utc=True)                 # 统一到 UTC
df["ts_local"] = df["ts_utc"].dt.tz_convert("Asia/Shanghai")        # 再转本地展示
df["date"] = df["ts_local"].dt.date
df["hour"] = df["ts_local"].dt.hour
```
预期：`dt` 属性只在 datetime64 列上可用；对 object 列报 `AttributeError: Can only use .dt accessor with datetimelike values` → 说明上一行解析失败（多半是 `errors="coerce"` 产生了 NaN）。
坑：混合时区字符串在 pandas 2.0+ 会抛 `ValueError: Tz-aware datetime.datetime cannot be converted to datetime64 unless utc=True` → 加 `utc=True`。
坑：`tz_convert` 只能用于**已带时区**的列；naive 列要用 `tz_localize("Asia/Shanghai")`，对已带时区的列用 `tz_localize` 会报 `TypeError: Already tz-aware`。
给定 `format=` 能显著提速并避免"01/02 是 1 月 2 日还是 2 月 1 日"的歧义；不给 format 时 pandas 会推断，混合格式可能失败（VERIFY BEFORE USE：以你本地 pandas 版本实测）。

## §6 长宽表转换

```python
long = df.melt(id_vars=["user_id", "date"], value_vars=["a", "b", "c"],
               var_name="metric", value_name="value")
wide = long.pivot_table(index="date", columns="metric", values="value",
                        aggfunc="mean")          # 有重复键时必须给 aggfunc
wide = wide.reset_index()                        # 把 index 还原成列
```
预期：`melt` 后行数 ≈ 原行数 × len(value_vars)，列名固定为 `metric` / `value`。
坑：`pivot`（不带 aggfunc）遇到重复 (index, columns) 组合直接抛 `ValueError: Index contains duplicate entries, cannot reshape` → 换 `pivot_table` 或先去重。
坑：`pivot_table` 默认 `dropna=True`，缺失组合整列消失；需要保留用 `dropna=False`。

## §7 分组聚合

```python
g = (df.groupby("city", observed=True)                     # observed=True 只看出现的类别组合
       .agg(n=("user_id", "size"),
            avg_amount=("amount", "mean"),
            p95=("amount", lambda s: s.quantile(0.95)))
       .reset_index())
```
预期：结果行数 = `city` 的唯一值数；列名即 `n / avg_amount / p95`（命名聚合）。
坑：`groupby` 默认 `sort=True`，结果按组键排序——若下游依赖原顺序需 `sort=False`。
坑：对 category 列 groupby 默认会产生所有类别组合（含空组），加 `observed=True` 抑制。
坑：lambda 聚合走 Python 循环，数据量大时慢；优先用内置字符串（`"mean"`、`"quantile"` 等）。

## §8 大数据集分块读取

```python
total, parts = 0, []
for chunk in pd.read_csv("raw.csv", chunksize=200_000, usecols=["a", "b", "c"],
                         dtype={"a": "int32", "b": "category"}):
    chunk = chunk[chunk["c"] > 0]        # 尽早过滤，减少驻留内存
    parts.append(chunk.groupby("b")["a"].sum())
    total += len(chunk)
result = pd.concat(parts).groupby(level=0).sum()
```
预期：`chunksize` 使 `read_csv` 返回可迭代的 TextFileReader（不是 DataFrame）；内存占用近似恒定。
判据：先用 `wc -l` 和单行采样确定列与 dtype，再写全量脚本；`usecols` + `dtype` 能明显减少峰值内存（具体幅度取决于列数与 dtype，实测为准）。
坑：`groupby(...).sum()` 必须跨块**再次聚合**（如上 `groupby(level=0).sum()`），否则分块结果拼接后仍有重复组键——分位数类指标不能简单相加，需保留原始数据再算。

## §9 归一化与编码

```python
# min-max → [0,1]
df["x_norm"] = (df["x"] - df["x"].min()) / (df["x"].max() - df["x"].min())
# z-score（标准差为 0 时全为 NaN/inf，需判空）
sd = df["x"].std(ddof=0)
df["x_z"] = (df["x"] - df["x"].mean()) / sd if sd > 0 else 0.0
# one-hot
df = pd.get_dummies(df, columns=["city"], prefix="city", drop_first=False, dtype="int8")
```
预期：one-hot 后新增列数 = `city` 唯一值数；`drop_first=True` 时少一列（用于避免线性模型共线性）。
坑：`get_dummies` 在**训练集/测试集分别调用**会得到不同列 → 落地时以训练集列为准 `reindex(columns=train_cols, fill_value=0)`。
target encoding（类别→目标均值）必须在**训练折内**计算，见 feature-engineer 的 `feature-patterns.md` 泄漏说明；etl-builder 单独执行时不知道 target，故 `encode_target` 需额外传入目标列与折号。

## §10 常见坑

1. **链式赋值**：`df[df.x > 1]["y"] = 0` 可能不生效并抛 `SettingWithCopyWarning`（pandas 1.x/2.x 常见）。改用 `df.loc[df.x > 1, "y"] = 0`；若中间结果来自切片，先 `.copy()`。pandas 3.0 起默认启用 Copy-on-Write，该警告不再出现（VERIFY BEFORE USE：以本地 `pd.__version__` 实测为准）。
2. **dtype 静默变化**：`fillna` 引入 NaN 会让 int→float；`replace` 引入字符串会让数值列→object。每个变换后跑一次 `df.dtypes` 对比。
3. **时区**：跨系统导出 CSV 时 `to_csv` 会写下带偏移量的字符串（`2026-09-09 10:00:00+08:00`），再次读入是 object 而非 datetime。落盘建议统一 UTC 并显式 `format`。
4. ** inplace 参数**：`inplace=True` 在 `df` 是别的对象的视图时行为不直观，且 pandas 3.0 起部分方法不推荐；统一写成 `df = df.xxx(...)`。

## §11 每步必做的验收检查

```python
def audit(df, step):
    print(step, "| rows:", len(df), "| cols:", df.shape[1],
          "| nulls:", int(df.isna().sum().sum()),
          "| dup:", int(df.duplicated().sum()))
    print(df.dtypes.to_string())
```
每执行一类变换调用一次 `audit(df, "after_fillna")`。任一项不符合预期 → 回退到上一步的副本重做，不要在脏结果上继续叠加变换。
