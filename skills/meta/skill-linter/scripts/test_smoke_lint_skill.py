"""Smoke tests per SKILL-STANDARD-v2 G7: exit codes are the CI contract."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "lint_skill.py"
ROOT = SCRIPT.parents[4]
SELF = SCRIPT.parents[1]  # skills/meta/skill-linter


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )


def test_self_lint_has_no_failures():
    r = run(str(SELF))
    assert r.returncode == 0
    assert "RESULT: PASS" in r.stdout


def test_json_output_is_valid_and_has_summary():
    r = run(str(SELF), "--json")
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["summary"]["fail"] == 0
    assert payload["skills"][0]["name"] == "skill-linter"


def test_missing_target_returns_exit_2():
    r = run("/tmp/definitely-not-here")
    assert r.returncode == 2


def test_broken_skill_is_caught(tmp_path):
    """故意造残缺技能：缺 frontmatter 包裹、缺章节、失败表过短。"""
    d = tmp_path / "broken-skill"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "name: broken-skill\ndescription: nope\n\n"
        "# Broken\n\n## 工作流\n\n- 动作：无\n\n"
        "## 失败处置表\n\n| 现象 | 原因 | 处置 |\n|---|---|---|\n| 出错 | 不明 | 重试 |\n",
        encoding="utf-8",
    )
    r = run(str(d), "--json")
    assert r.returncode == 1
    checks = {f["check"] for f in json.loads(r.stdout)["skills"][0]["findings"]
              if f["level"] == "FAIL"}
    assert "FM-FIELDS" in checks
    assert "BODY-SECTS" in checks
    assert "FAIL-TABLE" in checks


def test_every_non_pass_finding_carries_a_fix():
    r = run(str(SELF), "--json")
    for skill in json.loads(r.stdout)["skills"]:
        for f in skill["findings"]:
            if f["level"] != "PASS":
                assert f["fix"], f"finding {f['check']} has no fix line"


def test_directory_tree_mode_produces_counts():
    r = run("skills/meta")
    assert r.returncode == 0
    assert "skills:" in r.stdout and "FAIL:" in r.stdout and "WARN:" in r.stdout
