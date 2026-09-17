---
name: weibo-publisher
description: >
  微博发布客户端，双模式：官方开放平台 API 发微博（需 WEIBO_ACCESS_TOKEN，
  可附带已上传的 pic_ids）；Web 内部 API 发微博（仅需 WEIBO_COOKIE 或
  --cookie-file）；另提供图片上传的 dry-run 流程演示（仅打印计划）。
  所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送；
  Web 端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发微博 / 发一条微博 / 发带图微博 / 发布到微博 /
  post to Weibo / publish a Weibo status / update my Weibo.
  Do NOT use for 转发、评论、删除微博与私信（脚本未实现这些子命令），
  不用于定时发布、超话与粉丝群运营，也不用于小红书、B 站等其他平台发布。
description_zh: 微博发布、转发、评论、删除、图片上传，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to api.weibo.com / weibo.com and valid session credentials in environment variables. Python 3.8+.
tags: [weibo, social, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 微博发布客户端

双模式发布客户端：官方 API 发微博、Web 内部接口发微博、图片上传；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/social/weibo-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `post-official` / `post-web` / `upload-image`（注：原始描述标注 `repost`/`comment`/`delete` 脚本未实现，调用前先 dry-run 验证） |
| `--text` | 发微博必需 | 微博正文，支持 `#话题#` |
| `--pic-ids` | post-official 可选 | 已上传图片的 pic_id，逗号分隔 |
| `WEIBO_ACCESS_TOKEN` 或 `WEIBO_APPKEY`+`WEIBO_APPSECRET` | post-official 必需 | 官方 API 凭据 |
| `WEIBO_COOKIE` 或 `--cookie-file` | post-web 必需 | Web 内部接口凭据 |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 官方 API 发 / Web Cookie 发 / 仅上传图片？(2) 微博正文与配图？(3) 凭据用 `WEIBO_ACCESS_TOKEN`（官方）还是 `WEIBO_COOKIE` / `--cookie-file`（Web）？

## 前置自检

1. **Python**：`python3 --version` —— 预期 `3.8` 及以上；否则安装 Python 3.8+，STOP。
2. **脚本**：`test -f weibo_publisher.py && echo OK` —— 预期 `OK`；否则仓库损坏，STOP。
3. **凭据**：
   - 官方：`test -n "$WEIBO_ACCESS_TOKEN" -o -n "$WEIBO_APPKEY" && echo OK` —— 否则 STOP。
   - Web：`test -n "$WEIBO_COOKIE" -o -f ~/.weibo_cookie && echo OK` —— 否则 STOP，提示设置 `WEIBO_COOKIE` 或后续用 `--cookie-file`。

任一失败即 STOP，修复后再继续。

## 工作流

### 步骤 1：注入凭据

- **动作**：`export WEIBO_ACCESS_TOKEN="your_token"`（官方）或 `export WEIBO_COOKIE="SUB=xxx; SSOLoginState=xxx; ..."`（Web）；或 Web 命令加 `--cookie-file ~/.weibo_cookie`。
- **预期**：对应环境变量非空。
- **若失败**：未设置 → 退出码 1 报凭据缺失；STOP 并补齐。

### 步骤 2：dry-run 预览（默认，不联网）

- **动作**：`python weibo_publisher.py post-web --text "Hello 微博！#话题#"`
- **预期**：打印请求计划（method / url / body），**不发生网络请求**。
- **若失败**：参数错误 → 退出码 1 提示缺 `--text`；补齐后重跑。

### 步骤 3：--execute 真正发布

- **动作**：在步骤 2 命令后追加 `--execute`。
- **预期**：退出码 `0`，输出发布结果（含微博 ID / 链接）。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 4：核对返回

- **动作**：打开输出链接确认微博可见。
- **预期**：内容已发布。
- **若失败**：返回成功但不可见 → Token/Cookie 失效；刷新凭据后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `post-official` | `--text --pic-ids --execute` | 官方 API 发微博（文本+图片） |
| `post-web` | `--text --execute` | Web 内部接口发微博（仅需 Cookie） |
| `upload-image` | `--execute`（演示） | 上传图片返回 pic_id（dry-run 仅打印计划） |
| （通用） | `--cookie-file <path>` | Web 模式用文件替代 `WEIBO_COOKIE` |

> 说明：`repost`/`comment`/`delete` 在原始描述中标注为脚本未实现；如需使用，先 dry-run 验证是否可用，不可用则改用平台 UI。

## 端点核对（VERIFY BEFORE USE）

Web 内部 API 无官方文档，端点可能随时变更。首次使用必须按 SKILL.md 在浏览器 DevTools 核对：

- 官方发布：`POST https://api.weibo.com/2/statuses/update.json`
- 官方上传：`POST https://api.weibo.com/2/statuses/upload.json`
- Web 发布：`POST https://weibo.com/ajax/statuses/build`
- Web 上传：`POST https://weibo.com/ajax/statuses/upload`

所有端点集中在脚本常量中维护。

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--text` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Token/Cookie 失效或端点变更 | 刷新 `WEIBO_ACCESS_TOKEN`/`WEIBO_COOKIE`；Web 重核端点 |
| 端点返回 4xx/5xx | Web 端点已调整 | 按 DevTools 更新端点常量 |
| 发布成功但随后被删除 | 命中风控关键词或短时间高频发布 | 查看站内通知，删改敏感表述并降低发布频率 |
| 图片上传失败 / pic_id 无效 | 图片超体积或上传接口变更 | 压缩图片后重传，并按 DevTools 重新核对上传端点 |
| 频繁发布触发限流 | 同账号短时多次调用发布接口 | 拉开发布间隔，批量场景改为逐条人工确认 |

## 交付标准

- **成功定义**：退出码 `0` 且输出含微博 ID / 链接。
- **产物**：发布后的微博链接。
- **保存位置**：不落本地文件，链接回传用户。
- **完整性验证**：微博主页确认可见、配图正常。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：Token/Cookie 走环境变量或 `--cookie-file`，**绝不入库、绝不写入仓库**。
- 端点 VERIFY BEFORE USE：Web 端点发布前在 DevTools 核对。
- 不可逆操作前确认：先 dry-run 展示计划，用户确认后再 `--execute`。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`；仓库内位于 `skills/writing/_common/`）。

## 参考

- 本技能为纯提示型，无需外部参考文件。
