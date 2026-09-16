---
name: pub-plotter
description: "Publication-grade plots in SciencePlots style (IEEE / ACM / NeurIPS / colorblind-safe, single/double column) from a data JSON, output PDF/PNG. 学习自 garrettj403/SciencePlots (9.2k stars). Use when the user asks 期刊风格图 / IEEE 风格曲线图 / 论文绑图 / 出版级图表 / camera-ready 出图 / 论文绘图 / publication plot. Do NOT use for architecture diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: Requires matplotlib; data input is a JSON file; stdlib fallback reports status "mock" when matplotlib is absent.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Publication Plotter

由数据 JSON 一键产出期刊风格图（IEEE/ACM/NeurIPS/色盲安全四套预设），免手调 rcParams。

> 诚实声明：**双轨语义**——装了 matplotlib 时 `status: "success"`、`rendered: true`，产物为真实图片文件；没装时脚本不报错而是返回 `status: "mock"`，**没有图片产生**，此时 MUST 告知用户未出图，勿把 JSON 报告当交付物。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 数据 JSON | 建议 | `--data data.json`；**文件不存在时脚本不报错，静默改用内置演示数据**，务必先确认路径 |
| 图型 | 否 | `--type line\|bar\|boxplot`（默认 `line`） |
| 风格 | 否 | `--style ieee\|acm\|neurips\|colorblind_safe`（默认 `ieee`） |
| 输出路径 | 否 | `--output fig.pdf`；扩展名决定格式（.pdf/.png），缺省写到 `/tmp/fig_pub_<type>.pdf` |

数据 JSON 按图型给键（缺键同样静默用演示数据）：
```json
{"x": [0, 1, 2, 3], "series": [{"name": "Ours", "values": [0.7, 0.8, 0.85, 0.9]}]}
{"labels": ["Baseline", "Ours"], "values": [0.75, 0.85]}
{"groups": ["Baseline", "Ours"], "data": [[0.8, 0.82, 0.78], [0.88, 0.91, 0.85]]}
```

缺失时一次性问齐：「请提供：① 数据 JSON 路径 `--data`（并确认文件存在）② 图型 `--type` ③ 目标风格 `--style` ④ 输出名 `--output`（.pdf 还是 .png）。」

## 前置自检
```bash
python3 -c "import matplotlib; print(matplotlib.__version__)"   # 预期打印版本号；ImportError → 走 mock 轨，STOP 并告知用户
test -f "$DATA_JSON" && echo DATA_OK                            # 预期打印 DATA_OK；否则脚本会静默用演示数据
test -f scripts/pub_plotter.py && echo OK                       # 预期打印 OK，否则脚本缺失 STOP
```
matplotlib 缺失时修复：`pip install matplotlib`；装不上则明确按 mock 轨处理（无图片交付）。

## 工作流

### 步骤 1：出图
```bash
python3 scripts/pub_plotter.py --type line --style ieee --data data.json --output fig.pdf
python3 scripts/pub_plotter.py --type bar --style acm --data data.json --output fig.png
python3 scripts/pub_plotter.py --type boxplot --style colorblind_safe --data data.json --output fig.pdf
```
预期：stdout JSON 含 `output`（图片实际路径）、`style`、`type`、`rendered: true`、`status: "success"`（line 型另含 `width_inches`）。
若失败：`ImportError` → 脚本返回 `status: "mock"`，装 matplotlib 后重试；JSON 非法 → `json.JSONDecodeError`，校验数据文件。

### 步骤 2：核对产物

预期：`output` 指向的文件存在且非空：`test -s "$(python3 -c "...")"` 或直接 `ls -la <output>`；PDF 可用阅读器打开、PNG 为 300 dpi。
若失败：文件不存在但 `status: "success"` → 检查 `--output` 目录是否可写；图内容与数据对不上 → 回查数据 JSON 键名是否匹配所用图型。

### 步骤 3：交接下游

预期：experiment-runner 的 `results.json` 可直接作 `--data` 输入；成品图交 latex-formatter 插入正文。
若失败：下游报缺字段 → 用本文件「输入清单」里的键名重排数据 JSON。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--type` | `line` / `bar` / `boxplot` | 图型，默认 `line` |
| `--style` | `ieee` / `acm` / `neurips` / `colorblind_safe` | 风格预设，默认 `ieee` |
| `--data` | 路径 | 数据 JSON；**不存在时静默用演示数据** |
| `--output` | 路径 | .pdf/.png；缺省 `/tmp/fig_pub_<type>.pdf` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `status: "mock"` | matplotlib 未安装 | 结果仅为报告、无图片；`pip install matplotlib` 后重跑 |
| 图是演示数据的样子 | `--data` 路径错或 JSON 键名不匹配 | 先 `test -f`，再核对键名（line→`series`，bar→`labels`+`values`，boxplot→`groups`+`data`） |
| `json.JSONDecodeError` | 数据文件非法 JSON | `python3 -c "import json;json.load(open('<f>'))"` 定位 |
| 字号/线宽不像目标 venue | 风格预设选错或被手改 | 用 `--style` 四选一，勿叠加自定义 rcParams |

## 交付标准

成功定义：`status: "success"` 且 `rendered: true`，`output` 指向的图片文件存在非空。
产物命名：`fig.pdf` / `fig.png` 或 `--output` 指定名；未指定时为 `/tmp/fig_pub_<type>.pdf`。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`test -s <output>` 通过；`status: "mock"` 时 MUST 只交报告并声明未出图，不得伪造图片路径。

## 参考

无外部 references 文件；四套风格预设与三种绘图函数内置在 `scripts/pub_plotter.py` 的 `STYLES` / `plot_line` / `plot_bar` / `plot_boxplot`。

## 链路位置

与 figure-maker 并列的图源（本技能偏期刊风格定稿）；上游接 experiment-runner 的 results.json；产物统一进 latex-formatter 组装，tex-cleaner 收口提交。
