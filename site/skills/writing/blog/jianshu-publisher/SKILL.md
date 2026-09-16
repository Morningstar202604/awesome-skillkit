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

# 简书发布客户端

简书发布/管理自动化客户端，基于简书 Web 端内部接口（无公开 API）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 子命令 | 是 | `draft-save` / `publish` / `edit` / `delete`（无 list/分类查询子命令） |
| Cookie | 是 | 环境变量 `JIANSHU_COOKIE` 或 `--cookie-file` 二选一 |
| 文章标题 | draft-save/edit 时必需 | `--title` |
| 正文 | draft-save/edit 时必需 | `--markdown`（文本）或 `--markdown-file`（文件）二选一 |
| `note_id` | publish/edit/delete 时必需 | draft-save 返回的草稿 ID |
| `--execute` | 否 | 不加则 dry-run，只打印请求计划不联网 |

缺输入时一次性问齐（不要分多轮追问）：
"请提供：① Cookie（环境变量 `JIANSHU_COOKIE` 或 Cookie 文件路径）；② 子命令；③ 若存草稿/编辑：标题与 Markdown 正文（文件或文本）。注意：本脚本不支持列出文章列表与专题投稿，需要时告知用户去简书后台操作。"

## 前置自检

依次执行，任一失败 → 按提示修复后 STOP，不要继续：

```bash
# 1. Python 3 与脚本就位
python3 --version && test -f scripts/jianshu_publisher.py && echo OK
# 预期：Python 3.x + OK；失败 → 安装 Python 3.8+ / cd 到本技能目录

# 2. publish_common 可导入（打包后与技能目录平级的 _common/）
python3 -c "import sys; sys.path.insert(0, '../_common'); import publish_common; print('OK')"
# 预期：OK；失败 → 确认 _common/publish_common.py 存在

# 3. Cookie 在且非空
test -n "$JIANSHU_COOKIE" || test -f ~/.jianshu_cookie && echo OK
# 预期：OK；失败 → 让用户提供简书登录态 Cookie（含 remember_user_token、_m7e_session 等字段），写入环境变量或文件，绝不入库

# 4. 端点已核对（首次使用必做，见下文"端点核对"）
# 预期：已按 DevTools 流程核对过 ENDPOINTS；未核对 → 先完成核对再执行写操作
```

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

## 工作流

发布一篇新文章按以下 4 步执行；编辑/删除已有文章直接用对应子命令，同样遵守 dry-run 默认。

### 步骤 1：保存草稿

- **动作**：`python jianshu_publisher.py draft-save --execute --title "标题" --markdown "# 正文..." --brief "摘要" --tags "A,B"`（也可用 `--markdown-file article.md`）。
- **预期**：退出码 0，返回 JSON 中含 `note_id`（草稿 ID），记录它供后续步骤使用。
- **若失败**：先跑一次不带 `--execute` 的 dry-run 核对请求计划；payload 结构与"端点核对"中 DevTools 观察到的不一致 → 修 `ENDPOINTS`/payload 后重试。

### 步骤 2：发布草稿

- **动作**：`python jianshu_publisher.py publish --execute <note_id>`
- **预期**：退出码 0，API 返回成功；文章在简书后台可见。
- **若失败**：退出码 1 → 读 stdout 中的 API 错误信息对照"失败处置表"；确认 `<note_id>` 是步骤 1 返回的真实 ID。

### 步骤 3：复核发布结果

- **动作**：GET `https://www.jianshu.com/notes/<note_id>`（或让用户在简书后台确认）。
- **预期**：能访问且内容与提交一致。
- **若失败**：404 → 发布实际未成功，回步骤 2 排查；不要重复发布造成多篇重复文章。

### 步骤 4：后续维护（按需）

- **动作**：编辑用 `edit --execute <note_id> --markdown-file article.md --title "新标题" --tags "A,B"`；删除用 `delete --execute <note_id>`（不可逆，执行前向用户确认）。
- **预期**：退出码 0；编辑后复核内容已更新，删除后原链接不再可访问。
- **若失败**：退出码 1 + API 错误 → Cookie 失效或端点变更，按"失败处置表"处置。

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

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| 子命令 | `draft-save` / `publish` / `edit` / `delete` | 见"功能"节 |
| `--cookie` | Cookie 字符串 | 优先用 `--cookie-file`，避免进 shell 历史 |
| `--cookie-file` | Cookie 文件路径 | 如 `~/.jianshu_cookie` |
| `--execute` | 开关 | 缺省 dry-run 只打印请求计划 |
| `--title` | 字符串 | draft-save/edit 需要 |
| `--markdown` / `--markdown-file` | 文本 / 路径 | 正文二选一 |
| `--brief` | 字符串 | 文章摘要（draft-save） |
| `--tags` | 逗号分隔 | 如 `Python,AI` |
| `--cover-image` | URL | 封面图（draft-save） |
| `<note_id>` | 位置参数 | publish/edit/delete 的目标文章 ID |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| 退出码 1 + API 错误 | Cookie 失效或未登录 | 重新获取登录态 Cookie（含 `remember_user_token`、`_m7e_session`），更新环境变量/文件 |
| 退出码 1 + 参数错误 | 参数拼写/缺漏 | 对照"参数速查表"修正；dry-run 先核对请求计划 |
| 请求 404/405 | 端点已变更 | 回"端点核对"流程，按 DevTools 实测更新 `ENDPOINTS` 常量 |
| publish/edit/delete 报文章不存在 | `<note_id>` 错误 | 用 draft-save 实际返回的 note_id，不要猜 |
| dry-run 输出的 payload 与预期不符 | 参数传入方式有误 | 修正参数后重跑 dry-run，确认再 `--execute` |
| `ModuleNotFoundError: publish_common` | `_common/` 缺失或不在搜索路径 | 确认与技能目录平级的 `_common/publish_common.py` 存在并可导入 |

## 交付标准

- **成功定义**：写操作在 `--execute` 下退出码 0 且步骤 3 复核通过；dry-run 模式下交付物为完整请求计划。
- **产物命名**：结果原样保存脚本 stdout JSON（如 `jianshu_draft_result.json`）；草稿期记录 `note_id`。
- **保存位置**：当前工作目录；Cookie 永远只在环境变量或用户目录的 Cookie 文件（如 `~/.jianshu_cookie`），绝不写入仓库。
- **完整性验证**：GET 文章链接可访问且内容与提交一致；删除后原链接不再可访问。

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