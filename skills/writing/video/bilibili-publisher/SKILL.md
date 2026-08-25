---
name: bilibili-publisher
description: B 站视频/专栏/动态发布客户端（官方 API + Web 内部 API）
description_zh: B 站视频投稿、专栏文章发布、动态发布，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [bilibili, video, publishing, automation, china-platform]
metadata:
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# B 站 Publisher

B 站发布客户端，支持两种模式：
1. **官方开放平台 API** —— 视频上传/投稿，需申请 AppKey
2. **Web 内部 API** —— 专栏文章/动态发布，仅需 Cookie

## 功能

- `video-upload` —— 视频文件上传（演示流程，实际需分片上传 + 断点续传）
- `video-submit` —— 视频投稿提交（官方 API）
- `article-save` —— 专栏草稿保存（Web 内部 API）
- `article-publish` —— 专栏文章发布（Web 内部 API）
- `dynamic-post` —— 动态发布（Web 内部 API）

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：
  - 官方 API：`BILI_ACCESS_KEY`、`BILI_SECRET_KEY` 环境变量
  - Web API：`BILI_COOKIE` 环境变量或 `--cookie-file`

## 使用示例

```bash
# 专栏草稿保存
export BILI_COOKIE="your_cookie_here"
python bilibili_publisher.py article-save --execute \
  --title "我的专栏文章" \
  --content "# 标题\n正文内容..." \
  --summary "文章摘要" \
  --category 0 \
  --tags "Python,AI" \
  --images "https://example.com/img1.png"

# 专栏发布
python bilibili_publisher.py article-publish --execute <article_id>

# 动态发布
python bilibili_publisher.py dynamic-post --execute \
  --content "发个动态 #话题#" \
  --images "https://example.com/img1.png,https://example.com/img2.png"
```

## 端点核对（首次使用必做）

Web 内部 API 无官方文档，端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 视频上传凭证: `GET https://member.bilibili.com/x/web-interface/upload/pre`
- 视频分片上传: `POST https://member.bilibili.com/x/web-interface/upload/chunk`
- 视频完成上传: `POST https://member.bilibili.com/x/web-interface/upload/complete`
- 视频投稿: `POST https://member.bilibili.com/x/web-interface/archive/add`
- 专栏草稿: `POST https://api.bilibili.com/x/article/add`
- 专栏发布: `POST https://api.bilibili.com/x/article/publish`
- 动态发布: `POST https://api.bilibili.com/x/dynamic/publish`

## 认证

**官方 API**：
- `BILI_ACCESS_KEY` + `BILI_SECRET_KEY` — 需自行实现签名鉴权

**Web 内部 API**：
- `BILI_COOKIE` — 包含 `SESSDATA`、`bili_jct`、`DedeUserID` 等字段
- 或 `--cookie-file` 指定文件路径

```bash
export BILI_COOKIE="SESSDATA=xxx; bili_jct=xxx; DedeUserID=xxx; ..."
# 或
python bilibili_publisher.py article-save --cookie-file ~/.bili_cookie ...
```

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库
- `publish_common`（打包后与技能目录平级的 `_common/publish_common.py`；仓库内位于 `skills/writing/_common/`）

## 相关技能

- `toutiao-publisher` — 今日头条/抖音发布
- `xiaohongshu-publisher` — 小红书发布
- `weibo-publisher` — 微博发布
- `cross-post-orchestrator` — 多平台编排