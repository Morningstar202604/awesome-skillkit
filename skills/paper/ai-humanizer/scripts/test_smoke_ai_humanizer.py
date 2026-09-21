# -*- coding: utf-8 -*-
r"""Strong smoke test for ai-humanizer (SOTA: lexical + structural).

真输入 + 真断言：验证词表命中带定位、结构指标（burstiness / 句首重复 / TTR / n-gram）、
分数受结构惩罚、诚实声明存在。
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SP = Path(__file__).resolve().parent
SCRIPT = SP / "ai_humanizer.py"
spec = importlib.util.spec_from_file_location("ai_humanizer", SCRIPT)
ah = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ah)


def test_llm_verb_spam_detected_with_positions():
    r = ah.humanize("We leverage a novel framework to delve into pivotal issues.")
    types = {i["type"] for i in r["issues"]}
    assert "llm_verb_spam" in types, types
    assert "buzzwords" in types, types
    hit = next(i for i in r["issues"] if i["type"] == "llm_verb_spam")
    assert hit["positions"] and hit["positions"][0].startswith("L1:C"), hit


def test_uniform_sentences_flagged_as_low_burstiness():
    """句长完全一致 → burstiness≈0 → 结构告警。"""
    text = "This sentence has exactly seven words here. " * 12
    r = ah.humanize(text)
    assert r["metrics"]["burstiness"] is not None, r["metrics"]
    assert r["metrics"]["burstiness"] < 0.05, r["metrics"]
    assert any(s["type"] == "low_burstiness" for s in r["structural"]), r["structural"]


def test_varied_sentences_not_flagged():
    text = ("Short one. " + " ".join(["word"] * 30) + ". Medium length here sits. "
            + " ".join(["w"] * 12) + ". Tiny. " + " ".join(["w"] * 22) + ".")
    r = ah.humanize(text)
    assert not any(s["type"] == "low_burstiness" for s in r["structural"]), r["metrics"]


def test_opener_repetition_detected():
    text = ("Furthermore we show A. Furthermore we show B. Furthermore we show C. "
            "Furthermore we show D. However the trend differs sharply from prior reports.")
    r = ah.humanize(text)
    assert any(s["type"] == "opener_repetition" for s in r["structural"]), r["structural"]
    assert r["metrics"]["max_opener_run"] >= 3


def test_repeated_ngram_detected():
    text = ("the model achieves robust gains on the benchmark under distribution shift here "
            "the model achieves robust gains on the benchmark under distribution shift here "
            "the model achieves robust gains on the benchmark under distribution shift here")
    r = ah.humanize(text)
    assert any(s["type"] == "repeated_ngram" for s in r["structural"]), r["structural"]


def test_clean_text_scores_high_and_status_clean():
    text = ("The encoder maps tokens to vectors. We evaluate on three benchmarks, reporting "
            "accuracies of 91.2%, 88.7% and 94.0%. Ablations remove each module in turn. "
            "Accuracy falls by 2.4 points without attention. We release code and seeds.")
    r = ah.humanize(text)
    assert r["score"] >= 85, r
    assert r["status"] == "clean", r


def test_detector_note_is_honest():
    r = ah.humanize("text")
    note = r["detector_note"].lower()
    assert "unreliable" in note and "never for misconduct" in note, note
    assert r["method"] == "lexical+structural"


def test_cli_report_and_json(tmpdir=None):
    with tempfile.TemporaryDirectory() as d:
        fp = Path(d, "t.txt")
        fp.write_text("We leverage novel methods.", encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), "--file", str(fp), "--report"],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        assert "AI-Humanize Score" in r.stdout
        assert "Note:" in r.stdout
        outp = Path(d, "o.json")
        r2 = subprocess.run([sys.executable, str(SCRIPT), "--file", str(fp), "--output", str(outp)],
                            capture_output=True, text=True, timeout=60)
        assert r2.returncode == 0
        o = json.loads(outp.read_text(encoding="utf-8"))
        assert "metrics" in o and "structural" in o


def test_cli_needs_input():
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=60)
    assert r.returncode != 0
