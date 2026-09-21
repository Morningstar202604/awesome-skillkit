# 报销表清洗方案

## 一、列名混乱：三套写法 → 统一标准

### 识别当前列名
```python
print(df.columns.tolist())
```
预期看到类似：
```
['日期', '日期1', '日期2',
 '金额/amount', '金额/￥', '支出',
 '姓名', '报销人', ...]
```

### 列名映射规则
```python
col_map = {
    '金额/amount': '金额',
    '金额/￥':     '金额',
    '日期1':       '日期',
    '支出':        '金额',          # 若"支出"也是金额列
    '报销人':      '姓名',
}
df.rename(columns=col_map, inplace=True)
# 去重：同名保留第一列，其余记入 findings
```
> **注意**：若出现两个"金额"列，必须告知用户保留哪一列，不可静默丢弃。

---

## 二、日期格式三种 → 统一为 `YYYY-MM-DD`

假设三种格式是：`2024.3.5` / `2024/03/05` / `20240305`（或中文`2024年3月5日`）

```python
import pandas as pd

# errors='coerce'：无法解析的变成 NaT，先看清再决定
df['日期'] = pd.to_datetime(df['日期'], errors='coerce')

# 统计失败数，报告给用户
failed = df['日期'].isna().sum()
print(f"日期解析失败：{failed} 行，请检查以下样例：")
print(df[df['日期'].isna()]['日期'].dropna().unique()[:10])

# 统一输出格式
df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
```

---

## 三、金额列混乱：单位/空格/文本干扰

```python
def clean_money(s):
    if pd.isna(s):
        return None
    # 去掉 ￥、空格、千分位逗号
    s = str(s).replace('￥','').replace(',','').replace(' ','')
    try:
        return float(s)
    except ValueError:
        return None   # 记入 findings 等待人工复核

df['金额'] = df['金额'].apply(clean_money)
failed_money = df['金额'].isna().sum()
print(f"金额解析失败：{failed_money} 行")
```

---

## 四、完整清洗 pipeline（可直接跑）

```python
import pandas as pd
from pathlib import Path

path = Path('报销表.xlsx')
df = pd.read_excel(path)

# 1. 记录清洗前
before = {
    'rows': len(df),
    'cols': list(df.columns),
    'nulls': df.isna().sum().to_dict(),
}

# 2. 列名标准化
col_map = {'金额/amount':'金额', '金额/￥':'金额', '日期1':'日期', '报销人':'姓名'}
df.rename(columns={k:v for k,v in col_map.items() if k in df.columns}, inplace=True)

# 3. 日期解析
df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
date_nat = df['日期'].isna().sum()

# 4. 金额清洗
def clean_money(s):
    if pd.isna(s): return None
    s = str(s).replace('￥','').replace(',','').replace(' ','')
    try: return float(s)
    except ValueError: return None
df['金额'] = df['金额'].apply(clean_money)
money_nat = df['金额'].isna().sum()

# 5. 去重（按姓名+日期+金额）
dup_before = df.duplicated(subset=['姓名','日期','金额']).sum()
df.drop_duplicates(subset=['姓名','日期','金额'], inplace=True)

# 6. 保存
out = path.parent / (path.stem + '_cleaned.xlsx')
df.to_excel(out, index=False)

# 7. 生成 findings
print(f"""
=== 清洗报告 ===
原始行数：{before['rows']} → 清洗后：{len(df)}（删除重复 {dup_before} 行）
日期解析失败：{date_nat} 行
金额解析失败：{money_nat} 行
输出文件：{out}
""")
```

---

## 五、交付清单

| 项目 | 说明 |
|---|---|
| `_cleaned.xlsx` | 标准列名（日期/姓名/金额），日期YYYY-MM-DD，金额纯数字 |
| `findings.md` | 记录：①原列名分布 ②各格式日期失败数 ③金额失败样例 ④删除重复行数 |
| **原始文件** | **绝不修改** |

> **关键原则**：每步只做一处修复，每步后重新打印计数确认——若数字不符预期，立即停止排查，不要继续往下洗。