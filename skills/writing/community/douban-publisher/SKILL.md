---
name: douban-publisher
description: 豆瓣日记/广播/小组发布客户端（Web 内部 API）
description_zh: 豆瓣日记创建、广播发布、小组话题发布，基于 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [douban, publishing, automation, china-platform]
---

# 豆瓣 Publisher

豆瓣发布客户端，基于豆瓣 Web 内部接口（无公开 API，早期 OAuth API 已停止维护）。

## 功能

- `note-create` —— 创建日记
- `status-post` —— 发布广播
- `group-topic` —— 发布小组话题

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：`DOUBAN_COOKIE` 环境变量或 `--cookie-file`

## 使用示例

```bash
export DOUBAN_COOKIE="dbcl2=xxx; ck=xxx; ..."
python douban_publisher.py note-create --execute \
  --title "我的日记" \
  --content "日记内容..." \
  --privacy 0

python douban_publisher.py status-post --execute \
  --content "发个广播 #话题#"

python douban_publisher.py group-topic --execute 123456 \
  --title "小组话题标题" \
  --content "话题内容..."
```

## 端点核对（首次使用必做）

豆瓣无公开 API（早期 OAuth API 已停止维护），端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 创建日记: `POST https://www.douban.com/j/note/new`
- 发布广播: `POST https://www.douban.com/j/status/new`
- 小组话题: `POST https://www.douban.com/j/group/topic/new`

## 认证

`DOUBAN_COOKIE` — 包含 `dbcl2`、`ck`、`_vwo_uuid_v2` 等字段的完整 Cookie

```bash
export DOUBAN_COOKIE="dbcl2=xxx; ck=xxx; ..."
# 或
python douban_publisher.py note-create --cookie-file ~/.douban_cookie ...
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
- `oschina-publisher` — 开源中国发布
- `cross-post-orchestrator` — 多平台编排