#!/usr/bin/env python3
"""organize.py -- directory health-check and organizer planner (scan / plan / apply / dedupe).

Design principles
-----------------
1. **Read-only by default**: `scan` / `plan` / `dedupe` never touch disk; `apply` defaults to
   dry-run and only actually moves files with explicit `--yes`.
2. **Closed boundary**: every target path goes through `_resolve_within`; the resolved real path
   must stay inside the given directory, ruling out `../` escapes and symlink escape.
3. **Do no harm**: never delete any file; for duplicates it only gives a "keep" recommendation,
   leaving deletion to the user.
4. **Fast**: dedup hashes only the first 1KB of each file, avoiding full reads of large files.

Subcommands
-----------
  scan   <dir>                              directory health-check (extension distribution, size, dup groups)
  plan   <dir> --by {type,date,size}        produce an organizing plan (print only, no moves)
  apply  <dir> --by {type,date} [--yes]     execute the organizing (dry-run by default)
  dedupe <dir>                              list duplicate groups + keep recommendation

Stdlib only. Python >= 3.8.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Number of head bytes read for dedup. 1KB is chosen because the magic number and basic metadata
# of almost every file format live in this range -- enough to tell apart "same size but different
# content"; going larger only slows things down without improving discrimination.
HEAD_BYTES = 1024

# Size-bucket thresholds (coarse human-readable grouping, ascending by upper bound).
SIZE_BUCKETS = [
    ("tiny(<10KB)", 10 * 1024),
    ("small(<1MB)", 1024 * 1024),
    ("medium(<10MB)", 10 * 1024 * 1024),
    ("large(<100MB)", 100 * 1024 * 1024),
    ("huge(>=100MB)", None),
]

# Directories excluded when organizing: these are the tool's own outputs or version-control
# internals; touching them would break the repo/environment state.
SKIP_DIR_NAMES = {".git", ".svn", ".hg", "__pycache__", ".pytest_cache",
                  ".mypy_cache", ".ruff_cache", ".venv", "node_modules"}


class BoundaryError(Exception):
    """The target path escaped the given directory boundary."""


def _resolve_within(root: Path, target: Path) -> Path:
    """Resolve target to an absolute real path and assert it is still inside root.

    `Path.resolve()` expands symlinks, so this blocks both `../` text escape and symlinks
    pointing outside the directory -- the script's single safety gate; every write/move
    path must pass through it.
    """
    root_real = root.resolve()
    # strict=False: the target file may not exist yet (apply creates new directories)
    target_real = (target if target.is_absolute() else root / target).resolve()
    if target_real != root_real and root_real not in target_real.parents:
        raise BoundaryError(f"{target_real} escaped the directory boundary {root_real}")
    return target_real


def _iter_files(root: Path):
    """Yield regular files under root, skipping symlinks and tool directories."""
    for dirpath, dirnames, filenames in os.walk(root):
        # dirnames must be pruned in place to stop os.walk from descending further
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.is_symlink() or not p.is_file():
                continue
            yield p


def _head_hash(path: Path) -> str:
    """sha1 of the file's first HEAD_BYTES bytes; it's fine if fewer are readable."""
    h = hashlib.sha1()
    with path.open("rb") as fh:
        h.update(fh.read(HEAD_BYTES))
    return h.hexdigest()


def _fingerprint(path: Path) -> tuple:
    """Fast dedup fingerprint = (file size, first-1KB hash).

    Only files with exactly the same size need head comparison; files of different sizes are
    immediately judged different.
    """
    return (path.stat().st_size, _head_hash(path))


def _ext_label(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    return ext if ext else "(no-ext)"


def _fmt_size(n: int) -> str:
    """Human-readable size: B has no decimals, others keep one."""
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{int(size)}B" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def _size_bucket(n: int) -> str:
    for label, upper in SIZE_BUCKETS:
        if upper is None or n < upper:
            return label
    return SIZE_BUCKETS[-1][0]


def _dup_groups(root: Path):
    """Return [(fingerprint, [paths...]) ...], keeping only groups with >=2 files.

    The grouping key is (size, head_hash): first bucket by size, then subdivide within each
    bucket by head hash, so files with a unique size need not even be read.
    """
    by_size = defaultdict(list)
    for p in _iter_files(root):
        by_size[p.stat().st_size].append(p)
    groups = defaultdict(list)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue
        for p in paths:
            groups[(size, _head_hash(p))].append(p)
    return sorted(
        ((fp, sorted(ps)) for fp, ps in groups.items() if len(ps) > 1),
        key=lambda kv: (-kv[0][0], str(kv[1][0])),
    )


def _keep_recommendation(paths: list) -> tuple:
    """Pick the one to keep in a duplicate group: oldest (earliest mtime) first; on tie, shortest path."""
    ranked = sorted(paths, key=lambda p: (p.stat().st_mtime, len(str(p)), str(p)))
    return ranked[0], ranked[1:]


# --------------------------------------------------------------------------
# scan
# --------------------------------------------------------------------------
def cmd_scan(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1

    files = list(_iter_files(root))
    if not files:
        print(f"No files to organize under {root.resolve()}.")
        return 0

    total = sum(p.stat().st_size for p in files)

    by_ext = defaultdict(lambda: [0, 0])
    by_bucket = defaultdict(int)
    for p in files:
        st = p.stat()
        slot = by_ext[_ext_label(p)]
        slot[0] += 1
        slot[1] += st.st_size
        by_bucket[_size_bucket(st.st_size)] += 1

    print(f"# directory health-check: {root.resolve()}")
    print(f"total files: {len(files)}    total size: {_fmt_size(total)}")
    print()

    print("## grouped by extension (count desc)")
    print(f"{'ext':<12}{'count':>8}{'size':>12}")
    for ext, (cnt, size) in sorted(
        by_ext.items(), key=lambda kv: (-kv[1][0], kv[0])
    ):
        print(f"{ext:<12}{cnt:>8}{_fmt_size(size):>12}")
    print()

    print("## size distribution")
    for label, _ in SIZE_BUCKETS:
        if by_bucket.get(label):
            print(f"{label:<16}{by_bucket[label]:>6} files")
    print()

    groups = _dup_groups(root)
    wasted = sum(fp[0] * (len(ps) - 1) for fp, ps in groups)
    print("## duplicate detection (size + first-1KB hash)")
    if not groups:
        print("No duplicates found.")
    else:
        print(f"duplicate groups: {len(groups)}    wasted space: {_fmt_size(wasted)}")
        for idx, (fp, paths) in enumerate(groups, 1):
            print(f"  [{idx}] {_fmt_size(fp[0])} x{len(paths)}")
            for p in paths:
                print(f"        {_rel(p, root)}")
        print()
        print("Tip: run `dedupe <dir>` to get a keep recommendation.")
    return 0


# --------------------------------------------------------------------------
# plan
# --------------------------------------------------------------------------
def _plan_type(p: Path, root: Path) -> Path:
    return Path(_ext_label(p))


def _plan_date(p: Path, root: Path) -> Path:
    return Path(datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m"))


def _plan_size(p: Path, root: Path) -> Path:
    return Path(_size_bucket(p.stat().st_size))


PLANNERS = {"type": _plan_type, "date": _plan_date, "size": _plan_size}


def _build_moves(root: Path, by: str):
    """Return [(src, dst) ...]; dst already resolves name clashes within a directory / against existing targets.

    Conflict-resolution: when `name.ext` is taken, try `name_1.ext`, `name_2.ext`... in turn,
    the index monotonically increasing to the first free slot; this way repeated plan/apply runs
    don't overwrite each other.
    """
    planner = PLANNERS[by]
    moves = []
    taken = set()
    for p in _iter_files(root):
        bucket = planner(p, root)
        if bucket == Path("."):  # already sits under the target bucket root; no move needed
            continue
        dst_dir = _resolve_within(root, bucket)
        candidate = dst_dir / p.name
        counter = 1
        while str(candidate) in taken or (
            candidate.exists() and candidate.resolve() != p.resolve()
        ):
            candidate = dst_dir / f"{p.stem}_{counter}{p.suffix}"
            counter += 1
        taken.add(str(candidate))
        moves.append((p, candidate))
    return sorted(moves, key=lambda m: str(m[0]))


def _rel(path: Path, root: Path) -> Path:
    """Display path relative to root; resolve both sides to absolute before comparing.

    A direct `path.relative_to(root)` raises ValueError when `root` is relative and `path`
    is absolute (as `_resolve_within` returns), so resolve both sides here.
    """
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        return path


def cmd_plan(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    moves = _build_moves(root, args.by)
    print(f"# organizing plan: {root.resolve()}  (by={args.by})")
    if not moves:
        print("Nothing to move: every file is already in its target location.")
        return 0
    print(f"{len(moves)} moves total; full list below (this command makes no moves):")
    print()
    for src, dst in moves:
        print(f"will move {_rel(src, root)} to {_rel(dst, root)}")
    print()
    print(f"Once confirmed, execute: apply {root} --by {args.by} --yes")
    return 0


# --------------------------------------------------------------------------
# apply
# --------------------------------------------------------------------------
def cmd_apply(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    if args.by == "size":
        print(
            "ERROR: apply does not support --by size.\n"
            "Reason: size is a file attribute, not a semantic category; archiving by size "
            "makes files unsearchable.\n"
            "To observe the size distribution, use `scan`, or first `plan --by size` for a human review.",
            file=sys.stderr,
        )
        return 2

    moves = _build_moves(root, args.by)
    if not moves:
        print("Nothing to move.")
        return 0

    dry = not args.yes
    print(f"# {'DRY-RUN (no disk changes)' if dry else 'EXECUTE (real moves)'}"
          f"  dir={root.resolve()}  by={args.by}")
    print()
    moved = skipped = 0
    for src, dst in moves:
        rel_src = _rel(src, root)
        rel_dst = _rel(dst, root)
        if dry:
            print(f"[dry-run] {rel_src} -> {rel_dst}")
            continue
        try:
            _resolve_within(root, dst)
            if dst.exists():
                print(f"[skip] target already exists, skipping: {rel_dst}")
                skipped += 1
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"[ok] {rel_src} -> {rel_dst}")
            moved += 1
        except BoundaryError as e:
            print(f"[skip] {e}", file=sys.stderr)
            skipped += 1
        except OSError as e:
            print(f"[skip] {rel_src} move failed: {e}", file=sys.stderr)
            skipped += 1

    print()
    if dry:
        print(f"DRY-RUN ended: planned {len(moves)} moves; no disk changes made.")
        print(f"To execute after confirming, add --yes: apply {root} --by {args.by} --yes")
    else:
        print(f"Done: moved {moved}, skipped {skipped}.")
    return 0


# --------------------------------------------------------------------------
# dedupe
# --------------------------------------------------------------------------
def cmd_dedupe(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    groups = _dup_groups(root)
    print(f"# duplicate report: {root.resolve()}")
    if not groups:
        print("No duplicates found (criterion: same size + same first-1KB hash).")
        return 0

    wasted = sum(fp[0] * (len(ps) - 1) for fp, ps in groups)
    print(f"{len(groups)} duplicate groups, {_fmt_size(wasted)} wasted space.")
    print("This command only gives advice; it never deletes any file.")
    print()
    for idx, (fp, paths) in enumerate(groups, 1):
        keep, drop = _keep_recommendation(paths)
        print(f"[{idx}] size {_fmt_size(fp[0])}, {len(paths)} copies")
        print(f"    keep: {_rel(keep, root)}  (oldest / shortest path)")
        for p in drop:
            print(f"    can clean: {_rel(p, root)}")
        print()

    print("Cleanup advice (please confirm manually before acting; this script does not do it for you):")
    print("  1. First `diff` or binary-compare to confirm the contents really match;")
    print("  2. Confirm no other file depends on the copy to be deleted via a hardlink/reference;")
    print("  3. Move them to a `_dupes_backup/` directory and watch for a while before deleting.")
    return 0


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="organize.py",
        description="Directory health-check and organizer planner (read-only by default; apply needs --yes)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="scan a directory: extension distribution, size, duplicates")
    s.add_argument("dir")
    s.set_defaults(func=cmd_scan)

    s = sub.add_parser("plan", help="produce an organizing plan (does not execute)")
    s.add_argument("dir")
    s.add_argument("--by", choices=["type", "date", "size"], default="type")
    s.set_defaults(func=cmd_plan)

    s = sub.add_parser("apply", help="execute the organizing (dry-run by default; only --yes really moves)")
    s.add_argument("dir")
    s.add_argument("--by", choices=["type", "date"], default="type")
    s.add_argument("--dry-run", action="store_true",
                   help="explicitly declare a dry-run (the default; for self-documentation only)")
    s.add_argument("--yes", action="store_true",
                   help="actually perform moves; without this it always dry-runs")
    s.set_defaults(func=cmd_apply)

    s = sub.add_parser("dedupe", help="list duplicate groups with a keep recommendation")
    s.add_argument("dir")
    s.set_defaults(func=cmd_dedupe)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BoundaryError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
