---
name: baijiahao-publisher
description: 百家号发布客户端（官方开放平台 API）
description_zh: 百家号文章发布、视频发布、草稿箱管理，基于官方开放平台接口
version: 1.0.0
author: skillkit authors
license: Apache-2.0
tags: [baijiahao, publishing, automation, china-platform]
---

# 百家号 Publisher

百家号发布客户端，基于百度百家号官方开放平台 API。

## 功能

- `article-publish` —— 发布文章
- `video-publish` —— 发布视频
- `draft-save` —— 保存草稿

## 安全设计

- **默认 dry-run**：所有写操作默认只打印请求计划，不联网；加 `--execute` 才真正发送。
- **凭据隔离**：`BAIJIAHAO_ACCESS_TOKEN` 或 `BAIJIAHAO_APPID`/`BAIJIAHAO_APPSECRET`

## 使用示例

```bash
export BAIJIAHAO_ACCESS_TOKEN="your_token"
python baijiahao_publisher.py article-publish --execute \
  --title "我的文章" \
  --content "# 标题\n正文内容..." \
  --cover-images "https://example.com/cover.png" \
  --tags "Python,AI" \
  --category-id 1

python baijiahao_publisher.py video-publish --execute \
  --title "我的视频" \
  --description "视频描述" \
  --video-url "https://example.com/video.mp4" \
  --cover-image "https://example.com/cover.png" \
  --tags "Python,AI" \
  --category-id 1

python baijiahao_publisher.py draft-save --execute \
  --title "草稿标题" \
  --content "# 标题\n正文..."
```

## 认证

- `BAIJIAHAO_ACCESS_TOKEN` — 直接使用 access_token
- 或 `BAIJIAHAO_APPID` + `BAIJIAHAO_APPSECRET` — 需自行实现 OAuth2 刷新

```bash
export BAIJIAHAO_ACCESS_TOKEN="your_token"
# 或
export BAIJIAHAO_APPID="xxx"
export BAIJIAHAO_APPSECRET="xxx"
```

## 端点

- 文章发布: `POST https://baijiahao.baidu.com/api/article/publish`
- 视频发布: `POST https://baijiahao.baidu.com/api/video/publish`
- 草稿保存: `POST https://baijiahao.baidu.com/api/article/draft/save`

## 退出码

- `0` 成功
- `1` API 错误或参数错误

## 依赖

- Python 3.8+
- 标准库
- `publish_common`

## 相关技能

- `toutiao-publisher` — 今日头条发布
- `csdn-publisher` — CSDN 发布
- `cross-post-orchestrator` — 多平台编排