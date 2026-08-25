---
name: csdn-publisher
description: CSDN 博客发布/管理自动化（Web 内部 API）
description_zh: CSDN 博客发布、编辑、删除、草稿箱管理，基于 Web 端内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [csdn, blog, publishing, automation, china-platform]
metadata:
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# CSDN Publisher

CSDN 博客发布/管理自动化客户端，基于 CSDN Web 端内部接口（无公开 API）。

## 功能

- `categories` —— 拉取分类列表（用于获取 category_id）
- `draft-save` —— 保存草稿，返回 article_id
- `publish` —— 发布草稿
- `edit` —— 编辑已发布文章
- `delete` —— 删除文章（移至回收站）
- `list` —— 列出我的文章

## 安全设计

- **默认 dry-run**：所有写操作（draft-save/publish/edit/delete）默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：Cookie 从环境变量 `CSDN_COOKIE` 或 `--cookie-file` 读取，绝不写入代码仓库。
- **端点声明**：所有端点在 `ENDPOINTS` 常量中集中维护，标注 `VERIFY BEFORE USE`。

## 使用示例

```bash
# 1. 拉取分类（获取 category_id）
export CSDN_COOKIE="your_cookie_here"
python csdn_publisher.py categories --execute

# 2. 保存草稿
python csdn_publisher.py draft-save --execute \
  --title "我的新文章" \
  --markdown "# 标题\n内容..." \
  --brief "文章摘要" \
  --category-id "109265" \
  --tags "Python,AI" \
  --cover-image "https://example.com/cover.png"

# 3. 发布草稿（拿到 draft-save 返回的 article_id）
python csdn_publisher.py publish --execute 123456 \
  --title "我的新文章" \
  --markdown "# 标题\n内容..." \
  --brief "文章摘要" \
  --category-id "109265" \
  --tags "Python,AI"

# 4. 编辑已发布文章
python csdn_publisher.py edit --execute 123456 \
  --markdown-file article.md \
  --title "更新后的标题"

# 5. 删除文章
python csdn_publisher.py delete --execute 123456

# 6. 列出我的文章
python csdn_publisher.py list --execute --page 1 --size 20
```

## 端点核对（首次使用必做）

CSDN 无公开 API，端点可能随时变更。首次使用前请按以下步骤核对：

1. 打开浏览器 DevTools（F12），切到 Network 标签
2. 在 blog.csdn.net 登录并执行对应操作（新建草稿/发布/编辑/删除/列表）
3. 观察 XHR 请求，确认：
   - Request URL 与 `ENDPOINTS` 中对应值一致
   - Request Method / Headers / Payload 结构一致
4. 如有出入，直接修改脚本顶部 `ENDPOINTS` 常量

当前端点（需核对）：
- categories: `GET/POST https://blog.csdn.net/api/articles/category/list`
- draft_save: `POST https://blog.csdn.net/api/articles/save`
- publish: `POST https://blog.csdn.net/api/articles/publish`
- edit: `POST https://blog.csdn.net/api/articles/update`
- delete: `POST https://blog.csdn.net/api/articles/delete`
- list: `POST https://blog.csdn.net/api/articles/list`

## 认证

Cookie 从环境变量 `CSDN_COOKIE` 或 `--cookie-file` 读取。需包含 CSDN 登录态 Cookie（通常包含 `uuid_tt_dd`、`UserIdentity` 等字段）。

```bash
export CSDN_COOKIE="uuid_tt_dd=xxx; UserIdentity=xxx; ..."
# 或
python csdn_publisher.py draft-save --cookie-file ~/.csdn_cookie ...
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
- `wechat-mp-publisher` — 微信公众号发布
- `juejin-publisher` — 掘金发布
- `cross-post-orchestrator` — 多平台编排
- `ai-cover-generator` — AI 封面图生成