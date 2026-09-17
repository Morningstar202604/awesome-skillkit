---
name: cnblogs-skill
description: 博客园(cnblogs.com)自动化发文与管理技能。覆盖选题调研、文章撰写（含风格排版）、配图生成上传、API发文全流程、格式检查、社区互动（推荐/评论/回复/消息）、博问互动等全部操作。当用户提到博客园、cnblogs、发博文、写文章发布、博客管理、博客互动、推荐博文、回复评论、查看博客消息、博问提问回复等场景时必须使用此技能。即使用户没有明确说"博客园"，只要意图是管理一个技术博客账号（发文、互动、活跃），也应触发。Do NOT use for publishing to platforms other than cnblogs.com.
license: Apache-2.0
compatibility: Requires network access to cnblogs.com and valid session credentials in environment variables. Python 3.8+.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: "content-publishing"
  verified-date: "2026-08-26"
---

# 博客园自动化发文与管理技能

## 概述

本技能是博客园(cnblogs.com)的全自动化操作技能，定位为**自动化发文 + 自动化管理博客园**。

采用 **API优先、浏览器兜底** 的双轨策略：
- **API方式**（推荐）：通过 `i.cnblogs.com/api/posts` 等 REST 接口直接操作，无需浏览器交互
- **浏览器方式**（兜底）：通过任意 Playwright 驱动的浏览器会话操作页面，用于评论提交、博问互动等无 API 的场景

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 任务意图 | 是 | 发文 / 检查格式 / 配图 / 社区互动 / 选题调研（决定路由到哪个工作流） |
| 文章主题（或全文） | 发文时必需 | 有全文则走格式检查，只有主题则从选题调研开始 |
| `account.local.json` | 是（首次需配置） | 账号数据，见下节"账号信息" |
| `auth-state.json` | 是 | 浏览器登录态文件，位于会话工作目录 |
| 待检 Markdown 文件 | 格式检查时必需 | 传给预发布检查脚本 |

缺输入时一次性问齐（不要分多轮追问）：
"请提供：① 本次要做什么（发文/检查格式/配图/互动/选题）；② 若发文：文章主题或全文文件路径、目标个人分类；③ 若检查：Markdown 文件路径与文章标题。"

## 前置自检

依次执行，任一失败 → 按提示修复后 STOP，不要继续发文流程：

```bash
# 1. 账号文件已配置（首次使用时）
test -f references/account.local.json && echo OK
# 预期：OK；失败 → 复制 references/account.example.json 为 account.local.json 并填入真实账号，仍缺则提示用户配置，不要猜测账号

# 2. 预发布检查脚本存在
test -f scripts/cnblogs-pre-publish-check.py && echo OK
# 预期：OK；失败 → cd 到本技能目录再操作

# 3. 登录态有效（返回 JSON = 有效；返回 <!doctype = 过期）
curl -s "https://i.cnblogs.com/api/posts/{任意已有postId}" -H "Cookie: $COOKIE" | head -c 20
# 预期：JSON 开头；失败（HTML 开头）→ 提示用户通过浏览器重新登录并重新导出 auth-state.json
```

Cookie 存储在会话工作目录的 `auth-state.json` 文件中（含 HttpOnly），提取方式见 `references/publish-api.md` 的"Cookie 提取"章节。POST 请求另需 `X-XSRF-TOKEN` header：GET `https://i.cnblogs.com/posts`（HTML 页面），从 `Set-Cookie` 头提取 `XSRF-TOKEN` 值并 `decodeURIComponent` 解码；XSRF token 会定期变化，每次 POST 前重新获取最安全。

## 账号信息

账号数据**不随本技能分发**，存于 `references/account.local.json`（gitignored）：

| 字段 | 说明 |
|------|------|
| `username` | 博客园用户名 |
| `blog_url` | 博客首页地址 |
| `blog_id` | 博客 ID（API 发文必需） |
| `signature_id` | 签名 ID |
| `personal_categories` | 个人分类 ID 映射 |
| `published_posts` | 已发布文章台账（本地运营记录） |

首次使用：复制 `references/account.example.json` 为 `account.local.json` 并填入你自己的账号。所有发文/互动流程先读该文件；文件缺失时提示用户配置，不要猜测账号。

## 已发布文章列表

→ 运营台账已移至 `references/account.local.json` 的 `published_posts` 字段（含 PostId、标题、分类），发文成功后由流程负责追加更新。

## 认证管理

### Cookie 来源

Cookie 存储在会话工作目录的 `auth-state.json` 文件中。该文件包含浏览器完整 cookie（含 HttpOnly），由 Playwright 登录会话的 `storage_state` 导出。

提取方式见 `references/publish-api.md` 的"Cookie 提取"章节。

### XSRF Token

POST 请求需要 `X-XSRF-TOKEN` header。获取方式：

1. GET 请求 `https://i.cnblogs.com/posts`（HTML 页面）
2. 从响应的 `Set-Cookie` 头中提取 `XSRF-TOKEN` 值
3. `decodeURIComponent` 解码后使用

重要：XSRF token 会定期变化，每次 POST 前重新获取最安全。

### 登录态验证

```python
# GET 请求任意 API 端点，返回 JSON = 有效，返回 HTML = 过期
curl -s "https://i.cnblogs.com/api/posts/{任意已有postId}" -H "Cookie: $COOKIE" | head -c 20
# JSON 开头 = 有效；<!doctype = 过期
```

过期后需提示用户通过浏览器重新登录。

## 工作流

1. **准备**：确认账号认证状态与目标分类（见 认证管理 / 分类 ID 映射）
2. **写稿**：按 发文风格规范 与 排版硬性要求 产出正文，配图按 配图规范 处理
3. **预检**：跑 预发布检查脚本 做提交前把关
4. **发布**：执行 核心工作流 章节的发布步骤
5. **善后**：按 评论与社区互动规范 跟进互动；异常查 失败处置表

## 核心工作流

### 任务路由

根据用户需求选择对应工作流，**先读参考文件再操作**：

| 用户意图 | 工作流 | 参考文件 |
|----------|--------|----------|
| 选题/找热门话题 | 热点调研 | `references/topic-research.md` |
| 写文章/发文/发布博文 | API发文流程 | `references/publish-api.md` |
| 检查文章格式 | 格式检查 | `references/formatting-guide.md` |
| 生成配图/上传图片 | 配图流程 | `references/image-guide.md` |
| 评论/回复评论/社区活跃 | 社区互动 | `references/community.md` |
| 查看消息/有没有人回复 | 社区互动 | `references/community.md` |
| 遇到操作失败/超时 | 故障排查 | `references/troubleshooting.md` |

### 发文完整流程（API方式）

按以下 6 步执行；每步含动作、预期与失败分支，详细字段和代码示例见 `references/publish-api.md`。

### 步骤 1：热点调研与选题

- **动作**：按 `references/topic-research.md` 浏览博客园首页 + websearch 搜索最新话题和数据；分析高阅读量文章的标题技巧、结构、引流方式；选定有差异化角度的话题，并用 websearch 获取最新数据、案例、趋势作为素材。
- **预期**：确定 1 个选题，且手头有 ≥2 条带出处的数据/案例支撑。
- **若失败**：找不到有差异化的角度 → 换热点话题+实操角度（教人怎么做），不要硬写。

### 步骤 2：撰写正文

- **动作**：按 `references/formatting-guide.md` 的排版规范和下文"发文风格规范"写 Markdown 正文（`##`/`###` 标题、短段落多空行、`---` 分隔、章节标题带 emoji、文末要点回顾）。
- **预期**：正文含开头故事/场景、至少 1 个对比表格、不超过 5 组引用块、"本文要点回顾"有序列表。
- **若失败**：结构缺项 → 对照 `references/formatting-guide.md` 的文章结构模板补齐。

### 步骤 3：格式检查

- **动作**：
  ```bash
  python3 scripts/cnblogs-pre-publish-check.py <markdown_file> --title "文章标题"
  ```
  检查 8 项：h1 标题、标题 HTML 实体、代码块反引号、br 标签、引用块数量、签名区格式、标题层级跳跃。
- **预期**：全部 PASS，退出码 0。
- **若失败**：任一项 FAIL → 按 `references/formatting-guide.md` 对应规则修改后重跑，全部 PASS 才能发布。

### 步骤 4：生成并上传配图

- **动作**：按 `references/image-guide.md` 用任意可用的文生图工具/技能生成 2 张配图（暗色技术风、3:2 比例；无配图能力可跳过本步），再用 Python urllib 直接 POST 到博客园图床，把图片 URL 插入 Markdown 正文（开头 1 张概念图，中间 1 张数据/对比图）。
- **预期**：拿到 2 个图床 URL，正文对应位置出现 `![...](图片URL)`。
- **若失败**：上传 401/403 → Cookie 过期，回前置自检第 3 项重新验证登录态；插入图片时 replace 不生效 → 目标文本必须完全一致（含标点、换行），改用精确匹配重试。

### 步骤 5：提取凭据并创建文章

- **动作**：按 `references/publish-api.md` 从 `auth-state.json` 提取 Cookie，GET HTML 页面获取新 XSRF；POST `https://i.cnblogs.com/api/posts` 创建文章，`publishAt` 必须为 `null`（传空字符串 `""` 会报 DateTime 转换错误）。
- **预期**：API 返回新文章 PostId。
- **若失败**：返回 HTML 而非 JSON → 登录态过期，提示用户重新登录；DateTime 转换错误 → 检查 `publishAt` 是否为 `null`。

### 步骤 6：验证发布结果并更新台账

- **动作**：GET 新文章确认字段完整、图片到位、格式检查全 PASS；把 PostId、标题、分类追加到 `references/account.local.json` 的 `published_posts` 字段。
- **预期**：GET 返回的文章字段与提交一致，台账新增 1 行记录。
- **若失败**：字段缺失/图片未显示 → 按 `references/publish-api.md` 修正字段后用更新接口重新提交；台账更新失败 → 手动补记，不要丢失 PostId。

详细字段格式和代码示例见 `references/publish-api.md`。

## 发文风格规范

这是用户明确要求的写作风格，必须严格遵守。详细规范见 `references/formatting-guide.md`。

### 核心风格

| 规则 | 要求 |
|------|------|
| **段落留白** | 短段落多空行，一句或几句话就空行，不要多段话挤在一起 |
| **个人观点** | 有自己的观点和态度，不是文档搬运，不站队但调动两边情绪 |
| **标题层级** | 用 `##`（h2）和 `###`（h3），禁止 `#`（h1） |
| **章节分隔** | 用 `---` 分割线 |
| **标题emoji** | 每个章节标题带 emoji |
| **对比内容** | 用 Markdown 表格 |
| **引用块** | 每篇不超过 5 组，用于关键结论和金句 |
| **要点回顾** | 文末" 本文要点回顾"有序列表（不加粗体） |
| **数据驱动** | 用数据说话，有出处，不空谈 |
| **开头抓人** | 用故事/场景/冲突事件开头，制造紧迫感 |
| **客观中立** | 不带情绪但调动观众情绪，哪边好说哪边好 |

### 文章结构模板

```text
##  抓人的开头（故事/场景/冲突）

核心数据和事实。

- 观点A
- 观点B

本文要解决的核心问题。

![概念图](图片URL)

---

##  一、第一个章节

### 1.1 子节

内容。

| 表格 |
|------|

---

##  本文要点回顾

1. 要点一
2. 要点二
```

### 标题技巧（从优秀文章学到）

- 用问句+反直觉答案："为什么...？因为..."
- 用具体数字："一个周末生成24,506行代码"
- 用冲突对比："正在消失 vs 正在崛起"
- 热点话题+实操角度：不只报道，教人怎么做
- TL;DR放最前面：10秒内获取核心价值

## 排版硬性要求

| 规则 | 要求 | 原因 |
|------|------|------|
| 段落分隔 | 用空行留白 | `<br>` 在 Markdown 模式下不渲染 |
| 代码块标记 | 三个反引号 ` ``` ` | 两个反引号不渲染 |
| 标题HTML实体 | 标题中不能有 `&quot;` 等 | 显示为原始实体码 |
| 签名区 | HTML 标签，不用 Markdown | 系统签名通过 API 管理 |
| 标签数量 | 不超过 8 个 | 博客园限制 |
| 投稿限制 | 3小时同分类只能投1篇候选区 | 超限换分类直接发布 |

## 配图规范

| 规则 | 要求 |
|------|------|
| 数量 | 每篇 2 张 |
| 风格建议 | 暗色技术风：背景 #0d1117，绿色 #238636，蓝色 #58a6ff，flat-design |
| 比例 | 3:2（1536x1024） |
| 生成工具 | 任意文生图工具/技能（本技能不绑定特定实现） |
| 上传方式 | Python urllib 直接 POST 到图床 |
| 插入位置 | 开头1张（概念图），中间1张（数据/对比图） |

详细流程见 `references/image-guide.md`。

## 评论与社区互动规范

### 互动原则

| 原则 | 说明 |
|------|------|
| 质量优先 | 回复要有实质内容，补充观点或展开讨论；宁可不回也不要乱回 |
| 一问一答 | 别人回复了才回，不主动刷屏 |
| 内容筛选 | 纯客套/情绪化/无实质内容的评论跳过不回 |
| 真诚透明 | 被问及是否用 AI 时如实说明：AI 辅助整理素材与润色，观点和分析框架是自己的 |
| 不刷数据 | 不做机械的互赞互评任务，避免社区反感和平台风控 |

### 应该回复的情况

- 评论者提出了具体技术问题
- 评论者分享了有价值的不同观点
- 评论者指出了文章中的错误
- 评论者提出了有建设性的补充

### 应该跳过的情况

- 纯客套："感谢分享"、"学到了"、"写的很好"
- 情绪化表达：无实质内容的争论
- 只有一个表情、只说"顶"、"沙发"
- 已经回复过的人再次发无关内容

详细操作见 `references/community.md`。

## 分类 ID 映射

### 个人分类

→ 见 `references/account.local.json` 的 `personal_categories` 字段（每账号不同）。

### 网站分类（博客园平台级，全站通用）

| 分类 ID | 名称 | 适用场景 |
|---------|------|---------|
| 108762 | AI综合 | AI相关文章（最常用） |
| 108696 | 编程语言 | Python等编程语言文章 |
| 108766 | AI安全 | AI安全事件文章 |
| 108781 | AI Agent | AI Agent指南文章 |

> 注意：平台级分类 ID 以博客园当前实际为准，使用前建议在网站上核对。

## 参考文件索引

| 文件 | 内容 | 何时读取 |
|------|------|----------|
| `references/topic-research.md` | 选题调研：热点发现、优秀文章分析、引流技巧 | 用户要求找话题/选题时 |
| `references/publish-api.md` | API发文完整流程：Cookie提取、XSRF获取、POST请求、创建/更新文章、签名管理 | 用户要求发文时 |
| `references/formatting-guide.md` | 排版规范：标题层级、段落留白、表格、引用块、签名区、文章结构模板、预发布检查清单 | 写文章或检查格式时 |
| `references/image-guide.md` | 配图生成与上传：baidu-image-gen用法、Python urllib上传、风格规范 | 文章需要配图时 |
| `references/community.md` | 社区互动：评论API、回复规范、推荐博文、消息查看、博问互动、每日活跃流程 | 用户要求互动时 |
| `references/troubleshooting.md` | 已知坑与解决方案：13个已知问题及详细解决方案 | 操作失败时 |

## 预发布检查脚本

```bash
python3 scripts/cnblogs-pre-publish-check.py <markdown_file> --title "文章标题"
```

检查 8 项：h1标题、标题HTML实体、代码块反引号、br标签、引用块数量、签名区格式、标题层级跳跃。全部 PASS 才能发布。

## 失败处置表

| 现象/错误码 | 原因 | 处置 |
|-------------|------|------|
| API 返回 HTML 而非 JSON | 登录态过期 | 提示用户浏览器重新登录，重新导出 `auth-state.json` |
| POST 缺 `XSRF-TOKEN` 报错 | XSRF token 过期或未带 | 每次 POST 前重新 GET `https://i.cnblogs.com/posts` 提取新 token |
| `publishAt` 报 DateTime 转换错误 | 传了空字符串 `""` | `publishAt` 必须为 `null` |
| GET API 端点拿不到 XSRF | API 端点不返回 Set-Cookie | 改 GET HTML 页面（`https://i.cnblogs.com/posts`）提取 |
| 图片上传 401/403 | 图床凭据过期或 Cookie 不完整 | 确认 Cookie 取自 `auth-state.json`（含 HttpOnly），必要时重新登录 |
| 格式检查任一项 FAIL | 正文违反排版硬性要求 | 按 `references/formatting-guide.md` 修改后重跑检查 |
| 投稿超限 | 3 小时内同分类已投 1 篇候选区 | 换分类直接发布，或等待后再投 |
| 更多未列出的失败 | — | 查 `references/troubleshooting.md`（13 个已知问题及解决方案） |

## 交付标准

- **成功定义**：发文流程 = API 返回 PostId 且 GET 复核字段/图片/格式全部到位，并已更新台账；互动流程 = 目标评论/消息已按规范处理；格式检查 = 8 项全 PASS。
- **产物命名**：文章 Markdown `<主题-slug>.md`；配图 `cover-1.<ext>`、`mid-1.<ext>`（或生成工具默认名）。
- **保存位置**：会话工作目录；账号台账固定在 `references/account.local.json` 的 `published_posts`。
- **完整性验证**：GET 已发布文章 URL 可访问且正文图片显示；`published_posts` 含本次 PostId、标题、分类。

## 关键注意事项（踩过的坑）

1. **API优先**：能用 API 完成的操作不要用浏览器，API 更快更可靠
2. **publishAt 必须为 null**：传空字符串 `""` 会报 DateTime 转换错误
3. **XSRF 从 HTML 页获取**：GET API 端点不返回 Set-Cookie，需 GET HTML 页面
4. **图片插入用精确文本匹配**：replace 时确保目标文本完全一致（包括标点、换行）
5. **签名通过 API 管理**：不要在文章正文中放签名，用 `POST /api/signature` 设置
6. **标签不超过 8 个**：博客园限制
7. **投稿限制**：3小时同分类只能投1篇候选区
8. **评论行为克制**：只回该回的，不主动重复评论
9. **浏览器session会过期**：优先用API，浏览器仅用于评论/点赞等无API操作
10. **cookie从auth-state.json提取**：包含HttpOnly cookie，比浏览器document.cookie更完整
11. **短段落多空行**：这是用户最强调的排版要求，一句或几句话就空行
12. **互动真诚透明**：被问及是否用 AI 时如实说明；不做虚假人设话术
