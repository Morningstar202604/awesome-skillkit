---
name: neural-net-draw
description: "Draw neural-network structure diagrams as compile-ready LaTeX TikZ from a layer-size list (e.g. 784,512,256,10). 学习自 PlotNeuralNet (25k stars). Use when the user asks 画网络结构图 / 画 CNN 层级图 / 画 MLP 结构图 / 神经网络示意图 / neural network diagram / TikZ 网络图 / network architecture figure. Do NOT use for pipeline/block diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: Stdlib only; emits TikZ source for the PlotNeuralNet toolchain (compilation requires pgfplots in the preamble).
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Neural Net Drawer

由层宽列表生成可直接编译的神经网络结构图 TikZ 源码（逐神经元画节点）。

> 诚实声明：输出的 `compilable: true` 是**静态断言**——脚本不执行编译，只在数学上保证 TikZ 语法自洽；编译是否通过取决于你的 preamble 是否含 pgfplots/TikZ。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 层宽列表 | 是 | `--layers "784,512,256,10,1"`，逗号分隔的每层神经元数 |
| 图题标签 | 否 | `--label "CNN+MLP"`（默认 `Model`，写入生成文件首行注释） |
| 激活函数名 | 否 | `--activation relu`（默认 `relu`；**仅写入输出 JSON 元数据，不改变绘图**） |
| 输出路径 | 否 | `--output net.tex`；缺省时**必定写盘**到 `/tmp/nn_model.tex` |

缺失时一次性问齐：「请提供：① 层宽列表 `--layers` ② 图题 `--label`（可省）③ 是否指定 `--output`（否则落盘 /tmp/nn_model.tex）。」

## 前置自检
```bash
python3 --version                                # 预期 >= 3.8，否则报错并 STOP
test -f scripts/neural_net_draw.py && echo OK    # 预期打印 OK，否则脚本缺失 STOP
```
若产物需要编译预览：`which pdflatex`，且 preamble 需含 `\usepackage{pgfplots}` + `\usetikzlibrary{arrows}`；无 LaTeX 环境时只交付 .tex 源码，不要声称已验证编译。

## 工作流

### 步骤 1：生成 TikZ 源码
```bash
python3 scripts/neural_net_draw.py --layers "784,512,256,10,1" --label "CNN+MLP" --output net.tex
python3 scripts/neural_net_draw.py --layers "3,8,8,2" --activation relu
```
预期：stdout 输出 JSON，含 `output`（.tex 实际落盘路径）、`layers`、`n_params_est`、`compilable: true`、`note: "Requires pgfplots in LaTeX preamble"`；且 `output` 指向的文件存在。
若失败：`--layers` 含非整数 → `ValueError`，检查列表只含逗号分隔整数后重试。

### 步骤 2：核对产物边界

预期：`.tex` 内每层最多绘制 **10 个可见神经元**（`min(n_nodes, 10)`，层宽极大时仅示意）；`n_params_est` 按**全连接层**估算（相邻层乘积+偏置），卷积/残差结构不适用此估计。
若失败：图与预期不符 → 记住本图是层级示意图，不表达真实张量形状/卷积核；需要模块级流程图改用 arch-diagram。

### 步骤 3：编译验证（可选）
```bash
pdflatex -interaction=nonstopmode net.tex
```
预期：生成 `net.pdf`，退出码 0。
若失败：`pgfplots.sty not found` → 在 preamble 加 `\usepackage{pgfplots}`；无权改 preamble → 直接交付 .tex 并注明依赖。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--layers` | 逗号分隔整数 | 每层神经元数（必填） |
| `--label` | 字符串 | 图题，默认 `Model` |
| `--activation` | 字符串 | 默认 `relu`，仅记录在 JSON，不影响绘图 |
| `--output` | 路径 | 输出 .tex；缺省固定为 `/tmp/nn_model.tex` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `ValueError: invalid literal for int()` | `--layers` 含非数字 | 只传逗号分隔整数，如 `"784,512,10"` |
| 产物写到了 /tmp/nn_model.tex | 未传 `--output` | 脚本缺省即写此路径；需要别的位置必须显式 `--output` |
| `pgfplots.sty not found` | preamble 缺包 | 加 `\usepackage{pgfplots}`；交付时注明该依赖 |
| 画的神经元数少于层数字 | 每层可见节点上限 10 | 属预期行为，勿当作 bug；需要完整点阵须改脚本 |

## 交付标准

成功定义：stdout JSON 的 `output` 指向的 .tex 文件存在，内容以 `\begin{tikzpicture}` 开头、`\end{tikzpicture}` 结尾。
产物命名：`net.tex` 或 `--output` 指定名；未指定时为 `/tmp/nn_model.tex`。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`grep -c "\\\\begin{tikzpicture}" <output>` 返回 1；编译交付物时 MUST 附「需 pgfplots」说明，未编译过不得声称 PDF 已验证。

## 参考

无外部 references 文件；绘制与参数量估算逻辑内置在 `scripts/neural_net_draw.py` 的 `draw_nn` / `_estimate_params`。

## 链路位置

图源与 arch-diagram 互补：网络层级走本技能，模块流程走 arch-diagram。产物统一进 latex-formatter 组装。
