# 搜索引擎配置详解

## SearXNG

### 公共实例列表

| 实例 | URL | 状态 | 备注 |
|------|-----|------|------|
| Sapti | https://search.sapti.me | ✅ 稳定 | 推荐首选 |
| searx.be | https://searx.be | ⚠️ 间歇 | 德国实例 |
| Ononoki | https://search.ononoki.org | ✅ 稳定 | 日本实例 |
| Tiekoetter | https://searx.tiekoetter.com | ⚠️ 间歇 | 欧洲实例 |

### 自建实例（推荐生产环境）

```bash
# Docker 一键部署
docker run -d -p 8080:8080 searxng/searxng

# 或手动部署
git clone https://github.com/searxng/searxng
cd searxng
pip install -r requirements.txt
python searx/webapp.py
```

自建实例优势：
- 无速率限制
- 可配置搜索引擎
- 隐私完全可控

### 配置参数

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

### HTML 抓取限制

- 反爬机制：连续请求过多会返回 CAPTCHA
- 建议：每次搜索间隔 ≥1 秒
- 建议：使用代理池分散请求

### 结果解析要点

DuckDuckGo HTML 结构：
```html
<div class="result">
  <a class="result__a" href="...">标题</a>
  <div class="result__url">url</div>
  <div class="result__snippet">摘要</div>
</div>
```

重定向 URL 处理：
```
原始：https://duckduckgo.com/l/?uddg=https://example.com/
解析：https://example.com/
```

---

## Brave Search

### 免费额度

- 2,000 次查询/月
- 需要注册获取 API Key

### 注册流程

1. 访问 https://brave.com/search/api/
2. 注册账号
3. 创建 API Key
4. 设置环境变量 `BRAVE_API_KEY`

### 限制

- 速率限制：10 次/秒
- 每次返回最多 50 条结果
- 不支持自定义搜索引擎

---

## 错误处理策略

```python
# 搜索失败重试策略
def search_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return search_searxng(query)
        except SearchEngineError:
            if attempt == max_retries - 1:
                return search_ddg(query)  # 最终降级
            time.sleep(1 * (attempt + 1))  # 指数退避
```

---

## 性能优化

| 优化项 | 方法 | 效果 |
|--------|------|------|
| 缓存 | MD5 哈希 + 24h TTL | 减少重复请求 |
| 连接池 | httpx.Client 复用 | 降低延迟 |
| 并行搜索 | 多实例并发请求 | 提升速度 |
| 结果去重 | URL 哈希集合 | 避免重复 |
