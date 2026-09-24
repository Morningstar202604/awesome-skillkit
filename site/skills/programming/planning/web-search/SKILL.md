---
name: web-search
description: "Free web search via SearXNG (primary) and DuckDuckGo (fallback) with no API keys required. Auto-fallback, 24h cache, deep search mode. Use when the agent needs to find information from the web without paid API keys, search the web, look up references, or find information online. Do NOT use for multi-source synthesis reports (use deep-research)."
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

# Web Search — Free Web Search Engine

Query the web using free search engines. No API key required; it calls public search services directly.
All commands are run from the skill directory (the directory containing this file).

## Search Engines

| Engine | Type | Stability | Rate limit | Recommended use |
|------|------|--------|----------|----------|
| **SearXNG** | Aggregator | ★★★ | Medium | Default; aggregates multiple engines |
| **DuckDuckGo** | HTML scraping | ★★ | Strict | Fallback; strong anti-bot |
| **Brave Search** | JSON API | ★★★ | Lenient | Optional; requires registration |

## Input Checklist

| Input | Required | Description |
|------|------|------|
| query | Yes | The search keywords (recommended ≤200 chars; overly long queries are truncated by the engine) |
| engine | No | Search engine: `searxng` / `ddg` / `brave` (default searxng) |
| language | No | Language code: `zh` / `en` / `ja` (default zh) |
| region | No | Region code: `cn` / `us` / `jp` (default kl=cn-cn, DDG only) |
| max_results | No | Max number of results to return (default 10; the parsing layer also truncates to 10 per engine) |
| use_cache | No | Whether to use the cache (default true, TTL 24 hours) |

When missing, ask all at once: "Please provide: (1) what to search for. I'll use defaults for everything else."

## Pre-flight Checks

Run in order; if a fatal item fails → fix it, then STOP.

```bash
# 1. Python available (fatal)
python3 --version                                        # Expected: Python 3.x

# 2. HTTP client (fatal)
python3 -c "import httpx; print('httpx OK')"             # Expected: httpx OK; failure → pip install httpx

# 3. HTML parsing (only needed for engine=ddg; if it fails, use searxng first)
python3 -c "import bs4; print('bs4 OK')"                 # failure → pip install beautifulsoup4

# 4. Script in place (fatal; must run from the skill directory)
test -f scripts/search_client.py && echo OK              # Expected: OK; failure → cd to the skill directory
```

- Network reachability: any public SearXNG instance being reachable is enough; if all fail, the script automatically falls back to DuckDuckGo.
- Only engine=brave needs the `BRAVE_API_KEY` environment variable (credentials go through environment variables only, never into files or the command line).

## Parameter Cheat Sheet

`python3 scripts/search_client.py` (run):

| Parameter | Values | Description |
|------|------|------|
| query (positional) | Search terms | Defaults to printing help and exit 1 |
| --engine / -e | searxng / ddg / brave | Default searxng |
| --language / -l | Language code | Default zh |
| --max-results / -m | integer | Default 10 |
| --format / -f | markdown / json | Default markdown |
| --no-cache | switch | Skip cache read/write |
| --deep / -d | switch | Multi-round deep search |
| --rounds / -r | integer | Deep-search rounds, default 3 |

## Workflow

### Step 1: Run a single search

Action (run):

```bash
python3 scripts/search_client.py "Python FastAPI best practices" --format json
python3 scripts/search_client.py "Python FastAPI best practices" -e ddg --format json
```

Expected: stdout outputs JSON with `query`/`total_results`/`search_time_ms`/`engine`/`results[]`, each entry containing `title`/`url`/`content`/`engine`/`parsed_url`/`score`; on a cache hit, `engine=cache` and `cached=true`.
On failure: the JSON has an `error` field and `results` is empty (the script doesn't throw into the shell) → check the failure-handling table.

### Step 2: Cache-hit check (done automatically by the script)

Action (internal read logic): look up the current-directory cache keyed by `_search_cache_<md5(query)>.json`, TTL 24 hours (86400 seconds).
Expected: on a hit it returns directly, with `search_time_ms` near 0.
On failure (corrupt/expired file) → automatically treat as a miss, re-search, and overwrite.

### Step 3: Engine selection and auto-fallback (done automatically by the script)

- SearXNG: try public instances in order (`https://search.sapti.me`, `https://searx.be`, `https://search.ononoki.org`, `https://searx.tiekoetter.com` — VERIFY BEFORE USE; public-instance availability changes over time), request `/search?q=<query>&language=<lang>&format=json`, taking the first that returns non-empty results.
- Auto-fallback: if all SearXNG instances fail → automatically switch to DuckDuckGo (`POST https://html.duckduckgo.com/html/`, form `q=<query>&kl=cn-cn`; for the HTML selector parsing see references/parsers.md).
- Brave: `GET https://api.search.brave.com/res/v1/web/search`, Bearer auth, free quota 2000 calls/month.

Expected: the `engine` field honestly reflects the engine actually used; the fallback completes silently without error.
On failure: both engines fail → return an `error` field (e.g. `All SearXNG instances failed: ...`).

### Step 4: Multi-round deep search (complex queries)

Action (run): `python3 scripts/search_client.py "<complex query>" --deep --rounds 3 --format json`
Expected: round 1 is the base search; each later round extracts keywords from existing result titles to generate follow-ups (up to 3 sub-queries per round), merges and dedupes by URL, then outputs; terminates early when there are no usable follow-ups.
On failure: if a whole round fails, that round is empty and the final result may only contain round 1 → treat as partial success and report honestly.

### Step 5: Persist results to cache (done automatically by the script)

Expected: non-cached results are automatically written to `_search_cache_<md5>.json` (the file contains query/timestamp/results); cache files are already ignored by the skill directory's `.gitignore` and don't enter version control.
On failure: a cache-write failure is only a stderr warning (`Warning: Failed to save cache: ...`) and doesn't affect the search results themselves.

## Output Formats

### JSON format

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

### Markdown format

```markdown
# Search results: Python FastAPI best practices

**Engine:** SearXNG | **Time:** 342ms | **Results:** 10

---

## 1. FastAPI Documentation
**URL:** https://fastapi.tiangolo.com/
> FastAPI is a modern, fast web framework for building APIs with Python...

## 2. FastAPI vs Flask
**URL:** https://example.com/fastapi-vs-flask
> Comparison of FastAPI and Flask performance and features...
```

## Cache Management

| Item | Description |
|------|------|
| `_search_cache_<md5>.json` | Search-result cache file (keyed by the query's md5) |
| Cache validity | 24 hours (86400 seconds) |
| `.gitignore` | Already ignores `_search_cache_*.json`; caches don't enter the repo |

## Failure Handling Table

| Symptom / error code | Cause | Action |
|------|------|------|
| `All SearXNG instances failed: ...` | All public instances are down or rate-limited | The script already auto-fell back to DDG; if DDG also fails, see the next row |
| `DuckDuckGo search failed: ...` | Anti-bot block or network unreachable | Check the network; retry after changing the egress IP; if it still fails → suggest the user search manually |
| `Brave Search requires an API key; set the BRAVE_API_KEY environment variable` | Key not configured | `export BRAVE_API_KEY=...` or switch to searxng/ddg |
| Result format is wrong / persistently empty | The engine changed its markup | Update the parsing logic (see references/parsers.md), or retry with a different engine |
| Results are clearly unrelated to the query | Dirty cache data | Rerun with `--no-cache` to confirm, then delete the corresponding cache file |

## Delivery Criteria

- Definition of success: `results[]` is non-empty and each entry has a clickable `url` and `title`; on total failure, an `error` field must be returned honestly — results must not be fabricated.
- Artifact naming: output to stdout by default; for archival, redirect to `search_<YYYYMMDD>_<slug>.json`.
- Save location: current working directory; cache file `_search_cache_<md5>.json` persists automatically, and the same query is reused directly within 24 hours.
- Completeness verification: `python3 scripts/search_client.py "<query>" --format json | python3 -m json.tool` parses cleanly and `total_results == len(results)`; when citing results, preserve the original URL verbatim — don't rewrite links.

## References

- references/engine-config.md — read when switching instances / tuning timeouts / configuring Brave quota (detailed engine config)
- references/parsers.md — read when result parsing is abnormal or an engine changes markup (parser implementation and selectors)
- references/gotchas.md — read when result quality is abnormal (common pitfalls)
- references/examples.md — read when calibrating query phrasing (search case library)
