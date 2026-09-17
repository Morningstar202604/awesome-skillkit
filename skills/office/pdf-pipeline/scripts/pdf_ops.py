#!/usr/bin/env python3
"""pdf_ops.py — page-level PDF operations built on pypdf.

Subcommands:
  merge    Concatenate several PDFs into one.
  split    Cut one PDF into several files by page ranges (or per page).
  extract  Pull text out, each page tagged with its page number.
  meta     Read or rewrite document metadata; probe AcroForm fields.
  rotate   Turn selected pages by 90/180/270 degrees.

Original code written for the awesome-skillkit collection (Apache-2.0).
"""

import argparse
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    sys.exit("pypdf is required: pip install pypdf")

META_KEYS = ("Title", "Author", "Subject", "Keywords", "Creator", "Producer")


def open_reader(path):
    """Open a PDF, turning missing/encrypted/broken files into a clean exit(1)."""
    if not Path(path).exists():
        sys.exit(f"ERROR: 文件不存在：{path}")
    try:
        reader = PdfReader(path)
        if reader.is_encrypted:
            sys.exit(f"ERROR: {path} 有口令保护，请提供解密后的副本")
        return reader
    except SystemExit:
        raise
    except Exception as exc:
        sys.exit(f"ERROR: 无法读取 {path}（{exc}）")


def parse_pages(spec, total):
    """Turn '1-3,5' (1-based, inclusive) into a sorted 0-based page list."""
    picked = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            lo, hi = int(lo), int(hi)
            if not (1 <= lo <= hi <= total):
                sys.exit(f"range '{part}' out of bounds (1..{total})")
            picked.update(range(lo - 1, hi))
        else:
            i = int(part)
            if not (1 <= i <= total):
                sys.exit(f"page '{part}' out of bounds (1..{total})")
            picked.add(i - 1)
    return sorted(picked)


def load_writer_from(reader):
    writer = PdfWriter()
    writer.append(reader)
    return writer


def cmd_merge(args):
    writer = PdfWriter()
    total = 0
    for path in args.inputs:
        reader = open_reader(path)
        writer.append(reader)
        total += len(reader.pages)
        print(f"  + {path} ({len(reader.pages)} pages)")
    writer.write(args.output)
    print(f"merged: {args.output} ({total} pages)")


def cmd_split(args):
    reader = open_reader(args.input)
    total = len(reader.pages)
    base = Path(args.input).stem
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    if args.per_page:
        groups = [[i] for i in range(total)]
        labels = [str(i + 1) for i in range(total)]
    elif args.ranges:
        groups, labels = [], []
        for part in args.ranges.split(","):
            pages = parse_pages(part, total)
            groups.append(pages)
            labels.append(part.strip().replace(",", "-"))
    else:
        sys.exit("give --ranges '1-3,4' or --per-page; nothing to do")
    for group, label in zip(groups, labels):
        writer = PdfWriter()
        for i in group:
            writer.add_page(reader.pages[i])
        out = outdir / f"{base}_{label}.pdf"
        writer.write(out)
        print(f"  wrote {out} ({len(group)} pages)")
    print(f"split done: {len(groups)} file(s) in {outdir}")


def cmd_extract(args):
    reader = open_reader(args.input)
    total = len(reader.pages)
    pages = parse_pages(args.pages, total) if args.pages else range(total)
    chunks = []
    empty = 0
    for i in pages:
        text = reader.pages[i].extract_text() or ""
        if not text.strip():
            empty += 1
        chunks.append(f"=== page {i + 1}/{total} ===\n{text.strip()}")
    result = "\n\n".join(chunks) + "\n"
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"extracted {len(pages)} page(s) -> {args.output}")
    else:
        print(result, end="")
    if empty == len(list(pages)) and len(list(pages)) > 0:
        print("[warn] no text layer on any selected page; "
              "this looks like a scanned PDF — run OCR first "
              "(e.g. ocrmypdf in.pdf out.pdf)", file=sys.stderr)


def cmd_meta(args):
    reader = open_reader(args.input)
    info = reader.metadata or {}
    print(f"file: {args.input}")
    print(f"pages: {len(reader.pages)}")
    for key in META_KEYS:
        value = info.get(f"/{key}", "")
        if value:
            print(f"{key}: {value}")
    fields = reader.get_fields()
    if fields:
        print(f"form fields ({len(fields)}):")
        for name, spec in fields.items():
            print(f"  - {name} [{spec.get('/FT', '?')}]")
    else:
        print("form fields: none")
    if args.set:
        writer = load_writer_from(reader)
        updates = {}
        for pair in args.set:
            key, _, value = pair.partition("=")
            key = key.strip()
            if key not in META_KEYS:
                sys.exit(f"key '{key}' not in {META_KEYS}")
            updates[f"/{key}"] = value
        writer.add_metadata(updates)
        target = args.output or args.input
        writer.write(target)
        print(f"metadata written -> {target}")
        for key, value in updates.items():
            print(f"  {key[1:]}: {value}")


def cmd_rotate(args):
    reader = open_reader(args.input)
    total = len(reader.pages)
    if args.degrees % 90 != 0:
        sys.exit("degrees must be a multiple of 90")
    indices = range(total) if args.pages == "all" else parse_pages(args.pages, total)
    writer = PdfWriter()
    rotated = set()
    for i in range(total):
        page = reader.pages[i]
        if i in list(indices):
            page.rotate(args.degrees)
            rotated.add(i + 1)
        writer.add_page(page)
    writer.write(args.output)
    print(f"rotated {sorted(rotated)} by {args.degrees}° -> {args.output}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("merge", help="concatenate PDFs into one")
    p.add_argument("inputs", nargs="+", help="input PDFs, in join order")
    p.add_argument("--output", required=True, help="merged output path")
    p.set_defaults(func=cmd_merge)

    p = sub.add_parser("split", help="split by page ranges or per page")
    p.add_argument("input", help="PDF to split")
    p.add_argument("--ranges", default="", help="'1-3,5' style, one file per group")
    p.add_argument("--per-page", action="store_true", help="one file per page")
    p.add_argument("--outdir", default="split_out", help="output directory")
    p.set_defaults(func=cmd_split)

    p = sub.add_parser("extract", help="extract text with page tags")
    p.add_argument("input", help="PDF to read")
    p.add_argument("--pages", default="", help="restrict to '1-3,5'")
    p.add_argument("--output", default="", help="write to file instead of stdout")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("meta", help="read/rewrite metadata, probe form fields")
    p.add_argument("input", help="PDF to inspect or modify")
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                   help=f"set metadata key ({', '.join(META_KEYS)}), repeatable")
    p.add_argument("--output", default="", help="save-as path (default: in place)")
    p.set_defaults(func=cmd_meta)

    p = sub.add_parser("rotate", help="rotate pages by 90/180/270")
    p.add_argument("input", help="PDF to modify")
    p.add_argument("--degrees", type=int, default=90, choices=(90, 180, 270))
    p.add_argument("--pages", default="all", help="'all' or '1-3,5'")
    p.add_argument("--output", required=True, help="output path")
    p.set_defaults(func=cmd_rotate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
