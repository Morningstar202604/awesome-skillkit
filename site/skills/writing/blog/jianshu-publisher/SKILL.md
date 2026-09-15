---
name: jianshu-publisher
description: >
  简书文章发布与管理客户端，基于 www.jianshu.com Web 端内部接口（简书无公开开放 API）。
  支持保存草稿（返回 note_id）、发布指定草稿、编辑已发布文章、删除文章。
  Cookie 从环境变量 JIANSHU_COOKIE 或 --cookie-file 读取，绝不入库；
  所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送；
  端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发简书 / 发一篇简书文章 / 发布到简书 / 更新简书文章 /
  删除简书文章 / 存简书草稿 / publish to Jianshu / post an article on Jianshu /
  edit my Jianshu note. Do NOT use for 列出文章列表、专题投稿与分类查询
  （脚本未提供子命令），不用于公众号、知乎、掘金、CSDN 等其他平台发布，
  也不用于正文写作、排版与配图生成。
description_zh: 简书文章发布、编辑、删除、草稿箱管理，基于 Web 端内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to www.jianshu.com and valid session credentials in environment variables. Python 3.8+.
tags: [jianshu, blog, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 简书 Publisher

简书发布/管理自动化客户端，基于简书 Web 端内部接口（无公开 API）。

## 功能

- `draft-save` —— 保存草稿，返回 note_id
- `publish` —— 发布草稿
- `edit` —— 编辑已发布文章
- `delete` —— 删除文章

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：Cookie 从环境变量 `JIANSHU_COOKIE` 或 `--cookie-file` 读取，绝不写入代码仓库。
- **端点声明**：所有端点在 `ENDPOINTS` 常量中集中维护，标注 `VERIFY BEFORE USE`。

## 使用示例

```bash
# 1. 保存草稿
export JIANSHU_COOKIE="your_cookie_here"
python jianshu_publisher.py draft-save --execute \
  --title "我的新文章" \
  --markdown "# 标题\n内容..." \
  --brief "文章摘要" \
  --tags "Python,AI" \
  --cover-image "https://example.com/cover.png"

# 2. 发布草稿（拿到 draft-save 返回的 note_id）
python jianshu_publisher.py publish --execute <note_id>

# 3. 编辑已发布文章
python jianshu_publisher.py edit --execute <note_id> \
  --markdown-file article.md \
  --title "更新后的标题" \
  --tags "Python,AI"

# 4. 删除文章
python jianshu_publisher.py delete --execute <note_id>
```

## 端点核对（首次使用必做）

简书无公开 API，端点可能随时变更。首次使用前请按以下步骤核对：

1. 打开浏览器 DevTools（F12），切到 Network 标签
2. 在 www.jianshu.com 登录并执行对应操作（新建草稿/发布/编辑/删除）
3. 观察 XHR 请求，确认：
   - Request URL 与 `ENDPOINTS` 中对应值一致
   - Request Method / Headers / Payload 结构一致
4. 如有出入，直接修改脚本顶部 `ENDPOINTS` 常量

当前端点（需核对）：
- draft_save: `POST https://www.jianshu.com/notes`
- publish: `PUT https://www.jianshu.com/notes/{note_id}/publish`
- edit: `PUT https://www.jianshu.com/notes/{note_id}`
- delete: `DELETE https://www.jianshu.com/notes/{note_id}`

## 认证

Cookie 从环境变量 `JIANSHU_COOKIE` 或 `--cookie-file` 读取。需包含简书登录态 Cookie（通常包含 `remember_user_token`、`_m7e_session` 等字段）。

```bash
export JIANSHU_COOKIE="remember_user_token=xxx; _m7e_session=xxx; ..."
# 或
python jianshu_publisher.py draft-save --cookie-file ~/.jianshu_cookie ...
```

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库（`argparse` `json` `os` `sys` `urllib`）
- `publish_common`（打包后与技能目录平级的 `_common/publish_common.py`；仓库内位于 `skills/writing/_common/`）

## 相关技能

- `cnblogs-skill` — 博客园发布
- `csdn-publisher` — CSDN 发布
- `wechat-mp-publisher` — 微信公众号发布
- `juejin-publisher` — 掘金发布
- `cross-post-orchestrator` — 多平台编排
- `ai-cover-generator` — AI 封面图生成