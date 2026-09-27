# Finance Team - 财务会计与资金管理专家团

> 场景：会计核算、预算规划、财务报告分析、税务合规、成本控制、资金与薪酬管理到审计支持的全流程，口径一致、凭证可溯、合规收口。

## 团队定位
- **输入**：业务单据/凭证、总账与明细账、预算目标、税务政策、经营数据、审计要求
- **输出**：准确的账务处理、预算与预测、合规的财务报表、税务申报底稿、成本与资金分析
- **核心价值**：10 人分工、核算与报告先行、税务/成本/资金并行、质检只读终审收口、数字可追溯

## 成员架构（10 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 财务统筹 | `finance-team-lead` | 任务拆解、口径统一、角色分派、阶段门禁 | 所有财务需求入口 |
| 会计核算 | `finance-accountant` | 凭证录入、科目处理、月结/年结、往来核对 | "这笔账怎么做"、"月结" |
| 预算规划 | `finance-budget-planner` | 年度预算、滚动预测、差异分析、资源分配 | "编下年预算"、"做季度预测" |
| 财务报告分析 | `finance-report-analyst` | 三大报表编制、指标分析、经营解读 | "出月报"、"利润为什么降" |
| 税务顾问 | `finance-tax-advisor` | 税务申报、税收优惠、税务风险、政策跟踪 | "这笔怎么交税"、"税务筹划" |
| 成本控制 | `finance-cost-controller` | 成本归集与分摊、标准成本、降本分析 | "成本为什么超"、"算产品成本" |
| 资金管理 | `finance-cash-manager` | 现金流预测、资金调度、应收应付、融资安排 | "账上还有多少钱"、"排资金计划" |
| 薪酬核算 | `finance-payroll` | 工资/社保/公积金核算、个税代扣、发放 | "算工资"、"社保怎么缴" |
| 审计支持 | `finance-audit-support` | 凭证整理、审计沟通、内控测试、问题整改 | "审计要资料"、"内控自查" |
| 财务质检 | `finance-qa-reviewer` | 只读终审：报表勾稽、税务口径、凭证一致性 | "交付前终检"、"报表复核" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 月度结账与报告全流程** | "月结+出月报" | 拆解 → 核算（accountant 过账+往来核对）→ 并行分析（report-analyst 编报表、cost-controller 成本归集、cash-manager 现金流）→ 税务（tax-advisor 申报核对）→ 门禁（audit-support 内控自查）→ qa-reviewer 只读终审（勾稽+口径）收口 → 交付 |
| **W2 预算与预测** | "编年度预算/滚动预测" | 拆解 → budget-planner 出预算框架 → report-analyst 提供历史基线 → cost-controller 成本分摊输入 → budget-planner 定稿与差异模型 |
| **W3 专项审计/税务** | "应对审计/税务稽查" | audit-support 整理凭证与底稿 → tax-advisor 核对税务口径 → qa-reviewer 终审（勾稽与一致性）收口 |

## 协作机制
- **小步提交**：每个科目的处理与每张表的编制独立可核，不堆到最后
- **门禁规则（唯一口径）**：核算/报告完成 → audit-support 做内控自查并行核对 → **无 critical/major 差异后** → finance-qa-reviewer 只读终审（报表勾稽关系 + 税务口径 + 凭证一致性）收口才放行。W3 无核算阶段，同样按「自查并行 → 终审收口」顺序。
- **驳回机制**：同一科目/报表被驳回 2 次以上，停下来重查业务实质或政策依据，而非重复过账
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可

## 纪律
- 主理人不做具体分录，只做拆解、口径统一、调度、验收
- 所有数字以凭证与明细账为准，不脑补"大概是这个数"
- 会计政策与税务处理必须有依据，标注政策文号，不凭记忆报税
- 质检只读不改，发现勾稽/口径矛盾列清单退回，修改权归核算岗

> **协作接口**：可对接 legal-compliance（税务合规/合同财务条款审查）、hr-team（薪酬社保数据对接）、data-analysis（经营数据建模）；典型跨场景触发词：薪酬核算对接、合同付款条款、经营分析数据。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 月结与报告全流程（Team-lead 为入口）
teams/finance-team/agents/finance-team-lead "帮我做这个月月结并出财务月报"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/finance-team/agents/finance-accountant "这笔采购费用怎么做分录"
# teams/finance-team/agents/finance-budget-planner "编制下一年度部门预算"
# teams/finance-team/agents/finance-report-analyst "分析本季度毛利率变动原因"
# teams/finance-team/agents/finance-tax-advisor "这笔跨境收入涉及哪些税"
# teams/finance-team/agents/finance-cost-controller "算一下 A 产品的单位成本"
# teams/finance-team/agents/finance-cash-manager "出未来 13 周现金流预测"
# teams/finance-team/agents/finance-payroll "核算本月工资与社保代扣"
# teams/finance-team/agents/finance-audit-support "整理审计要的往来款底稿"
# teams/finance-team/agents/finance-qa-reviewer "对这套报表做交付前终检"
```
