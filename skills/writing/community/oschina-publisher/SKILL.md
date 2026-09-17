---
name: oschina-publisher
description: >
  开源中国（OSChina）发布客户端，双模式：博客发布走官方开放平台 API
  （需 OSCHINA_ACCESS_TOKEN，必填 --catalog 分类 ID，可带标签）；
  提问与发动态走 Web 内部 API（需 OSCHINA_COOKIE 或 --cookie-file，动态可带图片）。
  所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送；
  Web 端点标注 VERIFY BEFORE USE，需按 SKILL.md 在浏览器 DevTools 核对。
  Use when the user asks to 发开源中国博客 / 发布到 OSChina / 在开源中国提问 /
  发开源中国动态 / publish a blog on OSChina / post an oschina question /
  create an oschina dynamic. Do NOT use for Gitee 码云的代码托管、Issue 与 PR 操作，
  不用于软件下载与资讯抓取，也不用于 CSDN、SegmentFault、V2EX 等其他技术社区发布。
description_zh: 开源中国博客发布、问答、动态发布，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to my.oschina.net and valid session credentials in environment variables. Python 3.8+.
tags: [oschina, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 开源中国发布客户端

双模式发布客户端：博客走官方开放平台 API，问答/动态走 Web 内部接口；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/community/oschina-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `blog-publish`（官方 API）/ `question-ask`（Web）/ `dynamic-post`（Web） |
| `--title` | blog-publish / question-ask 必需 | 标题 |
| `--content` | 是 | 正文，支持 Markdown |
| `--catalog` | blog-publish 必需 | 博客分类 ID（官方 API 必填） |
| `--tags` | 可选 | 逗号分隔标签，如 `"Python,AI"` |
| `--images` | dynamic-post 可选 | 图片 URL，可多个逗号分隔 |
| `OSCHINA_ACCESS_TOKEN` | blog-publish 必需 | 官方 API 凭据 |
| `OSCHINA_COOKIE` 或 `--cookie-file` | question-ask / dynamic-post 必需 | Web 内部接口凭据 |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 发博客 / 提问 / 发动态？(2) 标题与正文？(3) 博客需提供 `--catalog` 分类 ID，动态可带 `--images`？(4) 凭据用 `OSCHINA_ACCESS_TOKEN`（博客）还是 `OSCHINA_COOKIE` / `--cookie-file`（问答/动态）？

## 前置自检

1. **Python**：`python3 --version` —— 预期 `3.8` 及以上；否则安装 Python 3.8+，STOP。
2. **脚本**：`test -f oschina_publisher.py && echo OK` —— 预期 `OK`；否则仓库损坏，STOP。
3. **凭据**：
   - 博客：`test -n "$OSCHINA_ACCESS_TOKEN" && echo OK` —— 否则 STOP，提示设置 `OSCHINA_ACCESS_TOKEN`。
   - 问答/动态：`test -n "$OSCHINA_COOKIE" -o -f ~/.oschina_cookie && echo OK` —— 否则 STOP，提示设置 `OSCHINA_COOKIE` 或后续用 `--cookie-file`。

任一失败即 STOP，修复后再继续。

## 工作流

### 步骤 1：注入凭据

- **动作**：`export OSCHINA_ACCESS_TOKEN="your_token"`（博客）或 `export OSCHINA_COOKIE="your_cookie"`（问答/动态）；或后续命令加 `--cookie-file ~/.oschina_cookie`。
- **预期**：对应环境变量非空。
- **若失败**：未设置 → 退出码 1 报凭据缺失；STOP 并补齐。

### 步骤 2：dry-run 预览（默认，不联网）

- **动作**：`python oschina_publisher.py blog-publish --title "我的博客" --content "# 标题\n正文内容..." --tags "Python,AI" --catalog 123`
- **预期**：打印请求计划（method / url / body），**不发生网络请求**。
- **若失败**：参数错误 → 退出码 1 提示缺字段（如缺 `--catalog`）；补齐后重跑。

### 步骤 3：--execute 真正发布

- **动作**：在步骤 2 命令后追加 `--execute`。
- **预期**：退出码 `0`，输出创建结果（含文章/问题/动态标识或链接）。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 4：核对返回

- **动作**：打开输出链接确认内容。
- **预期**：目标内容可见。
- **若失败**：返回成功但不可见 → Cookie/Token 失效；刷新凭据后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `blog-publish` | `--title --content --catalog --tags --execute` | 官方 API 发布博客（`--catalog` 必填） |
| `question-ask` | `--title --content --tags --execute` | Web 内部接口提问 |
| `dynamic-post` | `--content --images --execute` | Web 内部接口发动态（可带图） |
| （通用） | `--cookie-file <path>` | 用文件替代 `OSCHINA_COOKIE` |

## 端点核对（VERIFY BEFORE USE）

Web 内部 API 无官方文档，端点可能随时变更。首次使用必须按 SKILL.md 在浏览器 DevTools 核对：

- 博客发布：`POST https://www.oschina.net/action/openapi/blog/add`
- 提问：`POST https://www.oschina.net/action/api/question/add`
- 动态：`POST https://www.oschina.net/action/api/dynamic/add`

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--title` / `--catalog` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Token/Cookie 失效或端点变更 | 刷新 `OSCHINA_ACCESS_TOKEN`/`OSCHINA_COOKIE`；重核端点 |
| 端点返回 4xx/5xx | Web 端点已调整 | 按 DevTools 更新端点常量 |
| 博客发布返回分类不存在 | `--catalog` 传了其他账号的 category ID | 调分类查询接口取本账号 ID，重跑 dry-run 后发布 |
| 提问被拒绝，提示等级不足 | 新账号或权限不够 | 先在社区完成基础互动，等权限放开再发 |
| 动态带图上传失败 | 图片超过平台体积或格式限制 | 压缩为 JPG 并小于限制体积后重传 |

## 交付标准

- **成功定义**：退出码 `0` 且输出含目标 URL / ID。
- **产物**：发布后的博客、问题或动态链接。
- **保存位置**：不落本地文件，链接回传用户。
- **完整性验证**：浏览器打开链接确认可见、格式正确。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：Token/Cookie 走环境变量或 `--cookie-file`，**绝不入库、绝不写入仓库**。
- 端点 VERIFY BEFORE USE：Web 端点发布前在 DevTools 核对。
- 不可逆操作前确认：先 dry-run 展示计划，用户确认后再 `--execute`。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`）。

## 参考

- 本技能为纯提示型，无需外部参考文件。
