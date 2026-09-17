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

# V2EX 发布客户端

基于 V2EX Web 内部接口创建主题、回复主题与查询节点；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/community/v2ex-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `topic-create`（建主题）/ `reply-create`（回复）/ `node-list`（查节点） |
| `--title` | topic-create 必需 | 主题标题 |
| `--content` | topic-create / reply-create 必需 | 正文 |
| `--node-id` | topic-create 必需 | 节点 ID；未知时先 `node-list` 查询 |
| `<topic_id>` | reply-create 必需 | 被回复主题 ID，作为位置参数（如 `12345`） |
| `V2EX_COOKIE` 或 `--cookie-file` | 写操作必需 | 登录态凭据（node-list 只读也可不带） |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 建主题 / 回复 / 查节点？(2) 标题与正文？(3) 建主题需 `--node-id`（不知道就先 `node-list`）？(4) 回复需主题 ID？(5) Cookie 已设为 `V2EX_COOKIE` 还是用 `--cookie-file`？

## 前置自检

1. **Python**：`python3 --version` —— 预期 `3.8` 及以上；否则安装 Python 3.8+，STOP。
2. **脚本**：`test -f v2ex_publisher.py && echo OK` —— 预期 `OK`；否则仓库损坏，STOP。
3. **凭据（写操作）**：`test -n "$V2EX_COOKIE" -o -f ~/.v2ex_cookie && echo OK` —— 否则 STOP，提示设置 `V2EX_COOKIE` 或后续用 `--cookie-file`。

任一失败即 STOP，修复后再继续。

## 工作流

### 步骤 1：查询节点 ID（如未知）

- **动作**：`python v2ex_publisher.py node-list --execute`
- **预期**：输出节点列表，含节点名与 `node_id`。
- **若失败**：退出码 1 → 网络或端点问题；见「失败处置表」。

### 步骤 2：注入凭据

- **动作**：`export V2EX_COOKIE="A2=xxx; PB3_SESSION=xxx; ..."`（或后续命令加 `--cookie-file ~/.v2ex_cookie`）。
- **预期**：环境变量非空。
- **若失败**：未设置 → 退出码 1 报凭据缺失；STOP 并补齐。

### 步骤 3：dry-run 预览（默认，不联网）

- **动作**：`python v2ex_publisher.py topic-create --title "我的主题" --content "正文内容..." --node-id 123`
- **预期**：打印请求计划（method / url / body），**不发生网络请求**。
- **若失败**：参数错误 → 退出码 1 提示缺 `--node-id` 等；补齐后重跑。

### 步骤 4：--execute 真正发布

- **动作**：在步骤 3 命令后追加 `--execute`。
- **预期**：退出码 `0`，输出创建结果（含主题链接/ID）。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 5：核对返回

- **动作**：打开输出链接确认主题/回复可见。
- **预期**：内容已发布。
- **若失败**：返回成功但不可见 → Cookie 失效；刷新 `V2EX_COOKIE` 后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `topic-create` | `--title --content --node-id --execute` | 创建主题（`--node-id` 必填） |
| `reply-create <topic_id>` | `--content --execute` | 回复指定主题 |
| `node-list` | `--execute` | 列出节点与 ID |
| （通用） | `--cookie-file <path>` | 用文件替代 `V2EX_COOKIE` |

## 端点核对（VERIFY BEFORE USE）

V2EX 无公开 API，端点可能随时变更。首次使用必须按 SKILL.md 在浏览器 DevTools 核对：

- 创建主题：`POST https://www.v2ex.com/api/topics/create`
- 创建回复：`POST https://www.v2ex.com/api/replies/create`
- 节点列表：`GET https://www.v2ex.com/api/nodes/show.json`

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--title` / `--node-id` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Cookie 失效或端点变更 | 刷新 `V2EX_COOKIE`；重核端点 |
| 端点返回 4xx/5xx | 端点已调整 | 按 DevTools 更新端点常量 |
| 发帖提示节点无效 | `--node-id` 用了节点名而非数字 ID | 用节点列表接口取数字 ID 后重试 |
| 新号发帖被限制 | 注册天数或活跃度不足 | 等账号满足发帖门槛，先回复积累活跃 |
| 被判定刷屏 / 重复搬运 | 短时间重复发同类主题 | 合并为一条主题或降低频率，勿跨节点重复发 |

## 交付标准

- **成功定义**：退出码 `0` 且输出含主题/回复链接或 ID。
- **产物**：发布后的主题或回复链接。
- **保存位置**：不落本地文件，链接回传用户。
- **完整性验证**：浏览器打开链接确认可见、格式正确。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：`V2EX_COOKIE` 环境变量或 `--cookie-file`，**绝不入库、绝不写入仓库**。
- 端点 VERIFY BEFORE USE：发布前在 DevTools 核对。
- 不可逆操作前确认：主题/回复一经发布即公开，先 dry-run 展示计划，用户确认后再 `--execute`。
- 禁止滥用：不用于节点收藏、感谢、私信、举报等互动，不批量抓取或搬运帖子。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`）。

## 参考

- 本技能为纯提示型，无需外部参考文件。
