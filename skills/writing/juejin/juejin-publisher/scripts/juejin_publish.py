#!/usr/bin/env python3
"""juejin_publish.py - 掘金文章发布客户端（Web 端内部 API）。

⚠️ 掘金没有公开的开放 API。本脚本使用的端点来自社区通用实践
（抓取 juejin.cn Web 端请求）。平台随时可能调整端点或字段——
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里
确认一次，如有出入直接修改下方 ENDPOINTS 常量。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖浏览器 Cookie（含 sessionid_a1），从环境变量
    JUEJIN_COOKIE 或 --cookie-file 读取；禁止把 Cookie 写入仓库。

子命令：
  categories           拉取分类列表（用于取 category_id）
  tags      --category 拉取某分类下标签列表（用于取 tag_id）
  draft-save           保存草稿，返回 article_id
  publish   ARTICLE_ID 发布草稿

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
    load_json,
)

# ---- 端点常量（VERIFY BEFORE USE —— 首次使用请按 SKILL.md 核对）----
ENDPOINTS = {
    "categories": "https://api.juejin.cn/content_api/v1/column/listquery?cursor=0&limit=100",
    "tags": "https://api.juejin.cn/content_api/v1/tag/query_list",
    "draft_save": "https://api.juejin.cn/content_api/v1/article/draft_save",
    "publish": "https://api.juejin.cn/content_api/v1/article/publish",
}


class JuejinAPIError(Exception):
    def __init__(self, err_no, err_msg):
        super().__init__("juejin err_no=%s err_msg=%s" % (err_no, err_msg))
        self.err_no = err_no


# ---------- 纯函数（可单测） ----------


def build_article_payload(
    title, markdown, brief, category_id, tag_ids, cover_image=""
) -> dict:
    """edit_type=10 表示 Markdown 编辑器。"""
    return {
        "category_id": str(category_id),
        "tag_ids": [str(t) for t in tag_ids],
        "link_cover": "",
        "cover_image": cover_image,
        "title": title,
        "brief_content": brief,
        "edit_type": 10,
        "html_content": "",
        "html": "",
        "markdown_content": markdown,
        "theme": None,
        "need_review": True,
    }


def build_publish_payload(article_id, article_payload: dict) -> dict:
    payload = dict(article_payload)
    payload["article_id"] = str(article_id)
    return payload


def parse_juejin_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("err_no") not in (0, None):
        raise JuejinAPIError(data.get("err_no"), data.get("err_msg", ""))
    return data


def load_cookie(args) -> str:
    return load_credential(
        env="JUEJIN_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


# ---------- 网络执行 ----------


def http_json(url: str, cookie=None, payload: dict | None = None) -> dict:
    """掘金接口封装：经公共 http_json 发送并做业务错误检查。"""
    return parse_juejin_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            headers={"Referer": "https://juejin.cn/editor"},
        )
    )


# ---------- 子命令 ----------


def cmd_categories(args):
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["categories"], load_cookie(args))
        print(dump_json(data)[:4000])
        return
    print("[PLAN] GET", ENDPOINTS["categories"])


def cmd_tags(args):
    url = ENDPOINTS["tags"]
    if dry_run_guard(args.execute):
        # 端点为 POST query_list；若实测为 GET 带参，改这里
        data = http_json(
            url, load_cookie(args), {"key": "", "limit": 100, "cursor": "0"}
        )
        print(dump_json(data)[:4000])
        return
    print("[PLAN] POST", url)


def cmd_draft_save(args):
    payload = build_article_payload(
        args.title,
        args.markdown,
        args.brief,
        args.category_id,
        args.tag_ids.split(","),
        args.cover_image,
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["draft_save"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["draft_save"])
    print(dump_json({k: v for k, v in payload.items() if k != "markdown_content"}))


def cmd_publish(args):
    with open(args.markdown_file, encoding="utf-8-sig") as fh:
        md = fh.read()
    payload = build_publish_payload(
        args.article_id,
        build_article_payload(
            args.title,
            md,
            args.brief,
            args.category_id,
            args.tag_ids.split(","),
            args.cover_image,
        ),
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["publish"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["publish"])
    print(
        dump_json(
            {k: v for k, v in payload.items() if k not in ("markdown_content", "html")}
        )
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="掘金发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="完整 Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    add("categories", cmd_categories)
    add("tags", cmd_tags)

    p = add("draft-save", cmd_draft_save)
    p.add_argument("--title", required=True)
    p.add_argument("--markdown", required=True)
    p.add_argument("--brief", default="")
    p.add_argument("--category-id", required=True)
    p.add_argument("--tag-ids", default="")
    p.add_argument("--cover-image", default="")

    p = add("publish", cmd_publish)
    p.add_argument("article_id")
    p.add_argument("--title", required=True)
    p.add_argument("--markdown-file", required=True)
    p.add_argument("--brief", default="")
    p.add_argument("--category-id", required=True)
    p.add_argument("--tag-ids", default="")
    p.add_argument("--cover-image", default="")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
