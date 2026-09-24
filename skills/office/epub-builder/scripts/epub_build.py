#!/usr/bin/env python3
"""epub_build.py -- Markdown -> EPUB 3 (pure stdlib).

An EPUB is essentially "a zip + a set of XML", so no third-party library is needed:
zipfile packages it, OPF/NCX/NAV are hand-written, and HTML conversion uses a lightweight
parser inside this script.

Three hard details of the EPUB spec (getting them wrong makes readers reject the file outright):
  1. `mimetype` must be the **first** entry in the zip and **uncompressed** (ZIP_STORED),
     with content exactly `application/epub+zip` and no trailing newline.
  2. `META-INF/container.xml` must declare the OPF path.
  3. `content.opf` manifest must cover every resource; the spine must cover every chapter.

Subcommands:
  build   <input.md> --out book.epub [--title X --author Y]
  inspect <book.epub>
"""

import argparse
import html
import re
import sys
import unicodedata
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

EPUB_MIMETYPE = "application/epub+zip"
CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

# Chapter splitting: an H1 starts a new chapter; without an H1 the whole thing is one chapter
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

CSS = """body{font-family:serif;line-height:1.7;margin:5%;}
h1{font-size:1.5em;border-bottom:2px solid #ddd;padding-bottom:.3em;}
h2{font-size:1.2em;margin-top:1.6em;}
h3{font-size:1.05em;}
blockquote{border-left:3px solid #ccc;margin-left:0;padding-left:1em;color:#555;}
code{background:#f4f4f4;padding:.1em .3em;border-radius:3px;font-size:.9em;}
pre{background:#f4f4f4;padding:.8em;overflow:auto;border-radius:4px;}
pre code{background:none;padding:0;}
table{border-collapse:collapse;margin:1em 0;width:100%;}
th,td{border:1px solid #ddd;padding:.4em .6em;text-align:left;}
th{background:#f0f0f0;}
img{max-width:100%;}
"""


class EpubError(Exception):
    """User-facing error."""


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def xesc(s: str) -> str:
    """XML text escaping (the attribute version uses esc with quote=True)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- Markdown


def inline_md(text: str) -> str:
    """Inline Markdown -> HTML. Escape first, then process markup, to avoid injection and ordering bugs."""
    s = esc(text)
    # inline code first: stash it so the * inside is not treated as emphasis
    codes = []

    def _stash(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`\n]+)`", _stash, s)
    s = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    # restore inline code (content already escaped, drop back into <code>)
    for i, c in enumerate(codes):
        s = s.replace(f"\x00{i}\x00", f"<code>{c}</code>")
    return s


def md_to_html(md: str, start_at_h2: bool = True) -> str:
    """Minimal block-level Markdown parser: headings / lists / quotes / code blocks / tables / paragraphs.

    When `start_at_h2=True`, drop the leading H1 (the title is already used as the chapter name
    and file name).
    """
    lines = md.splitlines()
    out, i, n = [], 0, len(lines)
    in_code = False
    code_buf = []
    list_type = None      # "ul" | "ol"
    para_buf = []

    def flush_para():
        if para_buf:
            out.append(f"<p>{inline_md(' '.join(para_buf))}</p>")
            para_buf.clear()

    def close_list():
        nonlocal list_type
        if list_type:
            out.append(f"</{list_type}>")
            list_type = None

    while i < n:
        line = lines[i]

        # code block
        if line.strip().startswith("```"):
            if in_code:
                out.append("<pre><code>" + esc("\n".join(code_buf)) + "</code></pre>")
                code_buf, in_code = [], False
            else:
                flush_para(); close_list()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # blank line: end the current paragraph and list
        if not line.strip():
            flush_para(); close_list()
            i += 1
            continue

        # table: current line starts with | and the next line is the separator row
        if (line.lstrip().startswith("|") and i + 1 < n
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])):
            flush_para(); close_list()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><thead><tr>"
                       + "".join(f"<th>{inline_md(h)}</th>" for h in header)
                       + "</tr></thead><tbody>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in r) + "</tr>")
            out.append("</tbody></table>")
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para(); close_list()
            level = len(m.group(1))
            if level == 1 and start_at_h2:
                i += 1
                continue
            lv = min(level, 6)
            out.append(f"<h{lv}>{inline_md(m.group(2))}</h{lv}>")
            i += 1
            continue

        # blockquote
        if line.lstrip().startswith(">"):
            flush_para(); close_list()
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline_md(' '.join(buf))}</blockquote>")
            continue

        # horizontal rule
        if re.match(r"^\s*([-*_])\1{2,}\s*$", line):
            flush_para(); close_list()
            out.append("<hr/>")
            i += 1
            continue

        # unordered list
        m = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if m:
            flush_para()
            if list_type != "ul":
                close_list(); out.append("<ul>"); list_type = "ul"
            out.append(f"<li>{inline_md(m.group(1))}</li>")
            i += 1
            continue

        # ordered list
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            flush_para()
            if list_type != "ol":
                close_list(); out.append("<ol>"); list_type = "ol"
            out.append(f"<li>{inline_md(m.group(1))}</li>")
            i += 1
            continue

        para_buf.append(line.strip())
        i += 1

    if in_code and code_buf:      # an unclosed code block must still be flushed; don't lose content
        out.append("<pre><code>" + esc("\n".join(code_buf)) + "</code></pre>")
    flush_para(); close_list()
    return "\n".join(out)


def split_chapters(md: str):
    """Split into chapters by H1. Returns [(title, body_md)]; without an H1 the whole doc is one chapter."""
    matches = list(H1_RE.finditer(md))
    if not matches:
        return [("Body", md)]

    chapters = []
    # content before the first H1 (if any) becomes a preface
    if matches[0].start() > 0 and md[: matches[0].start()].strip():
        chapters.append(("Preface", md[: matches[0].start()]))
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(md)
        body = md[m.end(): end]
        chapters.append((m.group(1).strip(), body))
    return chapters


def slugify(name: str, idx: int) -> str:
    """Chapter file name: keep alphanumeric and CJK chars, turn everything else into hyphens."""
    keep = []
    for ch in name.strip().lower():
        if ch.isalnum() or "\u4e00" <= ch <= "\u9fff":
            keep.append(ch)
        elif ch in " -_":
            keep.append("-")
    s = re.sub(r"-+", "-", "".join(keep)).strip("-")
    if not s:
        s = f"chapter-{idx}"
    return f"chap{idx:02d}-{s}"[:60]


# ---------------------------------------------------------------- EPUB parts


def container_xml() -> str:
    return CONTAINER_XML


def content_opf(title, author, lang, uid, chapter_files, css_file, mtime) -> str:
    manifest = [
        '    <item id="nav" href="nav.xhtml" '
        'media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="ncx" href="toc.ncx" '
        'media-type="application/x-dtbncx+xml"/>',
        f'    <item id="css" href="{css_file}" media-type="text/css"/>',
    ]
    spine = []
    for i, (cf, _t) in enumerate(chapter_files, 1):
        manifest.append(
            f'    <item id="chap{i}" href="{cf}" '
            f'media-type="application/xhtml+xml"/>'
        )
        spine.append(f'    <itemref idref="chap{i}"/>')

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0"
         unique-identifier="bookid" xml:lang="{lang}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:{uid}</dc:identifier>
    <dc:title>{xesc(title)}</dc:title>
    <dc:creator>{xesc(author)}</dc:creator>
    <dc:language>{lang}</dc:language>
    <meta property="dcterms:modified">{mtime}</meta>
  </metadata>
  <manifest>
{chr(10).join(manifest)}
  </manifest>
  <spine toc="ncx">
{chr(10).join(spine)}
  </spine>
</package>
"""


def toc_ncx(title, uid, chapter_files) -> str:
    """EPUB 2 compatible TOC: older readers only understand NCX."""
    points = []
    for i, (cf, ct) in enumerate(chapter_files, 1):
        points.append(f"""    <navPoint id="nav{i}" playOrder="{i}">
      <navLabel><text>{xesc(ct)}</text></navLabel>
      <content src="{cf}"/>
    </navPoint>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
  "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{uid}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{xesc(title)}</text></docTitle>
  <navMap>
{chr(10).join(points)}
  </navMap>
</ncx>
"""


def nav_xhtml(chapter_files) -> str:
    """Native EPUB 3 TOC."""
    items = "\n".join(
        f'      <li><a href="{cf}">{esc(ct)}</a></li>' for cf, ct in chapter_files
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="zh" lang="zh">
<head><meta charset="utf-8"/><title>Table of Contents</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>Table of Contents</h1>
    <ol>
{items}
    </ol>
  </nav>
</body>
</html>
"""


def chapter_xhtml(title, body_html) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh" lang="zh">
<head><meta charset="utf-8"/><title>{esc(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
<section>
<h1>{esc(title)}</h1>
{body_html}
</section>
</body>
</html>
"""


# ---------------------------------------------------------------- build


ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)   # fixed timestamp -> reproducible builds


def write_epub(out: Path, parts) -> None:
    """Write the zip in EPUB-spec order: mimetype first and uncompressed."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        # 1) mimetype must be written first, with ZIP_STORED (no compression)
        zi = zipfile.ZipInfo("mimetype", date_time=ZIP_TIMESTAMP)
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, EPUB_MIMETYPE)

        # 2) all other resources are DEFLATED
        for name, data in parts:
            zi = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data if isinstance(data, bytes) else data.encode("utf-8"))


def cmd_build(args) -> int:
    src = Path(args.input)
    if not src.is_file():
        raise EpubError(f"Markdown file not found: {src}")

    md = src.read_text(encoding="utf-8", errors="replace")
    if not md.strip():
        raise EpubError(f"{src} is an empty file")

    title = args.title or (H1_RE.search(md).group(1).strip()
                           if H1_RE.search(md) else src.stem)
    author = args.author or "Anonymous"
    lang = args.lang

    chapters = split_chapters(md)
    if not chapters:
        raise EpubError("no chapters could be parsed")

    # assemble the chapter files
    chapter_files = []
    parts = []
    for i, (ctitle, body_md) in enumerate(chapters, 1):
        fname = f"{slugify(ctitle, i)}.xhtml"
        # the chapter name is already the H1; drop the H1 in the body to avoid duplication
        body_html = md_to_html(body_md, start_at_h2=True)
        chapter_files.append((fname, ctitle))
        parts.append((f"OEBPS/{fname}", chapter_xhtml(ctitle, body_html)))

    uid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{title}|{author}|{len(chapters)}"))
    mtime = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    parts.append(("OEBPS/style.css", CSS))
    parts.append(("OEBPS/nav.xhtml", nav_xhtml(chapter_files)))
    parts.append(("OEBPS/toc.ncx", toc_ncx(title, uid, chapter_files)))
    parts.append(("OEBPS/content.opf",
                  content_opf(title, author, lang, uid, chapter_files,
                              "style.css", mtime)))
    parts.append(("META-INF/container.xml", container_xml()))

    out = Path(args.out)
    write_epub(out, parts)
    size_kb = out.stat().st_size / 1024

    print(f"built: {out}")
    print(f"  title     : {title}")
    print(f"  author    : {author}")
    print(f"  language  : {lang}")
    print(f"  chapters  : {len(chapter_files)}")
    print(f"  size      : {size_kb:.1f} KB")
    for fname, ctitle in chapter_files:
        print(f"    - {fname}  ({ctitle})")

    # self-check on build: mimetype ordering and storage are the easiest places this format gets wrong
    with zipfile.ZipFile(out) as z:
        infos = z.infolist()
        first = infos[0]
        ok_first = first.filename == "mimetype"
        ok_stored = first.compress_type == zipfile.ZIP_STORED
        content = z.read("mimetype").decode("utf-8") if ok_first else ""
    print()
    print(f"  mimetype  : first entry={ok_first} "
          f"storage={'STORED' if ok_stored else 'DEFLATED'} "
          f"{'OK' if ok_first and ok_stored else 'X violates EPUB spec'}")
    if content != EPUB_MIMETYPE:
        print(f"  X mimetype content is abnormal: {content!r}")
    return 0


# ---------------------------------------------------------------- inspect


def cmd_inspect(args) -> int:
    book = Path(args.epub)
    if not book.is_file():
        raise EpubError(f"EPUB not found: {book}")
    if not zipfile.is_zipfile(book):
        raise EpubError(f"{book} is not a valid zip/EPUB")

    with zipfile.ZipFile(book) as z:
        names = z.namelist()
        infos = z.infolist()
        first = infos[0]
        mimetype_ok = (first.filename == "mimetype"
                       and first.compress_type == zipfile.ZIP_STORED)
        mt = z.read("mimetype").decode("utf-8") if "mimetype" in names else ""

        # locate the OPF
        opf_path = None
        if "META-INF/container.xml" in names:
            root = ET.fromstring(z.read("META-INF/container.xml"))
            for el in root.iter():
                if el.tag.endswith("rootfile"):
                    opf_path = el.get("full-path")
                    break
        if not opf_path or opf_path not in names:
            print(f"WARN: container.xml does not point to a valid OPF ({opf_path})", file=sys.stderr)
            opf_path = next((n for n in names if n.endswith(".opf")), None)

        print(f"inspect: {book}")
        print(f"  size           : {book.stat().st_size / 1024:.1f} KB")
        print(f"  entries        : {len(names)}")
        print(f"  mimetype       : {mt or '(missing)'}")
        print(f"  mimetype valid : "
              f"{'yes (first entry and STORED)' if mimetype_ok else 'no <- readers may reject it'}")
        print(f"  opf            : {opf_path or '(missing)'}")

        if opf_path:
            opf = ET.fromstring(z.read(opf_path))
            base = "/".join(opf_path.split("/")[:-1])

            def local(tag):
                return tag.split("}")[-1]

            meta, items, spine, nav_id = {}, {}, [], None
            for el in opf.iter():
                tag = local(el.tag)
                if tag in ("title", "creator", "language", "identifier"):
                    meta.setdefault(tag, (el.text or "").strip())
                elif tag == "item":
                    iid = el.get("id", "")
                    items[iid] = {
                        "href": el.get("href", ""),
                        "media_type": el.get("media-type", ""),
                    }
                    # the nav document carries properties="nav" (EPUB3 convention)
                    if "nav" in (el.get("properties") or "").split():
                        nav_id = iid
                elif tag == "itemref":
                    spine.append(el.get("idref", ""))

            # chapter order follows the spine (this is the reader's actual reading order);
            # it is more reliable than "iterate the manifest's xhtml" because manifest order
            # has no spec guarantee
            chapters = []
            for idref in spine:
                it = items.get(idref)
                if not it or idref == nav_id:
                    continue
                if "xhtml" not in it["media_type"]:
                    continue
                chapters.append(it["href"])

            print()
            print(f"  metadata       :")
            print(f"    title        : {meta.get('title', '(missing)')}")
            print(f"    creator      : {meta.get('creator', '(missing)')}")
            print(f"    language     : {meta.get('language', '(missing)')}")
            ident = meta.get("identifier", "")
            print(f"    identifier   : {ident[:60]}{'...' if len(ident) > 60 else ''}")
            print()
            print(f"  chapter list   : {len(chapters)} chapters (in spine order)")
            for i, href in enumerate(chapters, 1):
                full = f"{base}/{href}" if base else href
                t = ""
                if full in names:
                    try:
                        html_text = z.read(full).decode("utf-8", "replace")
                        m = re.search(r"<h1>(.*?)</h1>", html_text, re.S)
                        if m:
                            t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                    except Exception:
                        pass
                print(f"    {i:>2}. {href:<30} {t}")

        # NCX and NAV must both exist, serving old and new readers respectively
        print()
        print(f"  toc.ncx        : {'yes' if any(n.endswith('toc.ncx') for n in names) else 'no'}")
        print(f"  nav.xhtml      : {'yes' if any(n.endswith('nav.xhtml') for n in names) else 'no'}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="epub_build.py",
        description="Markdown -> EPUB 3, plus read-back inspection of an EPUB (pure stdlib)",
        epilog="Example: python3 epub_build.py build book.md --out book.epub "
               "--title My Book --author Jane Doe",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build", help="convert Markdown into an EPUB")
    s.add_argument("input", help="Markdown source file")
    s.add_argument("--out", default="book.epub", help="output EPUB path")
    s.add_argument("--title", help="book title (defaults to the first H1 or the file name)")
    s.add_argument("--author", help="author (defaults to 'Anonymous')")
    s.add_argument("--lang", default="en", help="language code (default en)")
    s.set_defaults(func=cmd_build)

    s = sub.add_parser("inspect", help="read back an EPUB and print its metadata and chapter list")
    s.add_argument("epub")
    s.set_defaults(func=cmd_inspect)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except EpubError as e:
        die(str(e))
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
