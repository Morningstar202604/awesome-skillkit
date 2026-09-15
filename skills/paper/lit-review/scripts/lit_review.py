#!/usr/bin/env python3
"""Literature Review — 文献检索 + 关系图谱 + 总结。

用法:
  python3 lit_review.py --topic "LLM agents" --venues "ACL,NeurIPS" --max 20   # mock 数据
  python3 lit_review.py --topic "..." --arxiv                                  # 真调 arXiv API

数据来源标注: 输出顶层 `data_source` = "arxiv"（真实检索）| "mock"（合成数据）。
`--arxiv` 网络失败时自动回退 mock 并在 `warning` 中说明，mock 结果 MUST 标注 模拟数据。
`SKILLKIT_MOCK=1` 可强制 mock（CI/离线场景）。
"""
import argparse
import json
import sys
from pathlib import Path

# Mock paper database (synthetic — data_source: "mock")
MOCK_PAPERS = [
    {"id": "P001", "title": "Multi-Agent LLM Coordination", "year": 2024, "venue": "ACL", "citations": 120},
    {"id": "P002", "title": "LLM Agent Benchmarking", "year": 2024, "venue": "NeurIPS", "citations": 85},
    {"id": "P003", "title": "Cost-Efficient Agent Routing", "year": 2025, "venue": "ICML", "citations": 45},
    {"id": "P004", "title": "Zero-Shot Agent Teams", "year": 2025, "venue": "AAAI", "citations": 30},
    {"id": "P005", "title": "Agent Memory Architectures", "year": 2024, "venue": "ICLR", "citations": 200},
]

_ARXIV_API = "https://export.arxiv.org/api/query"


def _fetch_arxiv(topic: str, max_results: int) -> list:
    """真调 arXiv API（Atom XML）。网络/解析异常向上抛出，由调用方兜底。

    合法返回 0 条时原样返回 []（真实空结果，不回退 mock 以免编造数据）。
    arXiv 对共享出口 IP 常见 429 限流：按其礼仪 sleep 3s 后重试一次。
    """
    import time
    import urllib.error
    import urllib.parse
    import urllib.request
    import xml.etree.ElementTree as ET

    query = urllib.parse.quote(topic)
    url = (f"{_ARXIV_API}?search_query=all:{query}"
           f"&max_results={max_results}&sortBy=relevance")
    req = urllib.request.Request(
        url, headers={"User-Agent": "awesome-skillkit-lit-review/1.0"})

    body = None
    for attempt in range(2):  # 首次 + 429 退避重试一次
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 0:
                time.sleep(3)  # arXiv 礼仪间隔
                continue
            raise
    root = ET.fromstring(body)

    ns = {"a": "http://www.w3.org/2005/Atom"}
    papers = []
    for entry in root.findall("a:entry", ns):
        raw_id = (entry.findtext("a:id", "", ns) or "").rsplit("/abs/", 1)[-1]
        arxiv_id = raw_id.split("v")[0]
        published = entry.findtext("a:published", "", ns) or ""
        papers.append({
            "id": arxiv_id,
            "title": " ".join((entry.findtext("a:title", "", ns) or "").split()),
            "year": int(published[:4]) if published[:4].isdigit() else 0,
            "venue": "arXiv",
            "citations": 0,  # arXiv 不提供引用数，如实置 0
            "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
        })
    return papers


def search_papers(topic: str, venues: list = None, max_results: int = 10,
                  arxiv: bool = False) -> tuple:
    """Search papers. 返回 (papers, meta)。

    meta: {"data_source": "arxiv"|"mock", "warning": str|None}
    """
    import os

    force_mock = os.environ.get("SKILLKIT_MOCK") == "1"
    if arxiv and not force_mock:
        try:
            papers = _fetch_arxiv(topic, max_results)
            warning = ("--venues 过滤仅对 mock 数据生效，arXiv 结果未按 venues 过滤"
                       if venues else None)
            return papers[:max_results], {"data_source": "arxiv", "warning": warning}
        except Exception as e:  # 网络/解析失败 → 诚实兜底为 mock
            fallback_warning = (f"arXiv API 调用失败（{e}），已回退为 MOCK 合成数据，"
                                f"结果 MUST 标注 模拟数据")
            papers, meta = search_papers(topic, venues, max_results, arxiv=False)
            meta["warning"] = fallback_warning
            return papers, meta

    # Mock 路径
    results = [dict(p) for p in MOCK_PAPERS][:max_results] if max_results >= 0 else []
    if venues:
        results = [p for p in results if p.get("venue") in venues]
    return results, {"data_source": "mock", "warning": None}


def build_citation_graph(papers: list) -> dict:
    """Build simplified citation relationships."""
    graph = {"nodes": [], "edges": []}
    for p in papers:
        graph["nodes"].append({"id": p["id"], "title": p["title"], "year": p["year"]})
    # Mock: connect sequential papers
    for i in range(len(papers) - 1):
        graph["edges"].append({"from": papers[i]["id"], "to": papers[i + 1]["id"], "type": "related"})
    return graph


def summarize(papers: list) -> dict:
    """Generate literature summary."""
    if not papers:
        return {"status": "empty"}

    years = [p.get("year", 0) for p in papers]
    venues = {}
    for p in papers:
        v = p.get("venue", "unknown")
        venues[v] = venues.get(v, 0) + 1

    return {
        "n_papers": len(papers),
        "year_range": [min(years), max(years)] if years else [],
        "venue_distribution": venues,
        "total_citations": sum(p.get("citations", 0) for p in papers),
        "top_cited": sorted(papers, key=lambda x: -x.get("citations", 0))[:3],
        "trends": "Increasing focus on cost-efficiency and multi-agent (2025 papers)",
        "gaps_identified": ["Few works address budget-constrained routing", "No standardized eval for 3+ agents"],
    }


def main():
    parser = argparse.ArgumentParser(description="Literature review")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--venues", help="Comma-separated venues")
    parser.add_argument("--max", type=int, default=10)
    parser.add_argument("--arxiv", action="store_true")
    parser.add_argument("--output", help="Output file")
    args = parser.parse_args()

    venues = args.venues.split(",") if args.venues else None
    papers, meta = search_papers(args.topic, venues, args.max, args.arxiv)
    graph = build_citation_graph(papers)
    summary = summarize(papers)

    result = {
        "topic": args.topic,
        "data_source": meta["data_source"],
        "warning": meta.get("warning"),
        "papers": papers,
        "citation_graph": graph,
        "summary": summary,
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Review written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    sys.exit(main())
