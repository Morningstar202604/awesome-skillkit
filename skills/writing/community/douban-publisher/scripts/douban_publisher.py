#!/usr/bin/env python3
"""douban_publisher.py - 豆瓣日记/广播/小组发布客户端（Web 内部 API）。

⚠️ 豆瓣没有公开的开放 API（早期有 OAuth API 已停止维护）。本脚本使用的端点来自社区通用实践
（抓取 www.douban.com Web 端请求）。平台随时可能调整端点或字段——
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里
确认一次，如有出入直接修改下方 ENDPOINTS 常量。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖浏览器 Cookie（含 dbcl2、ck、_vwo_uuid_v2 等），从环境变量
    DOUBAN_COOKIE 或 --cookie-file 读取；禁止把 Cookie 写入仓库。

子命令：
  note-create      创建日记
  status-post      发布广播
  group-topic      发布小组话题

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
    "note_create": "https://www.douban.com/j/note/new",
    "status_post": "https://www.douban.com/j/status/new",
    "group_topic": "https://www.douban.com/j/group/topic/new",
}
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class DoubanAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("douban code=%s msg=%s" % (code, msg))
        self.code = code


def build_note_payload(title, content, privacy=0) -> dict:
    """privacy: 0=公开, 1=仅自己可见, 2=好友可见"""
    return {
        "title": title,
        "content": content,
        "privacy": str(privacy),
    }


def build_status_payload(content) -> dict:
    return {"text": content}


def build_group_topic_payload(group_id, title, content) -> dict:
    return {
        "group_id": str(group_id),
        "title": title,
        "content": content,
    }


def parse_douban_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("r") not in (0, None):  # 豆瓣约定 r=0 表示成功，非 0 均为错误
        raise DoubanAPIError(data.get("r"), data.get("msg", data.get("err", "")))
    return data


def load_cookie(args) -> str:
    return load_credential(
        env="DOUBAN_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def http_json(
    url: str, cookie=None, payload: dict | None = None, method="POST"
) -> dict:
    return parse_douban_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://www.douban.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_note_create(args):
    payload = build_note_payload(args.title, args.content, args.privacy)
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["note_create"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["note_create"])
    print(dump_json(payload))


def cmd_status_post(args):
    payload = build_status_payload(args.content)
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["status_post"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["status_post"])
    print(dump_json(payload))


def cmd_group_topic(args):
    payload = build_group_topic_payload(args.group_id, args.title, args.content)
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["group_topic"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["group_topic"])
    print(dump_json(payload))


def main(argv=None):
    ap = argparse.ArgumentParser(description="豆瓣发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="完整 Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("note-create", cmd_note_create)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--privacy", type=int, default=0, choices=[0, 1, 2])

    p = add("status-post", cmd_status_post)
    p.add_argument("--content", required=True)

    p = add("group-topic", cmd_group_topic)
    p.add_argument("group_id")
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
