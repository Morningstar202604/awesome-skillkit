# Methodology sources and design trade-offs (feishu-dingtalk-bridge)

> When to read: when you want to add a platform (e.g. Slack / WeCom app messages), adjust the signing implementation,
> or question "why the three vendors don't share one payload". This file only covers design rationale.

## Idea sources (distilled from public methodology; not copied text)

| This skill's approach | Idea distilled from |
|---|---|
| One independent builder per vendor, no generic payload then translation | Adapter pattern: when interface differences are too large, wrapping beats normalization; forced unification leaks platform edge cases |
| `build-message` / `parse-webhook` two subcommands | Port-adapter architecture's outbound/inbound separation: send and receive contracts are inherently different |
| dry-run prints payload before sending | `kubectl --dry-run=client` and Terraform `plan`'s "see what will happen first" convention |
| Accept only environment-variable **names**, not secret values | Twelve-factor-app config principle + avoid secrets landing in `ps`-visible command-line args |
| Success judged by business code, not HTTP code | The general convention of Chinese IM open platforms: Feishu/DingTalk/WeCom all use 200 + business error codes, a classic "a layer of status on top of HTTP" |
| Signing implementation exposed only as a reference function | Keep secret computation in the caller (proxy layer); the script stays secret-free and testable |

## Key trade-offs

**Why no unified `Message` abstraction?** The three vendors differ not in "field names" but at the
**semantic level**: Feishu has no markdown type (must go through rich text or message cards), WeCom's
title must be inlined into the body, and @ implementations land in two different places—body tags vs. top-level objects. An abstraction immediately
degrades into pseudo-abstraction of "if platform == ...", making each edge case harder to see. After separating implementations,
platform differences are laid out explicitly in a comparison table—exactly the information the user needs most.

**Why doesn't the script compute the DingTalk signature?** Signing needs the secret in plaintext. If the script accepts a secret arg,
the secret lands in shell history and the process list; if the script reads env vars and computes, it conflicts with the principle of "the script
holds no credentials." The compromise: the algorithm is provided as a `dingtalk_sign()` reference function
(importable and unit-testable by the caller), and `build-message` only prints "timestamp and algorithm notes."
This way the payload is still fully visible, and the secret stays in the proxy layer.

**Why must Feishu's `content` be stringified?** This is the platform's design, not ours—
Feishu requires `content` to be a JSON **string**, not a nested object. Getting this wrong only yields
a generic `19002 parameter error`, costly to debug. So the script uniformly does `json.dumps`,
and marks this difference in the SKILL.md comparison table.

**Why intercept over-long bodies at the script layer?** WeCom's cap is 4096 chars, Feishu's 15000, DingTalk's 20000—
clearly different. Local interception saves a round trip that would fail anyway; more importantly, it forces the sender
to **actively rewrite the content** (into a summary + link) rather than relying on silent platform-side truncation—
a truncated alert message might lose the single most important line.

**Why are error-code explanations hardcoded into the parser?** These three vendors' error-code semantics are opaque (`310000`
looks like "parameter error," but is actually a security-settings issue). Writing targeted explanations for the most common codes directly into
the parse output turns debugging from "search the docs" into "read one hint line"—the highest-frequency payoff.

## Official documentation

- Feishu custom bot (webhook, msg_type, encrypted callback): <https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot>
- Feishu message content and rich-text `post` structure: <https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json>
- Feishu event subscription and `schema 2.0`: <https://open.feishu.cn/document/ukTMukTMukTM/uUTNz4SN1MjL1UzM>
- DingTalk custom bot (signing algorithm, security settings, `errcode`): <https://open.dingtalk.com/document/orgapp/custom-robot-access>
- DingTalk signing implementation notes: <https://open.dingtalk.com/document/orgapp/custom-robot-access#title-jfe-ycv-4jb>
- WeCom group bot (markdown limits, rate limits): <https://developer.work.weixin.qq.com/document/path/91770>
- WeCom callback and AES decryption: <https://developer.work.weixin.qq.com/document/path/90930>
- Python `hmac` / `base64` (basis for signing implementation): <https://docs.python.org/3/library/hmac.html>
