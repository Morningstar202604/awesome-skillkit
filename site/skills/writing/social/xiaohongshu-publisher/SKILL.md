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

# 小红书发布客户端

基于小红书 Web 内部接口管理笔记：保存草稿、发布、编辑、删除；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/social/xiaohongshu-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `draft-save` / `publish` / `edit` / `delete` |
| `--title` | draft-save / edit 必需 | 标题 |
| `--content` | draft-save / edit 必需 | 正文（`publish` / `delete` 不接收该参数，只需 `note_id`） |
| `--tags` | 可选 | 话题标签，逗号分隔，如 `"Python,AI"` |
| `--images` | draft-save / edit 可选 | 多图 URL，逗号分隔 |
| `--cover-image` | draft-save / edit 可选 | 封面图 URL |
| `<note_id>` | publish / edit / delete 必需 | 笔记 ID，作为位置参数 |
| `XHS_COOKIE` 或 `--cookie-file` | 是 | 登录态凭据 |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 存草稿 / 发布 / 编辑 / 删除？(2) 标题与正文、话题标签、配图？(3) 发布/编辑/删除需提供 `note_id`（草稿返回的）？(4) Cookie 已设为 `XHS_COOKIE` 还是用 `--cookie-file`？

## 前置自检

1. **Python**：`python3 --version` —— 预期 `3.8` 及以上；否则安装 Python 3.8+，STOP。
2. **脚本**：`test -f xiaohongshu_publisher.py && echo OK` —— 预期 `OK`；否则仓库损坏，STOP。
3. **凭据**：`test -n "$XHS_COOKIE" -o -f ~/.xhs_cookie && echo OK` —— 否则 STOP，提示设置 `XHS_COOKIE` 或后续用 `--cookie-file`。

任一失败即 STOP，修复后再继续。

## 工作流

### 步骤 1：注入凭据

- **动作**：`export XHS_COOKIE="xhs_track=xxx; a1=xxx; web_session=xxx; ..."`（或后续命令加 `--cookie-file ~/.xhs_cookie`）。
- **预期**：环境变量非空。
- **若失败**：未设置 → 退出码 1 报凭据缺失；STOP 并补齐。

### 步骤 2：dry-run 预览（默认，不联网）

- **动作**：`python xiaohongshu_publisher.py draft-save --title "我的笔记" --content "正文内容..." --tags "Python,AI" --images "https://example.com/img1.png,https://example.com/img2.png" --cover-image "https://example.com/cover.png"`
- **预期**：打印请求计划（method / url / body），**不发生网络请求**，草稿模式返回计划中的 `note_id`。
- **若失败**：参数错误 → 退出码 1 提示缺字段；补齐后重跑。

### 步骤 3：--execute 真正执行

- **动作**：在步骤 2 命令后追加 `--execute`；发布/编辑/删除用 `python xiaohongshu_publisher.py publish --execute <note_id>` 等。
- **预期**：退出码 `0`，输出执行结果（含笔记链接/状态）。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 4：核对返回

- **动作**：打开小红书笔记链接确认。
- **预期**：草稿/发布/编辑/删除状态符合预期。
- **若失败**：返回成功但不可见 → Cookie 失效；刷新 `XHS_COOKIE` 后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `draft-save` | `--title --content --tags --images --cover-image --execute` | 存草稿，返回 `note_id` |
| `publish <note_id>` | `--execute` | 发布草稿笔记 |
| `edit <note_id>` | `--title --content --tags --images --cover-image --execute` | 编辑已发布笔记（与 draft-save 同参数集） |
| `delete <note_id>` | `--execute` | 删除笔记 |
| （通用） | `--cookie-file <path>` | 用文件替代 `XHS_COOKIE` |

## 端点核对（VERIFY BEFORE USE）

小红书无公开 API，端点可能随时变更。首次使用必须按 SKILL.md 在浏览器 DevTools 核对：

- 草稿保存：`POST https://www.xiaohongshu.com/api/sns/web/v1/note/create`
- 发布：`POST https://www.xiaohongshu.com/api/sns/web/v1/note/publish`
- 编辑：`POST https://www.xiaohongshu.com/api/sns/web/v1/note/update`
- 删除：`POST https://www.xiaohongshu.com/api/sns/web/v1/note/delete`

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--title` / `--content` / `note_id` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Cookie 失效或端点变更 | 刷新 `XHS_COOKIE`；重核端点 |
| 端点返回 4xx/5xx | 端点已调整 | 按 DevTools 更新端点常量 |
| 发布后笔记仅自己可见 | 命中违规词或判定为疑似营销 | 改掉绝对化用词与导流话术后重发 |
| 多图上传中断 | 图片过大或上传超时 | 单张压缩到平台限制内并逐张上传 |
| 草稿未保存成功 | note_id 未返回，Cookie 已失效 | 刷新 `XHS_COOKIE` 后重新保存并确认返回 note_id |

## 交付标准

- **成功定义**：退出码 `0` 且输出含笔记 ID / 链接 / 状态。
- **产物**：草稿 `note_id` 或发布后的笔记链接。
- **保存位置**：不落本地文件，ID/链接回传用户。
- **完整性验证**：小红书 App/网页确认笔记状态正确。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：`XHS_COOKIE` 环境变量或 `--cookie-file`，**绝不入库、绝不写入仓库**。
- 端点 VERIFY BEFORE USE：发布前在 DevTools 核对。
- 不可逆操作前确认：发布/删除一经执行影响公开内容，先 dry-run 展示计划，用户确认后再 `--execute`。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`）。

## 参考

- 本技能为纯提示型，无需外部参考文件。
