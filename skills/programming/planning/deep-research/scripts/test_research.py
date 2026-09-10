#!/usr/bin/env python3
"""deep-research 单元测试"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from research_agent import QueryAnalyzer, SearchOrchestrator, ReportGenerator


def test_query_analyzer():
    """测试查询分析"""
    analyzer = QueryAnalyzer()
    
    # 简单主题
    result = analyzer.analyze("Python FastAPI")
    assert "sub_queries" in result
    assert len(result["sub_queries"]) > 0
    print("✓ test_query_analyzer: simple topic")
    
    # 复杂主题
    result = analyzer.analyze("FastAPI 和 Flask 对比 2024 最佳实践")
    assert "sub_queries" in result
    assert any("2024" in q for q in result["sub_queries"])
    print("✓ test_query_analyzer: complex topic")
    
    # 英文主题
    result = analyzer.analyze("Python best practices 2024")
    assert "sub_queries" in result
    print("✓ test_query_analyzer: english topic")


def test_report_generator():
    """测试报告生成"""
    reporter = ReportGenerator()
    
    research = {
        "topic": "Test Topic",
        "total_queries": 5,
        "total_results": 10,
        "deduped_results": 8,
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "Test content",
                "engine": "searxng",
                "parsed_url": {"domain": "example.com"},
                "quality_score": 0.9,
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "content": "More content",
                "engine": "ddg",
                "parsed_url": {"domain": "example.com"},
                "quality_score": 0.8,
            },
        ],
        "trust_scores": {
            "https://example.com/1": 0.9,
            "https://example.com/2": 0.8,
        },
        "analysis": {"strategy": "standard"},
    }
    
    # Markdown 报告
    md = reporter.generate_markdown(research)
    assert "Test Topic" in md
    assert "Test Result 1" in md
    assert "⭐" in md  # 可信度星标
    print("✓ test_report_generator: markdown")
    
    # JSON 报告
    js = reporter.generate_json(research)
    parsed = json.loads(js)
    assert parsed["topic"] == "Test Topic"
    print("✓ test_report_generator: json")


def test_orchestrator_no_network():
    """测试无网络环境下的编排器"""
    orchestrator = SearchOrchestrator()
    
    # 由于没有 web-search，应该返回错误
    result = orchestrator.search("test topic", max_rounds=1)
    assert "error" in result or "results" in result
    print("✓ test_orchestrator_no_network")


def test_deduplication():
    """测试去重"""
    orchestrator = SearchOrchestrator()
    
    results = [
        {"url": "https://example.com/1", "title": "A"},
        {"url": "https://example.com/1", "title": "A"},  # 重复
        {"url": "https://example.com/2", "title": "B"},
    ]
    
    deduped = orchestrator._deduplicate(results)
    assert len(deduped) == 2
    print("✓ test_deduplication")


def test_quality_scoring():
    """测试质量评分"""
    orchestrator = SearchOrchestrator()
    
    result = {
        "url": "https://docs.python.org/3/",
        "title": "Python Documentation - The Official Python Language Reference",
        "content": "This is the official Python documentation. It contains comprehensive information about the Python programming language, its standard library, and best practices for using Python in production environments...",
        "engine": "google",
        "parsed_url": {"domain": "docs.python.org"},
    }
    
    score = orchestrator._calculate_quality_score(result)
    assert 0 <= score <= 1
    # 官方文档 + 完整内容应该得分较高
    assert score > 0.75, f"Expected > 0.75, got {score}"
    print(f"✓ test_quality_scoring: {score:.2f}")


if __name__ == "__main__":
    test_query_analyzer()
    test_report_generator()
    test_orchestrator_no_network()
    test_deduplication()
    test_quality_scoring()
    print("\n全部测试通过 ✓")
