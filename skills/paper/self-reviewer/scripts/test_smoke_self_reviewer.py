# -*- coding: utf-8 -*-
"""Strong smoke test for self-reviewer (SOTA reproducibility rubric).

真输入 + 真断言：验证 keyword-fallback 与 llm-evidence 双轨、evidence 可复核、
ready 必须 uncertain 为空、method 诚实标注。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "self_reviewer.py"
spec = importlib.util.spec_from_file_location("self_rev", SCRIPT)
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)


def _draft(with_ablation=False, with_stats=True, words=3500):
    lines = [
        "\\section{Abstract} We propose a method.",
        "\\section{Method}\\section{Experiments}\\section{Related}\\section{Conclusion}",
        "\\cite{a}\\cite{b}",
    ]
    if with_stats:
        lines.append("We report p-value < 0.05 with 95% confidence interval.")
    if with_ablation:
        lines.append("An ablation study removes module A.")
    lines.append("Seeds and code are released for reproducibility.")
    lines.append("Limitations: single-domain evaluation.")
    lines.append("word " * words)
    return "\n".join(lines)


def test_keyword_pass_with_evidence():
    """命中关键词的 rubric 项必须 passed 且带 evidence（source=keyword）。"""
    r = sr.review_paper(_draft(with_ablation=True, with_stats=True))
    assert "Statistical significance tested" in r["passed"], r["passed"]
    ev = r["evidence"].get("Statistical significance tested")
    assert ev and ev["source"] == "keyword" and ev["evidence"], r
    assert r["method"] == "keyword-fallback", r["method"]


def test_uncertain_when_missed():
    """未命中关键词的 rubric 项进 uncertain，且 status 不得 ready。"""
    r = sr.review_paper(_draft(with_ablation=False, with_stats=False))
    joined = " ".join(r["uncertain"])
    assert "Statistical significance" in joined, r["uncertain"]
    assert r["status"] == "needs_work", r["status"]


def test_ready_requires_no_uncertain():
    """全通过且无 uncertain → ready；有任一 uncertain → needs_work。"""
    r_ready = sr.review_paper(_draft(with_ablation=True, with_stats=True))
    # 强制清掉 baseline（关键词没命中）→ 必须 needs_work
    assert r_ready["status"] != "ready" or not r_ready["uncertain"], r_ready
    # 构造一篇 baseline 也命中的
    full = _draft(with_ablation=True, with_stats=True) + "We compare against two baselines."
    r2 = sr.review_paper(full)
    assert "Baseline methods compared (2+)" in r2["passed"], r2
    assert not r2["uncertain"], r2["uncertain"]
    assert r2["status"] == "ready", r2


def test_llm_evidence_mode():
    """提供 LLM 证据（confidence≥0.6）时 method=llm-evidence 且证据记入。"""
    llm = {"Ablation study included": {"evidence": "Table 5 ablates A", "confidence": 0.9}}
    r = sr.review_paper(_draft(with_ablation=False, with_stats=True), llm_evidence=llm)
    assert r["method"] == "llm-evidence", r["method"]
    assert "Ablation study included (LLM)" in r["passed"], r["passed"]
    ev = r["evidence"]["Ablation study included"]
    assert ev["source"] == "llm" and ev["confidence"] == 0.9, ev


def test_llm_low_confidence_stays_uncertain():
    """LLM 置信度 <0.6 不得自动 passed，必须留 uncertain 待复核。"""
    llm = {"Limitations discussed": {"evidence": "?", "confidence": 0.2}}
    r = sr.review_paper(_draft(with_ablation=True, with_stats=True), llm_evidence=llm)
    # 本篇本身有 limitations 关键词 → 会 keyword 命中；用 llm 不命中项验证
    llm2 = {"Ablation study included": {"evidence": "?", "confidence": 0.1}}
    r2 = sr.review_paper(_draft(with_ablation=False, with_stats=True), llm_evidence=llm2)
    assert any("Ablation study included" in u for u in r2["uncertain"]), r2["uncertain"]


def test_score_is_passed_over_hardgates():
    """score 分母不含 uncertain（避免未检到拉低分）。"""
    r = sr.review_paper(_draft(with_ablation=True, with_stats=True))
    denom = len(r["passed"]) + len(r["failed"])
    assert denom > 0
    expected = int(100 * len(r["passed"]) / denom)
    assert r["score"] == expected, (r["score"], expected)


def test_cli_end_to_end():
    """CLI 冒烟 + 缺失文件 rc=1。"""
    with tempfile.TemporaryDirectory() as d:
        p1 = subprocess.run(
            [sys.executable, str(SCRIPT), "--paper", "/no/such/paper.tex"],
            capture_output=True, text=True, timeout=60,
        )
        assert p1.returncode == 1, p1
        assert "File not found" in json.loads(p1.stdout)["error"]
        # 正常路径
        pp = Path(d, "p.tex")
        pp.write_text(_draft(with_ablation=True, with_stats=True))
        outp = Path(d, "r.json")
        p2 = subprocess.run(
            [sys.executable, str(SCRIPT), "--paper", str(pp), "--output", str(outp)],
            capture_output=True, text=True, timeout=60,
        )
        assert p2.returncode == 0, p2.stderr
        d2 = json.loads(outp.read_text(encoding="utf-8"))
        assert d2["status"] in ("ready", "needs_work")
        assert "method" in d2 and "evidence" in d2
