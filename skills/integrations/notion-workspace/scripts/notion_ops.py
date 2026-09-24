#!/usr/bin/env python3
"""notion_ops.py -- Notion API request builder and response parser (offline, no
network requests).

Design principles
-----------------
1. **Pure functions**: this script only does two things -- "build a request body" and
   "parse a response" -- and never calls `requests`/`urllib` to send HTTP. It
   therefore needs no credentials to test fully.
2. **Dry-run first**: the `build-*` family only prints the JSON that would be sent;
   whether to write to disk is decided by a human.
3. **Credentials never hit disk**: the script never reads the token; at real send
   time the proxy layer pulls `os.environ["NOTION_TOKEN"]` into the request header.
4. **Version header is fixed**: `NOTION_VERSION` is the single source of truth for
   the version; change the version in this one place.

Subcommands
-----------
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

# Notion requires every request to carry the Notion-Version header; without it you
# get a 400. 2022-06-28 is the long-term stable version: page properties, database
# queries, and block children are all specified against it.
NOTION_VERSION = "2022-06-28"

# Per-request rich-text/array limits. The Notion server enforces a hard limit of
# 100 child blocks, and the same for rich-text arrays; paginated writes surface these
# limits as a 400.
MAX_CHILDREN_PER_REQUEST = 100
MAX_RICH_TEXT_ITEMS = 100

# Default page icon: use an emoji rather than an external image to avoid the extra
# permissions that come with uploading attachments.
DEFAULT_ICON = {"type": "emoji", "emoji": "📄"}

# Supported block-type allowlist -- only types explicitly covered by the mapping
# table are allowed; unknown types raise an error rather than being guessed, to
# prevent silently producing payloads Notion does not recognize.
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

# Markdown render prefix: block type -> (prefix, whether a closing fence is needed)
MARKDOWN_PREFIX = {
    "heading_1": "# ",
    "heading_2": "## ",
    "heading_3": "### ",
    "bulleted_list_item": "- ",
    "numbered_list_item": "1. ",
    "quote": "> ",
    "callout": "> [!NOTE] ",
}

# Rich-text annotation -> Markdown wrapper. Order-sensitive: longer first, to avoid
# `**` matching inside `***`.
ANNOTATION_WRAPS = [
    ("code", "`", "`"),
    ("bold", "**", "**"),
    ("italic", "*", "*"),
    ("strikethrough", "~~", "~~"),
    ("underline", "<u>", "</u>"),
]


class BuildError(Exception):
    """Request-body construction failed (bad input, not a network problem)."""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    """Read a JSON file; on failure raise a readable error instead of a traceback."""
    p = Path(path)
    if not p.is_file():
        raise BuildError(f"{what} file does not exist: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"{what} is not valid JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    """Unified output style: ensure_ascii=False keeps text readable, indent 2 for review."""
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Rich text and blocks
# ---------------------------------------------------------------------------
def rich_text(text: str, link: str | None = None) -> list:
    """Wrap a string into a Notion rich-text array.

    Notion rich text is an array rather than a string, to support mixing styles
    within one run. Here we generate a single element: plain text + optional link.
    """
    item = {"type": "text", "text": {"content": text}}
    if link:
        item["text"]["link"] = {"url": link}
    return [item]


def make_block(kind: str, text: str = "", *, checked: bool = False,
               language: str = "plain text", icon: str = "💡") -> dict:
    """Build a single block object. Text content always goes through rich_text."""
    if kind not in SUPPORTED_BLOCKS:
        raise BuildError(
            f"unsupported block type '{kind}'; supported: {', '.join(sorted(SUPPORTED_BLOCKS))}"
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
    """Wrap text with Markdown markers per annotation (outermost applied last)."""
    out = text
    for key, left, right in ANNOTATION_WRAPS:
        if ann.get(key):
            out = f"{left}{out}{right}"
    return out


def rich_text_to_md(items: list) -> str:
    """Render a rich-text array back into a Markdown fragment."""
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
    """Build the create-page request body (POST /v1/pages).

    The parent shape differs between the "parent page" and "parent database" cases:
      - page:     {"type": "page_id",     "page_id": "..."}
      - database: {"type": "database_id", "database_id": "..."}
    This difference is the most common source of a 400, so it is distinguished
    explicitly on the command line rather than auto-guessed.
    """
    if not title.strip():
        raise BuildError("title must not be empty")
    if len(blocks) > MAX_CHILDREN_PER_REQUEST:
        raise BuildError(
            f"{len(blocks)} child blocks exceeds the per-request limit {MAX_CHILDREN_PER_REQUEST}; "
            "batch it: create the page first, then append via PATCH /v1/blocks/{id}/children"
        )

    if parent_type == "database":
        if not parent_id:
            raise BuildError("--parent-type database requires --parent (the database ID)")
        parent = {"type": "database_id", "database_id": parent_id}
        # The database's title column name depends on the schema; default to the
        # conventional "Name". In real use, read an existing record with parse-page
        # first to confirm the column name.
        properties = {"Name": {"title": rich_text(title)}}
    else:
        if not parent_id:
            raise BuildError(
                "--parent is required (the parent page ID; the workspace root does not "
                "support API page creation)"
            )
        parent = {"type": "page_id", "page_id": parent_id}
        # A subpage under a parent page: the title is a page-level title field, not a property
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
            return _die("--blocks file must be a JSON array, elements like "
                        '{"type": "paragraph", "text": "..."}')
        converted = []
        for i, item in enumerate(raw, 1):
            if not isinstance(item, dict) or "type" not in item:
                return _die(f"--blocks element #{i} is missing the type field")
            converted.append(make_block(
                item["type"],
                item.get("text", ""),
                checked=item.get("checked", False),
                language=item.get("language", "plain text"),
                icon=item.get("icon", "💡"),
            ))
        blocks = converted

    payload = build_page_request(args.title, blocks, args.parent, args.parent_type)

    print(f"# DRY-RUN: request body to be sent to POST https://api.notion.com/v1/pages")
    print(f"# request headers (token injected at runtime from env, not stored):")
    print(f"#   Authorization: Bearer $NOTION_TOKEN")
    print(f"#   Notion-Version: {NOTION_VERSION}")
    print(f"#   Content-Type: application/json")
    print(f"# child blocks: {len(blocks)} / limit {MAX_CHILDREN_PER_REQUEST}")
    _dump(payload)
    print()
    print("# No request sent. With real credentials attached, the AI runs it with curl:")
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
    """Build the database-query request body (POST /v1/databases/{id}/query).

    Pagination is **cursor-based**: the request carries start_cursor, the response
    returns has_more/next_cursor; there is no offset concept. To page, you must
    feed the previous page's next_cursor back verbatim.
    """
    if not database_id.strip():
        raise BuildError("database id must not be empty")
    if not 1 <= page_size <= 100:
        raise BuildError(f"page_size must be between 1 and 100 (got {page_size}) -- "
                         "this is a hard Notion server limit")

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
        return _die("--filter file must be a JSON object")
    sorts = _load_json(args.sorts, "--sorts") if args.sorts else None
    if sorts is not None and not isinstance(sorts, list):
        return _die("--sorts file must be a JSON array")

    payload = build_query_request(
        args.database, flt, sorts, args.page_size, args.start_cursor
    )

    url = f"https://api.notion.com/v1/databases/{args.database}/query"
    print("# DRY-RUN: request body to be sent to the database-query endpoint")
    print(f"# POST {url}")
    print(f"#   Notion-Version: {NOTION_VERSION}")
    _dump(payload)
    print()
    print("# Pagination: read has_more and next_cursor from the response body;")
    print("#       if has_more is true, feed next_cursor back into --start-cursor and run again.")
    print("# Rate limit: Notion averages ~3 req/s per integration; space out pages and back off on 429.")
    return 0


# ---------------------------------------------------------------------------
# parse-page
# ---------------------------------------------------------------------------
def extract_properties(props: dict) -> list:
    """Flatten page properties into [(column name, value string, column type)].

    Notion property values are objects branched by type, each with a different shape:
      title/rich_text -> {"rich_text": [...]}
      select/status   -> {"select": {"name": ...}} / {"status": {"name": ...}}
      multi_select    -> {"multi_select": [{"name": ...}]}
      people          -> {"people": [{"name": ...}]}
      number/checkbox -> the value directly
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
    """Render a page object (+ optional child blocks) into readable Markdown."""
    props = page.get("properties") or {}
    title = ""
    for name, val in props.items():
        if isinstance(val, dict) and val.get("type") == "title":
            title = rich_text_to_md(val.get("title") or []) or name
            break

    out = [f"# {title or '(untitled)'}", ""]
    rows = extract_properties(props)
    if rows:
        out.append("| Property | Value | Type |")
        out.append("|---|---|---|")
        for name, text, ptype in rows:
            # a bare | in a table cell tears the columns; escape it uniformly
            safe = text.replace("|", "\\|") or "(empty)"
            out.append(f"| {name} | {safe} | {ptype} |")
        out.append("")

    out.append(f"- page ID: `{page.get('id', '(missing)')}`")
    out.append(f"- URL: {page.get('url', '(missing)')}")
    if page.get("created_time"):
        out.append(f"- created: {page['created_time']}")
    if page.get("last_edited_time"):
        out.append(f"- last edited: {page['last_edited_time']}")

    if blocks:
        out += ["", "## Body blocks", ""]
        out.append(blocks_to_markdown(blocks))
    return "\n".join(out)


def cmd_parse_page(args) -> int:
    raw = _load_json(args.json, "--json")
    if args.raw:
        _dump(raw)
        return 0

    # accept both a single page object and a database-query response ({"results": [...]})
    if isinstance(raw, dict) and "results" in raw:
        pages = raw.get("results") or []
        print(f"# database query response: {len(pages)} records"
              f"  has_more={raw.get('has_more')}")
        nxt = raw.get("next_cursor")
        if raw.get("has_more"):
            print(f"# next-page cursor: {nxt}")
        print()
        for i, page in enumerate(pages, 1):
            print(f"## record {i}")
            print(page_to_markdown(page))
            print()
        return 0

    if not isinstance(raw, dict):
        return _die("--json must be a page object or a database-query response object")
    print(page_to_markdown(raw))
    return 0


# ---------------------------------------------------------------------------
# blocks-to-markdown
# ---------------------------------------------------------------------------
def blocks_to_markdown(blocks: list) -> str:
    """Convert a block list (or {"results": [...]}) into Markdown.

    Unknown block types do not abort the conversion; they render as a comment
    placeholder -- half-readable is far better than losing the whole page.
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
            lines += [f"### {body.get('title', '(subpage)')}", ""]
        elif btype == "unsupported":
            lines.append("<!-- unsupported block -->")
        else:
            lines.append(f"<!-- unmapped block type: {btype} -->")
    return "\n".join(lines).rstrip() + "\n"


def cmd_blocks_to_markdown(args) -> int:
    raw = _load_json(args.json, "--json")
    if not isinstance(raw, (dict, list)):
        return _die("--json must be a block array or a block-list response containing results")
    sys.stdout.write(blocks_to_markdown(raw))
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="notion_ops.py",
        description="Notion request building and response parsing (offline pure functions, no network)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build-page", help="build the create-page request body and print it (no send)")
    s.add_argument("--title", required=True)
    s.add_argument("--blocks", help="child-blocks JSON file (array)")
    s.add_argument("--parent", help="parent page ID or parent database ID")
    s.add_argument("--parent-type", choices=["page", "database"], default="page")
    s.set_defaults(func=cmd_build_page)

    s = sub.add_parser("build-database-query", help="build the database-query request body and print it")
    s.add_argument("--database", required=True)
    s.add_argument("--filter", help="filter JSON file")
    s.add_argument("--sorts", help="sorts JSON file")
    s.add_argument("--page-size", type=int, default=50)
    s.add_argument("--start-cursor", help="next_cursor from the previous page's response")
    s.set_defaults(func=cmd_build_database_query)

    s = sub.add_parser("parse-page", help="parse a page/query response into Markdown")
    s.add_argument("--json", required=True)
    s.add_argument("--raw", action="store_true", help="print as-is without parsing")
    s.set_defaults(func=cmd_parse_page)

    s = sub.add_parser("blocks-to-markdown", help="convert a block response to Markdown")
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
