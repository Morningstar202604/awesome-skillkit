---
name: neural-net-draw
description: "Draw neural-network structure diagrams as compile-ready LaTeX TikZ from a layer spec. 学习自 PlotNeuralNet (25k stars). Use when the user asks 画网络结构图 / 画 CNN 层级图 / 画 MLP 结构图 / 神经网络示意图 / neural network diagram / TikZ 网络图 / network architecture figure. Do NOT use for pipeline/block diagrams (use arch-diagram)."
license: Apache-2.0
compatibility: Stdlib only; emits TikZ source for the PlotNeuralNet toolchain (compilation requires pgfplots + tikz in the preamble).
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# Neural Net Drawer (SOTA)

由层规格生成可编译的神经网络结构图 TikZ。支持两种画法：

- **per-neuron**（兼容 v1）：每层逐神经元画圆点（层宽极大时每层最多 10 个可见点，层高层高封顶 3cm）；
- **typed-blocks**（PlotNeuralNet 风格）：按层类型（conv/pool/residual/linear/attention/…）画彩色 `nnblock`，更贴近真实架构。

> 诚实声明：`compilable: true` 是**静态语法自洽**断言——脚本不执行 pdflatex，只在数学上保证 TikZ 自洽；编译是否通过取决于 preamble 是否含 pgfplots + tikz。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 层规格 | 是 | `--layers`：逗号分隔。旧式纯宽度 `"784,512,10"`（默认全连接）或类型式 `"784:input,64:conv,64:pool,128:linear,10:output"`。合法类型：`input,conv,pool,residual,linear,fc,attention,dropout,output` |
| 图题标签 | 否 | `--label "CNN+MLP"`（默认 `Model`，写入生成文件首行注释） |
| 激活函数名 | 否 | `--activation relu`（默认 `relu`；**仅写入输出 JSON 元数据，不改变绘图**） |
| 画法 | 否 | `--style auto/per-neuron/typed-blocks`（默认 `auto`：有类型→typed-blocks，否则 per-neuron） |
| 输出路径 | 否 | `--output net.tex`；缺省**必定写盘**到 `/tmp/nn_model.tex` |

缺失时一次性问齐：「请提供：① 层规格 `--layers`（可带类型）② 图题 `--label`（可省）③ 是否指定 `--output`（否则落盘 /tmp/nn_model.tex）。」

## 前置自检
```bash
python3 --version                                # 预期 >= 3.8，否则报错并 STOP
test -f scripts/neural_net_draw.py && echo OK    # 预期打印 OK，否则脚本缺失 STOP
```
若产物需要编译预览：`which pdflatex`，且 preamble 需含 `\usepackage{pgfplots}` + `\usepackage{tikz}`；无 LaTeX 环境时只交付 .tex 源码，不要声称已验证编译。

## 工作流

### 步骤 1：生成 TikZ 源码
```bash
# 旧式（纯宽度，自动 per-neuron）
python3 scripts/neural_net_draw.py --layers "784,512,256,10,1" --label "CNN+MLP" --output net.tex
# SOTA（带类型，自动 typed-blocks）
python3 scripts/neural_net_draw.py --layers "784:input,64:conv,64:pool,128:linear,10:output" --style typed-blocks
python3 scripts/neural_net_draw.py --layers "512:residual,256:attention,10:output"
```
预期：stdout 输出 JSON，含 `output`（.tex 实际落盘路径）、`layers`（解析后的 `w:type` 列表）、`n_params_est`、`method`（`per-neuron`/`typed-blocks`）、`compilable: true`、`note`；且 `output` 指向的文件存在。
若失败：`--layers` 含非整数宽度或未知类型 → `ValueError`，宽度只留数字、类型只留合法枚举后重试。

### 步骤 2：核对产物边界
- `n_params_est` 仅对**全连接/linear 层**按相邻层乘积 + 偏置估算；conv/attn 等层按其核尺寸/头数依赖无法建模，本工具计 0 并标注近似——需要精确参数量请用模型导出（`torch` 的 `num_parameters()`）。
- per-neuron：每层最多 10 个可见节点（层宽极大时仅示意），层高层高封顶 3cm。
若失败：图与预期不符 → 记住这是层级/模块示意图，不表达真实张量形状/卷积核；需要模块级流程图改用 arch-diagram。

### 步骤 3：编译验证（可选）
```bash
pdflatex -interaction=nonstopmode net.tex
```
预期：生成 `net.pdf`，退出码 0。
若失败：`pgfplots.sty not found` → 在 preamble 加 `\usepackage{pgfplots}`；无权改 preamble → 直接交付 .tex 并注明依赖。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--layers` | `w` 或 `w:type` | 每层（必填）；类型枚举见上 |
| `--label` | 字符串 | 图题，默认 `Model` |
| `--activation` | 字符串 | 默认 `relu`，仅记录在 JSON，不影响绘图 |
| `--style` | auto/per-neuron/typed-blocks | 默认 auto |
| `--output` | 路径 | 输出 .tex；缺省固定 `/tmp/nn_model.tex` |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| `ValueError: unknown layer type` | `w:type` 的 type 不在合法枚举 | 只用 `input,conv,pool,residual,linear,fc,attention,dropout,output` |
| `ValueError: invalid literal for int()` | `--layers` 宽度含非数字 | 宽度只传整数（类型用 `:type` 后缀） |
| 产物写到了 /tmp/nn_model.tex | 未传 `--output` | 脚本缺省即写此路径；需要别的位置必须显式 `--output` |
| `pgfplots.sty not found` | preamble 缺包 | 加 `\usepackage{pgfplots}`；交付时注明该依赖 |
| 画的神经元数少于层数字 | per-neuron 每层上限 10、层高层高封顶 | 属预期行为，勿当作 bug；要完整点阵/精确高度须改脚本 |

## 交付标准

成功定义：stdout JSON 的 `output` 指向的 .tex 文件存在，内容以 `\begin{tikzpicture}` 开头、`\end{tikzpicture}` 结尾。
产物命名：`net.tex` 或 `--output` 指定名；未指定时为 `/tmp/nn_model.tex`。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`grep -c "\\\\begin{tikzpicture}" <output>` 返回 1；编译交付物时 MUST 附「需 pgfplots + tikz」说明，未编译过不得声称 PDF 已验证。

## 参考

无外部 references 文件；绘制与参数量估算逻辑内置在 `scripts/neural_net_draw.py` 的 `draw_nn` / `_render_per_neuron` / `_render_typed_blocks` / `_estimate_params`。对标 PlotNeuralNet（HarisIqbal88）。

## 链路位置

图源与 arch-diagram 互补：网络层级走本技能，模块流程走 arch-diagram。产物统一进 latex-formatter 组装。
