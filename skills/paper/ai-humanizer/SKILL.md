---
name: ai-humanizer
description: "Strip AI-flavored writing from academic text: clichés ('delve', 'leverage', 'state-of-the-art' spam), empty intensifiers, over-qualification, repetitive sentence openers — while keeping the academic register. 学习自 academic-humanizer (1.5k stars). Use when the user asks 去 AI 味 / 降低 AI 痕迹 / 学术文本去套路. Do NOT use for hedging/defensive tone (use anti-defensive)."
license: Apache-2.0
compatibility: Stdlib only; takes --text or --file, supports --report.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# AI Humanizer

Keep the science, lose the robot voice.

## When to Use

- Draft reads like LLM output: "novel framework leverages state-of-the-art..."
- Six detectable AI-tell categories before submission
- Need a before/after report for co-authors

## Quick Use

```bash
python3 scripts/ai_humanizer.py --text "Our novel framework leverages state-of-the-art methods"
python3 scripts/ai_humanizer.py --file draft.md --report humanize_report.json
```

## Verdict Semantics

- No AI-tells → pass
- Cliché / empty expression / over-qualification clusters → `needs_edit` with per-hit notes

## Chain Position

polish 链一环：与 anti-defensive 并列（本技能管"AI 腔"，
anti-defensive 管"防御腔"），随后 tex-cleaner 收口。
