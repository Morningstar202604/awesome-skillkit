# 搜索案例库

## Table of Contents

- [案例 1：基础搜索（SearXNG）](#案例-1基础搜索searxng)
- [案例 2：中文搜索](#案例-2中文搜索)
- [案例 3：缓存命中](#案例-3缓存命中)
- [案例 4：搜索引擎降级](#案例-4搜索引擎降级)
- [案例 5：深度搜索](#案例-5深度搜索)
- [案例 6：错误处理](#案例-6错误处理)
- [案例来源](#案例来源)

---

## 案例 1：基础搜索（SearXNG）

**Input:**
```python
result = search("Python FastAPI 最佳实践", engine="searxng")
```

**Output:**
```json
{
  "query": "Python FastAPI 最佳实践",
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

## 案例 2：中文搜索

**Input:**
```python
result = search("机器学习入门教程", engine="searxng", language="zh")
```

**Output:**
```json
{
  "query": "机器学习入门教程",
  "total_results": 10,
  "engine": "searxng",
  "results": [
    {
      "title": "机器学习入门 - 菜鸟教程",
      "url": "https://www.runoob.com/ml/ml-tutorial.html",
      "content": "机器学习是人工智能的一个分支...",
      "engine": "bing",
      "score": 0.92
    }
  ]
}
```

---

## 案例 3：缓存命中

**第一次搜索：**
```python
result1 = search("Python 爬虫", use_cache=True)
# 输出：search_time_ms=450, cached=False
```

**第二次搜索（相同查询）：**
```python
result2 = search("Python 爬虫", use_cache=True)
# 输出：search_time_ms=2, cached=True
```

**说明：** 第二次直接从缓存读取，耗时从 450ms 降至 2ms。

---

## 案例 4：搜索引擎降级

**SearXNG 失败场景：**
```python
# 所有 SearXNG 实例不可用时
result = search("test query", engine="searxng")
# 自动降级到 DuckDuckGo
# result["engine"] = "duckduckgo"
```

---

## 案例 5：深度搜索

**Input:**
```python
result = deep_search("2024年AI发展趋势", max_rounds=3)
```

**流程：**
1. 第 1 轮：搜索 "2024年AI发展趋势" → 10 条结果
2. 分析结果，生成子查询：
   - "2024年AI大模型"
   - "2024年AI应用"
3. 第 2 轮：搜索子查询 → 各 5 条结果
4. 第 3 轮：继续深入 → 各 3 条结果
5. 汇总去重 → 最终 15 条结果

**Output:**
```json
{
  "query": "2024年AI发展趋势",
  "total_results": 15,
  "rounds": 3,
  "results": [...]
}
```

---

## 案例 6：错误处理

**网络不可达：**
```python
result = search("test", use_cache=False)
# 输出：
{
  "query": "test",
  "error": "所有搜索引擎不可用",
  "results": [],
  "total_results": 0
}
```

---

## Case sources

| Case | Source | Scenario |
|------|------|------|
| 案例 1 | 真实搜索 | 技术文档查询 |
| 案例 2 | 真实搜索 | 中文内容检索 |
| 案例 3 | 测试用例 | 缓存功能验证 |
| 案例 4 | 测试用例 | 降级逻辑验证 |
| 案例 5 | 测试用例 | 深度搜索验证 |
| 案例 6 | 测试用例 | 错误处理验证 |
