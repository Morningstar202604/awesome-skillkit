---
name: journal-adapt
description: "Adapt a draft to a target venue's writing conventions: IEEE / ACM / NeurIPS / ACL / Nature / Cell, including banned-phrase screening (e.g. Nature dislikes 'In this paper we' / 'Novel') and section-shape checks. 学习自 Awesome-Journal-Skills (200+ journals). Use when the user asks 投 IEEE / 改成 Nature 风格 / 期刊格式适配. Do NOT use for LaTeX template mechanics (use latex-formatter)."
license: Apache-2.0
compatibility: Stdlib only; static text checks against per-venue rule tables.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Journal Adapt

Retarget an existing draft to a venue's voice and structure.

## When to Use

- Same paper, different venue: rephrase and reshuffle per venue rules
- Screening banned phrases before a Nature/Cell submission

## Quick Use

```bash
python3 scripts/journal_adapt.py --input draft.tex --target ieee
python3 scripts/journal_adapt.py --input draft.tex --target nature
```

## Checks

- Per-venue banned phrases (hits block the pass)
- Required sections and page-limit awareness

## Chain Position

上游接 self-reviewer 的 ready 判定；语气打磨可续接
anti-defensive 与 ai-humanizer，最终 tex-cleaner 收口提交包。
