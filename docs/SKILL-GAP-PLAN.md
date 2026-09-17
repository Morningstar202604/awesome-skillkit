# awesome-skillkit 能力域补全计划

> 编制日期：2026-09-17 · 基线：v0.16.1（127 技能 / 31 包 / 13 链域 48 链）
> 目标：对标 6 个主流 skill 生态来源，补齐**真实空白域**，产出可安装场景包

---

## 一、调研方法

对比以下来源的**技能分类分布**（只学分类思路与缺口，不复制内容）：

| 类别 | 来源 | 观察到的重点 |
|------|------|------------|
| 大厂官方 | Anthropic `anthropics/skills`（17 技能 / 5 类） | 文档四件套 + 设计生成 + 开发工具 + 品牌通讯 + **元技能** |
| 大厂官方 | OpenAI `openai/skills` | **元技能为主**：skill-creator / plan / skill-installer（六级作用域） |
| 大厂官方 | Google `google-gemini/gemini-skills`、`google-labs-code/stitch-skills` | API/SDK 集成、设计工具链 |
| 大厂官方 | Vercel `vercel-labs/agent-skills` | 前端最佳实践、**find-skills（技能商店）**、Remotion 视频 |
| 大厂官方 | HuggingFace `huggingface/skills` | ML 全流程：数据集→训练→评估→论文发布 |
| 大厂官方 | Microsoft `microsoft/agent-skills` | Azure 服务、文档智能 |
| 社区头部 | ComposioHQ / travisvn / VoltAgent / obra superpowers | **工具与自动化**、文件整理、集成类（Jira/Slack/Notion/CRM）、浏览器自动化 |
| 社区头部 | K-Dense claude-scientific-skills | 科研计算专用 |
| 目录站 | awesomeclaude.ai（204 技能 / 13 类）、openagentskill.com | 分类全景与热度分布 |

**关键观察**：主流生态分布高度集中在 8 个域——①文档产出 ②开发与测试 ③**工具与自动化** ④**外部集成** ⑤设计与视觉 ⑥数据与可视化 ⑦**元技能** ⑧知识与记忆。我们已在 ①③⑤⑥⑧ 有布局，**②④⑦ 是明显空白**。

---

## 二、缺口矩阵（实测对照）

| 域 | 现状 | 判断 |
|----|------|------|
| 文档产出 | docx-writer / pdf-pipeline / ppt-builder / excel-assistant ✅ | **基本够**，缺 EPUB（电子书）与 Markdown 工作流 |
| 开发与测试 | 上游 33 个编程技能 + webapp-flow-tester ✅ | **够** |
| 工具与自动化 | 仅 file 相关零散 | 🔴 **几乎空白** — 文件整理、批量重命名、定时任务、邮件、格式转换 |
| 外部集成 | 只有 git/GitHub 部分 | 🔴 **空白** — Notion / 飞书 / 钉钉 / 企业微信 / Slack / Jira / CRM / 云盘 |
| 元技能 | 只有 skill-tester（在 agent 包） | 🔴 **空白** — skill 生成器、技能发现、规范校验 |
| 设计与视觉 | 4 包 12 技能 ✅ | **够** |
| 数据与可视化 | result-visualizer / figure-maker | 🟡 **偏弱** — 缺仪表盘、交互式图表、表格数据转换 |
| 知识与记忆 | memory 4 技能 ✅ | 🟡 缺**个人知识库**（wiki/笔记系统、知识图谱） |
| 安全 | 2 个 secrets 技能 | 🟡 缺 PII 脱敏、提示注入防御 |

---

## 三、补全方案（5 个新场景包 / 16 个新技能）

### 包 1 · `Toolsmith`（工具与自动化）🔴 优先级最高

> 对标：ComposioHQ/file-organizer、invoice-organizer、obra/superpowers

| 技能 | 解决什么 | 形态 |
|------|---------|------|
| `file-organizer` | 按类型/日期/内容智能整理文件与文件夹，带去重与预演 | 脚本型 + dry-run |
| `batch-renamer` | 批量重命名（正则/序号/EXIF 日期/模板） | 脚本型 |
| `format-converter` | 文档/图片/音视频格式转换统一入口（pandoc/ffmpeg/imagemagick） | 脚本型 |
| `task-scheduler` | 用 cron/at 或平台计划任务落地定时自动化 | 提示型 + 脚本 |

### 包 2 · `Workspace Integrations`（外部集成）🔴 优先级最高

> 对标：Microsoft/Azure、linear-claude-skill、slack、hubspot-admin-skills

| 技能 | 解决什么 | 形态 |
|------|---------|------|
| `notion-workspace` | Notion 页面/数据库读写、批量导出导入 | MCP/API |
| `feishu-dingtalk-bridge` | 飞书 / 钉钉 / 企业微信：消息、文档、多维表格、审批 | API |
| `issue-tracker-sync` | Jira / Linear / GitHub Issues 三向同步与周报生成 | API |
| `cloud-drive-manager` | 网盘（百度/阿里/OneDrive）批量上传下载归档 | API |

### 包 3 · `Skill Forge`（元技能）🔴 对标 OpenAI

> 对标：OpenAI skill-creator/plan/skill-installer、find-skills、SkillCheck

| 技能 | 解决什么 | 形态 |
|------|---------|------|
| `skill-author` | 从需求生成合规 SKILL.md（frontmatter + 十诫骨架 + 自检） | 提示型 + 模板 |
| `skill-linter` | 校验技能规范（命名/描述/触发词/行数/参考文件完整性） | 脚本型 |
| `skill-finder` | 在本仓库与外部市场检索、推荐、装配技能组合 | 脚本型 |

### 包 4 · `Knowledge Base`（知识与知识图谱）🟡

> 对标：karpathy-llm-wiki、swarmvault、tapestry

| 技能 | 解决什么 | 形态 |
|------|---------|------|
| `personal-wiki` | 从零散资料构建可检索个人 wiki（分片索引） | 脚本型 |
| `knowledge-graph-builder` | 把文档/代码转成可查询知识图谱 | 脚本型 |

### 包 5 · `Data Viz Studio`（数据可视化增强）🟡

> 对标：D3.js Visualization、UI UX Pro Max 图表库

| 技能 | 解决什么 | 形态 |
|------|---------|------|
| `dashboard-designer` | 从数据生成可交互仪表盘（HTML/Plotly） | 脚本型 |
| `chart-recommender` | 数据特征 → 推荐图型 + 配色 + 标注规范 | 提示型 + 词库 |

### 顺带补强（不新建包）

- `office-productivity` + `epub-builder`（Markdown/txt → EPUB 电子书）
- `security` + `pii-redactor`（PII 检测脱敏）、`prompt-injection-guard`（提示注入防御）

---

## 四、执行节奏

| 批次 | 内容 | 技能数 | 产出 |
|------|------|:---:|------|
| P0 | Toolsmith + Skill Forge | 7 | v0.17.0 |
| P1 | Workspace Integrations | 4 | v0.18.0 |
| P2 | Knowledge Base + Data Viz Studio + 补强项 | 5 | v0.19.0 |

**每个技能的交付规范**（沿用仓库既有标准）：

1. `SKILL.md`：全中文正文 + frontmatter 机器层（英文 description + ≥5 中英双语触发词 + category/pattern/tier/verified-date）
2. 骨架 10 章节：输入清单 / 前置自检 / 工作流 / 交付标准 / 失败处置表 / 参考
3. 脚本型技能必须**实测通过**并附输出；
4. 参考文件方法论蒸馏，`references/sources-and-methodology.md` 署名，**零内容复制**；
5. 全部注册进 `manifest.json` 与 `skill_chains.json` 链域。

**质量门禁**：`validate_skills.py` 0 error → `pytest` 全绿 → `build.py` 32+ zip → 双平台推送 + Release 附件 → 站点快照同步。

---

## 五、红线

- ✅ 只学大厂技能的**分类思路与问题定义**，逐字原创
- ❌ 不复制、不翻译、不改写任何第三方 SKILL.md 正文与脚本
- ✅ 触达外部服务的技能默认 **dry-run**，凭证只走环境变量，不落盘
- ✅ 涉及云平台/网盘/办公套件的技能，明确标注所需凭证与最小权限

---

## 六、待办清单

- [ ] P0-A：Toolsmith 包 4 技能
- [ ] P0-B：Skill Forge 包 3 技能
- [ ] 注册 manifest + skill_chains + CHANGELOG，发版 v0.17.0
- [x] P1：Workspace Integrations 4 技能 → v0.18.0
- [ ] P2：Knowledge Base 2 + Data Viz 2 + 补强 3 → v0.19.0
- [ ] 三语言 README 数据刷新（每次发版）
