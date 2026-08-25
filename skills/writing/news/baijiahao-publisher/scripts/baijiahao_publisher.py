#!/usr/bin/env python3
"""baijiahao_publisher.py - 百家号发布客户端（官方开放平台 API）。

百家号有官方开放平台 API（需申请 AppKey），文档：https://open.baijiahao.baidu.com/
本脚本支持文章发布、视频发布、草稿箱管理。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 认证依赖官方 API access_token（从环境变量读取）。

子命令：
  article-publish    发布文章
  video-publish      发布视频
  draft-save         保存草稿

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
API_BASE = "https://baijiahao.baidu.com/api"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class BaijiahaoAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("baijiahao code=%s msg=%s" % (code, msg))
        self.code = code


def get_access_token(args) -> str:
    token = os.environ.get("BAIJIAHAO_ACCESS_TOKEN", "")
    if not token:
        appid = os.environ.get("BAIJIAHAO_APPID", "")
        secret = os.environ.get("BAIJIAHAO_APPSECRET", "")
        if not appid or not secret:
            raise SystemExit(
                "需要 BAIJIAHAO_ACCESS_TOKEN 或 BAIJIAHAO_APPID/BAIJIAHAO_APPSECRET"
            )
        raise SystemExit("请先设置 BAIJIAHAO_ACCESS_TOKEN 环境变量")
    return token


def parse_bjh_response(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("errno") not in (0, None):
        raise BaijiahaoAPIError(
            data.get("errno"), data.get("errmsg", data.get("msg", ""))
        )
    return data


def http_json(url: str, token: str, payload: dict | None = None, method="POST") -> dict:
    full_url = url + (
        "?access_token=" + token if "?" not in url else "&access_token=" + token
    )
    return parse_bjh_response(
        _http_json(
            full_url,
            payload=payload,
            method=method,
        )
    )


def cmd_article_publish(args):
    token = get_access_token(args)
    payload = {
        "title": args.title,
        "content": args.content,
        "cover_images": args.cover_images.split(",") if args.cover_images else [],
        "tags": args.tags.split(",") if args.tags else [],
        "category_id": args.category_id,
    }
    if dry_run_guard(args.execute):
        data = http_json(
            API_BASE + "/article/publish",
            token,
            payload,
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", API_BASE + "/article/publish")
    print(dump_json(payload))


def cmd_video_publish(args):
    token = get_access_token(args)
    payload = {
        "title": args.title,
        "description": args.description,
        "video_url": args.video_url,
        "cover_image": args.cover_image,
        "tags": args.tags.split(",") if args.tags else [],
        "category_id": args.category_id,
    }
    if dry_run_guard(args.execute):
        data = http_json(
            API_BASE + "/video/publish",
            token,
            payload,
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", API_BASE + "/video/publish")
    print(dump_json(payload))


def cmd_draft_save(args):
    token = get_access_token(args)
    payload = {
        "title": args.title,
        "content": args.content,
        "cover_images": args.cover_images.split(",") if args.cover_images else [],
        "tags": args.tags.split(",") if args.tags else [],
        "category_id": args.category_id,
    }
    if dry_run_guard(args.execute):
        data = http_json(
            API_BASE + "/article/draft/save",
            token,
            payload,
        )
        print(dump_json(data))
        return
    print("[PLAN] POST", API_BASE + "/article/draft/save")
    print(dump_json(payload))


def main(argv=None):
    ap = argparse.ArgumentParser(description="百家号发布客户端（默认 dry-run）")
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
    p.add_argument("--category-id", type=int, required=True)

    p = add("video-publish", cmd_video_publish)
    p.add_argument("--title", required=True)
    p.add_argument("--description", required=True)
    p.add_argument("--video-url", required=True)
    p.add_argument("--cover-image", required=True)
    p.add_argument("--tags", default="")
    p.add_argument("--category-id", type=int, required=True)

    p = add("draft-save", cmd_draft_save)
    p.add_argument("--title", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--cover-images", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--category-id", type=int, required=True)

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
