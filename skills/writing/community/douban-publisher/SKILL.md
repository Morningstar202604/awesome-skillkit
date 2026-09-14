---
name: douban-publisher
description: >
  豆瓣内容发布客户端，基于 www.douban.com Web 内部接口（豆瓣无公开 API，
  早期 OAuth API 已停止维护）。支持创建日记（--privacy 可选公开/仅自己可见/好友可见）、
  发布广播、在指定小组发布话题。Cookie 从环境变量 DOUBAN_COOKIE 或 --cookie-file
  读取，绝不入库；所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正
  联网发送；端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发豆瓣日记 / 发豆瓣广播 / 在豆瓣小组发帖 /
  发布豆瓣小组话题 / publish a Douban note / post a Douban status /
  create a Douban group topic. Do NOT use for 豆瓣电影、图书、音乐的评分与评论，
  不用于豆列、相册与同城活动管理，不用于抓取他人内容，
  也不用于微博、小红书等其他平台发布。
description_zh: 豆瓣日记创建、广播发布、小组话题发布，基于 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [douban, publishing, automation, china-platform]
metadata:
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
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