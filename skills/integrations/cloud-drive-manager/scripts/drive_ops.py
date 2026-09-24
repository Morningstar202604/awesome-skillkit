#!/usr/bin/env python3
"""drive_ops.py -- upload planner, checksum-list generator, and list parser for
cloud-drive archiving.

Targets chunked-upload + instant-upload drives such as Baidu Netdisk, Aliyun Drive,
and OneDrive. This script does only three **offline** things: work out what to
upload, leave a verification basis, and turn responses into human-readable text.

Design principles
-----------------
1. **Pure functions + read-only**: `plan-upload` / `checksum-plan` only read local
   directories, `parse-list` only reads JSON files. None of them touches the network
   or writes to the remote.
2. **Dry-run by default**: `plan-upload` outputs a plan, not an action; the real
   upload runs only after a human confirms.
3. **Credentials never hit disk**: access_token / client_secret are always read
   from environment variables (BAIDU_ACCESS_TOKEN / ALIYUN_REFRESH_TOKEN /
   ONEDRIVE_ACCESS_TOKEN); the script never touches those values internally.
4. **Deletes require double confirmation**: when `parse-list` sees a delete-class
   result it prints an extra warning; a real delete requires the user to confirm
   both the "target path" and the "affected file count" separately.

Subcommands
-----------
  plan-upload   --dir X --remote Y [--prefix P] [--manifest m.json]
  checksum-plan --dir X [--output sha256.txt] [--algo sha256|md5] [--exclude GLOB]
  parse-list    --json f.json [--provider {baidu|aliyun|onedrive}]

Stdlib only. Python >= 3.8.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Cloud-drive platform constants
# ---------------------------------------------------------------------------

# Thresholds and chunk size for chunked uploads. All three offer both "simple
# upload" and "chunked upload" paths with different thresholds; above the
# threshold, using simple upload is rejected outright.
CHUNK_POLICY = {
    "baidu": {
        "simple_max_mb": 4,      # under 4MB use simple upload
        "chunk_mb": 4,           # fixed 4MB chunks (platform convention)
        "slice_threshold_mb": 4,
        "note": "Baidu Netdisk's uploadid endpoint forces chunking for files over 4MB; chunks must be 4MB",
    },
    "aliyun": {
        "simple_max_mb": 100,
        "chunk_mb": 8,
        "slice_threshold_mb": 100,
        "note": "Aliyun Drive uploads files under 100MB in a single request; above that, use 8MB chunks",
    },
    "onedrive": {
        "simple_max_mb": 250,    # single-request upload limit is 250MB
        "chunk_mb": 10,          # chunks must be multiples of 320KiB; 10MB satisfies that
        "slice_threshold_mb": 250,
        "note": "OneDrive single-request upload limit is 250MB; chunks must be multiples of 320KiB",
    },
}

# How instant upload works: the client hashes the file content first; if the server
# already holds a **whole-file** record with the same hash, it creates a reference
# directly and no bytes are transferred.
HASH_ALGO = {
    "baidu": "md5 (per-chunk md5 during chunked upload, plus whole-file md5 for instant upload)",
    "aliyun": "sha1 + per-segment sha1 (Aliyun Drive uses sha1, not md5, as the dedup key)",
    "onedrive": "quickXorHash (Microsoft's own algorithm) or sha256 (depending on the API version)",
}

# Each provider's list response names the "entry array" differently.
LIST_KEY = {"baidu": "list", "aliyun": "items", "onedrive": "value"}

# Double-confirmation requirement for deletes (written into the output so the
# user cannot miss it).
DELETE_CONFIRM = (
    "Deletes are irreversible: please confirm twice -- "
    "(1) confirm the target path is exactly right; (2) confirm the affected file "
    "count matches expectation. If either is in doubt, move/archive to a folder "
    "instead of deleting."
)

SUPPORTED_ALGOS = ("sha256", "md5", "sha1")


class PlanError(Exception):
    """Plan generation failed (bad input, not a network problem)."""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    p = Path(path)
    if not p.is_file():
        raise PlanError(f"{what} file does not exist: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PlanError(f"{what} is not valid JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def fmt_size(n: int) -> str:
    """Human-readable size: B has no decimals; others keep one decimal."""
    size = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{int(size)}B" if unit == "B" else f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


# ---------------------------------------------------------------------------
# plan-upload
# ---------------------------------------------------------------------------
def collect_files(root: Path, prefix: str, exclude: list) -> list:
    """Walk the directory and collect files to upload.

    **Skip symlinks**: following links would make "upload directory A" accidentally
    upload large files from directory B too, losing control over quota and privacy.
    """
    if not root.is_dir():
        raise PlanError(f"not a directory: {root}")
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(p.name, pat)
               for pat in exclude):
            continue
        if prefix:
            rel = f"{prefix.rstrip('/')}/{rel}"
        out.append((p, rel))
    return out


def decide_strategy(provider: str, size: int) -> dict:
    """Choose simple vs. chunked upload based on the platform threshold."""
    pol = CHUNK_POLICY[provider]
    mb = size / (1024 * 1024)
    if mb <= pol["simple_max_mb"]:
        return {"mode": "simple", "chunks": 1, "chunk_size_mb": None}
    chunk_mb = pol["chunk_mb"]
    chunk_bytes = chunk_mb * 1024 * 1024
    chunks = (size + chunk_bytes - 1) // chunk_bytes
    return {"mode": "slice", "chunks": chunks, "chunk_size_mb": chunk_mb}


def build_manifest(root: Path, remote: str, provider: str,
                   files: list) -> dict:
    """Build the upload plan (manifest): file list + size + target path + strategy."""
    entries = []
    total = 0
    for path, rel in files:
        size = path.stat().st_size
        total += size
        entries.append({
            "local": str(path),
            "relative": rel,
            "size": size,
            "size_human": fmt_size(size),
            "remote_path": f"{remote.rstrip('/')}/{rel}",
            **decide_strategy(provider, size),
        })
    return {
        "provider": provider,
        "source_dir": str(root.resolve()),
        "remote_root": remote,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file_count": len(entries),
        "total_bytes": total,
        "total_human": fmt_size(total),
        "will_create_dirs": sorted({
            str(Path(e["remote_path"]).parent) for e in entries
        }),
        "files": entries,
    }


def cmd_plan_upload(args) -> int:
    exclude = [x.strip() for x in (args.exclude or "").split(",") if x.strip()]
    root = Path(args.dir)
    files = collect_files(root, args.prefix or "", exclude)

    print(f"# DRY-RUN: upload plan (nothing uploaded)")
    print(f"# source dir: {root.resolve()}")
    print(f"# target drive: {args.provider}  remote root: {args.remote}")
    print(f"# credentials: read from env vars; not written to disk, not printed")
    print()

    if not files:
        # An empty list is not success: having nothing to upload means this archive
        # does nothing. Returning 0 would make the caller think "the plan is ready".
        # Return non-zero with a reason so the pipeline stops here (instead of walking
        # to the upload step with an empty plan before noticing).
        return _die(
            f"no uploadable files under {root.resolve()} (or all excluded by --exclude). "
            "Check the source path and whether --exclude globs are too broad."
        )

    manifest = build_manifest(root, args.remote, args.provider, files)

    print(f"{manifest['file_count']} files, total {manifest['total_human']}")
    print()
    print("## File list")
    print(f"{'relative path':<48}{'size':>10}  {'strategy'}")
    for e in manifest["files"]:
        strategy = "simple" if e["mode"] == "simple" else \
            f"slice x{e['chunks']} ({e['chunk_size_mb']}MB/chunk)"
        rel = e["relative"]
        if len(rel) > 46:
            rel = "..." + rel[-43:]
        print(f"{rel:<48}{e['size_human']:>10}  {strategy}")
    print()

    print("## Remote directories to create")
    for d in manifest["will_create_dirs"]:
        print(f"  {d}/")
    print()

    print("## Chunking rationale")
    pol = CHUNK_POLICY[args.provider]
    print(f"- {pol['note']}")
    print(f"- instant-upload / dedup key algorithm: {HASH_ALGO[args.provider]}")
    print()

    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"# manifest written to {args.manifest}")
    print("# Nothing uploaded. After confirming the list, the AI/user attaches")
    print("# credentials to run the upload; then compare per-file against checksum-plan")
    print("# results to verify integrity.")
    return 0


# ---------------------------------------------------------------------------
# checksum-plan
# ---------------------------------------------------------------------------
def hash_file(path: Path, algo: str, block: int = 1 << 20) -> str:
    """Stream the file digest without reading the whole file into memory."""
    h = hashlib.new(algo)
    with path.open("rb") as fh:
        while True:
            buf = fh.read(block)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def cmd_checksum_plan(args) -> int:
    algo = args.algo
    if algo not in SUPPORTED_ALGOS:
        return _die(f"unsupported algorithm '{algo}'; use {', '.join(SUPPORTED_ALGOS)}")

    exclude = [x.strip() for x in (args.exclude or "").split(",") if x.strip()]
    root = Path(args.dir)
    if not root.is_dir():
        return _die(f"not a directory: {root}")

    files = collect_files(root, "", exclude)
    if not files:
        # Same as plan-upload: computing no digest is not success but "wrong source
        # dir or everything excluded". Returning 0 would let the caller treat the
        # empty list as a valid checksum basis, and a later sha256sum -c would pass
        # with zero rows while masking the real problem.
        return _die(
            f"no files to checksum under {root.resolve()} (or all excluded by --exclude). "
            "Check the source path and --exclude globs."
        )

    lines = []
    total = 0
    for path, rel in files:
        digest = hash_file(path, algo)
        size = path.stat().st_size
        total += size
        # Use the `hash  *path` two-space format: binary-mode marker, so sha256sum -c can verify directly
        lines.append(f"{digest}  {rel}")

    header = [
        f"# {algo} checksum list",
        f"# source dir: {root.resolve()}",
        f"# generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"# file count: {len(files)}  total: {fmt_size(total)}",
        f"# verify with: {algo}sum -c <this file>",
        "",
    ]
    text = "\n".join(header + lines) + "\n"

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"# written to {args.output}")
        print(f"# algorithm: {algo}  files: {len(files)}  total: {fmt_size(total)}")
        print(f"# verify command: {algo}sum -c {args.output}")
    else:
        sys.stdout.write(text)
    return 0


# ---------------------------------------------------------------------------
# parse-list
# ---------------------------------------------------------------------------
def _norm_entry(provider: str, item: dict) -> dict:
    """Normalize the three providers' list-entry field names into (name, size,
    is_dir, mtime, id).

    The three use completely different field names: OneDrive distinguishes type via
    `folder`/`file` sub-objects, Baidu uses an integer `isdir`, and Aliyun uses a
    `type` string.
    """
    if provider == "baidu":
        return {
            "name": Path(item.get("path", "")).name or item.get("server_filename", ""),
            "path": item.get("path", ""),
            "size": item.get("size", 0),
            "is_dir": item.get("isdir") == 1,
            "mtime": item.get("server_mtime", 0),
            "id": item.get("fs_id", ""),
        }
    if provider == "aliyun":
        return {
            "name": item.get("name", ""),
            "path": item.get("path", ""),
            "size": item.get("size", 0),
            "is_dir": item.get("type", "") == "folder",
            "mtime": item.get("updated_at", ""),
            "id": item.get("file_id", ""),
        }
    # onedrive
    is_dir = "folder" in item
    return {
        "name": item.get("name", ""),
        "path": (item.get("parentReference") or {}).get("path", ""),
        "size": (item.get("size", 0) if not is_dir else 0),
        "is_dir": is_dir,
        "mtime": item.get("lastModifiedDateTime", ""),
        "id": item.get("id", ""),
    }


def cmd_parse_list(args) -> int:
    raw = _load_json(args.json, "--json")
    provider = args.provider

    if isinstance(raw, dict):
        items = raw.get(LIST_KEY[provider]) or raw.get("files") or []
    elif isinstance(raw, list):
        items = raw
    else:
        return _die("--json must be a list-response object or an entry array")

    if not items:
        print(f"# {provider} list: 0 entries")
        return 0

    entries = [_norm_entry(provider, it) for it in items]
    dirs = [e for e in entries if e["is_dir"]]
    files = [e for e in entries if not e["is_dir"]]
    total = sum(e["size"] for e in files)

    print(f"# {provider} directory listing: {len(entries)} entries"
          f" ({len(dirs)} dirs, {len(files)} files, files total {fmt_size(total)})")
    print()
    print(f"{'type':<6}{'name':<40}{'size':>10}  id")
    for e in sorted(entries, key=lambda x: (not x["is_dir"], x["name"])):
        kind = "DIR" if e["is_dir"] else "FILE"
        size = "-" if e["is_dir"] else fmt_size(e["size"])
        name = e["name"]
        if len(name) > 38:
            name = name[:35] + "..."
        print(f"{kind:<6}{name:<40}{size:>10}  {e['id']}")

    # Double-confirmation reminder for deletes: list parsing is the mandatory step
    # before a delete, so intercept it here.
    print()
    print(f"# If you plan to delete these entries -- {DELETE_CONFIRM}")
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="drive_ops.py",
        description="Cloud-drive upload plan, checksum list, and list parsing (offline read-only; no upload, no delete)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("plan-upload", help="generate an upload plan (does not upload)")
    s.add_argument("--dir", required=True, help="local source directory")
    s.add_argument("--remote", required=True, help="remote root path, e.g. /archive/2026")
    s.add_argument("--provider", choices=["baidu", "aliyun", "onedrive"],
                   default="baidu")
    s.add_argument("--prefix", default="", help="sub-path prepended to relative paths")
    s.add_argument("--exclude", default="", help="comma-separated globs, e.g. *.tmp,.DS_Store")
    s.add_argument("--manifest", help="write the plan to a JSON file")
    s.set_defaults(func=cmd_plan_upload)

    s = sub.add_parser("checksum-plan", help="generate a sha256/md5/sha1 checksum list")
    s.add_argument("--dir", required=True)
    s.add_argument("--output", help="output file; defaults to stdout")
    s.add_argument("--algo", choices=list(SUPPORTED_ALGOS), default="sha256")
    s.add_argument("--exclude", default="")
    s.set_defaults(func=cmd_checksum_plan)

    s = sub.add_parser("parse-list", help="parse a cloud-drive list response into a readable table")
    s.add_argument("--json", required=True)
    s.add_argument("--provider", choices=["baidu", "aliyun", "onedrive"],
                   default="baidu")
    s.set_defaults(func=cmd_parse_list)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except PlanError as e:
        return _die(str(e))


if __name__ == "__main__":
    sys.exit(main())
