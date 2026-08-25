#!/usr/bin/env python3
"""csdn_publisher.py - CSDN 博客发布/管理客户端（Web 端内部 API）。

⚠️ CSDN 没有公开的开放 API。本脚本使用的端点来自社区通用实践
（抓取 blog.csdn.net Web 端请求）。平台随时可能调整端点或字段——
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里
确认一次，如有出入直接修改下方 ENDPOINTS 常量。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖浏览器 Cookie（含 uuid_tt_dd、UserIdentity 等），从环境变量
    CSDN_COOKIE 或 --cookie-file 读取；禁止把 Cookie 写入仓库。

子命令：
  categories           拉取分类列表（用于取 category_id）
  draft-save           保存草稿，返回 article_id
  publish   ARTICLE_ID 发布草稿
  edit      ARTICLE_ID 编辑已发布文章
  delete    ARTICLE_ID 删除文章（移至回收站）
  list                 列出我的文章

退出码：0 成功；1 API 错误或参数错误。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# 复用发布公共工具（HTTP / dry-run 守卫 / 凭据），避免重复造轮子
_common = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "_common"
    )
)
if os.path.isdir(_common) and _common not in sys.path:
    sys.path.insert(0, _common)
from publish_common import (
    http_json as _http_json,
    dry_run_guard,
    load_credential,
    dump_json,
)

# ---- 端点常量（VERIFY BEFORE USE —— 首次使用请按 SKILL.md 核对）----
ENDPOINTS = {
    "categories": "https://blog.csdn.net/api/articles/category/list",
    "draft_save": "https://blog.csdn.net/api/articles/save",
    "publish": "https://blog.csdn.net/api/articles/publish",
    "edit": "https://blog.csdn.net/api/articles/update",
    "delete": "https://blog.csdn.net/api/articles/delete",
    "list": "https://blog.csdn.net/api/articles/list",
}
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class CsdnAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("csdn code=%s msg=%s" % (code, msg))
        self.code = code


def build_article_payload(
    title, markdown, brief, category_id, tags, cover_image=""
) -> dict:
    return {
        "title": title,
        "markdown_content": markdown,
        "brief": brief,
        "category_id": str(category_id),
        "tags": tags,
        "cover_image": cover_image,
        "is_original": 1,
    }


def build_publish_payload(article_id, article_payload: dict) -> dict:
    payload = dict(article_payload)
    payload["article_id"] = str(article_id)
    return payload


def parse_csdn_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("code") not in (0, 200, None):
        raise CsdnAPIError(data.get("code"), data.get("msg", data.get("message", "")))
    return data


def load_cookie(args) -> str:
    return load_credential(
        env="CSDN_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def http_json(url: str, cookie=None, payload: dict | None = None) -> dict:
    """CSDN 接口封装：经公共 http_json 发送并做业务错误检查。"""
    return parse_csdn_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            headers={
                "Referer": "https://blog.csdn.net/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_categories(args):
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["categories"], load_cookie(args))
        print(dump_json(data)[:4000])
        return
    print("[PLAN] GET", ENDPOINTS["categories"])


def cmd_draft_save(args):
    payload = build_article_payload(
        args.title,
        args.markdown,
        args.brief,
        args.category_id,
        args.tags.split(",") if args.tags else [],
        args.cover_image,
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["draft_save"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["draft_save"])
    print(dump_json({k: v for k, v in payload.items() if k != "markdown_content"}))


def cmd_publish(args):
    payload = build_publish_payload(
        args.article_id,
        build_article_payload(
            args.title,
            args.markdown,
            args.brief,
            args.category_id,
            args.tags.split(",") if args.tags else [],
            args.cover_image,
        ),
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["publish"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["publish"])
    print(dump_json({k: v for k, v in payload.items() if k != "markdown_content"}))


def cmd_edit(args):
    with open(args.markdown_file, encoding="utf-8-sig") as fh:
        md = fh.read()
    payload = build_publish_payload(
        args.article_id,
        build_article_payload(
            args.title,
            md,
            args.brief,
            args.category_id,
            args.tags.split(",") if args.tags else [],
            args.cover_image,
        ),
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["edit"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["edit"])
    print(
        dump_json(
            {k: v for k, v in payload.items() if k not in ("markdown_content", "html")}
        )
    )


def cmd_delete(args):
    payload = {"article_id": args.article_id}
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["delete"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["delete"])
    print(dump_json(payload))


def cmd_list(args):
    url = ENDPOINTS["list"]
    if dry_run_guard(args.execute):
        data = http_json(url, load_cookie(args), {"page": args.page, "size": args.size})
        print(dump_json(data)[:4000])
        return
    print("[PLAN] POST", url)


def main(argv=None):
    ap = argparse.ArgumentParser(description="CSDN 博客发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="完整 Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    add("categories", cmd_categories)

    p = add("draft-save", cmd_draft_save)
    p.add_argument("--title", required=True)
    p.add_argument("--markdown", required=True)
    p.add_argument("--brief", default="")
    p.add_argument("--category-id", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--cover-image", default="")

    p = add("publish", cmd_publish)
    p.add_argument("article_id")
    p.add_argument("--title", required=True)
    p.add_argument("--markdown", required=True)
    p.add_argument("--brief", default="")
    p.add_argument("--category-id", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--cover-image", default="")

    p = add("edit", cmd_edit)
    p.add_argument("article_id")
    p.add_argument("--title", required=True)
    p.add_argument("--markdown-file", required=True)
    p.add_argument("--brief", default="")
    p.add_argument("--category-id", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--cover-image", default="")

    p = add("delete", cmd_delete)
    p.add_argument("article_id")

    p = add("list", cmd_list)
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--size", type=int, default=20)

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
