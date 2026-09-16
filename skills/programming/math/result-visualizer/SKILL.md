---
name: result-visualizer
description: "将模型结果绘制成图：折线、散点、直方图、热力图、柱状图，输出 PNG/SVG 供报告与展示。何时使用：模型已求解或仿真已完成、需要可视化呈现时。触发场景（中/英）：画结果图 / 数据可视化 / 出图表 / plot results / visualize data / make a chart。排除项：不做超出给定结果的统计推断。"
license: Apache-2.0
compatibility: Requires matplotlib. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: programming/math
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# Result Visualizer

把数值结果转成可发布的图。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| data | 是 | 结果 JSON 文件路径（含待绘图序列） |
| type | 否 | `line` / `scatter` / `histogram` | line |
| x | 否 | 散点图的 x 字段名 | t |
| y | 否 | 散点图的 y 字段名 | y |
| output | 否 | 输出图片路径 | 标准输出路径 |

缺失时一次性问齐：「请提供：① data（结果 JSON 路径）。type/x/y/output 我按默认处理。」

## 前置自检

```bash
python3 --version
python3 -c "import matplotlib; print('matplotlib', matplotlib.__version__)"
test -f scripts/visualizer.py && echo "OK script present"
```

- 预期：版本号输出；`matplotlib <版本>` 打印；脚本存在。
- 若失败：缺 matplotlib → `pip install matplotlib`；脚本缺失 → STOP 回报。

## 工作流

### 步骤 1：选择图类型

| Type | Use Case | Input |
|------|----------|-------|
| line | 时间序列、收敛曲线 | t[], y[] |
| scatter | 相关性、分布 | x[], y[] |
| histogram | 分布、MC 结果 | samples[] |
| heatmap | 2D 参数空间 | matrix[][] |
| bar | 类别对比 | labels[], values[] |
| subplot | 多面板报告 | 多个序列 |

- 动作：按数据形态选 `type`，散点需同时给 `--x` `--y`。
- 预期：选定单一 `type` 与对应字段。
- 若失败：数据非数值/字段缺失 → 退回 data 校验。

### 步骤 2：运行绘图脚本

```bash
python3 scripts/visualizer.py --data results.json --type line --output fig1.png
python3 scripts/visualizer.py --data results.json --type scatter --x t --y y
```

- 预期：生成图片文件（给 `--output` 时），或标准输出 `{"output": "...", "type": "...", "rendered": true}`。
- 若失败：`FileNotFoundError` → data 路径错；`KeyError` → x/y 字段不在 JSON；缺后端 → 设 `MPLBACKEND=Agg`。

### 步骤 3：套用出版级样式

- 动作：按下方样式约定检查输出图。
- 预期：DPI、字号、配色、网格符合规范。
- 若失败：样式不符 → 调整脚本参数或参考 cheatsheet 重绘。

| 样式项 | 取值 |
|--------|------|
| 分辨率 | 打印 150 DPI / 网页 72 DPI |
| 字号 | ≥ 12 |
| 配色 | 色盲安全（默认 tab10） |
| 网格 | alpha=0.3 |
| 布局 | tight_layout，无标签重叠 |

## 输出格式

```json
{
  "output": "/tmp/fig1.png",
  "type": "line",
  "rendered": true
}
```

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| --data | 文件路径 | 必需，结果 JSON |
| --type | line/scatter/histogram | 默认 line |
| --x | 字段名 | 默认 t |
| --y | 字段名 | 默认 y |
| --output | 图片路径 | 可选，输出文件 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `FileNotFoundError` | data 路径错误 | 核对路径或退回输入清单 |
| `KeyError: 'x'` | 散点字段缺失 | 显式指定 `--x`/`--y` |
| `no display / backend` | 无 GUI 环境 | 设 `MPLBACKEND=Agg` 后重跑 |

## 交付标准

- 成功定义：产出 PNG/SVG 且 JSON 报告 `rendered: true`。
- 产物命名：`fig1.png`（或 `--output` 指定，建议带序号与类型）。
- 保存位置：`/tmp/` 或用户指定目录。
- 验证完整性：用图片查看器/读取文件头确认非 0 字节；核对样式表四项正确。

## 参考

- references/matplotlib-cheatsheet.md — 选图类型、配色与样式速查时读
