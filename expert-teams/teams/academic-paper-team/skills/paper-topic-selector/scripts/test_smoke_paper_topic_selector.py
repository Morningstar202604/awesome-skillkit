r"""Strong smoke test for paper-topic-selector (SOTA: multi-candidate ranking).

真输入 + 真断言：验证四因子加权、可行性模型、诚实 novelty 来源、排序与落选说明。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "topic_selector.py"
spec = importlib.util.spec_from_file_location("topic_selector", SCRIPT)
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)


def test_weights_match_skill_md():
    assert ts.WEIGHTS == {"novelty": 0.40, "feasibility": 0.30,
                          "impact": 0.20, "buildability": 0.10}


def test_total_is_weighted_sum():
    r = ts.evaluate_topic("zero-shot coordination benchmark", {"time": "6mo", "gpu": "8xA100"})
    s = r["scores"]
    expect = round(0.4 * s["novelty"] + 0.3 * s["feasibility"]
                   + 0.2 * s["impact"] + 0.1 * s["buildability"], 3)
    assert r["total"] == expect, (r["total"], expect)


def test_feasibility_drops_for_heavy_topic_and_short_deadline():
    light = ts.evaluate_topic("prompt tuning on top of existing models",
                              {"time": "6mo", "gpu": "8xA100"})
    heavy = ts.evaluate_topic("large multimodal pretrain from scratch",
                              {"time": "1mo", "gpu": "1xA100"})
    assert light["scores"]["feasibility"] > heavy["scores"]["feasibility"], (light, heavy)
    assert heavy["workload_weeks"] > light["workload_weeks"]
    assert heavy["recommendation"] == "reject", heavy


def test_deadline_parsing_units():
    assert ts._deadline_weeks({"time": "1y"}) == 52
    assert abs(ts._deadline_weeks({"time": "8w"}) - 8) < 1e-6
    assert abs(ts._deadline_weeks({"time": "3 months"}) - 3 * 4.345) < 1e-6
    assert abs(ts._deadline_weeks({}) - 6 * 4.345) < 1e-6  # 默认 6mo


def test_novelty_is_honest_by_default():
    r = ts.evaluate_topic("zero-shot coordination without shared memory")
    assert r["novelty_source"] == "heuristic-keyword"
    assert r["novelty_verified"] is False
    assert "lit-review" in r["next"]


def test_novelty_verified_with_lit_review_gaps():
    gaps = ["Existing work assumes shared context; zero-shot coordination remains unexplored"]
    base = ts.evaluate_topic("zero-shot coordination without shared memory")
    r = ts.evaluate_topic("zero-shot coordination without shared memory", None, gaps)
    assert r["novelty_source"] == "lit-review"
    assert r["novelty_verified"] is True
    assert r["novelty_evidence"], r
    assert r["scores"]["novelty"] > base["scores"]["novelty"]


def test_rank_orders_by_total_and_lists_rejected():
    cands = ["prompt tuning adapter on top of existing models for efficiency",
             "large multimodal pretrain from scratch",
             "zero-shot robustness benchmark for safety evaluation"]
    out = ts.rank(cands, {"time": "6mo", "gpu": "8xA100"})
    totals = [t["total"] for t in out["ranked_topics"]]
    assert totals == sorted(totals, reverse=True), totals
    assert [t["rank"] for t in out["ranked_topics"]] == list(range(1, len(totals) + 1))
    assert any("from scratch" in r["topic"] for r in out["rejected"]), out["rejected"]
    assert all(r["reason"] for r in out["rejected"])
    assert "honesty_note" in out


def test_cli_multi_topic_and_bad_constraints():
    r = subprocess.run([sys.executable, str(SCRIPT), "--topic", "a prompt adapter",
                        "--topic", "b zero-shot benchmark"],
                       capture_output=True, text=True, timeout=60, check=False)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o["n_candidates"] == 2 and len(o["ranked_topics"]) + len(o["rejected"]) == 2

    r2 = subprocess.run([sys.executable, str(SCRIPT), "--topic", "x", "--constraints", "{bad"],
                        capture_output=True, text=True, timeout=60, check=False)
    assert r2.returncode == 2 and json.loads(r2.stdout)["status"] == "error"

    r3 = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=60, check=False)
    assert r3.returncode == 2


def test_cli_candidates_file_and_lit_review():
    with tempfile.TemporaryDirectory() as d:
        cf = Path(d, "c.json")
        cf.write_text(json.dumps({
            "constraints": {"time": "6mo", "gpu": "8xA100"},
            "candidates": [{"topic": "zero-shot coordination without shared memory"},
                           {"topic": "large pretrain from scratch"}]}), encoding="utf-8")
        lf = Path(d, "lr.json")
        lf.write_text(json.dumps({"summary": {"gaps_identified": [
            "zero-shot coordination without shared memory is unexplored"]}}), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--candidates", str(cf),
                            "--lit-review-json", str(lf)],
                           capture_output=True, text=True, timeout=60, check=False)
        assert r.returncode == 0, r.stderr
        o = json.loads(r.stdout)
        assert o["novelty_source"] == "lit-review"
        assert o["ranked_topics"][0]["novelty_verified"] is True


def test_help_contract():
    r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                       capture_output=True, text=True, timeout=60, check=False)
    assert r.returncode == 0 and "usage" in r.stdout.lower()
