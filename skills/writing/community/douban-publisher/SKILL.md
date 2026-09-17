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
compatibility: Requires network access to www.douban.com and valid session credentials in environment variables. Python 3.8+.
tags: [douban, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 豆瓣发布客户端

基于豆瓣 Web 内部接口发布日记、广播与小组话题；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/community/douban-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `note-create`（日记）、`status-post`（广播）、`group-topic`（小组话题）三选一 |
| `--title` | note-create / group-topic 必需 | 日记或话题标题 |
| `--content` | 是 | 正文，纯文本 |
| `--privacy` | note-create 可选 | 可见范围：`0`=公开 / 其他取值见平台；VERIFY BEFORE USE |
| `<group_id>` | group-topic 必需 | 小组 ID，作为位置参数传入（如 `123456`） |
| `DOUBAN_COOKIE` 或 `--cookie-file` | 是 | 登录态凭据，二选一 |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 要发日记 / 广播 / 小组话题？(2) 标题与正文？(3) 若是日记，可见范围？(4) 若是小组话题，小组 ID？(5) Cookie 已设为 `DOUBAN_COOKIE` 还是用 `--cookie-file` 指定文件？

## 前置自检

1. **Python**：`python3 --version` —— 预期输出含 `3.8` 及以上；若报错或低于 3.8 → 安装 Python 3.8+，STOP。
2. **脚本**：`test -f douban_publisher.py && echo OK` —— 预期 `OK`；若不存在 → 仓库损坏，STOP。
3. **凭据**：`test -n "$DOUBAN_COOKIE" -o -f ~/.douban_cookie && echo OK` —— 预期 `OK`；否则 STOP，提示设置 `export DOUBAN_COOKIE=...` 或后续用 `--cookie-file`。

任一失败即 STOP，修复后再继续；前置全绿才进入工作流。

## 工作流

### 步骤 1：注入凭据

- **动作**：`export DOUBAN_COOKIE="dbcl2=xxx; ck=xxx; ..."`（或后续命令加 `--cookie-file ~/.douban_cookie`）。
- **预期**：`echo "$DOUBAN_COOKIE"` 非空；dry-run 阶段不会校验，但 `--execute` 前必须就位。
- **若失败**：未设置 → 脚本报凭据缺失类错误并退出码 1；STOP 并补齐凭据。

### 步骤 2：dry-run 预览（默认，不联网）

- **动作**：`python douban_publisher.py note-create --title "我的日记" --content "日记内容..." --privacy 0`
- **预期**：打印请求计划（method / url / body），**不发生任何网络请求**。
- **若失败**：参数错误 → 退出码 1 并提示缺字段；按提示补齐后重跑本步。

### 步骤 3：--execute 真正发布

- **动作**：在步骤 2 命令后追加 `--execute`。
- **预期**：退出码 `0`，输出创建结果（含日记/广播/话题的标识或链接）。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 4：核对返回

- **动作**：读取上一步输出的链接/ID，在浏览器打开确认。
- **预期**：目标内容已可见。
- **若失败**：返回成功但页面不可见 → Cookie 失效或被风控；刷新 `DOUBAN_COOKIE` 后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `note-create` | `--title --content --privacy --execute` | 创建日记 |
| `status-post` | `--content --execute` | 发布广播 |
| `group-topic <group_id>` | `--title --content --execute` | 在指定小组发话题 |
| （通用） | `--cookie-file <path>` | 用文件替代 `DOUBAN_COOKIE` 环境变量 |

## 端点核对（VERIFY BEFORE USE）

豆瓣无公开 API（早期 OAuth API 已停止维护），端点可能随时变更。首次使用必须按 SKILL.md 在浏览器 DevTools 核对下列端点：

- 创建日记：`POST https://www.douban.com/j/note/new`
- 发布广播：`POST https://www.douban.com/j/status/new`
- 小组话题：`POST https://www.douban.com/j/group/topic/new`

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--title` / `--content` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Cookie 失效或端点变更 | 刷新 `DOUBAN_COOKIE`；按 DevTools 更新端点常量 |
| 端点返回 4xx/5xx | 端点已被豆瓣调整 | 重核对端点，更新脚本顶部常量 |
| 登录态过期 / 提示登录后可见 | Cookie 超时或被风控清除 | 重新导出 `DOUBAN_COOKIE` 后重跑；先 dry-run 验证再 `--execute` |
| 日记保存成功但列表里看不到 | 误选了「仅自己可见」 | 改 `--privacy` 为公开，或在网页端修改可见范围 |
| 小组发帖被判定为广告 | 新号或正文含外链、联系方式 | 删去外链与推广话术，改用小组长文或稍后重试 |

## 交付标准

- **成功定义**：退出码 `0` 且输出含目标 URL / ID。
- **产物**：发布后的日记、广播或小组话题链接。
- **保存位置**：不落本地文件；发布结果以链接形式回传用户。
- **完整性验证**：浏览器打开链接，确认内容可见、格式正确。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：`DOUBAN_COOKIE` 环境变量或 `--cookie-file`，**绝不入库、绝不写入仓库**。
- 端点 VERIFY BEFORE USE：发布前在 DevTools 核对，勿轻信文档中的端点。
- 不可逆操作前确认：小组话题一经发布即公开，先 dry-run 展示计划，用户确认后再 `--execute`。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`）。

## 参考

- 本技能为纯提示型，无需外部参考文件。
