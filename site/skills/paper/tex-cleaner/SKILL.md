---
name: tex-cleaner
description: "Pre-flight cleanup for arXiv/venue submission: strip comments (escape/verbatim-aware), flag packages installed-but-unused via a command→package map, list missing assets (\\input/\\bibliography/\\includegraphics), undefined refs, TOC leftovers, non-ASCII in TeX source. 学习自 google-research/arxiv-latex-cleaner (7k stars). Use when the user asks arXiv 提交前清理 / 清理 LaTeX 工程 / tex 瘦身 / 删 tex 注释 / 检查未定义引用 / latex cleanup / 提交打包前检查. Fails with rc=1 when the input file does not exist (or when --clean is given without --output). Also triggers on / 清理 tex 工程 / 删多余宏包 / 检查未定义引用 / arxiv 打包 / strip latex comments. Do NOT use for fixing LaTeX compilation errors (use latex-formatter) or for writing paper content."
license: Apache-2.0
compatibility: Stdlib only; static scan/clean on .tex files. Never modifies the input file.
metadata:
  version: "2.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-21"
---

# TeX Cleaner (SOTA)

提交 zip 前的最后一公里：注释剥离 + 未用宏包 + 资源清单 + arXiv-ready 判定。

> 诚实声明：**默认只读**——不带 `--clean` 时仅打印报告、不改动任何文件；`--clean` **必须**同时给 `--output`（否则 rc=1，绝不静默无操作），且写的是**新文件**，原文件不动。`arxiv_ready` 是静态扫描结论，**不含编译验证**。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| TeX 源文件 | 是 | `--input draft.tex`；不存在则 rc=1 |
| 清理开关 | 否 | `--clean`；单独使用报错，必须搭配 `--output` |
| 输出路径 | 否 | `--output draft_clean.tex`；只在 `--clean` 同时给出时生效 |
| 基准目录 | 否 | `--dir`；核对 `\input`/图/bib 是否存在（默认取 `--input` 所在目录） |

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
python3 scripts/tex_cleaner.py --input draft.tex --dir paper/   # 顺带核对资源存在性
```
预期：输出 JSON 含 `status`（`"clean"`/`"issues_found"`）、`issues[]`、`unused_packages[]`、`assets{groups,missing}`、`removed_comments`、`full_line_comments_removed`、`n_lines_original`、`n_lines_cleaned`、`arxiv_ready`（bool）；此时**未写任何文件**。
若失败：rc=1 且 `{"status":"error","error":"Not found: ..."}` → 核对 `--input` 路径。

### 步骤 2：逐类处置 issues

| type | 含义 | 处置 |
|------|------|------|
| `unused_packages` | 宏包装了但命令未出现（命令→宏包映射判定） | 删 `\usepackage`；**注意**隐式生效的包在 `NEVER_UNUSED` 白名单里不会报 |
| `external_files` | 有 `\input`/`\include` 引用 | 确认所有外部文件进提交包 |
| `missing_assets` | 引用的图/bib/input 在 `--dir` 下找不到 | 补齐文件或改路径（提交包最常见的漏项） |
| `low_res_figures` | 图路径含 `lowres` 或 `.bmp` | 转 PDF/PNG（≥300dpi） |
| `toc_present` / `lof_present` | `\tableofcontents` / `\listoffigures` | arXiv 稿删除 |
| `long_urls` | `\url{...}` 内 ≥50 字符 | 改用 `\href{url}{短文字}` |
| `undefined_refs` | `\ref`/`\eqref`/`\autoref`/`\cref` 无对应 `\label` | 补 `\label` 或删引用 |
| `non_ascii` | 非 ASCII 字符 | 替换为 LaTeX 命令或删除 |

若失败：改完重跑步骤 1，直到 `status: "clean"` 且 `arxiv_ready: true`。

### 步骤 3：落盘清理文件
```bash
python3 scripts/tex_cleaner.py --input draft.tex --clean --output draft_clean.tex
```
预期：stdout 报告多出 `cleaned_to: "<output>"`；新文件注释已剥离（行尾注释截断、整行注释删行、`\%` 与 verbatim 内 `%` 保留），**原 draft.tex 逐字节未变**。报告里**不含** `cleaned_text`（避免正文回灌）。
若失败：rc=1 且 error 含 `--output` → 补齐 `--output` 重跑；路径不可写 → 换可写路径。

### 步骤 4：交接下游
预期：`draft_clean.tex` 连同 `assets.groups` 列出的文件打提交包；若还需语义复审，回 self-reviewer 跑一轮。
若失败：编译报缺文件 → 回查 `missing_assets` 类 issue 是否漏带文件。

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| `--input` | 路径 | TeX 源文件（必填） |
| `--clean` | 标志 | 启用清理；必须与 `--output` 同用（否则 rc=1） |
| `--output` | 路径 | 清理后**新**文件路径，原文件永不修改 |
| `--dir` | 路径 | 资源存在性核对基准目录，默认 `--input` 所在目录 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------------|------|------|
| rc=1，`Not found` | `--input` 文件不存在 | 核对路径后重试 |
| rc=1，error 含 `--output` | 只传 `--clean` 未传 `--output` | `--clean --output <f>` 一起给 |
| `missing_assets` 误报 | `--dir` 不是真实工程根目录 | 用 `--dir` 指向包含图/bib 的目录 |
| `unused_packages` 误报 | 宏包靠隐式机制生效（如 `hyperref` 改写 `\ref`） | 把该包加进脚本 `NEVER_UNUSED`，或人工忽略该条 |
| `non_ascii` 计数很大 | 中文批注/全角符号混入 | 逐处替换为 LaTeX 命令或删除；编译器不支持时 MUST 清零 |
| issues 反复清不掉 | 改的文件与 `--input` 不是同一份 | 确认编辑的就是 `--input` 指向的文件后重跑步骤 1 |

## 交付标准

成功定义：`status: "clean"` 且 `arxiv_ready: true`；若清理，则 `cleaned_to` 指向的新文件存在且原文件逐字节未变。
产物命名：`draft_clean.tex` 或 `--output` 指定名。
保存位置：调用方当前目录或 `--output` 指定路径。
验证方法：`python3 -c "import json,sys;r=json.load(sys.stdin);assert r['arxiv_ready']"` 接收 stdout 报告通过；清理正确性用「原文件未被改动 + 新文件无行尾注释」双查。

## 参考

无外部 references 文件；注释剥离（`strip_comments`，转义 + verbatim 感知）、未用宏包（`find_unused_packages` + `PACKAGE_COMMANDS`/`NEVER_UNUSED`）、资源清单（`collect_assets`）逻辑内置在 `scripts/tex_cleaner.py`。对标 google-research/arxiv-latex-cleaner。

## 链路位置

paper 域各链的收口步（full_paper / quick_draft / polish_only / submit_ready 均以本技能结尾）；收口后如需复审可回 self-reviewer。
