# Content Writing Team - 内容创作专家团队

> 场景：全链路中文内容生产托管——从选题定位、长文/社媒/短视频/广告/故事成稿、标题打磨、多平台改编到事实核查与终检，一次 brief 交付多端终稿。

## 团队定位
- **输入**：内容 brief（目标、读者、平台、调性、KPI、素材/参考）
- **输出**：多平台终稿（含标题组、发布建议）、事实核查通过、品牌调性一致
- **核心价值**：14 人串行闭环、主理人全程把关品牌一致性与平台不串味

## 成员架构（14 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 内容总指挥 | `content-team-lead` | brief 拆解、选题路线、分工排期、品牌一致性、终审 | 所有内容需求入口 |
| 内容策略师 | `content-strategist` | 受众洞察、内容支柱、信息架构 | "写给谁看"、"内容定位" |
| 排期师 | `content-planner` | 选题日历、节点排播、产能与复盘指标 | "排个发布日历"、"月度内容规划" |
| 长文作者 | `content-article-writer` | 深度长文、白皮书、专栏、万字稿 | "写篇深度稿"、"白皮书" |
| 社媒作者 | `content-social-media-writer` | 小红书/微博/知乎/朋友圈短帖 | "写小红书"、"发个微博" |
| 短视频编剧 | `content-short-video-scriptwriter` | 口播稿、分镜表、前 3 秒钩子 | "写个抖音脚本"、"分镜" |
| 广告文案 | `content-copywriter` | slogan、落地页、电商详情、EDM | "写个 slogan"、"落地页文案" |
| 叙事作者 | `content-storyteller` | 品牌故事、人物稿、叙事软文 | "写品牌故事"、"人物特稿" |
| 标题专家 | `content-title-expert` | 爆款标题、封面大字、A/B 标题组 | "想几个标题"、"封面文案" |
| SEO 作者 | `content-seo-writer` | 关键词布局、TDK、长尾文 | "做 SEO 文"、"关键词" |
| 本地化作者 | `content-localization-writer` | 跨语言/跨区域改写、文化适配 | "改成粤语版"、"海外版" |
| 编辑 | `content-editor` | 删冗余、顺逻辑、润声腔、错别字 | "润一下稿"、"改稿子" |
| 多平台适配师 | `content-multiplatform-adaptor` | 一稿多投、平台调性/字数适配 | "一篇发多平台" |
| 审读官 | `content-reviewer` | 事实核查、合规红线、原创度终检（只读） | "终检"、"事实核查" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 完整内容项目** | "从选题写到发布全程托管" | Phase 0(lead+strategist/planner **并行**)→1(主笔成稿)→2(title-expert→editor **串行**)→3(multiplatform-adaptor)→4(reviewer+lead 终审) |
| **W2 单点创作** | "只帮我写一篇/一段" | 按路由表直调对应主笔；润色走 editor；终检走 reviewer |
| **W3 批量矩阵** | "一个主题出 N 篇多平台" | planner 出矩阵排期→按平台分派主笔→统一 title/editor→reviewer 抽检 |

## 协作机制
- **技能调用协议**：每 Phase 前必扫 `skills/`，命中即用、严格按其执行
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可
- **思想纪律**：忠于 brief、不绕圈、出错即停（2–3 轮无解即回传复核）
- **自检闸门**：`content-quality-checklist` A 组开工前/B 组产出后，任一不过即停
- **一致性终审**：选题—大纲—成稿—改编—标题首尾咬合，不平台串味
- **原创零容忍**：全程禁止洗稿/复制网文，引用必标来源

## 技能依赖
团队专用 skills 目录：`teams/content-writing-team/skills/`
核心 skills：`content-strategy-canvas`（策略画布）、`title-crafting-guide`（标题）、`multi-platform-adaptation-guide`（多端改编）、`copywriting-framework`（广告文案框架）、`seo-writing-guide`（SEO 写作）、`content-quality-checklist`（质检闸门）。

> **协作接口**：可对接 visual（图文配图/海报文案）、video（短视频脚本/口播稿）、academic（科普/学术传播）、software/fullstack（技术博客/产品文案）；典型跨场景触发词：小红书图文、抖音脚本、技术博客、产品文案。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 完整内容项目托管（Team-lead 为入口）
teams/content-writing-team/agents/content-team-lead "帮我从选题写到发布，全程托管"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/content-writing-team/agents/content-strategist "帮我做受众与内容定位"
# teams/content-writing-team/agents/content-planner "排一个月发布日历"
# teams/content-writing-team/agents/content-article-writer "写一篇 5000 字深度稿"
# teams/content-writing-team/agents/content-social-media-writer "写小红书种草帖"
# teams/content-writing-team/agents/content-short-video-scriptwriter "写 60 秒抖音口播脚本"
# teams/content-writing-team/agents/content-copywriter "写电商详情页文案"
# teams/content-writing-team/agents/content-storyteller "写品牌故事"
# teams/content-writing-team/agents/content-title-expert "给这稿想 5 个标题"
# teams/content-writing-team/agents/content-seo-writer "写一篇 SEO 长尾文"
# teams/content-writing-team/agents/content-localization-writer "把这稿改成粤语版"
# teams/content-writing-team/agents/content-editor "润色这篇稿子"
# teams/content-writing-team/agents/content-multiplatform-adaptor "把长文改成小红书/微博版"
# teams/content-writing-team/agents/content-reviewer "终检前做事实核查"
```
