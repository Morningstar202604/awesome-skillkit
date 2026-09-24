#!/usr/bin/env python3
"""convert.py -- unified format-conversion entry point (document / image / media / batch).

Design principles
-----------------
1. **Probe dependencies before calling**: before each subcommand runs, `shutil.which` looks for
   the binary and `import` looks for the library; when something is missing it prints the exact
   install command for the current OS, rather than raising a FileNotFoundError and leaving you
   to guess.
2. **Never overwrite input**: if the output path equals any input path (even after realpath),
   refuse outright.
3. **No silent degradation**: if it can't convert, say so; never emit a half-baked file and
   call it success.
4. **Batch never halts**: in `batch` mode a single file's failure is only logged; the rest
   keep processing.

Subcommands
-----------
  doc   <in> <out> [--pdf-engine X]           document conversion (pandoc)
  image <in> <out> [--width N] [--quality Q]  image conversion/resize (Pillow)
  media <in> <out> [--vcodec X] [--acodec Y]  audio/video conversion (ffmpeg)
  batch <dir> --to <ext> [--kind K] [--yes]   batch-convert a directory (dry-run by default)

Python >= 3.8; images need Pillow, documents need pandoc, media needs ffmpeg.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# extension-to-pipeline ownership, used by batch to decide which pipeline to route to
DOC_EXTS = {".md", ".markdown", ".docx", ".odt", ".rst", ".html", ".htm",
            ".tex", ".epub", ".rtf", ".txt"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif",
              ".tiff", ".ico", ".avif"}
MEDIA_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv",
              ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".opus"}

# extension -> output format name, so we don't have to look the table up each time
DOC_FORMATS = {
    ".md": "markdown", ".markdown": "markdown", ".docx": "docx",
    ".odt": "odt", ".rst": "rst", ".html": "html", ".htm": "html",
    ".tex": "latex", ".epub": "epub", ".rtf": "rtf", ".txt": "plain",
}


def _os_family() -> str:
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    if s == "windows":
        return "windows"
    return "linux"


def install_hint(tool: str) -> str:
    """Give the install command for the current OS. Cover all three platforms so the user does not have to guess."""
    hints = {
        "pandoc": {
            "macos": "brew install pandoc",
            "linux": "sudo apt-get install pandoc   # or sudo dnf install pandoc",
            "windows": "winget install --id JohnMacFarlane.Pandoc",
        },
        "ffmpeg": {
            "macos": "brew install ffmpeg",
            "linux": "sudo apt-get install ffmpeg   # or sudo dnf install ffmpeg",
            "windows": "winget install --id Gyan.FFmpeg",
        },
    }
    fam = _os_family()
    return hints.get(tool, {}).get(fam, f"install {tool} manually")


def require_binary(tool: str, why: str) -> str:
    """Return the absolute path if the binary is found; otherwise print install guidance and exit."""
    path = shutil.which(tool)
    if path:
        return path
    print(f"ERROR: `{tool}` not found ({why}).", file=sys.stderr)
    print(f"  -> install: {install_hint(tool)}", file=sys.stderr)
    print(f"  -> after installing, confirm with `{tool} --version`, then re-run this command.", file=sys.stderr)
    raise SystemExit(4)


def require_pillow():
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("ERROR: image conversion needs Pillow, which is not installed in this environment.", file=sys.stderr)
        print("  -> install: python3 -m pip install pillow", file=sys.stderr)
        print("  -> after installing, confirm with `python3 -c \"import PIL;print(PIL.__version__)\"`.",
              file=sys.stderr)
        raise SystemExit(4)
    from PIL import Image
    return Image


def _same_path(a: Path, b: Path) -> bool:
    """Compare after realpath, blocking self-overwrite where in/out point at the same file."""
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return False


def _guard(inp: Path, outp: Path) -> None:
    if not inp.exists():
        print(f"ERROR: input file not found: {inp}", file=sys.stderr)
        raise SystemExit(1)
    if _same_path(inp, outp):
        print(f"ERROR: output path equals input ({outp}); this would destroy the source file. "
              f"Use a different output name.",
              file=sys.stderr)
        raise SystemExit(2)
    outp.parent.mkdir(parents=True, exist_ok=True)


def _run(cmd: list, action: str) -> int:
    print(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"ERROR: {action} failed (rc={proc.returncode})", file=sys.stderr)
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        for line in tail[-12:]:
            print(f"  | {line}", file=sys.stderr)
        # An external tool's exit code may fall outside [0,255] (signals are negative;
        # ffmpeg can return 234, etc.). sys.exit() only accepts 0-255, and out-of-range
        # values get truncated into a confusing number; map negatives to 1.
        rc = proc.returncode
        return rc if 0 <= rc <= 255 else 1
    return 0


# --------------------------------------------------------------------------
# doc
# --------------------------------------------------------------------------
def cmd_doc(args) -> int:
    inp, outp = Path(args.input), Path(args.output)
    _guard(inp, outp)

    src_fmt = DOC_FORMATS.get(inp.suffix.lower())
    dst_fmt = DOC_FORMATS.get(outp.suffix.lower())
    unknown = [e for e in (src_fmt, dst_fmt) if e is None]
    if unknown:
        print(f"ERROR: cannot infer format from extension ({inp.suffix} -> {outp.suffix}).",
              file=sys.stderr)
        print(f"  supported: {' '.join(sorted(set(DOC_FORMATS)))}", file=sys.stderr)
        print("  for other formats specify explicitly: pandoc -f <from> -t <to>", file=sys.stderr)
        return 3

    # Probe dependencies after the extension check: a wrong format should not first report
    # "pandoc not found" and mislead the user.
    pandoc = require_binary("pandoc", "required for document conversion")

    cmd = [pandoc, str(inp)]
    # Explicitly set -f/-t: pandoc's auto-detection of .tex/.rst is inconsistent across versions
    cmd += ["-f", src_fmt, "-t", dst_fmt]
    if args.pdf_engine and dst_fmt == "latex":
        cmd += ["--pdf-engine", args.pdf_engine]
    cmd += ["-o", str(outp)]

    rc = _run(cmd, "document conversion")
    if rc == 0:
        print(f"OK: {inp} -> {outp}  ({outp.stat().st_size} bytes)")
    elif rc == 47 or "xelatex" in (args.pdf_engine or ""):
        print("  -> PDF output needs a LaTeX engine; in addition to "
              f"{install_hint('pandoc')}, also install texlive", file=sys.stderr)
    return rc


# --------------------------------------------------------------------------
# image
# --------------------------------------------------------------------------
def cmd_image(args) -> int:
    Image = require_pillow()
    inp, outp = Path(args.input), Path(args.output)
    _guard(inp, outp)
    if outp.suffix.lower() not in IMAGE_EXTS:
        print(f"WARN: output extension {outp.suffix} is not a common image format; "
              f"trying to write based on content.",
              file=sys.stderr)

    with Image.open(inp) as im:
        orig = f"{im.width}x{im.height}"
        src_mode = im.mode
        if args.width and args.width != im.width:
            ratio = args.width / im.width
            new_h = max(1, round(im.height * ratio))
            im = im.resize((args.width, new_h), Image.LANCZOS)
        # JPEG has no alpha channel; saving directly errors with "cannot write mode RGBA as JPEG"
        fmt = (Image.registered_extensions()
               .get(outp.suffix.lower(), "").upper())
        if fmt == "JPEG" and im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGB")
        save_kw = {}
        if args.quality is not None:
            save_kw["quality"] = args.quality
        im.save(outp, **save_kw)
        print(f"OK: {inp.name} {orig}/{src_mode} -> {outp.name} "
              f"{im.width}x{im.height} ({outp.stat().st_size} bytes)")
    return 0


# --------------------------------------------------------------------------
# media
# --------------------------------------------------------------------------
def cmd_media(args) -> int:
    inp, outp = Path(args.input), Path(args.output)
    _guard(inp, outp)
    dst_ext = outp.suffix.lower()
    if dst_ext not in MEDIA_EXTS:
        print(f"ERROR: cannot infer format from extension ({inp.suffix} -> {outp.suffix}).",
              file=sys.stderr)
        print(f"  supported media outputs: {' '.join(sorted(MEDIA_EXTS))}", file=sys.stderr)
        print("  for other formats, call ffmpeg -i <in> <out> directly to set the container.",
              file=sys.stderr)
        return 3
    ffmpeg = require_binary("ffmpeg", "required for audio/video conversion")
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(inp)]
    if args.vcodec:
        cmd += ["-c:v", args.vcodec]
    if args.acodec:
        cmd += ["-c:a", args.acodec]
    cmd += [str(outp)]
    rc = _run(cmd, "media conversion")
    if rc == 0:
        print(f"OK: {inp} -> {outp}  ({outp.stat().st_size} bytes)")
    return rc


# --------------------------------------------------------------------------
# batch
# --------------------------------------------------------------------------
def _kind_of(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in DOC_EXTS:
        return "doc"
    if ext in MEDIA_EXTS:
        return "media"
    return "unknown"


def _lane_of_ext(ext: str) -> str:
    """Which pipeline an extension belongs to."""
    if ext in IMAGE_EXTS:
        return "image"
    if ext in DOC_EXTS:
        return "doc"
    if ext in MEDIA_EXTS:
        return "media"
    return "unknown"


def _crosses_lane(src_kind: str, dst_lane: str) -> bool:
    """Whether source and target cross pipelines.

    Cross-pipeline conversion (e.g. .mp4 -> .jpg, .md -> .jpg) is out of scope for this tool:
    the former needs frame extraction, the latter needs rendering; both are a different kind of
    task. Letting them through would only produce garbage files, so we block them at planning
    time with a clear reason.
    """
    return src_kind != dst_lane


def cmd_batch(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    target_ext = args.to if args.to.startswith(".") else f".{args.to}"
    dst_lane = args.kind if args.kind != "auto" else _lane_of_ext(target_ext)
    if dst_lane == "unknown":
        print(f"ERROR: target extension {target_ext} does not belong to any known pipeline.", file=sys.stderr)
        print(f"  images: {' '.join(sorted(IMAGE_EXTS))}", file=sys.stderr)
        print(f"  docs:   {' '.join(sorted(DOC_EXTS))}", file=sys.stderr)
        print(f"  media:  {' '.join(sorted(MEDIA_EXTS))}", file=sys.stderr)
        return 3

    candidates, crossed, skipped_already = [], [], []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        if p.suffix.lower() == target_ext:
            skipped_already.append(p)     # already the target format
            continue
        src_kind = _kind_of(p)
        if src_kind == "unknown":
            continue
        if _crosses_lane(src_kind, dst_lane):
            crossed.append((p, src_kind))
            continue
        candidates.append(p)

    if not candidates:
        print(f"No files convertible to {target_ext} under {root.resolve()}.")
        if crossed:
            print(f"({len(crossed)} files skipped because they cross pipelines; see notes below)")
        for p, kind in crossed:
            print(f"  [skip:cross-pipeline {kind}->{dst_lane}] {p.relative_to(root)}")
        return 0

    print(f"# batch convert: {root.resolve()}  ->  {target_ext}  (pipeline: {dst_lane})")
    print(f"{len(candidates)} candidate files")
    print()

    out_dir = Path(args.outdir) if args.outdir else root / f"_converted{target_ext}"
    would_skip = []
    runnable = []
    for p in candidates:
        out = out_dir / (p.stem + target_ext)
        if out.exists() and not args.overwrite:
            would_skip.append((p, out, "target already exists"))
            continue
        runnable.append((p, out, dst_lane))

    if not args.yes:
        for p, out, kind in runnable:
            print(f"[dry-run] ({kind}) {p.relative_to(root)} -> {out.relative_to(root)}")
        for p, out, why in would_skip:
            print(f"[skip:{why}] {p.relative_to(root)}")
        for p, kind in crossed:
            print(f"[skip:cross-pipeline {kind}->{dst_lane}] {p.relative_to(root)}")
        print()
        print(f"DRY-RUN: would convert {len(runnable)}, skip "
              f"{len(would_skip) + len(crossed)}. No disk changes made.")
        print(f"To execute after confirming, add --yes: batch {root} --to {target_ext} --yes")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for p, out, kind in runnable:
        ns = argparse.Namespace(input=str(p), output=str(out))
        try:
            if kind == "image":
                ns.width = args.width
                ns.quality = args.quality
                rc = cmd_image(ns)
            elif kind == "doc":
                ns.pdf_engine = None
                rc = cmd_doc(ns)
            else:
                ns.vcodec = None
                ns.acodec = None
                rc = cmd_media(ns)
        except SystemExit as e:          # require_* raises on missing deps; batch mode must not halt
            print(f"[fail] {p.name}: missing dependency (rc={e.code})", file=sys.stderr)
            rc = 1
        ok += (rc == 0)
        fail += (rc != 0)

    print()
    print(f"Done: {ok} succeeded, {fail} failed, "
          f"{len(would_skip) + len(crossed)} skipped.")
    print(f"Output directory: {out_dir}")
    return 0 if fail == 0 else 5


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="convert.py",
        description="Unified format-conversion entry point (document/image/media/batch); "
                    "prints install guidance when a dependency is missing",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("doc", help="document conversion (pandoc)")
    s.add_argument("input")
    s.add_argument("output")
    s.add_argument("--pdf-engine", default=None, help="e.g. xelatex / weasyprint")
    s.set_defaults(func=cmd_doc)

    s = sub.add_parser("image", help="image conversion/resize (Pillow)")
    s.add_argument("input")
    s.add_argument("output")
    s.add_argument("--width", type=int, default=None, help="target width (proportional scaling)")
    s.add_argument("--quality", type=int, default=None, help="JPEG/WebP quality 1-100")
    s.set_defaults(func=cmd_image)

    s = sub.add_parser("media", help="audio/video conversion (ffmpeg)")
    s.add_argument("input")
    s.add_argument("output")
    s.add_argument("--vcodec", default=None, help="e.g. libx264 / libvpx-vp9")
    s.add_argument("--acodec", default=None, help="e.g. aac / libmp3lame")
    s.set_defaults(func=cmd_media)

    s = sub.add_parser("batch", help="batch-convert a directory (dry-run by default)")
    s.add_argument("dir")
    s.add_argument("--to", required=True, help="target extension, e.g. jpg / pdf / mp4")
    s.add_argument("--kind", choices=["auto", "image", "doc", "media"],
                   default="auto")
    s.add_argument("--outdir", default=None, help="output directory, default <dir>/_converted<ext>")
    s.add_argument("--width", type=int, default=None)
    s.add_argument("--quality", type=int, default=None)
    s.add_argument("--overwrite", action="store_true")
    s.add_argument("--yes", action="store_true", help="confirm execution")
    s.set_defaults(func=cmd_batch)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
