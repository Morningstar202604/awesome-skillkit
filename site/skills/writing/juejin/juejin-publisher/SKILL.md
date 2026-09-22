---
name: "juejin-publisher"
description: "掘金（juejin.cn）文章发布自动化。通过 Web 端接口保存草稿并发布 Markdown 文章，Cookie 认证，默认 dry-run。当用户提到 掘金发文、掘金发布文章、发沸点文章到掘金、publish to juejin、juejin article、juejin.cn post、publish article on juejin 等场景时使用。首次使用需按文档核对端点。 Do NOT use for publishing to platforms other than juejin.cn."
license: Apache-2.0
compatibility: Requires network access to juejin.cn and valid session credentials in environment variables. Python 3.8+.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 掘金发布技能

通过掘金 Web 编辑器同款内部接口完成 Markdown 文章的草稿保存与发布。掘金**没有公开开放 API**，端点属于内部实现。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| `JUEJIN_COOKIE` 环境变量或 `--cookie-file <path>`（或 `--cookie` 字符串） | 是 | 登录态 Cookie，必须含 `sessionid_a1`；从浏览器 DevTools → Application → Cookies 复制完整值 |
| `draft-save --title` / `--markdown` | 是 | Markdown 文件路径 |
| `draft-save / publish --category-id` | 是 | 目标分类 ID（hex 字符串），用 categories 命令查询 |
| `--tag-ids` | 否 | 逗号分隔的标签 ID，用 tags 命令查询 |
| `--brief` | 否 | 摘要 |
| `--cover-image` | 否 | 封面图外链 URL（Web 端上传走独立图片服务，本脚本未封装） |
| `publish <article_id>` | 是 | draft-save 返回的 `data.article_id` |

缺输入时一次性问齐：
「请一次性提供：① JUEJIN_COOKIE（或 cookie 文件路径）；② 文章标题；③ Markdown 文件路径；④ category_id 与 tag_ids（如未提供，我会先用 categories/tags 命令查询）；⑤ 摘要与封面图外链。不逐条追问。」

## 前置自检

```bash
python3 --version                                                # 需 ≥ 3.8（仅标准库）
test -n "$JUEJIN_COOKIE" && echo cookie-present                   # 或确认 --cookie-file 存在
test -f article.md && echo markdown-ok                            # 正文文件存在
python3 scripts/juejin_publish.py categories   # 只读干跑：验证接口连通（配好 Cookie 后可加 --execute）
```

`categories` 返回 JSON 且无 `err_no` 非 0 即通过；返回 errcode 非 0 或 HTTP 401/403 → Cookie 过期，重新复制。任一失败 → 修复 → 重跑，通过前 STOP，不进入发布步骤。

## 端点核对（首次使用必做）

社区通用端点已写入 `scripts/juejin_publish.py` 顶部 `ENDPOINTS` 常量（标 VERIFY BEFORE USE），平台可能随时调整。核对步骤：

1. 浏览器登录 juejin.cn → 打开创作者编辑器 → F12 → Network 面板
2. 手动保存一次草稿、发布一次文章
3. 找到 `content_api/v1/article/...` 相关请求，对照修改脚本中的 URL 与字段名

## 工作流

### 步骤 1：查询分类 / 标签 ID

```bash
# python3 scripts/juejin_publish.py --execute categories | head -50
# python3 scripts/juejin_publish.py --execute tags | head -50
```

预期：JSON 输出分类/标签列表；记下目标 `category_id`（hex 字符串）与 `tag_ids`。
若失败：err_no 非 0 或 HTTP 401/403 → Cookie 过期，重新复制后重跑。

### 步骤 2：dry-run 保存草稿，确认后真发

```bash
# python3 scripts/juejin_publish.py draft-save \
#   --title "文章标题" --markdown article.md \
#   --category-id <id> --tag-ids <id1>,<id2> \
#   --brief "摘要"
```

预期：不加 `--execute` 输出 `[PLAN] POST <端点>` 与 payload（不含 Markdown 正文），展示给用户确认。
若失败：argparse 报缺参数 → 按报错补齐。

确认后执行：

```bash
# python3 scripts/juejin_publish.py --execute draft-save \
#   --title "文章标题" --markdown article.md \
#   --category-id <id> --tag-ids <id1>,<id2> --brief "摘要"
```

预期：JSON 返回 `data.article_id`，记下用于步骤 3。
若失败：err_no 非 0 → 见失败处置表。

### 步骤 3：发布

```bash
# python3 scripts/juejin_publish.py publish <article_id> \
#   --title "文章标题" --markdown-file article.md \
#   --category-id <id> --tag-ids <id1>,<id2>
```

预期：返回 `need_review=true`，发布走平台审核；几分钟后在个人主页确认状态为「已发布」。
若失败：审核未通过或长时间待审 → 到掘金后台查看原因，修正后重发。

## 参数速查表

| 子命令 | 参数 | 说明 |
|--------|------|------|
| （全局） | `--cookie` / `--cookie-file` | Cookie 字符串或文件路径，与环境变量 JUEJIN_COOKIE 任选其一 |
| `categories` | — | 查询分类列表（GET column/listquery） |
| `tags` | — | 查询标签列表（POST query_list） |
| `draft-save` | `--title`、`--markdown`、`--category-id`、`--tag-ids`、`--brief`、`--cover-image` | 保存草稿，返回 data.article_id |
| `publish <article_id>` | `--title`、`--markdown-file`、`--brief`、`--category-id`、`--tag-ids`、`--cover-image` | 提交发布，走平台审核 |
| 以上所有子命令 | `--execute` | 缺省 dry-run；加后才真发 |

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| 输出以 `[PLAN]` 开头 | 未加 `--execute`（默认 dry-run） | 向用户展示计划，确认后加 `--execute` |
| `juejin err_no=<N> err_msg=<M>` | 平台拒绝（Cookie 失效/参数错/风控） | 按 err_msg 修正；Cookie 失效重新复制 |
| HTTP 401/403 | Cookie 过期或风控 | 重新从浏览器复制完整 Cookie |
| 发布后长时间待审 | `need_review=true` 平台审核 | 几分钟后在个人主页确认，勿重复提交 |
| 高频发布被风控 | 一天多篇触发风控 | 拉开发布间隔 |
| 端点 404/响应结构变化 | 掘金调整内部 API | 回到「端点核对」按 DevTools 实测更新 ENDPOINTS |

## 安全规则

1. 默认 dry-run，`--execute` 才真正发送——AI 必须先展示计划等确认。
2. Cookie 只放环境变量或本地文件，**绝不写入任何进仓库的文件**。
3. 掘金对高频发布有风控，一天多篇时拉开间隔。

## 交付标准

- 成功定义：publish 返回 need_review=true 且几分钟后文章在个人主页可见。
- 产物：`data.article_id`（草稿 ID，发布凭据，需记录）；无本地产物。
- 验证完整性：到个人主页人工确认文章状态与内容完整（标题/分类/标签/摘要/正文）。

## 参考

- `scripts/juejin_publish.py` 顶部 `ENDPOINTS` 常量 —— 全部端点来源（VERIFY BEFORE USE，首次使用按上文核对）。
- 无 references 目录；封面图建议先用外链（`--cover-image`）。
