---
name: feishu-dingtalk-bridge
description: "Compose and parse chat messages across Feishu (Lark), DingTalk, and WeCom group robots, normalizing three different auth and payload protocols behind one workflow. Use when the user asks to send a Feishu bot message / send a DingTalk notification / send a WeCom message / push a notification to a group / push a bot alert / push a daily report to a group / send to Feishu bot / DingTalk webhook / WeCom group robot / push alert to chat group. Do NOT use for Notion pages (use notion-workspace), issue trackers (use issue-tracker-sync), or file archiving (use cloud-drive-manager)."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only for the helper script. Live execution needs outbound HTTPS to open.feishu.cn / oapi.dingtalk.com / qyapi.weixin.qq.com and the webhook token, access_token or sign secret in environment variables."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Feishu / DingTalk / WeCom Bridge

One notification needs to go to three groups at once, yet the three protocols have not a single thing in common: Feishu stuffs content into a
**stringified JSON**, DingTalk uses a standalone `markdown` object, and WeCom kneads title and body into
a single `content` string. This skill collapses that difference into three steps: pick the platform → build the payload → send.

**Core judgment: do not try to write one generic payload and translate it — the three's field semantics differ,**
**each must be built separately.** The only thing shared is the rhythm of "dry-run review the payload first, then send."

**Red lines (enforced by this skill)**

1. **Never hardcode credentials**: webhook token, access_token, and sign secret are read only from environment variables
   (`FEISHU_WEBHOOK_TOKEN` / `DINGTALK_ACCESS_TOKEN` / `DINGTALK_SIGN_SECRET` /
   `WECOM_WEBHOOK_KEY`). The script **never reads or prints** these values; even signing is computed by the proxy layer
   at send time.
2. **Dry-run by default**: `build-message` only prints "the JSON that would be sent" and **sends no request**.
   An authorization like `--yes` is only sent after the user explicitly gives it in the session.
3. **Least privilege**: a group robot only needs the webhook token; **do not** request enterprise-application-level
   `im:message` full-send permission; only add the robot to the groups that need it, never to company-wide groups.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Target platform | Yes | `feishu` / `dingtalk` / `wecom`, multi-select allowed (built separately per platform) |
| Message body | Yes | Plain text or Markdown; length is bounded by each platform's limits |
| Message format | No | Default `markdown`; use `--format text` for plain text |
| Title | No | Used for Markdown messages (Feishu/DingTalk have a separate field; WeCom inlines it as `#`) |
| @ targets | No | `--at-mobiles` comma-separated; the phone numbers must be in the group |
| webhook credentials | Required for real execution | Read only from environment variables; not needed during the dry-run stage |
| Sign secret | Optional for DingTalk | DingTalk **must** pick one of three: sign / keyword / IP allowlist |

**When inputs are missing, ask for all at once:**

> Please provide in one go: ① which platform(s) to send to (multi-select allowed); ② the message body and format (Markdown or plain text);
> ③ whether to @ someone (a phone number, must already be in the group); ④ whether that platform's webhook credentials are already in
> the environment (please do not paste the token directly to me — I only check whether it exists). By default I will first show you the payload,
> and will not send.

## Cross-protocol Difference Table

| Dimension | Feishu | DingTalk | WeCom |
|---|---|---|---|
| Auth method | Path token in the webhook URL | `access_token` query + **sign**/keyword/IP allowlist (pick one, mandatory) | `key` in the webhook URL |
| Signing | No signing mechanism; relies on URL token secrecy | HMAC-SHA256(secret, `{ts}\n{secret}`) → base64 → urlencode | No signing |
| Credential validity | Long-lived unless the robot is reset | **`access_token` gets reset**; the sign secret can be rotated | Long-lived unless the robot is removed |
| Message type field | `msg_type` (underscore) | `msgtype` (one word) | `msgtype` (one word) |
| Markdown support | **No standalone type**: use `post` (rich text) or the message card `interactive` | Native `markdown` type, with a standalone `title` | Native `markdown` type, `title` inlined |
| Content container type | **Stringified JSON** (`content` is a string) | Nested object | Nested object |
| @ people | `<at user_id="...">` tags in the body | Top-level `at.atMobiles` object | `<@userid>` placeholders in the body |
| Single text limit | About 15000 chars | About 20000 chars | **4096 chars (tightest)** |
| Success detection | `code == 0` (**HTTP 200 does not mean success**) | `errcode == 0` (flat structure) | `errcode == 0` (flat structure) |
| Callback receiving | Event subscription (`schema 2.0`, encryptable) | Needs an outbound callback URL, JSON | Needs a callback URL + AES decryption, **XML** |
| Typical failure codes | 19002 bad params / 9499 bad signature | 310000 security check failed / 300001 token invalid | 93000 invalid key / 45009 rate limit exceeded |
| Rate limits | About 100 req/min/robot | About 20 msgs/min/robot | About 20 msgs/min/robot |

## Pre-flight Self-check

```bash
python3 --version                                        # expect >= 3.8
test -f scripts/im_bridge.py && echo SCRIPT_OK            # expect to print SCRIPT_OK
# Credential check: only judge existence, never echo — a token in terminal history is a leak
for v in FEISHU_WEBHOOK_TOKEN DINGTALK_ACCESS_TOKEN WECOM_WEBHOOK_KEY; do
  printf '%s: ' "$v"; test -n "$(printenv $v)" && echo present || echo missing
done
test -n "$DINGTALK_SIGN_SECRET" && echo "sign secret present" || echo "sign secret missing"
# python3 scripts/im_bridge.py --help >/dev/null && echo CLI_OK
```

| Result | Interpretation |
|---|---|
| A platform is `missing` | Only affects that platform's real sending; payload construction proceeds, build the payload first then add credentials |
| DingTalk sign secret `missing` | If the robot already has a keyword or IP allowlist configured, signing may be skipped; otherwise `310000` is inevitable |
| `SCRIPT_OK` missing | The script is absent; fall back to hand-writing JSON per this doc's protocol table |

## Workflow

### Step 1: Confirm Platform and Security Settings

First ask which platform to send to. For DingTalk you **must** confirm the three-way security setting:

- **Signing** (recommended): after generating a secret, put it in the `DINGTALK_SIGN_SECRET` environment variable;
- **Keyword**: the message body must contain the configured keyword, else it silently fails (`310000`);
- **IP allowlist**: only applies when the server has a fixed public IP.

Expected: get the platform list plus DingTalk's security mode.
On failure (none of the three configured): no matter how you assemble the payload it will be rejected; first guide the user to add one in the robot settings.

### Step 2: Build the Payload (dry-run)

```bash
# Feishu
python3 scripts/im_bridge.py build-message --platform feishu --text build complete   # dry run: builds the three providers' message payloads (does not send)

# python3 scripts/im_bridge.py build-message --platform feishu \
#   --title "Release notice" --text "v0.18.0 released"

# DingTalk (with signing)
# python3 scripts/im_bridge.py build-message --platform dingtalk \
#   --title "Release notice" --text "v0.18.0 released" --sign --sign-secret-env DINGTALK_SIGN_SECRET

# WeCom (mind the 4096-char limit)
# python3 scripts/im_bridge.py build-message --platform wecom \
#   --title "Release notice" --text "v0.18.0 released" --at-mobiles 13800000000
```

Expected: prints the full URL (credential positions as `{token}` placeholders), request header notes, body length vs the limit,
and the final JSON. The ending explicitly states "no request was sent."

On failure: `over the limit` → split the message or switch to "send a link + summary";
`unsupported --format` → check whether `markdown` was mistyped as `md`.

### Step 3: Send

```bash
# Feishu
curl -sS -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/$FEISHU_WEBHOOK_TOKEN" \
  -H 'Content-Type: application/json' --data @payload.json

# DingTalk (sign is computed by the proxy layer per the script-printed algorithm and appended to the URL)
curl -sS -X POST "https://oapi.dingtalk.com/robot/send?access_token=$DINGTALK_ACCESS_TOKEN&timestamp=$TS&sign=$SIGN" \
  -H 'Content-Type: application/json' --data @payload.json

# WeCom
curl -sS -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=$WECOM_WEBHOOK_KEY" \
  -H 'Content-Type: application/json' --data @payload.json
```

**Before sending, the payload must be reviewed by the user** — once a message is out it cannot be recalled, and it is a visible action.

Expected: Feishu `{"code":0,"msg":"success"}`; DingTalk/WeCom `{"errcode":0,"errmsg":"ok"}`.
On failure: save the response body to a file for step 4 to parse.

### Step 4: Parse Response / Callback

```bash
python3 scripts/im_bridge.py parse-webhook --platform feishu --json response.json
python3 scripts/im_bridge.py parse-webhook --platform dingtalk --json callback.json
```

Expected: success/failure judgment plus targeted explanation for the error code (e.g. 310000 points directly to a security-settings issue).

On failure: Feishu returns `{"encrypt": "..."}` → the callback has encryption enabled; first decrypt with the Encrypt Key.
Before decryption, reading any field is untrustworthy.

### Step 5: Batch Distribution and Idempotency

When pushing the same content to multiple groups, build and send per platform and per group; **must record the send result for every group**.
On the receiving side, dedup by event ID (Feishu's `header.event_id`) or message ID — both Feishu and DingTalk
**re-deliver** the same event on timeout without an ACK.

Expected: one row per group in the ledger, marked success/failure with the error code.
On failure: a group returns 429 → that robot is rate-limited; serialize and add intervals, do not retry concurrently.

## Delivery Standards

- **Definition of success**: the target group actually receives the message, and the response body has `code == 0` (Feishu) or
  `errcode == 0` (DingTalk/WeCom). **Judging only by the HTTP status code is not accepted.**
- **Artifacts**: one `payload.json` per platform, the raw `response.json`,
  and the batch-distribution ledger (group / platform / result / error code / time).
- **Integrity verification**:
  - Read the success code from the response body, not curl's exit code (curl still returns 0 for HTTP 4xx/5xx by default);
  - Ledger row count == target group count, no omissions;
  - No credential plaintext in artifacts: `grep -lE '\$?(FEISHU_WEBHOOK_TOKEN|DINGTALK_ACCESS_TOKEN|WECOM_WEBHOOK_KEY)' *.json` should have no hits.

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| DingTalk `310000` security check failed | No signing, the body lacks the configured keyword, and the IP is not on the allowlist | Fill in one of the three; use `--sign` for signing, or ensure the body contains the keyword for keyword mode |
| DingTalk `300001` invalid token | The robot's access_token was reset (changing groups or settings resets it) | Copy the new token from the robot settings page and update the environment variable |
| Feishu returns HTTP 200 but actually failed | Feishu still returns 200 on failure; judging only by the HTTP code false-reports success | Must read the response body `code`; use `parse-webhook`; treat any `code != 0` as failure |
| Feishu `19002` parameter error | `content` was written as a nested object (it must be a **stringified JSON**) | Build with the script, do not hand-assemble; check the spelling of `msg_type` (underscore) |
| WeCom content is not visible in WeChat | Markdown messages **only render in the WeCom client** | Send `text` type instead, or tell the recipient to open it in WeCom |
| WeCom body is truncated or returns 400 | Over the 4096-char limit | Split into multiple messages, or switch to "summary + document link" |
| The same event is processed twice | Feishu/DingTalk re-deliver on timeout without ACK; no idempotency key | Build a dedup table from `header.event_id` (Feishu) or the message ID |
| @ does not work | The @'d person is not in the group, or you @'d by phone number while the platform wants a user_id | First add the person to the group; for WeCom/Feishu use the in-platform user ID instead |
| Robot rate-limited | WeCom/DingTalk about 20 msgs/min, Feishu about 100 req/min | Send serially with intervals ≥3s; on 429 use exponential backoff, do not retry concurrently |
| Callback decryption fails | Feishu enabled encrypted callbacks; what arrived is `{"encrypt": ...}` | Decrypt with the Encrypt Key (aes-256-cbc) before parsing; verify `schema 2.0` |

## References

- `scripts/im_bridge.py` — `build-message` (three-platform payload construction, including DingTalk signing params)
  and `parse-webhook` (response/callback parsing and targeted error-code explanation)
- `references/sources-and-methodology.md` — the design rationale for collapsing the three protocols' differences, the signing algorithms,
  and judgments like "HTTP 200 is not success"
