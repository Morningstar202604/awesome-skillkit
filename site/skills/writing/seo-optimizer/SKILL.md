---
name: seo-optimizer
description: "Optimize article for search: extract keywords, generate meta tags, score SEO quality, and adapt titles/captions per platform. Use after editing, before publishing to specific platforms. 当用户要求 做 SEO 优化 / 选关键词 / 优化标题 时使用。 Do NOT use for paid advertising strategy."
license: Apache-2.0
compatibility: Pure Python analysis. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: basic
  verified-date: "2026-09-09"
---

# SEO Optimizer

Optimize content for search visibility and platform discovery.

## When to Use

- Article is edited, ready for platform-specific optimization
- Need meta description, tags, and keyword density check
- Adapting one article for multiple platforms (different title lengths)
- Scoring content SEO-readiness before publish

## Input

```json
{
  "title": "FastAPI 性能优化",
  "content": "full article text...",
  "platform": "csdn",
  "target_keywords": ["fastapi", "性能", "优化"]
}
```

## Output

```json
{
  "title": {
    "optimized": "FastAPI 性能优化：5 个关键步骤从 200ms 到 30ms",
    "issues": [],
    "suggestions": ["Add number for CTR"]
  },
  "meta": {
    "description": "FastAPI 性能优化实战：从 P99 200ms 优化到 30ms...",
    "tags": ["fastapi", "性能优化", "python"],
    "keywords": ["fastapi", "性能", "缓存", "async", "索引"]
  },
  "score": 78,
  "platform": "csdn"
}
```

## SEO Score Factors

| Factor | Weight | Check |
|--------|--------|-------|
| Title has keyword | 20 | Primary keyword in title |
| Title length | 10 | Within platform limit |
| Meta description | 15 | 80-160 chars, has keyword |
| Keyword density | 15 | 1-3% (not stuffed) |
| Heading structure | 10 | H1 > H2 > H3 hierarchy |
| Word count | 10 | > 800 words |
| Internal links | 10 | At least 1 |
| Readability | 10 | Short paragraphs, lists |

## Platform Title Limits

| Platform | Max Title | Max Tags | Caption Style |
|----------|----------|----------|---------------|
| CSDN | 50 chars | 5 | 关键词 + 数字 |
| 掘金 | 60 chars | 3 | 【标题】 |
| 微信 | 30 chars | 0 | 短 + 悬念 |
| 百家号 | 30 chars | 3 | 数字 + 痛点 |
| 头条 | 30 chars | 3 | 数字 + 疑问 |

## Workflow

1. Extract keywords from content (frequency analysis)
2. Optimize title (add number, keyword, platform length)
3. Generate meta description (first 150 chars, compelling)
4. Score: 8 factors × weights
5. Per-platform: adapt title/tags to each limit
6. Output: optimized metadata + score

## References

- [references/keyword-research.md](references/keyword-research.md) — keyword selection tips
- [references/platform-rules.md](references/platform-rules.md) — per-platform SEO rules