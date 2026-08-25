---
name: "wechat-mp-publisher"
description: "微信公众号文章发布自动化。基于官方草稿箱 API：获取 access_token、上传正文图片与封面素材、创建草稿（draft/add）、提交发布（freepublish）。当用户提到公众号发文、微信公众号发布、公众号草稿、推送文章到公众号等场景时使用。所有写操作默认 dry-run，确认后才真正执行。"
---

# 微信公众号发布 Skill

## compatibility
- Python 3.8+（仅标准库，无第三方依赖）
- 已认证的公众号（服务号/订阅号均可），在后台「设置与开发 → 基本配置」拿到 AppID/AppSecret
- 草稿箱与 freepublish 接口要求公众号已获得**发布接口权限**（大部分认证号默认有）

## 凭据管理

凭据不随技能分发，两种方式提供：

```bash
export WECHAT_MP_APPID=wx你的appid
export WECHAT_MP_SECRET=你的secret
```

或命令行 `--appid / --secret`。**secret 等同密码，禁止写入任何文件进仓库。**
IP 白名单：需把执行机器的出口 IP 加入公众号后台的 IP 白名单，否则 token 返回 errcode 40164。

## 安全规则（必须遵守）

1. **默认 dry-run**：所有写操作不加 `--execute` 只打印请求计划，绝不联网发送
2. AI 在 dry-run 输出展示给用户确认后，才能追加 `--execute` 执行
3. 发布前先跑内容检查（markdown→HTML 转义、图片 URL 可访问）

## 工作流

### 1. 获取 access_token

```bash
python3 scripts/wechat_mp_publish.py --execute token
```

token 有效期 7200 秒，脚本每次操作自动获取，无需缓存。

### 2. 上传封面图（永久素材，返回 media_id）

封面必须是**永久素材** media_id（`uploadimg` 的临时 url 不能当封面）：

```bash
python3 scripts/wechat_mp_publish.py --execute add-thumb cover.jpg
```

### 3. 创建草稿

先把 Markdown 转 HTML（标题 h2 起、代码块转义），然后：

```bash
python3 scripts/wechat_mp_publish.py --execute add-draft \
  --title "文章标题" \
  --content-html article.html \
  --thumb-media-id <第2步返回的media_id> \
  --author "作者" \
  --digest "摘要"
```

返回 `media_id` 即草稿 ID。

### 4. 提交发布

```bash
python3 scripts/wechat_mp_publish.py --execute publish <草稿media_id>
```

发布是异步的：返回 ok 后用 `freepublish/get` 查询发布状态；发布后文章在公众号后台「发表记录」可见。

## 常见错误码

| errcode | 含义 | 处理 |
|---------|------|------|
| 40001 | appid/secret 错误 | 核对凭据 |
| 40164 | IP 不在白名单 | 公众号后台加白 |
| 45009 | 频率限制 | 等待后重试 |
| 53401 | 封面 media_id 无效 | 用 add-thumb 重新上传 |
| 53404 | 文章被判定违规 | 人工修改内容 |

## 官方文档

- 草稿箱: https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/
- 发布能力: https://developers.weixin.qq.com/doc/offiaccount/Publish/Publish.html
- 素材管理: https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/new_asset.html

接口字段以官方文档为准；若微信调整 API，以 DevTools/官方文档实测结果更新 `scripts/wechat_mp_publish.py` 顶部的端点常量。
