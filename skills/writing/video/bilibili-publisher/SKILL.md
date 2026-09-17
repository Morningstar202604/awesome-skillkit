---
name: bilibili-publisher
description: >
  B 站（bilibili）发布客户端，双模式：专栏草稿保存、专栏发布与动态发布走 Web 内部 API
  （仅需 BILI_COOKIE 或 --cookie-file，加 --execute 即真实提交）；
  视频投稿走官方 API（需 BILI_ACCESS_KEY/BILI_SECRET_KEY 签名，脚本输出投稿参数计划，
  分片上传与断点续传需自行接入）。所有写操作默认 dry-run 只打印请求计划，
  加 --execute 才真正联网发送。Use when the user asks to 发 B 站 / 投稿 bilibili /
  上传视频到 B 站 / 发 B 站专栏 / 发 B 站动态 / publish to bilibili /
  upload video to bilibili / post a bilibili article.
  Do NOT use for 视频剪辑、压制、字幕与封面生成，不用于下载或搬运已有视频、
  不用于弹幕与评论管理，也不用于直播推流与开播设置。
description_zh: B 站视频投稿、专栏文章发布、动态发布，支持官方开放平台与 Web 内部接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to api.bilibili.com and valid session credentials in environment variables. Python 3.8+.
tags: [bilibili, video, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# B 站发布客户端

B 站发布客户端，双模式：1) 官方开放平台 API——视频上传/投稿，需申请 AppKey；2) Web 内部 API——专栏文章/动态发布，仅需 Cookie。

能力边界（零隐性假设）：`article-save` / `article-publish` / `dynamic-post` 加 `--execute` 会真实发送；`video-upload` / `video-submit` 即使加 `--execute` 也只打印请求计划（分片上传与签名鉴权需自行接入），不会真发。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `BILI_COOKIE` 环境变量或 `--cookie-file <path>` | Web 模式必需 | 需含 `SESSDATA`、`bili_jct`、`DedeUserID` 字段 |
| `BILI_ACCESS_KEY` + `BILI_SECRET_KEY` 环境变量 | `video-submit` 必需 | 官方 API 凭据；缺失时脚本直接退出并报「官方 API 需要 BILI_ACCESS_KEY 和 BILI_SECRET_KEY」 |
| `article-save --title` / `--content` | 是 | content 为 Markdown/HTML 字符串（非文件路径） |
| `article-save --summary / --category / --tags / --images` | 否 | 逗号分隔的图片 URL 列表 |
| `article-publish <article_id>` | 是 | article-save 或平台上拿到的专栏 ID |
| `dynamic-post --content` | 是 | 动态文本；`--images` 可选 |
| `video-submit --title` / `--tid` | 是 | tid 为分区 ID（整数） |
| `video-submit --tags / --source / --desc / --dynamic` | 否 | source 为转载来源 |

缺输入时一次性问齐：
「请一次性提供：① 发布类型（专栏草稿/专栏发布/动态/视频投稿）；② Cookie（BILI_COOKIE 或 cookie 文件路径）；③ 对应内容（标题、正文、图片 URL 等）。不逐条追问。」

## 前置自检

```bash
python3 --version                                   # 需 ≥ 3.8（仅标准库 + publish_common）
test -n "$BILI_COOKIE" && echo cookie-present       # Web 模式凭据（或确认 --cookie-file 存在）
test -n "$BILI_ACCESS_KEY" -a -n "$BILI_SECRET_KEY" && echo official-creds-present  # video-submit 前置
python3 bilibili_publisher.py article-save --title t --content c   # 不加 --execute，确认脚本能运行
```

任一失败 → 按上文「输入清单」补凭据/依赖 → 重跑，通过前 STOP，不进入执行步骤。

## 工作流

### 步骤 1：核对端点（首次使用必做）

动作：Web 内部 API 无官方文档，在浏览器 DevTools 核对下列端点（标注 VERIFY BEFORE USE，可能随时变更）：

- 视频上传凭证: `GET https://member.bilibili.com/x/web-interface/upload/pre`
- 视频分片上传: `POST https://member.bilibili.com/x/web-interface/upload/chunk`
- 视频完成上传: `POST https://member.bilibili.com/x/web-interface/upload/complete`
- 视频投稿: `POST https://member.bilibili.com/x/web-interface/archive/add`
- 专栏草稿: `POST https://api.bilibili.com/x/article/add`
- 专栏发布: `POST https://api.bilibili.com/x/article/publish`
- 动态发布: `POST https://api.bilibili.com/x/dynamic/publish`

预期：实测端点与脚本常量一致。
若失败：以 DevTools 实测结果更新 `scripts/bilibili_publisher.py` 顶部的端点常量。

### 步骤 2：dry-run 生成请求计划（默认）

```bash
export BILI_COOKIE="SESSDATA=xxx; bili_jct=xxx; DedeUserID=xxx; ..."
python3 bilibili_publisher.py article-save \
  --title "我的专栏文章" \
  --content "# 标题\n正文内容..." \
  --summary "文章摘要" \
  --category 0 \
  --tags "Python,AI" \
  --images "https://example.com/img1.png"
```

预期：输出 `[PLAN] POST <端点>` 与完整 payload JSON，无任何网络请求。
若失败：argparse 报缺少必填参数 → 按报错补参后重跑。

### 步骤 3：向用户展示计划并确认

动作：把 [PLAN] 输出原样展示给用户。
预期：用户明确同意后才追加 `--execute`。
若失败：用户不同意 → 修改参数回到步骤 2。

### 步骤 4：真实执行

```bash
python3 bilibili_publisher.py article-save --execute --title "..." --content "..."   # 草稿保存
python3 bilibili_publisher.py article-publish --execute <article_id>                  # 专栏发布
python3 bilibili_publisher.py dynamic-post --execute \
  --content "发个动态 #话题#" \
  --images "https://example.com/img1.png,https://example.com/img2.png"                # 动态发布
```

预期：打印平台 JSON 响应，`code` 为 0 表示成功；article-save 响应含新草稿 ID。
若失败：脚本抛 `bili code=<N> msg=<M>`（退出码 1）→ 对照下方失败处置表。

## 参数速查表

| 子命令 | 参数 | 说明 |
|--------|------|------|
| （全局） | `--cookie` / `--cookie-file` | Cookie 字符串或文件路径，二选一 |
| `video-upload <file>` | `--title` | 演示流程：打印分片上传三步计划，不真传 |
| `video-submit` | `--title`、`--tid`、`--tags`、`--source`、`--desc`、`--dynamic` | 官方 API；dry-run 打印投稿 payload |
| `article-save` | `--title`、`--content`、`--summary`、`--category`、`--tags`、`--images` | Web API 草稿保存 |
| `article-publish <article_id>` | — | Web API 专栏发布 |
| `dynamic-post` | `--content`、`--images` | Web API 动态发布 |
| 以上所有子命令 | `--execute` | 缺省 dry-run；加后才真发 |

## 退出码

- `0` 成功
- `1` API 错误（响应 code 非 0，抛 `bili code=<N>`）
- `2` argparse 参数错误

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| `SystemExit: 官方 API 需要 BILI_ACCESS_KEY 和 BILI_SECRET_KEY` | video-submit 缺官方凭据 | export 两个环境变量后重跑 |
| 输出以 `[PLAN]` 开头 | 未加 `--execute`（默认 dry-run） | 确认计划后加 `--execute` |
| `bili code=-101` 等 | Cookie 缺失或过期 | 重新从浏览器导出 Cookie（含 SESSDATA/bili_jct/DedeUserID） |
| `bili code=<N> msg=<M>` | 平台拒绝（风控/参数/权限） | 按 msg 修正参数；高频发布会被风控，拉开间隔 |
| `json.JSONDecodeError` | 响应非 JSON，多为端点变更或风控页 | 回到步骤 1 重新核对端点 |
| video 命令只打印 [PLAN] | 设计如此（分片/签名未接入） | 需真实投稿时自行接入签名鉴权与分片上传 |

## 交付标准

- 成功定义：目标命令以 `--execute` 运行且响应 JSON `code=0`。
- 产物命名：article-save 响应中的草稿 ID 用于后续 `article-publish`；动态/专栏无本地产物。
- 验证完整性：到 B 站对应页面（专栏草稿箱/动态）人工确认内容可见，或用响应 JSON 中的 ID 回查。

## 依赖

- Python 3.8+，标准库
- `publish_common`（打包后与技能目录平级的 `_common/publish_common.py`；仓库内位于 `skills/writing/_common/`）

## 相关技能

- `toutiao-publisher` — 今日头条/抖音发布
- `xiaohongshu-publisher` — 小红书发布
- `weibo-publisher` — 微博发布
- `cross-post-orchestrator` — 多平台编排

## 参考

- 本技能为纯提示型，无需外部参考文件。
