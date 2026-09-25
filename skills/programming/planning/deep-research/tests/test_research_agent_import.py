import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def test_search_client_is_auto_discovered_without_pythonpath():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    code = (
        "import research_agent, sys\n"
        "sys.stdout.write('LOADED' if research_agent.search is not None else 'MISSING')\n"
    )
    r = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(SCRIPTS),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert "LOADED" in r.stdout, (r.stdout, r.stderr)
