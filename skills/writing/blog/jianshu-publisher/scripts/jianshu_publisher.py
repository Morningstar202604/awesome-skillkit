#!/usr/bin/env python3
"""jianshu_publisher.py - 简书发布客户端（Web 端内部 API）。

⚠️ 简书没有公开的开放 API。本脚本使用的端点来自社区通用实践
（抓取 www.jianshu.com Web 端请求）。平台随时可能调整端点或字段——
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里
确认一次，如有出入直接修改下方 ENDPOINTS 常量。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖浏览器 Cookie（含 remember_user_token、_m7e_session 等），从环境变量
    JIANSHU_COOKIE 或 --cookie-file 读取；禁止把 Cookie 写入仓库。

子命令：
  draft-save           保存草稿，返回 note_id
  publish   NOTE_ID    发布草稿
  edit      NOTE_ID    编辑已发布文章
  delete    NOTE_ID    删除文章

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
    "draft_save": "https://www.jianshu.com/notes",
    "publish": "https://www.jianshu.com/notes/{note_id}/publish",
    "edit": "https://www.jianshu.com/notes/{note_id}",
    "delete": "https://www.jianshu.com/notes/{note_id}",
}
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class JianshuAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("jianshu code=%s msg=%s" % (code, msg))
        self.code = code


def build_note_payload(title, markdown, brief, tags, cover_image="") -> dict:
    return {
        "note": {
            "title": title,
            "content": markdown,
            "brief": brief,
            "tag_names": tags,
            "cover_image": cover_image,
        }
    }


def parse_jianshu_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("status") not in ("ok", "success", None) and data.get("code") not in (
        0,
        200,
        None,
    ):
        raise JianshuAPIError(
            data.get("code"), data.get("message", data.get("msg", ""))
        )
    return data


def load_cookie(args) -> str:
    return load_credential(
        env="JIANSHU_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def http_json(
    url: str, cookie=None, payload: dict | None = None, method="POST"
) -> dict:
    """简书接口封装：经公共 http_json 发送并做业务错误检查。"""
    return parse_jianshu_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://www.jianshu.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_draft_save(args):
    payload = build_note_payload(
        args.title,
        args.markdown,
        args.brief,
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
    url = ENDPOINTS["publish"].format(note_id=args.note_id)
    if dry_run_guard(args.execute):
        data = http_json(url, load_cookie(args), method="PUT")
        print(dump_json(data))
        return
    print("[PLAN] PUT", url)


def cmd_edit(args):
    with open(args.markdown_file, encoding="utf-8-sig") as fh:
        md = fh.read()
    payload = build_note_payload(
        args.title,
        md,
        args.brief,
        args.tags.split(",") if args.tags else [],
        args.cover_image,
    )
    url = ENDPOINTS["edit"].format(note_id=args.note_id)
    if dry_run_guard(args.execute):
        data = http_json(url, load_cookie(args), payload, method="PUT")
        print(dump_json(data))
        return
    print("[PLAN] PUT", url)
    print(dump_json({k: v for k, v in payload.items() if k != "markdown_content"}))


def cmd_delete(args):
    url = ENDPOINTS["delete"].format(note_id=args.note_id)
    if dry_run_guard(args.execute):
        data = http_json(url, load_cookie(args), method="DELETE")
        print(dump_json(data))
        return
    print("[PLAN] DELETE", url)


def main(argv=None):
    ap = argparse.ArgumentParser(description="简书发布客户端（默认 dry-run）")
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
    p.add_argument("--markdown", required=True)
    p.add_argument("--brief", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--cover-image", default="")

    p = add("publish", cmd_publish)
    p.add_argument("note_id")

    p = add("edit", cmd_edit)
    p.add_argument("note_id")
    p.add_argument("--title", required=True)
    p.add_argument("--markdown-file", required=True)
    p.add_argument("--brief", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--cover-image", default="")

    p = add("delete", cmd_delete)
    p.add_argument("note_id")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
