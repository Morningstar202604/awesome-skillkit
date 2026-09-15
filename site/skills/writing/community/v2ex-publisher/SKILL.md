---
name: v2ex-publisher
description: >
  V2EX 发帖与回复客户端，基于 www.v2ex.com Web 内部接口（无公开开放 API）。
  支持创建主题帖（需 --node-id 节点 ID）、回复指定主题、获取节点列表（用于查 node_id）。
  Cookie 从环境变量 V2EX_COOKIE 或 --cookie-file 读取，绝不入库；
  所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送；
  端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发 V2EX / 在 V2EX 发帖 / 回复 V2EX 主题 /
  查 V2EX 节点 / post on V2EX / create a V2EX topic / reply to a V2EX thread.
  Do NOT use for 节点收藏、感谢、私信与举报等互动操作，不用于批量抓取或搬运帖子，
  也不用于 SegmentFault、开源中国等其他社区发布。
description_zh: V2EX 主题创建、回复、节点列表获取，基于 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to www.v2ex.com and valid session credentials in environment variables. Python 3.8+.
tags: [v2ex, community, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# V2EX Publisher

V2EX 发帖/回复客户端，基于 V2EX Web 内部接口（无公开 API）。

## 功能

- `topic-create` —— 创建主题帖
- `reply-create` —— 回复主题
- `node-list` —— 获取节点列表（用于获取 node_id）

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：`V2EX_COOKIE` 环境变量或 `--cookie-file`

## 使用示例

```bash
export V2EX_COOKIE="A2=xxx; PB3_SESSION=xxx; ..."
python v2ex_publisher.py topic-create --execute \
  --title "我的主题" \
  --content "正文内容..." \
  --node-id 123

python v2ex_publisher.py reply-create --execute 12345 \
  --content "回复内容..."

python v2ex_publisher.py node-list --execute
```

## 端点核对（首次使用必做）

V2EX 无公开 API，端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 创建主题: `POST https://www.v2ex.com/api/topics/create`
- 创建回复: `POST https://www.v2ex.com/api/replies/create`
- 节点列表: `GET https://www.v2ex.com/api/nodes/show.json`

## 认证

`V2EX_COOKIE` — 包含 `A2`、`PB3_SESSION` 等字段的完整 Cookie

```bash
export V2EX_COOKIE="A2=xxx; PB3_SESSION=xxx; ..."
# 或
python v2ex_publisher.py topic-create --cookie-file ~/.v2ex_cookie ...
```

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库
- `publish_common`

## 相关技能

- `segmentfault-publisher` — SegmentFault 发布
- `oschina-publisher` — 开源中国发布
- `douban-publisher` — 豆瓣发布
- `cross-post-orchestrator` — 多平台编排