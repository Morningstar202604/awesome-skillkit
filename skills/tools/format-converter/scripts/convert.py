#!/usr/bin/env python3
"""convert.py -- 格式转换统一入口（文档 / 图片 / 音视频 / 批量）。

设计原则
--------
1. **依赖先探测再调用**：每个子命令开工前先 `shutil.which` 找二进制、`import` 找库，
   缺失时给出针对当前系统的确切安装命令，而不是抛一个 FileNotFoundError 让人猜。
2. **绝不覆盖输入**：输出路径与任一输入路径相同（含 realpath 后相同）时直接拒绝。
3. **不静默降级**：转不了就说转不了，不产出半成品文件冒充成功。
4. **批量不中断**：`batch` 模式单个文件失败只记录，继续处理其余文件。

子命令
------
  doc   <in> <out> [--pdf-engine X]        文档转换（pandoc）
  image <in> <out> [--width N] [--quality Q]  图片转换/缩放（Pillow）
  media <in> <out> [--vcodec X] [--acodec Y]  音视频转换（ffmpeg）
  batch <dir> --to <ext> [--kind K] [--yes]    目录内批量转换（默认 dry-run）

Python >= 3.8；图片依赖 Pillow，文档依赖 pandoc，媒体依赖 ffmpeg。
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# 各类转换的扩展名归属，用于 batch 自动判断该走哪条管线
DOC_EXTS = {".md", ".markdown", ".docx", ".odt", ".rst", ".html", ".htm",
            ".tex", ".epub", ".rtf", ".txt"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif",
              ".tiff", ".ico", ".avif"}
MEDIA_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv",
              ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".opus"}

# 扩展名 -> 输出格式名，避免每次都查表
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
    """给出针对当前系统的安装命令。三平台都给，避免用户猜。"""
    hints = {
        "pandoc": {
            "macos": "brew install pandoc",
            "linux": "sudo apt-get install pandoc   # 或 sudo dnf install pandoc",
            "windows": "winget install --id JohnMacFarlane.Pandoc",
        },
        "ffmpeg": {
            "macos": "brew install ffmpeg",
            "linux": "sudo apt-get install ffmpeg   # 或 sudo dnf install ffmpeg",
            "windows": "winget install --id Gyan.FFmpeg",
        },
    }
    fam = _os_family()
    return hints.get(tool, {}).get(fam, f"请手动安装 {tool}")


def require_binary(tool: str, why: str) -> str:
    """找到二进制就返回绝对路径；否则打印安装指引并退出。"""
    path = shutil.which(tool)
    if path:
        return path
    print(f"ERROR: 找不到 `{tool}`（{why}）。", file=sys.stderr)
    print(f"  → 安装：{install_hint(tool)}", file=sys.stderr)
    print(f"  → 装好后用 `{tool} --version` 确认，再重跑本命令。", file=sys.stderr)
    raise SystemExit(4)


def require_pillow():
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("ERROR: 图片转换需要 Pillow，当前环境未安装。", file=sys.stderr)
        print("  → 安装：python3 -m pip install pillow", file=sys.stderr)
        print("  → 装好后 `python3 -c \"import PIL;print(PIL.__version__)\"` 确认。",
              file=sys.stderr)
        raise SystemExit(4)
    from PIL import Image
    return Image


def _same_path(a: Path, b: Path) -> bool:
    """realpath 后比较，挡住 in/out 指向同一文件的自我覆盖。"""
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return False


def _guard(inp: Path, outp: Path) -> None:
    if not inp.exists():
        print(f"ERROR: 输入文件不存在: {inp}", file=sys.stderr)
        raise SystemExit(1)
    if _same_path(inp, outp):
        print(f"ERROR: 输出路径与输入相同（{outp}），会破坏源文件。请换输出名。",
              file=sys.stderr)
        raise SystemExit(2)
    outp.parent.mkdir(parents=True, exist_ok=True)


def _run(cmd: list, action: str) -> int:
    print(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"ERROR: {action} 失败 (rc={proc.returncode})", file=sys.stderr)
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        for line in tail[-12:]:
            print(f"  | {line}", file=sys.stderr)
        return proc.returncode
    return 0


# --------------------------------------------------------------------------
# doc
# --------------------------------------------------------------------------
def cmd_doc(args) -> int:
    inp, outp = Path(args.input), Path(args.output)
    _guard(inp, outp)
    pandoc = require_binary("pandoc", "文档转换需要它")

    src_fmt = DOC_FORMATS.get(inp.suffix.lower())
    dst_fmt = DOC_FORMATS.get(outp.suffix.lower())
    unknown = [e for e in (src_fmt, dst_fmt) if e is None]
    if unknown:
        print(f"ERROR: 无法从扩展名推断格式（{inp.suffix} -> {outp.suffix}）。",
              file=sys.stderr)
        print(f"  支持：{' '.join(sorted(set(DOC_FORMATS)))}", file=sys.stderr)
        print("  其他格式请显式指定：pandoc -f <from> -t <to>", file=sys.stderr)
        return 3

    cmd = [pandoc, str(inp)]
    # 显式指定 -f/-t：pandoc 对 .tex/.rst 的自动识别在部分版本上不一致
    cmd += ["-f", src_fmt, "-t", dst_fmt]
    if args.pdf_engine and dst_fmt == "latex":
        cmd += ["--pdf-engine", args.pdf_engine]
    cmd += ["-o", str(outp)]

    rc = _run(cmd, "文档转换")
    if rc == 0:
        print(f"OK: {inp} -> {outp}  ({outp.stat().st_size} bytes)")
    elif rc == 47 or "xelatex" in (args.pdf_engine or ""):
        print("  → PDF 输出需要 LaTeX 引擎，尝试："
              f"{install_hint('pandoc')} 之外再装 texlive", file=sys.stderr)
    return rc


# --------------------------------------------------------------------------
# image
# --------------------------------------------------------------------------
def cmd_image(args) -> int:
    Image = require_pillow()
    inp, outp = Path(args.input), Path(args.output)
    _guard(inp, outp)
    if outp.suffix.lower() not in IMAGE_EXTS:
        print(f"WARN: 输出扩展名 {outp.suffix} 不是常见图片格式，按内容尝试写出。",
              file=sys.stderr)

    with Image.open(inp) as im:
        orig = f"{im.width}x{im.height}"
        src_mode = im.mode
        if args.width and args.width != im.width:
            ratio = args.width / im.width
            new_h = max(1, round(im.height * ratio))
            im = im.resize((args.width, new_h), Image.LANCZOS)
        # JPEG 不支持透明通道，直接存会报 "cannot write mode RGBA as JPEG"
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
    ffmpeg = require_binary("ffmpeg", "音视频转换需要它")
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(inp)]
    if args.vcodec:
        cmd += ["-c:v", args.vcodec]
    if args.acodec:
        cmd += ["-c:a", args.acodec]
    cmd += [str(outp)]
    rc = _run(cmd, "媒体转换")
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
    """目标扩展名属于哪条管线。"""
    if ext in IMAGE_EXTS:
        return "image"
    if ext in DOC_EXTS:
        return "doc"
    if ext in MEDIA_EXTS:
        return "media"
    return "unknown"


def _crosses_lane(src_kind: str, dst_lane: str) -> bool:
    """源与目标是否跨管线。

    跨管线转换（如 .mp4 -> .jpg、.md -> .jpg）不是本工具支持的场景：
    前者需要抽帧、后者需要渲染，都属于另一类任务。放行只会产出垃圾文件，
    因此在计划阶段就拦下并给出明确原因。
    """
    return src_kind != dst_lane


def cmd_batch(args) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        print(f"ERROR: 不是目录: {root}", file=sys.stderr)
        return 1
    target_ext = args.to if args.to.startswith(".") else f".{args.to}"
    dst_lane = args.kind if args.kind != "auto" else _lane_of_ext(target_ext)
    if dst_lane == "unknown":
        print(f"ERROR: 目标扩展名 {target_ext} 不属于任何已知管线。", file=sys.stderr)
        print(f"  图片：{' '.join(sorted(IMAGE_EXTS))}", file=sys.stderr)
        print(f"  文档：{' '.join(sorted(DOC_EXTS))}", file=sys.stderr)
        print(f"  媒体：{' '.join(sorted(MEDIA_EXTS))}", file=sys.stderr)
        return 3

    candidates, crossed, skipped_already = [], [], []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        if p.suffix.lower() == target_ext:
            skipped_already.append(p)     # 已是目标格式
            continue
        src_kind = _kind_of(p)
        if src_kind == "unknown":
            continue
        if _crosses_lane(src_kind, dst_lane):
            crossed.append((p, src_kind))
            continue
        candidates.append(p)

    if not candidates:
        print(f"目录 {root.resolve()} 内没有可转换为 {target_ext} 的文件。")
        if crossed:
            print(f"（{len(crossed)} 个文件因跨管线被跳过，见下方说明）")
        for p, kind in crossed:
            print(f"  [skip:跨管线 {kind}->{dst_lane}] {p.relative_to(root)}")
        return 0

    print(f"# 批量转换: {root.resolve()}  ->  {target_ext}  (管线: {dst_lane})")
    print(f"候选文件 {len(candidates)} 个")
    print()

    out_dir = Path(args.outdir) if args.outdir else root / f"_converted{target_ext}"
    would_skip = []
    runnable = []
    for p in candidates:
        out = out_dir / (p.stem + target_ext)
        if out.exists() and not args.overwrite:
            would_skip.append((p, out, "目标已存在"))
            continue
        runnable.append((p, out, dst_lane))

    if not args.yes:
        for p, out, kind in runnable:
            print(f"[dry-run] ({kind}) {p.relative_to(root)} -> {out.relative_to(root)}")
        for p, out, why in would_skip:
            print(f"[skip:{why}] {p.relative_to(root)}")
        for p, kind in crossed:
            print(f"[skip:跨管线 {kind}->{dst_lane}] {p.relative_to(root)}")
        print()
        print(f"DRY-RUN：将转换 {len(runnable)} 个，跳过 "
              f"{len(would_skip) + len(crossed)} 个。磁盘未变化。")
        print(f"确认后加 --yes 执行：batch {root} --to {target_ext} --yes")
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
        except SystemExit as e:          # 缺依赖时 require_* 会抛，批量模式不中断
            print(f"[fail] {p.name}: 缺少依赖（rc={e.code}）", file=sys.stderr)
            rc = 1
        ok += (rc == 0)
        fail += (rc != 0)

    print()
    print(f"完成：成功 {ok} 个，失败 {fail} 个，"
          f"跳过 {len(would_skip) + len(crossed)} 个。")
    print(f"输出目录：{out_dir}")
    return 0 if fail == 0 else 5


# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="convert.py",
        description="格式转换统一入口（文档/图片/音视频/批量），依赖缺失时给出安装指引",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("doc", help="文档转换（pandoc）")
    s.add_argument("input")
    s.add_argument("output")
    s.add_argument("--pdf-engine", default=None, help="如 xelatex / weasyprint")
    s.set_defaults(func=cmd_doc)

    s = sub.add_parser("image", help="图片转换/缩放（Pillow）")
    s.add_argument("input")
    s.add_argument("output")
    s.add_argument("--width", type=int, default=None, help="目标宽度（等比缩放）")
    s.add_argument("--quality", type=int, default=None, help="JPEG/WebP 质量 1-100")
    s.set_defaults(func=cmd_image)

    s = sub.add_parser("media", help="音视频转换（ffmpeg）")
    s.add_argument("input")
    s.add_argument("output")
    s.add_argument("--vcodec", default=None, help="如 libx264 / libvpx-vp9")
    s.add_argument("--acodec", default=None, help="如 aac / libmp3lame")
    s.set_defaults(func=cmd_media)

    s = sub.add_parser("batch", help="目录内批量转换（默认 dry-run）")
    s.add_argument("dir")
    s.add_argument("--to", required=True, help="目标扩展名，如 jpg / pdf / mp4")
    s.add_argument("--kind", choices=["auto", "image", "doc", "media"],
                   default="auto")
    s.add_argument("--outdir", default=None, help="输出目录，默认 <dir>/_converted<ext>")
    s.add_argument("--width", type=int, default=None)
    s.add_argument("--quality", type=int, default=None)
    s.add_argument("--overwrite", action="store_true")
    s.add_argument("--yes", action="store_true", help="确认执行")
    s.set_defaults(func=cmd_batch)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
