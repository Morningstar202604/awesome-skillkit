"""RED: manifest.json sha256/size_kb MUST match committed site/packs zips (and vice versa)."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_spec = importlib.util.spec_from_file_location(
    "validate_skills", ROOT / "tools" / "validate_skills.py"
)
vs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vs)

DATA = b"zip-bytes-for-digest-gate-test"


def make_fixture(
    tmp_path,
    *,
    tamper_sha=None,
    drop_zip=False,
    bad_size=False,
    orphan=False,
    fileless=False,
    malformed=False,
):
    packs_dir = tmp_path / "site" / "packs"
    packs_dir.mkdir(parents=True)
    (packs_dir / "demo.zip").write_bytes(DATA)
    entry = {
        "id": "demo",
        "file": "dist/demo.zip",
        "size_kb": max(len(DATA) // 1024, 1),
        "sha256": hashlib.sha256(DATA).hexdigest(),
        "skills": [],
    }
    if fileless:
        entry.pop("file")
    if tamper_sha is not None:
        entry["sha256"] = tamper_sha
    if bad_size:
        entry["size_kb"] = 999
    if drop_zip:
        (packs_dir / "demo.zip").unlink()
    if orphan:
        (packs_dir / "rogue.zip").write_bytes(b"unmanifested")
    if malformed:
        mpath = tmp_path / "manifest.json"
        mpath.write_text("{not json", encoding="utf-8")
        return mpath, packs_dir
    mpath = tmp_path / "manifest.json"
    mpath.write_text(
        json.dumps({"version": "0.0.0", "packs": [entry]}), encoding="utf-8"
    )
    return mpath, packs_dir


def errors_of(mpath, packs_dir):
    issues = []
    vs.check_manifest_digests(mpath, packs_dir, issues)
    return [i.msg for i in issues if i.level == "ERROR"]


def test_matching_digests_clean(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path)
    assert errors_of(mpath, packs_dir) == []


def test_sha256_mismatch_is_error(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path, tamper_sha="0" * 64)
    errs = errors_of(mpath, packs_dir)
    assert any("sha256" in e for e in errs), errs


def test_missing_zip_is_error(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path, drop_zip=True)
    errs = errors_of(mpath, packs_dir)
    assert any("missing" in e for e in errs), errs


def test_size_kb_mismatch_is_error(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path, bad_size=True)
    errs = errors_of(mpath, packs_dir)
    assert any("size_kb" in e for e in errs), errs


def test_orphan_site_zip_is_error(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path, orphan=True)
    errs = errors_of(mpath, packs_dir)
    assert any("rogue.zip" in e for e in errs), errs


def test_all_bundle_zip_exempt_from_orphan_check(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path, orphan=False)
    (packs_dir / "_all.zip").write_bytes(b"bundle")
    assert errors_of(mpath, packs_dir) == []


def test_fileless_pack_resolved_by_id_zip(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path, fileless=True)
    (packs_dir / "demo.zip").write_bytes(DATA)
    assert errors_of(mpath, packs_dir) == []


def test_malformed_manifest_is_error(tmp_path):
    mpath, packs_dir = make_fixture(tmp_path, malformed=True)
    errs = errors_of(mpath, packs_dir)
    assert any("manifest" in e for e in errs), errs
