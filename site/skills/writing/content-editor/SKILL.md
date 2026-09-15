---
name: content-editor
description: "Proofread, polish, and style-unify article drafts. Detects banned words, inconsistent tone, overlong sentences, and grammar issues. Scores editability. Use after drafting, before SEO and publishing. 当用户要求 润色文章 / 校对错别字 / 统一文风 / 改掉 AI 腔 时使用。 Do NOT use for generating new content from scratch (editing and polishing only)."
license: Apache-2.0
compatibility: Pure Python analysis; LLM-assisted for rewriting. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Content Editor

Proofread, polish, and enforce style consistency.

## When to Use

- Draft is written, needs quality pass before publishing
- Enforce house style / brand voice
- Remove filler words, fix grammar
- Ensure consistent tone across sections
- Score editability (0-100)

## Input

```json
{
  "draft": {
    "title": "...",
    "sections": [{"heading": "...", "draft": "text..."}]
  },
  "style": "technical | casual | news",
  "brand_voice": "optional: description of desired voice"
}
```

## Output

```json
{
  "score": 82,
  "issues": [
    {"type": "banned_word", "word": "我觉得", "line": 12},
    {"type": "long_sentence", "chars": 78, "limit": 40, "line": 25}
  ],
  "suggestions": ["Add transition phrase between sections 2 and 3"],
  "sections_edited": 5,
  "status": "reviewed"
}
```

## Style Rules

| Style | Ban | Use | Max Sentence |
|-------|-----|-----|--------------|
| Technical | 我觉得/应该/可能 | 根据/实测/结论是 | 40 chars |
| Casual | 综上所述/由此可见 | 说白了/你看 | 25 chars |
| News | 震惊/炸了/绝了 | 据悉/报道称 | 30 chars |

## Workflow

1. Load draft
2. Scan for banned words (style-specific)
3. Check sentence length
4. Verify section transitions
5. Score (100 - issues×5 - long_sentences×2)
6. Output: issues list + suggestions + score

## References

- [references/style-guide.md](references/style-guide.md) — house style rules
- [references/grammar-checks.md](references/grammar-checks.md) — common Chinese/English errors