# Fullstack Web Team - 全栈 Web 交付专家团

> 场景：Web 应用全链路交付——从需求分析、架构设计、技术选型、前后端实现、API 设计、数据建模、DevOps/CI-CD、测试、安全、性能、无障碍、移动端适配、技术债治理，到可上线交付包。

## 团队定位
- **输入**：产品需求/模糊想法、约束（团队/预算/时间/合规）、或既有代码库需加固
- **输出**：可运行、测试通过、CI 绿、有部署脚本、有回滚预案、有文档的完整交付包
- **核心价值**：15 位 fullstack 专家 + 4 位 core 单兵分工协作，Phase 门禁质量把关，主理人只做编排与验收

## 成员架构（19 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 主理人 | `fullstack-team-lead` | 全链路编排、Phase 调度、门禁把关、终审汇编 | 所有 Web 应用类需求入口 |
| 系统架构师 | `fullstack-architect` | 架构风格、技术选型、模块边界、ADR | "怎么架构"、"选什么框架" |
| 前端工程师 | `fullstack-frontend-engineer` | 组件架构、状态管理、数据获取、构建优化 | "前端怎么搭"、"组件怎么拆" |
| 后端工程师 | `fullstack-backend-engineer` | 服务分层、认证授权、中间件、后台任务、韧性 | "接口怎么实现"、"鉴权怎么做" |
| API 设计师 | `fullstack-api-designer` | REST/GraphQL 契约、Schema、校验、错误、版本 | "API 怎么设计" |
| 数据库工程师 | `fullstack-database-engineer` | 数据建模、SQL/NoSQL、索引、迁移、回滚 | "库怎么设计"、"查询慢" |
| DevOps 工程师 | `fullstack-devops-engineer` | 容器化、IaC、部署策略、可观测性、密钥管理 | "怎么部署"、"日志怎么看" |
| CI/CD 工程师 | `fullstack-ci-cd-engineer` | 流水线、质量门禁、发布管理、可追溯 | "CI 怎么搭" |
| 测试工程师 | `fullstack-qa-engineer` | 测试策略、用例设计、自动化、覆盖率、缺陷管理 | "测什么"、"用例怎么补" |
| 安全工程师 | `fullstack-security-engineer` | OWASP Top10、认证授权、依赖漏洞、密钥管理 | "有没有安全漏洞" |
| 性能工程师 | `fullstack-performance-engineer` | 瓶颈定位、前端/后端/DB 优化、容量规划 | "为什么慢"、"怎么提速" |
| 代码质量官 | `fullstack-code-quality-reviewer` | 可读性、可维护性、复杂度、重复、规范一致 | "代码怎么改好" |
| 无障碍专家 | `fullstack-accessibility-expert` | WCAG AA、语义标签、键盘/读屏、对比度 | "无障碍行不行" |
| 移动端工程师 | `fullstack-mobile-engineer` | 响应式、触摸交互、PWA/离线、设备适配 | "手机上好不好用" |
| 技术债治理师 | `fullstack-tech-debt-strategist` | 债务盘点、量化、优先级、重构策略、还债节奏 | "哪里最该还债" |
| 通用架构师（单兵） | `core-architect` | 只读架构分析、模块边界、接口契约、扩展性评估 | "架构怎么设计"（用户明确指定） |
| 通用代码审查（单兵） | `core-code-reviewer` | 只读正确性缺陷、安全漏洞、性能陷阱审查 | "帮我审代码"（用户明确指定） |
| 通用安全审计（单兵） | `core-security-auditor` | 只读注入、硬编码密钥、越权、依赖漏洞扫描 | "安全扫描一下"（用户明确指定） |
| 通用测试工程师（单兵） | `core-test-engineer` | 单元测试、边界条件、回归测试设计与编写 | "补测试"、"提升覆盖率"（用户明确指定） |

**core-* 单兵与 fullstack-\* 专家的正交边界**：core-* 是用户明确指定时的**只读单兵**（core-architect/core-code-reviewer/core-security-auditor 默认 edit:deny，不做流程编排）；fullstack-* 是主理人 Phase 流程内的**可写交付角色**。两者不互相替代、不并行重复派发同一任务；未被用户点名时，主理人只调度 fullstack-* 成员。`core-researcher` 归属学术团队（见 academic-paper-team）。

## Workflow 对照

| Workflow | 触发场景 | 执行 Phases |
|----------|----------|-------------|
| **W1 全链路** | "从零做个 Web 应用上线" | 1→2→3→4→5→6→7 |
| **W2 绿地脚手架** | "快速起步，先跑起来" | 1+2+3（不可跳过 Phase 2） |
| **W3 加固既有代码** | "安全/性能/质量/无障碍加固" | 5+6 |
| **W4 仅接口与数据** | "只做 API 设计 + 数据建模" | 2 |
| **W5 发布就绪** | "冲刺上线，CI/CD/部署" | 4 |

## 协作机制
- **Checkpoint**：主理人每 Phase 前执行 `git tag phase-N` + `checkpoint-N.md`；DevOps 提供回滚脚本模板
- **版本追踪**：每 Phase 结束写入 `versions.md`
- **并行显式**：Phase 注释「并行 Task 调用」
- **交接模板**：4 块，完整产出仍传递，主理人自身留摘要
- **监测断路**：3 轮无新增=卡死，同义=死循环，不可编译/跑/测试不绿=停滞

## 技能依赖
见 `SKILLS_INDEX.md` 中全栈团队专用段：`web-search`、`api-design-reviewer`、`deep-security-scan`、`security-scan`、`performance-profiler`、`frontend-app-builder`、`frontend-testing-debugging`、`ci-cd-pipeline-builder`、`test-case-generator-v2`、`uml-and-software-architecture-visualization`、`docker-development`、`helm-chart-builder`、`terraform-patterns`、`github-actions-advanced`、`supabase-postgres-best-practices`、`react-best-practices`、`shadcn`、`stripe-best-practices`、`observability-designer`、`slo-architect`、`kubernetes-operator` 等。

> **协作接口**：可对接 visual（产品页/官网UI设计）、content（落地页文案/SEO）、academic（论文配套系统/数据平台）、software（模块集成）；典型跨场景触发词：产品落地页、官网、Web应用+设计、论文系统。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 完整 Web 应用（Team-lead 为入口）
teams/fullstack-web-team/agents/fullstack-team-lead "帮我从零做一个电商 Web 应用上线"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/fullstack-web-team/agents/fullstack-architect "微服务还是单体，怎么选型"
# teams/fullstack-web-team/agents/fullstack-frontend-engineer "React 组件架构怎么分层"
# teams/fullstack-web-team/agents/fullstack-security-engineer "帮我做次安全审计"

# 通用单兵（用户明确指定时）
# teams/fullstack-web-team/agents/core-architect "只做架构分析，不改代码"
# teams/fullstack-web-team/agents/core-code-reviewer "帮我审这段 diff"
```
