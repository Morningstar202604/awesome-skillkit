"""Smoke tests per SKILL-STANDARD-v2 G7: the CLI contract stays runnable."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "find_skill.py"
ROOT = SCRIPT.parents[4]


def run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd or ROOT, capture_output=True, text=True, timeout=60,
    )


def test_help_lists_all_three_subcommands():
    r = run("--help")
    assert r.returncode == 0
    for sub in ("search", "pack", "stats"):
        assert sub in r.stdout


def test_search_hits_a_known_skill():
    r = run("search", "pdf", "--top", "3", "--json")
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["total_matches"] > 0
    assert payload["matches"], "should return at least one match"
    assert payload["matches"][0]["name"] == "pdf-pipeline"


def test_search_miss_returns_exit_1():
    r = run("search", "zzzz-no-such-skill-anywhere")
    assert r.returncode == 1


def test_stats_matches_manifest_version():
    r = run("stats", "--json")
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert payload["manifest_version"] == manifest["version"]
    assert payload["packs"] == len(manifest["packs"])
    assert payload["skills_on_disk"] > 100


def test_pack_finds_common_pack():
    r = run("pack", "video-generation", "image-generation", "--json")
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["mode"] == "existing-pack"
    assert any(p["id"] == "ai-media-toolkit" for p in payload["common_packs"])


def test_works_from_any_working_directory():
    """数据源锚定在脚本自身位置，换 cwd 不该影响结果——否则 CI 里极易踩坑。"""
    r = run("stats", "--json", cwd="/tmp")
    assert r.returncode == 0
    payload = json.loads(r.stdout)
    assert payload["hub"] == "awesome-skillkit"


def test_missing_manifest_fails_loudly(tmp_path):
    """数据源缺失时必须显式失败，不得静默返回空结果。"""
    stray = tmp_path / "skills" / "meta" / "skill-finder" / "scripts"
    stray.mkdir(parents=True)
    copy = stray / "find_skill.py"
    copy.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(copy), "stats"],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 2
    assert "manifest.json" in r.stderr


def test_ranking_is_reproducible():
    a = run("search", "视频", "--json").stdout
    b = run("search", "视频", "--json").stdout
    assert a == b
