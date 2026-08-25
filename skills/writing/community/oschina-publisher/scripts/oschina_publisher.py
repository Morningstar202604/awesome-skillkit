#!/usr/bin/env python3
"""oschina_publisher.py - 开源中国发布客户端（官方开放平台 API + Web 内部 API）。

开源中国有官方开放平台 API（需申请 AppKey），也可用 Web 内部 API（Cookie 认证）。
本脚本支持：
  - 博客发布（官方 API）
  - 问答/动态发布（Web 内部 API）

⚠️ Web 内部 API 端点来自社区通用实践，平台随时可能调整。
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里确认。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 官方 API 凭据从环境变量读取；Web Cookie 从 OSCHINA_COOKIE 或 --cookie-file 读取。

子命令：
  blog-publish      发布博客（官方 API）
  question-ask      提问（Web 内部 API）
  dynamic-post      发布动态（Web 内部 API）

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
OFFICIAL_API = "https://www.oschina.net/action/openapi"
# Web 内部 API 端点
WEB_API = "https://www.oschina.net/action/api"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class OscAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("oschina code=%s msg=%s" % (code, msg))
        self.code = code


def get_official_token(args) -> str:
    token = os.environ.get("OSCHINA_ACCESS_TOKEN", "")
    if not token:
        raise SystemExit("需要 OSCHINA_ACCESS_TOKEN 环境变量")
    return token


def get_web_cookie(args) -> str:
    return load_credential(
        env="OSCHINA_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def parse_osc_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("errorCode") not in (0, None):
        raise OscAPIError(
            data.get("errorCode"), data.get("errorMessage", data.get("msg", ""))
        )
    return data


def http_official(
    url: str, token: str, payload: dict | None = None, method="POST"
) -> dict:
    full_url = url + (
        "?access_token=" + token if "?" not in url else "&access_token=" + token
    )
    return parse_osc_response(
        _http_json(
            full_url,
            payload=payload,
            method=method,
        )
    )


def http_web(url: str, cookie: str, payload: dict | None = None, method="POST") -> dict:
    return parse_osc_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://www.oschina.net/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_blog_publish(args):
    token = get_official_token(args)
    payload = {
        "title": args.title,
        "content": args.content,
        "tags": args.tags.split(",") if args.tags else [],
        "catalog": args.catalog,
    }
    if dry_run_guard(args.execute):
        data = http_official(
            OFFICIAL_API + "/blog/add",
            token,
            payload,
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", OFFICIAL_API + "/blog/add")
    print(dump_json(payload))


def cmd_question_ask(args):
    cookie = get_web_cookie(args)
    payload = {
        "title": args.title,
        "description": args.content,
        "tags": args.tags.split(",") if args.tags else [],
    }
    if dry_run_guard(args.execute):
        data = http_web(
            WEB_API + "/question/add",
            cookie,
            payload,
            headers={
                "Referer": "https://www.oschina.net/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", WEB_API + "/question/add")
    print(dump_json(payload))


def cmd_dynamic_post(args):
    cookie = get_web_cookie(args)
    payload = {
        "content": args.content,
        "images": args.images.split(",") if args.images else [],
    }
    if dry_run_guard(args.execute):
        data = http_web(
            WEB_API + "/dynamic/add",
            cookie,
            payload,
            headers={
                "Referer": "https://www.oschina.net/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", WEB_API + "/dynamic/add")
    print(dump_json(payload))


def main(argv=None):
    ap = argparse.ArgumentParser(description="开源中国发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="Web Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("blog-publish", cmd_blog_publish)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--catalog", type=int, required=True)

    p = add("question-ask", cmd_question_ask)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default="")

    p = add("dynamic-post", cmd_dynamic_post)
    p.add_argument("--content", required=True)
    p.add_argument("--images", default="")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
