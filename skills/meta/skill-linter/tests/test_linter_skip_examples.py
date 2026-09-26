"""RED: batch scan MUST skip examples/ fixtures; direct file/dir targets still lint."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_spec = importlib.util.spec_from_file_location(
    "lint_skill",
    ROOT / "skills" / "meta" / "skill-linter" / "scripts" / "lint_skill.py",
)
ls = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ls)

GOOD_FIXTURE = (
    ROOT
    / "skills"
    / "programming"
    / "ai-engineering"
    / "skill-tester"
    / "examples"
    / "good-skill"
    / "SKILL.md"
)


def make_tree(tmp_path):
    fixture = tmp_path / "skills" / "dom" / "pkg" / "examples" / "good-skill"
    fixture.mkdir(parents=True)
    (fixture / "SKILL.md").write_text(
        "---\nname: good-skill\ndescription: x\n---\n# s\n"
    )
    real = tmp_path / "skills" / "dom" / "pkg" / "real-skill"
    real.mkdir(parents=True)
    (real / "SKILL.md").write_text("---\nname: real-skill\ndescription: x\n---\n# s\n")
    return fixture / "SKILL.md", real / "SKILL.md"


def test_batch_scan_skips_examples_fixture(tmp_path):
    _, real = make_tree(tmp_path)
    found = ls.iter_skill_files(tmp_path / "skills")
    assert found == [real], f"batch scan must exclude examples/, got {found}"


def test_batch_scan_keeps_sample_skip(tmp_path):
    sample = tmp_path / "skills" / "dom" / "pkg" / "assets" / "sample-x"
    sample.mkdir(parents=True)
    (sample / "SKILL.md").write_text("---\nname: sample-x\ndescription: x\n---\n# s\n")
    assert ls.iter_skill_files(tmp_path / "skills") == []


def test_direct_file_target_still_lints_example():
    assert ls.iter_skill_files(GOOD_FIXTURE) == [GOOD_FIXTURE]


def test_direct_skill_dir_target_still_lints_example():
    assert ls.iter_skill_files(GOOD_FIXTURE.parent) == [GOOD_FIXTURE]


def test_repo_batch_excludes_good_skill():
    found = ls.iter_skill_files(ROOT / "skills")
    assert GOOD_FIXTURE not in found
    assert found, "batch scan must still return shipped skills"
    assert all("examples" not in p.parts for p in found)
