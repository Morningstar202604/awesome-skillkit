---
name: toutiao-publisher
description: >
  今日头条发布客户端，双模式：文章发布走官方开放平台 API
  （需 TOUTIAO_ACCESS_TOKEN 或 TOUTIAO_APPID/APPSECRET，可带封面图与标签）；
  微头条发布走 Web 内部 API（需 TOUTIAO_COOKIE 或 --cookie-file，可带图片）。
  所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送；
  Web 端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发头条 / 发今日头条文章 / 发微头条 /
  发布到今日头条 / publish to Toutiao / post a Toutiao article /
  create a microblog on Toutiao. Do NOT use for 抖音与西瓜视频的短视频发布、
  不用于头条广告投放与收益提现，也不用于评论、私信与粉丝互动等操作。
description_zh: 今日头条文章发布、微头条发布，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to www.toutiao.com and valid session credentials in environment variables. Python 3.8+.
tags: [toutiao, douyin, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 今日头条/抖音发布客户端

双模式发布客户端：文章走官方开放平台 API，微头条走 Web 内部接口；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/news/toutiao-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `article-publish`（官方 API）/ `micro-post`（Web 内部接口） |
| `--title` | article-publish 必需 | 文章标题 |
| `--content` | 是 | 正文，支持 Markdown |
| `--cover-images` | article-publish 可选 | 封面图 URL，逗号分隔 |
| `--tags` | 可选 | 逗号分隔标签，如 `"Python,AI"` |
| `--images` | micro-post 可选 | 配图 URL，逗号分隔 |
| `TOUTIAO_ACCESS_TOKEN` 或 `TOUTIAO_APPID`+`TOUTIAO_APPSECRET` | article-publish 必需 | 官方 API 凭据 |
| `TOUTIAO_COOKIE` 或 `--cookie-file` | micro-post 必需 | Web 内部接口凭据 |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 发文章 / 发微头条？(2) 标题与正文？(3) 可选封面图/标签/配图？(4) 凭据用 `TOUTIAO_ACCESS_TOKEN`（文章）还是 `TOUTIAO_COOKIE` / `--cookie-file`（微头条）？

## 前置自检

1. **Python**：`python3 --version` —— 预期 `3.8` 及以上；否则安装 Python 3.8+，STOP。
2. **脚本**：`test -f toutiao_publisher.py && echo OK` —— 预期 `OK`；否则仓库损坏，STOP。
3. **凭据**：
   - 文章：`test -n "$TOUTIAO_ACCESS_TOKEN" -o -n "$TOUTIAO_APPID" && echo OK` —— 否则 STOP，提示设置凭据。
   - 微头条：`test -n "$TOUTIAO_COOKIE" -o -f ~/.toutiao_cookie && echo OK` —— 否则 STOP，提示设置 `TOUTIAO_COOKIE` 或后续用 `--cookie-file`。

任一失败即 STOP，修复后再继续。

## 工作流

### 步骤 1：注入凭据

- **动作**：`export TOUTIAO_ACCESS_TOKEN="your_token"`（文章）或 `export TOUTIAO_COOKIE="tt_webid=xxx; s_v_web_id=xxx; ..."`（微头条）；或微头条命令加 `--cookie-file ~/.toutiao_cookie`。
- **预期**：对应环境变量非空。
- **若失败**：未设置 → 退出码 1 报凭据缺失；STOP 并补齐。

### 步骤 2：dry-run 预览（默认，不联网）

- **动作**：`python toutiao_publisher.py article-publish --title "我的文章" --content "# 标题\n正文内容..." --cover-images "https://example.com/cover.png" --tags "Python,AI"`
- **预期**：打印请求计划（method / url / body），**不发生网络请求**。
- **若失败**：参数错误 → 退出码 1 提示缺字段；补齐后重跑。

### 步骤 3：--execute 真正发布

- **动作**：在步骤 2 命令后追加 `--execute`。
- **预期**：退出码 `0`，输出发布结果（含文章/微头条标识或链接）。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 4：核对返回

- **动作**：打开输出链接或头条后台确认。
- **预期**：内容已发布。
- **若失败**：返回成功但不可见 → Token/Cookie 失效；刷新凭据后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `article-publish` | `--title --content --cover-images --tags --execute` | 官方 API 发文章 |
| `micro-post` | `--content --images --execute` | Web 内部接口发微头条（可带图） |
| （通用） | `--cookie-file <path>` | 微头条用文件替代 `TOUTIAO_COOKIE` |

## 端点核对（VERIFY BEFORE USE）

Web 内部 API 无官方文档，端点可能随时变更。首次使用必须按 SKILL.md 在浏览器 DevTools 核对：

- 文章发布：`POST https://open.toutiao.com/api/articles/publish`
- 微头条：`POST https://www.toutiao.com/api/microblog/create`

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--title` / `--content` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Token/Cookie 失效或端点变更 | 刷新凭据；微头条重核端点 |
| 端点返回 4xx/5xx | Web 端点已调整 | 按 DevTools 更新端点常量 |

## 交付标准

- **成功定义**：退出码 `0` 且输出含内容标识或链接。
- **产物**：发布后的文章/微头条链接。
- **保存位置**：不落本地文件，链接回传用户。
- **完整性验证**：头条后台确认内容可见、配图正常。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：Token/Cookie 走环境变量或 `--cookie-file`，**绝不入库、绝不写入仓库**。
- 端点 VERIFY BEFORE USE：微头条 Web 端点发布前在 DevTools 核对。
- 不可逆操作前确认：先 dry-run 展示计划，用户确认后再 `--execute`。
- 不越界：不用于抖音/西瓜视频短视频、广告投放、收益提现、评论私信等互动。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`）。
