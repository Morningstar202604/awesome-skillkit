---
name: jianshu-publisher
description: 简书发布/管理自动化（Web 内部 API）
description_zh: 简书文章发布、编辑、删除、草稿箱管理，基于 Web 端内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [jianshu, blog, publishing, automation, china-platform]
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
- `publish_common`（同目录 `../../../_common/publish_common.py`）

## 相关技能

- `cnblogs-skill` — 博客园发布
- `csdn-publisher` — CSDN 发布
- `wechat-mp-publisher` — 微信公众号发布
- `juejin-publisher` — 掘金发布
- `cross-post-orchestrator` — 多平台编排
- `ai-cover-generator` — AI 封面图生成