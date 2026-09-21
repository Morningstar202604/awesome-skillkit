# 报销表清洗方案

## 一、列名混乱处理

### 1. 统一列名

| 原列名 | 目标列名 | 操作 |
|---|---|---|
| `金额` / `amount` / `￥` | `amount` | 映射替换 |
| `日期` / `报销日期` / `date` | `date` | 映射替换 |
| 其他 | 保留原样 | 不做改动 |

**Python 实现：**
```python
col_map = {
    '金额': 'amount', 'amount': 'amount', '￥': 'amount',
    '日期': 'date', '报销日期': 'date', 'date': 'date'
}
df.columns = [col_map.get(c, c) for c in df.columns]
```

---

## 二、三种日期格式统一

先识别现有格式：

```python
print(df['date'].head(10))
# 可能输出：
# 0    2024-03-15
# 1    15/03/2024
# 2    2024.03.15
```

**统一转换为 `YYYY-MM-DD`：**
```python
import pandas as pd

# 强制解析，无法解析的标记为 NaT
df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')

# 格式化输出
df['date'] = df['date'].dt.strftime('%Y-%m-%d')

# 统计失败数（用于 findings）
nat_count = df['date'].isna().sum()
```

> 若仍有大量 `NaT`，说明有脏数据（如"待报销"、空白），需单独筛选处理。

---

## 三、金额列清理

常见缺陷：含 `￥`、逗号、空格

```python
# 剥离非数字字符（保留小数点和负号）
df['amount'] = df['amount'].astype(str).str.replace(r'[￥,\s]', '', regex=True)

# 转为数值，失败则记为 NaN
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# 统计失败数
fail_count = df['amount'].isna().sum()
```

---

## 四、完整清洗流程（一键执行）

```python
import pandas as pd

def clean_reimbursement(path):
    # 读取
    df = pd.read_excel(path)  # 或 pd.read_csv(path, encoding='utf-8-sig')
    
    # 1. 列名映射
    col_map = {
        '金额': 'amount', 'amount': 'amount', '￥': 'amount',
        '日期': 'date', '报销日期': 'date', 'date': 'date'
    }
    df.columns = [col_map.get(c, c) for c in df.columns]
    
    # 2. 日期统一
    df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
    nat_dates = df['date'].isna().sum()
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # 3. 金额清理
    df['amount'] = df['amount'].astype(str).str.replace(r'[￥,\s]', '', regex=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    fail_amounts = df['amount'].isna().sum()
    
    # 4. 去重
    before = len(df)
    df = df.drop_duplicates()
    dupes = before - len(df)
    
    return df, {'nat_dates': nat_dates, 'fail_amounts': fail_amounts, 'duplicates': dupes}

# 使用
df_clean, stats = clean_reimbursement('报销表.xlsx')
df_clean.to_excel('报销表_cleaned.xlsx', index=False)
print(f"清洗完成: 缺失日期{stats['nat_dates']}条, 无效金额{stats['fail_amounts']}条, 去重{stats['duplicates']}条")
```

---

## 五、Findings 模板

```markdown
## 报销表清洗报告

### 输入文件
- 路径：报销表.xlsx
- 原始行数：XXX

### 问题统计
| 问题类型 | 数量 |
|---|---|
| 日期格式不一致 | 3种（YYYY-MM-DD、DD/MM/YYYY、YYYY.MM.DD） |
| 列名不统一 | 2种（金额/￥、日期/报销日期） |
| 金额含符号 | XXX条（￥、逗号等） |
| 无法解析日期 | X条 |
| 无效金额 | X条 |
| 重复记录 | X条 |

### 输出文件
- 路径：报销表_cleaned.xlsx
- 格式：所有日期转为 YYYY-MM-DD，金额转为纯数值

### 删除/标记的行
- 日期无法解析：XXX（建议人工核查）
- 金额无法解析：XXX（建议人工核查）
```

---

需要我直接帮你处理某个具体文件吗？