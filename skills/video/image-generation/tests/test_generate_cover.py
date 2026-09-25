import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_cover.py"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_help_exits_zero():
    r = _run("--help")
    assert r.returncode == 0, r.stderr
    assert "usage" in (r.stdout + r.stderr).lower()


def test_dry_run_prints_plan_and_writes_nothing(tmp_path):
    out = tmp_path / "cover.png"
    r = _run("--prompt", "hello world", "--out", str(out))
    assert r.returncode == 0, r.stderr
    assert "[PLAN]" in r.stdout
    assert not out.exists()


def test_invalid_size_rejected():
    r = _run("--prompt", "x", "--size", "100x100")
    assert r.returncode == 1
    combined = r.stdout + r.stderr
    assert "16" in combined
