---
name: feishu-dingtalk-bridge
description: "Compose and parse chat messages across Feishu (Lark), DingTalk, and WeCom group robots, normalizing three different auth and payload protocols behind one workflow. Use when the user asks to 发飞书机器人 / 发钉钉通知 / 发企业微信消息 / 群里推一条通知 / 机器人告警推送 / 日报推送到群 / send to Feishu bot / DingTalk webhook / WeCom group robot / push alert to chat group. Do NOT use for Notion pages (use notion-workspace), issue trackers (use issue-tracker-sync), or file archiving (use cloud-drive-manager)."
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

# Feishu / DingTalk / WeCom Bridge（飞书 钉钉 企业微信 消息桥）

一条通知要同时推到三个群，但三家的协议没有一处相同：飞书把内容塞进
**字符串化的 JSON**，钉钉用独立的 `markdown` 对象，企微把标题和正文揉成
一个 `content` 字符串。本技能把这层差异收敛成"选平台 → 出负载 → 发"三步。

**核心判断：不要试图写一套通用负载再翻译——三家的字段语义不同，**
**必须各自构造。** 唯一共享的是"先 dry-run 审负载、再发送"的节奏。

**红线（本技能强制）**

1. **凭证绝不硬编码**：webhook token、access_token、加签密钥只从环境变量读
   （`FEISHU_WEBHOOK_TOKEN` / `DINGTALK_ACCESS_TOKEN` / `DINGTALK_SIGN_SECRET` /
   `WECOM_WEBHOOK_KEY`）。脚本**从不读取也不打印**这些值，连加签都由代理层在
   发送时计算。
2. **默认 dry-run**：`build-message` 只打印"将要发送的 JSON"，**不发请求**。
   加 `--yes` 之类的授权由用户在会话中明确给出后才发送。
3. **最小权限**：群机器人只需 webhook 令牌，**不要**申请企业应用级别的
   `im:message` 全量发送权限；机器人只加到需要的群，不给全员群。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 目标平台 | 是 | `feishu` / `dingtalk` / `wecom`，可多选（同一内容分别构造） |
| 消息正文 | 是 | 纯文本或 Markdown；长度受各平台上限约束 |
| 消息格式 | 否 | 默认 `markdown`；纯文本用 `--format text` |
| 标题 | 否 | Markdown 消息用（飞书/钉钉独立字段，企微内联为 `#`） |
| @ 对象 | 否 | `--at-mobiles` 逗号分隔；手机号需在群里 |
| webhook 凭证 | 真实执行必填 | 只从环境变量读取；dry-run 阶段不需要 |
| 加签密钥 | 钉钉可选 | 钉钉**必须**三选一：加签 / 关键词 / IP 白名单 |

**缺输入时一次性问齐**：

> 请一次提供：① 发哪个平台（可多选）；② 消息正文与格式（Markdown 还是纯文本）；
> ③ 是否需要 @ 某人（手机号，需已在群内）；④ 该平台的 webhook 凭证是否已放进
> 环境变量（请不要直接把令牌贴给我，我只检查它是否存在）。默认我先出负载给你看，
> 不发送。

## 三家协议差异对照表

| 维度 | 飞书 | 钉钉 | 企业微信 |
|---|---|---|---|
| 鉴权方式 | webhook URL 里的 path token | `access_token` query + **加签**/关键词/IP 白名单（三选一，强制） | webhook URL 里的 `key` |
| 加签 | 无加签机制，靠 URL token 保密 | HMAC-SHA256(secret, `{ts}\n{secret}`) → base64 → urlencode | 无加签 |
| 凭证有效期 | 长期，除非重置机器人 | **`access_token` 会被重置**，加签密钥可轮换 | 长期，除非移除机器人 |
| 消息类型字段 | `msg_type`（下划线） | `msgtype`（连写） | `msgtype`（连写） |
| Markdown 支持 | **无独立类型**：用 `post`（富文本）或消息卡片 `interactive` | 原生 `markdown` 类型，含独立 `title` | 原生 `markdown` 类型，`title` 内联 |
| 内容容器类型 | **字符串化的 JSON**（`content` 是 string） | 嵌套对象 | 嵌套对象 |
| @ 人 | 正文内 `<at user_id="...">` 标签 | 顶层 `at.atMobiles` 对象 | 正文内 `<@userid>` 占位 |
| 单条文本上限 | 约 15000 字符 | 约 20000 字符 | **4096 字符（最紧）** |
| 成功判定 | `code == 0`（**HTTP 200 不代表成功**） | `errcode == 0`（扁平结构） | `errcode == 0`（扁平结构） |
| 回调接收 | 事件订阅（`schema 2.0`，可加密） | 需要出网回调地址，JSON | 需要回调 URL + AES 解密，**XML** |
| 典型失败码 | 19002 参数错 / 9499 签名错 | 310000 安全校验失败 / 300001 token 失效 | 93000 key 无效 / 45009 频率超限 |
| 频率限制 | 约 100 次/分钟/机器人 | 约 20 条/分钟/机器人 | 约 20 条/分钟/机器人 |

## 前置自检

```bash
python3 --version                                        # 预期 >= 3.8
test -f scripts/im_bridge.py && echo SCRIPT_OK            # 预期打印 SCRIPT_OK
# 凭证检查：只判断存在性，绝不回显 —— 令牌进终端历史就等于泄露
for v in FEISHU_WEBHOOK_TOKEN DINGTALK_ACCESS_TOKEN WECOM_WEBHOOK_KEY; do
  printf '%s: ' "$v"; test -n "$(printenv $v)" && echo present || echo missing
done
test -n "$DINGTALK_SIGN_SECRET" && echo "sign secret present" || echo "sign secret missing"
# python3 scripts/im_bridge.py --help >/dev/null && echo CLI_OK
```

| 结果 | 判读 |
|---|---|
| 某平台 `missing` | 只影响该平台的真实发送；负载构造照常可跑，先出负载再补凭证 |
| 钉钉 sign secret `missing` | 若机器人已配关键词或 IP 白名单则可不加签；否则 `310000` 必现 |
| `SCRIPT_OK` 缺失 | 脚本不在，退化为照本文档的协议表手写 JSON |

## 工作流

### 步骤 1：确定平台与安全设置

先问清发哪个平台。对钉钉**必须**确认三选一的安全设置：

- **加签**（推荐）：生成密钥后放环境变量 `DINGTALK_SIGN_SECRET`；
- **关键词**：消息正文必须含设定关键词，否则静默失败（`310000`）；
- **IP 白名单**：仅适用于服务器有固定公网 IP 的场景。

预期：拿到平台清单 + 钉钉的安全模式。
若失败（三个都没配）：无论如何拼负载都会被拒，先引导用户去机器人设置里补一项。

### 步骤 2：构造负载（dry-run）

```bash
# 飞书
python3 scripts/im_bridge.py build-message --platform feishu --text 构建完成   # 干跑：构造三家消息负载（不发送）

# python3 scripts/im_bridge.py build-message --platform feishu \
#   --title "发布通知" --text "v0.18.0 已发布"

# 钉钉（带加签）
# python3 scripts/im_bridge.py build-message --platform dingtalk \
#   --title "发布通知" --text "v0.18.0 已发布" --sign --sign-secret-env DINGTALK_SIGN_SECRET

# 企业微信（注意 4096 字符上限）
# python3 scripts/im_bridge.py build-message --platform wecom \
#   --title "发布通知" --text "v0.18.0 已发布" --at-mobiles 13800000000
```

预期：打印完整 URL（凭证位置用 `{token}` 占位）、请求头说明、正文长度与上限、
以及最终 JSON。结尾明确写着"未发送任何请求"。

若失败：`超过上限` → 拆消息或改为"发链接 + 摘要"；
`不支持的 --format` → 检查是否把 `markdown` 拼成了 `md`。

### 步骤 3：发送

```bash
# 飞书
curl -sS -X POST "https://open.feishu.cn/open-apis/bot/v2/hook/$FEISHU_WEBHOOK_TOKEN" \
  -H 'Content-Type: application/json' --data @payload.json

# 钉钉（sign 由代理层按脚本打印的算法计算后拼到 URL）
curl -sS -X POST "https://oapi.dingtalk.com/robot/send?access_token=$DINGTALK_ACCESS_TOKEN&timestamp=$TS&sign=$SIGN" \
  -H 'Content-Type: application/json' --data @payload.json

# 企业微信
curl -sS -X POST "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=$WECOM_WEBHOOK_KEY" \
  -H 'Content-Type: application/json' --data @payload.json
```

**发送前必须把 payload 给用户过目**——消息一旦发出无法撤回，且是可见动作。

预期：飞书 `{"code":0,"msg":"success"}`；钉钉/企微 `{"errcode":0,"errmsg":"ok"}`。
若失败：把响应体存文件交给步骤 4 解析。

### 步骤 4：解析响应 / 回调

```bash
python3 scripts/im_bridge.py parse-webhook --platform feishu --json response.json
python3 scripts/im_bridge.py parse-webhook --platform dingtalk --json callback.json
```

预期：成功/失败判定 + 针对错误码的定向解释（如 310000 直接指出是安全设置问题）。

若失败：飞书回 `{"encrypt": "..."}` → 回调启用了加密，需先用 Encrypt Key
解密；解密前任何字段读取都不可信。

### 步骤 5：批量分发与幂等

同一内容推多群时，逐平台、逐群构造并发送；**必须记录每个群的发送结果**。
接收侧用事件 ID（飞书 `header.event_id`）或消息 ID 做去重——飞书与钉钉
都会在超时未 ACK 时**重推**同一条事件。

预期：台账里每个群一行，标注成功/失败与错误码。
若失败：某群 429 → 该机器人已限流，串行化并加间隔，不要并发重试。

## 交付标准

- **成功定义**：目标群实际收到消息，且响应体 `code == 0`（飞书）或
  `errcode == 0`（钉钉/企微）。**不接受只看 HTTP 状态码**。
- **产物**：每平台一个 `payload.json`、原始响应 `response.json`、
  批量分发台账（群名 / 平台 / 结果 / 错误码 / 时间）。
- **完整性验证**：
  - 从响应体读成功码，而非 curl 退出码（curl 对 HTTP 4xx/5xx 默认仍返回 0）；
  - 台账行数 == 目标群数，无遗漏；
  - 产物中不得出现凭证明文：`grep -lE '\$?(FEISHU_WEBHOOK_TOKEN|DINGTALK_ACCESS_TOKEN|WECOM_WEBHOOK_KEY)' *.json` 应无命中。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| 钉钉 `310000` 安全校验失败 | 未加签、且正文不含设定关键词、IP 也不在白名单 | 三选一补齐；加签用 `--sign`，关键词模式确保正文含该词 |
| 钉钉 `300001` token 无效 | 机器人的 access_token 被重置（换群、改设置都会重置） | 去机器人设置页复制新 token，更新环境变量 |
| 飞书 HTTP 200 但实际失败 | 飞书失败时仍返回 200，只判 HTTP 码会误报成功 | 必须读响应体 `code`；用 `parse-webhook` 解析，`code != 0` 一律当失败 |
| 飞书 `19002` 参数错误 | `content` 写成了嵌套对象（应为**字符串化的 JSON**） | 用脚本构造，勿手拼；核对 `msg_type` 拼法（下划线） |
| 企微消息在微信里看不到内容 | markdown 消息**只支持企业微信客户端**查看 | 改发 `text` 类型，或提示接收方用企业微信打开 |
| 企微正文被截断或 400 | 超过 4096 字符上限 | 拆分多条，或改为"摘要 + 文档链接" |
| 同一条事件被重复处理 | 飞书/钉钉超时未 ACK 会重推；无幂等键 | 用 `header.event_id`（飞书）或消息 ID 建去重表 |
| @ 了但不生效 | 被 @ 的人不在群里，或 @ 用的是手机号而平台要 user_id | 先拉人入群；企微/飞书改用平台内的用户 ID |
| 机器人限流 | 企微/钉钉约 20 条/分钟，飞书约 100 次/分钟 | 串行发送 + 间隔 ≥3s；遇 429 指数退避，勿并发重试 |
| 回调解密失败 | 飞书启用了加密回调，收到的是 `{"encrypt": ...}` | 用 Encrypt Key（aes-256-cbc）解密后再解析；校验 `schema 2.0` |

## 参考

- `scripts/im_bridge.py` —— `build-message`（三平台负载构造，含钉钉加签参数）
  与 `parse-webhook`（响应/回调解析与错误码定向解释）
- `references/sources-and-methodology.md` —— 三家协议差异收敛、加签算法与
  "HTTP 200 不等于成功"这类判据的设计依据
