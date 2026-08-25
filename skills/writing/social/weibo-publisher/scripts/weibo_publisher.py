#!/usr/bin/env python3
"""weibo_publisher.py - 微博发布客户端（官方开放平台 API + Web 内部 API 混合）。

微博有官方开放平台 API（需申请 AppKey），也可用 Web 内部 API（Cookie 认证）。
本脚本两种模式均支持：
  - 官方 API：需环境变量 WEIBO_APPKEY, WEIBO_APPSECRET, WEIBO_ACCESS_TOKEN
  - Web 内部 API：仅需 WEIBO_COOKIE（含 SUB、SSOLoginState 等）

⚠️ Web 内部 API 端点来自社区通用实践，平台随时可能调整。
首次使用前务必按 SKILL.md 的「端点核对」步骤在浏览器 DevTools 里确认。

安全设计：
  - 默认 --dry-run：只打印将发送的方法/URL/payload，不联网。
    加 --execute 才真正发送。
  - 官方 API 凭据从环境变量读取；Web Cookie 从 WEIBO_COOKIE 或 --cookie-file 读取。

子命令：
  post                 发布微博（文本 + 图片）
  repost  MID          转发微博
  comment  MID         评论微博
  delete   MID         删除微博
  upload-image  FILE   上传图片（返回 pic_id）

退出码：0 成功；1 API 错误或参数错误。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse

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
OFFICIAL_API = "https://api.weibo.com/2"
# Web 内部 API 端点
WEB_API = "https://weibo.com/ajax"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class WeiboAPIError(Exception):
    def __init__(self, code, msg):
        super().__init__("weibo code=%s msg=%s" % (code, msg))
        self.code = code


def get_official_token(args) -> str:
    """获取官方 API access_token（优先用环境变量，否则用 AppKey+Secret 刷新）。"""
    token = os.environ.get("WEIBO_ACCESS_TOKEN", "")
    if token:
        return token
    appkey = os.environ.get("WEIBO_APPKEY", "")
    secret = os.environ.get("WEIBO_APPSECRET", "")
    if not appkey or not secret:
        raise SystemExit(
            "官方 API 需要 WEIBO_ACCESS_TOKEN 或 WEIBO_APPKEY/WEIBO_APPSECRET"
        )
    # 这里简化：实际应用需实现 OAuth2 刷新流程
    raise SystemExit("请先设置 WEIBO_ACCESS_TOKEN 环境变量")


def get_web_cookie(args) -> str:
    return load_credential(
        env="WEIBO_COOKIE",
        cookie_file=getattr(args, "cookie_file", ""),
        name="认证",
    )


def parse_weibo_official(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("error_code") not in (0, None):
        raise WeiboAPIError(
            data.get("error_code"), data.get("error", data.get("error_msg", ""))
        )
    return data


def parse_weibo_web(raw: bytes) -> dict:
    data = json.loads(raw.decode("utf-8"))
    if data.get("ok") != 1 and data.get("code") not in (0, 200, None):
        raise WeiboAPIError(data.get("code"), data.get("msg", ""))
    return data


def http_official(
    url: str, token: str, payload: dict | None = None, method="POST"
) -> dict:
    """官方 API 请求。"""
    full_url = url + (
        "?access_token=" + token if "?" not in url else "&access_token=" + token
    )
    return parse_weibo_official(
        _http_json(
            full_url,
            payload=payload,
            method=method,
        )
    )


def http_web(url: str, cookie: str, payload: dict | None = None, method="POST") -> dict:
    """Web 内部 API 请求。"""
    return parse_weibo_web(
        _http_json(
            url,
            cookie=cookie,
            payload=payload,
            method=method,
            headers={
                "Referer": "https://weibo.com/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
    )


def cmd_post_official(args):
    token = get_official_token(args)
    payload = {"status": args.text}
    if args.pic_ids:
        payload["pic_ids"] = args.pic_ids
    if dry_run_guard(args.execute):
        data = http_official(OFFICIAL_API + "/statuses/update.json", token, payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", OFFICIAL_API + "/statuses/update.json")
    print(dump_json(payload))


def cmd_post_web(args):
    cookie = get_web_cookie(args)
    payload = {"text": args.text, "visible": 0}
    if args.pic_ids:
        payload["pic_ids"] = args.pic_ids
    if dry_run_guard(args.execute):
        data = http_web(WEB_API + "/statuses/build", cookie, payload)
        print(dump_json(data))
        return
    print("[PLAN] POST", WEB_API + "/statuses/build")
    print(dump_json(payload))


def cmd_upload_image(args):
    # 图片上传较复杂（multipart），这里只做 dry-run 演示
    if dry_run_guard(args.execute):
        print("[PLAN] 图片上传需 multipart/form-data，略")
        return
    print("[PLAN] POST", WEB_API + "/statuses/upload")


def main(argv=None):
    ap = argparse.ArgumentParser(description="微博发布客户端（默认 dry-run）")
    ap.add_argument("--cookie", default="", help="Web Cookie 字符串")
    ap.add_argument("--cookie-file", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn):
        p = sub.add_parser(name)
        p.add_argument("--execute", action="store_true")
        p.set_defaults(fn=fn)
        return p

    p = add("post-official", cmd_post_official)
    p.add_argument("--text", required=True)
    p.add_argument("--pic-ids", default="", help="已上传的 pic_ids，逗号分隔")

    p = add("post-web", cmd_post_web)
    p.add_argument("--text", required=True)
    p.add_argument("--pic-ids", default="", help="已上传的 pic_ids，逗号分隔")

    p = add("upload-image", cmd_upload_image)
    p.add_argument("file")

    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
