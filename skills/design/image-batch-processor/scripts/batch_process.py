#!/usr/bin/env python3
"""batch_process.py -- batch-resize, compress, crop, watermark, convert and OCR images.

A local image workbench built on Pillow. Given an input directory (or a single
image), it walks the matching files, applies a fixed pipeline in order
(resize -> crop -> watermark -> compress/format), and writes each result to the
output directory while preserving the input's relative path. Nothing touches
the original files; dry-run prints the planned operations without writing.

Pipeline order is fixed and intentional:
    resize (fit, keep aspect ratio) -> crop (exact box) -> watermark overlay
    -> re-save (compress quality / target format).

Design principles
-----------------
1. **Never touch the source**: outputs always go under --output; originals are
   only opened for reading.
2. **One bad file must not stop the batch**: a corrupt image, unsupported pixel
   mode, or permission error is logged as [skip] and the run continues.
3. **Preview first**: `--dry-run` lists every planned operation; no file is
   written until it is off.

Examples
--------
  # Plan only: resize a folder of photos to a 1920x1080 box, re-save as JPEG q80
  python3 batch_process.py --input photos/ --output out/ --resize 1920x1080 \
      --compress 80 --dry-run

  # Run: fit longest side to 1080, add a bottom-right text watermark, convert webp
  python3 batch_process.py --input photos/ --output out/ --resize 1080 \
      --watermark-text "CONFIDENTIAL" --watermark-opacity 0.3 --format webp

Required: Pillow. Optional: pytesseract (+ a tesseract binary) for --ocr.
Python >= 3.8.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    print(
        "ERROR: Pillow is required. Install it with: pip install pillow",
        file=sys.stderr,
    )
    sys.exit(2)

# Pixel-mode RGB background used when flattening images that carry an alpha
# channel (JPEG has no alpha channel; compositing over white is the safe default).
FLATTEN_BACKGROUND = (255, 255, 255)

# Allowed output formats mapped to Pillow save format names.
FORMAT_MAP = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}

# Margin (px) between the watermark and the image edge for corner placements.
WATERMARK_MARGIN = 12


def parse_resize(spec: str):
    """Parse --resize into a bounding box (W,H) or a single max-side length.

    Returns either:
      * ("box", (width, height))  -- fit inside this box, keep aspect ratio
      * ("maxside", N)            -- scale so the longest edge == N
    """
    spec = spec.strip().lower()
    if "x" in spec:
        parts = spec.split("x", 1)
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            w, h = int(parts[0]), int(parts[1])
            if w > 0 and h > 0:
                return ("box", (w, h))
    elif spec.isdigit():
        n = int(spec)
        if n > 0:
            return ("maxside", n)
    raise ValueError(
        f"--resize must be WxH (e.g. 1920x1080) or a single max dimension (e.g. 1080); got '{spec}'"
    )


def parse_crop(spec: str):
    """Parse --crop WxH+X+Y into a PIL crop box (left, upper, right, lower)."""
    # Format: WxH+X+Y  (e.g. 800x600+100+50)
    try:
        size_part, rest = spec.split("+", 1)
        w_s, h_s = size_part.lower().split("x")
        x_s, y_s = rest.split("+")
        w, h, x, y = int(w_s), int(h_s), int(x_s), int(y_s)
        if w <= 0 or h <= 0:
            raise ValueError
        return (x, y, x + w, y + h)
    except (ValueError, AttributeError):
        raise ValueError(
            f"--crop must be WxH+X+Y (e.g. 800x600+100+50); got '{spec}'"
        )


def apply_resize(img: Image.Image, spec) -> Image.Image:
    """Resize preserving aspect ratio (fit). Never upscales beyond source size."""
    kind, value = spec
    w, h = img.size
    if kind == "box":
        box_w, box_h = value
        # thumbnail() keeps aspect ratio and only downscales when the image is
        # larger than the box; it does not enlarge small images. It mutates the
        # image in place and returns None, so operate on an explicit copy.
        if w > box_w or h > box_h:
            resized = img.copy()
            resized.thumbnail((box_w, box_h), Image.LANCZOS)
            return resized
        return img
    # maxside: scale so the longer edge equals value.
    longest = max(w, h)
    if longest <= value:
        return img
    scale = value / float(longest)
    new_size = (max(1, round(w * scale)), max(1, round(h * scale)))
    return img.resize(new_size, Image.LANCZOS)


def apply_crop(img: Image.Image, box) -> Image.Image:
    """Crop to an explicit (left, upper, right, lower) box."""
    return img.crop(box)


def _load_font(size: int):
    """Best-effort TrueType font at the requested size, with a default fallback."""
    for name in ("DejaVuSans.ttf", "Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _anchor_position(img_w: int, img_h: int, wm_w: int, wm_h: int, position: str):
    """Compute the (left, upper) paste coordinate for a watermark of given size."""
    m = WATERMARK_MARGIN
    if position == "center":
        return ((img_w - wm_w) // 2, (img_h - wm_h) // 2)
    if position == "top-left":
        return (m, m)
    if position == "top-right":
        return (img_w - wm_w - m, m)
    if position == "bottom-left":
        return (m, img_h - wm_h - m)
    # default: bottom-right
    return (img_w - wm_w - m, img_h - wm_h - m)


def apply_watermark(img: Image.Image, args) -> Image.Image:
    """Overlay a text or image watermark with the chosen position and opacity."""
    if not args.watermark_text and not args.watermark_image:
        return img

    base = img.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))

    if args.watermark_text:
        draw = ImageDraw.Draw(overlay)
        font = _load_font(args.watermark_size)
        # Measure text so we can anchor it correctly.
        try:
            bbox = draw.textbbox((0, 0), args.watermark_text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:  # very old Pillow
            tw, th = draw.textsize(args.watermark_text, font=font)
        left, upper = _anchor_position(base.size[0], base.size[1], tw, th,
                                       args.watermark_position)
        alpha = int(255 * max(0.0, min(1.0, args.watermark_opacity)))
        draw.text((left, upper), args.watermark_text, font=font,
                  fill=(255, 255, 255, alpha))
    else:
        wm_path = Path(args.watermark_image)
        if not wm_path.is_file():
            print(f"   [skip] watermark image not found: {wm_path}", file=sys.stderr)
            return img
        wm = Image.open(wm_path).convert("RGBA")
        # Apply opacity to the watermark's alpha channel.
        alpha = wm.split()[-1].point(lambda p: int(p * max(0.0, min(1.0, args.watermark_opacity))))
        wm.putalpha(alpha)
        left, upper = _anchor_position(base.size[0], base.size[1], wm.size[0],
                                       wm.size[1], args.watermark_position)
        overlay.paste(wm, (left, upper), wm)

    return Image.alpha_composite(base, overlay)


def save_image(img: Image.Image, out_path: Path, args) -> str:
    """Save the image honoring --compress (JPEG quality) and --format.

    Returns the actual Pillow format used.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Decide target format: explicit --format wins; --compress implies JPEG.
    if args.format:
        target = FORMAT_MAP[args.format]
    elif args.compress is not None:
        target = "JPEG"
    else:
        target = img.format or "PNG"

    save_kwargs = {}
    if target == "JPEG":
        # JPEG cannot carry alpha; flatten onto the background.
        if img.mode in ("RGBA", "LA", "P"):
            flat = Image.new("RGB", img.size, FLATTEN_BACKGROUND)
            flat.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            img = flat
        else:
            img = img.convert("RGB")
        quality = args.compress if args.compress is not None else 85
        save_kwargs["quality"] = int(quality)
        save_kwargs["optimize"] = True
    elif target == "PNG":
        img = img.convert("RGBA" if img.mode in ("RGBA", "LA") else "RGB")
    elif target == "WEBP":
        quality = args.compress if args.compress is not None else 85
        save_kwargs["quality"] = int(quality)

    img.save(out_path, target, **save_kwargs)
    return target


def output_extension(target_format: str) -> str:
    ext = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}.get(target_format, ".png")
    return ext


def collect_inputs(input_path: Path, recursive: bool, patterns: set) -> list[Path]:
    """Return the list of image files to process."""
    if input_path.is_file():
        return [input_path]
    if not input_path.is_dir():
        print(f"ERROR: input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(2)
    walker = input_path.rglob("*") if recursive else input_path.glob("*")
    return sorted(
        p for p in walker
        if p.is_file() and p.suffix.lower().lstrip(".") in patterns
    )


def run_ocr(img: Image.Image, out_txt: Path, dry_run: bool) -> None:
    """Best-effort OCR: write extracted text next to the output image."""
    try:
        import pytesseract  # type: ignore
    except ImportError:
        print("   [warn] --ocr requested but pytesseract is not installed; "
              "skipping OCR. Install with: pip install pytesseract (and a tesseract binary).",
              file=sys.stderr)
        return
    if dry_run:
        print(f"   [dry-run] would OCR -> {out_txt.name}")
        return
    try:
        text = pytesseract.image_to_string(img)
        out_txt.write_text(text, encoding="utf-8")
        print(f"   [ocr] text -> {out_txt}")
    except Exception as exc:  # tesseract binary missing, corrupt image, etc.
        print(f"   [skip] OCR failed: {exc}", file=sys.stderr)


def run(args) -> int:
    input_path = Path(args.input)
    output_dir = Path(args.output)
    patterns = {p.strip().lower().lstrip(".") for p in args.patterns.split(",") if p.strip()}

    # Parse operation specs up front so bad input fails fast, before scanning.
    resize_spec = parse_resize(args.resize) if args.resize else None
    crop_box = parse_crop(args.crop) if args.crop else None

    files = collect_inputs(input_path, args.recursive, patterns)
    if not files:
        print(f"No matching images under {input_path} (patterns: {', '.join(sorted(patterns))}).")
        return 0

    # The directory that defines the "relative path" we preserve in output.
    base = input_path if input_path.is_dir() else input_path.parent

    planned = 0
    done = skipped = 0
    for path in files:
        rel = path.relative_to(base)
        planned += 1

        # Decide output stem/extension (format may change the suffix).
        target = None
        if args.format:
            target = FORMAT_MAP[args.format]
        elif args.compress is not None:
            target = "JPEG"
        new_ext = output_extension(target) if target else path.suffix
        out_path = output_dir / rel.with_suffix(new_ext)

        ops = []
        if resize_spec:
            ops.append(f"resize={args.resize}")
        if crop_box:
            ops.append(f"crop={args.crop}")
        if args.watermark_text:
            ops.append(f"watermark-text='{args.watermark_text}'@{args.watermark_position}")
        if args.watermark_image:
            ops.append(f"watermark-image={args.watermark_image}@{args.watermark_position}")
        if args.compress is not None:
            ops.append(f"compress=q{args.compress}")
        if args.format:
            ops.append(f"format={args.format}")
        op_str = ", ".join(ops) if ops else "copy (no transform)"

        if args.dry_run:
            print(f"[dry-run] {rel} -> {out_path}  [{op_str}]")
            if args.ocr:
                print(f"[dry-run]   OCR -> {out_path.with_suffix('.txt')}")
            done += 1
            continue

        try:
            with Image.open(path) as opened:
                opened.load()
                img = opened.convert("RGBA") if opened.mode not in ("RGB", "RGBA") else opened.copy()

                if resize_spec:
                    img = apply_resize(img, resize_spec)
                if crop_box:
                    img = apply_crop(img, crop_box)
                if args.watermark_text or args.watermark_image:
                    img = apply_watermark(img, args)

                save_image(img, out_path, args)
                print(f"[ok] {rel} -> {out_path}")
                done += 1

                if args.ocr:
                    run_ocr(img, out_path.with_suffix(".txt"), dry_run=False)
        except (OSError, ValueError) as exc:
            # Corrupt file, unsupported format, truncated image, permission error.
            print(f"[skip] {rel}: {exc}", file=sys.stderr)
            skipped += 1
        except Exception as exc:  # never let one bad file crash the whole batch
            print(f"[skip] {rel}: unexpected error: {exc}", file=sys.stderr)
            skipped += 1

    print()
    if args.dry_run:
        print(f"DRY-RUN: planned {planned} image(s); no files written.")
    else:
        print(f"Done: processed {done}, skipped {skipped}, out of {planned}.")
    return 0 if skipped == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="batch_process.py",
        description="Batch-process images with Pillow: resize (fit), crop, "
                    "watermark, compress, format-convert, and optional OCR. "
                    "Dry-run prints the plan; originals are never modified.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--input", required=True, help="input image file or directory (required)")
    p.add_argument("--output", required=True, help="output directory (required)")
    p.add_argument("--recursive", action="store_true", help="process subdirectories recursively")
    p.add_argument("--compress", type=int, default=None, metavar="QUALITY",
                   help="JPEG quality 1-95; if set without --format, re-saves as JPEG")
    p.add_argument("--resize", default=None,
                   help="WxH box (e.g. 1920x1080) or max side (e.g. 1080); keeps aspect ratio")
    p.add_argument("--crop", default=None, help="crop box WxH+X+Y (e.g. 800x600+100+50)")
    p.add_argument("--watermark-text", default=None, help="text to overlay as a watermark")
    p.add_argument("--watermark-image", default=None, help="path to a PNG watermark image")
    p.add_argument("--watermark-position", default="bottom-right",
                   choices=["center", "top-left", "top-right", "bottom-left", "bottom-right"],
                   help="watermark anchor (default: bottom-right)")
    p.add_argument("--watermark-opacity", type=float, default=0.3,
                   help="watermark opacity 0.1-1.0 (default: 0.3)")
    p.add_argument("--watermark-size", type=int, default=36,
                   help="font size for text watermark (default: 36)")
    p.add_argument("--format", default=None, choices=["jpg", "png", "webp"],
                   help="output format; keep original extension if not set")
    p.add_argument("--ocr", action="store_true",
                   help="extract text from each image with pytesseract (writes a .txt alongside)")
    p.add_argument("--dry-run", action="store_true", help="print the operation plan, write nothing")
    p.add_argument("--patterns", default="jpg,jpeg,png,webp,bmp,tiff",
                   help="comma-separated extensions to process (default: jpg,jpeg,png,webp,bmp,tiff)")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
