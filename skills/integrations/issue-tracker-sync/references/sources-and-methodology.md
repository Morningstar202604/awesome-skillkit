# Methodology sources and design trade-offs（issue-tracker-sync）

> 何时读：当你要接入第四个 tracker（如 GitLab / Azure Boards / 飞书任务）、
> 改周报分组逻辑，或质疑"为什么不做自动双向同步"时读本文件。

## Idea sources (distilled from public methodology; not copied text)

| This skill's approach | Idea distilled from |
|---|---|
| 用"规范语义"做中间层，而非直接对拷状态名 | 数据集成里的 canonical model / 语义中介模式：N 个源两两映射是 N²，经中间层是 2N |
| `build` / `field-map` / `weekly-report` 三段分离 | 端口-适配器：出站写操作、参考数据、只读报表三者生命周期与权限都不同 |
| 优先级用内部编号 P0..P4 | 配置管理中的"内部标识 + 外部映射表"惯例，避免把某个平台的枚举当基准 |
| 归一化提取按平台分支写，不做通用猜测 | 解析器设计里的 anti-guessing 原则：猜测型字段提取的错误是静默的，代价最高 |
| 周报必须记录 ID 映射台账 | 分布式系统里的 correlation ID / 外部 ID 映射表思路：无锚点的同步不可恢复 |
| dry-run 先出请求体 | Terraform `plan` / `kubectl --dry-run=client` 的两阶段惯例 |

## Key trade-offs

**为什么不做自动双向同步？** 双向同步需要三个前提：可靠的 ID 映射、冲突检测
策略（两边都改了谁赢）、以及幂等写入。三者都依赖对方平台的事件流，而三家的
webhook 语义、重推行为、字段变更通知各不相同。半成品的双向同步比不做更危险——
它会在无人察觉时把状态改回去。因此本技能只做**单向构造 + 只读报告**，
把同步锚点（ID 台账）显式交给使用者维护。

**为什么状态映射是"语义对齐"而非查表替换？** 三家都允许自定义工作流。
Jira 站点可以把 "In Progress" 重命名成 "开发中"，也可以插入 "待产品确认"
这样的中间态。直接按字符串映射会在第一个自定义站点上崩掉。以规范语义为中间层，
映射不上时报告"需人工确认"，比猜一个结果安全。

**为什么 `field-map` 同时提供人类可读与 `--json` 两种输出？** 表格给人看，
JSON 给编排层消费（比如让 AI 按映射表批量构造请求）。同一个事实源出两种视图，
避免文档与代码里的映射表各自漂移。

**为什么不帮用户查 Jira 的 customfield ID？** 那需要真实凭证与网络调用，
与本技能"脚本离线可测"的约束冲突；更重要的是字段 ID 是**站点特定**的，
写死在脚本里必然过期。正确做法是在 SKILL.md 里给出查询命令，让使用者
在真实环境里拿到当前值。

**周报为什么按状态分组而不是按负责人分组？** 周报的读者是团队，
最需要立刻看到的是"什么卡住了"（阻塞项高亮置顶），其次才是"谁在做什么"。
按负责人分组会掩盖阻塞项——它们会散落在各人的表格里，需要读者自己去发现。

**为什么 GitHub 的 `closed` 要拆成已完成/已取消？** `closed` 是二值状态，
但语义上"完成了"和"决定不做"对周报读者的意义完全不同：前者是交付，
后者是决策。用标签区分是 GitHub 生态的通行做法；退而求其次也可读
`state_reason` 字段。

## Official documentation

- Jira REST API v2 建 issue：<https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issues/#api-rest-api-2-issue-post>
- Jira 字段查询（找出 customfield ID 与优先级枚举）：<https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-fields/>
- Jira Cloud 用户搜索（拿 accountId）：<https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/>
- Linear GraphQL `issueCreate` mutation：<https://developers.linear.app/docs/graphql/working-with-the-graphql-api>
- Linear 优先级枚举说明：<https://linear.app/docs/priorities>
- GitHub Issues REST（创建与字段）：<https://docs.github.com/en/rest/issues/issues#create-an-issue>
- GitHub API 版本头：<https://docs.github.com/en/rest/about-the-rest-api/api-versions>
- Python `datetime.date.fromisocalendar`（ISO 周计算依据）：<https://docs.python.org/3/library/datetime.html#datetime.date.fromisocalendar>
