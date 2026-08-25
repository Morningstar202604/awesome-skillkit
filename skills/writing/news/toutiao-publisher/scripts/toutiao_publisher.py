#!/usr/bin/env python3
"""toutiao_publisher.py - 今日头条/抖音文章发布客户端（官方开放平台 + Web 内部 API）。

头条/抖音有官方开放平台 API（需申请 AppKey），也可用 Web 内部 API（Cookie 认证）。
本脚本支持：
  - 文章发布（官方 API：/api/articles/publish）
  - 微头条发布（Web 内部 API）

⚠️ Web 内部 API 端点来自社区通用实践，平台随时可能调整。
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里确认。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 官方 API 凭据从环境变量读取；Web Cookie 从 TOUTIAO_COOKIE 或 --cookie-file 读取。

子命令：
  article-publish    发布文章（官方 API）
  micro-post         发布微头条（Web 内部 API）

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

# 官方 API 端点
OFFICIAL_API = "https://open.toutiao.com/api"
# Web 内部 API 端点
WEB_API = "https://www.toutiao.com/api"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class ToutiaoAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("toutiao code=%s msg=%s" % (code, msg))
        self.code = code


def get_official_token(args) -> str:
    token = os.environ.get("TOUTIAO_ACCESS_TOKEN", "")
    if not token:
        appid = os.environ.get("TOUTIAO_APPID", "")
        secret = os.environ.get("TOUTIAO_APPSECRET", "")
        if not appid or not secret:
            raise SystemExit(
                "官方 API 需要 TOUTIAO_ACCESS_TOKEN 或 TOUTIAO_APPID/TOUTIAO_APPSECRET"
            )
        raise SystemExit("请先设置 TOUTIAO_ACCESS_TOKEN 环境变量")
    return token


def get_web_cookie(args) -> str:
    return load_credential(
        env="TOUTIAO_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def parse_toutiao_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("code") not in (0, 200, None):
        raise ToutiaoAPIError(
            data.get("code"), data.get("msg", data.get("message", ""))
        )
    return data


def http_official(
    url: str, token: str, payload: dict | None = None, method="POST"
) -> dict:
    full_url = url + (
        "?access_token=" + token if "?" not in url else "&access_token=" + token
    )
    return parse_toutiao_response(
        _http_json(
            full_url,
            payload=payload,
            method=method,
        )
    )


def http_web(url: str, cookie: str, payload: dict | None = None, method="POST") -> dict:
    return parse_toutiao_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://www.toutiao.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_article_publish(args):
    token = get_official_token(args)
    payload = {
        "title": args.title,
        "content": args.content,
        "cover_urls": args.cover_images.split(",") if args.cover_images else [],
        "tags": args.tags.split(",") if args.tags else [],
    }
    if dry_run_guard(args.execute):
        data = http_official(
            OFFICIAL_API + "/articles/publish",
            get_official_token(args),
            payload,
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", OFFICIAL_API + "/articles/publish")
    print(dump_json(payload))


def cmd_micro_post(args):
    cookie = get_web_cookie(args)
    payload = {
        "content": args.content,
        "images": args.images.split(",") if args.images else [],
    }
    if dry_run_guard(args.execute):
        data = http_web(
            WEB_API + "/microblog/create",
            cookie,
            payload,
            headers={
                "Referer": "https://www.toutiao.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", WEB_API + "/microblog/create")
    print(dump_json(payload))


def main(argv=None):
    ap = argparse.ArgumentParser(description="今日头条/抖音发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="Web Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("article-publish", cmd_article_publish)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--cover-images", default="", help="封面图 URL 列表，逗号分隔")
    p.add_argument("--tags", default="")

    p = add("micro-post", cmd_micro_post)
    p.add_argument("--content", required=True)
    p.add_argument("--images", default="")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
