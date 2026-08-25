---
name: weibo-publisher
description: 微博发布/管理自动化（官方 API + Web 内部 API）
description_zh: 微博发布、转发、评论、删除、图片上传，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [weibo, social, publishing, automation, china-platform]
---

# 微博 Publisher

微博发布/管理自动化客户端，支持两种模式：
1. **官方开放平台 API** —— 需申请 AppKey，适合生产系统集成
2. **Web 内部 API** —— 仅需 Cookie，适合个人账号自动化

## 功能

- `post-official` —— 官方 API 发布微博（文本 + 图片）
- `post-web` —— Web 内部 API 发布微博（仅需 Cookie）
- `repost` —— 转发微博
- `comment` —— 评论微博
- `delete` —— 删除微博
- `upload-image` —— 上传图片（返回 pic_id）

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：
  - 官方 API：`WEIBO_APPKEY`、`WEIBO_APPSECRET`、`WEIBO_ACCESS_TOKEN` 环境变量
  - Web API：`WEIBO_COOKIE` 环境变量或 `--cookie-file`
- **端点声明**：所有端点在常量中集中维护。

## 使用示例

```bash
# 官方 API 模式
export WEIBO_ACCESS_TOKEN="your_token"
python weibo_publisher.py post-official --execute \
  --text "Hello 微博！#话题#" \
  --pic-ids "pic_id1,pic_id2"

# Web Cookie 模式（个人账号自动化）
export WEIBO_COOKIE="SUB=xxx; SSOLoginState=xxx; ..."
python weibo_publisher.py post-web --execute \
  --text "Hello 微博！#话题#"
```

## 认证

**官方 API**：
- `WEIBO_ACCESS_TOKEN` — 直接使用 access_token
- 或 `WEIBO_APPKEY` + `WEIBO_APPSECRET` — 需自行实现 OAuth2 刷新

**Web 内部 API**：
- `WEIBO_COOKIE` — 包含 `SUB`、`SSOLoginState` 等字段的完整 Cookie
- 或 `--cookie-file` 指定文件路径

```bash
export WEIBO_COOKIE="SUB=xxx; SSOLoginState=xxx; ..."
# 或
python weibo_publisher.py post-web --cookie-file ~/.weibo_cookie ...
```

## 端点核对（Web 模式首次使用必做）

Web 内部 API 无官方文档，端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 官方发布: `POST https://api.weibo.com/2/statuses/update.json`
- 官方上传: `POST https://api.weibo.com/2/statuses/upload.json`
- Web 发布: `POST https://weibo.com/ajax/statuses/build`
- Web 上传: `POST https://weibo.com/ajax/statuses/upload`

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库
- `publish_common`（同目录 `../../../_common/publish_common.py`）

## 相关技能

- `xiaohongshu-publisher` — 小红书发布
- `csdn-publisher` — CSDN 发布
- `juejin-publisher` — 掘金发布
- `cross-post-orchestrator` — 多平台编排