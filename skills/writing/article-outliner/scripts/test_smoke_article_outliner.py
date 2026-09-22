"""Smoke tests per SKILL-STANDARD-v2 G7: CLI contract stays runnable.

--help exercises argparse wiring without touching the network or filesystem.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "outliner.py"


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

# --- 强测试：退出码契约 ---

def test_main_returns_zero_and_writes_file(tmp_path):
    import subprocess, sys, json
    out = tmp_path / "o.json"
    r = subprocess.run([sys.executable, str(SP / "outliner.py"), "--topic", "FastAPI 调优",
                        "--output", str(out)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    o = json.loads(out.read_text(encoding="utf-8"))
    assert o["total_words_target"] > 0 and len(o["sections"]) >= 5


def test_no_point_drop_and_budget_identity(tmp_path):
    """要点多于节数时不丢点；word_count_target 之和恒等于 total_words_target；
    占位字段有显式标记（防把骨架当成品交付）。"""
    import subprocess, sys, json
    out = tmp_path / "o2.json"
    r = subprocess.run([sys.executable, str(SP / "outliner.py"), "--topic", "T",
                        "--points", "a", "b", "c", "d", "e", "f", "g",
                        "--output", str(out)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    o = json.loads(out.read_text(encoding="utf-8"))
    got = sorted(p for s in o["sections"] for p in s["points"])
    assert got == ["a", "b", "c", "d", "e", "f", "g"], got
    assert sum(s["word_count_target"] for s in o["sections"]) == o["total_words_target"]
    assert o["placeholders"], "占位字段标记缺失（title/hook/conclusion/heading）"
