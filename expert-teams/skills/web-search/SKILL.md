---
name: web-search
description: "免费联网搜索规程。当任何团队需要查最新资料、官方文档、报错解法、依赖版本或事实核查时调用。优先使用自建 SearXNG 或 DuckDuckGo 等免费、无需付费 Key 的搜索入口，带本地缓存避免重复抓取，要求交叉验证、标注来源时间，不凭单一来源下结论。支持引擎自动降级、24 小时缓存与多轮深度搜索；触发词：搜索 / 查资料 / 联网找信息。Do NOT use for 多来源综合报告（交给 deep-research）。"
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

# Web Search / 免费联网搜索（SearXNG / DuckDuckGo）

使用免费搜索引擎查询网络信息。无需 API Key，直接调用公共搜索服务；所有命令均在技能目录（本文件所在目录）下执行。本 skill 供**全部团队**共用，目标：在不依赖付费搜索 API 的前提下，稳定拿到最新、可溯源的资料，并通过缓存与交叉验证降低重复请求和错误结论。

## 这是什么

一套「选入口 → 构造查询 → 抓取 → 缓存 → 交叉验证」的搜索作业规范 + 一个可执行客户端。它规定用哪些免费入口、怎么拆关键词、怎么判可信度，以及什么情况下必须打开原文精读而不是只看摘要。

## 何时使用

- 查某个库/框架的最新用法、版本号、Breaking Change。
- 排查报错信息、已知 issue、官方迁移指南。
- 事实核查：政策、价格、API 字段、统计口径。
- 为 deep-research 提供原始素材；agent 需要在没有付费 API Key 的情况下联网找信息。
- 不用于：多来源综合报告（转 `deep-research`）。

## 方法论：核心步骤

1. **选免费入口**：优先自建/可用的 SearXNG 实例；不可用时回退 DuckDuckGo HTML 端点。不强行依赖需要付费 Key 的引擎。
2. **拆关键词**：把自然语言问题拆成 2–4 个核心词组合，英文技术问题用英文查，一次只查一个子问题。
3. **判源分级**：官方文档 / 官方 GitHub > 权威技术媒体 > 高赞社区问答 > 个人博客 > 内容农场。
4. **打开原文**：摘要只够定位；涉及版本号、配置项、报错根因时必须 fetch 原文核对，不抄二手转述。
5. **缓存结果**：同一查询短时间内不重复抓取；把命中的 URL 与结论记入临时缓存，标注抓取时间。
6. **交叉验证**：关键结论至少两个独立来源一致才采纳；冲突时以官方源为准并记录分歧。

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

## 查询构造清单

- [ ] 技术报错：直接用报错原文（去变量值）+ 库名 + 版本号。
- [ ] 查用法：`框架名 + 功能关键词 + 官方文档`，必要时加 `site:github.com`。
- [ ] 查版本：`包名 + changelog / release notes`，锁定最新稳定版而非预发布。
- [ ] 一个查询失败就换关键词同义词，不死磕同一串。
- [ ] 结果过期（>6 个月且涉及快速变动领域）时重查。

## 缓存约定

- 缓存键 = 归一化后的查询词；值 = URL 列表 + 摘要 + 抓取时间戳。
- 脚本落盘缓存（`_search_cache_<md5>.json`）TTL 为 24 小时；在此之内的同查询直接复用原始结果。
- 结论复用策略另按内容时效：技术文档 7 天、时效性新闻 1 天，超过各自时效即使缓存未过期也要重查并重新核实。
- 缓存只存定位信息，不存需要重新核实的结论性数字。

## 缓存管理

| 项 | 说明 |
|------|------|
| `_search_cache_<md5>.json` | 搜索结果缓存文件（键为 query 的 md5） |
| 缓存有效期 | 24 小时（86400 秒） |
| `.gitignore` | 已忽略 `_search_cache_*.json`，缓存不入库 |

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

- `references/engine-config.md` — 需要换实例/调超时/配 Brave 额度时读（引擎配置详解）
- `references/parsers.md` — 结果解析异常或引擎改版时读（解析器实现与选择器）
- `references/gotchas.md` — 结果质量异常时读（常见陷阱）
- `references/examples.md` — 校准查询写法时读（搜索案例库）

## 与其他 skill 的协作

- 单次定位/查文档用本 skill 即可；若需要系统性综述、多轮迭代，转交 `deep-research`。
- 搜索中发现依赖漏洞/可疑密钥时，把线索交给 `security-scan` 进一步确认。
- 搜索结果中的报错解法，落地前仍要在本地复现验证，不直接照搬。

## 易错点

- **只看第一条结果就下结论**：搜索结果排序 ≠ 正确性，尤其报错解法常有多个过时方案。
- **抄博客不验版本**：博客写的是旧版 API，新版已废弃，直接照抄导致报错。必须核对当前版本文档。
- **一次问太宽**：「怎么学机器学习」这种大词搜不到有用结果，要拆成具体子问题。
- **不标时间**：引用了一年前的价格/政策却没说抓取时间，误导决策。
- **重复抓取**：同一问题反复搜，浪费额度且拿到的是同一份二手内容。
- **把搜索结果当交付物**：搜索是手段，最终交付要自己综合、标注来源 URL。
