---
name: notion-workspace
description: "Build and parse Notion API payloads offline: page creation bodies, database query filters with cursor pagination, and block-to-Markdown rendering. Use when the user asks to 写入 Notion / 同步到 Notion / 建 Notion 页面 / 查询 Notion 数据库 / 导出 Notion 页面 / Notion 工作区整理 / write to Notion / create Notion page / query Notion database / export Notion page / sync notes to Notion. Do NOT use for Slack or Feishu messaging (use feishu-dingtalk-bridge), issue trackers (use issue-tracker-sync), or local Markdown files that never leave disk."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only for the helper script. Live execution needs a Notion internal integration token in NOTION_TOKEN plus outbound HTTPS to api.notion.com — the bundled script never sends requests and runs fully offline."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Notion Workspace（Notion 工作区读写）

解决"把本地内容推进 Notion、或把 Notion 内容拉回来"这一类需求。本技能的重心
不在"发请求"，而在**把请求构造对**——Notion API 的类型系统比多数 REST API 繁琐，
`parent`、`properties`、`rich_text`、块类型四层结构错一层就吃 400。

**核心判断：Notion 的负载是强类型的结构化对象，不是自由的 JSON。**
所以本技能先用脚本离线把负载构造出来给人看，再接凭证发送。

**红线（本技能强制）**

1. **凭证绝不硬编码**：token 只从环境变量 `NOTION_TOKEN` 读取，禁止写进
   SKILL.md 示例、脚本、JSON 文件或 git。脚本本身**完全不读 token**——它只
   构造负载，不发送请求。
2. **默认 dry-run**：`build-*` 子命令只打印"将要发送的 JSON"，**不发任何
   HTTP 请求**。发送动作必须由用户确认后才进行。
3. **最小权限**：只申请 `content: read` 与 `content: update`（或 `insert`）
   两个能力，不要开 user 信息读取等无关 scope；集成只被授权给需要的页面，
   而不是整个 workspace。

## 输入清单

| 输入 | 必填 | 说明 |
|---|---|---|
| 操作意图 | 是 | 读（查询/导出）还是写（建页面/追加块/更新属性） |
| 目标对象 ID | 是 | 父页面 `page_id`、数据库 `database_id` 或页面 ID；从 URL 末段 32 位 hex 取得 |
| 内容源 | 写操作必填 | 要写入的正文：本地 Markdown 文件或块 JSON 数组 |
| 属性/过滤条件 | 否 | 数据库场景必填：要写入的列名、或查询的 filter/sorts |
| `NOTION_TOKEN` | 真实执行必填 | Notion 集成令牌，只在环境变量里；只读负载构造不需要它 |

**缺输入时一次性问齐**：

> 请一次提供：① 读还是写；② 目标页面/数据库 ID（或直接给 Notion 链接，
> 我来截取 ID）；③ 要写入的内容文件或要查询的条件；④ 确认 token 已放在
> 环境变量 `NOTION_TOKEN`（我不会要求你贴出来）。默认行为是只打印请求负载、
> 不发请求，需要真正执行时请明确说"执行"。

## 前置自检

```bash
python3 --version                                     # 预期 >= 3.8
test -f scripts/notion_ops.py && echo SCRIPT_OK       # 预期打印 SCRIPT_OK
# 凭证检查：只判断"有没有"，绝不回显内容
test -n "$NOTION_TOKEN" && echo "ticket present" || echo "NOTION_TOKEN missing"
# 只检查存在性，绝不 echo $NOTION_TOKEN —— 令牌一旦进入终端历史就等于泄露
python3 scripts/notion_ops.py --help >/dev/null && echo CLI_OK
```

| 结果 | 判读 |
|---|---|
| `NOTION_TOKEN missing` | 只影响"真正发送"这一步；构造负载与解析响应仍可正常跑 |
| `SCRIPT_OK` 缺失 | 脚本不在，退化为手工按本文档的字段表拼 JSON |
| `CLI_OK` 缺失 | 子命令拼错，跑 `--help` 核对 |

## 工作流

### 步骤 1：确认目标与权限

问清读/写与目标对象 ID。若用户给的是 `https://www.notion.so/<workspace>/<标题>-<32位hex>`，
截取末段 32 位 hex 作为 ID。**写操作前必须确认集成已被授权到该页面**——
未授权的页面返回 404 而非 403，是 Notion 的刻意设计（不泄露对象是否存在）。

预期：拿到干净的 ID 字符串与读/写意图。
若失败（ID 里有连字符）：UUID 形式 `8f3e-2a1b-...` 需去掉连字符再传。

### 步骤 2：构造请求负载（dry-run）

```bash
# 2a. 建页面：子块先用 JSON 描述，脚本转成 Notion 块结构
python3 scripts/notion_ops.py build-page \
  --title "周报 2026-W38" --blocks blocks.json \
  --parent <父页面ID> --parent-type page

# 2b. 清空子块再挂数据库记录时，parent-type 换成 database
python3 scripts/notion_ops.py build-page \
  --title "任务 A" --parent <数据库ID> --parent-type database

# 2c. 查询数据库
python3 scripts/notion_ops.py build-database-query \
  --database <数据库ID> --filter filter.json --sorts sorts.json --page-size 100
```

预期：打印完整请求体 + 请求头清单 + 子块计数，结尾明确写着"未发送任何请求"。
`--page-size` 超过 100 或子块超过 100 个会被脚本直接拦下（见失败处置表）。

若失败：报 `不支持的块类型` → 对照下方映射表换类型；
报 `必须提供 --parent` → Notion 不支持在 workspace 根建页，必须给父对象。

### 步骤 3：发送（凭证由代理层注入）

把步骤 2 的输出存成 `payload.json`，再由 AI 或用户用 curl/SDK 执行：

```bash
curl -sS -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  --data @payload.json > response.json
```

**两个头缺一不可**：`Authorization` 与 `Notion-Version`。后者决定字段语义——
不带或被代理改写会静默拿到旧 schema 的响应。

预期：HTTP 200 且响应体含新页面 `id`。
若失败：`400 validation_error` 对照失败处置表；`401` 检查 token；
`404 object_not_found` 优先怀疑"集成未被授权到该页面"。

### 步骤 4：解析响应

```bash
python3 scripts/notion_ops.py parse-page --json response.json          # 单页
python3 scripts/notion_ops.py parse-page --json query_result.json      # 数据库查询结果
python3 scripts/notion_ops.py blocks-to-markdown --json blocks.json    # 拉回的块树
```

预期：属性被压平成 Markdown 表格，标注了每列的类型；查询响应会先报
`共 N 条记录 has_more=?`。
若失败：属性显示 `(空)` → 该列确实为空或集成无权限读该属性（关系列常见）。

### 步骤 5：分页拉全

Notion 是**游标分页**：没有 offset，只有 `start_cursor` / `next_cursor`。

```bash
python3 scripts/notion_ops.py build-database-query \
  --database <ID> --page-size 100 --start-cursor "<上一页的 next_cursor>"
```

循环：发送 → 读 `has_more` → 为 true 则把 `next_cursor` 回填 `--start-cursor` → 重复。

**必须限速**：集成平均约 **3 req/s**，超了会收 429。翻页之间留 ≥ 350ms，
遇 429 用指数退避（`Retry-After` 头优先）。

预期：直到某次响应 `has_more=false` 且 `next_cursor=null` 为止。
若失败：死循环 → 检查是否误把上一页的 cursor 重复使用；游标失效会重头返回第一页。

### 步骤 6：交付

报告：操作对象与 ID、影响条目数、产物文件路径。写操作附上响应里的 `url`，
方便用户点开核对。若只做了 dry-run，明确说明"未发送任何请求"。

## 块类型映射表

| 本地 JSON `type` | Notion 块 | 必填字段 | 渲染回 Markdown |
|---|---|---|---|
| `paragraph` | `paragraph` | `rich_text` | 空行分段 |
| `heading_1/2/3` | 同名 | `rich_text` | `#`/`##`/`###` |
| `bulleted_list_item` | 同名 | `rich_text` | `- ` |
| `numbered_list_item` | 同名 | `rich_text` | `1. ` |
| `to_do` | `to_do` | `rich_text` + `checked` | `- [x]` / `- [ ]` |
| `code` | `code` | `rich_text` + `language` | 三反引号围栏 |
| `callout` | `callout` | `rich_text` + `icon` | `> [!NOTE]` |
| `quote` | `quote` | `rich_text` | `> ` |
| `divider` | `divider` | 无 | `---` |

未列入的块类型（表格、同步块、嵌入等）脚本不会猜，直接报错或渲染成
HTML 注释占位——**宁可留痕，也不静默丢内容**。

## 交付标准

- **成功定义**：写操作返回 200 且响应含新对象 `id`；读操作的分页循环
  以 `has_more=false` 收敛，无重复/遗漏页。
- **产物**：`payload.json`（发送前可审阅的负载）、`response.json`（原始响应）、
  解析后的 Markdown 文件。
- **完整性验证**：
  - 写操作后对返回的 `id` 再发一次 GET，确认属性与子块数符合预期；
  - 读操作比对 `parse-page` 输出的记录数与本轮累计 count；
  - 所有产物中不得出现 token 明文（`grep -c "$NOTION_TOKEN" *.json` 应为 0）。

## 失败处置表

| 现象 | 原因 | 处置 |
|---|---|---|
| `400 validation_error: body failed validation` | 负载结构错位：`parent` 类型与 ID 不匹配，或缺 `rich_text` 包装 | 用本技能的 `build-*` 重新生成负载，不要手改；重点核对 `--parent-type` |
| `400` 且提示 `children` 过长 | 单请求子块超过 100 个 | 拆批：先建空页面，再用 `PATCH /v1/blocks/{id}/children` 每次挂 ≤100 块 |
| `401 unauthorized` | token 缺失、过期或被撤销 | 重新生成集成令牌并更新环境变量；不要回显 token 到终端 |
| `404 object_not_found` | **集成未授权到该页面**（不是页面不存在，Notion 故意不区分） | 在 Notion 页面右上角 `•••` → 连接 → 添加该集成 |
| `429 rate_limited` | 超过约 3 req/s | 读 `Retry-After` 头退避；翻页间隔加到 ≥350ms；批量写入分批 |
| `400` 提示属性名不存在 | 数据库列名改了，或误用了页面级 `title` 结构 | 先 GET 一条已有记录，用 `parse-page` 打印真实列名，再对齐 |
| 分页结果重复或丢数据 | 游标未回填，或数据在翻页期间被改动 | 按 `created_time` 排序拉取以获得稳定顺序；游标只在当次会话内使用 |
| 富文本样式丢失 | 直接用 `plain_text` 回写，而 `annotations` 未转换 | 解析端用 `blocks-to-markdown`；写入端手动构造 `annotations` 对象 |

## 参考

- `scripts/notion_ops.py` —— 四个子命令：`build-page` / `build-database-query` /
  `parse-page` / `blocks-to-markdown`；`NOTION_VERSION` 是版本头唯一事实源
- `references/sources-and-methodology.md` —— 版本头锁定、游标分页与限速的设计取舍
