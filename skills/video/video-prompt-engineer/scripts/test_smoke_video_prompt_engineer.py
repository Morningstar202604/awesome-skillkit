"""Smoke + functional tests for prompt_audit.py (G7)."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "prompt_audit.py"


def test_help_contract():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stderr
    assert "usage" in (r.stdout + r.stderr).lower()


FULL_PROMPT = (
    "A young woman in a black hoodie walks through a rainy neon-lit street, "
    "slow push-in from medium shot to close-up, night exterior with cyan-orange "
    "neon spill, cinematic live-action, 5 seconds, 9:16 vertical."
)


def test_full_prompt_scores_6_of_6():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--prompt", FULL_PROMPT, "--json"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data["score"] == "6/6", data


def test_bare_prompt_reports_missing():
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--prompt", "a beautiful scene", "--json"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 1  # missing slots -> exit 1
    data = json.loads(r.stdout)
    assert data["missing"], data
