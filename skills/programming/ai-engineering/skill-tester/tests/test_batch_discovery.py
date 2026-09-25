import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
REPO = Path(__file__).resolve().parents[5]


def _run(script, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _results(stdout):
    payload = json.loads(stdout)
    if isinstance(payload, dict) and isinstance(payload.get("skills"), list):
        return payload["skills"]
    return [payload]


def test_quality_batch_recurses_and_skips_fixtures(tmp_path):
    nested = tmp_path / "outer" / "inner" / "skill-one"
    nested.mkdir(parents=True)
    (nested / "SKILL.md").write_text(
        "---\nname: skill-one\ndescription: d\n---\n# body\n", encoding="utf-8"
    )
    top = tmp_path / "skill-two"
    top.mkdir()
    (top / "SKILL.md").write_text(
        "---\nname: skill-two\ndescription: d\n---\n# body\n", encoding="utf-8"
    )
    fixture = tmp_path / "outer" / "examples" / "fixture-skill"
    fixture.mkdir(parents=True)
    (fixture / "SKILL.md").write_text(
        "---\nname: fixture\ndescription: d\n---\n# body\n", encoding="utf-8"
    )

    r = _run("quality_scorer.py", str(tmp_path), "--batch", "--json")
    assert r.returncode == 0, r.stderr
    paths = [item["skill_path"].replace("\\", "/") for item in _results(r.stdout)]
    assert len(paths) == 2, paths
    assert not any("examples/" in p for p in paths), paths
    assert any(p.endswith("skill-one") for p in paths), paths
    assert any(p.endswith("skill-two") for p in paths), paths


def test_quality_batch_on_repo_finds_nested_skills():
    r = _run(
        "quality_scorer.py", str(REPO / "skills" / "programming"), "--batch", "--json"
    )
    assert r.returncode == 0, r.stderr
    paths = [item["skill_path"].replace("\\", "/") for item in _results(r.stdout)]
    assert len(paths) >= 20, f"expected >=20 nested skills, got {len(paths)}"
    assert all((Path(p) / "SKILL.md").is_file() for p in paths)


def test_security_scanner_finds_scripts_under_repo_root():
    r = _run("security_scorer.py", str(REPO / "skills"), "--json")
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["scripts_scored"] > 0, payload


def test_security_scanner_reports_null_score_when_no_scripts(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    r = _run("security_scorer.py", str(empty), "--json")
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["scripts_scored"] == 0
    assert payload["overall_score"] is None
