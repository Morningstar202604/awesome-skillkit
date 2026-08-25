#!/usr/bin/env python3
"""publish_common.py - 中文平台发布脚本的公共工具。

集中 HTTP 请求、dry-run 守卫、凭据加载三类重复逻辑，供
wechat-mp-publisher / juejin-publisher / ai-cover-generator 的脚本以
`from publish_common import ...` 方式复用（各脚本顶部注入 _common 路径）。

设计要点：
  - 纯标准库，无第三方依赖。
  - 网络异常统一包装为 PublishError，不吞掉业务错误码
    （业务层 errcode/err_no 由各平台脚本自行判定）。
  - cookie 接受 str 或 dict，dict 自动拼成 `k=v; ` 形式。
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class PublishError(Exception):
    """网络/连接层统一异常（不含平台业务错误码）。"""


def _normalize_cookie(cookie):
    if isinstance(cookie, dict):
        return "; ".join("%s=%s" % (k, v) for k, v in cookie.items())
    return cookie


def http_json(
    url: str,
    *,
    cookie=None,
    payload=None,
    method=None,
    headers=None,
    timeout: int = 30,
    raw: bool = False,
):
    """统一的 GET/POST JSON 端点。

    - payload 非 None 时自动 POST 并序列化；否则 GET（可被 method 覆盖）。
    - cookie 可为 str 或 dict；dict 自动拼成 `k=v; ` 形式。
    - 网络异常统一包装为 PublishError；HTTP 错误原样抛出交由业务层处理。
    - raw=True 时返回原始 bytes，否则按 JSON 解析为 dict（空响应返回 {}）。
    """
    if method is None:
        method = "POST" if payload is not None else "GET"
    req = urllib.request.Request(url, method=method)
    req.add_header("User-Agent", UA)
    cookie = _normalize_cookie(cookie)
    if cookie:
        req.add_header("Cookie", cookie)
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)
    if payload is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
        req.data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw_bytes = resp.read()
    except urllib.error.HTTPError as exc:
        raise PublishError("%s %s -> HTTP %s" % (method, url, exc.code)) from exc
    except urllib.error.URLError as exc:
        raise PublishError("连接失败 %s: %s" % (url, exc.reason)) from exc
    if raw:
        return raw_bytes
    if not raw_bytes:
        return {}
    return json.loads(raw_bytes.decode("utf-8"))


def dry_run_guard(execute: bool, what: str = "请求") -> bool:
    """统一的 dry-run 提示；返回 True 表示允许真实发送。"""
    if execute:
        return True
    print("[DRY-RUN] 未发送任何%s。确认无误后追加 --execute 真正执行。" % what)
    return False


def load_credential(*, env=None, cookie_file=None, name: str = "认证") -> str:
    """从环境变量或文件加载凭据；都没有则报错退出（绝不伪造成功）。"""
    val = ""
    if env:
        val = os.environ.get(env, "")
    if (
        not val
        and isinstance(cookie_file, str)
        and cookie_file
        and os.path.exists(cookie_file)
    ):
        with open(cookie_file, encoding="utf-8-sig") as fh:
            val = fh.read().strip()
    if not val:
        raise SystemExit(
            "缺少%s：设置环境变量 %s 或提供凭据文件" % (name, env or "(见 SKILL.md)")
        )
    return val


def load_json(path: str):
    """BOM-safe 读取 JSON 文件（utf-8-sig）。"""
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def dump_json(data, indent=2) -> str:
    """序列化为 JSON 字符串（ensure_ascii=False，供终端/日志输出）。"""
    return json.dumps(data, ensure_ascii=False, indent=indent)
