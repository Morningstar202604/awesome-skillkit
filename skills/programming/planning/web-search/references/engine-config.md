# Search Engine Configuration Guide

## Table of Contents

- [SearXNG](#searxng)
  - [Public instance list](#public-instance-list)
  - [Self-hosted instance (recommended for production)](#self-hosted-instance-recommended-for-production)
  - [Configuration parameters](#configuration-parameters)
- [DuckDuckGo](#duckduckgo)
  - [HTML scraping limits](#html-scraping-limits)
  - [Result parsing notes](#result-parsing-notes)
- [Brave Search](#brave-search)
  - [Free quota](#free-quota)
  - [Registration flow](#registration-flow)
  - [Limits](#limits)
- [Error-handling strategy](#error-handling-strategy)
- [Performance optimization](#performance-optimization)

## SearXNG

### Public instance list

| Instance | URL | Status | Notes |
|------|-----|------|------|
| Sapti | https://search.sapti.me | ✅ stable | Recommended first choice |
| searx.be | https://searx.be | ⚠️ intermittent | German instance |
| Ononoki | https://search.ononoki.org | ✅ stable | Japanese instance |
| Tiekoetter | https://searx.tiekoetter.com | ⚠️ intermittent | European instance |

### Self-hosted instance (recommended for production)

```bash
# One-command Docker deploy
docker run -d -p 8080:8080 searxng/searxng

# Or manual deploy
git clone https://github.com/searxng/searxng
cd searxng
pip install -r requirements.txt
python searx/webapp.py
```

Advantages of a self-hosted instance:
- No rate limits
- Configurable engines
- Privacy fully under your control

### Configuration parameters

```yaml
general:
  debug: false
  instance_name: "SearXNG"
  
search:
  safe_search: 0  # 0=off, 1=moderate, 2=strict
  autocomplete: "google"
  default_lang: "auto"
  
engines:
  - name: google
    enabled: true
  - name: bing
    enabled: true
  - name: duckduckgo
    enabled: true
  - name: github
    enabled: true
```

---

## DuckDuckGo

### HTML scraping limits

- Anti-scraping: too many consecutive requests return a CAPTCHA
- Recommendation: ≥1 second between searches
- Recommendation: use a proxy pool to spread requests

### Result parsing notes

DuckDuckGo HTML structure:
```html
<div class="result">
  <a class="result__a" href="...">title</a>
  <div class="result__url">url</div>
  <div class="result__snippet">snippet</div>
</div>
```

Redirect URL handling:
```
raw: https://duckduckgo.com/l/?uddg=https://example.com/
parsed: https://example.com/
```

---

## Brave Search

### Free quota

- 2,000 queries/month
- Registration required to get an API key

### Registration flow

1. Visit https://brave.com/search/api/
2. Register an account
3. Create an API key
4. Set the environment variable `BRAVE_API_KEY`

### Limits

- Rate limit: 10 requests/second
- At most 50 results per response
- No custom engines

---

## Error-handling strategy

```python
# retry strategy on search failure
def search_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return search_searxng(query)
        except SearchEngineError:
            if attempt == max_retries - 1:
                return search_ddg(query)  # final fallback
            time.sleep(1 * (attempt + 1))  # exponential backoff
```

---

## Performance optimization

| Optimization | Method | Effect |
|--------|------|------|
| Cache | MD5 hash + 24h TTL | Reduces duplicate requests |
| Connection pool | Reuse httpx.Client | Lower latency |
| Parallel search | Concurrent requests across instances | Faster |
| Result dedup | URL hash set | Avoids duplicates |
