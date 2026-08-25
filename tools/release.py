#!/usr/bin/env python3
"""Release helper per docs/VERSIONING.md.

Validates a semver bump, syncs manifest.json version/updated, requires the
matching CHANGELOG section, and (with --commit) commits + annotates the tag.

Usage:
    python tools/release.py 1.6.4 [--commit]

Pushing remains manual:  git push origin main --follow-tags
Stdlib only.
"""

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def fail(msg: str) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("version", help="target version X.Y.Z")
    ap.add_argument(
        "--commit", action="store_true", help="run git add/commit/tag (no push)"
    )
    args = ap.parse_args(argv[1:])

    m = SEMVER_RE.match(args.version)
    if not m:
        return fail(f"'{args.version}' is not X.Y.Z semver")

    manifest_path = ROOT / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return fail(f"cannot read manifest.json: {e}")

    old = str(manifest.get("version", ""))
    om = SEMVER_RE.match(old)
    if not om:
        return fail(f"manifest has no parsable current version (got '{old}')")
    if tuple(map(int, m.groups())) <= tuple(map(int, om.groups())):
        return fail(f"new version must be strictly greater than current {old}")

    changelog_path = ROOT / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    section = f"## [{args.version}]"
    if section not in changelog:
        return fail(
            f"CHANGELOG.md lacks a '{section}' entry. "
            "Write the changelog first, then rerun."
        )

    today = datetime.date.today().isoformat()

    # guard: a tag must contain the full content it claims to release.
    # v1.7.0-v1.11.0 shipped with new skill files left untracked because
    # only manifest/changelog were staged — never again.
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    if dirty:
        return fail(
            "working tree is dirty — commit ALL changes before releasing "
            "(uncommitted content would be missing from the tag):\n" + dirty
        )

    dated = f"{section} - {today}"
    if dated not in changelog:
        print(f"WARN: CHANGELOG section date is not today ({today}); continuing.")

    raw = manifest_path.read_text(encoding="utf-8")
    trailing_nl = raw.endswith("\n")
    manifest["version"] = args.version
    manifest["updated"] = today
    out = json.dumps(manifest, ensure_ascii=False, indent=2)
    if trailing_nl:
        out += "\n"
    manifest_path.write_text(out, encoding="utf-8")
    print(f"manifest.json: {old} -> {args.version} (updated={today})")

    git_cmds = [
        ["git", "add", "manifest.json", "CHANGELOG.md"],
        ["git", "commit", "-m", f"chore(release): v{args.version}"],
        ["git", "tag", "-a", f"v{args.version}", "-m", f"v{args.version}"],
    ]
    if args.commit:
        for cmd in git_cmds:
            subprocess.run(cmd, cwd=ROOT, check=True)
        print("done: committed and tagged. push with:")
        print("  git push origin main --follow-tags")
    else:
        print("dry-run. next steps:")
        for cmd in git_cmds:
            print("  " + " ".join(cmd))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
