---
name: excel-assistant
description: >
  Clean, analyze, and summarize spreadsheet data: inspect structure, fix
  common defects (encoding, merged cells, dates-as-text), compute answers,
  and deliver a cleaned file plus findings. Use when the user asks to 处理Excel /
  清洗数据 / 表格分析 / 这个表怎么回事 / summarize this spreadsheet /
  fix my csv / 汇总统计. Do NOT use for building presentations or writing reports.
license: Apache-2.0
compatibility: Works best with python3 + pandas + openpyxl; degrades to manual guidance.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: office-productivity
  verified-date: "2026-08-26"
---

# Excel Assistant（检查 → 清洗 → 给答案）

绝不修改用户原始文件。先复制，清洗副本，每处改动都给出前后对比证据，最后附一份书面 findings 说明。

## 输入清单

| 输入 | 必填 | 默认 | 说明 |
|---|---|---|---|
| 文件路径 | 是 | — | xlsx / xls / csv |
| 目标 | 是 | — | 如：汇总各月销售额 / 找出重复客户 / 画趋势 |
| 约束 | 否 | — | 不能动的列、输出格式 |

缺必填项时，只问一次：

> 请提供：① 表格文件路径；② 你想得到什么结果（一句话即可）。
> 可选：哪些列不能动、希望输出 xlsx 还是 csv。

## 前置自检

```bash
python -c "import pandas, openpyxl; print('xl-ok')"
```

- 输出 `xl-ok` → 走下方自动化路径。
- ImportError → 明确告知是哪个导入失败，提议 `pip install pandas openpyxl`；未经同意则进入纯指引模式：给出精确的手工步骤而不是执行代码，并如实说明。

## 工作流

### 步骤 1：先检查，后动手

```python
import pandas as pd
df = pd.read_csv(PATH, encoding="utf-8-sig")   # or read_excel(PATH)
print(df.shape); print(df.dtypes); print(df.head(3))
print(df.isna().sum())
```

预期得到：行列数、字段类型、样例行、空值计数。记下这些数字——它们是"前"证据。CSV 乱码？按顺序重试编码：utf-8-sig → gbk → gb18030。

### 步骤 2：每步只做一处修复

每步最多一种修复，每步之后重新运行检查：
①去重（`df.duplicated()` 先看再删）→ ②补/标缺失（填充规则要写进交付说明）
→ ③日期列转 datetime（`pd.to_datetime(col, errors="coerce")` 后检查 NaT 数）
→ ④数值列剥离单位字符再转类型。

每步的预期结果：空值/重复计数精确按预测变化；若不符，撤销并排查——绝不盲串修复。

### 步骤 3：回答目标

计算所需的聚合/趋势/排序。预期得到：一个能直接回答输入清单里那句话的数字或表格，而不是无关的边角信息。

### 步骤 4：交付

```python
df.to_excel(PATH_stem + "_cleaned.xlsx", index=False)
```

另附一份简短的 `findings.md`：哪里有问题、改了什么、答案是什么、删掉了哪些行（计数）。

## 失败处置表

| 现象 | 可能原因 | 处置 |
|---|---|---|
| csv 报 UnicodeDecodeError | 非 UTF8 编码 | 依次尝试 gbk、gb18030；报告哪个成功 |
| 数字读成 object 类型 | 单元格含单位/空格 | 剥离非数字字符后转类型，统计失败数 |
| 日期大量变 NaT | 日/月顺序有歧义 | 询问用户是哪种惯例；补充 format 字符串 |
| xlsx 含合并单元格 | 表头跨列 | 用 openpyxl 取消合并，向下填充表头行，与用户确认 |
| 合计与用户预期不符 | 有隐藏筛选/工作表 | 说明假设，列出检查过的工作表 |

## 交付标准

成功 = `<name>_cleaned.xlsx`（或 csv）且原始文件未被改动 + `findings.md` 含前后计数对比和直接答案。缺任何一项即未完成——如实说明。

## 参考

无——上方的 pandas 片段就是全部工具。

## 链条衔接（下游建议）

本技能属 office / productivity 类单点技能，可独立使用；清洗后的结构化结果可继续喂给 meeting-notes（汇总）或 resume-tailor（按数据填简历）。建议在 skill_chains.json 中新增 office（或 productivity）域并登记本技能。衔接仅为文字描述。
