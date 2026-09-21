# -*- coding: utf-8 -*-
r"""Strong smoke test for anti-defensive (SOTA: hedge density + retain/tighten classifier).

真输入 + 真断言：验证对冲密度、统计语境附近的限定被标 retain（不扣分）、
纯语弱化被标 tighten（扣分）、定位与 CLI 契约。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "anti_defensive.py"
spec = importlib.util.spec_from_file_location("anti_defensive", SCRIPT)
ad = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ad)


def test_double_hedge_is_tighten():
    r = ad.check("The method may possibly improve accuracy.")
    it = next(i for i in r["issues"] if i["type"] == "double_hedge")
    assert it["action"] == "tighten", it
    assert it["tightened"] == 1 and it["retained"] == 0
    assert it["positions"][0].startswith("L1:C")


def test_hedge_near_statistical_context_is_retained():
    """限定语紧邻置信区间/样本量 → 合理统计限定，应 retain 且不扣分。"""
    text = ("Accuracy may vary; we report a 95% confidence interval and sample size n = 500.")
    r = ad.check(text)
    it = next(i for i in r["issues"] if i["type"] == "double_hedge") if \
        any(i["type"] == "double_hedge" for i in r["issues"]) else None
    # 用 filler_phrase 这个一定会命中且可放统计语境的模式来验证分类器
    text2 = ("It should be noted that the p-value equals 0.03 with a 95% confidence interval, "
             "and the estimate depends on sample size n = 500.")
    r2 = ad.check(text2)
    it2 = next(i for i in r2["issues"] if i["type"] == "filler_phrase")
    assert it2["action"] == "retain", it2
    assert it2["retained"] == 1 and it2["tightened"] == 0
    assert r2["score"] == 100, r2


def test_retain_does_not_lower_score():
    retained = ad.check("It should be noted that our estimate has a 95% confidence interval.")
    tightened = ad.check("It should be noted that our model is good.")
    assert retained["score"] == 100, retained
    assert tightened["score"] == 85, tightened


def test_hedge_density_metric():
    text = " ".join(["word"] * 50) + " may might could possibly likely suggests indicates"
    r = ad.check(text)
    assert r["hedges_total"] >= 6, r["hedges_total"]
    assert 0 < r["hedge_density_per_100w"], r
    assert r["method"] == "pattern+context-classifier"


def test_filler_and_undersell_and_editorializing():
    r = ad.check("It is important to note that we obtain a minor improvement. "
                 "Unfortunately the gain is a small effect.")
    types = {i["type"] for i in r["issues"]}
    assert "filler_phrase" in types, types
    assert "undersell" in types, types
    assert "editorializing" in types, types
    assert len(r["issues"]) == r["n_flags"]


def test_clean_text_is_clean():
    r = ad.check("We train for 100 epochs and report 91.2% accuracy on the held-out split.")
    assert r["status"] == "clean" and r["score"] == 100, r


def test_note_explains_retain_semantics():
    r = ad.check("text")
    assert "retain" in r["note"] and "academic error" in r["note"], r["note"]


def test_missing_file_rc1():
    r = subprocess.run([sys.executable, str(SCRIPT), "--file", "/no/such.md"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 1
    assert json.loads(r.stdout)["status"] == "error"


def test_cli_end_to_end():
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d, "s.md")
        fp.write_text("It should be noted that we may possibly see gains.", encoding="utf-8")
        outp = Path(d, "o.json")
        r = subprocess.run([sys.executable, str(SCRIPT), "--file", str(fp), "--output", str(outp)],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        o = json.loads(outp.read_text(encoding="utf-8"))
        assert o["status"] in ("clean", "rewrite_needed")
        assert "hedge_density_per_100w" in o
