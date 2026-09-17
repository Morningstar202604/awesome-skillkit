---
name: baijiahao-publisher
description: >
  百家号（百度）发布客户端，基于官方开放平台 API。支持发布图文文章、发布视频
  （提交 video_url 与封面图）、保存草稿，三者均可带封面图、标签与类目 ID。
  凭据取自环境变量 BAIJIAHAO_ACCESS_TOKEN（或 APPID/APPSECRET 自行换取）；
  所有写操作默认 dry-run 只打印请求计划，加 --execute 才真正联网发送。
  Use when the user asks to 发百家号 / 发百家号文章 / 百家号发视频 /
  存百家号草稿 / publish to Baijiahao / post an article on Baijiahao /
  upload a video to Baijiahao. Do NOT use for 百度贴吧、百度知道与搜索 SEO 投放，
  不用于视频剪辑转码与素材下载，也不用于草稿定时发布、收益结算与数据看板查询。
description_zh: 百家号文章发布、视频发布、草稿箱管理，基于官方开放平台接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
compatibility: Requires network access to baijiahao.baidu.com and valid session credentials in environment variables. Python 3.8+.
tags: [baijiahao, publishing, automation, china-platform]
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 百家号发布客户端

基于百度百家号官方开放平台 API 发布图文、发布视频与保存草稿；默认 dry-run，确认后才真正联网。

所有命令在本技能 `scripts/` 目录内执行（先 `cd skills/writing/news/baijiahao-publisher/scripts`）。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 动作 | 是 | `article-publish`（图文）/ `video-publish`（视频）/ `draft-save`（草稿） |
| `--title` | 是 | 标题 |
| `--content` | article-publish / draft-save 必需 | 正文，支持 Markdown |
| `--cover-images` / `--cover-image` | 可选 | 封面图 URL（文章用复数，视频用单数） |
| `--tags` | 可选 | 逗号分隔标签，如 `"Python,AI"` |
| `--category-id` | 可选 | 类目 ID |
| `--video-url` | video-publish 必需 | 视频文件 URL（需公网可访问） |
| `--description` | video-publish 可选 | 视频描述 |
| `BAIJIAHAO_ACCESS_TOKEN` 或 `BAIJIAHAO_APPID`+`BAIJIAHAO_APPSECRET` | 是 | 凭据 |

缺任意必需项时一次性问齐：

> 请告诉我：(1) 发文章 / 发视频 / 存草稿？(2) 标题与正文/视频 URL？(3) 可选封面图、标签、类目 ID？(4) 凭据用 `BAIJIAHAO_ACCESS_TOKEN` 还是 `APPID`+`APPSECRET`？

## 前置自检

1. **Python**：`python3 --version` —— 预期 `3.8` 及以上；否则安装 Python 3.8+，STOP。
2. **脚本**：`test -f baijiahao_publisher.py && echo OK` —— 预期 `OK`；否则仓库损坏，STOP。
3. **凭据**：`test -n "$BAIJIAHAO_ACCESS_TOKEN" -o -n "$BAIJIAHAO_APPID" && echo OK` —— 否则 STOP，提示设置凭据。

任一失败即 STOP，修复后再继续。

## 工作流

### 步骤 1：注入凭据

- **动作**：`export BAIJIAHAO_ACCESS_TOKEN="your_token"`（或 `export BAIJIAHAO_APPID/BAIJIAHAO_APPSECRET` 自行实现 OAuth2 刷新）。
- **预期**：对应环境变量非空。
- **若失败**：未设置 → 退出码 1 报凭据缺失；STOP 并补齐。

### 步骤 2：dry-run 预览（默认，不联网）

- **动作**：`python baijiahao_publisher.py article-publish --title "我的文章" --content "# 标题\n正文内容..." --cover-images "https://example.com/cover.png" --tags "Python,AI" --category-id 1`
- **预期**：打印请求计划（method / url / body），**不发生网络请求**。
- **若失败**：参数错误 → 退出码 1 提示缺字段；补齐后重跑。

### 步骤 3：--execute 真正发布

- **动作**：在步骤 2 命令后追加 `--execute`。
- **预期**：退出码 `0`，输出发布结果（含文章/视频标识或链接）。
- **若失败**：API 错误 → 退出码 1；见「失败处置表」。

### 步骤 4：核对返回

- **动作**：打开百家号后台对应内容确认。
- **预期**：内容已发布/已存草稿。
- **若失败**：返回成功但不可见 → Token 失效；刷新凭据后重试。

## 参数速查表

| 命令 | 关键参数 | 说明 |
|------|----------|------|
| `article-publish` | `--title --content --cover-images --tags --category-id --execute` | 发布图文 |
| `video-publish` | `--title --description --video-url --cover-image --tags --category-id --execute` | 发布视频 |
| `draft-save` | `--title --content --execute` | 保存草稿 |
| （通用） | `--cookie-file` 不支持 | 百家号为官方 API，凭据仅走环境变量 |

## 端点

- 文章发布：`POST https://baijiahao.baidu.com/api/article/publish`
- 视频发布：`POST https://baijiahao.baidu.com/api/video/publish`
- 草稿保存：`POST https://baijiahao.baidu.com/api/article/draft/save`

## 失败处置表

| 现象 / 错误码 | 原因 | 处置 |
|---------------|------|------|
| 退出码 1 + 参数错误 | 缺 `--title` / `--content` / `--video-url` 等 | 补齐参数后重跑 dry-run |
| 退出码 1 + API 错误 | Token 失效或权限不足 | 刷新 `BAIJIAHAO_ACCESS_TOKEN`；核对账号权限 |
| 视频发布失败 | `video-url` 不可公网访问 | 改用公网可访问的 URL 后重试 |
| 审核不通过 | 命中平台敏感词或类目错配 | 改类目与措辞后重新提交，勿反复原样重试 |
| 封面图上传失败 | 图片尺寸/体积不符要求 | 按平台要求裁到规定比例并压缩后重传 |
| 文章仍在审核中无法再发 | 同一账号有进行中的审核任务 | 先查任务状态，等上一单出结果再提交 |

## 交付标准

- **成功定义**：退出码 `0` 且输出含内容标识或链接。
- **产物**：发布后的文章/视频链接或草稿 ID。
- **保存位置**：不落本地文件，链接回传用户。
- **完整性验证**：百家号后台确认内容可见、视频可播放。

## 安全红线

- 默认 dry-run：所有写操作不加 `--execute` 只打印请求计划，绝不联网。
- 凭据隔离：Token/APPID/APPSECRET 走环境变量，**绝不入库、绝不写入仓库**。
- 不可逆操作前确认：文章/视频一经发布即公开，先 dry-run 展示计划，用户确认后再 `--execute`。
- 不越界：不用于百度贴吧、百度知道、搜索 SEO 投放、视频转码与素材下载。

## 依赖

- Python 3.8+，标准库。
- `publish_common`（与技能目录平级的 `_common/publish_common.py`）。

## 参考

- 本技能为纯提示型，无需外部参考文件。
