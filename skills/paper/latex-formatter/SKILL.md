---
name: latex-formatter
description: "Check and normalize paper LaTeX: document class/template sniffing (IEEE etc), balanced environments, unescaped special chars, bibliography presence. Use when the user asks 检查 LaTeX / 论文格式检查 / tex 编译前检查 / 排版论文 / 修 LaTeX 报错. 当用户要求 按模板规整 tex / 查未闭合环境 时使用。Fails with rc=1 when the input file does not exist."
license: Apache-2.0
compatibility: Stdlib only; requires python3; static checks on .tex files, no compiler needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# LaTeX Formatter

Gate LaTeX drafts before compile / journal submission: sniff template, check balance, flag issues.

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 草稿文件 | 是 | `--input draft.tex` 读 .tex 文件 |
| 目标模板 | 否 | `--template ieee`/`acm`/`neurips`/`generic`，默认 `ieee` |
| 输出路径 | 否 | `--output clean.json`，缺省打印到 stdout |

缺失时一次性问齐：「请提供：① 草稿文件路径 `--input` ② 目标模板 `--template`（ieee/acm/neurips/generic）③ 是否落盘 `--output`。其余用默认：template=ieee，输出 JSON 到 stdout。」

## 前置自检
```bash
python3 --version                           # 预期 >= 3.8，否则报错并 STOP
test -f scripts/latex_formatter.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
test -f draft.tex && echo SRC_OK             # 仅当用 --input 时；缺失则脚本将 rc=1 STOP
```
若 `python3` 不存在 → 提示安装 Python ≥3.8；若脚本缺失 → 提示目录不完整；若 `--input` 文件不存在 → 脚本返回 **rc=1**，须先补文件。

## 工作流

### 步骤 1：运行格式门禁
```bash
python3 scripts/latex_formatter.py --input draft.tex --template ieee --output clean.json
python3 scripts/latex_formatter.py --input draft.tex --template neurips
```
预期：输出 JSON 含 `template`、`class`、`status`、`issues[]`、`suggestions[]`、`n_lines`。
若失败：进程退出码 1 且 `{"status":"error","error":"File not found: ..."}` → `--input` 路径不存在，STOP 补齐。

### 步骤 2：判读 verdict 并修

- `status == "pass"`（`issues` 为空）→ 通过，可进下游。
- `status == "issues_found"` → 按 `issues[]` 与 `suggestions[]` 修：
  - `Unbalanced environments` → 核对每个 `\begin{x}` 有匹配 `\end{x}`；
  - `no \bibliography` + 有 `\cite` → 加 `\bibliography{refs}`；
  - `Raw & / % / #` → 转义为 `\&` / `\%` / `\#`；
  - `Missing \begin{document}` → 补文档结构。
预期：`issues` 每项有可定位文案，`suggestions` 给修复动作。
若失败：修后仍 `issues_found` → 逐项复盘 `issues[]` 直到清空。

### 步骤 3：存档（可选）

预期：`--output` 指向的 JSON 文件存在且合法。
若失败：路径不可写 → 换可写目录重试。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--input` | 路径 | .tex 草稿（必填） |
| `--template` | ieee / acm / neurips / generic | 目标模板，默认 ieee |
| `--output` | 路径 | 结果 JSON 输出路径 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| 退出码 1 + File not found | `--input` 不存在 | 校验路径真实存在后重试 |
| `Unbalanced environments: ±N` | `\begin`/`\end` 不配对 | 逐对补齐环境 |
| `Raw & needs escaping` | 正文未转义特殊字符 | 改为 `\&`/`\%`/`\#` |

## 交付标准

成功定义：`status == "pass"`（无 issues），或已据 `issues_found` 完成修复。
产物命名：`clean.json`（若指定 `--output`）。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json;d=json.load(open('<output>'));assert d['status'] in ('pass','issues_found')"` 通过。

## 参考

无外部 references 文件；模板表内置在 `scripts/latex_formatter.py` 的 `TEMPLATES`（class / options / columns / font_size）。

## 链路位置

上游接 figure-maker / arch-diagram / neural-net-draw 的图产物；检查通过后移交 self-reviewer 做内容审，再进 journal-adapt 换模板。
