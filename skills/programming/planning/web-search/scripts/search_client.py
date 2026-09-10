#!/usr/bin/env python3
"""web-search — 免费网络搜索引擎客户端

支持 SearXNG（首选）和 DuckDuckGo（兜底）两个免费引擎。
无需 API Key，直接调用公共搜索服务。
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

# ── 搜索引擎实例 ───────────────────────────────────────────

SEARXNG_INSTANCES = [
    "https://search.sapti.me",
    "https://searx.be",
    "https://search.ononoki.org",
    "https://searx.tiekoetter.com",
]

CACHE_DIR = "."
CACHE_TTL = 86400  # 24 小时


# ── 缓存管理 ───────────────────────────────────────────────

def get_cache_path(query: str) -> str:
    """获取缓存文件路径"""
    cache_key = hashlib.md5(query.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"_search_cache_{cache_key}.json")


def load_cache(query: str) -> Optional[List[Dict]]:
    """加载搜索结果缓存"""
    cache_path = get_cache_path(query)
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, encoding="utf-8") as f:
            cache = json.load(f)
        
        # 检查过期时间
        if time.time() - cache.get("timestamp", 0) > CACHE_TTL:
            return None
        
        return cache.get("results", [])
    except (json.JSONDecodeError, IOError):
        return None


def save_cache(query: str, results: List[Dict]):
    """保存搜索结果到缓存"""
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


# ── SearXNG 搜索 ───────────────────────────────────────────

def search_searxng(query: str, language: str = "zh", region: str = "cn") -> List[Dict]:
    """
    使用 SearXNG 公共实例搜索
    
    SearXNG 是开源元搜索引擎，聚合多个引擎结果。
    公共实例可能有速率限制，建议本地部署。
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
    
    raise SearchEngineError(f"SearXNG 所有实例失败: {last_error}")


def parse_searxng_results(data: Dict) -> List[Dict]:
    """解析 SearXNG JSON 结果"""
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


# ── DuckDuckGo 搜索 ─────────────────────────────────────────

def search_ddg(query: str) -> List[Dict]:
    """
    使用 DuckDuckGo HTML 抓取搜索
    
    DuckDuckGo 不提供官方 API，通过 HTML 页面解析结果。
    """
    import httpx
    
    url = "https://html.duckduckgo.com/html/"
    data = {"q": query, "kl": "cn-cn"}
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
        raise SearchEngineError(f"DuckDuckGo 搜索失败: {e}")


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
            url = url_el.get("href", "")
            # 清理 DuckDuckGo 重定向 URL
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


# ── Brave Search ───────────────────────────────────────────

def search_brave(query: str, api_key: Optional[str] = None) -> List[Dict]:
    """
    使用 Brave Search API（可选）
    
    Brave 提供免费的搜索 API，但需要注册获取 API Key。
    免费版有 2000 次/月限制。
    """
    import httpx
    
    if not api_key:
        api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        raise SearchEngineError("Brave Search 需要 API Key，设置 BRAVE_API_KEY 环境变量")
    
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
        raise SearchEngineError(f"Brave Search 失败: {e}")


def parse_brave_results(data: Dict) -> List[Dict]:
    """解析 Brave Search JSON 结果"""
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


# ── 统一搜索接口 ───────────────────────────────────────────

class SearchEngineError(Exception):
    """搜索引擎错误"""
    pass


def search(
    query: str,
    engine: str = "searxng",
    language: str = "zh",
    max_results: int = 10,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    统一搜索接口
    
    Args:
        query: 搜索查询
        engine: 搜索引擎 (searxng/ddg/brave)
        language: 语言代码
        max_results: 最大结果数
        use_cache: 是否使用缓存
    
    Returns:
        搜索结果字典
    """
    start_time = time.time()
    
    # 检查缓存
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
    
    # 执行搜索
    search_func = {
        "searxng": search_searxng,
        "ddg": search_ddg,
        "brave": search_brave,
    }.get(engine, search_searxng)
    
    try:
        results = search_func(query, language)
    except SearchEngineError as e:
        # 自动降级
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
    
    # 限制结果数量
    results = results[:max_results]
    
    # 保存缓存
    save_cache(query, results)
    
    return {
        "query": query,
        "total_results": len(results),
        "search_time_ms": int((time.time() - start_time) * 1000),
        "engine": engine,
        "results": results,
        "cached": False,
    }


# ── 多轮搜索 ───────────────────────────────────────────────

def deep_search(
    query: str,
    max_rounds: int = 3,
    engine: str = "searxng",
) -> Dict[str, Any]:
    """
    多轮深度搜索
    
    将复杂查询拆分为多个子查询，并行搜索后汇总。
    """
    all_results = []
    
    # 第 1 轮：基础搜索
    round_1 = search(query, engine=engine)
    all_results.extend(round_1.get("results", []))
    
    if max_rounds == 1:
        return summarize_results(query, all_results)
    
    # 后续轮次：基于已有结果深入
    for i in range(2, max_rounds + 1):
        # 简单的子查询生成（实际应使用 LLM）
        follow_up_queries = generate_follow_up_queries(query, all_results)
        
        if not follow_up_queries:
            break
        
        for sub_query in follow_up_queries[:3]:  # 最多 3 个子查询
            sub_results = search(sub_query, engine=engine)
            all_results.extend(sub_results.get("results", []))
    
    return summarize_results(query, all_results)


def generate_follow_up_queries(original_query: str, results: List[Dict]) -> List[str]:
    """生成后续搜索查询（简化版）"""
    queries = []
    
    # 从结果中提取关键词
    for result in results[:3]:
        title = result.get("title", "")
        # 简单提取名词短语
        words = title.split()
        if len(words) >= 2:
            queries.append(f"{original_query} {words[-1]}")
    
    return queries[:3]


def summarize_results(query: str, results: List[Dict]) -> Dict[str, Any]:
    """汇总搜索结果"""
    # 去重
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


# ── 渲染器 ───────────────────────────────────────────────

def render_markdown(result: Dict) -> str:
    """渲染 Markdown 格式"""
    lines = [
        f"# 搜索结果：{result.get('query', '')}",
        f"",
        f"**引擎：** {result.get('engine', 'unknown')}",
        f"**耗时：** {result.get('search_time_ms', 0)}ms",
        f"**结果数：** {result.get('total_results', 0)}",
        f"",
    ]
    
    if result.get("cached"):
        lines.append("*（来自缓存）*")
        lines.append("")
    
    if "error" in result:
        lines.append(f"⚠️ **错误：** {result['error']}")
        lines.append("")
        return "\n".join(lines)
    
    for i, r in enumerate(result.get("results", []), 1):
        lines.append(f"## {i}. {r.get('title', '无标题')}")
        lines.append(f"**URL:** {r.get('url', '')}")
        content = r.get("content", "")
        if content:
            lines.append(f"> {content[:200]}{'...' if len(content) > 200 else ''}")
        lines.append("")
    
    lines.append("---")
    lines.append(f"*由 web-search v1.0 生成*")
    
    return "\n".join(lines)


# ── CLI 入口 ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Web Search — 免费搜索引擎客户端")
    parser.add_argument("query", nargs="?", help="搜索查询")
    parser.add_argument("--engine", "-e", choices=["searxng", "ddg", "brave"], default="searxng")
    parser.add_argument("--language", "-l", default="zh")
    parser.add_argument("--max-results", "-m", type=int, default=10)
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    parser.add_argument("--deep", "-d", action="store_true", help="多轮深度搜索")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="深度搜索轮次")
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    # 执行搜索
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
    
    # 输出
    if args.format == "markdown":
        print(render_markdown(result))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
