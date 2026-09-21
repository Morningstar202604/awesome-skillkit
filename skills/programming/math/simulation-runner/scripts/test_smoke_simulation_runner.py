"""Smoke tests per SKILL-STANDARD-v2 G7: CLI contract stays runnable.

--help exercises argparse wiring without touching the network or filesystem.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "simulation.py"


def test_help_contract():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "usage" in (r.stdout + r.stderr).lower()


SP = Path(__file__).resolve().parent  # noqa: E305
import json  # noqa: E402
import importlib.util  # noqa: E402

# --- 强测试：demo 诚实标注 + 空 spec 敏感性硬报错 ---

def test_no_args_is_labeled_demo():
    import subprocess, sys, json
    r = subprocess.run([sys.executable, str(SP / "simulation.py")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o.get("demo") is True and "演示" in o.get("note", ""), o.get("note")


def test_explicit_monte_carlo_is_not_demo():
    import subprocess, sys, json
    r = subprocess.run([sys.executable, str(SP / "simulation.py"), "--monte-carlo",
                        "--n", "2000", "--mu", "1", "--sigma", "2", "--threshold", "3"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o.get("demo") is None and o["n"] == 2000 and o["threshold"] == 3


def test_sensitivity_without_spec_rejected():
    import subprocess, sys, json
    r = subprocess.run([sys.executable, str(SP / "simulation.py"), "--sensitivity", "mu"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r
    assert json.loads(r.stdout)["status"] == "error"
