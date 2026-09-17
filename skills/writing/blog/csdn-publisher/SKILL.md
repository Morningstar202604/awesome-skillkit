---
name: csdn-publisher
description: >
  CSDN 博客发布与管理客户端，基于 blog.csdn.net Web 端内部接口（CSDN 无公开开放 API）。
  支持拉取文章分类（取 category_id）、保存草稿、发布草稿、编辑已发布文章、
  删除文章（移入回收站）、分页列出我的文章。Cookie 从环境变量 CSDN_COOKIE
  或 --cookie-file 读取，绝不入库；所有写操作默认 dry-run 只打印请求计划，
  加 --execute 才真正联网发送；端点标注 VERIFY BEFORE USE，需按 SKILL.md 在
  浏览器 DevTools 核对。Use when the user asks to 发 CSDN / 发一篇 CSDN 博客 /
  发布到 CSDN / 更新 CSDN 文章 / 删除 CSDN 文章 / 列出我的 CSDN 文章 /
  publish to CSDN / post a CSDN blog / update my CSDN article.
  Do NOT use for 掘金、知乎、公众号、博客园等其他平台发布，不用于 CSDN 下载、
  问答、私信与粉丝运营，也不用于纯 Markdown 写作、排版润色与配图生成。
description_zh: CSDN 博客发布、编辑、删除、草稿箱管理，基于 Web 端内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to blog.csdn.net and valid session credentials in environment variables. Python 3.8+.
tags: [csdn, blog, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# CSDN 发布客户端

CSDN 博客发布/管理自动化客户端，基于 CSDN Web 端内部接口（无公开 API）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 子命令 | 是 | `categories` / `draft-save` / `publish` / `edit` / `delete` / `list` |
| Cookie | 是 | 环境变量 `CSDN_COOKIE` 或 `--cookie-file` 二选一 |
| 文章标题 | draft-save/publish/edit 时必需 | `--title` |
| 正文 | draft-save/publish/edit 时必需 | draft-save 与 publish 用 `--markdown`（文本）；edit 用 `--markdown-file`（文件路径） |
| `category_id` | draft-save/publish 时必需 | 先用 `categories` 子命令拉取 |
| 文章 ID | publish/edit/delete 时必需 | draft-save 返回的 article_id |
| `--execute` | 否 | 不加则 dry-run，只打印请求计划不联网 |

缺输入时一次性问齐（不要分多轮追问）：
"请提供：① Cookie（环境变量 `CSDN_COOKIE` 或 Cookie 文件路径）；② 子命令；③ 若发文：标题、Markdown 正文（文件或文本）、分类（没有 category_id 我先跑 categories 拉取）、tags。"

## 前置自检

依次执行，任一失败 → 按提示修复后 STOP，不要继续：

```bash
# 1. Python 3 与脚本就位
python3 --version && test -f scripts/csdn_publisher.py && echo OK
# 预期：Python 3.x + OK；失败 → 安装 Python 3.8+ / cd 到本技能目录

# 2. publish_common 可导入（打包后与技能目录平级的 _common/）
python3 -c "import sys; sys.path.insert(0, '../_common'); import publish_common; print('OK')"
# 预期：OK；失败 → 确认 skills/writing/_common/publish_common.py 存在

# 3. Cookie 在且非空
test -n "$CSDN_COOKIE" || test -f ~/.csdn_cookie && echo OK
# 预期：OK；失败 → 让用户提供登录态 Cookie（含 uuid_tt_dd、UserIdentity 等字段），写入环境变量或文件，绝不入库

# 4. 端点已核对（首次使用必做，见下文"端点核对"）
# 预期：已按 DevTools 流程核对过 ENDPOINTS；未核对 → 先完成核对再执行写操作
```

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

## 工作流

发布一篇新文章按以下 4 步执行；编辑/删除已有文章直接用对应子命令，同样遵守 dry-run 默认。

### 步骤 1：拉取分类

- **动作**：`python csdn_publisher.py categories --execute`
- **预期**：退出码 0，stdout 输出 JSON 分类列表，从中取目标分类的 `category_id`（如示例中的 `109265`）。
- **若失败**：退出码 1 且报 API 错误 → Cookie 失效或端点变更，回"端点核对"流程确认，必要时让用户重新提供登录态 Cookie。

### 步骤 2：保存草稿

- **动作**：`python csdn_publisher.py draft-save --execute --title "标题" --markdown "# 正文..." --brief "摘要" --category-id "<步骤1取的id>" --tags "A,B"`（draft-save/publish 只接受 `--markdown`；`--markdown-file` 仅 edit 子命令支持）。
- **预期**：退出码 0，返回 JSON 中含 `article_id`（草稿 ID），记录它供步骤 3 使用。
- **若失败**：先跑一次不带 `--execute` 的 dry-run 核对请求计划；payload 结构与"端点核对"中 DevTools 观察到的不一致 → 修 `ENDPOINTS`/payload 后重试。

### 步骤 3：发布草稿

- **动作**：`python csdn_publisher.py publish --execute <article_id> --title "标题" --markdown "# 正文..." --brief "摘要" --category-id "<id>" --tags "A,B"`
- **预期**：退出码 0，API 返回成功；文章在 CSDN 后台可见。
- **若失败**：退出码 1 → 读 stdout 中的 API 错误信息对照"失败处置表"；确认 `<article_id>` 是步骤 2 返回的真实 ID。

### 步骤 4：复核发布结果

- **动作**：`python csdn_publisher.py list --execute --page 1 --size 20` 查看文章列表，确认新文章标题/ID 在列。
- **预期**：列表中出现刚发布的文章 ID 与标题。
- **若失败**：列表中没有 → 用 `list` 的分页参数翻查；仍无 → 发布实际未成功，回步骤 3 排查，不要重复发布造成多篇文章。

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

## 参数速查表

| 参数 | 取值 | 说明 |
|------|------|------|
| 子命令 | `categories` / `draft-save` / `publish` / `edit` / `delete` / `list` | 见"功能"节 |
| `--cookie` | Cookie 字符串 | 优先用 `--cookie-file`，避免进 shell 历史 |
| `--cookie-file` | Cookie 文件路径 | 如 `~/.csdn_cookie` |
| `--execute` | 开关 | 缺省 dry-run 只打印请求计划 |
| `--title` | 字符串 | draft-save/publish/edit 需要 |
| `--markdown` | 文本 | 正文（draft-save / publish 使用，必填） |
| `--markdown-file` | 文件路径 | 正文文件（edit 使用，必填） |
| `--brief` | 字符串 | 文章摘要（draft-save/publish） |
| `--category-id` | 字符串 | `categories` 拉取到的分类 ID（draft-save/publish） |
| `--tags` | 逗号分隔 | 如 `Python,AI` |
| `--cover-image` | URL | 封面图（draft-save） |
| `<article_id>` | 位置参数 | publish/edit/delete 的目标文章 ID |
| `--page` / `--size` | 整数 | list 分页 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| 退出码 1 + API 错误 | Cookie 失效或未登录 | 重新获取登录态 Cookie（含 `uuid_tt_dd`、`UserIdentity`），更新环境变量/文件 |
| 退出码 1 + 参数错误 | 参数拼写/缺漏 | 对照"参数速查表"修正；dry-run 先核对请求计划 |
| 请求 404/405 | 端点已变更 | 回"端点核对"流程，按 DevTools 实测更新 `ENDPOINTS` 常量 |
| publish 报文章不存在 | `<article_id>` 错误 | 用 draft-save 实际返回的 article_id，不要猜 |
| dry-run 输出的 payload 与预期不符 | 参数传入方式有误 | 修正参数后重跑 dry-run，确认再 `--execute` |
| `ModuleNotFoundError: publish_common` | `_common/` 缺失或不在搜索路径 | 确认与技能目录平级的 `_common/publish_common.py` 存在并可导入 |

## 交付标准

- **成功定义**：写操作在 `--execute` 下退出码 0 且步骤 4 复核通过；dry-run 模式下交付物为完整请求计划。
- **产物命名**：发布结果原样保存脚本 stdout JSON（如 `csdn_publish_result.json`）；草稿期记录 `article_id`。
- **保存位置**：当前工作目录；Cookie 永远只在环境变量或用户目录的 Cookie 文件（如 `~/.csdn_cookie`），绝不写入仓库。
- **完整性验证**：`list --execute` 能查到目标文章；标题/正文与提交内容一致。

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

## 参考

- 本技能为纯提示型，无需外部参考文件。
