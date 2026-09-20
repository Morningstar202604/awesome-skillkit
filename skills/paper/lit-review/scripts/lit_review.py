#!/usr/bin/env python3
"""Literature Review — 多源真实检索 + 真实引用图 + 诚实来源标注（SOTA 升级版）。

对标 2026 最佳实践：
  数据源（按优先级，自动回退，全程诚实标注 data_source）：
    1) --s2   : Semantic Scholar Graph API（真实引用/被引、venue、年份、摘要）
    2) --arxiv: arXiv API（真实检索，但无引用数 → citations=0）
    3) mock   : 内置合成数据（无网络兜底，MUST 标「模拟数据」）
  真实引用图：优先用 references 做「共同被引」边（两篇共享引用 → co-cited），
  而非旧版的顺序连接（无信息量）；缺引用元数据时退化为 venue+year 共现兜底。
  趋势/空白：默认 LLM 合成（seed 传入的摘要）；无 LLM 网关时回退到关键词共现
  （统计可复核），并如实标注 synthesis_method。

来源诚实：输出顶层 data_source = s2|arxiv|mock；任何回退都写进 warning；
mock 结果 MUST 标注 模拟数据。SKILLKIT_MOCK=1 强制 mock（CI/离线）。
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

_S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
_ARXIV_API = "https://export.arxiv.org/api/query"
_UA = {"User-Agent": "awesome-skillkit-lit-review/2.0 (SOTA)"}

MOCK_PAPERS = [
    {"id": "P001", "title": "Multi-Agent LLM Coordination", "year": 2024,
     "venue": "ACL", "citations": 120, "references": ["P005"], "doi": "mock:P001"},
    {"id": "P002", "title": "LLM Agent Benchmarking", "year": 2024,
     "venue": "NeurIPS", "citations": 85, "references": ["P005"], "doi": "mock:P002"},
    {"id": "P003", "title": "Cost-Efficient Agent Routing", "year": 2025,
     "venue": "ICML", "citations": 45, "references": ["P001"], "doi": "mock:P003"},
    {"id": "P004", "title": "Zero-Shot Agent Teams", "year": 2025,
     "venue": "AAAI", "citations": 30, "references": ["P001"], "doi": "mock:P004"},
    {"id": "P005", "title": "Agent Memory Architectures", "year": 2024,
     "venue": "ICLR", "citations": 200, "references": [], "doi": "mock:P005"},
]


# ---------------------------------------------------------------------------
# 数据源 1：Semantic Scholar（真实引用/被引）
# ---------------------------------------------------------------------------
def _fetch_s2(topic: str, max_results: int) -> list:
    query = urllib.parse.quote(topic)
    url = (f"{_S2_API}?query={query}&limit={max_results}"
           f"&fields=title,year,venue,citationCount,externalIds,abstract,references")
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read())
    out = []
    for p in data.get("papers", []) or []:
        ext = p.get("externalIds") or {}
        out.append({
            "id": ext.get("DOI") or p.get("paperId", ""),
            "title": (p.get("title") or "").strip(),
            "year": p.get("year") or 0,
            "venue": p.get("venue") or "unknown",
            "citations": p.get("citationCount") or 0,
            "abstract": (p.get("abstract") or "")[:600],
            "references": [r.get("paperId") for r in (p.get("references") or [])[:50]
                           if isinstance(r, dict) and r.get("paperId")],
            "doi": ext.get("DOI", ""),
        })
    return out


# ---------------------------------------------------------------------------
# 数据源 2：arXiv（真实检索，无引用数）
# ---------------------------------------------------------------------------
def _fetch_arxiv(topic: str, max_results: int) -> list:
    import time
    import xml.etree.ElementTree as ET

    query = urllib.parse.quote(topic)
    url = (f"{_ARXIV_API}?search_query=all:{query}"
           f"&max_results={max_results}&sortBy=relevance")
    body = None
    for attempt in range(2):  # 首次 + 429 退避重试一次
        try:
            req = urllib.request.Request(url, headers=_UA)
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
        abs_text = " ".join((entry.findtext("a:summary", "", ns) or "").split())
        papers.append({
            "id": arxiv_id,
            "title": " ".join((entry.findtext("a:title", "", ns) or "").split()),
            "year": int(published[:4]) if published[:4].isdigit() else 0,
            "venue": "arXiv",
            "citations": 0,  # arXiv 不提供引用数，如实置 0
            "abstract": abs_text[:600],
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "doi": "",
        })
    return papers


# ---------------------------------------------------------------------------
# 多源检索 + 诚实回退
# ---------------------------------------------------------------------------
def search_papers(topic: str, venues=None, max_results: int = 10,
                  source: str = "mock") -> tuple:
    """返回 (papers, meta)。meta={data_source, warning, retrieval_date}。"""
    import datetime
    ret_date = datetime.date.today().isoformat()
    force_mock = os.environ.get("SKILLKIT_MOCK") == "1"

    if source == "s2" and not force_mock:
        try:
            papers = _fetch_s2(topic, max_results)[:max_results]
            w = "Semantic Scholar 结果含真实引用数/venue；abstract 截断 600 字符"
            if venues:
                papers = _filter_venues(papers, venues)
            return papers, {"data_source": "s2", "warning": w, "retrieval_date": ret_date}
        except Exception as e:
            return _fallback(topic, venues, max_results, f"S2 API 失败({e})")

    if source == "arxiv" and not force_mock:
        try:
            papers = _fetch_arxiv(topic, max_results)[:max_results]
            w = "arXiv 结果无引用数(citations=0)；--venues 过滤不生效"
            return papers, {"data_source": "arxiv", "warning": w, "retrieval_date": ret_date}
        except Exception as e:
            return _fallback(topic, venues, max_results, f"arXiv API 失败({e})")

    papers = [dict(p) for p in MOCK_PAPERS][:max_results] if max_results >= 0 else []
    if venues:
        papers = _filter_venues(papers, venues)
    return papers, {"data_source": "mock",
                    "warning": "合成数据，MUST 标注 模拟数据",
                    "retrieval_date": ret_date}


def _fallback(topic, venues, max_results, reason):
    """S2/arXiv 失败 → 降级为 mock（保持诚实标注）。"""
    papers = [dict(p) for p in MOCK_PAPERS][:max_results]
    if venues:
        papers = _filter_venues(papers, venues)
    return papers, {"data_source": "mock",
                    "warning": f"{reason}，已回退为 MOCK 合成数据，MUST 标注 模拟数据",
                    "retrieval_date": None}


def _filter_venues(papers, venues):
    low = [v.lower() for v in venues]
    return [p for p in papers if (p.get("venue") or "").lower() in low] or papers


# ---------------------------------------------------------------------------
# 真实引用图：共同引用（co-citation）边，而非顺序连接
# ---------------------------------------------------------------------------
def build_citation_graph(papers: list, data_source: str) -> dict:
    """优先用 references 做共同被引边；缺引用元数据时按 venue+year 共现兜底。"""
    graph = {"nodes": [], "edges": [], "method": None}
    for p in papers:
        graph["nodes"].append({"id": p["id"], "title": p["title"], "year": p.get("year", 0)})

    # 方法 A：共同被引（两篇的 references 有交集 → co-cited 边）
    ref_sets = {p["id"]: set(p.get("references") or []) for p in papers}
    for i in range(len(papers)):
        for j in range(i + 1, len(papers)):
            a, b = papers[i]["id"], papers[j]["id"]
            if ref_sets.get(a) and ref_sets.get(b) and (ref_sets[a] & ref_sets[b]):
                graph["edges"].append({"from": a, "to": b, "type": "co-cited"})
    if graph["edges"]:
        graph["method"] = "co-citation (shared references)"
        return graph

    # 方法 B（无引用元数据，如 arXiv）：venue+year 共现兜底
    key = lambda p: (p.get("venue", "?"), p.get("year", 0))
    for i in range(len(papers)):
        for j in range(i + 1, len(papers)):
            if key(papers[i]) == key(papers[j]):
                graph["edges"].append({
                    "from": papers[i]["id"], "to": papers[j]["id"],
                    "type": "same-venue-year (low-confidence)"})
    graph["method"] = ("co-occurrence venue+year (no citation metadata)"
                       if graph["edges"] else "no edges (insufficient metadata)")
    return graph


# ---------------------------------------------------------------------------
# 趋势 / 空白：LLM 合成（seed 摘要），否则关键词共现回退
# ---------------------------------------------------------------------------
def summarize(papers: list, data_source: str, llm_topic=None) -> dict:
    if not papers:
        return {"status": "empty"}
    years = [p.get("year", 0) for p in papers if p.get("year")]
    venue_dist = dict(Counter(p.get("venue", "unknown") for p in papers))
    top_cited = sorted(papers, key=lambda x: -x.get("citations", 0))[:3]

    synthesis, trends, gaps = _synthesize(papers, llm_topic)
    return {
        "n_papers": len(papers),
        "year_range": [min(years), max(years)] if years else [],
        "venue_distribution": venue_dist,
        "total_citations": sum(p.get("citations", 0) for p in papers),
        "top_cited": [{"id": p["id"], "title": p["title"], "citations": p.get("citations", 0)}
                      for p in top_cited],
        "trends": trends,
        "gaps_identified": gaps,
        "synthesis_method": synthesis,
    }


def _get_model_route():
    """尽力导入仓库内 model_route helper；导入失败返回 None（走关键词回退）。"""
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                          "..", "..", "..", "meta", "_shared")))
        import model_route  # skills/meta/_shared/model_route.py
        return model_route
    except Exception:
        return None


def _synthesize(papers, llm_topic):
    abstracts = "\n".join(f"- {p.get('title')}: {(p.get('abstract') or '')[:180]}"
                          for p in papers[:10])
    mr = None if (llm_topic is None) else _get_model_route()
    if mr:
        prompt = (f"基于以下 {len(papers)} 篇论文标题/摘要，给出 2 条研究趋势与 2 条研究空白"
                  f"（各 ≤ 30 字，可直接写进 Related Work，分行输出）：\n{abstracts}")
        try:
            raw = mr.offline_or_model(prompt, "llm", lambda *a, **k: "",
                                       model_fn=None) or ""
            t, g = _parse_llm(raw)
            if t:
                return "llm", t, g
        except Exception:
            pass
    t, g = _keyword_fallback(papers)
    return "keyword-cooccurrence", t, g


def _keyword_fallback(papers):
    """纯统计：高频标题词 = 趋势信号；低覆盖但被高频词 = 空白候选。"""
    words = Counter()
    for p in papers:
        words.update((p.get("title") or "").split())
    common = [w for w, _ in words.most_common(4)]
    trends = f"高频主题词: {', '.join(common)}（基于 {len(papers)} 篇标题共现，非 LLM）"
    recent = {w for p in papers if p.get("year", 0) >= 2025 for w in p["title"].split()}
    gaps = [f"高频词 '{w}' 在 2025 年文献中未再出现，可能是未被跟进的方向"
            for w, _ in words.most_common(8) if w not in recent][:2]
    return trends, (gaps or ["暂无可量化空白信号（标题共现不足），建议扩大 --max 或换关键词"])


def _parse_llm(raw):
    lines = [l.strip() for l in (raw or "").splitlines() if l.strip()]
    t = lines[0] if lines else ""
    g = lines[1] if len(lines) > 1 else ""
    return t, g


def main():
    ap = argparse.ArgumentParser(description="Multi-source literature review (SOTA)")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--venues", help="Comma-separated venue filter（仅 s2/mock 生效）")
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--source", default="mock", choices=["s2", "arxiv", "mock"],
                    help="s2=Semantic Scholar(真实引用) | arxiv | mock")
    ap.add_argument("--s2", action="store_true", help="shorthand for --source s2")
    ap.add_argument("--arxiv", action="store_true", help="shorthand for --source arxiv")
    ap.add_argument("--no-llm", action="store_true", help="禁用 LLM 合成，强制关键词共现")
    ap.add_argument("--output", help="Output file")
    args = ap.parse_args()

    source = "s2" if args.s2 else ("arxiv" if args.arxiv else args.source)
    venues = args.venues.split(",") if args.venues else None
    papers, meta = search_papers(args.topic, venues, args.max, source)
    graph = build_citation_graph(papers, meta["data_source"])
    llm_topic = None if args.no_llm else args.topic
    summary = summarize(papers, meta["data_source"], llm_topic)

    result = {
        "topic": args.topic,
        "data_source": meta["data_source"],
        "warning": meta.get("warning"),
        "retrieval_date": meta.get("retrieval_date"),
        "papers": papers,
        "citation_graph": graph,
        "summary": summary,
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Review written to: {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
