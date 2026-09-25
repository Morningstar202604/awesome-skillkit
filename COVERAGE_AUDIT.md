# 线上操作场景覆盖度审计

**审计日期**：2026-09-25
**仓库状态**：36 场景包 / 18 域 / 153 真实技能（含 4 个本轮新增：transition-designer、motion-effects-designer、sound-designer、shot-designer 合并产物）
**审计方法**：将 153 技能映射到 20 类"AI 使用者线上高频操作"，逐项对照业界公开 agent skill 清单（Anthropic Agent Skills、aihero.dev、agnt.gg Top 100、DataCamp Top Agent Skills），严格过滤"已有覆盖/LLM 原生/平台自带"项。

---

## 一、覆盖矩阵

| # | 线上操作场景 | 现有覆盖技能 | 覆盖度 | 说明 |
|---|---|---|---|---|
| 1 | **内容创作与发布** | article-outliner/drafter/editor、seo-optimizer、humanize-rewriter、ai-trace-auditor、personal-voice-profile + 18 平台发布器 + cross-post-orchestrator | ✅ 深度覆盖 | 从选题→大纲→撰写→编辑→SEO→去AI味→平台适配→跨平台发布，全链路覆盖 |
| 2 | **搜索与信息获取** | web-search、deep-research | ✅ 覆盖 | 单次检索 + 多轮深度研究合成；web-search 有真实 search_client.py |
| 3 | **数据与表格处理** | excel-assistant、data-ml-science（7技能）、dataviz-studio（2技能） | ✅ 覆盖 | Excel 操作 + ETL/特征/建模/仿真/可视化 + 仪表盘/图表推荐 |
| 4 | **邮件与沟通** | internal-comms-writer、feishu-dingtalk-bridge | ⚠️ 部分覆盖 | 内部沟通写作 + IM webhook；无外部邮件撰写/管理（见缺口分析） |
| 5 | **日程与会议** | meeting-notes、task-scheduler | ⚠️ 部分覆盖 | 会议纪要 + 定时任务；无日历管理/会议调度（平台自带 lark-calendar） |
| 6 | **文件与文档管理** | file-organizer、batch-renamer、format-converter、docx-writer、docx-template-fill、pdf-pipeline、epub-builder | ✅ 深度覆盖 | 整理/重命名/格式转换/Word 生成/PDF 处理/EPUB 构建 |
| 7 | **购物与电商** | product-copywriter | ⚠️ 弱覆盖 | 仅文案；无电商平台运营（淘宝/京东/拼多多 主图/详情页/标题优化）（第三轮已评估，见缺口分析） |
| 8 | **金融与投资** | bank-statement-reconcile | ⚠️ 弱覆盖 | 仅银行对账；无投资分析/理财规划（高风险领域，见缺口分析） |
| 9 | **学习与教育** | edu-craft（3技能）、homework-autopilot（3技能） | ✅ 覆盖 | 课程设计/习题生成/费曼讲解 + 作业摄入/解题/去AI味 |
| 10 | **健康生活** | （无） | ❌ 未覆盖 | 无健康相关技能（高风险+LLM原生，见缺口分析） |
| 11 | **旅行出行** | （无） | ❌ 未覆盖 | 无旅行规划技能（LLM原生+research可覆盖，见缺口分析） |
| 12 | **编程开发** | programming 域 49 技能（18 子域） | ✅ 极深度覆盖 | 从需求规划→代码生成→调试→测试→CI/CD→部署→监控→安全，全链路 |
| 13 | **设计创作** | visual-design-studio（5技能）、image-studio（3技能） | ✅ 覆盖 | 设计需求解读→提示词→布局审计→前端设计→组件生成 + 图像生成/风格锚定 |
| 14 | **自动化与工作流** | task-scheduler、session-handoff、skill_chains.json | ✅ 覆盖 | 定时任务 + 会话交接 + 技能链编排 |
| 15 | **社交媒体运营** | 18 发布器 + growth-marketing（3技能） | ✅ 深度覆盖 | 16+ 平台适配 + 活动设计/渠道适配/文案 |
| 16 | **个人知识管理** | knowledge-base（2技能）、memory-systems（4技能） | ✅ 覆盖 | 知识图谱 + 个人 Wiki + 记忆架构/提取/管理/检索 |
| 17 | **网页操作与数据采集** | web-search（仅搜索） | ⚠️ 弱覆盖 | 无结构化网页数据提取/爬虫/表单填写/页面监控（**候选缺口**） |
| 18 | **图片处理与编辑** | image-generation（生成）、format-converter（格式） | ⚠️ 弱覆盖 | 无批量压缩/加水印/裁剪/OCR 文字提取（**候选缺口**） |
| 19 | **API 调用与数据集成** | api-design-reviewer、api-test-suite-builder、mcp-server-builder | ⚠️ 部分覆盖 | 覆盖 API 设计/测试/MCP 构建；无"调用公开 API 获取并处理数据"的用户侧技能 |
| 20 | **密码与安全** | env-secrets-manager、secrets-vault-manager、pii-redactor、prompt-injection-guard | ✅ 覆盖 | 开发侧密钥管理 + PII 脱敏 + 提示注入防护 |

---

## 二、业界 Benchmark 对照

| 业界清单类别 | 代表技能 | skillkit 对应 | 状态 |
|---|---|---|---|
| Anthropic 基础技能 | PPT/Excel/Word/PDF 文档生成 | ppt-builder、excel-assistant、docx-writer、pdf-pipeline | ✅ 已覆盖 |
| Anthropic 文档与资产创建 | frontend-design、品牌指南 | visual-design-studio、frontend-design-director | ✅ 已覆盖 |
| aihero.dev 工程技能 | TDD、codebase-design、domain-modeling、grilling | tdd-guide、senior-architect、code-intent-planner | ✅ 已覆盖 |
| aihero.dev 生产力技能 | handoff、teach、wait-what、writing-for-agents | session-handoff、feynman-explainer、skill-author | ✅ 已覆盖 |
| agnt.gg Top 100 | Content Research Writer、Blog Writer | ai-research-writing 全链路 | ✅ 已覆盖（更深） |
| agnt.gg Top 100 | Code Reviewer、PR Review | code-reviewer（含 PR Diff Mode） | ✅ 已覆盖 |
| agnt.gg Top 100 | Social Media Scheduler、WordPress Publisher | 18 发布器 + cross-post-orchestrator | ✅ 已覆盖（更广） |
| DataCamp 营销技能 | social-content-strategy、copywriting | growth-marketing 三技能 | ✅ 已覆盖 |
| DataCamp 数据技能 | data-analysis、chart-generation | data-ml-science、dataviz-studio | ✅ 已覆盖 |
| **业界常见但 skillkit 没有** | **Web Scraping / Data Extraction** | web-search（仅搜索） | ⚠️ 候选缺口 |
| **业界常见但 skillkit 没有** | **Image Editing / Batch Photo Processing** | image-generation（仅生成） | ⚠️ 候选缺口 |
| 业界常见但 skillkit 没有 | Email Writer / Inbox Manager | internal-comms-writer（仅内部） | ❌ 评估后不建议 |
| 业界常见但 skillkit 没有 | Travel Planner / Itinerary | deep-research + 通用写作 | ❌ 评估后不建议 |
| 业界常见但 skillkit 没有 | Finance / Stock Analysis | bank-statement-reconcile | ❌ 评估后不建议 |

---

## 三、候选缺口严格评估

### 候选 1：网页数据采集与浏览器操作（web-data-extraction）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 从网页提取结构化数据（商品价格、表格、文章列表）、填写在线表单、监控页面变化、处理 JS 渲染/分页/反爬 |
| **AI agent 高频使用？** | 是。"帮我把这个网页的表格导出来"、"爬取这个目录页所有链接"、"监控这个页面价格变化"是高频请求 |
| **LLM 原生能做？** | 部分。LLM 能写 Python 爬虫，但反爬处理、JS 渲染、XPath/CSS 选择器策略、数据清洗流水线是领域知识，LLM 不可靠 |
| **Harness 平台自带？** | 平台有 web.fetch（获取页面内容）和 computer_use_tool/bu（浏览器操作），但无结构化采集工作流指导 |
| **现有技能覆盖？** | web-search 仅做搜索，不提取页面结构化数据；deep-research 做研究合成，不做数据采集 |
| **国内平台适配？** | 淘宝/京东/大众点评/微博等国内网站反爬严格，需要专门策略 |
| **结论** | **建议新增**。这是最明显的缺口：搜索≠采集，平台有工具但无工作流技能。可命名 `web-data-extractor`，归属新包或并入 knowledge-base。核心价值：结构化提取模式、反爬应对、分页/登录处理、数据清洗输出 |

### 候选 2：图片批处理与编辑（image-batch-processor）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 批量压缩/裁剪/缩放/加水印/格式转换、从图片提取文字（OCR）、图片拼接/分割 |
| **AI agent 高频使用？** | 中高频。"把这些图片压缩到 200KB 以下"、"给所有图片加右下角水印"、"提取这张截图里的文字" |
| **LLM 原生能做？** | 不能直接操作图片文件。需要 Pillow/ImageMagick 等工具调用 |
| **Harness 平台自带？** | 平台有 image_edit（单图编辑）和 image_gen（生成），但无批量处理和 OCR |
| **现有技能覆盖？** | image-generation 仅生成；format-converter 做通用格式转换（含图片但无图片专项参数）；layout-spec-auditor 做尺寸审计 |
| **国内平台适配？** | 微信/小红书/淘宝对图片大小尺寸有严格限制，批量处理需求强 |
| **结论** | **建议新增（轻量）**。批量处理是 image-generation 不覆盖的明确场景。可命名 `image-batch-processor`，归属 image-studio 包。核心价值：批量压缩/水印/裁剪/OCR 的 Pillow 工作流 + 各平台尺寸速查表（部分已在 image-generation 中，可复用）。但需注意与 format-converter 的边界 |

### 候选 3：邮件撰写与管理（email-writer）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 撰写商务邮件、管理收件箱、邮件分类/回复/跟进 |
| **AI agent 高频使用？** | 高 |
| **LLM 原生能做？** | 邮件撰写本质是写作，LLM 原生能力强 |
| **现有技能覆盖？** | internal-comms-writer 覆盖内部沟通；article-drafter + content-editor 可覆盖外部邮件写作 |
| **结论** | **不建议新增**。邮件撰写是 LLM 原生能力 + 现有写作技能可覆盖。邮件管理（收件箱）需要 IMAP/SMTP 集成，属于平台工具范畴 |

### 候选 4：电商平台运营（e-commerce-ops）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 淘宝/京东/拼多多 商品标题优化、主图设计、详情页生成、竞品分析 |
| **AI agent 高频使用？** | 中（针对电商从业者） |
| **现有技能覆盖？** | product-copywriter（文案）、image-generation（主图）、seo-optimizer（标题关键词）、18 发布器（内容发布） |
| **第三轮评估结论** | 已拒绝——"product-copywriter + visual-design-studio + image-studio 已覆盖从产品事实到视觉资产的链路" |
| **新论据？** | 无。电商运营的核心操作（标题/主图/详情页）可由现有技能组合完成；平台后台操作（上架/改价）需要 API 集成，非技能范畴 |
| **结论** | **不建议新增**（维持第三轮结论） |

### 候选 5：旅行规划（travel-planner）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 行程规划、机票酒店比较、攻略生成 |
| **LLM 原生能做？** | 行程规划是 LLM 原生推理 + 搜索能力 |
| **现有技能覆盖？** | deep-research（攻略调研）+ article-outliner（行程结构化） |
| **结论** | **不建议新增**。LLM 原生 + 现有 research 技能可覆盖 |

### 候选 6：金融投资分析（finance-analyst）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 股票筛选、投资组合分析、理财规划 |
| **风险** | 高风险受监管领域，AI 提供投资建议有合规风险 |
| **现有技能覆盖？** | bank-statement-reconcile（对账）、data-ml-science（数据分析） |
| **结论** | **不建议新增**。高风险 + LLM 原生推理 + 合规限制 |

### 候选 7：健康管理（health-manager）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 饮食/运动/睡眠记录与建议 |
| **风险** | 医疗健康建议有安全风险 |
| **第三轮评估结论** | 已拒绝——"LLM 原生，非明确非 LLM 原生缺口" |
| **结论** | **不建议新增**（维持第三轮结论） |

### 候选 8：API 数据获取（api-data-fetcher）

| 评估维度 | 判断 |
|---|---|
| **场景描述** | 调用公开 API（天气/股票/地图）获取数据并处理 |
| **LLM 原生能做？** | LLM 能写 Python requests 代码调用 API |
| **现有技能覆盖？** | programming 域技能覆盖代码生成；api-test-suite-builder 覆盖 API 测试 |
| **结论** | **不建议新增**。API 调用是 LLM 原生代码能力，编程技能可覆盖 |

---

## 四、最终结论

### 覆盖度总评

**20 类线上操作场景中：**
- ✅ **深度覆盖**：8 类（内容创作、搜索、数据表格、文件文档、编程、设计、自动化、社交媒体、知识管理、安全）——实际 10 类
- ⚠️ **部分/弱覆盖**：6 类（邮件沟通、日程会议、电商、金融、网页采集、图片处理、API）——实际 7 类
- ❌ **未覆盖但评估后不需新增**：3 类（健康、旅行、邮件管理）

### 明确建议新增的技能（2 个）

| 优先级 | 技能名 | 归属包 | 核心理由 |
|---|---|---|---|
| **P0** | `web-data-extractor` | 新建 `web-ops` 包或并入 `knowledge-base` | 搜索≠采集。结构化网页数据提取、反爬应对、分页/登录处理是 LLM 不可靠的领域知识，平台有浏览器工具但无工作流。国内网站反爬严格，需求真实 |
| **P1** | `image-batch-processor` | `image-studio` | 批量压缩/水印/裁剪/OCR 是 image-generation（仅生成）不覆盖的明确场景。平台有单图编辑但无批量处理。轻量技能，Pillow 工作流即可 |

### 不建议新增的方向（已有覆盖或 LLM 原生）

邮件撰写、旅行规划、金融投资、健康管理、电商运营、API 数据获取、提示词调试、数据分析报告、学习计划、文件备份、跨技能编排——均已有技能覆盖或为 LLM 原生能力，维持前几轮评估结论。

### 覆盖证据

skillkit 的 153 技能在内容创作（写作+视频+音频+图像+发布）和编程开发两大领域达到业界领先深度；办公文档、数据处理、知识管理、设计创作均有完整链路。主要薄弱环节集中在"网页数据采集"和"图片批量处理"两个工具型操作场景。
