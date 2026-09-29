# CI smoke tests for commands that SKILL.md documents as self-checks.
#
# tools/validate_skills.py checks that referenced paths exist, but it cannot
# check that a documented command actually produces its documented result.
# Both P0-class regressions found in the 2026-09-29 audit (storyboard-designer
# field-name mismatch, channel-adapter sample failing its own gate) were of
# this kind. This file pins the documented self-checks so they cannot drift
# from their bundled fixtures again.
#
# To add a skill: give the exact command SKILL.md documents, plus the
# expected exit code and (optionally) a substring of stdout/stderr.

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

CASES = [
    # (label, argv relative to repo root, expected exit, expected substring)
    (
        "storyboard-designer: SKILL.md pre-flight self-check",
        [sys.executable,
         "skills/video/storyboard-designer/scripts/scene_lint.py",
         "skills/video/storyboard-designer/examples/"],
        0,
        "ALL OK",
    ),
    (
        "channel-adapter: bundled sample passes its own fit check",
        [sys.executable,
         "skills/marketing/channel-adapter/scripts/channel_fit_check.py",
         "--file", "skills/marketing/channel-adapter/assets/sample-variant.md",
         "--channel", "xhs"],
        0,
        '"status": "pass"',
    ),
    (
        "skill-finder: multi-keyword search documented in SKILL.md",
        [sys.executable,
         "skills/meta/skill-finder/scripts/find_skill.py",
         "search", "contract", "review"],
        0,
        None,
    ),
    (
        "skill-linter: bundled English skill has 0 FAIL",
        [sys.executable,
         "skills/meta/skill-linter/scripts/lint_skill.py",
         "skills/tools/file-organizer"],
        0,
        "FAIL: 0",
    ),
]


@pytest.mark.parametrize("label,args,code,needle", CASES, ids=[c[0] for c in CASES])
def test_documented_selfcheck(label, args, code, needle):
    completed = subprocess.run(
        args, cwd=ROOT, capture_output=True, text=True, timeout=120
    )
    assert completed.returncode == code, (
        f"{label}\nstdout: {completed.stdout[-2000:]}\nstderr: {completed.stderr[-2000:]}"
    )
    if needle is not None:
        assert needle in completed.stdout, f"{label}: {needle!r} not in stdout"
