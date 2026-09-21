> 我需要先看到实际文件或至少前10行，才能给出精确清洗方案。请把报销表路径发给我，或粘贴表头+3行数据。下面先给通用框架，确认列名后可直接落地。

## 一、先诊断（运行一次）
```python
import pandas as pd
df = pd.read_excel(PATH, header=None, nrows=5)   # 看原始模样
print(df.T)                                       # 列名行横向显示
```
报销表常见的三种混乱：
- **列名行混用**：同一列在标题行被写成 `'金额'` / `'amount'` / `'￥'`，甚至跨多行。
- **日期格式三种**：`2024-03-01`、`2024/3/1`、`2024.3.1`（有时还夹空格/换行）。
- **金额带单位/千分位**：`￥1,200.00`、`1,200 元`、`1200` 混在同一列。

## 二、列名对齐（最优先）
### 方案A：单行标题，但写法不同 → 建立映射字典
```python
COL_MAP = {
    '金额': 'amount', 'amount': 'amount', '￥': 'amount',
    '日期': 'date', '报销日期': 'date', '日期/Date': 'date',
    '姓名': 'name', '报销人': 'name',
    '部门': 'dept', '项目': 'project', '说明': 'note',
}
# 读入时把第一行当 header，再把列名转小写去空格后替换
df = pd.read_excel(PATH, header=0)
df.columns = df.columns.str.strip().str.lower()
df.columns = df.columns.str.replace('/', '').str.replace('\n', '').str.strip().str.lower()
df = df.rename(columns={k: v for k, v in COL_MAP.items() if k in df.columns})
# 仍未命中的列保留原名列，但记录到 findings
unmapped = [c for c in df.columns if c not in set(COL_MAP.values())]
```

### 方案B：标题跨多行 → 先 flatten
```python
# 假设第0行是主标题，第1行是副标题，合起来就是"金额/amount/￥"这种
df = pd.read_excel(PATH, header=None, nrows=3)
# 把前两行拼成一条列名，再按 / 拆分取第一段作为主名
raw_cols = [str(row0) + '/' + str(row1) for row0, row1 in zip(df.iloc[0], df.iloc[1])]
df = pd.read_excel(PATH, header=[0, 1])  # MultiIndex
df.columns = [c[0].strip() for c in df.columns]
```
**交付前务必打印 `df.columns.tolist()` 确认每列都被正确映射。**

## 三、日期统一（三种 → YYYY-MM-DD）
```python
def fix_date(s):
    # 先剥掉非数字/斜杠/点/横线的噪声，但保留 - / . / :
    s = str(s).strip()
    # 兼容 2024.3.1 / 2024/3/1 / 2024-3-1
    s = s.replace('.', '/').replace(' ', '/')
    return pd.to_datetime(s, dayfirst=False, errors='coerce')

df['date'] = pd.to_datetime(df['date'], errors='coerce')
nat_count = df['date'].isna().sum()
print(f'日期解析失败: {nat_count}')
# 若 nat_count 异常大，说明有另一种格式（如文本 "三月一日"），需单独处理
```
> **注意**：中国报销表通常是「日/月/年」还是「年-月-日」很明确，直接 `dayfirst=False`；若文件含美式日期（如 `03/01` 可能是3月1日或1月3日），请在 findings 里标注并询问。

## 四、金额统一（剥离 ￥/逗号/空格 → float）
```python
import re
def clean_money(s):
    if pd.isna(s): return np.nan
    s = str(s).strip()
    # 去掉 ￥、¥、RMB、元、空格、千分位逗号
    s = re.sub(r'[￥¥\s,]', '', s)
    s = re.sub(r'[Rr][Mm][Bb]|元', '', s)
    s = re.sub(r'[^\d.\-]', '', s)   # 保留数字、点、负号
    try:
        return float(s)
    except ValueError:
        return np.nan

df['amount'] = df['amount'].apply(clean_money)
bad = df['amount'].isna().sum()
print(f'金额清洗失败: {bad}')
```

## 五、去重与缺失标记（不删除，只记录）
```python
dup_before = len(df)
df = df.drop_duplicates(subset=['date', 'name', 'amount', 'project'], keep='first')
print(f'重复行: {len(df) - dup_before}')

# 缺失比例 > 20% 的列在 findings 里高亮
na_pct = df.isna().mean().sort_values(ascending=False)
```

## 六、交付清单（必须附 findings.md）
| 项目 | 内容 |
|---|---|
| 文件 | `<name>_cleaned.xlsx`（原始文件不动） |
| 列名 | 列出映射表 `原始 → amount/date/...` |
| 日期 | 三种格式 → `YYYY-MM-DD`，失败条数 |
| 金额 | 剥离 `￥/逗号/元` 后 float，失败条数 |
| 重复行 | 删除条数及判定字段 |
| 空值 | 每列缺失数/比例 |
| 样例 | head(3) + tail(3) 截图式表格 |

## 七、请你提供以下任一一项，我直接给落地版
1. **文件路径**（xlsx/xls/csv）→ 我跑上面流程，输出 `_cleaned.xlsx` + `findings.md`。
2. 若不便发文件，粘贴 **前10行原始文本**（含表头），我根据实际列名给出精确代码，不再通用。