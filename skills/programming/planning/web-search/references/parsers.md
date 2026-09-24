# 搜索结果解析器

## Table of Contents

- [SearXNG 解析](#searxng-解析)
  - [JSON 结构](#json-结构)
  - [解析函数](#解析函数)
- [DuckDuckGo 解析](#duckduckgo-解析)
  - [HTML 结构](#html-结构)
  - [解析函数](#解析函数)
- [Brave Search 解析](#brave-search-解析)
  - [JSON 结构](#json-结构)
- [统一输出格式](#统一输出格式)

## SearXNG 解析

### JSON 结构

```json
{
  "results": [
    {
      "title": "页面标题",
      "url": "https://example.com",
      "content": "页面摘要...",
      "engine": "google",
      "engine_id": "",
      "score": 0.95,
      "parsed_url": {
        "scheme": "https",
        "netloc": "example.com",
        "path": "/page"
      }
    }
  ],
  "number_of_results": 123456,
  "query": "search query"
}
```

### 解析函数

```python
def parse_searxng_results(data: Dict) -> List[Dict]:
    results = []
    for item in data.get("results", []):
        url = item.get("url", "")
        parsed = urlparse(url)
        
        results.append({
            "title": item.get("title", ""),
            "url": url,
            "content": item.get("content", ""),
            "engine": item.get("engine", ""),
            "parsed_url": {
                "scheme": parsed.scheme,
                "domain": parsed.netloc,
                "path": parsed.path,
            },
            "score": item.get("score", 0.0),
        })
    return results
```

---

## DuckDuckGo 解析

### HTML 结构

```html
<div class="result">
  <a class="result__a" href="/l/?uddg=https://example.com">
    Page Title
  </a>
  <div class="result__url">
    example.com › path
  </div>
  <div class="result__snippet">
    Page content snippet...
  </div>
</div>
```

### 解析函数

```python
from bs4 import BeautifulSoup
from urllib.parse import unquote

def parse_ddg_html(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    
    for element in soup.select(".result"):
        title_el = element.select_one(".result__a")
        url_el = element.select_one(".result__url")
        snippet_el = element.select_one(".result__snippet")
        
        if title_el and url_el:
            url = url_el.get("href", "")
            
            # 处理 DuckDuckGo 重定向
            if "/l/?uddg=" in url:
                url = unquote(url.split("uddg=")[1].split("&")[0])
            
            results.append({
                "title": title_el.get_text(strip=True),
                "url": url,
                "content": snippet_el.get_text(strip=True) if snippet_el else "",
                "engine": "duckduckgo",
                "score": 0.0,
            })
    
    return results
```

---

## Brave Search 解析

### JSON 结构

```json
{
  "web": {
    "results": [
      {
        "title": "Page Title",
        "url": "https://example.com",
        "description": "Page description...",
        "extra_snippets": []
      }
    ]
  }
}
```

---

## 统一输出格式

所有引擎的输出统一为：

```python
{
    "title": str,           # 页面标题
    "url": str,             # 原始 URL
    "content": str,         # 页面摘要/内容
    "engine": str,          # 来源引擎
    "parsed_url": {         # 解析后的 URL 组件
        "scheme": str,
        "domain": str,
        "path": str,
    },
    "score": float,         # 相关度分数（0-1）
}
```
