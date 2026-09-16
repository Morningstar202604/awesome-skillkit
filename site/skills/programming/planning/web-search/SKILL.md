---
name: web-search
description: "Free web search via SearXNG (primary) and DuckDuckGo (fallback) with no API keys required. Auto-fallback, 24h cache, deep search mode. Use when the agent needs to find information from the web without paid API keys. 当用户要求 搜索 / 查资料 / 联网找信息 时使用。 Do NOT use for multi-source synthesis reports (use deep-research)."
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
所有命令均在技能目录（本文件所在目录）下执行。

## 搜索引擎

| 引擎 | 类型 | 稳定性 | 速率限制 | 推荐场景 |
|------|------|--------|----------|----------|
| **SearXNG** | 聚合引擎 | ★★★ | 中等 | 首选，聚合多引擎 |
| **DuckDuckGo** | HTML 抓取 | ★★ | 严格 | 兜底，反爬强 |
| **Brave Search** | JSON API | ★★★ | 宽松 | 可选，需注册 |

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| query | 是 | 搜索关键词（建议 ≤200 字符，过长会被引擎截断） |
| engine | 否 | 搜索引擎：`searxng` / `ddg` / `brave`（默认 searxng） |
| language | 否 | 语言代码：`zh` / `en` / `ja`（默认 zh） |
| region | 否 | 地区代码：`cn` / `us` / `jp`（默认 kl=cn-cn，仅 DDG 使用） |
| max_results | 否 | 最大返回结果数（默认 10；解析层每引擎也截断为 10 条） |
| use_cache | 否 | 是否使用缓存（默认 true，TTL 24 小时） |

缺失时一次性问齐：「请提供：① 搜索内容。其余我将使用默认值。」

## 前置自检

依次执行；致命项失败 → 修复后 STOP。

```bash
# 1. Python 可用（致命）
python3 --version                                        # 预期：Python 3.x

# 2. HTTP 客户端（致命）
python3 -c "import httpx; print('httpx OK')"             # 预期：httpx OK；失败 → pip install httpx

# 3. HTML 解析（仅 engine=ddg 需要；失败可先用 searxng）
python3 -c "import bs4; print('bs4 OK')"                 # 失败 → pip install beautifulsoup4

# 4. 脚本就位（致命；必须在技能目录执行）
test -f scripts/search_client.py && echo OK              # 预期：OK；失败 → cd 到技能目录
```

- 网络可达：任一公共 SearXNG 实例可达即可；全失败时脚本自动降级 DuckDuckGo。
- 仅 engine=brave 时需要 `BRAVE_API_KEY` 环境变量（凭据只走环境变量，不写入文件或命令行）。

## 参数速查表

`python3 scripts/search_client.py`（run）：

| 参数 | 取值 | 说明 |
|------|------|------|
| query（位置参数） | 搜索词 | 缺省时打印帮助并 exit 1 |
| --engine / -e | searxng / ddg / brave | 默认 searxng |
| --language / -l | 语言代码 | 默认 zh |
| --max-results / -m | 整数 | 默认 10 |
| --format / -f | markdown / json | 默认 markdown |
| --no-cache | 开关 | 跳过缓存读写 |
| --deep / -d | 开关 | 多轮深度搜索 |
| --rounds / -r | 整数 | 深度搜索轮次，默认 3 |

## 工作流

### 步骤 1：执行单次搜索

动作（run）：

```bash
python3 scripts/search_client.py "Python FastAPI 最佳实践" --format json
python3 scripts/search_client.py "Python FastAPI best practices" -e ddg --format json
```

预期：stdout 输出 JSON，含 `query`/`total_results`/`search_time_ms`/`engine`/`results[]`，每条含 `title`/`url`/`content`/`engine`/`parsed_url`/`score`；缓存命中时 `engine=cache` 且 `cached=true`。
若失败：JSON 含 `error` 字段且 `results` 为空（脚本不向 shell 抛异常）→ 查失败处置表。

### 步骤 2：缓存命中检查（脚本自动执行）

动作（read 内部逻辑）：以 `_search_cache_<md5(query)>.json` 为键查当前目录缓存，TTL 24 小时（86400 秒）。
预期：命中则直接返回，`search_time_ms` 接近 0。
若失败（文件损坏/过期）→ 自动当作未命中，重新搜索并覆写。

### 步骤 3：引擎选择与自动降级（脚本自动执行）

- SearXNG：按序尝试公共实例（`https://search.sapti.me`、`https://searx.be`、`https://search.ononoki.org`、`https://searx.tiekoetter.com` — VERIFY BEFORE USE，公共实例可用性随时间变化），请求 `/search?q=<query>&language=<lang>&format=json`，取首个返回非空结果者。
- 自动降级：SearXNG 全失败 → 自动改用 DuckDuckGo（`POST https://html.duckduckgo.com/html/`，表单 `q=<query>&kl=cn-cn`；HTML 选择器解析见 references/parsers.md）。
- Brave：`GET https://api.search.brave.com/res/v1/web/search`，Bearer 鉴权，免费额度 2000 次/月。

预期：`engine` 字段如实反映最终使用的引擎；降级静默完成，不报错。
若失败：两引擎全败 → 返回 `error` 字段（如 `SearXNG 所有实例失败: ...`）。

### 步骤 4：多轮深度搜索（复杂查询）

动作（run）：`python3 scripts/search_client.py "<复杂查询>" --deep --rounds 3 --format json`
预期：第 1 轮基础搜索；后续每轮从已有结果标题提取关键词生成追问（每轮最多 3 个子查询），按 URL 合并去重后输出；无可用追问时提前终止。
若失败：某轮全失败则该轮为空，最终结果可能只有第 1 轮 → 视为部分成功，如实上报。

### 步骤 5：结果落缓存（脚本自动执行）

预期：非缓存结果自动写入 `_search_cache_<md5>.json`（文件含 query/timestamp/results）；缓存文件已被技能目录 `.gitignore` 忽略，不进入版本库。
若失败：缓存写失败仅 stderr 警告（`Warning: Failed to save cache: ...`），不影响搜索结果本身。

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
```

## 缓存管理

| 项 | 说明 |
|------|------|
| `_search_cache_<md5>.json` | 搜索结果缓存文件（键为 query 的 md5） |
| 缓存有效期 | 24 小时（86400 秒） |
| `.gitignore` | 已忽略 `_search_cache_*.json`，缓存不入库 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|------|------|------|
| `SearXNG 所有实例失败: ...` | 公共实例全部失效或被限流 | 脚本已自动降级 DDG；若 DDG 也失败，见下行 |
| `DuckDuckGo 搜索失败: ...` | 反爬拦截或网络不可达 | 检查网络；更换出口 IP 后重试；仍失败 → 建议用户手动搜索 |
| `Brave Search 需要 API Key，设置 BRAVE_API_KEY 环境变量` | 未配置密钥 | `export BRAVE_API_KEY=...` 或改用 searxng/ddg |
| 结果格式错误/持续为空 | 引擎改版 | 更新解析逻辑（见 references/parsers.md），或换 engine 重试 |
| 结果与查询明显无关 | 缓存脏数据 | `--no-cache` 重跑确认，再删除对应缓存文件 |

## 交付标准

- 成功定义：`results[]` 非空且每条含可点击 `url` 与 `title`；完全失败时必须如实返回 `error` 字段，不得编造结果。
- 产物命名：默认输出到 stdout；如需留档，重定向为 `search_<YYYYMMDD>_<slug>.json`。
- 保存位置：当前工作目录；缓存文件 `_search_cache_<md5>.json` 自动落盘，24 小时内同查询直接复用。
- 完整性验证：`python3 scripts/search_client.py "<query>" --format json | python3 -m json.tool` 可解析且 `total_results == len(results)`；引用结果时保留 URL 原文，不改写链接。

## 参考

- references/engine-config.md —— 需要换实例/调超时/配 Brave 额度时读（引擎配置详解）
- references/parsers.md —— 结果解析异常或引擎改版时读（解析器实现与选择器）
- references/gotchas.md —— 结果质量异常时读（常见陷阱）
- references/examples.md —— 校准查询写法时读（搜索案例库）
