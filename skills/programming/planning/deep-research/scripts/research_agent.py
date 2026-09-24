#!/usr/bin/env python3
"""deep-research -- deep-research agent.

Multi-round search + information synthesis + structured report generation.
Depends on the web-search skill.
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

# try to import web-search
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "web-search", "scripts"))
    from search_client import search, SearchEngineError
except ImportError:
    search = None
    SearchEngineError = Exception


# -- Domain trustworthiness library ------------------------------------------

DOMAIN_TRUSTWORTHINESS = {
    # official docs
    "docs.python.org": 1.0,
    "fastapi.tiangolo.com": 1.0,
    "flask.palletsprojects.com": 1.0,
    "github.com": 0.9,
    "stackoverflow.com": 0.85,

    # technical blogs
    "medium.com": 0.6,
    "dev.to": 0.65,
    "hackernoon.com": 0.55,
    "realpython.com": 0.85,
    "segmentfault.com": 0.7,
    "jianshu.com": 0.5,

    # news
    "techcrunch.com": 0.7,
    "thenewstack.io": 0.75,

    # Chinese tech sites
    "cnblogs.com": 0.65,
    "csdn.net": 0.6,
    "juejin.cn": 0.7,
    "oschina.net": 0.7,

    # other
    "wikipedia.org": 0.8,
    "reddit.com": 0.5,
}


# -- Query analyzer ----------------------------------------------------------

class QueryAnalyzer:
    """Analyze a research topic and decompose it into sub-questions."""

    # pattern-matching rules
    PATTERNS = [
        (r"(\w+) (?:and|vs|or) (\w+)", ["compare {0} and {1}", "{0} vs {1}"]),
        (r"best (\w+)", ["{0} best practices", "{0} pros and cons", "{0} comparison"]),
        (r"how to (\w+)", ["{0} methods", "{0} tutorial", "{0} examples"]),
        (r"(\w+) framework", ["{0} introduction", "{0} tutorial", "{0} best practices"]),
    ]

    def analyze(self, topic: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Analyze the query and return structured information."""
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
        """Decompose into sub-queries."""
        queries = [topic]

        for pattern, templates in self.PATTERNS:
            match = re.search(pattern, topic)
            if match:
                for tpl in templates:
                    try:
                        queries.append(tpl.format(*match.groups()))
                    except IndexError:
                        pass

        # add a time dimension
        for year in ["2024", "2025", "2026"]:
            if year not in topic:
                queries.append(f"{topic} {year}")

        # add an English query
        queries.append(self._to_english(topic))

        # de-duplicate
        return list(dict.fromkeys(queries))[:10]

    def _to_english(self, query: str) -> str:
        """Passthrough; queries are already English (an LLM would be used for real translation)."""
        # vocabulary mapping (kept empty; English input needs no translation)
        translations = {
            "python": "python",
            "fastapi": "fastapi",
            "flask": "flask",
            "django": "django",
        }

        result = query
        for src, dst in translations.items():
            result = result.replace(src, dst)

        return result

    def _select_strategy(self, topic: str, queries: List[str]) -> Dict:
        """Choose the search strategy."""
        is_comparison = any("vs" in q.lower() or "compare" in q.lower() for q in queries)
        is_tutorial = any("tutorial" in q.lower() or "how" in q.lower() for q in queries)
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
        """Estimate the required number of search rounds."""
        complexity = len(topic.split())
        if complexity > 10:
            return 4
        elif complexity > 5:
            return 3
        return 2


# -- Search engine ----------------------------------------------------------

class SearchOrchestrator:
    """Search orchestrator"""

    def __init__(self):
        self.query_analyzer = QueryAnalyzer()

    def search(self, topic: str, max_rounds: int = 3, use_cache: bool = True) -> Dict:
        """Main search flow."""
        if not search:
            return {"error": "web-search skill not found", "results": []}

        # Step 1: analyze the query
        analysis = self.query_analyzer.analyze(topic)
        sub_queries = analysis["sub_queries"]
        strategy = analysis["strategy"]

        all_results = {}

        # Step 2: multi-round search
        for round_num in range(1, max_rounds + 1):
            # choose this round's queries
            if round_num == 1:
                queries = sub_queries[:5]  # first round: base queries
            else:
                # later rounds: deepen based on existing results
                queries = self._generate_follow_up_queries(topic, all_results)

            # run the search
            round_results = {}
            for q in queries:
                try:
                    result = search(q, use_cache=use_cache)
                    if result.get("results"):
                        round_results[q] = result
                except Exception as e:
                    round_results[q] = {"error": str(e), "results": []}

            all_results[f"round_{round_num}"] = round_results

            # check whether to continue
            if self._should_continue(round_results, round_num, max_rounds):
                continue
            break

        # Step 3: summarize results
        return self._summarize(topic, all_results, analysis)

    def _generate_follow_up_queries(self, topic: str, results: Dict) -> List[str]:
        """Generate follow-up search queries."""
        queries = []

        # extract keywords from existing results
        for round_key, round_results in results.items():
            for query, result in round_results.items():
                for r in result.get("results", [])[:3]:
                    # extract from the title
                    title = r.get("title", "")
                    if title:
                        words = title.split()
                        if len(words) >= 2:
                            queries.append(f"{topic} {words[-1]}")

        # de-duplicate
        return list(dict.fromkeys(queries))[:5]

    def _should_continue(self, results: Dict, current_round: int, max_rounds: int) -> bool:
        """Decide whether to continue searching."""
        # insufficient number of results
        total_results = sum(
            len(r.get("results", []))
            for round_results in results.values()
            for r in round_results.values()
        )
        
        if total_results < 5 and current_round < max_rounds:
            return True
        
        return False
    
    def _summarize(self, topic: str, all_results: Dict, analysis: Dict) -> Dict:
        """Summarize search results."""
        # collect all results
        all_items = []
        for round_key, round_results in all_results.items():
            for query, result in round_results.items():
                for item in result.get("results", []):
                    item["query"] = query
                    item["round"] = round_key
                    all_items.append(item)

        # de-duplicate
        deduped = self._deduplicate(all_items)

        # quality evaluation
        evaluated = self._evaluate_quality(deduped)

        # trustworthiness assessment
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
        """De-duplicate."""
        seen_urls = set()
        unique = []
        
        for r in results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(r)
        
        return unique
    
    def _evaluate_quality(self, results: List[Dict]) -> List[Dict]:
        """Evaluate result quality."""
        evaluated = []

        for r in results:
            score = self._calculate_quality_score(r)
            r["quality_score"] = score
            evaluated.append(r)

        # sort by quality
        evaluated.sort(key=lambda x: x.get("quality_score", 0), reverse=True)

        return evaluated

    def _calculate_quality_score(self, result: Dict) -> float:
        """Calculate the quality score for a single result."""
        score = 0.0

        # domain trustworthiness (40%)
        domain = result.get("parsed_url", {}).get("domain", "")
        domain_score = DOMAIN_TRUSTWORTHINESS.get(domain, 0.5)
        score += domain_score * 0.4

        # content completeness (20%)
        content = result.get("content", "")
        if len(content) > 100:
            score += 0.2
        elif len(content) > 50:
            score += 0.1

        # title relevance (20%)
        title = result.get("title", "")
        if title and len(title) > 10:
            score += 0.2

        # engine authority (10%)
        engine = result.get("engine", "")
        engine_score = {"google": 0.9, "bing": 0.85, "duckduckgo": 0.7}.get(engine, 0.6)
        score += engine_score * 0.1

        # freshness (10%)
        url = result.get("url", "")
        if "2024" in url or "2025" in url or "2026" in url:
            score += 0.1

        return min(score, 1.0)

    def _assess_trustworthiness(self, results: List[Dict]) -> Dict[str, float]:
        """Assess trustworthiness."""
        trust_scores = {}
        
        for r in results:
            url = r.get("url", "")
            trust_scores[url] = r.get("quality_score", 0.5)
        
        return trust_scores


# -- Report generator -------------------------------------------------------

class ReportGenerator:
    """Generate a research report."""

    def generate_markdown(self, research: Dict) -> str:
        """Generate a Markdown report."""
        topic = research.get("topic", "Unknown Topic")
        results = research.get("results", [])
        trust_scores = research.get("trust_scores", {})

        lines = [
            f"# Deep research report: {topic}",
            f"",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Search queries:** {research.get('total_queries', 0)}",
            f"**Number of sources:** {research.get('deduped_results', 0)}",
            f"",
            "---",
            f"",
        ]

        # summary
        lines.append("## Summary")
        lines.append("")
        if results:
            top_result = results[0]
            lines.append(f"Based on a synthesis of {len(results)} sources, the key findings are:")
        else:
            lines.append("*No relevant results found.*")
        lines.append("")

        # key findings
        lines.append("## Key findings")
        lines.append("")

        for i, r in enumerate(results[:5], 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            content = r.get("content", "")[:200]
            trust = trust_scores.get(url, 0.5)
            stars = "⭐" * int(trust * 5)

            lines.append(f"### {i}. {title}")
            lines.append(f"**Source:** [{url}]({url}) {stars}")
            if content:
                lines.append(f"> {content}...")
            lines.append("")

        # source list
        lines.append("## Full sources")
        lines.append("")
        lines.append("| # | Title | URL | Trust |")
        lines.append("|---|-------|-----|-------|")

        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")[:30]
            url = r.get("url", "")
            trust = trust_scores.get(url, 0.5)
            stars = f"{int(trust * 5)}/5"
            lines.append(f"| {i} | {title} | [{url}]({url}) | {stars} |")

        lines.append("")
        lines.append("---")
        lines.append(f"*Generated by deep-research v1.0*")

        return "\n".join(lines)

    def generate_json(self, research: Dict) -> str:
        """Generate a JSON report."""
        return json.dumps(research, ensure_ascii=False, indent=2)


# -- Main pipeline ----------------------------------------------------------

def deep_research(
    topic: str,
    max_rounds: int = 3,
    min_sources: int = 5,
    output_format: str = "markdown",
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Main entry point for deep research.

    Args:
        topic: research topic
        max_rounds: maximum search rounds
        min_sources: minimum number of sources
        output_format: output format (markdown/json/both)
        use_cache: whether to use the cache

    Returns:
        the research results
    """
    orchestrator = SearchOrchestrator()
    reporter = ReportGenerator()

    # run the search
    research = orchestrator.search(topic, max_rounds=max_rounds, use_cache=use_cache)

    # generate the report
    if output_format in ("markdown", "both"):
        research["markdown_report"] = reporter.generate_markdown(research)

    if output_format in ("json", "both"):
        research["json_report"] = reporter.generate_json(research)

    return research


# -- CLI entry point --------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Deep Research -- deep-research agent")
    parser.add_argument("topic", help="research topic")
    parser.add_argument("--rounds", "-r", type=int, default=3, help="maximum search rounds")
    parser.add_argument("--format", "-f", choices=["markdown", "json", "both"], default="markdown")
    parser.add_argument("--no-cache", action="store_true", help="disable the cache")

    args = parser.parse_args()

    result = deep_research(
        topic=args.topic,
        max_rounds=args.rounds,
        output_format=args.format,
        use_cache=not args.no_cache,
    )

    # output
    if args.format == "markdown":
        print(result.get("markdown_report", ""))
    elif args.format == "json":
        print(result.get("json_report", json.dumps(result, ensure_ascii=False, indent=2)))
    else:
        print(result.get("markdown_report", ""))
        print("\n--- JSON ---\n")
        print(result.get("json_report", ""))

    # save the result
    output_file = f"research_{hashlib.md5(args.topic.encode()).hexdigest()[:8]}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nResult saved to: {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
