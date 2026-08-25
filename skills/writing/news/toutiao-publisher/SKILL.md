---
name: toutiao-publisher
description: 今日头条/抖音文章发布客户端（官方 API + Web 内部 API）
description_zh: 今日头条文章发布、微头条发布，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [toutiao, douyin, publishing, automation, china-platform]
metadata:
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 今日头条/抖音 Publisher

今日头条/抖音发布客户端，支持两种模式：
1. **官方开放平台 API** —— 文章发布，需申请 AppKey
2. **Web 内部 API** —— 微头条发布，仅需 Cookie

## 功能

- `article-publish` —— 文章发布（官方 API）
- `micro-post` —— 微头条发布（Web 内部 API）

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：
  - 官方 API：`TOUTIAO_ACCESS_TOKEN` 或 `TOUTIAO_APPID`/`TOUTIAO_APPSECRET`
  - Web API：`TOUTIAO_COOKIE` 环境变量或 `--cookie-file`

## 使用示例

```bash
# 文章发布（官方 API）
export TOUTIAO_ACCESS_TOKEN="your_token"
python toutiao_publisher.py article-publish --execute \
  --title "我的文章" \
  --content "# 标题\n正文内容..." \
  --cover-images "https://example.com/cover.png" \
  --tags "Python,AI"

# 微头条发布（Web Cookie）
export TOUTIAO_COOKIE="your_cookie"
python toutiao_publisher.py micro-post --execute \
  --content "发个微头条 #话题#" \
  --images "https://example.com/img1.png"
```

## 端点核对（首次使用必做）

Web 内部 API 无官方文档，端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 文章发布: `POST https://open.toutiao.com/api/articles/publish`
- 微头条: `POST https://www.toutiao.com/api/microblog/create`

## 认证

**官方 API**：`TOUTIAO_ACCESS_TOKEN` 或 `TOUTIAO_APPID`/`TOUTIAO_APPSECRET`
**Web 内部 API**：`TOUTIAO_COOKIE` 或 `--cookie-file`

```bash
export TOUTIAO_COOKIE="tt_webid=xxx; s_v_web_id=xxx; ..."
```

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库
- `publish_common`

## 相关技能

- `bilibili-publisher` — B 站发布
- `baijiahao-publisher` — 百家号发布
- `weibo-publisher` — 微博发布
- `cross-post-orchestrator` — 多平台编排