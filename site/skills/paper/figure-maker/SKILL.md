---
name: figure-maker
description: "Generate paper-ready charts (bar / line / boxplot) from a results JSON via matplotlib, saving PDF/PNG. Use when the user asks 画实验结果图 / 论文图表 / results plot / 把实验数据画成图 / 画柱状图. 当用户要求 生成 bar/line/boxplot 图 时使用。heatmap is NOT implemented yet and returns an honest 'unsupported' status — do not force it. Do NOT use for neural-network structure diagrams (use neural-net-draw)."
license: Apache-2.0
compatibility: Requires matplotlib (pre-installed in this repo's environment); input is a results JSON file.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Figure Maker

Turn an experiments results JSON into publication charts (bar / line / boxplot) as PDF/PNG.

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 数据文件 | 是（默认空数据） | `--data results.json` 读 results JSON；缺省用占位数据 |
| 图类型 | 否 | `--type bar`/`line`/`boxplot`（默认 bar）；`heatmap` 不被支持 |
| 输出路径 | 否 | `--output fig1.pdf`（.pdf/.png）；缺省写 `/tmp/fig_*.pdf` |

缺失时一次性问齐：「请提供：① 数据文件路径 `--data` ② 图类型 `--type`（bar/line/boxplot）③ 输出文件名 `--output`。其余默认：type=bar，输出 /tmp。」

## 前置自检
```bash
python3 --version                          # 预期 >= 3.8，否则报错并 STOP
test -f scripts/figure_maker.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
python3 -c "import matplotlib" && echo MPL_OK   # 预期 MPL_OK；缺失则图无法渲染 STOP
```
若 `matplotlib` 缺失 → 提示 `pip install matplotlib` 后再跑；若脚本缺失 → 提示目录不完整。

## 工作流

### 步骤 1：生成图表
```bash
python3 scripts/figure_maker.py --data results.json --type bar --output fig1.pdf
python3 scripts/figure_maker.py --data results.json --type line --output fig2.png
python3 scripts/figure_maker.py --data results.json --type boxplot --output fig3.pdf
```
预期：输出 JSON 含 `output`（文件路径）与 `rendered: true`；对应图形文件已生成。
若失败：JSON 含 `rendered: false` → matplotlib 未安装，回到前置自检。

### 步骤 2：处理不支持的类型
```bash
python3 scripts/figure_maker.py --data results.json --type heatmap --output fig4.pdf
```
预期：输出 `{"status": "unsupported", "type": "heatmap"}`，**不渲染**、不报错。
若失败：误以为会出图 → 改选 bar/line/boxplot，勿强制 heatmap。

### 步骤 3：取用产物

预期：`--output` 指向的 PDF/PNG 可被 LaTeX `\includegraphics` 引用。
若失败：文件不存在 → 检查 `--output` 路径可写，或省略用 `/tmp` 默认。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--data` | 路径 | results JSON（键见下）；缺省用占位数据 |
| `--type` | bar / line / boxplot / heatmap | 前三者支持，heatmap 返回 unsupported |
| `--output` | 路径 | 输出 .pdf/.png，缺省 `/tmp/fig_*.pdf` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `rendered: false` | matplotlib 未安装 | `pip install matplotlib` 后重跑 |
| `status: unsupported` | 选了 heatmap | 改用 bar/line/boxplot |
| 输出文件未生成 | `--output` 不可写 | 换可写目录或省略该参数 |

## 交付标准

成功定义：JSON `rendered: true` 且 `--output` 图形文件存在、可被 LaTeX 引用。
产物命名：如 `fig1.pdf` / `fig2.png`，由 `--output` 决定。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：用图片查看器/LaTeX 编译确认图形非空白；`status != "unsupported"`。

## 参考

无外部 references 文件；绘图逻辑内置在 `scripts/figure_maker.py`（`make_bar_chart` / `make_line_chart` / `make_boxplot`）。

## 链路位置

上游接 experiment-runner 的 results.json；同族图表任务也可走 pub-plotter（期刊风格更强）。图完成后进 latex-formatter 组装，或用 arch-diagram 补架构图。
