#!/usr/bin/env python3
"""web-search -- free web search engine client.

Supports two free engines: SearXNG (preferred) and DuckDuckGo (fallback).
No API key required; calls public search services directly.
"""
import json
import sys
import os
import time
import hashlib
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

# -- Search engine instances --------------------------------------------------

SEARXNG_INSTANCES = [
    "https://search.sapti.me",
    "https://searx.be",
    "https://search.ononoki.org",
    "https://searx.tiekoetter.com",
]

CACHE_DIR = "."
CACHE_TTL = 86400  # 24 hours


# -- Cache management --------------------------------------------------------

def get_cache_path(query: str) -> str:
    """Get the cache file path."""
    cache_key = hashlib.md5(query.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"_search_cache_{cache_key}.json")


def load_cache(query: str) -> Optional[List[Dict]]:
    """Load the search result cache."""
    cache_path = get_cache_path(query)
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        
        # check the expiry time
        if time.time() - cache.get("timestamp", 0) > CACHE_TTL:
            return None
        
        return cache.get("results", [])
    except (json.JSONDecodeError, IOError):
        return None


def save_cache(query: str, results: List[Dict]):
    """Save search results to the cache."""
    cache_path = get_cache_path(query)
    cache_data = {
        "query": query,
        "timestamp": time.time(),
        "results": results,
    }
    
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Warning: Failed to save cache: {e}", file=sys.stderr)


# -- SearXNG search ----------------------------------------------------------

def search_searxng(query: str, language: str = "zh", region: str = "cn") -> List[Dict]:
    """
    Search using public SearXNG instances.

    SearXNG is an open-source metasearch engine that aggregates results from multiple engines.
    Public instances may be rate-limited; a local deployment is recommended.
    """
    import httpx
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    
    last_error = None
    
    for instance in SEARXNG_INSTANCES:
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(
                    f"{instance}/search",
                    params={
                        "q": query,
                        "language": language,
                        "format": "json",
                    },
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
                results = parse_searxng_results(data)
                if results:
                    return results
        except Exception as e:
            last_error = e
            continue
    
    raise SearchEngineError(f"All SearXNG instances failed: {last_error}")


def parse_searxng_results(data: Dict) -> List[Dict]:
    """Parse SearXNG JSON results."""
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
    
    return results[:10]


# -- DuckDuckGo search -------------------------------------------------------

def search_ddg(query: str, language: str = "zh") -> List[Dict]:
    """
    Search by scraping DuckDuckGo HTML.

    DuckDuckGo offers no official API; results are parsed from the HTML page.
    language maps to the region parameter (kl): zh->cn-cn, en->wt-wt, otherwise lowercased as-is.
    """
    import httpx

    region_map = {"zh": "cn-cn", "en": "wt-wt"}
    region = region_map.get((language or "").lower(), (language or "cn-cn").lower().replace("_", "-"))
    url = "https://html.duckduckgo.com/html/"
    data = {"q": query, "kl": region}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, data=data, headers=headers)
            resp.raise_for_status()
            return parse_ddg_html(resp.text)
    except Exception as e:
        raise SearchEngineError(f"DuckDuckGo search failed: {e}")


def parse_ddg_html(html: str) -> List[Dict]:
    """Parse DuckDuckGo HTML results."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # DuckDuckGo result selectors
    for element in soup.select(".result"):
        title_el = element.select_one(".result__a")
        url_el = element.select_one(".result__url")
        snippet_el = element.select_one(".result__snippet")

        if title_el and url_el:
            url = url_el.get("href", "")
            # clean the DuckDuckGo redirect URL
            if "/l/?uddg=" in url:
                from urllib.parse import unquote
                url = unquote(url.split("uddg=")[1].split("&uddg=")[0])
            
            parsed = urlparse(url)
            results.append({
                "title": title_el.get_text(strip=True),
                "url": url,
                "content": snippet_el.get_text(strip=True) if snippet_el else "",
                "engine": "duckduckgo",
                "parsed_url": {
                    "scheme": parsed.scheme,
                    "domain": parsed.netloc,
                    "path": parsed.path,
                },
                "score": 0.0,
            })
    
    return results[:10]


# -- Brave Search ------------------------------------------------------------

def search_brave(query: str, api_key: Optional[str] = None) -> List[Dict]:
    """
    Use the Brave Search API (optional).

    Brave offers a free search API but requires registration for an API key.
    The free tier has a limit of 2000 queries/month.
    """
    import httpx

    if not api_key:
        api_key = os.getenv("BRAVE_API_KEY")

    if not api_key:
        raise SearchEngineError("Brave Search requires an API key; set the BRAVE_API_KEY environment variable")
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": 10},
                headers=headers,
            )
            resp.raise_for_status()
            return parse_brave_results(resp.json())
    except Exception as e:
        raise SearchEngineError(f"Brave Search failed: {e}")


def parse_brave_results(data: Dict) -> List[Dict]:
    """Parse Brave Search JSON results."""
    results = []
    
    for item in data.get("web", {}).get("results", []):
        url = item.get("url", "")
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        results.append({
            "title": item.get("title", ""),
            "url": url,
            "content": item.get("description", ""),
            "engine": "brave",
            "parsed_url": {
                "scheme": parsed.scheme,
                "domain": parsed.netloc,
                "path": parsed.path,
            },
            "score": 0.0,
        })
    
    return results[:10]


# -- Unified search interface ------------------------------------------------

class SearchEngineError(Exception):
    """Search engine error."""
    pass


def search(
    query: str,
    engine: str = "searxng",
    language: str = "zh",
    max_results: int = 10,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Unified search interface.

    Args:
        query: the search query
        engine: search engine (searxng/ddg/brave)
        language: language code
        max_results: maximum number of results
        use_cache: whether to use the cache

    Returns:
        a search-results dict
    """
    start_time = time.time()

    # check the cache
    if use_cache:
        cached = load_cache(query)
        if cached:
            return {
                "query": query,
                "total_results": len(cached),
                "search_time_ms": int((time.time() - start_time) * 1000),
                "engine": "cache",
                "results": cached,
                "cached": True,
            }
    
    # run the search
    search_func = {
        "searxng": search_searxng,
        "ddg": search_ddg,
        "brave": search_brave,
    }.get(engine, search_searxng)

    try:
        results = search_func(query, language)
    except SearchEngineError as e:
        # auto-fallback
        if engine == "searxng":
            try:
                results = search_ddg(query)
            except SearchEngineError:
                return {
                    "query": query,
                    "error": str(e),
                    "results": [],
                    "total_results": 0,
                }
        else:
            return {
                "query": query,
                "error": str(e),
                "results": [],
                "total_results": 0,
            }
    
    # cap the number of results
    results = results[:max_results]

    # save the cache
    save_cache(query, results)
    
    return {
        "query": query,
        "total_results": len(results),
        "search_time_ms": int((time.time() - start_time) * 1000),
        "engine": engine,
        "results": results,
        "cached": False,
    }


# -- Multi-round search ------------------------------------------------------

def deep_search(
    query: str,
    max_rounds: int = 3,
    engine: str = "searxng",
) -> Dict[str, Any]:
    """
    Multi-round deep search.

    Splits a complex query into sub-queries, searches them in parallel, and aggregates.
    """
    all_results = []

    # round 1: base search
    round_1 = search(query, engine=engine)
    all_results.extend(round_1.get("results", []))

    if max_rounds == 1:
        return summarize_results(query, all_results)

    # later rounds: go deeper based on existing results
    for i in range(2, max_rounds + 1):
        # simple sub-query generation (in practice an LLM should be used)
        follow_up_queries = generate_follow_up_queries(query, all_results)

        if not follow_up_queries:
            break

        for sub_query in follow_up_queries[:3]:  # at most 3 sub-queries
            sub_results = search(sub_query, engine=engine)
            all_results.extend(sub_results.get("results", []))

    return summarize_results(query, all_results)


def generate_follow_up_queries(original_query: str, results: List[Dict]) -> List[str]:
    """Generate follow-up search queries (simplified version)."""
    queries = []

    # extract keywords from results
    for result in results[:3]:
        title = result.get("title", "")
        # simple noun-phrase extraction
        words = title.split()
        if len(words) >= 2:
            queries.append(f"{original_query} {words[-1]}")

    return queries[:3]


def summarize_results(query: str, results: List[Dict]) -> Dict[str, Any]:
    """Aggregate search results."""
    # de-duplicate
    seen_urls = set()
    unique_results = []
    for r in results:
        url = r.get("url", "")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)
    
    return {
        "query": query,
        "total_results": len(unique_results),
        "results": unique_results,
    }


# -- Renderer ----------------------------------------------------------------

def render_markdown(result: Dict) -> str:
    """Render in Markdown."""
    lines = [
        f"# Search results: {result.get('query', '')}",
        f"",
        f"**Engine:** {result.get('engine', 'unknown')}",
        f"**Elapsed:** {result.get('search_time_ms', 0)}ms",
        f"**Results:** {result.get('total_results', 0)}",
        f"",
    ]

    if result.get("cached"):
        lines.append("*(from cache)*")
        lines.append("")

    if "error" in result:
        lines.append(f"⚠️ **Error:** {result['error']}")
        lines.append("")
        return "\n".join(lines)

    for i, r in enumerate(result.get("results", []), 1):
        lines.append(f"## {i}. {r.get('title', 'Untitled')}")
        lines.append(f"**URL:** {r.get('url', '')}")
        content = r.get("content", "")
        if content:
            lines.append(f"> {content[:200]}{'...' if len(content) > 200 else ''}")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by web-search v1.0*")

    return "\n".join(lines)


# -- CLI entry point ---------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Web Search -- free search engine client")
    parser.add_argument("query", nargs="?", help="search query")
    parser.add_argument("--engine", "-e", choices=["searxng", "ddg", "brave"], default="searxng")
    parser.add_argument("--language", "-l", default="zh")
    parser.add_argument("--max-results", "-m", type=int, default=10)
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--no-cache", action="store_true", help="disable the cache")
    parser.add_argument("--deep", "-d", action="store_true", help="multi-round deep search")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="deep-search rounds")

    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        sys.exit(1)

    # run the search
    if args.deep:
        result = deep_search(args.query, max_rounds=args.rounds, engine=args.engine)
    else:
        result = search(
            args.query,
            engine=args.engine,
            language=args.language,
            max_results=args.max_results,
            use_cache=not args.no_cache,
        )
    
    # output
    if args.format == "markdown":
        print(render_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
