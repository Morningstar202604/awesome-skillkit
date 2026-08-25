---
name: "juejin-publisher"
description: "掘金（juejin.cn）文章发布自动化。通过 Web 端接口保存草稿并发布 Markdown 文章，Cookie 认证，默认 dry-run。当用户提到掘金发文、掘金发布文章、发沸点文章到掘金等场景时使用。首次使用需按文档核对端点。"
license: Apache-2.0
metadata:
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 掘金发布 Skill

## compatibility
- Python 3.8+（仅标准库）
- 掘金账号登录态 Cookie（含 `sessionid_a1`）

## ⚠️ 端点核对（首次使用必做）

掘金**没有公开开放 API**。本技能使用 Web 编辑器同款内部接口，
社区通用端点已写入 `scripts/juejin_publish.py` 顶部 `ENDPOINTS` 常量。
平台可能随时调整——首次使用前核对一次：

1. 浏览器登录 juejin.cn → 打开创作者编辑器 → F12 → Network 面板
2. 手动保存一次草稿、发布一次文章
3. 找到 `content_api/v1/article/...` 相关请求，对照修改脚本中的 URL 与字段名

## 认证管理

```bash
export JUEJIN_COOKIE="sessionid_a1=...; 其他必要字段..."
```

从浏览器 DevTools → Application → Cookies 复制完整值。
Cookie 过期的表现：接口返回 err_no 非 0 或 HTTP 401/403——重新复制即可。
**禁止把 Cookie 写入任何进仓库的文件。**

## 工作流

### 1. 查分类 / 标签 ID

```bash
python3 scripts/juejin_publish.py --execute categories | head -50
```

记下目标分类的 category_id（如后端的 hex 字符串），以及标签 tag_ids。

### 2. 保存草稿（默认 dry-run）

```bash
python3 scripts/juejin_publish.py draft-save \
  --title "文章标题" --markdown article.md \
  --category-id <id> --tag-ids <id1>,<id2> \
  --brief "摘要"
# 输出确认无误后加 --execute 执行；返回 data.article_id
```

### 3. 发布

```bash
python3 scripts/juejin_publish.py publish <article_id> \
  --title "文章标题" --markdown-file article.md \
  --category-id <id> --tag-ids <id1>,<id2>
```

发布走平台审核（need_review=true），几分钟后在个人主页确认状态。

## 安全规则

1. 默认 dry-run，`--execute` 才真正发送——AI 必须先展示计划等确认
2. Cookie 只放环境变量或本地文件，绝不入库
3. 掘金对高频发布有风控，一天多篇时拉开间隔

## 已知限制

- 无官方 API，端点属于内部实现，可能随版本变动（核对步骤见上）
- 封面图：Web 端上传走独立图片服务，本脚本暂未封装；可先用外链 cover-image
