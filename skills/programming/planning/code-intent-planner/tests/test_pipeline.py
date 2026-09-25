import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
PIPELINE_RUN = (
    "import json, pipeline, sys\n"
    "r = pipeline.run_pipeline('remove the old cache', session_id='s1'"
    "{project_clause})\n"
    "print(json.dumps(r))\n"
)


def _run(code, hashseed, session_dir):
    env = dict(os.environ)
    env["SKILLKIT_SESSION_DIR"] = str(session_dir)
    env["PYTHONHASHSEED"] = str(hashseed)
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(SCRIPTS),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_cache_hit_is_stable_across_processes(tmp_path):
    sessions = tmp_path / "sessions"
    first = _run(PIPELINE_RUN.format(project_clause=""), "1", sessions)
    assert first.returncode == 0, first.stderr
    result = json.loads(first.stdout.strip().splitlines()[-1])
    assert result["source_layer"] == "L1", result

    second = _run(PIPELINE_RUN.format(project_clause=""), "999", sessions)
    assert second.returncode == 0, second.stderr
    assert "[Cache Hit]" in second.stderr, second.stderr


def test_l1_hit_uses_project_root_tech_stack(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()
    (project / "go.mod").write_text("module example.com/x\n", encoding="utf-8")
    sessions = tmp_path / "sessions"
    clause = ", project_root=%r" % str(project)
    r = _run(PIPELINE_RUN.format(project_clause=clause), "5", sessions)
    assert r.returncode == 0, r.stderr
    result = json.loads(r.stdout.strip().splitlines()[-1])
    slots = {s["name"]: s["value"] for s in result["slots"]}
    assert "go" in (slots.get("tech_stack") or ""), slots


def test_session_file_is_valid_json_without_temp_leftovers(tmp_path):
    sessions = tmp_path / "sessions"
    r = _run(PIPELINE_RUN.format(project_clause=""), "7", sessions)
    assert r.returncode == 0, r.stderr
    files = list(sessions.glob("_session_*.json"))
    assert len(files) == 1, files
    json.loads(files[0].read_text(encoding="utf-8"))
    assert not list(sessions.glob("*.tmp")), list(sessions.glob("*.tmp"))
