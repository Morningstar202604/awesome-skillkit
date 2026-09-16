#!/usr/bin/env python3
"""docx_ops.py — a small .docx toolkit built on python-docx.

Subcommands:
  create   Build a .docx from a markdown-ish text file or a structured JSON list.
  inspect  Print a structural summary of an existing .docx.
  styles   Apply CJK fonts (eastAsia) to the paragraph styles of a .docx.

Original code written for the awesome-skillkit collection (Apache-2.0).
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.enum.style import WD_STYLE_TYPE
except ImportError:
    sys.exit("python-docx is required: pip install python-docx")

BOLD_RE = re.compile(r"(\*\*.+?\*\*)")
SEP_ROW_RE = re.compile(r"^\|?[\s:\-|]+\|?\s*$")


def add_runs_with_bold(paragraph, text):
    """Append runs to a paragraph, turning **spans** into bold runs."""
    for chunk in BOLD_RE.split(text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            run = paragraph.add_run(chunk[2:-2])
            run.bold = True
        else:
            paragraph.add_run(chunk)


def add_table(doc, rows):
    """Add a table from a list of row string-lists; first row is the header."""
    if not rows:
        return
    cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=cols)
    table.style = "Table Grid"
    for i, row in enumerate(rows):
        for j in range(cols):
            cell = table.cell(i, j)
            cell.text = ""
            add_runs_with_bold(cell.paragraphs[0], row[j] if j < len(row) else "")


def add_block(doc, kind, text, rows=None):
    """Map one structured block onto python-docx calls."""
    if kind == "table":
        add_table(doc, rows or [])
        return
    para = None
    if kind in ("h1", "h2", "h3"):
        level = {"h1": 1, "h2": 2, "h3": 3}[kind]
        style_name = f"Heading {level}"
        try:
            para = doc.add_paragraph(style=style_name)
        except KeyError:
            para = doc.add_paragraph()
            para.style = doc.styles[style_name]
        para.add_run(text)
        return
    if kind == "bullet":
        para = _styled(doc, "List Bullet", text)
    elif kind == "number":
        para = _styled(doc, "List Number", text)
    else:  # plain paragraph
        para = doc.add_paragraph()
        add_runs_with_bold(para, text)
        return
    add_runs_with_bold(para, text)


def _styled(doc, style_name, text):
    """Add a paragraph with a list style; degrade to a prefixed paragraph."""
    try:
        para = doc.add_paragraph(style=style_name)
    except KeyError:
        para = doc.add_paragraph()
        prefix = "• " if "Bullet" in style_name else "1. "
        text = prefix + text
    return para


def parse_markdownish(path):
    """Parse markdown-ish text into (kind, text, rows) tuples."""
    blocks = []
    table_buf = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if stripped.startswith("|"):
                table_buf.append(stripped)
                continue
            if table_buf:
                blocks.append(_flush_table(table_buf))
                table_buf = []
            if not stripped:
                continue
            if stripped.startswith("### "):
                blocks.append(("h3", stripped[4:].strip(), None))
            elif stripped.startswith("## "):
                blocks.append(("h2", stripped[3:].strip(), None))
            elif stripped.startswith("# "):
                blocks.append(("h1", stripped[2:].strip(), None))
            elif stripped.startswith(("- ", "* ")):
                blocks.append(("bullet", stripped[2:].strip(), None))
            elif re.match(r"^\d+[.、]\s+", stripped):
                blocks.append(("number", re.sub(r"^\d+[.、]\s+", "", stripped), None))
            else:
                blocks.append(("para", stripped, None))
    if table_buf:
        blocks.append(_flush_table(table_buf))
    return blocks


def _flush_table(buf):
    rows = []
    for line in buf:
        if SEP_ROW_RE.match(line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return ("table", "", rows)


def cmd_create(args):
    src = Path(args.input)
    doc = Document()
    if src.suffix.lower() == ".json":
        data = json.loads(src.read_text(encoding="utf-8"))
        if args.title:
            doc.add_heading(args.title, level=0)
        for item in data:
            add_block(doc, item.get("type", "para"),
                      item.get("text", ""), item.get("rows"))
    else:
        if args.title:
            doc.add_heading(args.title, level=0)
        for kind, text, rows in parse_markdownish(src):
            add_block(doc, kind, text, rows)
    doc.save(args.output)
    print(f"created: {args.output}")


def cmd_inspect(args):
    doc = Document(args.file)
    paras = doc.paragraphs
    tables = doc.tables
    style_counter = {}
    for p in paras:
        name = p.style.name if p.style is not None else "(none)"
        style_counter[name] = style_counter.get(name, 0) + 1
    print(f"file: {args.file}")
    print(f"paragraphs: {len(paras)}  tables: {len(tables)}")
    print("styles in use:")
    for name in sorted(style_counter):
        print(f"  - {name}: {style_counter[name]}")
    print("available paragraph styles:")
    names = sorted(s.name for s in doc.styles
                   if s.type == WD_STYLE_TYPE.PARAGRAPH)
    print("  " + ", ".join(names))
    print(f"preview (first {args.preview} paragraphs):")
    for i, p in enumerate(paras[: args.preview]):
        text = p.text.strip()
        if len(text) > 60:
            text = text[:57] + "..."
        print(f"  [{i}] ({p.style.name}) {text!r}")
    if tables:
        t = tables[0]
        print(f"first table: {len(t.rows)} rows x {len(t.columns)} cols")


def set_east_asia(style, font_name):
    """Set w:eastAsia on the style's rFonts so CJK glyphs use font_name."""
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), font_name)


def cmd_styles(args):
    doc = Document(args.file)
    heading_prefixes = ("Heading", "Title")
    changed = []
    for style in doc.styles:
        if style.type != WD_STYLE_TYPE.PARAGRAPH:
            continue
        is_heading = style.name.startswith(heading_prefixes)
        cjk = args.heading_font if is_heading else args.body_font
        style.font.name = args.latin_font
        set_east_asia(style, cjk)
        changed.append(f"{style.name} -> eastAsia={cjk}, latin={args.latin_font}")
    target = args.output or args.file
    doc.save(target)
    print(f"saved: {target}")
    for line in changed:
        print(f"  {line}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="build .docx from markdown-ish text or JSON")
    p.add_argument("--input", required=True, help="source .md/.txt/.json file")
    p.add_argument("--output", required=True, help="target .docx path")
    p.add_argument("--title", default="", help="optional document title (Heading 0)")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("inspect", help="print structural summary of a .docx")
    p.add_argument("file", help=".docx to inspect")
    p.add_argument("--preview", type=int, default=8,
                   help="how many leading paragraphs to show (default 8)")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("styles", help="apply CJK fonts to paragraph styles")
    p.add_argument("file", help=".docx to modify")
    p.add_argument("--body-font", default="宋体", help="CJK font for body text")
    p.add_argument("--heading-font", default="黑体", help="CJK font for headings")
    p.add_argument("--latin-font", default="Calibri", help="font for latin glyphs")
    p.add_argument("--output", default="", help="save-as path (default: in place)")
    p.set_defaults(func=cmd_styles)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
