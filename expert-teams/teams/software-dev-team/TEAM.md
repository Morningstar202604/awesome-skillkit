# Software Dev Team - 软件开发交付专家团

> 场景：软件开发全流程交付——从需求拆解、架构设计、代码实现、代码评审、测试补全到交付，强门禁、小步走、可回滚。

## 团队定位
- **输入**：需求文档/用户故事、现有代码库、约束（时间/质量/合规）
- **输出**：通过评审门禁、测试全绿、可构建可运行的增量交付件
- **核心价值**：12 人分工、严门禁（评审并行 → tester 收口）、主理人只做拆解调度验收

## 成员架构（12 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 开发统筹 | `software-team-lead` | 任务拆解、验收标准、角色分派、阶段门禁 | 所有软件开发需求入口 |
| 架构师 | `software-architect` | 模块边界、接口契约、数据流、风险、备选方案 | "怎么设计模块"、"接口契约怎么定" |
| API 设计师 | `software-api-designer` | REST/GraphQL 契约、Schema、校验、错误模型、版本 | "设计接口"、"出 API spec" |
| 数据库工程师 | `software-database-engineer` | 数据建模、查询与索引、迁移规划、一致性 | "设计表结构"、"优化查询"、"迁移" |
| 前端工程师 | `software-frontend-engineer` | 组件架构、状态管理、路由、数据获取、构建优化 | "实现前端"、"组件怎么拆" |
| 后端工程师 | `software-backend-engineer` | 服务路由、中间件、认证鉴权、后台任务、韧性 | "实现后端"、"认证怎么做" |
| DevOps 工程师 | `software-devops-engineer` | 容器化、CI/CD、IaC、可观测、部署与回滚 | "Dockerfile"、"流水线"、"部署" |
| 安全工程师 | `software-security-engineer` | OWASP、注入/XSS、鉴权、依赖漏洞、密钥处理 | "安全审查"、"有没有漏洞" |
| 测试工程师 | `software-qa-engineer` | 测试策略、单测/集成/E2E、覆盖率与风险报告 | "测试计划"、"补用例" |
| 评审员 | `software-reviewer` | 正确性、安全、性能陷阱、数据一致性门禁 | "帮我评审这段代码"、"这有没有安全问题" |
| 代码质量评审员 | `software-code-quality-reviewer` | 可读性、可维护性、复杂度、重复、约定一致性 | "质量评审"、"代码是不是太复杂" |
| 测试工程师(门禁) | `software-tester` | 单元/边界/回归测试、缺口识别、覆盖率、独立可运行 | "补测试"、"覆盖率不够"、"边界用例" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全流程** | "新功能从零到交付" | 拆解 → 设计(api/database **并行**+architect) → 实现(frontend/backend **并行**) → 门禁(security+qa+reviewer+quality **并行**，reviewer 清零后) → tester（评审通过后收口，全绿才过） → 交付 |
| **W2 仅设计** | "只出架构方案/接口契约" | 拆解 → 设计（architect+api+database 并行，产出 ADR + api 契约 + 数据模型） |
| **W3 仅评审+测试** | "对现有代码跑门禁" | reviewer + quality + security + qa **并行**（无实现阶段）→ tester（评审通过后收口） |

## 协作机制
- **小步提交**：每步可构建可运行，保持主干稳定
- **门禁规则（唯一口径）**：实现完成 → 门禁四员（security+qa+reviewer+quality）并行评审 → **reviewer 无 critical/major 且门禁通过后** → 派 software-tester 补测试收口（全绿才过）。W3 无实现阶段，同样按「门禁并行 → tester 收口」顺序。
- **驳回机制**：同一任务被驳回 2 次以上，停下来重查任务定义或方案
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可

## 纪律
- 主理人不写实现代码，只做拆解、调度、验收
- 评审与测试结论以成员回报为准，不脑补
- 评审只报真实问题（正确性/安全/性能/数据一致性），风格偏好不报
- 测试只改测试代码，不动业务代码；失败用例给最小复现步骤

> **协作接口**：可对接 academic（论文配套代码/工具开发）、fullstack（模块集成/交付）、content（技术博客/文档）；典型跨场景触发词：论文代码、工具开发、技术文档、论文+实现。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 全流程开发（Team-lead 为入口）
teams/software-dev-team/agents/software-team-lead "帮我实现用户登录模块，从设计到测试全走一遍"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/software-dev-team/agents/software-architect "帮我设计订单模块的接口契约"
# teams/software-dev-team/agents/software-api-designer "出一份用户模块的 REST API spec"
# teams/software-dev-team/agents/software-database-engineer "设计订单表结构和索引"
# teams/software-dev-team/agents/software-frontend-engineer "实现购物车页面"
# teams/software-dev-team/agents/software-backend-engineer "实现下单接口和鉴权"
# teams/software-dev-team/agents/software-devops-engineer "写 Dockerfile 和 CI 流水线"
# teams/software-dev-team/agents/software-security-engineer "对这个模块做安全审查"
# teams/software-dev-team/agents/software-qa-engineer "设计支付流程的测试策略"
# teams/software-dev-team/agents/software-reviewer "帮我评审这个 PR"
# teams/software-dev-team/agents/software-code-quality-reviewer "做一次质量评审"
# teams/software-dev-team/agents/software-tester "帮我给支付模块补边界测试"
```
