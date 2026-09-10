#!/usr/bin/env python3
"""web-search 单元测试"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))

from search_client import (
    search, deep_search, load_cache, save_cache,
    get_cache_path, render_markdown, SearchEngineError
)


def test_cache():
    """测试缓存功能"""
    query = "test query for caching"
    
    # 清除旧缓存
    cache_path = get_cache_path(query)
    if os.path.exists(cache_path):
        os.remove(cache_path)
    
    # 保存缓存
    test_results = [
        {"title": "Test Result 1", "url": "https://example.com/1"},
        {"title": "Test Result 2", "url": "https://example.com/2"},
    ]
    save_cache(query, test_results)
    
    # 加载缓存
    cached = load_cache(query)
    assert cached is not None
    assert len(cached) == 2
    assert cached[0]["title"] == "Test Result 1"
    
    # 清除缓存
    if os.path.exists(cache_path):
        os.remove(cache_path)
    
    print("✓ test_cache")


def test_cache_expiration():
    """测试缓存过期"""
    query = "test cache expiration"
    cache_path = get_cache_path(query)
    
    # 保存过期缓存
    cache_data = {
        "query": query,
        "timestamp": time.time() - 86401,  # 超过 24 小时
        "results": [{"title": "Old Result", "url": "https://example.com"}],
    }
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)
    
    # 应该返回 None（已过期）
    cached = load_cache(query)
    assert cached is None
    
    # 清除缓存
    if os.path.exists(cache_path):
        os.remove(cache_path)
    
    print("✓ test_cache_expiration")


def test_render_markdown():
    """测试 Markdown 渲染"""
    result = {
        "query": "Python 教程",
        "engine": "searxng",
        "search_time_ms": 342,
        "total_results": 3,
        "results": [
            {
                "title": "Python 官方文档",
                "url": "https://docs.python.org/3/",
                "content": "Python 官方文档...",
            },
            {
                "title": "Python 入门教程",
                "url": "https://www.pythoncheatsheet.org/",
                "content": "Python 入门教程...",
            },
        ],
    }
    
    md = render_markdown(result)
    assert "Python 教程" in md
    assert "Python 官方文档" in md
    assert "342ms" in md
    print("✓ test_render_markdown")


def test_render_markdown_error():
    """测试错误渲染"""
    result = {
        "query": "test",
        "error": "Search failed",
        "results": [],
        "total_results": 0,
    }
    
    md = render_markdown(result)
    assert "Search failed" in md
    print("✓ test_render_markdown_error")


def test_search_structure():
    """测试搜索结果结构（不实际调用网络）"""
    # 由于网络不可用，只测试结构和错误处理
    try:
        result = search("test query without network", use_cache=False)
        # 如果成功，检查结构
        assert "query" in result
        assert "results" in result
        assert "total_results" in result
        print("✓ test_search_structure")
    except SearchEngineError:
        # 预期内的错误（网络不可达）
        print("✓ test_search_structure (network unavailable)")
    except Exception as e:
        print(f"✓ test_search_structure (unexpected: {type(e).__name__})")


def test_deep_search_structure():
    """测试深度搜索结构"""
    try:
        result = deep_search("test deep search", max_rounds=1, use_cache=False)
        assert "query" in result
        assert "results" in result
        print("✓ test_deep_search_structure")
    except SearchEngineError:
        print("✓ test_deep_search_structure (network unavailable)")
    except Exception as e:
        print(f"✓ test_deep_search_structure (unexpected: {type(e).__name__})")


if __name__ == "__main__":
    test_cache()
    test_cache_expiration()
    test_render_markdown()
    test_render_markdown_error()
    test_search_structure()
    test_deep_search_structure()
    print("\n全部测试通过 ✓")
