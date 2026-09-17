#!/usr/bin/env python3
"""wiki_build.py — 个人知识库（personal wiki）的目录初始化、索引、检索与体检。

设计约束：只用 Python 标准库（json / re / pathlib / argparse），
不依赖任何第三方包，保证在裸环境下也能跑通。

wiki 目录结构（init 子命令创建）::

    <dir>/
      raw/          原始资料：剪藏、原文、PDF 转出的文本，只进不改
      notes/        编译后的笔记：自己写的东西，带 [[wiki 链接]] 与 #标签
      index.json    分片索引：由 index 子命令生成，不要手改

子命令:
  init    <dir>                 初始化目录骨架
  index   <dir>                 扫描 raw/ 与 notes/ 重建 index.json
  search  <dir> "关键词"         在索引上按权重检索
  lint    <dir>                 孤儿笔记 / 断链 / 空笔记检查
  stats   <dir>                 总量与结构统计

约定（本技能的核心契约，index 与 lint 都基于它）:
  - 笔记标题：首个 H1（`# 标题`）；没有 H1 则退回文件名（去扩展名）。
  - 标签：正文中 `#标签` 形式，中英文皆可；`#` 后紧跟数字不算标签（避开 "#1"）。
  - 链接：`[[目标]]` 或 `[[目标|显示文字]]`；目标按「文件名 / H1 标题」两种别名解析。
  - raw/ 下的文件只做索引与检索，不参与 lint 的孤儿判定。
"""

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------- 常量与正则

RAW_DIR = "raw"
NOTES_DIR = "notes"
INDEX_FILE = "index.json"
MARKDOWN_SUFFIXES = {".md", ".markdown", ".txt"}

H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
# 标签：`#` 后跟字母/中文/下划线开头，允许后续数字。
# (?<![\w#]) 避免把 URL 片段（a#b）和 `##标题` 误判成标签。
TAG_RE = re.compile(r"(?<![\w#])#([A-Za-z_][\w\u4e00-\u9fff-]*|[\u4e00-\u9fff][\w\u4e00-\u9fff-]*)")
WIKILINK_RE = re.compile(r"\[\[([^\[\]|]+?)(?:\|([^\[\]]*))?\]\]")
# 中文按字计、英文按词计，只用作篇幅粗估
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z0-9]+")

# 检索权重：标题命中 > 标签命中 > 正文命中
W_TITLE, W_TAG, W_BODY = 10, 5, 1


class WikiError(Exception):
    """面向用户的错误：消息会被 main 捕获后直接打印为 ERROR 行。"""


# ---------------------------------------------------------------- 工具函数


def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def count_words(text: str) -> int:
    """中文按字、英文按词，得到一个跨语言可比的篇幅数。"""
    return len(CJK_RE.findall(text)) + len(WORD_RE.findall(text))


def display_width(s: str) -> int:
    """终端显示宽度：中日韩全角字符占 2 列，其余 1 列。

    直接用 len() 对齐会让「检索」和「infra」在等宽字体下错位，
    统计表里混排中英标签时尤其明显。
    """
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def pad(s: str, width: int) -> str:
    """按显示宽度右侧补空格。"""
    return s + " " * max(0, width - display_width(s))


def read_text(path: Path) -> str:
    """宽容读取：编码坏了也不能让整个索引挂掉。"""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise WikiError(f"无法读取 {path}: {e}")


def require_wiki(root: Path) -> Path:
    """确认根目录是个已初始化的 wiki，返回其绝对路径。"""
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise WikiError(f"目录不存在：{root}（先跑 init）")
    if not (root / NOTES_DIR).is_dir():
        raise WikiError(f"{root} 下没有 {NOTES_DIR}/，不是 wiki 目录（先跑 init）")
    return root


def iter_pages(root: Path):
    """产出 (bucket, path) ；bucket ∈ {raw, notes}。跳过隐藏文件与 .git。"""
    for bucket in (RAW_DIR, NOTES_DIR):
        base = root / bucket
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            if any(part.startswith(".") for part in p.relative_to(root).parts):
                continue
            if p.suffix.lower() not in MARKDOWN_SUFFIXES:
                continue
            yield bucket, p


def parse_page(root: Path, bucket: str, path: Path) -> dict:
    """把一篇 Markdown 解析成索引所需的字段。"""
    text = read_text(path)
    rel = path.relative_to(root).as_posix()

    m = H1_RE.search(text)
    title = m.group(1).strip() if m else path.stem
    body = text
    if m:
        # 正文命中检索时排除标题行本身，否则标题词会被重复计一次
        body = text[: m.start()] + text[m.end():]

    # 去重且保序：同一标签在一篇里出现多次只记一次
    tags, seen = [], set()
    for t in TAG_RE.findall(text):
        if t not in seen:
            seen.add(t)
            tags.append(t)

    links, seen_l = [], set()
    for target, alias in WIKILINK_RE.findall(text):
        target = target.strip()
        key = target.lower()
        if target and key not in seen_l:
            seen_l.add(key)
            links.append(
                {"target": target, "alias": (alias or "").strip() or None}
            )

    return {
        "path": rel,
        "bucket": bucket,
        "slug": path.stem,
        "title": title,
        "tags": tags,
        "links": links,
        "words": count_words(text),
        "lines": len(text.splitlines()),
        "empty": not text.strip() or count_words(text) < 5,
    }


# ---------------------------------------------------------------- 索引构建


def build_index(root: Path) -> dict:
    """扫描 raw/ 与 notes/，产出完整的索引字典。"""
    pages = [parse_page(root, b, p) for b, p in iter_pages(root)]

    # 别名表用于解析链接：slug（文件名）与 title（H1）都算，优先级 slug > title
    by_slug: dict[str, str] = {}
    by_title: dict[str, str] = {}
    for pg in pages:
        by_slug.setdefault(pg["slug"].lower(), pg["path"])
        by_title.setdefault(pg["title"].lower(), pg["path"])

    backlinks: dict[str, list] = defaultdict(list)
    unresolved: list[dict] = []
    for pg in pages:
        for lk in pg["links"]:
            tgt = lk["target"].lower()
            dest = by_slug.get(tgt) or by_title.get(tgt)
            if dest:
                backlinks[dest].append(pg["path"])
            else:
                unresolved.append({"from": pg["path"], "target": lk["target"]})

    for pg in pages:
        pg["backlinks"] = sorted(set(backlinks.get(pg["path"], [])))
        # 出链是否命中留到 lint 判定，这里只记计数
        pg["outlinks"] = len(pg["links"])

    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root_name": root.name,
        "count": len(pages),
        "pages": pages,
        "unresolved_links": unresolved,
    }


def save_index(root: Path, index: dict):
    (root / INDEX_FILE).write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_index(root: Path) -> dict:
    f = root / INDEX_FILE
    if not f.is_file():
        raise WikiError(f"索引不存在：{f}（先跑 index）")
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except ValueError as e:
        raise WikiError(f"索引损坏（{e}）：删掉 {INDEX_FILE} 后重跑 index")


# ---------------------------------------------------------------- 子命令


def cmd_init(args) -> int:
    root = Path(args.dir).expanduser().resolve()
    if root.exists() and any(root.iterdir()) and not args.force:
        # 不做破坏性覆盖：非空目录必须显式 --force
        raise WikiError(f"目录非空：{root}；确认要初始化请加 --force")

    for sub in (RAW_DIR, NOTES_DIR):
        (root / sub).mkdir(parents=True, exist_ok=True)
        # .gitkeep 让空目录能被 git 跟踪
        keep = root / sub / ".gitkeep"
        keep.touch(exist_ok=True)

    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {root.name} — 个人知识库\n\n"
            f"- `{RAW_DIR}/` 原始资料（剪藏、原文），只进不改\n"
            f"- `{NOTES_DIR}/` 编译后的笔记，用 [[双链]] 互连、用 #标签 分类\n\n"
            "重建索引：`python3 wiki_build.py index .`\n",
            encoding="utf-8",
        )

    idx = root / INDEX_FILE
    if not idx.exists():
        save_index(root, build_index(root))

    print(f"initialized: {root}")
    print(f"  {RAW_DIR}/  {NOTES_DIR}/  {INDEX_FILE}  README.md")
    return 0


def cmd_index(args) -> int:
    root = require_wiki(Path(args.dir))
    index = build_index(root)
    save_index(root, index)

    notes = [p for p in index["pages"] if p["bucket"] == NOTES_DIR]
    raw = [p for p in index["pages"] if p["bucket"] == RAW_DIR]
    tags = sorted({t for p in index["pages"] for t in p["tags"]})

    print(f"indexed: {root / INDEX_FILE}")
    print(f"  pages  : {index['count']}  (notes {len(notes)} / raw {len(raw)})")
    print(f"  tags   : {len(tags)}")
    print(f"  links  : resolved "
          f"{sum(len(p['backlinks']) for p in index['pages'])}, "
          f"unresolved {len(index['unresolved_links'])}")
    for p in index["pages"]:
        print(f"    - [{p['bucket']}] {p['title']} "
              f"({p['words']}w, {len(p['tags'])} tags, {p['outlinks']} out)")
    return 0


def cmd_search(args) -> int:
    root = require_wiki(Path(args.dir))
    index = load_index(root)
    query = args.keyword.strip().lower()
    if not query:
        raise WikiError("关键词为空")

    results = []
    for pg in index["pages"]:
        title_l = pg["title"].lower()
        tags_l = [t.lower() for t in pg["tags"]]
        # 正文命中：从磁盘现读，保证索引不存全文也能检索
        body_l = read_text(root / pg["path"]).lower()

        score, why = 0, []
        if query in title_l:
            score += W_TITLE * title_l.count(query)
            why.append("title")
        if any(query in t for t in tags_l):
            score += W_TAG * sum(1 for t in tags_l if query in t)
            why.append("tag")
        n_body = body_l.count(query)
        if n_body:
            score += W_BODY * n_body
            why.append("body")
        if score:
            results.append((score, pg, why, n_body))

    results.sort(key=lambda r: (-r[0], r[1]["path"]))
    limit = args.limit or 20

    print(f'search "{args.keyword}" in {root.name}: {len(results)} hit(s)')
    if not results:
        print("  (无命中；换关键词，或先跑 index 确认资料已入库)")
        return 0
    for score, pg, why, n_body in results[:limit]:
        bits = ", ".join(
            f"title×{pg['title'].lower().count(query)}" if w == "title"
            else f"tag" if w == "tag"
            else f"body×{n_body}"
            for w in why
        )
        print(f"  {score:>4}  [{pg['bucket']}] {pg['title']}")
        print(f"        {pg['path']}  ({bits})")
    if len(results) > limit:
        print(f"  ... 另有 {len(results) - limit} 条，用 --limit 调整")
    return 0


def cmd_lint(args) -> int:
    root = require_wiki(Path(args.dir))
    index = load_index(root)

    orphans, broken, empties, tagged = [], [], [], []
    for pg in index["pages"]:
        if pg["bucket"] != NOTES_DIR:
            continue
        if pg["empty"]:
            empties.append(pg)
        if not pg["backlinks"]:
            orphans.append(pg)
        if not pg["tags"]:
            tagged.append(pg)

    # 断链：出链里解析不到目标的那部分（索引已算好，这里按来源归拢）
    by_source = defaultdict(list)
    for u in index["unresolved_links"]:
        by_source[u["from"]].append(u["target"])

    print(f"lint {root.name}: "
          f"{len(orphans)} orphan(s), {len(by_source)} page(s) with broken link(s), "
          f"{len(empties)} empty")
    print()

    print("[孤儿笔记] 无任何入链，检索不到也走不到")
    for pg in orphans or []:
        print(f"  - {pg['path']}  ({pg['title']})")
    if not orphans:
        print("  (无)")
    print()

    print("[断链] 链接指向不存在的页")
    for src, targets in sorted(by_source.items()):
        print(f"  - {src}")
        for t in targets:
            print(f"      -> [[{t}]] 未找到")
    if not by_source:
        print("  (无)")
    print()

    print("[空笔记] 正文不足 5 个词，多为占位符")
    for pg in empties or []:
        print(f"  - {pg['path']}")
    if not empties:
        print("  (无)")
    print()

    if tagged:
        print(f"[提示] {len(tagged)} 篇笔记无标签（不算错误，但会削弱检索）")
        for pg in tagged[:5]:
            print(f"  - {pg['path']}")
        if len(tagged) > 5:
            print(f"  ... 另有 {len(tagged) - 5} 篇")

    return 1 if (orphans or by_source or empties) else 0


def cmd_stats(args) -> int:
    root = require_wiki(Path(args.dir))
    index = load_index(root)

    notes = [p for p in index["pages"] if p["bucket"] == NOTES_DIR]
    raw = [p for p in index["pages"] if p["bucket"] == RAW_DIR]
    all_pages = index["pages"]

    total_words = sum(p["words"] for p in all_pages)
    tag_counter = Counter(t for p in all_pages for t in p["tags"])
    # 平均链接数按「出链 + 入链」算，孤岛页一目了然
    link_counts = [p["outlinks"] + len(p["backlinks"]) for p in notes]
    avg_links = (sum(link_counts) / len(link_counts)) if link_counts else 0.0

    print(f"stats: {root.name}")
    print(f"  notes          : {len(notes)}")
    print(f"  raw            : {len(raw)}")
    print(f"  total words    : {total_words}")
    print(f"  avg words/note : {total_words / len(all_pages):.0f}" if all_pages else "  avg words/note : 0")
    print(f"  avg links/note : {avg_links:.2f}  (出入链合计)")
    print(f"  distinct tags  : {len(tag_counter)}")
    print(f"  generated_at   : {index.get('generated_at', '?')}")
    print()

    print("  [标签分布] top 10")
    if tag_counter:
        top = tag_counter.most_common(10)
        width = max(display_width(t) for t, _ in top)
        for tag, n in top:
            bar = "█" * min(n, 30)
            print(f"    {pad(tag, width)}  {n:>3}  {bar}")
    else:
        print("    (无标签；用 #标签 给笔记分类)")

    if notes:
        top = sorted(notes, key=lambda p: -p["outlinks"])[:5]
        print()
        print("  [出链最多] top 5")
        for p in top:
            print(f"    {p['outlinks']:>3}  {p['path']}")

    if index["unresolved_links"]:
        print()
        print(f"  [警告] {len(index['unresolved_links'])} 条断链，"
              f"跑 lint 看详情")
    return 0


# ---------------------------------------------------------------- 入口


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="wiki_build.py",
        description="个人知识库构建器：初始化 / 索引 / 检索 / 体检 / 统计（纯标准库）",
        epilog="示例：python3 wiki_build.py init mywiki && "
               "python3 wiki_build.py index mywiki",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="初始化 wiki 目录结构")
    s.add_argument("dir", help="wiki 根目录（不存在则创建）")
    s.add_argument("--force", action="store_true", help="目标目录非空时也继续")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("index", help="扫描 raw/ 与 notes/ 重建 index.json")
    s.add_argument("dir")
    s.set_defaults(func=cmd_index)

    s = sub.add_parser("search", help="在索引上检索（标题>标签>正文）")
    s.add_argument("dir")
    s.add_argument("keyword")
    s.add_argument("--limit", type=int, default=20, help="最多显示条数（默认 20）")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("lint", help="检查孤儿/断链/空笔记（有发现则退出码 1）")
    s.add_argument("dir")
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser("stats", help="输出总量、标签分布与链接密度")
    s.add_argument("dir")
    s.set_defaults(func=cmd_stats)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except WikiError as e:
        die(str(e))
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
