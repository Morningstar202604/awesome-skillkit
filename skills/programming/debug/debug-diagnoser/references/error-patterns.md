# Error Patterns（Python 报错模式速查）

> 配套 debug-diagnoser。`diagnoser.py` 用 10 条正则（`ERROR_PATTERNS`）对整段日志做 `re.search`（忽略大小写）并按 severity 排序输出 JSON；它对**单行错误文本**最有效，无法替代人工定位。本文件是人工侧的补充：按错误类型给成因、定位步骤和修复示例。
> 每个模式格式：`原文片段` → 成因 → 定位 → 修复。

## 目录
- §0 读 traceback 的三条规则 + 二分定位
- §1 TypeError
- §2 KeyError（含 pandas 列名陷阱）
- §3 AttributeError
- §4 ValueError（含 pandas Length mismatch）
- §5 IndexError
- §6 ImportError / ModuleNotFoundError
- §7 pandas / numpy 特有误导性报错
- §8 把新模式加进 diagnoser

## §0 读 traceback 的三条规则 + 二分定位

1. **最后一行**是错误类型与消息（`TypeError: ...`）；**倒数第二部分**是异常发生的具体代码行。中间的 `File "...", line N, in func` 是调用链，自下而上读。
2. 有 `During handling of the above exception, another exception occurred:` 时，**真正原因是上面那个**，下面是处理失败时抛出的新异常。
3. 有 `The above exception was the direct cause of ...` 时，看 `raise X from Y` 里的 Y。

二分定位（报错点不等于根因时）：
```bash
python3 -m pdb your_script.py        # 交互调试：在报错帧用 p 打印变量
python3 -X dev your_script.py        # 开发模式：打开额外警告，常能暴露根因
```
或在可疑段前后各插一行 `print(repr(x))`，先确认**输入**是否正确，再确认**输出**；若输入已错，继续向上游函数重复该动作。

## §1 TypeError

| 原文片段 | 常见成因 |
|---|---|
| `TypeError: 'NoneType' object is not subscriptable` | 函数无返回值（默认返回 None）却被 `x[0]` 索引；`dict.get()` 未命中返回 None |
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | 输入来自 CSV/JSON 未转换类型 |
| `TypeError: f() missing 1 required positional argument: 'y'` | 调用漏参 / 方法当函数用（少传 self 场景多见于把实例方法当回调） |
| `TypeError: 'int' object is not callable` | 变量覆盖了同名函数（如 `len = 5`） |

定位：打印被操作对象的类型，而不是值——`print(type(obj), repr(obj)[:80])`。
修复：
```python
val = d.get("key")
if val is None:                 # 显式处理 None，而非假设存在
    val = default
val = int(val)                  # 输入边界统一转类型
```

## §2 KeyError

| 原文片段 | 常见成因 |
|---|---|
| `KeyError: 'amount'`（dict） | 键不存在或拼写/大小写不一致 |
| `KeyError: 'amount '`（pandas） | **列名带首尾空格**（CSV 导出常见） |
| `KeyError: ('a', 'b')` | 这是 MultiIndex，需传元组 |

定位（pandas 第一步必做）：
```python
print([repr(c) for c in df.columns])      # repr 能暴露看不见的空格与换行
df.columns = df.columns.str.strip()       # 修复：统一去空格
print(df.columns.tolist())
```
修复：`d.get(k, default)`；pandas 先校验 `if col not in df.columns: raise KeyError(f"missing {col}; available={list(df.columns)}")`（把可用键打出来，比原生 KeyError 有用得多）。

## §3 AttributeError

| 原文片段 | 常见成因 |
|---|---|
| `AttributeError: 'NoneType' object has no attribute 'append'` | 链式调用中间返回 None（`list.append` / `sort` 原地返回 None） |
| `AttributeError: 'DataFrame' object has no attribute 'append'` | pandas 2.0 起移除了 `DataFrame.append`（改用 `pd.concat`） |
| `AttributeError: Can only use .dt accessor with datetimelike values` | 列还是 object，日期解析失败（多半 `errors="coerce"` 产生了 NaN） |
| `AttributeError: module 'x' has no attribute 'y'` | 循环导入导致模块未初始化完；或本地文件与库同名（如当前目录有 `json.py`） |

定位：确认对象是**你认为的类**——`print(type(obj), obj is None)`；模块类问题打 `print(mod.__file__)` 看导入的是不是你以为的那个文件。
修复：`out = []` 然后 `out.append(x)`（不要 `out = out.append(x)`）；`pd.concat([df1, df2])`；`df["ts"] = pd.to_datetime(df["ts"], errors="coerce")` 后检查 `isna().sum()`。

## §4 ValueError

| 原文片段 | 常见成因 |
|---|---|
| `ValueError: could not convert string to float: 'abc'` | 脏数据（单位后缀、千分位逗号、空串） |
| `ValueError: Length of values (3) does not match length of index (4)` | 赋值右侧长度与 DataFrame 行数不等（常见于 `apply` 返回变长结果后直接赋列） |
| `ValueError: The truth value of a Series is ambiguous...` | 把 Series 用在 `if` / `and` / `or` 里；布尔运算要用 `&`、`|`、`~` 并加括号，聚合用 `.any()` / `.all()` |
| `ValueError: cannot set a DataFrame with multiple columns to the single column y` | 赋值形状不匹配（右侧是一维，左侧选中多列） |

修复示例：
```python
df["x"] = pd.to_numeric(df["x"].str.replace(",", ""), errors="coerce")   # 先清格式再转
mask = (df["a"] > 0) & (df["b"] < 10)      # 括号必加，& 优先级高于比较
if mask.any():                              # 用 any()/all() 坍缩成标量
    ...
```
长度不匹配的定位：`print(len(rhs), len(df))`，再查 `apply` 的返回是否是列表（`result_type="expand"` 或 `pd.Series(...)` 处理）。

## §5 IndexError

| 原文片段 | 常见成因 |
|---|---|
| `IndexError: list index out of range` | 循环上界写错；空列表取 `[0]`（如 `re.findall(...)[0]` 未匹配） |
| `IndexError: single positional indexer is out-of-bounds`（pandas `.iloc`） | `.iloc` 按**位置**索引，与 `.loc` 的**标签**混用 |

定位：`print(len(seq))` 后立即打印索引值；正则类用 `m = re.search(...)` + `if m:` 判空，别直接 `[0]`。
修复：`seq[i] if i < len(seq) else default`；pandas 用 `.loc[label]` 取标签、`.iloc[pos]` 取位置，混用时先 `df.index` 确认。

## §6 ImportError / ModuleNotFoundError

| 原文片段 | 常见成因 |
|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | **包名 ≠ import 名**（`cv2 → opencv-python`、`PIL → Pillow`、`sklearn → scikit-learn`、`yaml → PyYAML`） |
| `ImportError: cannot import name 'X' from 'Y' (unknown location)` | 循环导入；或本地文件与库同名被优先导入 |
| `ImportError: attempted relative import with no known parent package` | 直接 `python3 pkg/mod.py` 运行包内文件；改用 `python3 -m pkg.mod` |

定位：
```bash
python3 -c "import mod; print(mod.__file__)"   # 看实际导入路径
python3 -m pip show -f scikit-learn            # 确认已安装与安装位置
python3 -m pip install package                 # 用当前解释器装，避免装到别的环境
```
注意：`pip` 与 `python3` 必须属于同一环境，`python3 -m pip` 是避免"装了却导不到"的最稳写法。

## §7 pandas / numpy 特有误导性报错

| 现象 | 真相 |
|---|---|
| `SettingWithCopyWarning`（**警告不是错误**） | 链式赋值可能未生效。改 `df.loc[mask, "col"] = v`；切片后先 `.copy()`。pandas 3.0 起默认 Copy-on-Write，该警告不再出现（VERIFY BEFORE USE） |
| `ValueError: cannot reindex on an axis with duplicate labels` | 索引有重复值，`join` / `reindex` 无法确定一一对应 → `df.reset_index(drop=True)` 或先去重 |
| `ValueError: Length mismatch: Expected axis has N elements, new values have M elements` | 赋 `columns=` 或 `index=` 时数量对不上 → 打印两侧长度 |
| `RuntimeWarning: invalid value encountered in divide` | 0/0 或 inf 参与运算，结果是 NaN/inf 而非报错 → 用 `np.errstate` 或先过滤分母 |
| `ValueError: operands could not be broadcast together with shapes (3,) (4,)` | numpy 形状不匹配；打印 `.shape` 逐个对齐 |
| `KeyError` 实为 MultiIndex | 见 §2；用 `df.columns.nlevels` 确认层级数 |
| 明明没错却结果不对 | 多为静默 dtype 变化或静默 NaN 引入，每个变换后 `df.dtypes` + `isna().sum()` 复核 |

## §8 把新模式加进 diagnoser

`diagnoser.py` 顶部 `ERROR_PATTERNS` 是列表，每项含 `pattern`（正则）、`cause`、`fix`、`severity`。新增一条：
```python
{
    "pattern": r"ValueError: cannot reindex",      # 用 re.search，不必匹配整行
    "cause": "索引有重复标签",
    "fix": "reset_index(drop=True) 或先 drop_duplicates",
    "severity": "medium",
}
```
预期：命中后 JSON 输出 `status: "diagnosed"` 且 `top_severity` 取 critical > high > medium > low 的最大值；未命中时 `status: "no_match"`，此时按 §0 人工定位，不要相信"没匹配 = 没问题"。
注意：脚本对整段日志做忽略大小写的 `re.search`，因此"日志里提到过某错误"也会命中——`locations` 字段的 `file:line` 才是判断当前错误位置的主要依据（最多保留 5 条）。
