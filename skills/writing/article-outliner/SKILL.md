---
name: article-outliner
description: "Create article outlines: structure, section hierarchy, key points, and reading flow. Supports blog posts, technical articles, news, and listicles. Use when the topic is defined but structure is needed before drafting."
license: Apache-2.0
compatibility: Pure prompt-based; may call LLM for generation. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: writing
  pattern: single-task
  tier: standard
  verified-date: "2026-09-09"
---

# Article Outliner

Structure articles before drafting: section hierarchy, key points, reading flow.

## When to Use

- Topic is defined, need structure before writing
- Planning a multi-section technical article
- Creating a listicle or how-to guide
- Structuring news or opinion pieces
- Preparing for multi-platform distribution (different lengths)

## Input

```json
{
  "topic": "FastAPI 性能优化",
  "type": "technical | blog | news | listicle | opinion",
  "target_length": "short(800) | medium(2000) | long(5000)",
  "audience": "beginner | intermediate | expert",
  "key_points": ["async", "caching", "DB indexing"],
  "platforms": ["csdn", "juejin", "wechat"]
}
```

## Output

```json
{
  "title": "FastAPI 性能优化：从 200ms 到 30ms 的 5 个关键步骤",
  "hook": "你的 FastAPI 接口为什么慢？",
  "sections": [
    {
      "id": 1,
      "heading": "为什么你的 FastAPI 慢",
      "level": 2,
      "points": ["同步 I/O 阻塞事件循环", "N+1 查询", "缺少缓存"],
      "word_count_target": 300
    },
    {
      "id": 2,
      "heading": "5 个优化技巧",
      "level": 2,
      "points": [
        {"sub": "使用 async/await", "detail": "替换同步数据库调用"},
        {"sub": "Redis 缓存", "detail": "热点数据 5min TTL"},
        {"sub": "数据库索引", "detail": "EXPLAIN 分析慢查询"},
        {"sub": "连接池", "detail": "pgBouncer / SQLAlchemy pool"},
        {"sub": "批量查询", "detail": "IN 查询替代循环"}
      ],
      "word_count_target": 1200
    },
    {
      "id": 3,
      "heading": "性能对比",
      "level": 2,
      "points": ["优化前 P99: 200ms", "优化后 P99: 30ms"],
      "word_count_target": 400
    }
  ],
  "conclusion": "总结 + CTA (关注/收藏/评论)",
  "total_words_target": 2000,
  "reading_time_min": 8
}
```

## Workflow

1. **Analyze topic** — determine complexity, audience level
2. **Choose structure** — linear (how-to), problem-solution, listicle, narrative
3. **Define sections** — 3-7 major sections for most articles
4. **Add key points** — 2-5 bullets per section
5. **Set word targets** — total word count / section count
6. **Write hook** — first 2 sentences must grab attention
7. **Plan CTA** — what should reader do after reading?

## Structure Patterns

| Pattern | Best For | Sections |
|---------|----------|----------|
| Problem → Solution | Technical articles | 3-5 |
| Listicle | Tips, tricks, resources | N items + intro + outro |
| Tutorial | How-to guides | Steps 1-N + prerequisites + result |
| News | Announcements, updates | What → Why → How → Impact |
| Opinion | Essays, commentary | Thesis → Arguments → Counter → Conclusion |

## References

- [references/outline-templates.md](references/outline-templates.md) — ready-made templates per type
- [references/flow-guide.md](references/flow-guide.md) — reading flow, transition phrases
