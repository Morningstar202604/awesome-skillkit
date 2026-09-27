# Academic Paper Team - 学术论文专家团

> 场景：学术论文全流程——从选题、文献综述、研究设计、方法选型、写作、逻辑审查、语言润色、图表制作、风险预判、伦理合规、模拟审稿、回复策略、期刊匹配、格式规范、可复现性、投稿交付。

## 团队定位
- **输入**：研究兴趣/模糊想法、约束条件（资源/时间/目标期刊）、或已有初稿/审稿意见
- **输出**：可投稿、可复现、经得起审稿的完整论文包（正文+图表+代码+数据+投稿材料）
- **核心价值**：专业分工协作，每环节由对应专家产出，主理人只做编排与质量把关

## 成员架构（19 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 主理人 | `academic-team-lead` | 全链路编排、Phase 调度、质量把关、终审汇编 | 所有论文类需求入口 |
| 选题策略师 | `academic-topic-strategist` | 可行性评估、缺口定位、创新点论证、问题收敛 | "这个题行不行"、"缺什么创新" |
| 文献综述师 | `academic-literature-synthesizer` | PRISMA 综述、检索式、缺口矩阵、定位图谱 | "帮我写综述"、"定位在哪" |
| 研究设计师 | `academic-research-designer` | 假设体系、变量操作化、因果识别、实验设计 | "怎么设计实验"、"因果怎么说" |
| 统计方法师 | `academic-statistical-methodologist` | 模型选择、检验力、效应量、多重性控制 | "用什么检验"、"样本量够吗" |
| 领域方法师 | `academic-domain-methodologist` | 领域基线对齐、惯例方法、度量合理性 | "这个领域一般怎么做" |
| 可复现管家 | `academic-reproducible-researcher` | 代码/数据/环境锁定、复现脚本、预注册 | "怎么保证可复现" |
| 学术主笔 | `academic-writer` | IMRaD 撰写、结构化摘要、叙事一致性 | "帮我写这段"、"摘要怎么搭" |
| 逻辑审核官 | `academic-logic-auditor` | 论证链重建、因果推理、谬误识别、反例压测 | "逻辑通不通"、"因果站得住吗" |
| 语言润色师 | `academic-language-refiner` | 术语统一、学术语体、精简冗余、句法优化 | "润色这段"、"术语统一" |
| 图表专家 | `academic-data-visualizer` | 图表选型、视觉编码、投稿图规范、自明图注 | "这张图怎么改" |
| 风险预判师 | `academic-risk-forecaster` | 审稿质疑推演、稳健性设计、外部效度边界 | "审稿人会挑什么毛病" |
| 伦理合规官 | `academic-ethics-reviewer` | 伦理审批、知情同意、数据合规、利益冲突、署名 | "伦理过关吗" |
| 模拟审稿人 | `academic-peer-reviewer` | 五维打分、缺陷清单、立场判定、改进优先级 | "帮我审一遍" |
| 答辩策略师 | `academic-rebuttal-strategist` | 意见分类、让争判断、逐条回应、补证规划 | "审稿意见怎么回" |
| 期刊联络官 | `academic-editor-liaison` | Venue 匹配、要素比较、投稿信要点、转投路线 | "投哪个刊" |
| 格式规范卫士 | `academic-format-guardian` | 目标格式适配、引用规范、盲审合规、投稿清单 | "格式对不对" |
| 通用调研员 | `core-researcher` | 技术调研、选型对比、文档检索、资料汇总 | "查资料"、"对比选型" |
| 事实核查官 | `core-fact-checker` | 关键事实、数字、引用、来源独立核查，防幻觉 | "这个数字准不准"、"引用核实" |

## Workflow 对照

| Workflow | 触发场景 | 执行 Phases |
|----------|----------|-------------|
| **W1 全链路** | "写完整论文"、"从选题到投稿" | 1→2→3(并行分支)→4→5→6→7→8 |
| **W2 快速选题** | "这个题行不行"、"缺什么创新" | 1 |
| **W3 稿件打磨** | "已有初稿要润色/查逻辑/出图" | 3(并行分支)→4（跳过 1-2，须用户确认） |
| **W4 审稿备战** | "拿到审稿意见要回复" | 5→7（跳过 1-4/6/8，须用户确认） |
| **W5 投稿定稿** | "投哪个刊"、"格式对不对" | 6→8（跳过 1-5/7，须用户确认） |

## 协作机制
- **Checkpoint**：主理人每 Phase 前执行 `git tag phase-N` + `checkpoint-N.md`
- **版本追踪**：每 Phase 结束写入 `versions.md`
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可
- **监测断路**：3 轮无新增=卡死，2 次同义=死循环，空/重复/无关=停滞

## 技能依赖
见 `SKILLS_INDEX.md` 中学术团队专用段：`paper-topic-selector`、`journal-adapt`、`lit-review`、`figure-maker`、`model-formulator`、`model-solver`、`pdf-pipeline`、`web-search`、`deep-research` 等。

> **协作接口**：可对接 software/fullstack（论文+配套代码/实验复现）、visual（数据图表/论文配图）、content（科普文章/学术传播）；典型跨场景触发词：论文+代码、实验复现、学术可视化、科普写作。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 完整论文（Team-lead 为入口）
teams/academic-paper-team/agents/academic-team-lead "帮我从选题到投稿写一篇关于 X 的论文"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/academic-paper-team/agents/academic-topic-strategist "这个研究方向可行吗"
# teams/academic-paper-team/agents/academic-writer "帮我写 Introduction"
# teams/academic-paper-team/agents/academic-peer-reviewer "帮我模拟审稿一次"
```
