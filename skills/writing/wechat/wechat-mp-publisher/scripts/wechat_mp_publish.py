#!/usr/bin/env python3
"""wechat_mp_publish.py - 微信公众号草稿箱 / 发布 API 客户端。

官方接口文档: https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/
              https://developers.weixin.qq.com/doc/offiaccount/Publish/Publish.html

安全设计：
  - 所有会改动线上状态的操作（add-draft / publish / 上传）默认 --dry-run，
    只打印将发送的 method/URL/payload，不联网；加 --execute 才真正发送。
  - 凭据（appid/secret）从环境变量或 --appid/--secret 读取，绝不写入本仓库。

子命令：
  token                 获取 access_token
  upload-img   FILE     上传正文图片（uploadimg，返回图文内可用的 url）
  add-thumb    FILE     上传永久素材作封面（add_material，返回 media_id）
  add-draft             创建草稿（draft/add），返回 media_id
  publish      MEDIA_ID 提交发布（freepublish/submit）

退出码：0 成功；1 API 错误或参数错误。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

# 复用发布公共工具（HTTP / dry-run 守卫），避免重复造轮子
_common = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "_common"
    )
)
if os.path.isdir(_common) and _common not in sys.path:
    sys.path.insert(0, _common)
from publish_common import http_json as _http_json, dry_run_guard, dump_json

API_BASE = "https://api.weixin.qq.com"


class WechatAPIError(Exception):
    def __init__(self, errcode, errmsg):
        super().__init__("wechat errcode=%s errmsg=%s" % (errcode, errmsg))
        self.errcode = errcode
        self.errmsg = errmsg


# ---------- 纯函数（可单测） ----------


def build_token_url(appid: str, secret: str) -> str:
    return "%s/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (
        API_BASE,
        appid,
        secret,
    )


def build_draft_payload(
    title,
    content_html,
    thumb_media_id,
    author="",
    digest="",
    need_open_comment=1,
    only_fans_can_comment=0,
) -> dict:
    return {
        "articles": [
            {
                "title": title,
                "author": author,
                "digest": digest,
                "content": content_html,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": need_open_comment,
                "only_fans_can_comment": only_fans_can_comment,
            }
        ]
    }


def multipart_body(
    file_field: str, filename: str, content: bytes, ctype: str
) -> tuple[bytes, str]:
    """构造 multipart/form-data 请求体。返回 (body, content_type)。"""
    boundary = "----skillkit" + uuid.uuid4().hex
    parts = [
        (
            '--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
            "Content-Type: %s\r\n\r\n" % (boundary, file_field, filename, ctype)
        ).encode("utf-8"),
        content,
        ("\r\n--%s--\r\n" % boundary).encode("utf-8"),
    ]
    body = b"".join(parts)
    return body, "multipart/form-data; boundary=%s" % boundary


def parse_wechat_response(raw) -> dict:
    """解析微信响应；业务失败（含 errcode 非 0）抛 WechatAPIError。

    接受原始 bytes 或已解析 dict（来自公共 http_json）。
    """
    data = raw if isinstance(raw, dict) else json.loads(raw.decode("utf-8"))
    errcode = data.get("errcode", 0)
    if errcode not in (0, None):
        raise WechatAPIError(errcode, data.get("errmsg", ""))
    return data


def require_creds(args) -> tuple[str, str]:
    appid = args.appid or os.environ.get("WECHAT_MP_APPID", "")
    secret = args.secret or os.environ.get("WECHAT_MP_SECRET", "")
    if not appid or not secret:
        raise SystemExit(
            "缺少凭据：用 --appid/--secret 或环境变量 "
            "WECHAT_MP_APPID / WECHAT_MP_SECRET"
        )
    return appid, secret


# ---------- 网络执行 ----------


def http_json(url: str, payload: dict | None = None) -> dict:
    """微信 JSON 接口封装：经公共 http_json 发送并做业务错误检查。"""
    return parse_wechat_response(_http_json(url, payload=payload))


def http_upload(url: str, filename: str, content: bytes, ctype: str) -> dict:
    body, content_type = multipart_body("media", filename, content, ctype)
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return parse_wechat_response(resp.read())
    except urllib.error.HTTPError as exc:
        raise WechatAPIError(exc.code, exc.read().decode("utf-8", "replace")[:200])


# ---------- 子命令 ----------


def cmd_token(args):
    appid, secret = require_creds(args)
    url = build_token_url(appid, secret)
    if dry_run_guard(args.execute):
        data = http_json(url)
        print(dump_json(data))
        return
    print("[PLAN] GET", url.replace(secret, "***"))


def cmd_upload_img(args):
    appid, secret = require_creds(args)
    url = "%s/cgi-bin/media/uploadimg?access_token=TOKEN" % API_BASE
    content = open(args.file, "rb").read()
    if dry_run_guard(args.execute):
        token = http_json(build_token_url(appid, secret))["access_token"]
        data = http_upload(
            url.replace("TOKEN", token), args.file, content, "image/jpeg"
        )
        print(dump_json(data))
        return
    print(
        "[PLAN] POST %s (multipart, file=%s, %d bytes)" % (url, args.file, len(content))
    )


def cmd_add_thumb(args):
    appid, secret = require_creds(args)
    url = "%s/cgi-bin/material/add_material?type=image&access_token=TOKEN" % API_BASE
    content = open(args.file, "rb").read()
    if dry_run_guard(args.execute):
        token = http_json(build_token_url(appid, secret))["access_token"]
        data = http_upload(
            url.replace("TOKEN", token), args.file, content, "image/jpeg"
        )
        print(dump_json(data))
        return
    print(
        "[PLAN] POST %s (multipart, file=%s, %d bytes)" % (url, args.file, len(content))
    )


def cmd_add_draft(args):
    appid, secret = require_creds(args)
    payload = build_draft_payload(
        args.title, args.content_html, args.thumb_media_id, args.author, args.digest
    )
    if dry_run_guard(args.execute):
        token = http_json(build_token_url(appid, secret))["access_token"]
        data = http_json(
            "%s/cgi-bin/draft/add?access_token=%s" % (API_BASE, token), payload
        )
        print(dump_json(data))
        return
    print("[PLAN] POST %s/cgi-bin/draft/add" % API_BASE)
    print(json.dumps(payload, ensure_ascii=False, indent=2)[:800])


def cmd_publish(args):
    appid, secret = require_creds(args)
    payload = {"media_id": args.media_id}
    if dry_run_guard(args.execute):
        token = http_json(build_token_url(appid, secret))["access_token"]
        data = http_json(
            "%s/cgi-bin/freepublish/submit?access_token=%s" % (API_BASE, token), payload
        )
        print(dump_json(data))
        return
    print("[PLAN] POST %s/cgi-bin/freepublish/submit" % API_BASE)
    print(json.dumps(payload, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="微信公众号草稿箱/发布客户端（默认 dry-run）"
    )
    ap.add_argument("--appid", default="")
    ap.add_argument("--secret", default="")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, **kw):
        p = sub.add_parser(name, **kw)
        p.add_argument(
            "--execute", action="store_true", help="真正发送请求（默认只打印计划）"
        )
        p.set_defaults(fn=fn)
        return p

    add("token", cmd_token)
    p = add("upload-img", cmd_upload_img)
    p.add_argument("file")
    p = add("add-thumb", cmd_add_thumb)
    p.add_argument("file")
    p = add("add-draft", cmd_add_draft)
    p.add_argument("--title", required=True)
    p.add_argument("--content-html", required=True, help="正文 HTML 文件路径")
    p.add_argument("--thumb-media-id", required=True)
    p.add_argument("--author", default="")
    p.add_argument("--digest", default="")
    p = add("publish", cmd_publish)
    p.add_argument("media_id")

    args = ap.parse_args(argv)
    if getattr(args, "content_html", None):
        with open(args.content_html, encoding="utf-8-sig") as fh:
            args.content_html = fh.read()
    args.fn(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
