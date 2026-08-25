---
name: oschina-publisher
description: 开源中国发布客户端（官方 API + Web 内部 API）
description_zh: 开源中国博客发布、问答、动态发布，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [oschina, publishing, automation, china-platform]
---

# 开源中国 Publisher

开源中国发布客户端，支持两种模式：
1. **官方开放平台 API** —— 博客发布，需申请 AppKey
2. **Web 内部 API** —— 问答/动态发布，仅需 Cookie

## 功能

- `blog-publish` —— 发布博客（官方 API）
- `question-ask` —— 提问（Web 内部 API）
- `dynamic-post` —— 发布动态（Web 内部 API）

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：
  - 官方 API：`OSCHINA_ACCESS_TOKEN`
  - Web API：`OSCHINA_COOKIE` 环境变量或 `--cookie-file`

## 使用示例

```bash
# 博客发布（官方 API）
export OSCHINA_ACCESS_TOKEN="your_token"
python oschina_publisher.py blog-publish --execute \
  --title "我的博客" \
  --content "# 标题\n正文内容..." \
  --tags "Python,AI" \
  --catalog 123

# 问答（Web Cookie）
export OSCHINA_COOKIE="your_cookie"
python oschina_publisher.py question-ask --execute \
  --title "如何解决某问题？" \
  --content "详细描述..." \
  --tags "Python,异步编程"

# 动态发布
python oschina_publisher.py dynamic-post --execute \
  --content "发个动态 #话题#" \
  --images "https://example.com/img1.png"
```

## 端点核对（首次使用必做）

Web 内部 API 无官方文档，端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 博客发布: `POST https://www.oschina.net/action/openapi/blog/add`
- 提问: `POST https://www.oschina.net/action/api/question/add`
- 动态: `POST https://www.oschina.net/action/api/dynamic/add`

## 认证

**官方 API**：`OSCHINA_ACCESS_TOKEN`
**Web 内部 API**：`OSCHINA_COOKIE` 或 `--cookie-file`

```bash
export OSCHINA_COOKIE="your_cookie"
# 或
python oschina_publisher.py question-ask --cookie-file ~/.oschina_cookie ...
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
- `segmentfault-publisher` — SegmentFault 发布
- `douban-publisher` — 豆瓣发布
- `cross-post-orchestrator` — 多平台编排