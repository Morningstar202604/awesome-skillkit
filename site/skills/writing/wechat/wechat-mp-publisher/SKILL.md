---
name: "wechat-mp-publisher"
description: "微信公众号文章发布自动化。基于官方草稿箱 API：获取 access_token、上传正文图片与封面素材、创建草稿（draft/add）、提交发布（freepublish）。当用户提到 公众号发文、微信公众号发布、公众号草稿、推送文章到公众号、publish to WeChat Official Account、wechat mp article、wechat official account draft、post article to weixin mp 时使用。所有写操作默认 dry-run，确认后才真正执行。 Do NOT use for personal WeChat chat messages (official account API only)."
license: Apache-2.0
compatibility: Requires network access to api.weixin.qq.com and valid session credentials in environment variables. Python 3.8+.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 微信公众号发布 Skill

基于官方草稿箱/发布 API 的公众号文章发布自动化：token → 上传素材 → 创建草稿 → 提交发布。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| AppID / AppSecret | 是 | 环境变量 `WECHAT_MP_APPID`/`WECHAT_MP_SECRET`，或命令行 `--appid`/`--secret` |
| 正文 HTML 文件 | add-draft 必需 | `--content-html <path>`，脚本读取文件内容（Markdown 需先转 HTML） |
| 封面 media_id | add-draft 必需 | `--thumb-media-id`，必须是 add-thumb 返回的**永久素材** media_id（uploadimg 的临时 url 不能当封面） |
| `--title` | add-draft 必需 | 文章标题 |
| 封面图文件 | add-thumb 必需 | 位置参数，图片文件路径 |
| `--author` / `--digest` | 否 | 作者与摘要 |
| 发布接口权限 | 是 | 已认证公众号且已获得草稿箱/freepublish 权限（大部分认证号默认有） |

缺输入时一次性问齐：
「请一次性提供：① AppID 与 AppSecret（或确认环境变量已配置）；② 文章标题；③ 正文 HTML 文件路径；④ 封面图文件路径（或已有 thumb media_id）；⑤ 作者与摘要。不逐条追问。」

## 前置自检

```bash
python3 --version                                                    # 需 ≥ 3.8（仅标准库）
test -n "$WECHAT_MP_APPID" -a -n "$WECHAT_MP_SECRET" && echo creds-ok   # 或确认 --appid/--secret
test -f article.html && echo html-ok                                 # 正文文件存在
python3 scripts/wechat_mp_publish.py token --execute                 # 验证凭据与 IP 白名单
```

`token --execute` 返回含 `access_token` 即通过；返回 errcode 40164 → 把执行机出口 IP 加入公众号后台 IP 白名单后重跑。任一失败 → 修复 → 重跑，通过前 STOP，不进入发布步骤。

## 安全规则

1. **默认 dry-run**：所有写操作不加 `--execute` 只打印 `[PLAN]` 请求计划，绝不联网发送。
2. AI 必须先把 dry-run 输出展示给用户确认，才能追加 `--execute` 执行。
3. 发布前先跑内容检查（markdown→HTML 转义、图片 URL 可访问）。
4. secret 等同密码，只放环境变量或命令行参数，**禁止写入任何进仓库的文件**。

## 工作流

### 步骤 1：获取 access_token 并验证凭据

```bash
python3 scripts/wechat_mp_publish.py token --execute
```

预期：JSON 返回含 `access_token`。token 有效期 7200 秒，脚本每次操作自动获取，无需缓存。
若失败：errcode 40001 → 核对 AppID/Secret；40164 → 加 IP 白名单（见失败处置表）。

### 步骤 2：上传封面（永久素材，返回 media_id）

```bash
python3 scripts/wechat_mp_publish.py --execute add-thumb cover.jpg
```

预期：JSON 返回 `media_id`，后续 add-draft 使用。封面必须是永久素材。
若失败：文件不存在/格式不支持 → 换 jpg/png 图片重试。

（可选）上传正文内嵌图片：

```bash
python3 scripts/wechat_mp_publish.py --execute upload-img img1.jpg
```

预期：返回图文正文内可用的 `url`（uploadimg 临时素材，**仅正文可用，不能当封面**）。

### 步骤 3：dry-run 创建草稿，确认后真发

先把 Markdown 转 HTML（标题 h2 起、代码块转义），然后：

```bash
python3 scripts/wechat_mp_publish.py add-draft \
  --title "文章标题" \
  --content-html article.html \
  --thumb-media-id <第2步返回的media_id> \
  --author "作者" \
  --digest "摘要"
```

预期：不加 `--execute` 时输出 `[PLAN] POST .../cgi-bin/draft/add` 与 payload，展示给用户确认。
若失败：argparse 报缺参数 → 按报错补齐。

确认后执行：

```bash
python3 scripts/wechat_mp_publish.py --execute add-draft \
  --title "文章标题" --content-html article.html \
  --thumb-media-id <media_id> --author "作者" --digest "摘要"
```

预期：JSON 返回 `media_id`，即草稿 ID，记下用于步骤 4。
若失败：errcode 53401 → 封面 media_id 无效，用 add-thumb 重新上传。

### 步骤 4：提交发布并验证

```bash
python3 scripts/wechat_mp_publish.py --execute publish <草稿media_id>
```

预期：freepublish/submit 返回 ok。发布是异步的：之后用 `freepublish/get` 查询发布状态；发布成功后文章在公众号后台「发表记录」可见。
若失败：errcode 53404 → 文章被判违规，人工修改内容。

## 参数速查表

| 子命令 | 参数 | 说明 |
|--------|------|------|
| （全局） | `--appid` / `--secret` | 与环境变量二选一 |
| `token` | — | 获取 access_token |
| `upload-img <file>` | — | 上传正文图片（uploadimg，返回临时 url） |
| `add-thumb <file>` | — | 上传永久素材封面（add_material，返回 media_id） |
| `add-draft` | `--title`、`--content-html`、`--thumb-media-id`、`--author`、`--digest` | 创建草稿（draft/add），返回 media_id |
| `publish <media_id>` | — | 提交发布（freepublish/submit） |
| 以上所有写子命令 | `--execute` | 缺省 dry-run；加后才真发 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| 输出以 `[PLAN]` 开头 | 未加 `--execute`（默认 dry-run） | 向用户展示计划，确认后加 `--execute` |
| 40001 | appid/secret 错误 | 核对凭据后重跑 |
| 40164 | 执行机 IP 不在白名单 | 公众号后台「基本配置」加白后重跑 |
| 45009 | 调用频率超限 | 等待后重试 |
| 53401 | 封面 media_id 无效 | 用 add-thumb 重新上传永久素材 |
| 53404 | 文章被判定违规 | 人工修改内容后重试 |
| `wechat errcode=<N> errmsg=<M>`（退出码 1） | 其他 API 错误 | 按官方文档核对 errcode 含义 |

## 交付标准

- 成功定义：publish 提交返回 ok，且 freepublish/get 查询到发布成功、公众号后台「发表记录」可见文章。
- 产物：草稿 media_id（步骤 3 返回），是发布与追溯的唯一凭据，需记录。
- 验证完整性：以 `freepublish/get` 返回状态为准，不以提交成功为准（发布异步）。

## 参考

- 草稿箱: https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/
- 发布能力: https://developers.weixin.qq.com/doc/offiaccount/Publish/Publish.html
- 素材管理: https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/new_asset.html

接口字段以官方文档为准；若微信调整 API，以 DevTools/官方文档实测结果更新 `scripts/wechat_mp_publish.py` 顶部的端点常量。
