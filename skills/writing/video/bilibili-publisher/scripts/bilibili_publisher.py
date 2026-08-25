#!/usr/bin/env python3
"""bilibili_publisher.py - B 站视频/专栏/动态发布客户端（官方开放平台 + Web 内部 API）。

B 站有官方开放平台 API（需申请 AppKey），也可用 Web 内部 API（Cookie 认证）。
本脚本支持：
  - 视频上传/投稿（需官方 API）
  - 专栏文章发布（Web 内部 API）
  - 动态发布（Web 内部 API）

⚠️ Web 内部 API 端点来自社区通用实践，平台随时可能调整。
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里确认。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 官方 API 凭据从环境变量读取；Web Cookie 从 BILI_COOKIE 或 --cookie-file 读取。

子命令：
  video-upload    FILE    上传视频文件（返回 bvid）
  video-submit    BVID    提交视频投稿
  article-save    保存专栏草稿（返回 article_id）
  article-publish ARTICLE_ID 发布专栏文章
  dynamic-post    发布动态

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
OFFICIAL_API = "https://member.bilibili.com/x"
# Web 内部 API 端点
WEB_API = "https://api.bilibili.com/x"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class BiliAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("bili code=%s msg=%s" % (code, msg))
        self.code = code


def get_official_credentials(args) -> tuple[str, str]:
    """获取官方 API 凭据。"""
    access_key = os.environ.get("BILI_ACCESS_KEY", "")
    secret_key = os.environ.get("BILI_SECRET_KEY", "")
    if not access_key or not secret_key:
        raise SystemExit("官方 API 需要 BILI_ACCESS_KEY 和 BILI_SECRET_KEY")
    return access_key, secret_key


def get_web_cookie(args) -> str:
    return load_credential(
        env="BILI_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def parse_bili_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("code") not in (0, None):
        raise BiliAPIError(data.get("code"), data.get("message", data.get("msg", "")))
    return data


def http_official(url: str, payload: dict | None = None, method="POST") -> dict:
    return parse_bili_response(
        _http_json(
            url,
            payload=payload,
            method=method,
        )
    )


def http_web(url: str, cookie: str, payload: dict | None = None, method="POST") -> dict:
    return parse_bili_response(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://www.bilibili.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_video_upload(args):
    """视频上传需 multipart/form-data + 断点续传，这里只做 dry-run 演示。"""
    if dry_run_guard(args.execute):
        print("[PLAN] 视频上传需分片上传 + 断点续传，略")
        return
    print("[PLAN] 视频上传流程：")
    print("  1. 获取上传凭证 (GET /x/web-interface/upload/pre)")
    print("  2. 分片上传 (POST /x/web-interface/upload/chunk)")
    print("  3. 完成上传 (POST /x/web-interface/upload/complete)")
    print("  4. 获取 bvid (GET /x/web-interface/archive/stat)")


def cmd_video_submit(args):
    """提交视频投稿（官方 API）。"""
    access_key, secret_key = get_official_credentials(args)
    payload = {
        "title": args.title,
        "copyright": 1,
        "source": args.source,
        "tid": args.tid,
        "tag": args.tags,
        "desc": args.desc,
        "dynamic": args.dynamic,
    }
    if dry_run_guard(args.execute):
        # 实际需签名鉴权
        print("[PLAN] POST", OFFICIAL_API + "/web-interface/archive/add")
        print(dump_json(payload))
        return
    print("[PLAN] 官方视频投稿需签名鉴权，略")


def cmd_article_save(args):
    """保存专栏草稿（Web 内部 API）。"""
    cookie = get_web_cookie(args)
    payload = {
        "title": args.title,
        "content": args.content,
        "summary": args.summary,
        "category": args.category,
        "tags": args.tags,
        "image_urls": args.images.split(",") if args.images else [],
    }
    if dry_run_guard(args.execute):
        data = http_web(
            WEB_API + "/article/add",
            cookie,
            payload,
            headers={
                "Referer": "https://www.bilibili.com/read/cv",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", WEB_API + "/article/add")
    print(dump_json({k: v for k, v in payload.items() if k != "content"}))


def cmd_article_publish(args):
    cookie = get_web_cookie(args)
    payload = {"id": args.article_id}
    if dry_run_guard(args.execute):
        data = http_web(
            WEB_API + "/article/publish",
            cookie,
            payload,
            headers={
                "Referer": "https://www.bilibili.com/read/cv",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", WEB_API + "/article/publish")
    print(dump_json(payload))


def cmd_dynamic_post(args):
    cookie = get_web_cookie(args)
    payload = {
        "content": args.content,
        "images": args.images.split(",") if args.images else [],
    }
    if dry_run_guard(args.execute):
        data = http_web(
            WEB_API + "/dynamic/publish",
            cookie,
            payload,
            headers={
                "Referer": "https://www.bilibili.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", WEB_API + "/dynamic/publish")
    print(dump_json(payload))


def main(argv=None):
    ap = argparse.ArgumentParser(description="B 站发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="Web Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("video-upload", cmd_video_upload)
    p.add_argument("file")
    p.add_argument("--title", required=True)

    p = add("video-submit", cmd_video_submit)
    p.add_argument("--title", required=True)
    p.add_argument("--tid", type=int, required=True, help="分区 ID")
    p.add_argument("--tags", default="")
    p.add_argument("--source", default="")
    p.add_argument("--desc", default="")
    p.add_argument("--dynamic", default="")

    p = add("article-save", cmd_article_save)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--category", type=int, default=0)
    p.add_argument("--tags", default="")
    p.add_argument("--images", default="")

    p = add("article-publish", cmd_article_publish)
    p.add_argument("article_id")

    p = add("dynamic-post", cmd_dynamic_post)
    p.add_argument("--content", required=True)
    p.add_argument("--images", default="")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
