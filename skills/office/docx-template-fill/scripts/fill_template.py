#!/usr/bin/env python3
"""
fill_template.py -- fill JSON data into {{placeholders}} in an existing Word template,
and optionally append a review note.

Design guardrails (repo SKILL-STANDARD-v2):
- dry-run by default: only print what would be done, touch no source file
- --apply actually writes (to a new file; the source template is never modified)
- zero network, zero copying: pure local file operations
- credentials (if any external source) come from environment variables, never hard-coded

Dependency: python-docx (`pip install python-docx`). If missing, degrades to
"only parse the placeholder list".
"""
import argparse
import json
import re
import sys
import os
from copy import deepcopy

PLACEHOLDER = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


def load_data(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def iter_paragraphs(doc):
    for p in doc.paragraphs:
        yield p, "para"
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p, "cell"


def collect_placeholders(doc):
    found = {}
    for p, _ in iter_paragraphs(doc):
        for m in PLACEHOLDER.finditer(p.text or ""):
            found[m.group(1)] = found.get(m.group(1), 0) + 1
    return found


def replace_in_paragraph(p, data: dict, dry: bool):
    """Replace placeholders inside a paragraph. Preserve the original formatting: reset the
    whole paragraph's text but only touch the text nodes, rebuilding no style
    (the template paragraph style is kept)."""
    text = p.text or ""
    changed = False
    for key, val in data.items():
        token = "{{" + key + "}}"
        if token in text:
            text = text.replace(token, str(val))
            changed = True
    if changed and not dry:
        # clear the runs and write back, keeping the paragraph style
        for r in list(p.runs):
            r.text = ""
        if p.runs:
            p.runs[0].text = text
        else:
            p.add_run(text)
    return changed


def add_review_note(doc, author: str, note: str, dry: bool) -> bool:
    """Append a comment-style revision note (approximated with a footnote-like area; a
    standard docx comment requires editing parts, so here it degrades to appending a
    "[NOTE]" paragraph at the end of the document, tagged with the author)."""
    if dry:
        return True
    p = doc.add_paragraph()
    r = p.add_run(f"[NOTE - {author}] {note}")
    r.italic = True
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Fill a Word template with JSON data (dry-run by default)")
    ap.add_argument("--template", required=True, help="path to .docx template with {{placeholders}}")
    ap.add_argument("--data", required=True, help="path to JSON data file")
    ap.add_argument("-o", "--out", default="filled.docx", help="output path (only with --apply)")
    ap.add_argument("--apply", action="store_true", help="actually write; default is dry-run")
    ap.add_argument("--note-author", default="reviewer", help="author name for review note")
    ap.add_argument("--note-text", default="", help="optional review note text to append")
    ap.add_argument("--list-only", action="store_true", help="only print placeholders found, then exit")
    args = ap.parse_args()

    if not os.path.isfile(args.template):
        print(f"[ERROR] template not found: {args.template}", file=sys.stderr)
        return 2

    try:
        import docx  # noqa: F401
        have_docx = True
    except ImportError:
        have_docx = False

    data = load_data(args.data)

    if not have_docx:
        print("[DEGRADE] python-docx not installed; cannot parse docx binary. "
              "Install with `pip install python-docx` then re-run.", file=sys.stderr)
        print("Available data keys that WOULD be filled:", json.dumps(list(data.keys()), ensure_ascii=False))
        return 3

    from docx import Document
    doc = Document(args.template)
    placeholders = collect_placeholders(doc)

    print(f"Placeholders in template ({len(placeholders)}):")
    for k, cnt in sorted(placeholders.items()):
        status = "WILL FILL" if k in data else "UNRESOLVED"
        print(f"  {{{{{k}}}}}  x{cnt}  ->  {status}")

    if args.list_only:
        return 0

    missing = [k for k in placeholders if k not in data]
    if missing:
        print(f"\n[WARN] {len(missing)} placeholder(s) have no data key: {missing}")

    unresolved = set(missing)
    filled = 0
    if args.apply:
        for p, _ in iter_paragraphs(doc):
            if replace_in_paragraph(p, data, dry=False):
                filled += 1
        if args.note_text:
            add_review_note(doc, args.note_author, args.note_text, dry=False)
        out = args.out
        doc.save(out)
        print(f"\n[APPLY] wrote {filled} paragraph(s) to {out}")
        if unresolved:
            print(f"[NOTICE] {len(unresolved)} placeholder(s) left as-is: {sorted(unresolved)}")
    else:
        print(f"\n[DRY-RUN] no file written. Re-run with --apply -o {args.out!r} to write.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
