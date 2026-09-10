---
name: article-drafter
description: "Generate article first draft from outline. Fills in each section with prose based on key points, audience level, and style. Use after outline is approved, before editing/SEO."
license: Apache-2.0
compatibility: Pure prompt-based; LLM generates text. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Article Drafter

Generate first-draft text from an approved outline.

## When to Use

- Outline is ready, need to fill in actual prose
- Converting research notes into readable article
- Generating section-by-section content for review
- Multi-platform: draft once, adapt later

## Input

```json
{
  "outline": {
    "title": "FastAPI 性能优化",
    "sections": [
      {"heading": "为什么慢", "points": ["同步I/O", "N+1"], "word_count_target": 300}
    ]
  },
  "audience": "intermediate",
  "tone": "technical",
  "research_notes": "optional raw material"
}
```

## Output

```json
{
  "title": "FastAPI 性能优化",
  "sections": [
    {
      "id": 1,
      "heading": "为什么慢",
      "draft": "FastAPI 默认使用 async/await，但很多开发者...",
      "word_count": 320
    }
  ],
  "total_words": 1850,
  "status": "draft",
  "needs_review": true
}
```

## Workflow

1. Load outline (from article-outliner)
2. For each section:
   - Read key points
   - Expand into 2-4 paragraphs
   - Match audience level (jargon density)
   - Hit word_count_target ± 20%
3. Write intro hook (from outline.hook)
4. Write conclusion + CTA
5. Output: full draft JSON (or markdown)

## Style Rules by Audience

| Audience | Jargon | Examples | Code |
|----------|--------|---------|------|
| Beginner | Minimal, explain all | 3-4 per section | Full snippets |
| Intermediate | Moderate, standard terms | 2-3 | Key snippets |
| Expert | High, assume knowledge | 0-1 | One-liners |

## References

- [references/drafting-tips.md](references/drafting-tips.md) — writing tips per section type
