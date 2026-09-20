---
name: pub-plotter
description: "Publication-grade plots with REAL journal physical widths (Nature/Science/IEEE/ACM/NeurIPS), Type-42 font embedding (pdf.fonttype=42, arXiv/LaTeX-safe), colorblind-safe palettes by default, and optional real `scienceplots` integration. Outputs PDF/PNG. Use when the user asks 期刊风格图 / IEEE 风格曲线图 / 论文出图 / 出版级图表 / camera-ready 出图 / 按 Nature/Science 版面出图 / publication plot. Do NOT use for architecture diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: Requires matplotlib (Agg backend). Uses real `scienceplots` if installed, else built-in equivalent rcParams (offline). When matplotlib absent → status "mock" (no image, MUST tell user).
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Publication Plotter

由数据 JSON 一键产出出版级图：**真实期刊物理宽度 + Type-42 字体嵌入 + 默认色盲安全色板**，免手调 rcParams；装了 `scienceplots` 包则自动走官方风格。

> 诚实声明（双轨）：装了 matplotlib → `status:"success"`、`rendered:true`，产物为真实 PDF/PNG（含嵌入字体）；没装 → 不报错而是 `status:"mock"`，**无图片产生**，MUST 告知用户未出图，勿把 JSON 报告当交付物。

## 出版级关键点（为什么这样出图）
- **字体嵌入**：`pdf.fonttype=42` / `ps.fonttype=42`（Type 42 子集嵌入），arXiv / LaTeX 不会拒收、放大不糊。
- **按版面出图**：`--journal nature_single|science|ieee|acm|neurips` 用真实物理宽度（Nature 单栏 3.504"≈89mm、Science 4.76"、IEEE 3.5"），「按最终尺寸设计」避免插回版面后字太大/太小。
- **色盲安全**：Paul Tol / Okabe-Ito 色板默认启用（`--no-colorblind` 关闭）——论文配色审稿硬指标。
- **矢量输出**：`.pdf` 矢量（推荐投稿），`.png` 300 dpi 兜底。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 数据 JSON | 建议 | `--data data.json`；**路径不存在时脚本报错退出（不再静默用演示数据）**，务必先确认 |
| 图型 | 否 | `--type line\|bar\|boxplot`（默认 `line`） |
| 风格 | 否 | `--style ieee\|acm\|neurips\|nature\|colorblind_safe`（默认 `ieee`） |
| 期刊版面 | 否 | `--journal nature_single\|science\|ieee\|acm\|neurips`（用真实物理宽度） |
| 色板 | 否 | 默认色盲安全；`--no-colorblind` 关闭 |
| 输出路径 | 否 | `--output fig.pdf`；扩展名决定格式，缺省 `/tmp/fig_pub_<type>.pdf` |

数据 JSON 按图型给键（bar 可选 `errors` 画误差棒/CI）：
```json
{"x":[0,1,2,3],"series":[{"name":"Ours","values":[0.7,0.8,0.85,0.9]}]}
{"labels":["Baseline","Ours"],"values":[0.75,0.85],"errors":[0.02,0.01]}
{"groups":["Baseline","Ours"],"data":[[0.8,0.82,0.78],[0.88,0.91,0.85]]}
```
缺失时一次性问齐：「请提供：① 数据 JSON 路径 `--data`（确认存在）② 图型 `--type` ③ 风格 `--style` 或版面 `--journal` ④ 是否要色盲安全（默认开）⑤ 输出名 `--output`（.pdf 还是 .png）。」

## 前置自检
```bash
python3 -c "import matplotlib; print(matplotlib.__version__)"   # 缺失 → mock 轨，STOP 并告知
python3 -c "import scienceplots" 2>/dev/null && echo SCIENCE_OK  # 可选，装了走官方风格
test -f scripts/pub_plotter.py && echo OK
```

## 工作流

### 步骤 1：出图
```bash
python3 scripts/pub_plotter.py --type line --journal nature_single --data data.json --output fig_nature.pdf
python3 scripts/pub_plotter.py --type bar --style acm --data data.json --output fig.png
python3 scripts/pub_plotter.py --type boxplot --style colorblind_safe --data data.json --output fig.pdf
```
预期：stdout JSON 含 `output`、`style`、`type`、`rendered:true`、`font_embedded:true`、`colorblind_safe`、`width_inches`（line 型）。
若失败：matplotlib 缺失 → `status:"mock"`；`--data` 不存在 → 脚本报 `--data 文件不存在`（退出码 2），先修路径。

### 步骤 2：核对产物
预期：`output` 指向文件存在且非空（`test -s <output>`）；PDF 矢量可读、PNG 300 dpi；`font_embedded:true`。
若失败：图内容与数据对不上 → 核对键名（line→`series`，bar→`labels`+`values`，boxplot→`groups`+`data`）。

### 步骤 3：交接下游
预期：experiment-runner 的 `results.json` 可直接当 `--data`；成品图交 latex-formatter 插入正文（`\includegraphics[width=\columnwidth]{fig.pdf}`）。
若失败：下游缺字段 → 用「输入清单」键名重排数据 JSON。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--type` | `line`/`bar`/`boxplot` | 图型，默认 `line` |
| `--style` | `ieee`/`acm`/`neurips`/`nature`/`colorblind_safe` | 风格预设，默认 `ieee` |
| `--journal` | `nature_single`/`science`/`ieee`/`acm`/`neurips` | 用真实期刊物理宽度 |
| `--no-colorblind` | 标志 | 关闭色盲安全色板（默认开） |
| `--data` | 路径 | 数据 JSON；**不存在即报错退出（不再静默演示）** |
| `--output` | 路径 | .pdf/.png；缺省 `/tmp/fig_pub_<type>.pdf` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `status: "mock"` | matplotlib 未安装 | 仅报告无图；`pip install matplotlib` 后重跑 |
| `--data 文件不存在`（退出码 2） | 路径错 | 先 `test -f` 修路径；勿期望静默演示 |
| `json.JSONDecodeError` | 数据非法 JSON | `python3 -c "import json;json.load(open('<f>'))"` 定位 |
| 字太大/太小 | 没按版面出图 | 加 `--journal <target>` 对齐真实版面宽度 |
| 图放大发糊 / arXiv 拒 | 字体未嵌入 | 本脚本恒 `pdf.fonttype=42`；确认输出 `.pdf` 而非 `.png` |
| 配色审稿被挑 | 用了非色盲安全色 | 保持默认色板；确需自定义再 `--no-colorblind` |

## 交付标准

成功定义：`status:"success"` 且 `rendered:true`、`font_embedded:true`，`output` 图片文件存在非空。
产物命名：`fig.pdf`/`fig.png` 或 `--output`；未指定 `/tmp/fig_pub_<type>.pdf`。
验证方法：`test -s <output>` 通过；`status:"mock"` 时 MUST 只交报告并声明未出图。

## 参考

风格预设 / 真实期刊宽度 / 出图逻辑内置 `scripts/pub_plotter.py`：`JOURNAL_WIDTHS`、`STYLES`、`setup_style`（`pdf.fonttype=42` + 可选 `scienceplots`）、`plot_line`/`plot_bar`/`plot_boxplot`。
SOTA 工具链：`scienceplots`（IEEE/Nature/Science 官方预设）、`pdf.fonttype=42`/`ps.fonttype=42`（字体嵌入）、Paul Tol / Okabe-Ito 色盲安全色板、期刊真实版宽（Nature 单栏 89mm）。

## 链路位置

与 figure-maker 并列的图源（本技能偏期刊风格定稿）；上游接 experiment-runner 的 `results.json`；产物进 latex-formatter 组装，tex-cleaner 收口提交。
