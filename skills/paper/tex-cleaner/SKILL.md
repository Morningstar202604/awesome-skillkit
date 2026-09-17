---
name: tex-cleaner
description: "Pre-flight cleanup for arXiv/venue submission: strip comments, flag unused packages, external file deps, undefined refs, TOC leftovers, non-ASCII in TeX source. 学习自 google-research/arxiv-latex-cleaner (7k stars). Use when the user asks arXiv 提交前清理 / 清理 LaTeX 工程 / tex 瘦身 / 删 tex 注释 / 检查未定义引用 / latex cleanup / 提交打包前检查. Fails with rc=1 when the input file does not exist. Also triggers on / 清理 tex 工程 / 删多余宏包 / 检查未定义引用 / arxiv 打包 / strip latex comments. Do NOT use for fixing LaTeX compilation errors (use latex-formatter) or for writing paper content."
license: Apache-2.0
compatibility: Stdlib only; static scan/clean on .tex files.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# TeX Cleaner

提交 zip 前的最后一公里：静态扫描 + 注释清理，产出 arXiv-ready 判定。

> 诚实声明：**默认只读**——不带 `--clean` 时仅打印报告、不改动任何文件；清理结果只在同时给出 `--clean` 和 `--output` 时写入**新文件**（原文件不动），满足 dry-run 优先。`arxiv_ready` 是静态扫描结论，不含编译验证。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| TeX 源文件 | 是 | `--input draft.tex` |
| 清理开关 | 否 | `--clean`；**仅 `--clean` 不落盘**，必须搭配 `--output` 才写出清理后文件 |
| 输出路径 | 否 | `--output draft_clean.tex`；只在 `--clean` 同时给出时生效 |

缺失时一次性问齐：「请提供：① 输入文件 `--input` ② 只查还是要清理 ③ 若清理，落盘路径 `--output`。」

## 前置自检
```bash
python3 --version                           # 预期 >= 3.8，否则报错并 STOP
test -f scripts/tex_cleaner.py && echo OK   # 预期打印 OK，否则脚本缺失 STOP
test -f "$INPUT" && echo TEX_OK             # 预期打印 TEX_OK；缺失则脚本 rc=1，先 STOP
```

## 工作流

### 步骤 1：只读检查（dry-run）
```bash
python3 scripts/tex_cleaner.py --input draft.tex
```
预期：输出 JSON 含 `status`（`"clean"` 或 `"issues_found"`）、`issues[]`、`removed_comments`、`n_lines_original`、`n_lines_cleaned`、`arxiv_ready`（bool）；此时**未写任何文件**。
若失败：rc=1 且 `{"error": "Not found: <path>"}` → 核对 `--input` 路径。

### 步骤 2：逐类处置 issues

预期：`issues[]` 按 `type` 分七类，处置如下——
| type | 含义 | 处置 |
|------|------|------|
| `external_files` | 有 `\input`/`\include` 引用 | 确认所有外部文件会进提交包 |
| `low_res_figures` | 图路径含 `lowres` 或 `.bmp` | 转 PDF/PNG（≥300dpi） |
| `toc_present` / `lof_present` | `\tableofcontents` / `\listoffigures` | arXiv 稿删除 |
| `long_urls` | `\url{...}` 内 ≥50 字符长串 | 改用 `\href` 加短文字 |
| `undefined_refs` | `\ref` 无对应 `\label` | 补 `\label` 或删 `\ref` |
| `non_ascii` | 非 ASCII 字符 | 删除或替换为 LaTeX 命令 |

若失败：改完重跑步骤 1，直到 `status: "clean"` 且 `arxiv_ready: true`。

### 步骤 3：落盘清理文件
```bash
python3 scripts/tex_cleaner.py --input draft.tex --clean --output draft_clean.tex
```
预期：stdout 同步骤 1 的报告，额外多 `cleaned_to: "<output>"` 字段；`draft_clean.tex` 已生成、注释行已剔除（保留 `%\` 开头行），**原 draft.tex 未被修改**。
若失败：输出里没有 `cleaned_to` → 说明只传了 `--clean` 没传 `--output`（或反之），补齐两个参数重跑；`--output` 路径不可写 → 换可写路径。

### 步骤 4：交接下游

预期：`draft_clean.tex` 连同外部文件/图件打提交包；若还需语义复审，回 self-reviewer 跑一轮。
若失败：编译报缺文件 → 回查 `external_files` 类 issue 是否漏带文件。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--input` | 路径 | TeX 源文件（必填） |
| `--clean` | 标志 | 启用清理；单独使用不落盘 |
| `--output` | 路径 | 清理后文件路径，仅与 `--clean` 同用时写出 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=1，`Not found` | `--input` 文件不存在 | 核对路径后重试 |
| 有 `clean` 报告但没生成文件 | 只传了 `--clean` 未传 `--output` | 两参数同时给：`--clean --output <f>` |
| `non_ascii` 计数很大 | 中文批注/全角符号混入 | 逐处替换为 LaTeX 命令或删除；编译器不支持时 MUST 清零 |
| issues 反复清不掉 | 改的文件与 `--input` 不是同一份 | 确认编辑的就是 `--input` 指向的文件后重跑步骤 1 |

## 交付标准

成功定义：`status: "clean"` 且 `arxiv_ready: true`；若清理，则 `cleaned_to` 指向的新文件存在且原文件未变。
产物命名：`draft_clean.tex` 或 `--output` 指定名。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`diff <input> <output>` 仅注释行差异；`python3 -c "import json,sys;r=json.load(sys.stdin);assert r['arxiv_ready']"` 接收 stdout 报告通过。

## 参考

无外部 references 文件；八类扫描与清理逻辑内置在 `scripts/tex_cleaner.py` 的 `clean_latex`。

## 链路位置

paper 域各链的收口步（full_paper / quick_draft / polish_only / submit_ready 均以本技能结尾）；收口后如需复审可回 self-reviewer。
