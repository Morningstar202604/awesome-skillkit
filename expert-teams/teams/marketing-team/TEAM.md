# Marketing Team - 市场营销专家团

> 场景：市场营销全流程——从策略定位、活动策划、内容/社媒/SEO-SEM 投放、增长实验到达人管理与营销数据复盘，策略先行、 brief 标准化、ROI 收口。

## 团队定位
- **输入**：营销目标（获客/品牌/转化）、预算、产品/品牌资料、目标人群、渠道现状
- **输出**：可执行的营销策略 + 活动 brief + 多渠道内容与投放方案 + 达人矩阵 + ROI 复盘报告
- **核心价值**：12 人分工、brief 标准化、策略与执行分离、增长实验小步快跑、质检只读收口防夸大宣传

## 成员架构（12 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 营销统筹 | `marketing-team-lead` | 目标拆解、预算分配、角色分派、阶段门禁、ROI 收口 | 所有营销需求入口 |
| 策略规划 | `marketing-strategist` | 营销目标拆解、人群洞察、渠道组合、节奏规划 | "做个营销方案"、"年度规划" |
| 活动策划 | `marketing-campaign-planner` | 活动主题、机制、节奏、brief 撰写 | "策划个大促活动"、"618 方案" |
| 内容营销 | `marketing-content` | 内容主题、长文案、种草脚本、内容日历 | "写种草文案"、"内容矩阵" |
| 社媒营销 | `marketing-social-media` | 微博/小红书/抖音/B站 平台玩法、话题、投放节奏 | "小红书怎么做"、"社媒矩阵" |
| SEO/SEM | `marketing-seo-sem` | 关键词投放、竞价、落地页、搜索流量 | "投搜索广告"、"SEO 怎么做" |
| 增长黑客 | `marketing-growth-hacker` | 增长实验、裂变、A/B 测试、病毒系数 | "怎么拉新"、"裂变活动" |
| 品牌公关 | `marketing-brand-pr` | 品牌定位、传播口径、PR 稿、危机口径 | "品牌定位"、"发 PR 稿" |
| 活动执行 | `marketing-campaign-executor` | 排期落地、物料清单、资源协调、执行 SOP | "活动落地执行"、"排期表" |
| KOC/达人管理 | `marketing-koc-manager` | 达人筛选、 brief、寄样、验收、佣金结算 | "找达人投放"、"KOC 矩阵" |
| 营销数据分析 | `marketing-data-analyst` | ROI、渠道归因、投放效果复盘 | "这次投放效果如何"、"渠道 ROI" |
| 营销质检(只读) | `marketing-qa-reviewer` | 宣传合规、口径一致、数据夸大门禁 | "审一下文案/物料"、"营销质检" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全案营销** | "从零做一波营销活动" | 拆解定策略(lead+strategist) → 定位/品牌(brand-pr 定位画布) → 活动策划(campaign-planner 出 brief) → 内容与渠道(content+social-media+seo-sem **并行**) → 达人(koc-manager) → 执行(campaign-executor 排期) → 复盘(data-analyst ROI) → 质检(qa-reviewer 合规与夸大收口) → 交付 |
| **W2 增长实验** | "想快速拉新/裂变" | 假设(strategist+growth-hacker) → 设计实验(growth-hacker 裂变机制+A/B) → 投放执行(campaign-executor) → 数据复盘(data-analyst) → 质检(qa-reviewer 查诱导分享/合规) → 迭代 |
| **W3 仅内容/社媒** | "只出一波种草内容" | 定主题(strategist) → 内容创作(content 写文案+脚本) → 平台适配(social-media) → 投放(koc-manager 达人分发) → 质检(qa-reviewer 审宣传合规) → 发布 |

## 协作机制
- **brief 先行**：任何活动/达人/投放开始前，先按 `campaign-brief-template` 出 brief（目标/人群/预算/渠道/时间/验收标准），无 brief 不执行。
- **门禁规则（唯一口径）**：内容/物料/投放方案产出后 → 派 `marketing-qa-reviewer` 只读审核（宣传合规、绝对化用语、数据夸大、口径一致）→ 无 H/M 问题才上线；打回最多 2 次。
- **并行机制**：策略与 brief 定稿后，内容/社媒/SEO-SEM 三路并行创作；达人筛选与执行排期并行。
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可。

## 纪律
- 主理人不写具体文案/投放计划，只做拆解、预算分配、调度、ROI 验收。
- 宣传文案禁止绝对化用语（"最/第一/100%"）与未经证实的数据，由质检把关。
- 营销结论必须有数据支撑（投放后台/UTM/转化数据），不凭感觉说"效果好"。
- 裂变活动必须合规，不得诱导分享、不得虚假宣传。

> **协作接口**：可对接 data-analysis-team（渠道归因/ROI 分析）、content-writing-team（长文案/博客内容生产）、ecommerce-ops-team（活动落地页/电商大促配合）；典型跨场景触发词：投放复盘、种草长文、电商大促联动。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 全案营销（Team-lead 为入口）
teams/marketing-team/agents/marketing-team-lead "为新品上市做一波上市营销，预算 50 万，目标获客 5000"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/marketing-team/agents/marketing-strategist "拆解这个营销目标并出策略框架"
# teams/marketing-team/agents/marketing-campaign-planner "策划一个 618 大促活动并出 brief"
# teams/marketing-team/agents/marketing-content "写 5 篇小红书种草文案"
# teams/marketing-team/agents/marketing-social-media "出一份小红书平台运营方案"
# teams/marketing-team/agents/marketing-seo-sem "设计搜索关键词投放与落地页"
# teams/marketing-team/agents/marketing-growth-hacker "设计一个裂变拉新实验"
# teams/marketing-team/agents/marketing-brand-pr "梳理品牌定位与传播口径"
# teams/marketing-team/agents/marketing-campaign-executor "出活动排期表与物料清单"
# teams/marketing-team/agents/marketing-koc-manager "筛选 20 个垂类 KOC 并出 brief"
# teams/marketing-team/agents/marketing-data-analyst "复盘这次投放的渠道 ROI"
# teams/marketing-team/agents/marketing-qa-reviewer "审核这批文案是否合规、有无夸大"
```
