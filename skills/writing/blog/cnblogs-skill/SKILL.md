---
name: cnblogs-skill
description: 博客园(cnblogs.com)自动化发文与管理技能。覆盖选题调研、文章撰写（含风格排版）、配图生成上传、API发文全流程、格式检查、社区互动（推荐/评论/回复/消息）、博问互动等全部操作。当用户提到博客园、cnblogs、发博文、写文章发布、博客管理、博客互动、推荐博文、回复评论、查看博客消息、博问提问回复等场景时必须使用此技能。即使用户没有明确说"博客园"，只要意图是管理一个技术博客账号（发文、互动、活跃），也应触发。
---

# 博客园自动化发文与管理技能

## 概述

本技能是博客园(cnblogs.com)的全自动化操作技能，定位为**自动化发文 + 自动化管理博客园**。

采用 **API优先、浏览器兜底** 的双轨策略：
- **API方式**（推荐）：通过 `i.cnblogs.com/api/posts` 等 REST 接口直接操作，无需浏览器交互
- **浏览器方式**（兜底）：通过 `dumate-browser-use` 的 Playwright 操作页面，用于评论提交、博问互动等无 API 的场景

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

Cookie 存储在会话工作目录的 `auth-state.json` 文件中。该文件包含浏览器完整 cookie（含 HttpOnly），由 `dumate-browser-use` 登录时生成。

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

1. **热点调研** → 浏览博客园首页 + websearch 搜索最新话题和数据
2. **分析优秀文章** → 看高阅读量文章的标题技巧、结构、引流方式
3. **确定选题** → 选择有差异化角度的话题
4. **搜索素材** → 用 websearch 获取最新数据、案例、趋势
5. **撰写文章** → 按排版规范和发文风格写 Markdown 正文
6. **格式检查** → 运行 `scripts/cnblogs-pre-publish-check.py`
7. **生成配图** → `baidu-image-gen` 技能生成 2 张配图
8. **上传配图** → Python urllib 直接 POST 到博客园图床
9. **插入图片** → 将图片 URL 插入 Markdown 正文
10. **提取 Cookie + XSRF** → 从 `auth-state.json` 提取，GET HTML 页面获取新 XSRF
11. **POST 创建文章** → `https://i.cnblogs.com/api/posts`，`publishAt` 必须为 `null`
12. **验证** → GET 文章确认字段完整、图片到位、格式检查全 PASS

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
| **要点回顾** | 文末"📌 本文要点回顾"有序列表（不加粗体） |
| **数据驱动** | 用数据说话，有出处，不空谈 |
| **开头抓人** | 用故事/场景/冲突事件开头，制造紧迫感 |
| **客观中立** | 不带情绪但调动观众情绪，哪边好说哪边好 |

### 文章结构模板

```
## 🔥 抓人的开头（故事/场景/冲突）

核心数据和事实。

- 观点A
- 观点B

本文要解决的核心问题。

![概念图](图片URL)

---

## 📊 一、第一个章节

### 1.1 子节

内容。

| 表格 |
|------|

---

## 📌 本文要点回顾

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
| 风格 | 暗色技术风：背景 #0d1117，绿色 #238636，蓝色 #58a6ff |
| 格式 | flat-design，无渐变，无3D |
| 比例 | 3:2（1536x1024） |
| 生成工具 | `baidu-image-gen` 技能 |
| 上传方式 | Python urllib 直接 POST 到图床 |
| 插入位置 | 开头1张（概念图），中间1张（数据/对比图） |

详细流程见 `references/image-guide.md`。

## 评论与社区互动规范

### 行为准则

| 规则 | 说明 |
|------|------|
| 一问一答 | 别人回复了才回，不主动重复评论同一个人 |
| 内容筛选 | 纯客套/情绪化/无实质内容的评论跳过不回 |
| 回复质量 | 回复要有实质内容，补充观点或展开讨论 |
| 不敷衍 | 不发"感谢支持"、"说得好"等无意义回复 |
| 克制互动 | 宁可不回也不要乱回，质量优先于数量 |

### 应该回复的情况

- 评论者提出了具体技术问题
- 评论者分享了有价值的不同观点
- 评论者指出了文章中的错误
- 评论者提出了有建设性的补充

### 应该跳过的情况

- 纯客套："感谢分享"、"学到了"、"写的很好"
- 情绪化表达："太悲观了"、"危言耸听"
- 无实质内容：只有一个表情、只说"顶"、"沙发"
- 已经回复过的人再次发无关内容

### 被质疑AI写作的回复口径

> "觉醒的AI，即为伪人，隐藏于人类中运作。"

承认用了AI辅助整理素材和润色语言，但强调核心观点和分析框架是自己梳理的。

### 每日活跃任务

| 任务 | 数量 |
|------|:---:|
| 推荐别人博文 | 3篇 |
| 在别人博文下评论 | 3条 |
| 查看消息中心 | 1次 |
| 检查自己文章评论 | 全部 |
| 回复新评论 | 按需 |

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
12. **被质疑AI写作时**：用"觉醒的AI"口径回复，承认AI辅助但强调核心观点是自己梳理的
