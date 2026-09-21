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
