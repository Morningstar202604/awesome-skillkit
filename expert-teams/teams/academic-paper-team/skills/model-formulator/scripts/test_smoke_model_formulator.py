"""Smoke tests per SKILL-STANDARD-v2 G7: CLI contract stays runnable.

--help exercises argparse wiring without touching the network or filesystem.
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "model_formulator.py"


def test_help_contract():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60, check=False,
    )
    assert r.returncode == 0, r.stderr
    assert "usage" in (r.stdout + r.stderr).lower()
