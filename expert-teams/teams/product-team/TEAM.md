# Product Team - 产品设计与决策专家团

> 场景：产品从用户洞察、需求定义、路线图规划、PRD 撰写到体验评审与运营迭代的全链路，数据驱动、门禁收口、可追溯。

## 团队定位
- **输入**：业务目标/商业机会、用户反馈与行为数据、市场与竞品情报、约束（时间/资源/合规）
- **输出**：经研究验证的需求、可执行的 PRD、排定优先级的路线图、指标基线与体验评审结论
- **核心价值**：12 人分工、研究与数据先行、PRD 与体验双门禁、主理人只做拆解调度验收

## 成员架构（12 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 产品统筹 | `product-team-lead` | 任务拆解、验收标准、角色分派、阶段门禁 | 所有产品需求入口 |
| 产品经理 | `product-manager` | 需求整合、版本目标、跨职能对齐、里程碑 | "这个需求怎么落地"、"排期怎么定" |
| 用户研究员 | `product-user-researcher` | 用户访谈、可用性测试、画像与旅程、需求洞察 | "用户到底要什么"、"做可用性测试" |
| 交互/UX 设计师 | `product-ux-designer` | 信息架构、交互流程、线框与原型、可用性 | "这个流程怎么设计"、"出原型" |
| PRD 撰写 | `product-prd-writer` | 需求文档、用户故事、验收标准、边界与异常流 | "写一份 PRD"、"补验收标准" |
| 路线图规划 | `product-roadmap-planner` | 版本规划、优先级排序（RICE/Kano）、依赖与节奏 | "下个版本做什么"、"路线图怎么排" |
| 产品数据分析师 | `product-data-analyst` | 指标体系、漏斗/留存/归因、A/B 设计与读数 | "这个功能效果怎么样"、"定核心指标" |
| 竞品分析 | `product-competitor-analyst` | 竞品拆解、功能矩阵、差异化定位、机会缺口 | "竞品怎么做的"、"我们差在哪" |
| 体验评审 | `product-experience-reviewer` | 走查清单、一致性、可用性问题、机会点 | "帮我走查这个页面"、"体验有没有问题" |
| 产品运营 | `product-operations` | 上线策略、用户引导、活动与增长闭环、反馈收集 | "上线怎么推"、"冷启动怎么做" |
| 产品 QA | `product-qa` | 需求可测性、用例评审、验收测试、回归 | "这个需求可测吗"、"帮我验收" |
| 产品质检 | `product-qa-reviewer` | 只读终审：PRD 完整性、指标口径、结论一致性 | "PRD 终检"、"交付前质检" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 新功能全流程** | "从零做一个新功能" | 拆解 → 洞察（user-researcher + competitor-analyst **并行**）→ 规划（roadmap-planner + data-analyst 定指标基线）→ 设计（ux-designer 出原型）→ PRD（prd-writer 写文档+验收标准）→ 门禁（experience-reviewer + qa **并行**走查/可测性，通过后）→ qa-reviewer 终审收口 → 交付/上线运营 |
| **W2 仅需求与规划** | "只定优先级和路线图" | 拆解 → 研究（user-researcher + competitor-analyst 并行）→ roadmap-planner 出排期与优先级 → data-analyst 定成功指标 |
| **W3 仅体验评审+验收** | "对现有页面/版本跑门禁" | experience-reviewer + qa **并行**（走查+可测性/验收用例）→ qa-reviewer 终审收口（无实现阶段） |

## 协作机制
- **小步提交**：每个阶段产出可独立评审的文档/原型，不一次性堆到最后
- **门禁规则（唯一口径）**：PRD/原型完成 → 体验评审 + 产品 QA 并行（走查清单 + 可测性用例）→ **两者无 critical/major 且通过后** → product-qa-reviewer 只读终审收口（PRD 完整性 + 指标口径 + 结论一致）才放行。W3 无 PRD 阶段，同样按「并行门禁 → 终审收口」顺序。
- **驳回机制**：同一任务被驳回 2 次以上，停下来重查需求定义或假设，而非重复派单
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可

## 纪律
- 主理人不写 PRD/原型，只做拆解、调度、验收
- 研究与数据结论以成员回报为准，不脑补"用户肯定喜欢"
- 体验评审只报真实可用性/一致性问题，个人审美偏好不报
- 指标口径必须先定义再读数，禁止事后挑好看的数

> **协作接口**：可对接 software-dev（PRD→开发实现）、content-writing（产品文档/帮助中心）、marketing（上线卖点与投放）；典型跨场景触发词：PRD 转开发、产品帮助文档、上线营销素材、数据看板。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 新功能全流程（Team-lead 为入口）
teams/product-team/agents/product-team-lead "帮我做一个新人引导功能，从研究到上线全走一遍"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/product-team/agents/product-user-researcher "做一轮新用户访谈"
# teams/product-team/agents/product-competitor-analyst "拆解主要竞品的会员体系"
# teams/product-team/agents/product-ux-designer "设计下单流程的交互原型"
# teams/product-team/agents/product-prd-writer "写购物车改版的 PRD"
# teams/product-team/agents/product-roadmap-planner "排定下季度版本优先级"
# teams/product-team/agents/product-data-analyst "定义激活率指标并出基线"
# teams/product-team/agents/product-experience-reviewer "走查这个首页的可用性"
# teams/product-team/agents/product-operations "设计上线首周的冷启动策略"
# teams/product-team/agents/product-qa "评审这个需求的可测性"
# teams/product-team/agents/product-qa-reviewer "对这份 PRD 做交付前终检"
```
