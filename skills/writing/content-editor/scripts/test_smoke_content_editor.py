"""Smoke tests per SKILL-STANDARD-v2 G7: CLI contract stays runnable.

--help exercises argparse wiring without touching the network or filesystem.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "editor.py"


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

# --- 强测试：输入校验与退出码 ---

def test_missing_draft_clean_error():
    import subprocess, sys, json
    r = subprocess.run([sys.executable, str(SP / "editor.py"), "--draft", "/no/such.json"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r
    o = json.loads(r.stdout)
    assert o["status"] == "error" and "不存在" in o["error"]


def test_bad_json_draft_clean_error(tmp_path):
    import subprocess, sys, json
    bad = tmp_path / "d.json"
    bad.write_text("[oops", encoding="utf-8")
    r = subprocess.run([sys.executable, str(SP / "editor.py"), "--draft", str(bad)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r
    assert json.loads(r.stdout)["status"] == "error"
