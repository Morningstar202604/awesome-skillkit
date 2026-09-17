#!/usr/bin/env python3
"""epub_build.py — Markdown → EPUB 3（纯标准库）。

EPUB 本质是「一个 zip + 一组 XML」，因此不用任何第三方库：
zipfile 打包、手写 OPF/NCX/NAV，HTML 转换用本脚本内的轻量解析器。

EPUB 规范的三个硬性细节（做错会导致阅读器直接拒收）：
  1. `mimetype` 必须是 zip 里的**第一个**条目，且**不压缩**（ZIP_STORED），
     内容恰为 `application/epub+zip`，不带换行。
  2. `META-INF/container.xml` 必须声明 OPF 的路径。
  3. `content.opf` 的 manifest 要覆盖全部资源，spine 要覆盖全部章节。

子命令:
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

# 章节切分：一级标题起新章；没有 H1 时整篇作为单章
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
    """面向用户的错误。"""


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def xesc(s: str) -> str:
    """XML 文本转义（属性用 esc 的 quote=True 版本）。"""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- Markdown


def inline_md(text: str) -> str:
    """行内 Markdown → HTML。先转义再处理标记，避免注入与顺序错乱。"""
    s = esc(text)
    # 行内代码优先：先占位，避免其中的 * 被当成强调
    codes = []

    def _stash(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`\n]+)`", _stash, s)
    s = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    # 还原行内代码（内容已转义，直接放回 <code>）
    for i, c in enumerate(codes):
        s = s.replace(f"\x00{i}\x00", f"<code>{c}</code>")
    return s


def md_to_html(md: str, start_at_h2: bool = True) -> str:
    """极简块级 Markdown 解析：标题/列表/引用/代码块/表格/段落。

    `start_at_h2=True` 时把开头的 H1 丢掉（标题已用作章节名与文件名）。
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

        # 代码块
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

        # 空行：结束段落与列表
        if not line.strip():
            flush_para(); close_list()
            i += 1
            continue

        # 表格：当前行以 | 开头且下一行是分隔行
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

        # 标题
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

        # 引用
        if line.lstrip().startswith(">"):
            flush_para(); close_list()
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline_md(' '.join(buf))}</blockquote>")
            continue

        # 分隔线
        if re.match(r"^\s*([-*_])\1{2,}\s*$", line):
            flush_para(); close_list()
            out.append("<hr/>")
            i += 1
            continue

        # 无序列表
        m = re.match(r"^\s*[-*+]\s+(.*)$", line)
        if m:
            flush_para()
            if list_type != "ul":
                close_list(); out.append("<ul>"); list_type = "ul"
            out.append(f"<li>{inline_md(m.group(1))}</li>")
            i += 1
            continue

        # 有序列表
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

    if in_code and code_buf:      # 未闭合的代码块也要落盘，别丢内容
        out.append("<pre><code>" + esc("\n".join(code_buf)) + "</code></pre>")
    flush_para(); close_list()
    return "\n".join(out)


def split_chapters(md: str):
    """按 H1 切章。返回 [(title, body_md)]，无 H1 则整篇一章。"""
    matches = list(H1_RE.finditer(md))
    if not matches:
        return [("正文", md)]

    chapters = []
    # H1 之前的内容（如果有）作为前言
    if matches[0].start() > 0 and md[: matches[0].start()].strip():
        chapters.append(("前言", md[: matches[0].start()]))
    for idx, m in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(md)
        body = md[m.end(): end]
        chapters.append((m.group(1).strip(), body))
    return chapters


def slugify(name: str, idx: int) -> str:
    """章节文件名：保留字母数字与中文，其余转连字符。"""
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


# ---------------------------------------------------------------- EPUB 部件


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
    """EPUB 2 兼容目录：老阅读器只认 NCX。"""
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
    """EPUB 3 原生目录。"""
    items = "\n".join(
        f'      <li><a href="{cf}">{esc(ct)}</a></li>' for cf, ct in chapter_files
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"
      xml:lang="zh" lang="zh">
<head><meta charset="utf-8"/><title>目录</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>目录</h1>
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


ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)   # 固定时间戳 → 可复现构建


def write_epub(out: Path, parts) -> None:
    """按 EPUB 规范顺序写 zip：mimetype 第一且不压缩。"""
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        # 1) mimetype 必须第一个写入、且用 ZIP_STORED（不压缩）
        zi = zipfile.ZipInfo("mimetype", date_time=ZIP_TIMESTAMP)
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, EPUB_MIMETYPE)

        # 2) 其余资源一律 DEFLATED
        for name, data in parts:
            zi = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data if isinstance(data, bytes) else data.encode("utf-8"))


def cmd_build(args) -> int:
    src = Path(args.input)
    if not src.is_file():
        raise EpubError(f"Markdown 文件不存在：{src}")

    md = src.read_text(encoding="utf-8", errors="replace")
    if not md.strip():
        raise EpubError(f"{src} 是空文件")

    title = args.title or (H1_RE.search(md).group(1).strip()
                           if H1_RE.search(md) else src.stem)
    author = args.author or "佚名"
    lang = args.lang

    chapters = split_chapters(md)
    if not chapters:
        raise EpubError("没有解析出任何章节")

    # 组装章节文件
    chapter_files = []
    parts = []
    for i, (ctitle, body_md) in enumerate(chapters, 1):
        fname = f"{slugify(ctitle, i)}.xhtml"
        # 章节名已是 H1，正文里的 H1 丢弃以免重复
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

    # 构建即自检：mimetype 顺序与存储方式是本格式最容易错的地方
    with zipfile.ZipFile(out) as z:
        infos = z.infolist()
        first = infos[0]
        ok_first = first.filename == "mimetype"
        ok_stored = first.compress_type == zipfile.ZIP_STORED
        content = z.read("mimetype").decode("utf-8") if ok_first else ""
    print()
    print(f"  mimetype  : 第一个条目={ok_first} "
          f"存储方式={'STORED' if ok_stored else 'DEFLATED'} "
          f"{'✓' if ok_first and ok_stored else '✗ 违反 EPUB 规范'}")
    if content != EPUB_MIMETYPE:
        print(f"  ✗ mimetype 内容异常：{content!r}")
    return 0


# ---------------------------------------------------------------- inspect


def cmd_inspect(args) -> int:
    book = Path(args.epub)
    if not book.is_file():
        raise EpubError(f"EPUB 不存在：{book}")
    if not zipfile.is_zipfile(book):
        raise EpubError(f"{book} 不是合法 zip/EPUB")

    with zipfile.ZipFile(book) as z:
        names = z.namelist()
        infos = z.infolist()
        first = infos[0]
        mimetype_ok = (first.filename == "mimetype"
                       and first.compress_type == zipfile.ZIP_STORED)
        mt = z.read("mimetype").decode("utf-8") if "mimetype" in names else ""

        # 定位 OPF
        opf_path = None
        if "META-INF/container.xml" in names:
            root = ET.fromstring(z.read("META-INF/container.xml"))
            for el in root.iter():
                if el.tag.endswith("rootfile"):
                    opf_path = el.get("full-path")
                    break
        if not opf_path or opf_path not in names:
            print(f"WARN: container.xml 未指向有效的 OPF（{opf_path}）", file=sys.stderr)
            opf_path = next((n for n in names if n.endswith(".opf")), None)

        print(f"inspect: {book}")
        print(f"  size           : {book.stat().st_size / 1024:.1f} KB")
        print(f"  entries        : {len(names)}")
        print(f"  mimetype       : {mt or '(缺失)'}")
        print(f"  mimetype 合规  : "
              f"{'是（第一个条目且 STORED）' if mimetype_ok else '否 ← 阅读器可能拒收'}")
        print(f"  opf            : {opf_path or '(缺失)'}")

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
                    # nav 文档带 properties="nav"（EPUB3 约定）
                    if "nav" in (el.get("properties") or "").split():
                        nav_id = iid
                elif tag == "itemref":
                    spine.append(el.get("idref", ""))

            # 章节顺序以 spine 为准（这是阅读器的实际读取顺序），
            # 比「遍历 manifest 里的 xhtml」可靠：manifest 顺序无规范保证
            chapters = []
            for idref in spine:
                it = items.get(idref)
                if not it or idref == nav_id:
                    continue
                if "xhtml" not in it["media_type"]:
                    continue
                chapters.append(it["href"])

            print()
            print(f"  元数据         :")
            print(f"    title        : {meta.get('title', '(缺)')}")
            print(f"    creator      : {meta.get('creator', '(缺)')}")
            print(f"    language     : {meta.get('language', '(缺)')}")
            ident = meta.get("identifier", "")
            print(f"    identifier   : {ident[:60]}{'…' if len(ident) > 60 else ''}")
            print()
            print(f"  章节清单       : {len(chapters)} 章（按 spine 顺序）")
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

        # NCX 与 NAV 必须同时存在，分别服务老/新阅读器
        print()
        print(f"  toc.ncx        : {'有' if any(n.endswith('toc.ncx') for n in names) else '无'}")
        print(f"  nav.xhtml      : {'有' if any(n.endswith('nav.xhtml') for n in names) else '无'}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="epub_build.py",
        description="Markdown → EPUB 3，以及 EPUB 读回检查（纯标准库）",
        epilog="示例：python3 epub_build.py build book.md --out book.epub "
               "--title 我的书 --author 张三",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build", help="把 Markdown 转成 EPUB")
    s.add_argument("input", help="Markdown 源文件")
    s.add_argument("--out", default="book.epub", help="输出 EPUB 路径")
    s.add_argument("--title", help="书名（默认取首个 H1 或文件名）")
    s.add_argument("--author", help="作者（默认「佚名」）")
    s.add_argument("--lang", default="zh", help="语言代码（默认 zh）")
    s.set_defaults(func=cmd_build)

    s = sub.add_parser("inspect", help="读回 EPUB，输出元数据与章节清单")
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
