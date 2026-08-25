#!/usr/bin/env python3
"""v2ex_publisher.py - V2EX 发帖/回复客户端（Web 内部 API）。

⚠️ V2EX 没有公开的开放 API。本脚本使用的端点来自社区通用实践
（抓取 www.v2ex.com Web 端请求）。平台随时可能调整端点或字段——
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里
确认一次，如有出入直接修改下方 ENDPOINTS 常量。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖浏览器 Cookie（含 A2、PB3_SESSION 等），从环境变量
    V2EX_COOKIE 或 --cookie-file 读取；禁止把 Cookie 写入仓库。

子命令：
  topic-create         创建主题帖
  reply-create  TOPIC_ID 回复主题
  node-list            获取节点列表（用于获取 node_id）

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
    "topic_create": "https://www.v2ex.com/api/topics/create",
    "reply_create": "https://www.v2ex.com/api/replies/create",
    "node_list": "https://www.v2ex.com/api/nodes/show.json",
}
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class V2exAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("v2ex code=%s msg=%s" % (code, msg))
        self.code = code


def build_topic_payload(title, content, node_id) -> dict:
    return {
        "title": title,
        "content": content,
        "node_id": str(node_id),
    }


def build_reply_payload(content, topic_id) -> dict:
    return {
        "content": content,
        "topic_id": str(topic_id),
    }


def parse_v2ex_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("status") != "ok" and data.get("code") not in (0, 200, None):
        raise V2exAPIError(data.get("code"), data.get("message", data.get("msg", "")))
    return data


def load_cookie(args) -> str:
    return load_credential(
        env="V2EX_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def http_json(
    url: str, cookie=None, payload: dict | None = None, method="POST"
) -> dict:
    return parse_v2ex_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://www.v2ex.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_topic_create(args):
    payload = build_topic_payload(args.title, args.content, args.node_id)
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["topic_create"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["topic_create"])
    print(dump_json(payload))


def cmd_reply_create(args):
    payload = build_reply_payload(args.content, args.topic_id)
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["reply_create"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["reply_create"])
    print(dump_json(payload))


def cmd_node_list(args):
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["node_list"], load_cookie(args), method="GET")
        print(dump_json(data)[:4000])
        return
    print("[PLAN] GET", ENDPOINTS["node_list"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="V2EX 发帖/回复客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="完整 Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("topic-create", cmd_topic_create)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--node-id", type=int, required=True)

    p = add("reply-create", cmd_reply_create)
    p.add_argument("topic_id")
    p.add_argument("--content", required=True)

    add("node-list", cmd_node_list)

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
