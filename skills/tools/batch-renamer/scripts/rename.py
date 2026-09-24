#!/usr/bin/env python3
"""rename.py -- batch renaming: preview, apply, undo trio.

Design principles
-----------------
1. **Preview is the default**: without `--yes` it only prints "old -> new" and never touches disk.
2. **On conflict, skip**: if a target name is already taken, skip the whole entry and report it;
   never silently overwrite.
3. **Always leave a trail**: every real run appends to `rename-log.txt`; `--undo` rolls back from it.
4. **Two-phase rename**: first rename every source file to a temp name, then to the final name,
   to avoid mid-way name clashes when a<->b swap -- the classic source of batch-rename accidents.

Subcommands
-----------
  preview <dir> [rules]             preview (default, does not execute)
  apply   <dir> [rules] --yes       execute
  undo    <dir> [--log PATH]        roll back from the log

Rules (composable, applied in a fixed order)
-------------------------------------------
  --pattern "IMG_{n:03d}.{ext}"   template: {n} index / {ext} extension / {stem} name / {date}
  --regex "OLD" "NEW"              regex replacement (on the file stem, Python re syntax)
  --prefix "P" / --suffix "S"      add prefix/suffix (on the stem, before the extension)
  --exif-date                       JPG/TIFF by EXIF DateTimeOriginal, falling back to mtime
  --lower / --upper                lowercase / uppercase the stem

Stdlib + optional Pillow (--exif-date). Python >= 3.8.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

LOG_NAME = "rename-log.txt"

SKIP_DIR_NAMES = {".git", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
                  ".venv", "node_modules"}

IMAGE_EXTS = {".jpg", ".jpeg", ".tif", ".tiff", ".png", ".heic", ".webp"}

# Unified temp-name prefix; after undo/interrupt it identifies files "renamed halfway"
TMP_PREFIX = ".rename_tmp_"


class BoundaryError(Exception):
    """The target path escaped the given directory boundary."""


def _resolve_within(root: Path, target: Path) -> Path:
    """After canonicalizing, assert the target is still inside root (blocks ../ and escaping symlinks)."""
    root_real = root.resolve()
    target_real = (target if target.is_absolute() else root / target).resolve()
    if target_real != root_real and root_real not in target_real.parents:
        raise BoundaryError(f"{target_real} escaped the directory boundary {root_real}")
    return target_real


def _rel(path: Path, root: Path) -> Path:
    """Display path relative to root.

    compute_plan returns **absolute** paths (via `_resolve_within`), while root may be
    `.` or a relative path; a direct `path.relative_to(root)` raises ValueError. Resolve
    both sides before comparing, so `.`/relative/absolute inputs all display correctly.
    """
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        return path


def _iter_files(root: Path):
    for dirpath, dirnames, filenames in sorted(__import__("os").walk(root)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in sorted(filenames):
            p = Path(dirpath) / name
            if p.is_symlink() or not p.is_file():
                continue
            if name == LOG_NAME or name.startswith(TMP_PREFIX):
                continue
            yield p


# --------------------------------------------------------------------------
# EXIF date extraction
# --------------------------------------------------------------------------
def _exif_date(path: Path) -> tuple:
    """Return (datetime, source note). Falls back to mtime if Pillow is missing or EXIF cannot be read."""
    if path.suffix.lower() in IMAGE_EXTS:
        try:
            from PIL import Image  # lazy import: no install needed unless --exif-date is used
        except ImportError:
            return (
                datetime.fromtimestamp(path.stat().st_mtime),
                "mtime (Pillow not installed)",
            )
        try:
            with Image.open(path) as im:
                exif = im.getexif()
                # 36867 = DateTimeOriginal; 306 = DateTime
                raw = exif.get(36867) or exif.get(306)
                if raw:
                    dt = datetime.strptime(str(raw).strip(), "%Y:%m:%d %H:%M:%S")
                    return dt, "EXIF"
        except Exception:  # corrupted image / non-standard EXIF -> fall back, don't block other files
            pass
    return datetime.fromtimestamp(path.stat().st_mtime), "mtime"


# --------------------------------------------------------------------------
# name computation
# --------------------------------------------------------------------------
def _apply_text_rules(stem: str, args) -> str:
    """Apply text rules in fixed order: regex -> prefix/suffix -> case."""
    out = stem
    if args.regex:
        old, new = args.regex
        try:
            out = re.sub(old, new, out)
        except re.error as e:
            raise ValueError(f"regex syntax error: {e}") from e
    if args.prefix:
        out = f"{args.prefix}{out}"
    if args.suffix:
        out = f"{out}{args.suffix}"
    if args.lower:
        out = out.lower()
    if args.upper:
        out = out.upper()
    return out


def _apply_pattern(pattern: str, path: Path, index: int, dt: datetime | None) -> str:
    """Template substitution. Supports {n} / {ext} / {stem} / {date}, each with an optional Python format spec.

    E.g. `{n:03d}` in `IMG_{n:03d}.{ext}` goes through standard format zero-padding;
    `{date}` with no spec defaults to `%Y%m%d`, and with a spec uses that strftime string
    (e.g. `{date:%Y-%m}`). Unknown placeholders raise immediately, so we don't silently
    generate a pile of identical strings.
    """
    base_date = dt or datetime.fromtimestamp(path.stat().st_mtime)
    fields = {
        "n": index,
        "ext": path.suffix.lstrip("."),
        "stem": path.stem,
        "date": base_date.strftime("%Y%m%d"),
    }
    placeholder = re.compile(r"\{([a-z]+)(?::([^}]*))?\}")

    def repl(m):
        key, spec = m.group(1), m.group(2)
        if key not in fields:
            raise ValueError(
                f"unknown placeholder {{{key}}}; supported: {{n}} {{ext}} {{stem}} {{date}}"
            )
        if spec is None:
            return str(fields[key])
        if key == "date":
            # for dates the spec string is a strftime template, not a format spec
            return base_date.strftime(spec)
        if key == "n":
            try:
                return format(int(fields[key]), spec)
            except ValueError as e:
                raise ValueError(f"illegal index format `{spec}`: {e}") from e
        return format(fields[key], spec)

    return placeholder.sub(repl, pattern)


def _pattern_uses(pattern: str, field: str) -> bool:
    """Whether the template actually uses a given placeholder.

    Only consume an index when `{n}` is actually used, to avoid gaps in numbering; only read
    EXIF when `{date}` is used, to skip needless image decoding.
    """
    return f"{{{field}" in pattern


def compute_plan(root: Path, args) -> list:
    """Return [(src, dst, note) ...], with already-compliant entries removed."""
    files = list(_iter_files(root))
    if not files:
        return []

    dates = {}
    if args.exif_date:
        for p in files:
            dates[p] = _exif_date(p)

    # Only increment the index when {n} is actually used; otherwise skipped files would
    # waste a number and produce gaps like IMG_000, IMG_002.
    counter = args.start
    uses_n = bool(args.pattern) and _pattern_uses(args.pattern, "n")
    uses_date = bool(args.pattern) and _pattern_uses(args.pattern, "date")
    plan = []
    for p in files:
        stem = _apply_text_rules(p.stem, args)
        note = ""
        if args.pattern:
            dt = dates.get(p, (None, ""))[0]
            index = counter if uses_n else 0
            try:
                new_name = _apply_pattern(args.pattern, p, index, dt)
            except ValueError as e:
                raise SystemExit(f"ERROR: {e}")
            if uses_n:
                counter += 1
        else:
            new_name = f"{stem}{p.suffix}"
        if args.exif_date and not args.pattern:
            dt, src = dates[p]
            new_name = f"{dt.strftime('%Y%m%d')}_{new_name}"
            note = f"[{src}]"
        elif args.exif_date and uses_date:
            note = f"[{dates[p][1]}]"

        if new_name == p.name:
            # already compliant: don't consume an index, but don't move it either
            continue
        plan.append((p, _resolve_within(root, Path(new_name)), note))
    return plan


def _detect_conflicts(root: Path, plan: list) -> tuple:
    """Split the plan into (executable, conflicts). Conflict = target already exists, or two plan rows hit the same target."""
    wanted = {}
    ok, conflicts = [], []
    for src, dst, note in plan:
        existing = dst.exists() and dst.resolve() != src.resolve()
        collides = wanted.get(str(dst))
        if existing:
            conflicts.append((src, dst, note, f"target already exists {dst.name}"))
        elif collides is not None:
            conflicts.append(
                (src, dst, note, f"name clash with {collides.name} in this batch")
            )
        else:
            wanted[str(dst)] = src
            ok.append((src, dst, note))
    return ok, conflicts


# --------------------------------------------------------------------------
# preview / apply
# --------------------------------------------------------------------------
def _has_rule(args) -> bool:
    """Whether at least one rename rule was given (SKILL.md lists "rules" as a required input)."""
    return any((
        args.pattern, args.regex, args.prefix, args.suffix,
        args.exif_date, args.lower, args.upper,
    ))


def _require_rule(args) -> int:
    """Error and return 2 if rules are missing; return 0 if rules are present. Shared by both command entry points."""
    if _has_rule(args):
        return 0
    print("ERROR: give at least one rename rule: "
          "--pattern / --regex / --prefix / --suffix / --exif-date / --lower / --upper.",
          file=sys.stderr)
    print("e.g. preview <dir> --pattern 'IMG_{n:03d}.{ext}'", file=sys.stderr)
    return 2


def cmd_preview(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    rc = _require_rule(args)
    if rc:
        return rc
    plan = compute_plan(root, args)
    print(f"# rename preview: {root.resolve()}")
    print("(this command makes no changes)")
    print()
    if not plan:
        print("Nothing to rename: every file already matches the target rules.")
        return 0
    ok, conflicts = _detect_conflicts(root, plan)
    pairs = [(_rel(src, root).as_posix(), _rel(dst, root).as_posix())
             for src, dst, _ in ok]
    width = max((len(a) for a, _ in pairs), default=10)
    for (rel_s, rel_d), (_, _, note) in zip(pairs, ok):
        print(f"  {rel_s:<{width}}  ->  {rel_d} {note}")
    if conflicts:
        print()
        print(f"## {len(conflicts)} conflicting entries skipped (not executed)")
        for src, dst, _, why in conflicts:
            print(f"  [skip:{why}] {_rel(src, root)} -> "
                  f"{_rel(dst, root)}")
    print()
    print(f"Total: {len(ok)} to rename, {len(conflicts)} skipped.")
    print(f"To execute after confirming: apply {root} <same rules> --yes")
    return 0


def _write_log(root: Path, entries: list) -> Path:
    """Append one JSON record per line; use JSON rather than delimited text, so parsing doesn't break on names with spaces/quotes."""
    log_path = root / LOG_NAME
    with log_path.open("a", encoding="utf-8") as fh:
        for old, new in entries:
            fh.write(json.dumps({
                "ts": datetime.now().isoformat(timespec="seconds"),
                "from": old, "to": new,
            }, ensure_ascii=False) + "\n")
    return log_path


def cmd_apply(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    if not args.yes:
        print("Refusing to run: apply needs explicit --yes before touching disk.")
        print("First run preview to review the plan:")
        print(f"  preview {root} <same rules>")
        return 2
    rc = _require_rule(args)
    if rc:
        return rc

    plan = compute_plan(root, args)
    if not plan:
        print("Nothing to rename.")
        return 0
    ok, conflicts = _detect_conflicts(root, plan)

    print(f"# executing rename: {root.resolve()}")
    print()
    done = []
    # phase 1: rename everything to a temp name, fully eliminating mid-way clashes on a<->b swap
    staged = []
    try:
        for src, dst, note in ok:
            tmp = src.with_name(f"{TMP_PREFIX}{len(staged)}{src.suffix}")
            try:
                _resolve_within(root, tmp)
                src.rename(tmp)
                staged.append((src, tmp, dst, note))
            except (BoundaryError, OSError) as e:
                print(f"[skip] {_rel(src, root)} staging failed: {e}", file=sys.stderr)
        # phase 2: temp name -> final name
        for src, tmp, dst, note in staged:
            try:
                if dst.exists():
                    print(f"[skip] target appeared, rolling back: {_rel(dst, root)}",
                          file=sys.stderr)
                    tmp.rename(src)
                    continue
                tmp.rename(dst)
                print(f"[ok] {_rel(src, root)} -> {_rel(dst, root)} {note}")
                done.append((_rel(src, root).as_posix(),
                             _rel(dst, root).as_posix()))
            except OSError as e:
                print(f"[skip] {_rel(src, root)} rename failed: {e}", file=sys.stderr)
                if tmp.exists():
                    tmp.rename(src)
    except KeyboardInterrupt:
        # interrupt fallback: rename files still at temp names back, so the directory is not left half-renamed
        for src, tmp, _dst, _n in staged:
            if tmp.exists():
                tmp.rename(src)
        print("\nInterrupted: staged files restored; no log was written.", file=sys.stderr)
        return 130

    if done:
        log_path = _write_log(root, done)
        print()
        print(f"Done: renamed {len(done)}, skipped {len(conflicts)}.")
        print(f"Change log: {log_path} (rollback: undo {root})")

    if conflicts:
        print()
        print(f"## {len(conflicts)} conflicting entries skipped")
        for src, dst, _, why in conflicts:
            print(f"  [skip:{why}] {_rel(src, root)} -> {_rel(dst, root)}")
    return 0


# --------------------------------------------------------------------------
# undo
# --------------------------------------------------------------------------
def cmd_undo(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    log_path = Path(args.log) if args.log else root / LOG_NAME
    if not log_path.is_file():
        print(f"ERROR: log not found {log_path}", file=sys.stderr)
        return 1

    records = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            print(f"WARN: skipping unparseable log line: {line[:60]}", file=sys.stderr)

    if not records:
        print("Log is empty; nothing to roll back.")
        return 0

    if not args.yes:
        print(f"# rollback preview ({len(records)} records, applied in reverse order)")
        print()
        for rec in reversed(records):
            print(f"  {rec['to']}  ->  {rec['from']}")
        print()
        print(f"To execute after confirming: undo {root} --yes")
        return 0

    print("# executing rollback")
    print()
    reverted, stuck = [], []
    for rec in reversed(records):
        cur = _resolve_within(root, Path(rec["to"]))
        orig = _resolve_within(root, Path(rec["from"]))
        if not cur.exists():
            print(f"[skip] no longer exists: {rec['to']}", file=sys.stderr)
            stuck.append(rec)
            continue
        if orig.exists():
            print(f"[skip] original name already taken, cannot roll back: {rec['from']}", file=sys.stderr)
            stuck.append(rec)
            continue
        try:
            orig.parent.mkdir(parents=True, exist_ok=True)
            cur.rename(orig)
            print(f"[ok] {rec['to']} -> {rec['from']}")
            reverted.append(rec)
        except OSError as e:
            print(f"[skip] {rec['to']} rollback failed: {e}", file=sys.stderr)
            stuck.append(rec)

    # Drop reverted records from the log, keeping the ones that couldn't roll back,
    # so a repeated undo doesn't go wrong.
    remaining = [r for r in records if r in stuck]
    log_path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in remaining),
        encoding="utf-8",
    )
    print()
    print(f"Rollback done: restored {len(reverted)}, left {len(stuck)} unhandled.")
    print(f"Log updated: {log_path} ({len(remaining)} records left)")
    return 0


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rename.py",
        description="Batch rename (preview by default / apply needs --yes / undo rolls back)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_rules(sp):
        sp.add_argument("dir")
        sp.add_argument("--pattern", help="template, e.g. 'IMG_{n:03d}.{ext}'")
        sp.add_argument("--regex", nargs=2, metavar=("OLD", "NEW"),
                        help="regex replacement, applied to the stem")
        sp.add_argument("--prefix", default=None, help="stem prefix")
        sp.add_argument("--suffix", default=None, help="stem suffix")
        sp.add_argument("--exif-date", action="store_true",
                        help="prepend YYYYMMDD_ from EXIF capture date (fall back to mtime)")
        sp.add_argument("--lower", action="store_true")
        sp.add_argument("--upper", action="store_true")
        sp.add_argument("--start", type=int, default=1, help="index start value (default 1)")

    s = sub.add_parser("preview", help="preview the rename result (default, does not execute)")
    add_rules(s)
    s.set_defaults(func=cmd_preview)

    s = sub.add_parser("apply", help="execute the rename (requires --yes)")
    add_rules(s)
    s.add_argument("--yes", action="store_true", help="confirm execution")
    s.set_defaults(func=cmd_apply)

    s = sub.add_parser("undo", help="roll back from rename-log.txt")
    s.add_argument("dir")
    s.add_argument("--log", default=None, help="custom log path")
    s.add_argument("--yes", action="store_true", help="confirm rollback")
    s.set_defaults(func=cmd_undo)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "lower", False) and getattr(args, "upper", False):
        print("ERROR: --lower and --upper are mutually exclusive.", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except BoundaryError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
