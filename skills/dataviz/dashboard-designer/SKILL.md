---
name: dashboard-designer
description: >
  Profile a CSV, then recommend and generate a dashboard: infer column types
  and distributions, propose a KPI-plus-chart layout with reasons, and build a
  self-contained single-file HTML dashboard whose charts are inline SVG with no
  CDN or network dependency. Use when the user asks to 做个仪表盘 / 数据看板 /
  把这个 CSV 可视化 / 分析数据出图表 / 生成 HTML 报表 / build a dashboard /
  visualize this CSV / make a data report / create an HTML dashboard. Do NOT use
  for choosing a single chart type without building anything (use
  chart-recommender), for academic publication figures (use pub-plotter), or for
  statistical modeling.
license: Apache-2.0
compatibility: 需要 python3 3.8+；脚本纯标准库。产出 HTML 零外部依赖，离线可看。
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: dataviz
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Dashboard Designer（仪表盘设计）

拿到一份 CSV，走完「**体检 → 设计 → 生成**」三段：先摸清每列的类型、缺失与分布，
再据此推荐该放几个指标卡、画什么图、为什么这么选，最后产出一个
**自包含单文件 HTML**——图表是服务端算好坐标写死的内联 SVG，
断网、内网、离线交付都能正常打开。

核心判断：**先体检再画图**。跳过 `inspect` 直接 `build`，等于拿不知道类型、
不知道缺失率的列去选图型，这是仪表盘最常见的失败起点。

本技能**不**替你决定单个图型（那用 `chart-recommender` 查词库），
**不**做统计建模，**不**出论文级配图（那用 `pub-plotter`）。

## 输入清单

| 输入 | 必需 | 默认 | 说明 |
|---|---|---|---|
| CSV 文件 | 是 | — | 自动嗅探分隔符（`,` `;` `\t` `\|`）与编码 |
| 仪表盘标题 | 否 | `<文件名> 数据仪表盘` | 显示在页面 H1 |
| 输出路径 | 否 | `dashboard.html` | 单文件，可直接双击打开 |
| 受众与场景 | 否 | 通用 | 决定指标卡数量与首屏信息密度 |
| 配色偏好 | 否 | 内置定性色板 | 已有品牌色时说明 |

缺输入时，一次性问齐：

> 请提供：① CSV 在哪？② 这份看板给谁看、回答什么问题（越具体越好）？
> ③ 输出文件名（默认 dashboard.html）？④ 有必须出现的指标吗？

## 前置自检

逐条执行，任一失败 → 按处置动作做：

```bash
# 1. Python 版本
python3 --version
# 预期：Python 3.8+（用到 statistics.fmean 与 walrus 之外的现代语法）。失败→STOP。

# 2. 脚本可用
# python3 scripts/dashboard.py --help >/dev/null && echo "script ok"
# 预期：script ok。失败→核对 scripts/ 路径。

# 3. CSV 可读且非空
head -3 <data.csv> && wc -l <data.csv>
# 预期：能看到表头与数据行；0 行 → 脚本报「是空文件」，先找用户要数据。

# 4. 输出目录可写
ls -d "$(dirname <out.html>)" >/dev/null && echo "outdir ok"
# 预期：outdir ok。失败→创建目录或换路径，不要写到只读位置。
```

## 工作流

### 步骤 1：体检 CSV

```bash
python3 scripts/dashboard.py inspect assets/sample.csv   # 随包样例 CSV；你的真实数据换成 data.csv
```

输出每列的**类型推断**（numeric / date / categorical / text）、缺失率、唯一值数，
数值列附带 min / max / mean / median / q1 / q3，日期列附带取值范围，
分类列附带 top 3 频次。

- **预期**：逐列打印一行画像，形如
  `营收  numeric  5.7%  1019  min=-747.13 max=9.3万 mean=4.9万 …`。
- **若失败**：报「无法解码」→ 让用户另存为 UTF-8；
  列全是 `text` → 数据可能不是逗号分隔，确认分隔符。

### 步骤 2：读推荐方案

```bash
python3 scripts/dashboard.py recommend assets/sample.csv
```

输出 Markdown 设计方案：**指标卡表** + **图表方案表**（含优先级与理由）+
**ASCII 布局图** + **数据注意事项**。

推荐规则是可解释的，不要当黑箱：

| 列特征 | 推荐 | 为什么 |
|---|---|---|
| 日期列 + 数值列 | 折线图（主图） | 趋势是时间序列的第一表达 |
| 分类列 + 数值列 | 条形图（副图） | 比大小；标签长或类别多时转水平条 |
| 两个以上数值列 | 散点图（可选） | 相关性保留原始分布，胜过任何聚合 |
| 只有分类列 | 条形图（计数） | 频次是唯一有信息量的聚合 |
| 无可用列 | 明细表 | 如实说明无法出图，不要硬凑 |

**数据注意事项**是这一节的产出重点，会主动点出三类陷阱：
缺失率 ≥1%（说明聚合已排除空缺行，必须标注）、
分类值 >20 个（只画 top 12，其余归入「其他」）、
最大值超过中位数 20 倍（右偏，直接画会被离群点压扁，建议对数轴或截断并标注）。

- **预期**：表格化输出，每行都有「为什么这么选」。
- **若失败**：推荐里有不认同的项 → 保留脚本结论但在交付时说明你的调整与理由，
  不要静默改掉用户看到的东西。

### 步骤 3：生成 HTML

```bash
python3 scripts/dashboard.py build assets/sample.csv --out dashboard.html --title "季度销售看板"   # 随包样例
```

产出单文件 HTML：KPI 卡片 + 网格布局图表 + 前 200 行明细表 + 数据提示区。

- **预期**：输出 `bytes` / `rows` / `kpis` / `charts`，且
  **`external: 0 个外部引用`**——这一行是自包含性的断言，不是装饰。
- **若失败**：若 `external` 不为 0，说明引入了外部资源，
  与本技能承诺的离线可用相违，必须回退。

### 步骤 4：渲染验证（不要只看退出码）

```bash
# 有浏览器环境时，截图或至少检查无控制台错误
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--no-sandbox'])
    pg = b.new_page(viewport={'width':1200,'height':1400})
    pg.goto('file://$PWD/dashboard.html')
    print('svg:', pg.evaluate('()=>document.querySelectorAll(\"svg\").length'))
    pg.screenshot(path='preview.png', full_page=False)
    b.close()
"
```

- **预期**：`svg` 数等于 `build` 报的 `charts` 数；截图里图题不与刻度重叠、
  轴标签不是 `8e+06` 这类科学计数法。
- **若失败**：没有浏览器 → 退化为检查 HTML 里 `<svg` 出现次数与
  `external: 0`；仍然要报告这两项，不能只报「生成成功」。

### 步骤 5：交付

说明四件事：文件**绝对路径**、数据规模与列类型分布、
`build` 报告的 `external: 0`（离线可用）、以及**数据注意事项**里的每一条。
提醒用户：改数据要重新 `build`，HTML 本身不含数据源，是纯快照。

- **预期**：交付说明覆盖上述四件事，且 `external: 0` 与数据注意事项已逐条转述。
- **若失败**：拿不到绝对路径（用户环境与生成环境不同）→ 用 `python3 -c
  "import os;print(os.path.abspath('<out>'))"` 打印后给出；`external` 不为 0 →
  不得交付，回步骤 3 排查外部引用来源（本技能承诺零外部依赖）。

## 交付标准

- 产物：一个可双击打开的自包含 `dashboard.html`。
- 位置：用户指定的 `--out` 路径；默认当前目录 `dashboard.html`。
- 完整性验证（至少做前两条）：
  - `build` 输出 `external: 0`；
  - HTML 中 `<svg` 出现次数等于 `charts` 数；
  - 有浏览器时截图确认标题不与刻度重叠、数值格式可读。
- 交付说明必须转述「数据注意事项」全文；有缺失或右偏却没说，视为未完成。

## 失败处置表

| 现象 / 错误 | 原因 | 处置 |
|---|---|---|
| `CSV 不存在：...` | 路径拼错或文件未上传 | 核对路径；不要拿 `.xlsx` 直接当 CSV |
| `无法解码 ...，请另存为 UTF-8` | 非 UTF-8/GBK 编码（如 UTF-16） | 让用户另存为 UTF-8；本脚本已尝试 utf-8-sig/utf-8/gbk/latin-1 |
| `... 是空文件` | 文件零字节或只有换行 | 找用户确认数据源 |
| 所有列都被判为 `text` | 分隔符不是逗号且嗅探失败 | 转成标准 CSV（逗号分隔）；单列数据本就不该出仪表盘 |
| 数值列被误判为 text | 列里混了单位（`1,200元`）或千分位异常 | 清洗掉单位后重跑；`to_float` 只处理千分位与百分号 |
| 图表区一片空白 | SVG 高度被设为 0，或数据全被过滤 | 跑 `inspect` 确认该列有有效值；空值列会渲染成「无有效数据」占位 |
| 轴标签出现 `8e+06` | 使用了科学计数法格式化 | 应使用 `fmt_num` 的「万/亿」缩写；若复现说明改坏了格式化 |
| 图题与刻度重叠 | 标题与 y 轴最高刻度同高 | 图题须独占顶部色带（`PAD_T` 留净空）；这是已知易犯点 |
| 条形图各柱高度几乎相同 | 类别间数值差异 <25%，高度差不传递信息 | 脚本会加注「请以数值为准」；必要时改用表格或加差值列 |
| 页面在用户机器上打不开图 | 曾引用 CDN，离线环境加载失败 | 本技能禁止外部依赖；确认 `external: 0`，内联 SVG 不受网络影响 |

## 参考

- `references/sources-and-methodology.md` —— 类型推断阈值、格式化与自包含
  设计的取舍，以及图形语法与色板的公开来源。
- `scripts/dashboard.py --help` —— inspect / recommend / build 三个子命令。
- 相关技能：`chart-recommender`（图型选择的深度词库）、
  `pub-plotter`（论文级配图）、`excel-assistant`（表格清洗）。
