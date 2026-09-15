---
name: self-reviewer
description: "Simulate a peer review pass on your own draft: section completeness (abstract, 4+ sections, citations, baselines, limitations), word-count floor, and a verdict of ready / needs_work. Use before submitting or after finishing a draft. 当用户要求 模拟审稿 / 自查论文 / 投稿前检查 时使用。 Fails with rc=1 when the paper file does not exist."
license: Apache-2.0
compatibility: Stdlib only; reads .tex or plain-text drafts.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Self Reviewer

Be your own reviewer #4 before a real one sees it.

## When to Use

- Finished a draft, want a structured pre-submission pass
- Checking the reviewer-proof checklist: baselines named, limitations stated

## Quick Use

```bash
python3 scripts/self_reviewer.py --paper draft.tex
python3 scripts/self_reviewer.py --paper draft.tex --checklist
```

## Verdict Semantics

- `ready` — all structural gates pass
- `needs_work` — short draft / missing sections / no baseline or limitations

## Chain Position

上游接 latex-formatter（格式先过关）。`needs_work` 时回到正文修订；
`ready` 后移交 journal-adapt 换目标模板，最后 tex-cleaner 收口。
