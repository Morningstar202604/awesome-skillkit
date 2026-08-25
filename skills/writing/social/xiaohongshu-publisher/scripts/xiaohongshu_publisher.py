#!/usr/bin/env python3
"""xiaohongshu_publisher.py - 小红书发布客户端（Web 端内部 API）。

⚠️ 小红书没有公开的开放 API。本脚本使用的端点来自社区通用实践
（抓取 www.xiaohongshu.com Web 端请求）。平台随时可能调整端点或字段——
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里
确认一次，如有出入直接修改下方 ENDPOINTS 常量。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖浏览器 Cookie（含 xhs_track、a1、web_session 等），从环境变量
    XHS_COOKIE 或 --cookie-file 读取；禁止把 Cookie 写入仓库。

子命令：
  draft-save           保存草稿，返回 note_id
  publish   NOTE_ID    发布草稿
  edit      NOTE_ID    编辑已发布笔记
  delete    NOTE_ID    删除笔记

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
    "draft_save": "https://www.xiaohongshu.com/api/sns/web/v1/note/create",
    "publish": "https://www.xiaohongshu.com/api/sns/web/v1/note/publish",
    "edit": "https://www.xiaohongshu.com/api/sns/web/v1/note/update",
    "delete": "https://www.xiaohongshu.com/api/sns/web/v1/note/delete",
}
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class XhsAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("xhs code=%s msg=%s" % (code, msg))
        self.code = code


def build_note_payload(title, content, tags, images, cover_image="") -> dict:
    """小红书笔记载荷：content 支持富文本/Markdown 混合。"""
    return {
        "title": title,
        "content": content,
        "tags": tags,
        "images": images,  # 图片 URL 列表
        "cover_image": cover_image,
        "source": "web",
    }


def parse_xhs_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("code") not in (0, 200, None):
        raise XhsAPIError(data.get("code"), data.get("msg", data.get("message", "")))
    return data


def load_cookie(args) -> str:
    return load_credential(
        env="XHS_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def http_json(
    url: str, cookie=None, payload: dict | None = None, method="POST"
) -> dict:
    return parse_xhs_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://www.xiaohongshu.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_draft_save(args):
    payload = build_note_payload(
        args.title,
        args.content,
        args.tags.split(",") if args.tags else [],
        args.images.split(",") if args.images else [],
        args.cover_image,
    )
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["draft_save"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["draft_save"])
    print(dump_json({k: v for k, v in payload.items() if k != "content"}))


def cmd_publish(args):
    if dry_run_guard(args.execute):
        data = http_json(
            ENDPOINTS["publish"], load_cookie(args), {"note_id": args.note_id}
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["publish"])


def cmd_edit(args):
    payload = build_note_payload(
        args.title,
        args.content,
        args.tags.split(",") if args.tags else [],
        args.images.split(",") if args.images else [],
        args.cover_image,
    )
    payload["note_id"] = args.note_id
    if dry_run_guard(args.execute):
        data = http_json(ENDPOINTS["edit"], load_cookie(args), payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["edit"])
    print(dump_json({k: v for k, v in payload.items() if k != "content"}))


def cmd_delete(args):
    if dry_run_guard(args.execute):
        data = http_json(
            ENDPOINTS["delete"], load_cookie(args), {"note_id": args.note_id}
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", ENDPOINTS["delete"])


def main(argv=None):
    ap = argparse.ArgumentParser(description="小红书发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="完整 Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("draft-save", cmd_draft_save)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--images", default="", help="图片 URL 列表，逗号分隔")
    p.add_argument("--cover-image", default="")

    p = add("publish", cmd_publish)
    p.add_argument("note_id")

    p = add("edit", cmd_edit)
    p.add_argument("note_id")
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--images", default="")
    p.add_argument("--cover-image", default="")

    p = add("delete", cmd_delete)
    p.add_argument("note_id")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
