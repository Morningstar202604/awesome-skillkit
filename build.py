#!/usr/bin/env python3
"""Cross-platform build for scene packs (mirror of build.sh).

Packages packs/*/pack.json into dist/<pack>.zip; each zip contains the skill
folders flat at top level so users unzip and drag them into their skills dir.

Usage:
    python3 build.py [output-dir]      # default: dist/

Stdlib only.
"""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".github"}
SKIP_FILES = {".gitignore", "docker-compose.yml"}
SKIP_SUFFIXES = {".pyc"}

# reproducible builds: fixed entry timestamps -> identical bytes for
# identical inputs -> stable manifest sha256 across rebuilds
FIXED_DATE = (2026, 1, 1, 0, 0, 0)


def is_excluded(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & SKIP_DIRS or rel.name in SKIP_FILES or rel.suffix in SKIP_SUFFIXES:
        return True
    # local account configs must never ship in a scene pack
    return any(part.endswith(".local.json") for part in rel.parts)


def find_skill_dir(name: str) -> Path | None:
    hits = [
        p.parent
        for p in SCRIPT_DIR.glob(f"skills/**/{name}/SKILL.md")
        if p.parent.name == name
    ]
    return hits[0] if hits else None


def add_tree(zf: zipfile.ZipFile, src_dir: Path, arc_prefix: str) -> int:
    count = 0
    for path in sorted(src_dir.rglob("*")):
        rel = path.relative_to(src_dir)
        if is_excluded(rel):
            continue
        if path.is_dir():
            continue
        zi = zipfile.ZipInfo(f"{arc_prefix}/{rel.as_posix()}", date_time=FIXED_DATE)
        zi.compress_type = zipfile.ZIP_DEFLATED
        zi.external_attr = 0o644 << 16
        zf.writestr(zi, path.read_bytes())
        count += 1
    return count


def skill_imports_common(skill_dir: Path) -> bool:
    """判断某技能脚本是否复用了 _common/publish_common。"""
    scripts = skill_dir / "scripts"
    if not scripts.is_dir():
        return False
    for py in scripts.glob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "publish_common" in text:
            return True
    return False


COMMON_DIR = SCRIPT_DIR / "skills" / "writing" / "_common"


def sync_manifest(fingerprints: dict[str, dict]) -> None:
    """Write size_kb/sha256 of built packs back into manifest.json."""
    manifest_path = SCRIPT_DIR / "manifest.json"
    if not manifest_path.is_file() or not fingerprints:
        return
    raw = manifest_path.read_text(encoding="utf-8")
    trailing_nl = raw.endswith("\n")
    manifest = json.loads(raw)
    changed = False
    for pack in manifest.get("packs", []):
        fp = fingerprints.get(pack.get("id", ""))
        if fp:
            if pack.get("size_kb") != fp["size_kb"]:
                pack["size_kb"] = fp["size_kb"]
                changed = True
            if pack.get("sha256") != fp["sha256"]:
                pack["sha256"] = fp["sha256"]
                changed = True
    if changed:
        out = json.dumps(manifest, ensure_ascii=False, indent=2)
        if trailing_nl:
            out += "\n"
        manifest_path.write_text(out, encoding="utf-8")
        print("manifest.json: size_kb/sha256 updated")


def main(argv: list[str]) -> int:
    out_dir = Path(argv[1]) if len(argv) > 1 else SCRIPT_DIR / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)

    pack_files = sorted(SCRIPT_DIR.glob("packs/*/pack.json"))
    if not pack_files:
        print("no packs found", file=sys.stderr)
        return 1

    built = 0
    all_skills: dict[str, Path] = {}
    fingerprints: dict[str, dict] = {}
    for pack_json in pack_files:
        pack = json.loads(pack_json.read_text(encoding="utf-8"))
        pack_id = pack_json.parent.name
        zip_path = out_dir / f"{pack_id}.zip"
        missing = False
        pack_skill_dirs: list[Path] = []
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for skill in pack["skills"]:
                skill_dir = find_skill_dir(skill["name"])
                if skill_dir is None:
                    print(
                        f"WARN: skill dir not found: {skill['name']} (pack {pack_id})",
                        file=sys.stderr,
                    )
                    missing = True
                    continue
                all_skills.setdefault(skill["name"], skill_dir)
                pack_skill_dirs.append(skill_dir)
                add_tree(zf, skill_dir, skill["name"])
            # 若本包技能复用了公共模块，则一并打包，保证解压后即可运行
            if COMMON_DIR.is_dir() and any(
                skill_imports_common(sd) for sd in pack_skill_dirs
            ):
                add_tree(zf, COMMON_DIR, "_common")
        size_kb = max(zip_path.stat().st_size // 1024, 1)
        digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        fingerprints[pack_id] = {"size_kb": size_kb, "sha256": digest}
        print(
            f"built: {zip_path}  ({len(pack['skills'])} skills, ~{size_kb} KB, sha256:{digest[:12]})"
        )
        built += 1

    sync_manifest(fingerprints)

    # convenience bundle: every skill from every pack in one zip
    if all_skills:
        zip_path = out_dir / "_all.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in sorted(all_skills):
                add_tree(zf, all_skills[name], name)
            if COMMON_DIR.is_dir() and any(
                skill_imports_common(sd) for sd in all_skills.values()
            ):
                add_tree(zf, COMMON_DIR, "_common")
        size_kb = max(zip_path.stat().st_size // 1024, 1)
        print(
            f"built: {zip_path}  (_all bundle, {len(all_skills)} skills, ~{size_kb} KB)"
        )
        built += 1

    print(f"done: {built} archive(s) -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
