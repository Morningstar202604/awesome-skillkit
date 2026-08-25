---
name: segmentfault-publisher
description: SegmentFault 发布客户端（Web 内部 API）
description_zh: SegmentFault 文章草稿、发布、提问，基于 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [segmentfault, publishing, automation, china-platform]
---

# SegmentFault Publisher

SegmentFault 发布客户端，基于 SegmentFault Web 内部接口（无公开 API）。

## 功能

- `article-save` —— 保存文章草稿（返回 article_id）
- `article-publish` —— 发布文章
- `question-ask` —— 提问

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：`SF_COOKIE` 环境变量或 `--cookie-file`

## 使用示例

```bash
export SF_COOKIE="your_cookie"
python segmentfault_publisher.py article-save --execute \
  --title "我的文章" \
  --content "# 标题\n正文内容..." \
  --summary "文章摘要" \
  --tags "Python,AI" \
  --cover-image "https://example.com/cover.png"

python segmentfault_publisher.py article-publish --execute \
  --title "发布的文章" \
  --content "# 标题\n正文..." \
  --tags "Python,AI"

python segmentfault_publisher.py question-ask --execute \
  --title "如何解决某问题？" \
  --content "详细描述..." \
  --tags "Python,异步编程"
```

## 端点核对（首次使用必做）

SegmentFault 无公开 API，端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 文章草稿: `POST https://segmentfault.com/api/articles/save`
- 文章发布: `POST https://segmentfault.com/api/articles/publish`
- 提问: `POST https://segmentfault.com/api/questions/ask`

## 认证

`SF_COOKIE` — 包含 SegmentFault 登录态 Cookie

```bash
export SF_COOKIE="your_cookie"
# 或
python segmentfault_publisher.py article-save --cookie-file ~/.sf_cookie ...
```

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库
- `publish_common`

## 相关技能

- `v2ex-publisher` — V2EX 发帖
- `oschina-publisher` — 开源中国发布
- `douban-publisher` — 豆瓣发布
- `cross-post-orchestrator` — 多平台编排