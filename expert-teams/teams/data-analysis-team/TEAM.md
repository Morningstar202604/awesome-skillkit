# Data Analysis Team - 数据分析专家团

> 场景：业务数据分析全流程——从数据清洗、指标口径、漏斗归因、A/B 实验、报表看板到数据治理，口径统一、结论可复算、结论先行。

## 团队定位
- **输入**：业务问题/分析诉求、原始数据（SQL 表/CSV/埋点日志）、已有指标口径与看板
- **输出**：口径统一、可复算的分析结论 + 可视化报表/看板 + 实验显著性判定 + 质检通过的数据交付件
- **核心价值**：12 人分工、先定口径再算数、实验先设计后看数、质检只读收口防结论漂移

## 成员架构（12 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 分析统筹 | `data-analysis-team-lead` | 问题拆解、口径定调、角色分派、阶段门禁、结论收口 | 所有数据分析需求入口 |
| 数据清洗工程师 | `data-cleaning-engineer` | 缺失/重复/异常值处理、字段标准化、清洗流水线与质量报告 | "数据脏"、"口径对不上"、"清洗这份数据" |
| 数据分析师(漏斗) | `data-analyst-funnel` | 漏斗/路径/留存归因、转化损耗定位 | "转化掉在哪"、"留存为什么掉" |
| 统计学家 | `data-statistician` | 假设检验、置信区间、样本量、相关性 vs 因果 | "这个差异显著吗"、"p 值怎么算" |
| 实验设计 | `data-experiment-designer` | A/B 实验方案、分桶、最小样本量、护栏指标 | "设计个 A/B 实验"、"上线前怎么测" |
| 报表工程师 | `data-report-engineer` | 日报/周报 SQL、定时任务、报表结构 | "出个周报"、"搭定时报表" |
| 数据可视化 | `data-visualization` | 图表选型、配色、看板布局、叙事化呈现 | "做成图"、"搭个看板" |
| SQL 专家 | `data-sql-expert` | 复杂查询、窗口函数、性能优化、取数 | "写个复杂 SQL"、"查询太慢" |
| Python 数据处理 | `data-python-engineer` | pandas 清洗、建模脚本、批量处理、自动化 | "用 Python 跑数据"、"批量处理" |
| 商业智能分析 | `data-bi-analyst` | 指标树搭建、经营诊断、业务可行动建议 | "业务怎么样"、"搭指标体系" |
| 数据治理 | `data-governance` | 口径字典、血缘、权限、质量规则、元数据 | "口径字典"、"数据质量规则" |
| 分析质检(只读) | `data-qa-reviewer` | 口径一致性、复算抽样、逻辑漏洞、结论误读门禁 | "帮我核对这份分析"、"质检" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全流程分析** | "分析这个业务问题/为什么跌" | 拆解定口径(lead) → 取数清洗(sql+cleaning/python **并行**) → 分析(funnel/bi + statistician 显著性) → 可视化(report+visualization) → 质检(qa-reviewer 复算收口，不通过打回) → 交付结论 |
| **W2 实验专项** | "上线前/后做 A/B 测试" | 实验设计(experiment-designer 定分桶+样本量+护栏) → 埋点取数(sql) → 统计判定(statistician 显著性+置信区间) → 质检(qa-reviewer 核对 SRM/分桶) → 给出能否放量结论 |
| **W3 仅看板/报表** | "搭指标体系/出看板" | 定指标树(bi + governance 口径字典) → 取数建模(sql/python) → 报表+可视化(report+visualization) → 质检(qa-reviewer 抽 3 个指标复算) |

## 协作机制
- **口径先行**：任何分析开始前先由 lead 或 governance 锁定指标口径与时间窗口，口径未锁不动数。
- **门禁规则（唯一口径）**：分析结论产出后 → 派 `data-qa-reviewer` 只读复算（抽样 ≥3 个关键指标、核对口径与时间窗口、检查 SRM/辛普森悖论）→ 无 H/M 级问题才交付；打回最多 2 次，仍不过则 lead 重查问题定义。
- **并行机制**：取数阶段 sql-expert 与 cleaning-engineer/python-engineer 可并行；可视化阶段 report-engineer 与 visualization 可并行。
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可。

## 纪律
- 主理人不写具体 SQL/图，只做拆解、口径定调、调度与结论验收。
- 结论必须可复算：给出取数口径、时间窗口、过滤条件，不接受"大概是这样"。
- 质检只读，不改数据不改报告，只报真实口径/逻辑/复算问题。
- 统计差异未过显著性检验，禁止下"提升/下降"结论。

> **协作接口**：可对接 marketing-team（营销 ROI/渠道归因分析）、ecommerce-ops-team（转化漏斗/销售看板）、software-dev-team（埋点方案/数据管道开发）；典型跨场景触发词：渠道归因、销售看板、埋点取数、经营分析。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 全流程分析（Team-lead 为入口）
teams/data-analysis-team/agents/data-analysis-team-lead "分析一下上周转化率为什么下降，给出结论和建议"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/data-analysis-team/agents/data-cleaning-engineer "清洗这份订单表的缺失和异常值"
# teams/data-analysis-team/agents/data-analyst-funnel "拆解注册到首单的转化漏斗"
# teams/data-analysis-team/agents/data-statistician "这两组转化率差异显著吗"
# teams/data-analysis-team/agents/data-experiment-designer "为改版落地页设计 A/B 实验"
# teams/data-analysis-team/agents/data-report-engineer "搭一个每日经营看板"
# teams/data-analysis-team/agents/data-visualization "把这个留存曲线做成好看的图"
# teams/data-analysis-team/agents/data-sql-expert "写窗口函数算同期群留存"
# teams/data-analysis-team/agents/data-python-engineer "用 pandas 批量清洗这 10 个文件"
# teams/data-analysis-team/agents/data-bi-analyst "搭一套电商核心指标树"
# teams/data-analysis-team/agents/data-governance "建一份核心指标口径字典"
# teams/data-analysis-team/agents/data-qa-reviewer "核对这份分析报告的口径和复算"
```
