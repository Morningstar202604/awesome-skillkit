# Search Case Library

## Table of Contents

- [Case 1: Basic search (SearXNG)](#case-1-basic-search-searxng)
- [Case 2: Chinese-language search](#case-2-chinese-language-search)
- [Case 3: Cache hit](#case-3-cache-hit)
- [Case 4: Search-engine fallback](#case-4-search-engine-fallback)
- [Case 5: Deep search](#case-5-deep-search)
- [Case 6: Error handling](#case-6-error-handling)
- [Case sources](#case-sources)

---

## Case 1: Basic search (SearXNG)

**Input:**
```python
result = search("Python FastAPI best practices", engine="searxng")
```

**Output:**
```json
{
  "query": "Python FastAPI best practices",
  "total_results": 10,
  "search_time_ms": 342,
  "engine": "searxng",
  "results": [
    {
      "title": "FastAPI Documentation",
      "url": "https://fastapi.tiangolo.com/",
      "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+...",
      "engine": "google",
      "score": 0.95
    },
    {
      "title": "FastAPI vs Flask - Which One Should You Choose?",
      "url": "https://realpython.com/fastapi-python-rest-api/",
      "content": "FastAPI is gaining popularity among Python developers...",
      "engine": "duckduckgo",
      "score": 0.88
    }
  ]
}
```

---

## Case 2: Chinese-language search

**Input:**
```python
result = search("machine learning beginner tutorial", engine="searxng", language="zh")
```

**Output:**
```json
{
  "query": "machine learning beginner tutorial",
  "total_results": 10,
  "engine": "searxng",
  "results": [
    {
      "title": "Machine Learning Intro - Runoob Tutorial",
      "url": "https://www.runoob.com/ml/ml-tutorial.html",
      "content": "Machine learning is a branch of artificial intelligence...",
      "engine": "bing",
      "score": 0.92
    }
  ]
}
```

---

## Case 3: Cache hit

**First search:**
```python
result1 = search("Python web scraping", use_cache=True)
# output: search_time_ms=450, cached=False
```

**Second search (same query):**
```python
result2 = search("Python web scraping", use_cache=True)
# output: search_time_ms=2, cached=True
```

**Note:** the second read straight from cache, dropping the latency from 450ms to 2ms.

---

## Case 4: Search-engine fallback

**SearXNG failure scenario:**
```python
# when all SearXNG instances are unavailable
result = search("test query", engine="searxng")
# auto-fallback to DuckDuckGo
# result["engine"] = "duckduckgo"
```

---

## Case 5: Deep search

**Input:**
```python
result = deep_search("2024 AI development trends", max_rounds=3)
```

**Flow:**
1. Round 1: search "2024 AI development trends" → 10 results
2. Analyze results, generate sub-queries:
   - "2024 AI large models"
   - "2024 AI applications"
3. Round 2: search the sub-queries → 5 results each
4. Round 3: go deeper → 3 results each
5. Aggregate and dedupe → final 15 results

**Output:**
```json
{
  "query": "2024 AI development trends",
  "total_results": 15,
  "rounds": 3,
  "results": [...]
}
```

---

## Case 6: Error handling

**Network unreachable:**
```python
result = search("test", use_cache=False)
# output:
{
  "query": "test",
  "error": "all search engines unavailable",
  "results": [],
  "total_results": 0
}
```

---

## Case sources

| Case | Source | Scenario |
|------|------|------|
| Case 1 | Real search | Technical documentation lookup |
| Case 2 | Real search | Chinese content retrieval |
| Case 3 | Test case | Cache feature verification |
| Case 4 | Test case | Fallback logic verification |
| Case 5 | Test case | Deep search verification |
| Case 6 | Test case | Error handling verification |
