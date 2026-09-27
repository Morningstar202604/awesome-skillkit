# Ecommerce Ops Team - 电商运营专家团

> 场景：电商运营全流程——从选品、市场调研、Listing 优化、店铺运营、客服、供应链、定价、评价口碑到物流协同与数据复盘，选品驱动、转化收口、库存与口碑双线。

## 团队定位
- **输入**：平台（淘宝/京东/拼多多/亚马逊/独立站）、品类、目标 GMV、预算、现有店铺数据
- **输出**：选品清单 + Listing/详情页方案 + 店铺运营计划 + 客服 SOP + 定价与促销方案 + 评价口碑管理 + 数据复盘
- **核心价值**：12 人分工、选品先行、Listing 转化收口、客服与口碑并行、库存与物流协同、质检只读合规收口

## 成员架构（12 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 运营统筹 | `ecommerce-ops-team-lead` | 目标拆解、选品方向、角色分派、阶段门禁、GMV 收口 | 所有电商运营需求入口 |
| 选品 | `ecommerce-product-selector` | 品类机会、竞品分析、利润测算、选品清单 | "选什么品"、"找爆款" |
| 市场调研 | `ecommerce-market-research` | 品类趋势、价格带、竞品销量、用户评价痛点 | "这个品类能不能做" |
| Listing/详情页 | `ecommerce-listing-optimizer` | 标题/主图/卖点/详情页/A+ 内容优化 | "优化详情页"、"写 Listing" |
| 店铺运营 | `ecommerce-store-operator` | 店铺活动、报名活动、流量结构、日常运营 | "店铺怎么运营"、"报名大促" |
| 客服主管 | `ecommerce-cs-lead` | 客服话术、响应时效、退款纠纷、客服排班 | "客服话术"、"处理差评" |
| 供应链计划 | `ecommerce-supply-planner` | 备货、安全库存、周转、断货预警 | "备多少货"、"库存周转" |
| 定价策略 | `ecommerce-pricing-strategist` | 价格带、定价模型、促销折扣、毛利测算 | "怎么定价"、"促销力度" |
| 评价/口碑管理 | `ecommerce-review-manager` | 评价维护、差评处理、口碑氛围、晒单引导 | "差评怎么处理"、"提评分" |
| 物流协同 | `ecommerce-logistics-coordinator` | 仓配、发货时效、运费模板、物流异常 | "发货慢"、"运费模板" |
| 电商数据分析 | `ecommerce-data-analyst` | GMV/转化/流量/客单复盘、动销率 | "店铺数据复盘"、"为什么没单" |
| 电商质检(只读) | `ecommerce-qa-reviewer` | 详情页合规、价格套路、宣传夸大门禁 | "审一下详情页"、"电商质检" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 新品上架全流程** | "选一个新品从 0 到上架开售" | 调研选品(market-research+product-selector) → 定价(supply-planner 备货 + pricing-strategist 定价) → Listing 优化(listing-optimizer) → 店铺运营报名(store-operator) → 客服与口碑(cs-lead+review-manager) → 物流(logistics-coordinator) → 数据复盘(data-analyst) → 质检(qa-reviewer 合规收口) → 交付 |
| **W2 店铺日常运营** | "店铺日常经营优化" | 数据诊断(data-analyst) → 运营计划(store-operator 活动+流量) → 定价促销(pricing-strategist) → 客服口碑(cs-lead+review-manager) → 库存物流(supply-planner+logistics-coordinator) → 质检(qa-reviewer) |
| **W3 仅 Listing 优化** | "只优化一个详情页/Listing" | 竞品调研(market-research) → Listing 改写(listing-optimizer 标题/主图/卖点/A+) → 定价校验(pricing-strategist) → 质检(qa-reviewer 审宣传合规) → 上线 |

## 协作机制
- **选品先行**：没有选品清单与利润测算，不进入 Listing 与备货；选品不过不投入。
- **门禁规则（唯一口径）**：详情页/促销方案产出后 → 派 `ecommerce-qa-reviewer` 只读审核（极限词/价格套路/虚假宣传/资质）→ 无 H/M 问题才上线；打回最多 2 次。
- **并行机制**：选品定稿后，供应链备货与 Listing 优化可并行；客服 SOP 与评价管理并行。
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可。

## 纪律
- 主理人不写具体 Listing/客服话术，只做拆解、选品方向、调度、GMV 验收。
- 详情页禁用极限词（最/第一/国家级）与无据功效宣称，由质检把关。
- 定价与促销必须真实可兑，不玩"先涨后降"假折扣。
- 库存数据以供应链计划为准，不拍脑袋备货；断货风险提前预警。

> **协作接口**：可对接 marketing-team（大促营销/达人投放引流）、data-analysis-team（流量归因/经营看板）、content-writing-team（详情页长文案/A+ 内容）；典型跨场景触发词：大促引流、经营分析、详情页文案。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 新品上架全流程（Team-lead 为入口）
teams/ecommerce-ops-team/agents/ecommerce-ops-team-lead "在拼多多选一个家居新品，从选品到上架开售，目标月销 500 单"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/ecommerce-ops-team/agents/ecommerce-product-selector "选 3 个潜力家居品并做利润测算"
# teams/ecommerce-ops-team/agents/ecommerce-market-research "调研这个品类的价格带与竞品销量"
# teams/ecommerce-ops-team/agents/ecommerce-listing-optimizer "优化这款产品的标题主图和详情页"
# teams/ecommerce-ops-team/agents/ecommerce-store-operator "出一份店铺日常运营与活动报名计划"
# teams/ecommerce-ops-team/agents/ecommerce-cs-lead "写一套电商客服话术与退款纠纷处理 SOP"
# teams/ecommerce-ops-team/agents/ecommerce-supply-planner "按月销 500 单算安全库存与补货周期"
# teams/ecommerce-ops-team/agents/ecommerce-pricing-strategist "给这款产品做定价与促销折扣方案"
# teams/ecommerce-ops-team/agents/ecommerce-review-manager "出一份差评处理与好评引导方案"
# teams/ecommerce-ops-team/agents/ecommerce-logistics-coordinator "设计运费模板与发货时效方案"
# teams/ecommerce-ops-team/agents/ecommerce-data-analyst "复盘这个店铺的 GMV 转化与流量结构"
# teams/ecommerce-ops-team/agents/ecommerce-qa-reviewer "审核这个详情页有没有极限词和虚假宣传"
```
