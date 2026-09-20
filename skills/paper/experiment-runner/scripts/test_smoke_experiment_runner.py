# -*- coding: utf-8 -*-
"""Strong smoke test for experiment-runner (SOTA stats).

真输入 + 真断言：验证 Welch t 检验（p/effect/CI）替代旧版假阈值。
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("exp_runner", SP / "experiment_runner.py")
exp_runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exp_runner)


def test_welch_stats_fields_present():
    """两组数据必须产出完整 Welch 统计结论。"""
    st = exp_runner.real_stats([0.91, 0.92, 0.90, 0.89], [0.85, 0.86, 0.84])
    for k in ("test", "method", "statistic", "p_value", "alpha",
              "effect_size_cohens_d", "ci95_diff", "significant"):
        assert k in st, f"missing {k}"
    assert st["test"] == "welch_ttest"
    assert st["method"] in ("scipy", "stdlib-fallback")
    assert isinstance(st["p_value"], float) and 0 <= st["p_value"] <= 1


def test_significant_when_clearly_better():
    """ours 明显优于 baseline → 必须 significant=True（旧假阈值也会 True，但这里是真 p 值）。"""
    st = exp_runner.real_stats([0.95, 0.96, 0.94, 0.95], [0.80, 0.81, 0.79])
    assert st["significant"] is True, f"expected significant, got {st}"
    assert st["p_value"] < 0.05
    # effect size 应为正（ours > baseline）
    assert st["effect_size_cohens_d"] > 0


def test_not_significant_when_equal():
    """两组几乎相同 → p 应较大（不显著）。"""
    st = exp_runner.real_stats([0.80, 0.81, 0.79, 0.80], [0.80, 0.79, 0.81, 0.80])
    assert st["significant"] is False or st["p_value"] >= 0.05, f"got {st}"


def test_real_mode_simulated_runs_and_reports_mode():
    """模拟模式必须诚实标注 mode=simulated。"""
    res = exp_runner.run_simulated({"n_runs": 6, "seed": 7, "baseline_metric": 0.8,
                                   "improvement_target": 0.05})
    assert res["mode"] == "simulated"
    assert res["simulation_notice"]
    assert res["stats"]["significant"] in (True, False)
    assert len(res["results"]) == 6


def test_seed_all_deterministic():
    """相同 seed → 相同结果（复现性核心承诺）。"""
    r1 = exp_runner.run_simulated({"n_runs": 5, "seed": 42, "baseline_metric": 0.8,
                                  "improvement_target": 0.05})
    r2 = exp_runner.run_simulated({"n_runs": 5, "seed": 42, "baseline_metric": 0.8,
                                   "improvement_target": 0.05})
    assert [x["ours"] for x in r1["results"]] == [x["ours"] for x in r2["results"]], "non-reproducible"


def test_cli_help_no_crash():
    r = subprocess.run([sys.executable, str(SP / "experiment_runner.py"), "--help"],
                       capture_output=True, text=True, timeout=60)
    assert "Traceback" not in (r.stdout + r.stderr), r.stdout + r.stderr
    assert r.returncode in (0, 1, 2)
