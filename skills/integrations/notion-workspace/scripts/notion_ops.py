#!/usr/bin/env python3
"""notion_ops.py -- Notion API 请求构造器与响应解析器（离线，不发网络请求）。

设计原则
--------
1. **纯函数**：本脚本只做「构造请求体」与「解析响应」两件事，绝不调用
   `requests` / `urllib` 发 HTTP。因此它不需要任何凭证即可完整测试。
2. **dry-run 优先**：`build-*` 系列只打印将要发送的 JSON，落盘与否由人决定。
3. **凭证不落盘**：脚本从不读取 token；真正发送时代理层用
   `os.environ["NOTION_TOKEN"]` 在请求头里临时取用。
4. **版本头固定**：`NOTION_VERSION` 是唯一版本事实源，改版本只改这一处。

子命令
------
  build-page            --title X [--blocks f.json] [--parent ID] [--parent-type page|database]
  build-database-query  --database ID [--filter f.json] [--sorts s.json] [--page-size N] [--start-cursor C]
  parse-page            --json f.json [--raw]
  blocks-to-markdown    --json f.json

Stdlib only. Python >= 3.8.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Notion 要求所有请求带 Notion-Version 头；不带会收到 400。
# 2022-06-28 是长期稳定版：页面属性、数据库查询、块子元素的语义都以它为准。
NOTION_VERSION = "2022-06-28"

# 单次请求的富文本/数组上限。Notion 服务端对 children 有 100 个块的硬上限，
# 富文本数组同理；分页拉取时写操作会把这些限制暴露成 400。
MAX_CHILDREN_PER_REQUEST = 100
MAX_RICH_TEXT_ITEMS = 100

# 页面默认图标：用 emoji 而非外链图片，避免上传附件带来的额外权限。
DEFAULT_ICON = {"type": "emoji", "emoji": "📄"}

# 支持的块类型白名单 —— 只允许映射表里明确覆盖的类型，
# 未知类型一律报错而不是猜，防止静默产出 Notion 不认的负载。
SUPPORTED_BLOCKS = {
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "code",
    "quote",
    "callout",
    "divider",
}

# Markdown 渲染前缀：块类型 -> (前缀, 是否需要闭合围栏)
MARKDOWN_PREFIX = {
    "heading_1": "# ",
    "heading_2": "## ",
    "heading_3": "### ",
    "bulleted_list_item": "- ",
    "numbered_list_item": "1. ",
    "quote": "> ",
    "callout": "> [!NOTE] ",
}

# 富文本 annotation -> Markdown 包裹符。顺序敏感：先长后短，避免
# `**` 先匹配掉 `***` 的情形。
ANNOTATION_WRAPS = [
    ("code", "`", "`"),
    ("bold", "**", "**"),
    ("italic", "*", "*"),
    ("strikethrough", "~~", "~~"),
    ("underline", "<u>", "</u>"),
]


class BuildError(Exception):
    """请求体构造失败（输入不合法，而非网络问题）。"""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    """读取一个 JSON 文件；失败时抛出可读异常而不是栈回溯。"""
    p = Path(path)
    if not p.is_file():
        raise BuildError(f"{what} 文件不存在: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"{what} 不是合法 JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    """统一输出风格：ensure_ascii=False 保中文可读，缩进 2 便于人工审阅。"""
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# 富文本与块
# ---------------------------------------------------------------------------
def rich_text(text: str, link: str | None = None) -> list:
    """把一个字符串包成 Notion 富文本数组。

    Notion 的富文本是数组而非字符串，是为了支持一段文字里混排多种样式。
    这里只生成单个元素：纯文本 + 可选链接。
    """
    item = {"type": "text", "text": {"content": text}}
    if link:
        item["text"]["link"] = {"url": link}
    return [item]


def make_block(kind: str, text: str = "", *, checked: bool = False,
               language: str = "plain text", icon: str = "💡") -> dict:
    """构造单个块对象。文本内容统一走 rich_text 包装。"""
    if kind not in SUPPORTED_BLOCKS:
        raise BuildError(
            f"不支持的块类型 '{kind}'；支持: {', '.join(sorted(SUPPORTED_BLOCKS))}"
        )
    if kind == "divider":
        return {"object": "block", "type": "divider", "divider": {}}

    body: dict = {"rich_text": rich_text(text)}
    if kind == "to_do":
        body["checked"] = bool(checked)
    elif kind == "code":
        body["language"] = language
    elif kind == "callout":
        body["icon"] = {"type": "emoji", "emoji": icon}

    return {"object": "block", "type": kind, kind: body}


def _wrap_annotations(text: str, ann: dict) -> str:
    """按 annotation 给文本加 Markdown 包裹符（由内到外依次套）。"""
    out = text
    for key, left, right in ANNOTATION_WRAPS:
        if ann.get(key):
            out = f"{left}{out}{right}"
    return out


def rich_text_to_md(items: list) -> str:
    """把富文本数组渲染回 Markdown 片段。"""
    parts = []
    for it in items or []:
        plain = (it.get("plain_text") or "").strip("\n")
        if not plain:
            continue
        rendered = _wrap_annotations(plain, it.get("annotations") or {})
        href = (it.get("href") or "")
        if href:
            rendered = f"[{rendered}]({href})"
        parts.append(rendered)
    return "".join(parts)


# ---------------------------------------------------------------------------
# build-page
# ---------------------------------------------------------------------------
def build_page_request(title: str, blocks: list, parent_id: str | None,
                       parent_type: str) -> dict:
    """构造创建页面的请求体（POST /v1/pages）。

    parent 的结构在「父页面」与「父数据库」两种场景下不同：
      - page:     {"type": "page_id",     "page_id": "..."}
      - database: {"type": "database_id", "database_id": "..."}
    这一差异是最常见的 400 来源，所以由命令行显式区分而非自动猜测。
    """
    if not title.strip():
        raise BuildError("标题不能为空")
    if len(blocks) > MAX_CHILDREN_PER_REQUEST:
        raise BuildError(
            f"子块 {len(blocks)} 个，超过单请求上限 {MAX_CHILDREN_PER_REQUEST}；"
            "请拆批：先建页面，再用 PATCH /v1/blocks/{id}/children 追加"
        )

    if parent_type == "database":
        if not parent_id:
            raise BuildError("--parent-type database 时必须提供 --parent（数据库 ID）")
        parent = {"type": "database_id", "database_id": parent_id}
        # 数据库的标题列名取决于表结构，默认取约定俗成的 Name，
        # 真实场景请先用 parse-page 读一条已有记录核对列名。
        properties = {"Name": {"title": rich_text(title)}}
    else:
        if not parent_id:
            raise BuildError(
                "必须提供 --parent（父页面 ID；workspace 根不支持 API 建页）"
            )
        parent = {"type": "page_id", "page_id": parent_id}
        # 挂在父页面下的子页面，标题不是 property 而是页面级 title 字段
        properties = {"title": {"title": rich_text(title)}}

    payload = {
        "parent": parent,
        "icon": DEFAULT_ICON,
        "properties": properties,
    }
    if blocks:
        payload["children"] = blocks
    return payload


def cmd_build_page(args) -> int:
    blocks: list = []
    if args.blocks:
        raw = _load_json(args.blocks, "--blocks")
        if not isinstance(raw, list):
            return _die("--blocks 文件必须是 JSON 数组，元素形如 "
                        '{"type": "paragraph", "text": "..."}')
        converted = []
        for i, item in enumerate(raw, 1):
            if not isinstance(item, dict) or "type" not in item:
                return _die(f"--blocks 第 {i} 个元素缺少 type 字段")
            converted.append(make_block(
                item["type"],
                item.get("text", ""),
                checked=item.get("checked", False),
                language=item.get("language", "plain text"),
                icon=item.get("icon", "💡"),
            ))
        blocks = converted

    payload = build_page_request(args.title, blocks, args.parent, args.parent_type)

    print(f"# DRY-RUN：以下为将发送到 POST https://api.notion.com/v1/pages 的请求体")
    print(f"# 请求头（token 运行时从环境变量注入，不落盘）：")
    print(f"#   Authorization: Bearer $NOTION_TOKEN")
    print(f"#   Notion-Version: {NOTION_VERSION}")
    print(f"#   Content-Type: application/json")
    print(f"# 子块数：{len(blocks)} / 上限 {MAX_CHILDREN_PER_REQUEST}")
    _dump(payload)
    print()
    print("# 未发送任何请求。接上真实凭证后由 AI 用 curl 执行：")
    print("#   curl -sS -X POST https://api.notion.com/v1/pages \\")
    print(f"#     -H \"Authorization: Bearer $NOTION_TOKEN\" \\")
    print(f"#     -H \"Notion-Version: {NOTION_VERSION}\" \\")
    print("#     -H 'Content-Type: application/json' --data @payload.json")
    return 0


# ---------------------------------------------------------------------------
# build-database-query
# ---------------------------------------------------------------------------
def build_query_request(database_id: str, flt: dict | None, sorts: list | None,
                        page_size: int, start_cursor: str | None) -> dict:
    """构造数据库查询请求体（POST /v1/databases/{id}/query）。

    分页是**游标式**：请求带 start_cursor，响应回 has_more/next_cursor，
    没有 offset 概念。所以要翻页必须把上一页的 next_cursor 原样回填。
    """
    if not database_id.strip():
        raise BuildError("database id 不能为空")
    if not 1 <= page_size <= 100:
        raise BuildError(f"page_size 必须在 1..100 之间（当前 {page_size}）——"
                         "这是 Notion 服务端的硬上限")

    payload: dict = {"page_size": page_size}
    if flt:
        payload["filter"] = flt
    if sorts:
        payload["sorts"] = sorts
    if start_cursor:
        payload["start_cursor"] = start_cursor
    return payload


def cmd_build_database_query(args) -> int:
    flt = _load_json(args.filter, "--filter") if args.filter else None
    if flt is not None and not isinstance(flt, dict):
        return _die("--filter 文件必须是 JSON 对象")
    sorts = _load_json(args.sorts, "--sorts") if args.sorts else None
    if sorts is not None and not isinstance(sorts, list):
        return _die("--sorts 文件必须是 JSON 数组")

    payload = build_query_request(
        args.database, flt, sorts, args.page_size, args.start_cursor
    )

    url = f"https://api.notion.com/v1/databases/{args.database}/query"
    print("# DRY-RUN：以下为将发送到数据库查询端点的请求体")
    print(f"# POST {url}")
    print(f"#   Notion-Version: {NOTION_VERSION}")
    _dump(payload)
    print()
    print("# 翻页：响应体里读 has_more 与 next_cursor，")
    print("#       若 has_more 为 true，把 next_cursor 回填到 --start-cursor 再来一次。")
    print("# 限速：Notion 对集成平均限制约 3 req/s，翻页请留间隔并对 429 做退避。")
    return 0


# ---------------------------------------------------------------------------
# parse-page
# ---------------------------------------------------------------------------
def extract_properties(props: dict) -> list:
    """把页面 properties 压平成 [(列名, 值字符串, 列类型)]。

    Notion 的属性值是「按类型分支的对象」，每种类型结构不同：
      title/rich_text -> {"rich_text": [...]}
      select/status   -> {"select": {"name": ...}} / {"status": {"name": ...}}
      multi_select    -> {"multi_select": [{"name": ...}]}
      people          -> {"people": [{"name": ...}]}
      number/checkbox -> 直接是值
    """
    rows = []
    for name, val in (props or {}).items():
        if not isinstance(val, dict):
            rows.append((name, str(val), "unknown"))
            continue
        ptype = val.get("type", "unknown")
        if ptype in ("title", "rich_text"):
            text = rich_text_to_md(val.get(ptype) or [])
        elif ptype in ("select", "status"):
            inner = val.get(ptype) or {}
            text = inner.get("name", "") if isinstance(inner, dict) else ""
        elif ptype == "multi_select":
            text = ", ".join(o.get("name", "") for o in (val.get(ptype) or []))
        elif ptype == "people":
            text = ", ".join(
                (o.get("name") or o.get("id", "")) for o in (val.get(ptype) or [])
            )
        elif ptype == "formula":
            inner = val.get(ptype) or {}
            text = str(inner.get(inner.get("type", ""), ""))
        elif ptype == "relation":
            text = ", ".join(o.get("id", "") for o in (val.get(ptype) or []))
        elif ptype in ("number", "checkbox", "url", "email", "phone_number"):
            text = str(val.get(ptype, ""))
        elif ptype in ("date", "created_time", "last_edited_time"):
            inner = val.get(ptype)
            text = inner.get("start", "") if isinstance(inner, dict) else str(inner or "")
        elif ptype == "files":
            text = ", ".join(f.get("name", "") for f in (val.get(ptype) or []))
        else:
            text = json.dumps(val.get(ptype), ensure_ascii=False)
        rows.append((name, text, ptype))
    return rows


def page_to_markdown(page: dict, blocks: list | None = None) -> str:
    """把页面对象（+ 可选子块）渲染成可读 Markdown。"""
    props = page.get("properties") or {}
    title = ""
    for name, val in props.items():
        if isinstance(val, dict) and val.get("type") == "title":
            title = rich_text_to_md(val.get("title") or []) or name
            break

    out = [f"# {title or '(无标题)'}", ""]
    rows = extract_properties(props)
    if rows:
        out.append("| 属性 | 值 | 类型 |")
        out.append("|---|---|---|")
        for name, text, ptype in rows:
            # 表格里出现裸 | 会撕裂列，统一转义
            safe = text.replace("|", "\\|") or "(空)"
            out.append(f"| {name} | {safe} | {ptype} |")
        out.append("")

    out.append(f"- 页面 ID：`{page.get('id', '(缺失)')}`")
    out.append(f"- URL：{page.get('url', '(缺失)')}")
    if page.get("created_time"):
        out.append(f"- 创建：{page['created_time']}")
    if page.get("last_edited_time"):
        out.append(f"- 最后编辑：{page['last_edited_time']}")

    if blocks:
        out += ["", "## 正文块", ""]
        out.append(blocks_to_markdown(blocks))
    return "\n".join(out)


def cmd_parse_page(args) -> int:
    raw = _load_json(args.json, "--json")
    if args.raw:
        _dump(raw)
        return 0

    # 既接受单页对象，也接受数据库查询响应（{"results": [...]}）
    if isinstance(raw, dict) and "results" in raw:
        pages = raw.get("results") or []
        print(f"# 数据库查询响应：{len(pages)} 条记录"
              f"  has_more={raw.get('has_more')}")
        nxt = raw.get("next_cursor")
        if raw.get("has_more"):
            print(f"# 下一页游标：{nxt}")
        print()
        for i, page in enumerate(pages, 1):
            print(f"## 记录 {i}")
            print(page_to_markdown(page))
            print()
        return 0

    if not isinstance(raw, dict):
        return _die("--json 必须是页面对象或数据库查询响应对象")
    print(page_to_markdown(raw))
    return 0


# ---------------------------------------------------------------------------
# blocks-to-markdown
# ---------------------------------------------------------------------------
def blocks_to_markdown(blocks: list) -> str:
    """把块列表（或 {"results": [...]}）转成 Markdown。

    未知块类型不会中断转换，而是渲染成注释占位——半可读远好于整页丢失。
    """
    if isinstance(blocks, dict):
        blocks = blocks.get("results") or []

    lines: list[str] = []
    for blk in blocks:
        btype = blk.get("type", "")
        body = blk.get(btype) or {}
        text = rich_text_to_md(body.get("rich_text") or [])

        if btype == "divider":
            lines += ["---", ""]
        elif btype == "to_do":
            mark = "x" if body.get("checked") else " "
            lines.append(f"- [{mark}] {text}")
        elif btype == "code":
            lang = body.get("language", "")
            lines += [f"```{lang}", text, "```", ""]
        elif btype in MARKDOWN_PREFIX:
            lines.append(f"{MARKDOWN_PREFIX[btype]}{text}")
        elif btype == "paragraph":
            lines += [text, ""]
        elif btype == "child_page":
            lines += [f"### {body.get('title', '(子页面)')}", ""]
        elif btype == "unsupported":
            lines.append("<!-- 不支持的块 -->")
        else:
            lines.append(f"<!-- 未映射的块类型: {btype} -->")
    return "\n".join(lines).rstrip() + "\n"


def cmd_blocks_to_markdown(args) -> int:
    raw = _load_json(args.json, "--json")
    if not isinstance(raw, (dict, list)):
        return _die("--json 必须是块数组或含 results 的块列表响应")
    sys.stdout.write(blocks_to_markdown(raw))
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="notion_ops.py",
        description="Notion 请求构造与响应解析（离线纯函数，不发网络请求）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build-page", help="构造创建页面请求体并打印（不发送）")
    s.add_argument("--title", required=True)
    s.add_argument("--blocks", help="子块 JSON 文件（数组）")
    s.add_argument("--parent", help="父页面 ID 或父数据库 ID")
    s.add_argument("--parent-type", choices=["page", "database"], default="page")
    s.set_defaults(func=cmd_build_page)

    s = sub.add_parser("build-database-query", help="构造数据库查询请求体并打印")
    s.add_argument("--database", required=True)
    s.add_argument("--filter", help="filter JSON 文件")
    s.add_argument("--sorts", help="sorts JSON 文件")
    s.add_argument("--page-size", type=int, default=50)
    s.add_argument("--start-cursor", help="上一页响应的 next_cursor")
    s.set_defaults(func=cmd_build_database_query)

    s = sub.add_parser("parse-page", help="解析页面/查询响应为 Markdown")
    s.add_argument("--json", required=True)
    s.add_argument("--raw", action="store_true", help="原样打印不解析")
    s.set_defaults(func=cmd_parse_page)

    s = sub.add_parser("blocks-to-markdown", help="把块响应转 Markdown")
    s.add_argument("--json", required=True)
    s.set_defaults(func=cmd_blocks_to_markdown)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BuildError as e:
        return _die(str(e))


if __name__ == "__main__":
    sys.exit(main())
