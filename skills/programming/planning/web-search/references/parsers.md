# Search Result Parsers

## Table of Contents

- [SearXNG parsing](#searxng-parsing)
  - [JSON structure](#json-structure)
  - [Parser function](#parser-function)
- [DuckDuckGo parsing](#duckduckgo-parsing)
  - [HTML structure](#html-structure)
  - [Parser function](#parser-function)
- [Brave Search parsing](#brave-search-parsing)
  - [JSON structure](#json-structure)
- [Unified output format](#unified-output-format)

## SearXNG parsing

### JSON structure

```json
{
  "results": [
    {
      "title": "page title",
      "url": "https://example.com",
      "content": "page snippet...",
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

### Parser function

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

## DuckDuckGo parsing

### HTML structure

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

### Parser function

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
            
            # handle DuckDuckGo redirects
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

## Brave Search parsing

### JSON structure

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

## Unified output format

All engines output a unified format:

```python
{
    "title": str,           # page title
    "url": str,             # raw URL
    "content": str,         # page snippet/content
    "engine": str,          # source engine
    "parsed_url": {         # parsed URL components
        "scheme": str,
        "domain": str,
        "path": str,
    },
    "score": float,         # relevance score (0-1)
}
```
