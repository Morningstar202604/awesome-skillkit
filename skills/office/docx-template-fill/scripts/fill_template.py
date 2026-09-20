#!/usr/bin/env python3
"""
fill_template.py — 把 JSON 数据填进已有 Word 模板的 {{占位符}}，
并可选追加修订批注。

设计红线（仓库 SKILL-STANDARD-v2）：
- 默认 dry-run：只打印将要做什么，不动原文件
- --apply 才真正写（输出到新文件，源模板永不改）
- 零网络、零拷贝：纯本地文件操作
- 凭证（如有外部源）走环境变量，不在脚本里写死

依赖：python-docx（pip install python-docx）。缺失时降级为"只解析占位符清单"。
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
    """替换段落内占位符。保留原格式：把整段文字重设，
    但只改文本节点，不重建样式（模板段落样式保留）。"""
    text = p.text or ""
    changed = False
    for key, val in data.items():
        token = "{{" + key + "}}"
        if token in text:
            text = text.replace(token, str(val))
            changed = True
    if changed and not dry:
        # 清空 run 并写回，保留段落样式
        for r in list(p.runs):
            r.text = ""
        if p.runs:
            p.runs[0].text = text
        else:
            p.add_run(text)
    return changed


def add_review_note(doc, author: str, note: str, dry: bool) -> bool:
    """追加一条批注样式的修订说明（用脚注区近似；docx 标准 comment 需
    修改 parts，此处降级为在文档末尾加【批注】段，标注作者）。"""
    if dry:
        return True
    p = doc.add_paragraph()
    r = p.add_run(f"【批注 · {author}】{note}")
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
