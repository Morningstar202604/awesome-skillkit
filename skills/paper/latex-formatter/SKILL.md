---
name: latex-formatter
description: "Check and normalize paper LaTeX: document class/template sniffing (IEEE etc), balanced environments, unescaped special chars, bibliography presence. Use when the user asks 检查 LaTeX / 论文格式检查 / tex 编译前检查. 当用户要求 排版论文 / 修 LaTeX 报错 时使用。 Fails with rc=1 when the input file does not exist."
license: Apache-2.0
compatibility: Stdlib only; static checks on .tex files, no compiler needed.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# LaTeX Formatter

Gate LaTeX drafts before compile/journal submission.

## When to Use

- Pre-compile sanity check of a draft.tex
- Detecting unescaped `& % #`, unbalanced `\begin{}`/`\end{}`, missing bibliography
- Reformatting toward a template (IEEE etc)

## Quick Use

```bash
python3 scripts/latex_formatter.py --input draft.tex --check
python3 scripts/latex_formatter.py --input draft.tex --template ieee --output clean.tex
```

## Gate Behavior

- Missing file → rc=1（失败当失败的门禁语义）
- Unbalanced environments / bare special chars / no bibliography → reported in JSON

## Chain Position

上游接 figure-maker / arch-diagram / neural-net-draw 的图产物；
检查通过后移交 self-reviewer 做内容审，再进 journal-adapt 换模板。
