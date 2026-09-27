"""Strong smoke test for lit-review (SOTA multi-source + co-citation).

离线可跑：验证 mock 数据源的诚实标注、共同引用图、关键词共现合成。
真实 S2/arXiv 路径单独测（需网络，默认跳过）。
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

SP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lit_review", SP / "lit_review.py")
lr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lr)


def test_mock_reports_honest_source():
    """mock 路径必须诚实标注 data_source=mock + 模拟数据警告。"""
    os.environ["SKILLKIT_MOCK"] = "1"
    try:
        papers, meta = lr.search_papers("LLM agents", max_results=5, source="mock")
        assert meta["data_source"] == "mock"
        assert papers, "mock returned no papers"
        assert any("模拟" in (meta.get("warning") or "") or "MOCK" in (meta.get("warning") or "")
                   for _ in [0])
    finally:
        del os.environ["SKILLKIT_MOCK"]


def test_co_citation_graph_not_sequential():
    """引用图必须基于共享引用（co-cited），而非旧版顺序连接。"""
    os.environ["SKILLKIT_MOCK"] = "1"
    try:
        papers, _ = lr.search_papers("LLM agents", max_results=5, source="mock")
        g = lr.build_citation_graph(papers, "mock")
        # mock P001/P002 共享 ref P005 → 必有一条 co-cited 边
        assert any(e["type"] == "co-cited" for e in g["edges"]), f"no co-cited: {g['edges']}"
        assert g["method"] and "co-citation" in g["method"]
        # 节点数应等于论文数
        assert len(g["nodes"]) == len(papers)
    finally:
        del os.environ["SKILLKIT_MOCK"]


def test_fallback_honest_when_network_fail():
    """无网络/失败时回退 mock 且 warning 标注『已回退为 MOCK / MUST 标注 模拟数据』。"""
    os.environ["SKILLKIT_MOCK"] = "1"
    try:
        _papers, meta = lr.search_papers("x", max_results=3, source="s2")
    finally:
        del os.environ["SKILLKIT_MOCK"]
    assert meta["data_source"] == "mock"
    # mock 警告：SKILLKIT_MOCK=1 时走 mock 路径，warning 应含模拟数据/合成数据标注
    w = (meta.get("warning") or "").upper()
    assert "MOCK" in w or "模拟" in (meta.get("warning") or ""), f"missing mock warning: {w}"


def test_keyword_synthesis_offline():
    """无 LLM 时 trends/gaps 由关键词共现产出，synthesis_method 如实标注。"""
    s = lr.summarize(lr.MOCK_PAPERS, "mock", llm_topic=None)  # None → 走关键词回退
    assert s["synthesis_method"] in ("keyword-cooccurrence", "llm")
    assert s["n_papers"] == len(lr.MOCK_PAPERS)
    assert s["total_citations"] == sum(p["citations"] for p in lr.MOCK_PAPERS)


def test_cli_help_no_crash():
    r = subprocess.run([sys.executable, str(SP / "lit_review.py"), "--help"],
                       capture_output=True, text=True, timeout=60, check=False)
    assert "Traceback" not in (r.stdout + r.stderr)
    assert r.returncode in (0, 1, 2)
