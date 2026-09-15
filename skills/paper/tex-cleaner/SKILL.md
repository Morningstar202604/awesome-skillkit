---
name: tex-cleaner
description: "Pre-flight cleanup for arXiv/venue submission: strip comments, flag unused packages, external file deps, undefined refs, TOC leftovers, non-ASCII in TeX source. 学习自 google-research/arxiv-latex-cleaner (7k stars). Use when the user asks arXiv 提交前清理 / 清理 LaTeX 工程 / tex 瘦身. Fails with rc=1 when the input file does not exist."
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

Last mile before the submission zip.

## When to Use

- Preparing the arXiv source bundle
- Hunting leftover `\todo`, dead `\usepackage`, unresolved `\ref`
- Checking for non-ASCII characters that break some compilers

## Quick Use

```bash
python3 scripts/tex_cleaner.py --input draft.tex --clean
python3 scripts/tex_cleaner.py --input draft.tex --check
```

## Gate Behavior

Five check classes (external files / low-res figures / undefined refs / TOC /
non-ASCII) are reported; missing file → rc=1.

## Chain Position

paper 域各链的收口步（full_paper / quick_draft / polish_only /
submit_ready 均以本技能结尾）；收口后如需复审可回 self-reviewer。
