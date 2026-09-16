---
name: arch-diagram
description: "Generate paper-style architecture/framework diagrams as TikZ (LaTeX) plus editable SVG: pipelines, block stacks, layer stacks. Use when the user asks 画架构图 / 方法总览图 / framework diagram / 画流程图 / pipeline 图. 当用户要求 生成方法章节配图 / 模块框图 时使用。Do NOT use for data charts (use figure-maker) or neuron-level networks (use neural-net-draw)."
license: Apache-2.0
compatibility: Stdlib only; requires python3; outputs TikZ source and SVG, no LaTeX compile required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Arch Diagram

Generate method-overview diagrams (TikZ + editable SVG) for the "Model Architecture" figure.

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 图类型 | 是 | `--type pipeline`（模块流程）/`nn`（网络层级）/`svg`（纯 SVG） |
| 区块或层 | 条件 | pipeline 用 `--blocks "Encoder,Decoder,Head"`；nn 用 `--layers`（见下） |
| 输出格式 | 否 | `--format tikz`/`svg`（仅 pipeline 生效） |
| 输出路径 | 否 | `--output arch.tex`；缺省写 `/tmp/arch.tex` |

缺失时一次性问齐：「请提供：① 图类型（pipeline / nn / svg）② 区块名或层规格（如 `"Encoder,Decoder"` 或 `"784,512,10"`）③ 输出路径（缺省 `/tmp`）。」

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
python3 scripts/arch_diagram.py --type pipeline --blocks "Data,Feature,Model,Loss" --format svg --output arch.svg
```
预期：输出 JSON 含 `output`（文件路径）、`format`、`n_blocks`、`compilable: true`。
若失败：`--blocks` 为空且无默认 → 脚本使用默认区块，补 `--blocks` 重试。

### 步骤 2：生成网络层级图（nn）
```bash
python3 scripts/arch_diagram.py --type nn --layers "input,hidden(256),hidden(128),output" --output nn.tex
```
预期：JSON 含 `n_layers`；TikZ 文件可编译（`compilable: true`）。
若失败：`--layers` 缺省时脚本用 `["input(4)","hidden(8)","hidden(4)","output(2)"]`，按需补 `--layers`。

### 步骤 3：取用产物

预期：`--output` 指向的文件存在且为合法 TikZ / SVG。
若失败：路径不可写 → 换可写目录或省略 `--output` 用 `/tmp` 默认。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--type` | pipeline / nn / svg | 图类型，默认 pipeline |
| `--blocks` | 逗号分隔字符串 | pipeline 的区块名，如 `Encoder,Decoder` |
| `--layers` | 多值，可选 `name(size)` | nn 的层规格，如 `input(4),hidden(8),output(2)` |
| `--format` | tikz / svg | 仅 `--type pipeline` 生效，默认 tikz |
| `--output` | 路径 | 输出文件，缺省 `/tmp/<type>.tex` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 输出文件为空 / 未生成 | 无 `--output` 且 `/tmp` 不可写 | 显式指定可写 `--output` |
| TikZ 编译报错 | preamble 缺 tikz 包 | 在 LaTeX 文档加 `\usepackage{tikz}` |
| SVG 在编辑器打不开 | 未用 `--format svg` | 加 `--format svg` 重跑 |

## 交付标准

成功定义：JSON `compilable: true`（tikz）或 `editable: true`（svg），且 `--output` 文件存在。
产物命名：如 `arch.tex` / `arch.svg` / `nn.tex`，由 `--output` 决定。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：对 tikz 用 LaTeX 编译（或目视确认含 `\begin{tikzpicture}`）；对 svg 用浏览器/Inkscape 打开。

## 参考

无外部 references 文件；生成逻辑内置在 `scripts/arch_diagram.py`（`generate_tikz_pipeline` / `generate_neural_net` / `generate_svg_pipeline`）。

## 链路位置

与 figure-maker / pub-plotter 并列的图源之一；产物统一进 latex-formatter 组装。神经元级网络结构移交 neural-net-draw。
