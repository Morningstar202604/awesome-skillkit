#!/usr/bin/env python3
"""segmentfault_publisher.py - SegmentFault 发布客户端（Web 内部 API）。

⚠️ SegmentFault 没有公开的开放 API。本脚本使用的端点来自社区通用实践
（抓取 segmentfault.com Web 端请求）。平台随时可能调整端点或字段——
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里
确认一次，如有出入直接修改下方 ENDPOINTS 常量。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖浏览器 Cookie，从环境变量 SF_COOKIE 或 --cookie-file 读取。

子命令：
  article-save     保存文章草稿（返回 article_id）
  article-publish  发布文章
  question-ask     提问

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
    "article_save": "https://segmentfault.com/api/articles/save",
    "article_publish": "https://segmentfault.com/api/articles/publish",
    "question_ask": "https://segmentfault.com/api/questions/ask",
}
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class SfAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("sf code=%s msg=%s" % (code, msg))
        self.code = code


def build_article_payload(title, content, summary, tags, cover_image="") -> dict:
    return {
        "title": title,
        "content": content,
        "summary": summary,
        "tags": tags.split(",") if tags else [],
        "cover_image": cover_image,
    }


def parse_sf_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("code") not in (0, 1, None):
        raise SfAPIError(data.get("code"), data.get("message", data.get("msg", "")))
    return data


def load_cookie(args) -> str:
    return load_credential(
        env="SF_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def http_json(
    url: str, cookie=None, payload: dict | None = None, method="POST"
) -> dict:
    return parse_sf_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://segmentfault.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_article_save(args):
    payload = build_article_payload(
        args.title, args.content, args.summary, args.tags, args.cover_image
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["article_save"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["article_save"])
    print(dump_json({k: v for k, v in payload.items() if k != "content"}))


def cmd_article_publish(args):
    payload = build_article_payload(
        args.title, args.content, args.summary, args.tags, args.cover_image
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["article_publish"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["article_publish"])
    print(dump_json({k: v for k, v in payload.items() if k != "content"}))


def cmd_question_ask(args):
    payload = {
        "title": args.title,
        "content": args.content,
        "tags": args.tags.split(",") if args.tags else [],
    }
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["question_ask"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["question_ask"])
    print(dump_json(payload))


def main(argv=None):
    ap = argparse.ArgumentParser(description="SegmentFault 发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="完整 Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("article-save", cmd_article_save)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--cover-image", default="")

    p = add("article-publish", cmd_article_publish)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--cover-image", default="")

    p = add("question-ask", cmd_question_ask)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default="")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
