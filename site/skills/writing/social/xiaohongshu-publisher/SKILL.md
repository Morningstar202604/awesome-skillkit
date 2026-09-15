---
name: xiaohongshu-publisher
description: >
  小红书笔记发布与管理客户端，基于 www.xiaohongshu.com Web 内部接口（无公开开放 API）。
  支持保存草稿（标题、正文、话题标签、多图与封面，返回 note_id）、发布笔记、
  编辑已发布笔记、删除笔记。Cookie 从环境变量 XHS_COOKIE 或 --cookie-file 读取，
  绝不入库；所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送；
  端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发小红书 / 发一篇小红书笔记 / 发布到小红书 /
  更新小红书笔记 / 删掉小红书笔记 / publish to Xiaohongshu / post a RedNote /
  edit my xiaohongshu note. Do NOT use for 评论、私信、点赞、收藏与涨粉运营，
  不用于笔记配图生成与修图，也不用于微博、B 站、抖音等其他平台发布。
description_zh: 小红书笔记草稿、发布、编辑、删除，基于 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to www.xiaohongshu.com and valid session credentials in environment variables. Python 3.8+.
tags: [xiaohongshu, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 小红书 Publisher

小红书发布客户端，基于小红书 Web 内部接口（无公开 API）。

## 功能

- `draft-save` —— 保存草稿，返回 note_id
- `publish` —— 发布笔记
- `edit` —— 编辑已发布笔记
- `delete` —— 删除笔记

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：`XHS_COOKIE` 环境变量或 `--cookie-file`

## 使用示例

```bash
export XHS_COOKIE="xhs_track=xxx; a1=xxx; web_session=xxx; ..."
python xiaohongshu_publisher.py draft-save --execute \
  --title "我的笔记" \
  --content "正文内容..." \
  --tags "Python,AI" \
  --images "https://example.com/img1.png,https://example.com/img2.png" \
  --cover-image "https://example.com/cover.png"

python xiaohongshu_publisher.py publish --execute <note_id>

python xiaohongshu_publisher.py edit --execute <note_id> \
  --title "更新标题" \
  --content "更新内容..."
```

## 端点核对（首次使用必做）

小红书无公开 API，端点可能随时变更。首次使用前请在浏览器 DevTools 核对。

当前端点（需核对）：
- 草稿保存: `POST https://www.xiaohongshu.com/api/sns/web/v1/note/create`
- 发布: `POST https://www.xiaohongshu.com/api/sns/web/v1/note/publish`
- 编辑: `POST https://www.xiaohongshu.com/api/sns/web/v1/note/update`
- 删除: `POST https://www.xiaohongshu.com/api/sns/web/v1/note/delete`

## 认证

`XHS_COOKIE` — 包含 `xhs_track`、`a1`、`web_session` 等字段

```bash
export XHS_COOKIE="xhs_track=xxx; a1=xxx; web_session=xxx; ..."
```

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库
- `publish_common`

## 相关技能

- `weibo-publisher` — 微博发布
- `bilibili-publisher` — B 站发布
- `toutiao-publisher` — 今日头条发布
- `cross-post-orchestrator` — 多平台编排