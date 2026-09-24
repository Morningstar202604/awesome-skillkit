#!/usr/bin/env python3
"""im_bridge.py -- message payload builder and callback parser for Feishu /
DingTalk / WeCom (Enterprise WeChat).

The three platforms split "send a message" into three completely different
protocols: Feishu uses msg_type + structured content, DingTalk uses msgtype + a
markdown object, and WeCom uses msgtype + a markdown.content string. This script
converges the differences into two subcommands.

Design principles
-----------------
1. **Pure functions**: only builds request bodies and parses callbacks; never
   sends an HTTP request, and is testable without any credentials.
2. **Dry-run by default**: `build-message` only prints the JSON that would be sent;
   sending happens after a human confirms.
3. **Credentials never hit disk**: webhook URL, app_secret, and signing secret are
   always read from environment variables; the script never accepts or echoes them.
4. **Signing only computes, never stores**: in `--sign` mode it only computes and
   prints the sign field; the secret is injected by the caller.

Subcommands
-----------
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
# Protocol constants for the three platforms
# ---------------------------------------------------------------------------

# Feishu custom-bot webhook; group bots only accept this path.
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/{token}"

# DingTalk custom bot. Note: DingTalk **forces** either signing or a keyword/IP
# allowlist; a bare webhook carrying only access_token is rejected by the platform.
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token={token}"

# WeCom group bot.
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"

# Feishu msg_type values. "interactive" is a message card (this module only covers
# the outer structure; the card's internal template structure evolves fast with
# versions, so it is not hardcoded here).
FEISHU_MSG_TYPES = ("text", "post", "interactive", "image", "file")
# DingTalk msgtype: markdown supports title and rich text, best for reports/alerts.
DINGTALK_MSG_TYPES = ("text", "markdown", "link", "actionCard", "feedCard")
# WeCom msgtype: markdown does not support images and is **visible only in the WeCom client**.
WECOM_MSG_TYPES = ("text", "markdown", "image", "news", "file", "template_card")

# Per-platform body length limit for a single message (beyond which it is truncated
# or rejected outright).
TEXT_LIMITS = {"feishu": 15000, "dingtalk": 20000, "wecom": 4096}

# Concatenation order for the signing timestamp and secret: DingTalk uses
# `{timestamp}\n{secret}`; using the secret directly as the HMAC-SHA256 key is wrong.
DINGTALK_SIGN_SEP = "\n"


class BuildError(Exception):
    """Payload construction failed (bad input, not a network problem)."""


def _die(msg: str, code: int = 2) -> int:
    print(f"ERROR: {msg}", file=sys.stderr)
    return code


def _load_json(path: str, what: str) -> object:
    p = Path(path)
    if not p.is_file():
        raise BuildError(f"{what} file does not exist: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BuildError(f"{what} is not valid JSON: {path} (line {e.lineno}: {e.msg})")


def _dump(obj: object) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------
def dingtalk_sign(secret: str, timestamp_ms: int) -> str:
    """DingTalk signing: HMAC-SHA256, key is the secret, message is
    `{timestamp}\\n{secret}`.

    Returns a base64 string (URL-encode it to get the final query-parameter value).
    Time window: if the timestamp differs from server time by more than 1 hour, it
    is rejected.

    Note: this is a reference implementation for the **caller** (the proxy layer
    that holds the secret); the `build-message` subcommand does not call it -- the
    script does not hold the secret.
    """
    string_to_sign = f"{timestamp_ms}{DINGTALK_SIGN_SEP}{secret}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), string_to_sign, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def _signed_url(base_url: str, secret_env: str, sign_flag: bool) -> tuple[str, dict]:
    """Append signing parameters to a DingTalk URL; return (url, extra context).

    Accepts only the environment-variable **name**, not the secret itself -- this way
    the secret never appears in command-line arguments (visible in the process list)
    or in script parameters.
    """
    if not sign_flag:
        return base_url, {"sign": "not enabled (pair it with a keyword or IP allowlist)"}
    if not secret_env:
        raise BuildError("--sign requires --sign-secret-env (the name of the env var holding the secret)")
    ts = int(time.time() * 1000)
    sep = "&" if "?" in base_url else "?"
    url = f"{base_url}{sep}timestamp={ts}&sign=<urlencode(HMAC-SHA256)>"
    return url, {
        "sign": "enabled",
        "timestamp": ts,
        "sign": f"<not computed here: the script does not read ${secret_env}; the proxy layer generates it at send time>",
        "algorithm": f"base64(hmac_sha256(key=${secret_env}, msg=f'{{timestamp}}\\n{{secret}}')), then urlencode",
    }


# ---------------------------------------------------------------------------
# Per-platform payload builders
# ---------------------------------------------------------------------------
def build_feishu(text: str, fmt: str, title: str, at_mobiles: list) -> dict:
    """Feishu group-bot payload.

    Feishu uses `msg_type` to distinguish message kinds, with content in `content`
    -- and content is a **stringified JSON** (not a nested object). This is the most
    error-prone spot: writing a nested object yields a 19002 parameter error.
    """
    if fmt == "markdown":
        # Feishu has no standalone markdown type: rich text goes via post (rich-text
        # message), or via the markdown element of an interactive (message card).
        # Here we build a post, with the title as the first line and the body organized
        # under the zh_cn language pack.
        payload = {
            "msg_type": "post",
            "content": json.dumps({
                "post": {
                    "zh_cn": {
                        "title": title or "Notification",
                        "content": [[{"tag": "text", "text": text}]],
                    }
                }
            }, ensure_ascii=False),
        }
    else:
        payload = {"msg_type": "text", "content": json.dumps(
            {"text": text}, ensure_ascii=False)}

    if at_mobiles:
        # Feishu's @ in text type uses the <at user_id="..."> tag, inside content,
        # not a top-level field -- unlike DingTalk/WeCom's standalone at object.
        payload["msg_type"] = "text"
        payload["content"] = json.dumps({
            "text": text + "".join(f' <at user_id="{m}"></at>' for m in at_mobiles)
        }, ensure_ascii=False)
    return payload


def build_dingtalk(text: str, fmt: str, title: str, at_mobiles: list) -> dict:
    """DingTalk group-bot payload.

    DingTalk puts the message type in `msgtype` (all lowercase, no underscore); the
    markdown type uses `markdown.title` + `markdown.text`; @ goes via the **top-level**
    `at` object.
    """
    if fmt == "markdown":
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title or "Notification", "text": text},
        }
    else:
        payload = {"msgtype": "text", "text": {"content": text}}

    if at_mobiles:
        payload["at"] = {"atMobiles": at_mobiles, "isAtAll": False}
    return payload


def build_wecom(text: str, fmt: str, title: str, at_mobiles: list) -> dict:
    """WeCom group-bot payload.

    WeCom's markdown merges title and body into a single `content` string (no
    separate title field), so the title is inlined using Markdown's H1 syntax.
    Another hard limit: markdown messages **can only be viewed inside the WeCom
    client**; receiving them in WeChat shows plain text -- the most common pitfall
    when choosing a message type.
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
        # WeCom uses <@userid> placeholders in the body; the @'d person must also be
        # in the group for it to take effect.
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
    "dingtalk": "DINGTALK_ACCESS_TOKEN (for signing, also set DINGTALK_SIGN_SECRET)",
    "wecom": "WECOM_WEBHOOK_KEY",
}


def cmd_build_message(args) -> int:
    platform = args.platform
    if len(args.text) > TEXT_LIMITS[platform]:
        return _die(
            f"body {len(args.text)} chars exceeds {platform} limit {TEXT_LIMITS[platform]}; "
            "split into multiple messages, or put it in a doc first and send a link"
        )

    at_mobiles = [m.strip() for m in (args.at_mobiles or "").split(",") if m.strip()]
    payload = BUILDERS[platform](args.text, args.format, args.title, at_mobiles)

    url_template = WEBHOOKS[platform]
    extra: dict = {}
    if platform == "dingtalk":
        url_template, extra = _signed_url(
            url_template, args.sign_secret_env, args.sign)

    print(f"# DRY-RUN: {platform} message payload (no request sent)")
    print(f"# POST {url_template}")
    print(f"#   credentials: read from env var {ENV_HINT[platform]}; not written to disk, not printed")
    print(f"#   Content-Type: application/json")
    print(f"#   body length: {len(args.text)} / limit {TEXT_LIMITS[platform]}")
    for k, v in extra.items():
        print(f"#   {k}: {v}")
    print()
    _dump(payload)
    print()
    print("# No request sent. At run time the AI/user injects credentials and sends, e.g.:")
    print(f"#   curl -sS -X POST \"{url_template.replace('{token}', '$TOKEN').replace('{key}', '$KEY')}\" \\")
    print("#     -H 'Content-Type: application/json' --data @payload.json")
    return 0


# ---------------------------------------------------------------------------
# Callback / response parsing
# ---------------------------------------------------------------------------
def parse_feishu(raw: dict) -> list:
    """The two Feishu bot message bodies.

    1) Response: `{"code": 0, "msg": "success", "data": {...}}` -- **code 0 means
       success**; when code is non-zero the HTTP status may still be 200, so looking
       only at the HTTP code misjudges success.
    2) Event callback: `{"schema": "2.0", "header": {...}, "event": {...}}`, and when
       encryption is enabled the whole thing is `{"encrypt": "..."}`, which must be
       decrypted before reading.
    """
    lines = []
    if "encrypt" in raw:
        return ["- callback is encrypted (`encrypt` field): decrypt with the Encrypt Key before parsing",
                "- any field read before decryption is untrusted"]
    if "code" in raw:
        code = raw.get("code")
        lines.append(f"- result: code={code} msg={raw.get('msg', '')}"
                     f"  {'OK success' if code == 0 else 'FAILED'}")
        if code != 0:
            lines.append("- note: on Feishu failure the HTTP status may still be 200; do not rely on the HTTP code alone")
    header = raw.get("header") or {}
    if header:
        lines.append(f"- event type: {header.get('event_type', '(missing)')}")
        lines.append(f"- event id: {header.get('event_id', '(missing)')}"
                     "  <- use it for idempotent dedup; Feishu re-pushes")
        lines.append(f"- timestamp: {header.get('create_time', '(missing)')}")
        lines.append(f"- app id: {header.get('app_id', '(missing)')}")
    event = raw.get("event") or {}
    if event:
        msg = event.get("message") or {}
        if msg:
            lines.append(f"- message type: {msg.get('message_type', '(missing)')}")
            lines.append(f"- chat id: {msg.get('chat_id', '(missing)')}")
            content = msg.get("content")
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    pass
            lines.append(f"- content: {json.dumps(content, ensure_ascii=False)}")
        sender = (event.get("sender") or {}).get("sender_id") or {}
        if sender:
            lines.append(f"- sender open_id: {sender.get('open_id', '(missing)')}")
    return lines or ["- unrecognized Feishu message body (neither response nor event callback)"]


def parse_dingtalk(raw: dict) -> list:
    """DingTalk's response body is **flat**: `{"errcode": 0, "errmsg": "ok"}`.

    Unlike Feishu, DingTalk puts errcode at the top level with no data wrapper.
    Callback messages look like
    `{"msgtype": "text", "text": {"content": "..."}, "senderNick": ...}`.
    """
    lines = []
    if "errcode" in raw:
        code = raw.get("errcode")
        lines.append(f"- result: errcode={code} errmsg={raw.get('errmsg', '')}"
                     f"  {'OK success' if code == 0 else 'FAILED'}")
        if code == 310000:
            lines.append("- 310000 = bot security-settings check failed: no signing and no keyword/IP allowlist hit")
        elif code == 300001:
            lines.append("- 300001 = invalid token; check whether access_token was reset")
    if "msgtype" in raw or "senderNick" in raw:
        lines.append(f"- callback message type: {raw.get('msgtype', '(missing)')}")
        lines.append(f"- sender nickname: {raw.get('senderNick', '(missing)')}")
        if raw.get("senderStaffId"):
            lines.append(f"- sender staffId: {raw['senderStaffId']}")
        body = raw.get("text") or {}
        if body.get("content"):
            lines.append(f"- content: {body['content'].strip()}")
        if raw.get("conversationId"):
            lines.append(f"- chat id: {raw['conversationId']}")
    return lines or ["- unrecognized DingTalk message body"]


def parse_wecom(raw: dict) -> list:
    """The WeCom group-bot response is likewise flat: `{"errcode": 0, "errmsg": "ok"}`.

    Callbacks (receiving messages) use a separate system: you configure a callback
    URL and do AES decryption + URL verification, and the body is XML not JSON -- this
    script only handles the JSON side.
    """
    lines = []
    if "errcode" in raw:
        code = raw.get("errcode")
        lines.append(f"- result: errcode={code} errmsg={raw.get('errmsg', '')}"
                     f"  {'OK success' if code == 0 else 'FAILED'}")
        if code == 93000:
            lines.append("- 93000 = invalid bot webhook key, or the bot was removed")
        elif code == 45009:
            lines.append("- 45009 = rate-limit hit: at most 20 messages per bot per minute")
    if "msgtype" in raw or "from" in raw:
        lines.append(f"- callback message type: {raw.get('msgtype', '(missing)')}")
        lines.append(f"- content: {(raw.get('text') or {}).get('content', '(missing)')}")
    return lines or ["- unrecognized WeCom message body"]


PARSERS = {"feishu": parse_feishu, "dingtalk": parse_dingtalk, "wecom": parse_wecom}


def cmd_parse_webhook(args) -> int:
    raw = _load_json(args.json, "--json")
    if not isinstance(raw, dict):
        return _die("--json must be an object (callback or response body)")
    print(f"# parse result: {args.platform}")
    for line in PARSERS[args.platform](raw):
        print(line)
    return 0


# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="im_bridge.py",
        description="Feishu/DingTalk/WeCom message-payload building and callback parsing (offline, no requests)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build-message", help="build a message payload per platform protocol and print it")
    s.add_argument("--platform", choices=["feishu", "dingtalk", "wecom"], required=True)
    s.add_argument("--text", required=True)
    s.add_argument("--format", choices=["text", "markdown"], default="markdown")
    s.add_argument("--title", default="", help="markdown message title (used by Feishu/DingTalk)")
    s.add_argument("--at-mobiles", default="", help="comma-separated phone numbers to @")
    s.add_argument("--sign", action="store_true", help="DingTalk signing mode")
    s.add_argument("--sign-secret-env", default="DINGTALK_SIGN_SECRET",
                   help="name of the env var holding the signing secret (default DINGTALK_SIGN_SECRET)")
    s.set_defaults(func=cmd_build_message)

    s = sub.add_parser("parse-webhook", help="parse a callback/response body")
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
