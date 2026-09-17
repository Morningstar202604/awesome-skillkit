---
name: segmentfault-publisher
description: >
  SegmentFault（思否）发布客户端，基于 segmentfault.com Web 内部接口（无公开开放 API）。
  支持保存文章草稿（返回 article_id，可带摘要、标签与封面图）、直接发布文章、
  发布提问。Cookie 从环境变量 SF_COOKIE 或 --cookie-file 读取，绝不入库；
  所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送；
  端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发 SegmentFault / 发思否文章 / 在思否提问 /
  存 SegmentFault 草稿 / publish to SegmentFault / post an article on SegmentFault /
  ask a question on SegmentFault. Do NOT use for 回答已有问题、采纳答案与声望操作，
  不用于 SegmentFault 课程、招聘与问答悬赏功能，
  也不用于 V2EX、开源中国、CSDN 等其他技术社区发布。
description_zh: SegmentFault 文章草稿、发布、提问，基于 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to segmentfault.com and valid session credentials in environment variables. Python 3.8+.
tags: [segmentfault, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# SegmentFault 发布客户端

基于 SegmentFault Web 内部接口保存草稿、发布文章与提问；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/community/segmentfault-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `article-save`（草稿）/ `article-publish`（发布）/ `question-ask`（提问） |
| `--title` | 是 | 标题 |
| `--content` | 是 | 正文，支持 Markdown |
| `--summary` | article-save 可选 | 文章摘要 |
| `--tags` | 可选 | 逗号分隔标签，如 `"Python,AI"` |
| `--cover-image` | article-save 可选 | 封面图 URL |
| `SF_COOKIE` 或 `--cookie-file` | 是 | 登录态凭据 |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 存草稿 / 发布文章 / 提问？(2) 标题与正文？(3) 草稿可选摘要、标签、封面图？(4) Cookie 已设为 `SF_COOKIE` 还是用 `--cookie-file` 指定文件？

## 前置自检

1. **Python**：`python3 --version` —— 预期 `3.8` 及以上；否则安装 Python 3.8+，STOP。
2. **脚本**：`test -f segmentfault_publisher.py && echo OK` —— 预期 `OK`；否则仓库损坏，STOP。
3. **凭据**：`test -n "$SF_COOKIE" -o -f ~/.sf_cookie && echo OK` —— 否则 STOP，提示设置 `SF_COOKIE` 或后续用 `--cookie-file`。

任一失败即 STOP，修复后再继续。

## 工作流

### 步骤 1：注入凭据

- **动作**：`export SF_COOKIE="your_cookie"`（或后续命令加 `--cookie-file ~/.sf_cookie`）。
- **预期**：环境变量非空。
- **若失败**：未设置 → 退出码 1 报凭据缺失；STOP 并补齐。

### 步骤 2：dry-run 预览（默认，不联网）

- **动作**：`python segmentfault_publisher.py article-save --title "我的文章" --content "# 标题\n正文内容..." --summary "文章摘要" --tags "Python,AI" --cover-image "https://example.com/cover.png"`
- **预期**：打印请求计划（method / url / body），**不发生网络请求**。
- **若失败**：参数错误 → 退出码 1 提示缺字段；补齐后重跑。

### 步骤 3：--execute 真正发布

- **动作**：在步骤 2 命令后追加 `--execute`。
- **预期**：退出码 `0`，`article-save` 输出返回 `article_id`，发布/提问输出目标链接。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 4：核对返回

- **动作**：打开输出链接或凭 `article_id` 进入编辑器确认。
- **预期**：草稿/文章/问题可见。
- **若失败**：返回成功但不可见 → Cookie 失效；刷新 `SF_COOKIE` 后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `article-save` | `--title --content --summary --tags --cover-image --execute` | 存草稿，返回 `article_id` |
| `article-publish` | `--title --content --tags --execute` | 直接发布文章 |
| `question-ask` | `--title --content --tags --execute` | 发布提问 |
| （通用） | `--cookie-file <path>` | 用文件替代 `SF_COOKIE` |

## 端点核对（VERIFY BEFORE USE）

SegmentFault 无公开 API，端点可能随时变更。首次使用必须按 SKILL.md 在浏览器 DevTools 核对：

- 文章草稿：`POST https://segmentfault.com/api/articles/save`
- 文章发布：`POST https://segmentfault.com/api/articles/publish`
- 提问：`POST https://segmentfault.com/api/questions/ask`

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--title` / `--content` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Cookie 失效或端点变更 | 刷新 `SF_COOKIE`；重核端点 |
| 端点返回 4xx/5xx | 端点已调整 | 按 DevTools 更新端点常量 |
| 草稿保存成功但 article_id 为空 | 响应结构变更或未登录 | 确认 Cookie 有效并核对响应字段，必要时按 DevTools 更新解析 |
| 文章因重复被拦下 | 同标题/同正文近期已发 | 改标题与正文差异化，或改为更新已有文章 |
| 提问被判定不合规范 | 标题过于笼统或缺可复现代码 | 补最小可复现示例与明确标题后重新提交 |

## 交付标准

- **成功定义**：退出码 `0` 且输出含 `article_id`（草稿）或目标 URL。
- **产物**：草稿 ID 或发布后的文章/问题链接。
- **保存位置**：不落本地文件，ID/链接回传用户。
- **完整性验证**：浏览器打开链接，确认内容可见、格式正确。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：`SF_COOKIE` 环境变量或 `--cookie-file`，**绝不入库、绝不写入仓库**。
- 端点 VERIFY BEFORE USE：发布前在 DevTools 核对。
- 不可逆操作前确认：发布/提问一经提交即公开，先 dry-run 展示计划，用户确认后再 `--execute`。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`）。

## 参考

- 本技能为纯提示型，无需外部参考文件。
