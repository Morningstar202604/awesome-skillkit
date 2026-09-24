# Search Strategy Guide

## Query decomposition strategies

### Pattern-matching rules

| Pattern | Trigger | Generated query |
|------|---------|---------|
| A and B | Contains "and"/"vs"/"compare" | Add "A vs B" query |
| Best X | Contains "best"/"optimal" | Add "X best practices", "X pros and cons" |
| How to X | Contains "how"/"how to" | Add "X tutorial", "X examples" |
| X framework | Contains "framework" | Add "X introduction", "X tutorial" |

### Time-dimension expansion

```python
# automatically add year queries
if "2024" not in topic and "2025" not in topic:
    queries.append(f"{topic} 2024")
    queries.append(f"{topic} 2025")
```

### Language-dimension expansion

```python
# automatically add English queries
if any('\u4e00' <= c <= '\u9fff' for c in topic):
    queries.append(to_english(topic))
```

---

## Search-engine selection strategy

| Scenario | First choice | Backup | Reason |
|------|---------|---------|------|
| Technical docs | SearXNG | DDG | Aggregates GitHub/official docs |
| News events | SearXNG + DDG | - | Multi-source verification |
| Chinese content | DDG | SearXNG | DDG's Chinese results are better |
| English content | SearXNG | DDG | SearXNG's English results are more accurate |

---

## Credibility scoring model

### Domain credibility weights

| Type | Weight | Examples |
|------|------|------|
| Official docs | 1.0 | docs.python.org, fastapi.tiangolo.com |
| Well-known blogs | 0.85 | realpython.com |
| Q&A communities | 0.85 | stackoverflow.com |
| Tech blogs | 0.65 | medium.com, dev.to |
| Chinese blogs | 0.6 | csdn.net, jianshu.com |
| News sites | 0.7 | techcrunch.com |

### Engine authority weights

| Engine | Weight | Notes |
|------|------|------|
| Google | 0.9 | Highest search quality |
| Bing | 0.85 | Microsoft's engine, reliable quality |
| DuckDuckGo | 0.7 | Privacy-first, slightly weaker results |

---

## Depth control strategy

| Depth level | Rounds | Queries per round | Suitable for |
|---------|------|-----------|---------|
| Basic | 1 | 3 | Simple queries |
| Standard | 2-3 | 5 | General research |
| Deep | 3-5 | 8 | Complex topics |
