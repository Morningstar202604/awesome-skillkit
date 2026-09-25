import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pii_scan.py"
PHONE = "13812345678"


def _run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _make_case(tmp_path):
    f = tmp_path / "note.txt"
    original = "phone: %s\n" % PHONE
    f.write_text(original, encoding="utf-8")
    return f, original


def test_default_writes_no_file(tmp_path):
    f, _ = _make_case(tmp_path)
    r = _run(str(f))
    assert r.returncode == 0, r.stderr
    assert "SUMMARY" in r.stdout
    assert not (tmp_path / "note.txt.redacted").exists()


def test_execute_writes_redacted_copy_and_keeps_source(tmp_path):
    f, original = _make_case(tmp_path)
    r = _run(str(f), "--execute")
    assert r.returncode == 0, r.stderr
    out = tmp_path / "note.txt.redacted"
    assert out.is_file()
    assert PHONE not in out.read_text(encoding="utf-8")
    assert f.read_text(encoding="utf-8") == original


def test_explicit_dry_run_flag_still_writes_nothing(tmp_path):
    f, _ = _make_case(tmp_path)
    r = _run(str(f), "--dry-run")
    assert r.returncode == 0, r.stderr
    assert not (tmp_path / "note.txt.redacted").exists()


def test_execute_directory_requires_out(tmp_path):
    (tmp_path / "sub").mkdir()
    r = _run(str(tmp_path), "--execute")
    assert r.returncode == 2
