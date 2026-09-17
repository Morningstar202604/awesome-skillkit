#!/usr/bin/env python3
"""im_bridge.py -- 飞书 / 钉钉 / 企业微信 消息负载构造器与回调解析器。

三家平台把"发一条消息"这件事拆成了三套完全不同的协议：
飞书用 msg_type + 结构化 content、钉钉用 msgtype + markdown 对象、
企业微信用 msgtype + markdown.content 字符串。本脚本把差异收敛成两个子命令。

设计原则
--------
1. **纯函数**：只构造请求体、解析回调，绝不发 HTTP 请求，无需任何凭证即可测试。
2. **默认 dry-run**：`build-message` 只打印将发送的 JSON，发送由人确认后执行。
3. **凭证不落盘**：webhook URL、app_secret、加签 secret 一律从环境变量读取；
   脚本内部从不接受、也不回显这些值。
4. **加签只算不存**：`--sign` 模式下只计算并打印 sign 字段，secret 由调用方注入。

子命令
------
  build-message --platform {feishu|dingtalk|wecom} --text X [--format markdown|text]
                [--title T] [--at-mobiles 13x,13y] [--sign]
  parse-webhook --platform {feishu|dingtalk|wecom} --json f.json

Stdlib only. Python >= 3.8.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import sys
import time
import urllib.parse
from pathlib import Path

# ---------------------------------------------------------------------------
# 三家平台的协议常量
# ---------------------------------------------------------------------------

# 飞书自定义机器人的 webhook；群机器人只认这一条路径。
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/{token}"

# 钉钉自定义机器人。注意：钉钉**强制**要求加签或关键词/ IP 白名单之一，
# 只带 access_token 的裸 webhook 已被平台拒绝。
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token={token}"

# 企业微信（WeCom）群机器人。
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"

# 飞书支持的 msg_type。interactive 是消息卡片（本文档只覆盖外层的结构，
# 卡片内部的 template 结构随版本演进较快，故不在此硬编码）。
FEISHU_MSG_TYPES = ("text", "post", "interactive", "image", "file")
# 钉钉的 msgtype：markdown 支持标题与富文本，最适合日报/告警。
DINGTALK_MSG_TYPES = ("text", "markdown", "link", "actionCard", "feedCard")
# 企业微信的 msgtype：markdown 不支持图片，且**仅企业微信客户端可见**。
WECOM_MSG_TYPES = ("text", "markdown", "image", "news", "file", "template_card")

# 各平台单条消息的正文长度上限（超出会被截断或直接报错）。
TEXT_LIMITS = {"feishu": 15000, "dingtalk": 20000, "wecom": 4096}

# 加签时间戳与密钥的拼接顺序：钉钉是 `{timestamp}\n{secret}`，
# 直接用 secret 做 key 做 HMAC-SHA256 是错的。
DINGTALK_SIGN_SEP = "\n"


class BuildError(Exception):
    """负载构造失败（输入不合法，非网络问题）。"""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    p = Path(path)
    if not p.is_file():
        raise BuildError(f"{what} 文件不存在: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"{what} 不是合法 JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# 加签
# ---------------------------------------------------------------------------
def dingtalk_sign(secret: str, timestamp_ms: int) -> str:
    """钉钉加签：HMAC-SHA256，密钥是 secret，消息是 `{timestamp}\\n{secret}`。

    返回 base64 字符串（再做 URL 编码才是最终的 query 参数值）。
    时限：时间戳与服务器时间相差超过 1 小时会被拒。

    注意：本函数是给**调用方**（拿到 secret 的代理层）用的参考实现，
    `build-message` 子命令不会调用它——脚本不持有密钥。
    """
    string_to_sign = f"{timestamp_ms}{DINGTALK_SIGN_SEP}{secret}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), string_to_sign, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _signed_url(base_url: str, secret_env: str, sign_flag: bool) -> tuple[str, dict]:
    """给钉钉 URL 补加签参数；返回 (url, 附加上下文)。

    只接受环境变量**名**，不接受密钥本身——这样密钥永远不会出现在命令行参数
    （进程列表可见）或脚本参数里。
    """
    if not sign_flag:
        return base_url, {"加签": "未启用（需配合关键词或 IP 白名单之一）"}
    if not secret_env:
        raise BuildError("--sign 需要同时提供 --sign-secret-env（存放密钥的环境变量名）")
    ts = int(time.time() * 1000)
    sep = "&" if "?" in base_url else "?"
    url = f"{base_url}{sep}timestamp={ts}&sign=<urlencode(HMAC-SHA256)>"
    return url, {
        "加签": "已启用",
        "timestamp": ts,
        "sign": f"<不在此计算：脚本不读取 ${secret_env} 的值，发送时由代理层生成>",
        "算法": f"base64(hmac_sha256(key=${secret_env}, msg=f'{{timestamp}}\\n{{secret}}'))，再做 urlencode",
    }


# ---------------------------------------------------------------------------
# 各平台负载构造
# ---------------------------------------------------------------------------
def build_feishu(text: str, fmt: str, title: str, at_mobiles: list) -> dict:
    """飞书群机器人负载。

    飞书用 `msg_type` 区分消息种类，内容在 `content` 里——而 content 是
    **字符串化的 JSON**（不是嵌套对象），这是最容易写错的一处：
    写成嵌套对象会得到 19002 参数错误。
    """
    if fmt == "markdown":
        # 飞书没有独立的 markdown 类型：富文本走 post（富文本消息），
        # 或者用 interactive（消息卡片）的 markdown 元素。
        # 这里构造 post，标题作为首行，正文按 zh_cn 语言包组织。
        payload = {
            "msg_type": "post",
            "content": json.dumps({
                "post": {
                    "zh_cn": {
                        "title": title or "通知",
                        "content": [[{"tag": "text", "text": text}]],
                    }
                }
            }, ensure_ascii=False),
        }
    else:
        payload = {"msg_type": "text", "content": json.dumps(
            {"text": text}, ensure_ascii=False)}

    if at_mobiles:
        # 飞书的 @ 在 text 类型里用 <at user_id="..."> 标签，且在 content 内部，
        # 不在顶层字段——与钉钉/企微的独立 at 对象不同。
        payload["msg_type"] = "text"
        payload["content"] = json.dumps({
            "text": text + "".join(f' <at user_id="{m}"></at>' for m in at_mobiles)
        }, ensure_ascii=False)
    return payload


def build_dingtalk(text: str, fmt: str, title: str, at_mobiles: list) -> dict:
    """钉钉群机器人负载。

    钉钉把消息类型放在 `msgtype`（全小写，无下划线），markdown 类型用
    `markdown.title` + `markdown.text` 两个字段；@ 走**顶层**的 `at` 对象。
    """
    if fmt == "markdown":
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title or "通知", "text": text},
        }
    else:
        payload = {"msgtype": "text", "text": {"content": text}}

    if at_mobiles:
        payload["at"] = {"atMobiles": at_mobiles, "isAtAll": False}
    return payload


def build_wecom(text: str, fmt: str, title: str, at_mobiles: list) -> dict:
    """企业微信群机器人负载。

    企微的 markdown 把标题与正文合并成一个 `content` 字符串（没有独立 title
    字段），因此标题用 Markdown 的一级标题语法内联进去。
    另一个硬限制：markdown 消息**只能在企业微信客户端内查看**，
    用微信接收会显示为纯文本，这是选择消息类型时最常踩的坑。
    """
    if fmt == "markdown":
        parts = []
        if title:
            parts.append(f"# {title}")
        parts.append(text)
        payload = {"msgtype": "markdown", "markdown": {"content": "\n".join(parts)}}
    else:
        payload = {"msgtype": "text", "text": {"content": text}}

    if at_mobiles:
        # 企微在正文里用 <@userid> 占位；同样需要先把被 @ 的人拉进群才能生效
        payload["text" if fmt == "text" else "markdown"] = {
            ("content" if fmt == "text" else "content"):
                (payload.get("text", {}).get("content", text)
                 + "".join(f" <@{m}>" for m in at_mobiles))
        }
        if fmt == "markdown":
            parts = []
            if title:
                parts.append(f"# {title}")
            parts.append(text + "".join(f" <@{m}>" for m in at_mobiles))
            payload["markdown"] = {"content": "\n".join(parts)}
    return payload


BUILDERS = {"feishu": build_feishu, "dingtalk": build_dingtalk, "wecom": build_wecom}

WEBHOOKS = {
    "feishu": FEISHU_WEBHOOK,
    "dingtalk": DINGTALK_WEBHOOK,
    "wecom": WECOM_WEBHOOK,
}

ENV_HINT = {
    "feishu": "FEISHU_WEBHOOK_TOKEN",
    "dingtalk": "DINGTALK_ACCESS_TOKEN（加签再配 DINGTALK_SIGN_SECRET）",
    "wecom": "WECOM_WEBHOOK_KEY",
}


def cmd_build_message(args) -> int:
    platform = args.platform
    if len(args.text) > TEXT_LIMITS[platform]:
        return _die(
            f"正文 {len(args.text)} 字符，超过 {platform} 上限 {TEXT_LIMITS[platform]}；"
            "请拆成多条发送或先落文档再发链接"
        )

    at_mobiles = [m.strip() for m in (args.at_mobiles or "").split(",") if m.strip()]
    payload = BUILDERS[platform](args.text, args.format, args.title, at_mobiles)

    url_template = WEBHOOKS[platform]
    extra: dict = {}
    if platform == "dingtalk":
        url_template, extra = _signed_url(
            url_template, args.sign_secret_env, args.sign)

    print(f"# DRY-RUN：{platform} 消息负载（未发送任何请求）")
    print(f"# POST {url_template}")
    print(f"#   凭证：从环境变量 {ENV_HINT[platform]} 读取，不落盘、不打印")
    print(f"#   Content-Type: application/json")
    print(f"#   正文长度：{len(args.text)} / 上限 {TEXT_LIMITS[platform]}")
    for k, v in extra.items():
        print(f"#   {k}：{v}")
    print()
    _dump(payload)
    print()
    print("# 未发送任何请求。真实执行时由 AI/用户注入凭证后发送，例如：")
    print(f"#   curl -sS -X POST \"{url_template.replace('{token}', '$TOKEN').replace('{key}', '$KEY')}\" \\")
    print("#     -H 'Content-Type: application/json' --data @payload.json")
    return 0


# ---------------------------------------------------------------------------
# 回调 / 响应解析
# ---------------------------------------------------------------------------
def parse_feishu(raw: dict) -> list:
    """飞书机器人的两种消息体。

    1) 响应：`{"code": 0, "msg": "success", "data": {...}}` —— **code 为 0 才算成功**，
       非 0 时 HTTP 状态码可能仍是 200，只看 HTTP 码会误判成功。
    2) 事件回调：`{"schema": "2.0", "header": {...}, "event": {...}}`，
       且启用加密时整体是 `{"encrypt": "..."}`，需要先解密才能读。
    """
    lines = []
    if "encrypt" in raw:
        return ["- 回调已加密（`encrypt` 字段）：需用 Encrypt Key 解密后再解析",
                "- 解密前的任何字段读取都不可信"]
    if "code" in raw:
        code = raw.get("code")
        lines.append(f"- 响应结果：code={code} msg={raw.get('msg', '')}"
                     f"  {'✅ 成功' if code == 0 else '❌ 失败'}")
        if code != 0:
            lines.append("- 注意：飞书失败时 HTTP 状态码仍可能是 200，不能只看 HTTP 码")
    header = raw.get("header") or {}
    if header:
        lines.append(f"- 事件类型：{header.get('event_type', '(缺失)')}")
        lines.append(f"- 事件 ID：{header.get('event_id', '(缺失)')}"
                     "  ← 用它做幂等去重，飞书会重推")
        lines.append(f"- 时间戳：{header.get('create_time', '(缺失)')}")
        lines.append(f"- 应用 ID：{header.get('app_id', '(缺失)')}")
    event = raw.get("event") or {}
    if event:
        msg = event.get("message") or {}
        if msg:
            lines.append(f"- 消息类型：{msg.get('message_type', '(缺失)')}")
            lines.append(f"- 会话 ID：{msg.get('chat_id', '(缺失)')}")
            content = msg.get("content")
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass
            lines.append(f"- 内容：{json.dumps(content, ensure_ascii=False)}")
        sender = (event.get("sender") or {}).get("sender_id") or {}
        if sender:
            lines.append(f"- 发送者 open_id：{sender.get('open_id', '(缺失)')}")
    return lines or ["- 未识别的飞书消息体（既非响应也非事件回调）"]


def parse_dingtalk(raw: dict) -> list:
    """钉钉的响应体是**扁平**的 `{"errcode": 0, "errmsg": "ok"}`。

    与飞书不同，钉钉把 errcode 放最外层，没有 data 包装。
    回调消息则形如 `{"msgtype": "text", "text": {"content": "..."}, "senderNick": ...}`。
    """
    lines = []
    if "errcode" in raw:
        code = raw.get("errcode")
        lines.append(f"- 响应结果：errcode={code} errmsg={raw.get('errmsg', '')}"
                     f"  {'✅ 成功' if code == 0 else '❌ 失败'}")
        if code == 310000:
            lines.append("- 310000 = 机器人安全设置校验失败：未加签且未命中关键词/IP 白名单")
        elif code == 300001:
            lines.append("- 300001 = token 无效，检查 access_token 是否被重置")
    if "msgtype" in raw or "senderNick" in raw:
        lines.append(f"- 回调消息类型：{raw.get('msgtype', '(缺失)')}")
        lines.append(f"- 发送者昵称：{raw.get('senderNick', '(缺失)')}")
        if raw.get("senderStaffId"):
            lines.append(f"- 发送者 staffId：{raw['senderStaffId']}")
        body = raw.get("text") or {}
        if body.get("content"):
            lines.append(f"- 内容：{body['content'].strip()}")
        if raw.get("conversationId"):
            lines.append(f"- 会话 ID：{raw['conversationId']}")
    return lines or ["- 未识别的钉钉消息体"]


def parse_wecom(raw: dict) -> list:
    """企微群机器人的响应同样是扁平结构：`{"errcode": 0, "errmsg": "ok"}`。

    回调（接收消息）走的是另一个体系：需要配置回调 URL 并做 AES 解密 +
    URL 验证，消息体是 XML 而非 JSON——本脚本只处理 JSON 侧。
    """
    lines = []
    if "errcode" in raw:
        code = raw.get("errcode")
        lines.append(f"- 响应结果：errcode={code} errmsg={raw.get('errmsg', '')}"
                     f"  {'✅ 成功' if code == 0 else '❌ 失败'}")
        if code == 93000:
            lines.append("- 93000 = 机器人 webhook key 无效或机器人已被移除")
        elif code == 45009:
            lines.append("- 45009 = 触发频率限制：每个机器人每分钟最多 20 条")
    if "msgtype" in raw or "from" in raw:
        lines.append(f"- 回调消息类型：{raw.get('msgtype', '(缺失)')}")
        lines.append(f"- 内容：{(raw.get('text') or {}).get('content', '(缺失)')}")
    return lines or ["- 未识别的企微消息体"]


PARSERS = {"feishu": parse_feishu, "dingtalk": parse_dingtalk, "wecom": parse_wecom}


def cmd_parse_webhook(args) -> int:
    raw = _load_json(args.json, "--json")
    if not isinstance(raw, dict):
        return _die("--json 必须是对象（回调或响应体）")
    print(f"# 解析结果：{args.platform}")
    for line in PARSERS[args.platform](raw):
        print(line)
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="im_bridge.py",
        description="飞书/钉钉/企业微信消息负载构造与回调解析（离线，不发请求）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build-message", help="按平台协议构造消息负载并打印")
    s.add_argument("--platform", choices=["feishu", "dingtalk", "wecom"], required=True)
    s.add_argument("--text", required=True)
    s.add_argument("--format", choices=["text", "markdown"], default="markdown")
    s.add_argument("--title", default="", help="markdown 消息标题（飞书/钉钉使用）")
    s.add_argument("--at-mobiles", default="", help="逗号分隔的手机号，触发 @")
    s.add_argument("--sign", action="store_true", help="钉钉加签模式")
    s.add_argument("--sign-secret-env", default="DINGTALK_SIGN_SECRET",
                   help="存放加签密钥的环境变量名（默认 DINGTALK_SIGN_SECRET）")
    s.set_defaults(func=cmd_build_message)

    s = sub.add_parser("parse-webhook", help="解析回调/响应体")
    s.add_argument("--platform", choices=["feishu", "dingtalk", "wecom"], required=True)
    s.add_argument("--json", required=True)
    s.set_defaults(func=cmd_parse_webhook)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BuildError as e:
        return _die(str(e))


if __name__ == "__main__":
    sys.exit(main())
