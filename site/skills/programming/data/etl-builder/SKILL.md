---
name: etl-builder
description: "Build data pipelines: extract from CSV/JSON/DB, apply transforms (clean, normalize, encode), load to target. Supports batch and incremental modes. Use when raw data needs cleaning before analysis or ML training. 当用户要求 写数据管道 / ETL 清洗 / 数据入库 时使用。 Do NOT use for running production ETL schedules (generation and local dry-run only)."
license: Apache-2.0
compatibility: Pure Python standard library (argparse/json/csv). No pandas or external DB required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/data
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# ETL Builder

构建 Extract → Transform → Load 数据管道：脚本执行抽取、变换与落库的本地 dry-run，产出结构化 JSON 报告。只做生成与本地演练，不调度生产 ETL。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `--source` | 必需 | 输入数据路径；支持 `.csv`（按行统计）与 `.json`（须为 list）；其他后缀按"非标准格式"处理。缺省 data/raw.csv |
| `--target` | 可选 | 输出路径，缺省 data/clean.csv。注意：脚本写入的是 JSON 状态摘要，不是数据本体 |
| `--transform` | 可选 | 逗号分隔的变换链，如 `dropna,fillna_median,normalize`；缺省 `dropna` |
| `--output` | 可选 | 报告落盘路径；缺省打印到 stdout |

缺失输入时一次性问齐：「请提供：①输入数据路径与格式（CSV/JSON）②输出目标路径 ③需要的变换链（默认 dropna）。其余我采用默认值：报告打印到终端。」

## 前置自检

运行前探测环境，任一失败→给出修复并 STOP：

```bash
python3 --version   # 预期 3.8+；失败：安装 python3
python3 scripts/etl_builder.py --help >/dev/null 2>&1   # 预期退出码 0；失败：脚本缺失 → 核对技能目录
test -f <用户给的 --source 路径>   # 预期退出码 0；失败：文件不存在 → 向用户要正确路径
```

## 工作流

### 步骤 1：确认源数据格式

```bash
test -f data/raw.csv && head -2 data/raw.csv
```

预期：文件存在且首行是表头。若失败：`.json` 输入须为 list（`python3 -c "import json;print(type(json.load(open('data/raw.json'))))"应为 list`）；其他后缀会得到 `Non-standard format, read raw` 提示 → 先转成 CSV 再继续。

### 步骤 2：运行管道

```bash
python3 scripts/etl_builder.py --source data/raw.csv --target data/clean.csv \
  --transform "dropna,fillna_median,normalize"
```

预期：stdout 输出 JSON，`status` 为 `complete`，含 `extract.rows`、`transform.transforms_applied`、`load.status=loaded` 三段。data/clean.csv 写入的是 `{"status": "loaded", ...}` 状态摘要（骨架实现，不含数据本体）。
若失败：见下方失败处置表。

### 步骤 3：核验变换链被正确识别

预期：`transforms_applied` 中每个名称对应一条描述（如 `dropna` → `Removed null values`）。脚本按关键词识别：`dropna`、`fillna*`、`normalize`、`*scale*`、`encode*`；不在集合内的名称会原样记为 `Applied: <name>` → 核对名称拼写或改用支持的变换。

### 步骤 4：交接下游

清洗结果就绪后，向用户报告 rows_in/rows_out 与已应用变换，再按需求交接 feature-engineer 做特征工程。

## 变换速查表

| 变换 | 脚本识别 | 说明 |
|------|----------|------|
| `dropna` | 是（关键词） | 去除含缺失值行 |
| `fillna_median` / `fillna_mean` | 是（`fillna` 前缀） | 中位数/均值填充 |
| `normalize` | 是（关键词） | Min-max 缩放到 [0,1] |
| `standardize` | 否（记为 Applied） | Z-score；脚本侧用 `scale` 关键词 |
| `encode_onehot` / `encode_target` | 是（`encode` 前缀） | 类别编码 |
| `clip_outliers` / `parse_dates` / `rename_cols` | 否（记为 Applied） | 需在下游代码实现，脚本仅记录 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `status: error`，`Source not found: <path>` | `--source` 路径不存在 | 核对路径后重跑；仍失败则向用户要正确路径 |
| `Non-standard format, read raw` | 输入非 `.csv`/`.json` 后缀 | 先转换为 CSV 再运行 |
| `.json` 输入解析异常 | JSON 顶层不是 list | 改存为 list 或转 CSV |
| `transforms_applied` 出现 `Applied: <name>` | 变换名不被关键词识别 | 按上表改用支持前缀的名称 |
| 报告未落盘 | 未传 `--output` | 属预期行为（打印 stdout）；需落盘时加 `--output report.json` |

## 交付标准

成功定义：输出 JSON `status=complete`，extract/transform/load 三段齐全，变换链与用户要求一致。
产物命名：状态摘要 `<target>`（缺省为 data 目录下的 clean.csv）；报告 `--output` 指定名（建议 `etl_report.json`）。
保存位置：与用户数据同目录层级；报告放工作目录根。
验证完整性：重跑同命令输出应一致（纯函数式 dry-run）；`extract.rows` 与源文件行数（减表头）吻合。

## 安全红线

- 本技能只做本地 dry-run，不触碰生产调度系统、不连接外部数据库。
- `--target` 会覆盖同名文件；目标路径已存在时先向用户确认。
- 输出目录不存在时脚本自动创建（`parents=True`），确认写入位置符合用户预期。

## 参考

- [references/transform-recipes.md](references/transform-recipes.md) —— 需要组合变换、处理特定数据形态的常用配方时读

清洗落库后，**接着说："干净数据就绪，继续调用 feature-engineer 做特征工程"——链条自动展开**。
