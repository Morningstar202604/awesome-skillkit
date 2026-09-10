#!/usr/bin/env python3
"""deep-research — 深度调研 Agent

多轮搜索 + 信息综合 + 结构化报告生成。
依赖 web-search skill。
"""
import json
import sys
import os
import re
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse

# 尝试导入 web-search
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web-search", "scripts"))
    from search_client import search, SearchEngineError
except ImportError:
    search = None
    SearchEngineError = Exception


# ── 域名可信度库 ───────────────────────────────────────────

DOMAIN_TRUSTWORTHINESS = {
    # 官方文档
    "docs.python.org": 1.0,
    "fastapi.tiangolo.com": 1.0,
    "flask.palletsprojects.com": 1.0,
    "github.com": 0.9,
    "stackoverflow.com": 0.85,
    
    # 技术博客
    "medium.com": 0.6,
    "dev.to": 0.65,
    "hackernoon.com": 0.55,
    "realpython.com": 0.85,
    "segmentfault.com": 0.7,
    "jianshu.com": 0.5,
    
    # 新闻
    "techcrunch.com": 0.7,
    "thenewstack.io": 0.75,
    
    # 中文技术站
    "cnblogs.com": 0.65,
    "csdn.net": 0.6,
    "juejin.cn": 0.7,
    "oschina.net": 0.7,
    
    # 其他
    "wikipedia.org": 0.8,
    "reddit.com": 0.5,
}


# ── 查询分析器 ───────────────────────────────────────────────

class QueryAnalyzer:
    """分析研究主题，拆解子问题"""
    
    # 模式匹配规则
    PATTERNS = [
        (r"(\w+)和(\w+)", ["对比 {0} 和 {1}", "{0} vs {1}"]),
        (r"最佳(\w+)", ["{0} 最佳实践", "{0} 优缺点", "{0} 比较"]),
        (r"如何(\w+)", ["{0} 方法", "{0} 教程", "{0} 示例"]),
        (r"(\w+)框架", ["{0} 介绍", "{0} 教程", "{0} 最佳实践"]),
    ]
    
    def analyze(self, topic: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """分析查询，返回结构化信息"""
        sub_queries = self._decompose(topic)
        strategy = self._select_strategy(topic, sub_queries)
        
        return {
            "original_topic": topic,
            "sub_queries": sub_queries,
            "strategy": strategy,
            "expected_rounds": self._estimate_rounds(topic),
            "focus_areas": focus_areas or [],
        }
    
    def _decompose(self, topic: str) -> List[str]:
        """拆解子查询"""
        queries = [topic]
        
        for pattern, templates in self.PATTERNS:
            match = re.search(pattern, topic)
            if match:
                for tpl in templates:
                    try:
                        queries.append(tpl.format(*match.groups()))
                    except IndexError:
                        pass
        
        # 添加时间维度
        for year in ["2024", "2025", "2026"]:
            if year not in topic:
                queries.append(f"{topic} {year}")
        
        # 添加英文查询
        queries.append(self._to_english(topic))
        
        # 去重
        return list(dict.fromkeys(queries))[:10]
    
    def _to_english(self, chinese: str) -> str:
        """简单翻译（实际应使用 LLM）"""
        # 常见词汇映射
        translations = {
            "python": "python",
            "fastapi": "fastapi",
            "flask": "flask",
            "django": "django",
            "最佳实践": "best practices",
            "教程": "tutorial",
            "对比": "vs",
            "如何": "how to",
        }
        
        result = chinese
        for cn, en in translations.items():
            result = result.replace(cn, en)
        
        return result if result != chinese else chinese
    
    def _select_strategy(self, topic: str, queries: List[str]) -> Dict:
        """选择搜索策略"""
        is_comparison = any("vs" in q.lower() or "对比" in q for q in queries)
        is_tutorial = any("tutorial" in q.lower() or "教程" in q for q in queries)
        is_news = any(any(y in q for y in ["2024", "2025", "2026"]) for q in queries)
        
        if is_comparison:
            return {"depth": "deep", "engines": ["searxng", "ddg"], "focus": "comparison"}
        elif is_tutorial:
            return {"depth": "standard", "engines": ["searxng"], "focus": "implementation"}
        elif is_news:
            return {"depth": "deep", "engines": ["searxng", "ddg"], "focus": "latest"}
        else:
            return {"depth": "standard", "engines": ["searxng"], "focus": "general"}
    
    def _estimate_rounds(self, topic: str) -> int:
        """估计所需搜索轮次"""
        complexity = len(topic.split())
        if complexity > 10:
            return 4
        elif complexity > 5:
            return 3
        return 2


# ── 搜索引擎 ───────────────────────────────────────────────

class SearchOrchestrator:
    """搜索编排器"""
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
    
    def search(self, topic: str, max_rounds: int = 3, use_cache: bool = True) -> Dict:
        """主搜索流程"""
        if not search:
            return {"error": "web-search skill not found", "results": []}
        
        # Step 1: 分析查询
        analysis = self.query_analyzer.analyze(topic)
        sub_queries = analysis["sub_queries"]
        strategy = analysis["strategy"]
        
        all_results = {}
        
        # Step 2: 多轮搜索
        for round_num in range(1, max_rounds + 1):
            # 选择本轮回溯
            if round_num == 1:
                queries = sub_queries[:5]  # 第一轮：基础查询
            else:
                # 后续轮次：基于已有结果深化
                queries = self._generate_follow_up_queries(topic, all_results)
            
            # 执行搜索
            round_results = {}
            for q in queries:
                try:
                    result = search(q, use_cache=use_cache)
                    if result.get("results"):
                        round_results[q] = result
                except Exception as e:
                    round_results[q] = {"error": str(e), "results": []}
            
            all_results[f"round_{round_num}"] = round_results
            
            # 检查是否需要继续
            if self._should_continue(round_results, round_num, max_rounds):
                continue
            break
        
        # Step 3: 汇总结果
        return self._summarize(topic, all_results, analysis)
    
    def _generate_follow_up_queries(self, topic: str, results: Dict) -> List[str]:
        """生成后续搜索查询"""
        queries = []
        
        # 从已有结果中提取关键词
        for round_key, round_results in results.items():
            for query, result in round_results.items():
                for r in result.get("results", [])[:3]:
                    # 从标题提取
                    title = r.get("title", "")
                    if title:
                        words = title.split()
                        if len(words) >= 2:
                            queries.append(f"{topic} {words[-1]}")
        
        # 去重
        return list(dict.fromkeys(queries))[:5]
    
    def _should_continue(self, results: Dict, current_round: int, max_rounds: int) -> bool:
        """判断是否需要继续搜索"""
        # 结果数量不足
        total_results = sum(
            len(r.get("results", []))
            for round_results in results.values()
            for r in round_results.values()
        )
        
        if total_results < 5 and current_round < max_rounds:
            return True
        
        return False
    
    def _summarize(self, topic: str, all_results: Dict, analysis: Dict) -> Dict:
        """汇总搜索结果"""
        # 收集所有结果
        all_items = []
        for round_key, round_results in all_results.items():
            for query, result in round_results.items():
                for item in result.get("results", []):
                    item["query"] = query
                    item["round"] = round_key
                    all_items.append(item)
        
        # 去重
        deduped = self._deduplicate(all_items)
        
        # 质量评估
        evaluated = self._evaluate_quality(deduped)
        
        # 可信度评估
        trust_scores = self._assess_trustworthiness(evaluated)
        
        return {
            "topic": topic,
            "total_queries": sum(
                len(r) for r in all_results.values()
            ),
            "total_results": len(deduped),
            "deduped_results": len(evaluated),
            "results": evaluated,
            "trust_scores": trust_scores,
            "analysis": analysis,
        }
    
    def _deduplicate(self, results: List[Dict]) -> List[Dict]:
        """去重"""
        seen_urls = set()
        unique = []
        
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(r)
        
        return unique
    
    def _evaluate_quality(self, results: List[Dict]) -> List[Dict]:
        """评估结果质量"""
        evaluated = []
        
        for r in results:
            score = self._calculate_quality_score(r)
            r["quality_score"] = score
            evaluated.append(r)
        
        # 按质量排序
        evaluated.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        return evaluated
    
    def _calculate_quality_score(self, result: Dict) -> float:
        """计算单个结果的质量分数"""
        score = 0.0
        
        # 域名可信度 (40%)
        domain = result.get("parsed_url", {}).get("domain", "")
        domain_score = DOMAIN_TRUSTWORTHINESS.get(domain, 0.5)
        score += domain_score * 0.4
        
        # 内容完整性 (20%)
        content = result.get("content", "")
        if len(content) > 100:
            score += 0.2
        elif len(content) > 50:
            score += 0.1
        
        # 标题相关性 (20%)
        title = result.get("title", "")
        if title and len(title) > 10:
            score += 0.2
        
        # 引擎权威性 (10%)
        engine = result.get("engine", "")
        engine_score = {"google": 0.9, "bing": 0.85, "duckduckgo": 0.7}.get(engine, 0.6)
        score += engine_score * 0.1
        
        # 新鲜度 (10%)
        url = result.get("url", "")
        if "2024" in url or "2025" in url or "2026" in url:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_trustworthiness(self, results: List[Dict]) -> Dict[str, float]:
        """评估可信度"""
        trust_scores = {}
        
        for r in results:
            url = r.get("url", "")
            trust_scores[url] = r.get("quality_score", 0.5)
        
        return trust_scores


# ── 报告生成器 ───────────────────────────────────────────────

class ReportGenerator:
    """生成研究报告"""
    
    def generate_markdown(self, research: Dict) -> str:
        """生成 Markdown 报告"""
        topic = research.get("topic", "Unknown Topic")
        results = research.get("results", [])
        trust_scores = research.get("trust_scores", {})
        
        lines = [
            f"# 深度研究报告：{topic}",
            f"",
            f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**搜索查询数：** {research.get('total_queries', 0)}",
            f"**信源数量：** {research.get('deduped_results', 0)}",
            f"",
            "---",
            f"",
        ]
        
        # 摘要
        lines.append("## 摘要")
        lines.append("")
        if results:
            top_result = results[0]
            lines.append(f"基于 {len(results)} 个信源的综合分析，核心发现如下：")
        else:
            lines.append("*未找到相关结果*")
        lines.append("")
        
        # 核心发现
        lines.append("## 核心发现")
        lines.append("")
        
        for i, r in enumerate(results[:5], 1):
            title = r.get("title", "无标题")
            url = r.get("url", "")
            content = r.get("content", "")[:200]
            trust = trust_scores.get(url, 0.5)
            stars = "⭐" * int(trust * 5)
            
            lines.append(f"### {i}. {title}")
            lines.append(f"**来源：** [{url}]({url}) {stars}")
            if content:
                lines.append(f"> {content}...")
            lines.append("")
        
        # 来源列表
        lines.append("## 完整来源")
        lines.append("")
        lines.append("| # | 标题 | URL | 可信度 |")
        lines.append("|---|------|-----|--------|")
        
        for i, r in enumerate(results, 1):
            title = r.get("title", "无标题")[:30]
            url = r.get("url", "")
            trust = trust_scores.get(url, 0.5)
            stars = f"{int(trust * 5)}/5"
            lines.append(f"| {i} | {title} | [{url}]({url}) | {stars} |")
        
        lines.append("")
        lines.append("---")
        lines.append(f"*由 deep-research v1.0 生成*")
        
        return "\n".join(lines)
    
    def generate_json(self, research: Dict) -> str:
        """生成 JSON 报告"""
        return json.dumps(research, ensure_ascii=False, indent=2)


# ── 主流水线 ───────────────────────────────────────────────

def deep_research(
    topic: str,
    max_rounds: int = 3,
    min_sources: int = 5,
    output_format: str = "markdown",
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    深度调研主入口
    
    Args:
        topic: 研究主题
        max_rounds: 最大搜索轮次
        min_sources: 最小信源数量
        output_format: 输出格式 (markdown/json/both)
        use_cache: 是否使用缓存
    
    Returns:
        研究结果
    """
    orchestrator = SearchOrchestrator()
    reporter = ReportGenerator()
    
    # 执行搜索
    research = orchestrator.search(topic, max_rounds=max_rounds, use_cache=use_cache)
    
    # 生成报告
    if output_format in ("markdown", "both"):
        research["markdown_report"] = reporter.generate_markdown(research)
    
    if output_format in ("json", "both"):
        research["json_report"] = reporter.generate_json(research)
    
    return research


# ── CLI 入口 ───────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Deep Research — 深度调研 Agent")
    parser.add_argument("topic", help="研究主题")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="最大搜索轮次")
    parser.add_argument("--format", "-f", choices=["markdown", "json", "both"], default="markdown")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    
    args = parser.parse_args()
    
    result = deep_research(
        topic=args.topic,
        max_rounds=args.rounds,
        output_format=args.format,
        use_cache=not args.no_cache,
    )
    
    # 输出
    if args.format == "markdown":
        print(result.get("markdown_report", ""))
    elif args.format == "json":
        print(result.get("json_report", json.dumps(result, ensure_ascii=False, indent=2)))
    else:
        print(result.get("markdown_report", ""))
        print("\n--- JSON ---\n")
        print(result.get("json_report", ""))
    
    # 保存结果
    output_file = f"research_{hashlib.md5(args.topic.encode()).hexdigest()[:8]}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到: {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
