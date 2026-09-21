---
name: arch-diagram
description: "Generate paper-style architecture/framework diagrams as compile-ready TikZ (LaTeX) plus well-formed editable SVG: pipelines with row/wrap/stack layouts, per-block colourblind-safe colours, automatic LaTeX/XML escaping. Use when the user asks 画架构图 / 方法总览图 / framework diagram / 画流程图 / pipeline 图. 当用户要求 生成方法章节配图 / 模块框图 时使用。Do NOT use for data charts (use pub-plotter / figure-maker) or neuron-level networks (use neural-net-draw)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; outputs TikZ source and SVG, no LaTeX compile required.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Arch Diagram (SOTA)

生成方法总览图（TikZ + 合法 SVG），用于 "Model Architecture" 配图。

> **v1 的三个硬伤已修**：① TikZ 里写的 `\sffootnotesize` **不是合法 LaTeX 命令**（编译必报 Undefined control sequence）→ 改为 `\footnotesize`；② SVG 引用了 `url(#arrow)` 却**从未定义 marker**（箭头不渲染）→ 现在输出 `<defs><marker id="arrow">`；③ 所有块挤在一条直线 → 新增 `row` / `wrap` / `stack` 布局。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 图类型 | 是 | `--type pipeline`（模块流程）/`nn`（层叠示意）/`svg`（纯 SVG） |
| 区块或层 | 条件 | pipeline 用 `--blocks "Encoder,Decoder,Head"`，可写 `Label#color`（`blue/orange/green/red/purple/gray/yellow/cyan`）；nn 用 `--layers` |
| 布局 | 否 | `--layout row`（默认）/`wrap`/`stack`；`wrap` 配合 `--per-row 3` |
| 输出格式 | 否 | `--format tikz`（默认）/`svg` |
| 输出路径 | 否 | `--output arch.tex`；缺省写 `/tmp/arch.tex` |

缺失时一次性问齐：「请提供：① 图类型（pipeline / nn / svg）② 区块名或层规格 ③ 布局（row/wrap/stack，块多时选 wrap）④ 输出路径（缺省 `/tmp`）。」

## 前置自检
```bash
python3 --version                       # 预期 >= 3.8，否则报错并 STOP
test -f scripts/arch_diagram.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示本技能目录不完整，勿继续。

## 工作流

### 步骤 1：生成 pipeline / block 图
```bash
python3 scripts/arch_diagram.py --type pipeline --blocks "Encoder,Decoder,Head" --output arch.tex
python3 scripts/arch_diagram.py --type pipeline --blocks "A,B,C,D,E" --layout wrap --per-row 3 --format svg --output arch.svg
python3 scripts/arch_diagram.py --type pipeline --blocks "Input#green,Encoder#blue,Head#red" --output arch.tex
```
预期：输出 JSON 含 `output`、`format`、`layout`、`n_blocks`、`blocks`、`escaped`（是否有标签被转义）、`font_command: "\\footnotesize"`、`compilable: true`（TikZ）或 `has_marker_def`/`valid_root`/`editable: true`（SVG）。
若失败：`--blocks` 为空 → 脚本用默认区块（Data/Feature/Model/Loss）；颜色名非法 → 回退 `blue`，不报错。

### 步骤 2：生成层叠示意图（nn）
```bash
python3 scripts/arch_diagram.py --type nn --layers "input(256)" "hidden(128)" "output(10)" --output nn.tex
```
预期：JSON 含 `n_layers`、`layers`、`note`。
若失败：省略 `--layers` 时用 `input(4)/hidden(8)/hidden(4)/output(2)`。
**注意**：本模式只是示意点阵——要发表级的神经元级网络图请改用 **neural-net-draw**（脚本 `note` 也会这么提示）。

### 步骤 3：编译 / 打开校验
```bash
pdflatex -interaction=nonstopmode arch.tex        # TikZ：需 \usepackage{tikz} + \usetikzlibrary{arrows.meta,positioning}
python3 -c "import xml.etree.ElementTree as ET; ET.parse('arch.svg')"   # SVG：验证 XML 合法
```
预期：TikZ 生成 PDF 退出码 0；SVG 解析不抛异常。
若失败：`Package tikz Error` → preamble 补包；SVG 解析失败 → 说明标签含未转义字符，检查 `escaped` 字段。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--type` | pipeline / nn / svg | 图类型，默认 pipeline |
| `--blocks` | 逗号分隔 | pipeline 区块名，支持 `Label#color` |
| `--layers` | 多值 `name(size)` | nn 层规格，如 `input(4) hidden(8)` |
| `--layout` | row / wrap / stack | 排布方式，默认 row |
| `--per-row` | 整数 | `--layout wrap` 时每行块数，默认 3 |
| `--format` | tikz / svg | 默认 tikz；`--type svg` 时强制 svg |
| `--output` | 路径 | 输出文件，缺省 `/tmp/<type>.tex` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 输出文件为空 / 未生成 | 无 `--output` 且 `/tmp` 不可写 | 显式指定可写 `--output` |
| TikZ 报 `Undefined control sequence` | 用了非法的字号命令（v1 的 `\sffootnotesize` 属此类） | 本版已修为 `\footnotesize`；自定义样式时只用 LaTeX 标准字号 |
| TikZ 编译报错 | preamble 缺 tikz 或库 | 加 `\usepackage{tikz}` + `\usetikzlibrary{arrows.meta,positioning}` |
| 箭头在浏览器/Inkscape 不显示 | SVG marker 未定义（v1 的 bug） | 本版已输出 `<defs><marker id="arrow">`；若仍不显示，检查 `has_marker_def` |
| SVG 在编辑器打不开 | 标签含未转义 `&`/`<` 或未用 `--format svg` | 本版会自动转义；用 `ET.parse` 自检 XML |
| 编译后箭头穿框压字 | 默认 anchor 与节点间距不足 | 块多时改 `--layout wrap` 或 `stack`，减少横向挤压 |
| TikZ 文本溢出节点框 | 标签过长 | 缩短标签，或在标签里用 `\\` 手动换行 |
| SVG 中文字体显示为方块 | 预览环境缺中文字体 | 用图内英文标签，或先装字体再打开 SVG |

## 交付标准

成功定义：TikZ 的 JSON `compilable: true` 且无 `\sffootnotesize` 之类非法命令；SVG 的 `valid_root: true` 且 `has_marker_def: true`，并能被 XML 解析器读通。
产物命名：如 `arch.tex` / `arch.svg` / `nn.tex`，由 `--output` 决定。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：TikZ 用 `pdflatex` 编译（或目视确认含 `\begin{tikzpicture}` 与 `\end{tikzpicture}`）；SVG 用 `ET.parse` 或浏览器打开。

## 参考

无外部 references 文件；生成逻辑内置在 `scripts/arch_diagram.py`（`generate_tikz_pipeline` / `generate_svg_pipeline` / `generate_neural_net`），转义在 `escape_latex` / `escape_xml`，布局在 `_positions`，色盲安全配色见 `PALETTE`（与 pub-plotter 同源）。

## 链路位置

与 pub-plotter 并列的图源之一；产物统一进 latex-formatter 组装。神经元级网络结构移交 neural-net-draw。
