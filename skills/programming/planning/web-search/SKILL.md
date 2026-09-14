---
name: web-search
description: "Free web search via SearXNG (primary) and DuckDuckGo (fallback) with no API keys required. Auto-fallback, 24h cache, deep search mode. Use when the agent needs to find information from the web without paid API keys. 当用户要求 搜索 / 查资料 / 联网找信息 时使用。"
license: Apache-2.0
compatibility: Requires network access. No API keys required.
metadata:
  version: "1.0"
  author: awesome-skillkit
  category: planning
  pattern: web-search
  tier: powerful
  verified-date: "2026-09-09"
---

# Web Search — 免费网络搜索引擎

使用免费搜索引擎查询网络信息。无需 API Key，直接调用公共搜索服务。

## 搜索引擎

| 引擎 | 类型 | 稳定性 | 速率限制 | 推荐场景 |
|------|------|--------|----------|----------|
| **SearXNG** | 聚合引擎 | ⭐⭐⭐ | 中等 | 首选，聚合多引擎 |
| **DuckDuckGo** | HTML 抓取 | ⭐⭐ | 严格 | 兜底，反爬强 |
| **Brave Search** | JSON API | ⭐⭐⭐ | 宽松 | 可选，需注册 |

---

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| query | 是 | 搜索关键词 |
| engine | 否 | 搜索引擎：`searxng` / `ddg` / `brave` | searxng |
| language | 否 | 语言代码：`zh` / `en` / `ja` | zh |
| region | 否 | 地区代码：`cn` / `us` / `jp` | 默认 |
| max_results | 否 | 最大返回结果数 | 10 |
| use_cache | 否 | 是否使用缓存 | true |

缺失时询问模板：「请提供：① 搜索内容。其余我将使用默认值。」

---

## 工作流程

### 步骤 1：查询预处理

```python
def preprocess_query(query: str) -> str:
    """搜索查询预处理"""
    # 1. 去除多余空格
    query = " ".join(query.split())
    
    # 2. 中英文混合优化
    # 中文查询添加空格分隔关键词
    if any('\u4e00' <= c <= '\u9fff' for c in query):
        query = optimize_chinese_query(query)
    
    # 3. 长度限制（搜索引擎通常限制 200 字符）
    if len(query) > 200:
        query = query[:200].rsplit(' ', 1)[0]
    
    return query
```

### 步骤 2：缓存检查

```python
def check_cache(query: str) -> Optional[List[Dict]]:
    """检查搜索结果缓存"""
    cache_key = hash(query)
    cache_path = f"_search_cache_{cache_key}.json"
    
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        
        # 缓存有效期：24 小时
        if time.time() - cache["timestamp"] < 86400:
            return cache["results"]
    
    return None
```

### 步骤 3：搜索引擎选择

```python
def select_engine(engine: str, query: str) -> Callable:
    """根据引擎选择搜索函数"""
    engines = {
        "searxng": search_searxng,
        "ddg": search_ddg,
        "brave": search_brave,
    }
    
    # 默认尝试 SearXNG，失败自动降级
    preferred = engines.get(engine, search_searxng)
    
    def search_with_fallback(q):
        try:
            return preferred(q)
        except Exception:
            # 降级到 DuckDuckGo
            return search_ddg(q)
    
    return search_with_fallback
```

### 步骤 4：执行搜索

```python
def search_searxng(query: str, language: str = "zh", region: str = "cn") -> List[Dict]:
    """
    使用 SearXNG 公共实例搜索
    
    SearXNG 是一个开源的元搜索引擎，聚合多个引擎的结果。
    公共实例：https://searx.be, https://search.sapti.me
    """
    import httpx
    
    # 公共实例列表（按稳定性排序）
    instances = [
        "https://search.sapti.me",
        "https://searx.be",
        "https://search.ononoki.org",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    
    for instance in instances:
        try:
            resp = httpx.get(
                f"{instance}/search",
                params={
                    "q": query,
                    "language": language,
                    "format": "json",
                },
                headers=headers,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return parse_searxng_results(data)
        except Exception:
            continue  # 尝试下一个实例
    
    raise SearchEngineError("所有 SearXNG 实例不可用")


def search_ddg(query: str) -> List[Dict]:
    """
    使用 DuckDuckGo HTML 抓取搜索
    
    DuckDuckGo 不提供官方 API，直接请求 HTML 页面解析结果。
    """
    import requests
    
    url = "https://html.duckduckgo.com/html/"
    data = {"q": query, "kl": "cn-cn"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36"
    }
    
    resp = requests.post(url, data=data, headers=headers, timeout=15)
    resp.raise_for_status()
    
    return parse_ddg_html(resp.text)
```

### 步骤 5：结果解析

```python
def parse_searxng_results(data: Dict) -> List[Dict]:
    """解析 SearXNG JSON 结果"""
    results = []
    
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "engine": item.get("engine", ""),
            "parsed_url": parse_url(item.get("url", "")),
            "score": item.get("score", 0.0),
        })
    
    return results[:10]  # 限制返回数量


def parse_ddg_html(html: str) -> List[Dict]:
    """解析 DuckDuckGo HTML 结果"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    # DuckDuckGo 结果选择器
    for element in soup.select(".result"):
        title_el = element.select_one(".result__a")
        url_el = element.select_one(".result__url")
        snippet_el = element.select_one(".result__snippet")
        
        if title_el and url_el:
            results.append({
                "title": title_el.get_text(strip=True),
                "url": url_el.get("href", ""),
                "content": snippet_el.get_text(strip=True) if snippet_el else "",
                "engine": "duckduckgo",
                "parsed_url": parse_url(url_el.get("href", "")),
                "score": 0.0,
            })
    
    return results[:10]
```

### 步骤 6：缓存保存

```python
def save_cache(query: str, results: List[Dict]):
    """保存搜索结果到缓存"""
    cache_key = hash(query)
    cache_path = f"_search_cache_{cache_key}.json"
    
    cache_data = {
        "query": query,
        "timestamp": time.time(),
        "results": results,
    }
    
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)
```

---

## 多轮搜索（Deep Search）

支持将复杂查询拆分为多个子查询，并行搜索后汇总。

```python
def deep_search(query: str, max_rounds: int = 3) -> Dict:
    """
    多轮深度搜索
    
    流程：
    1. 分析查询，拆分子问题
    2. 并行搜索每个子问题
    3. 汇总结果，去重排序
    4. 如有需要，继续下一轮搜索
    """
    # 第 1 轮：基础搜索
    round_1 = search(query)
    
    if max_rounds == 1:
        return summarize_results(round_1)
    
    # 分析是否需要深入
    follow_ups = analyze_follow_up(query, round_1)
    
    # 后续轮次
    all_results = round_1
    for i, sub_query in enumerate(follow_ups[:max_rounds - 1], 2):
        sub_results = search(sub_query)
        all_results = merge_results(all_results, sub_results)
    
    return summarize_results(all_results)
```

---

## 输出格式

### JSON 格式

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
      "content": "FastAPI is a modern, fast web framework for building APIs with Python...",
      "domain": "fastapi.tiangolo.com",
      "score": 0.95
    }
  ],
  "follow_up_suggestions": [
    "FastAPI vs Flask comparison",
    "FastAPI async best practices"
  ]
}
```

### Markdown 格式

```markdown
# 搜索结果：Python FastAPI 最佳实践

**引擎：** SearXNG | **耗时：** 342ms | **结果数：** 10

---

## 1. FastAPI Documentation
**URL:** https://fastapi.tiangolo.com/
> FastAPI is a modern, fast web framework for building APIs with Python...

## 2. FastAPI vs Flask
**URL:** https://example.com/fastapi-vs-flask
> Comparison of FastAPI and Flask performance and features...

...
```

---

## 缓存管理

| 命令 | 说明 |
|------|------|
| `_search_cache_*.json` | 搜索结果缓存文件 |
| 缓存有效期 | 24 小时 |
| 缓存键 | query 的哈希值 |
| `.gitignore` | 必须忽略缓存文件 |

---

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| SearXNG 全部超时 | 实例失效 | 自动降级到 DuckDuckGo |
| DuckDuckGo 返回空 | 反爬拦截 | 提示用户手动搜索 |
| 结果格式错误 | 引擎更新 | 更新解析逻辑 |
| 网络不可达 | 无网络连接 | 报告错误，建议检查网络 |

---

## 参考

- references/engine-config.md —— 引擎配置详解
- references/parsers.md —— 结果解析器实现
- references/examples.md —— 搜索案例库