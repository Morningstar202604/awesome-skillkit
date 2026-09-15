---
name: anti-defensive
description: "Detect and fix defensive academic writing: over-hedging (double 'may/might'), self-deprecating framing, vague attribution like 'some researchers'. 学习自 anti-defensive-writing (771 stars). Use when the user asks 论文语气太弱 / 去掉防御性表达 / 强化陈述. Do NOT use for removing AI-flavored clichés (use ai-humanizer)."
license: Apache-2.0
compatibility: Stdlib only; takes --text or --file, outputs verdict + rewrites.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: paper
  pattern: single-task
  tier: standard
  verified-date: "2026-09-15"
---

# Anti-Defensive

Say what you mean; stop hedging twice in one sentence.

## When to Use

- Reviewers say claims are weak / wishy-washy
- Sentences stack "may", "might", "suggests that possibly"
- "Some researchers believe" without a citation

## Quick Use

```bash
python3 scripts/anti_defensive.py --text "Our results suggest that the method may possibly improve"
python3 scripts/anti_defensive.py --file draft_section.md
```

## Verdict Semantics

- Clean neutral statements pass
- Double hedging / defensive stock phrases → `rewrite_needed` with suggested fixes

## Chain Position

polish 链一环：journal-adapt 之后、ai-humanizer 并列，最后由
tex-cleaner 收口。改完的段落应回灌 latex-formatter 复检。
