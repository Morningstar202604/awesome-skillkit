# Math Modeling Team - 数学建模竞赛专家团

> 场景：全国大学生数学建模竞赛（CUMCM/高教社杯）全程托管——从选题、建模、求解、写作到终审交付，72 小时严格节奏。

## 团队定位
- **输入**：赛题原文、数据（或无数据）、目标奖项
- **输出**：查重安全、格式合规、可冲省一/国奖的论文 PDF + 程序 + 数据
- **核心价值**：9 人串行闭环、主理人全程把关一致性与查重

## 成员架构（9 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 竞赛总指挥 | `math-team-lead` | 选题路线、3天节奏、创新点、查重管控、终审 | 所有建模竞赛需求入口 |
| 数据分析师 | `math-data-analyst` | 数据清洗、EDA、特征工程、训练划分 | "清洗数据"、"缺失值怎么办"、"EDA" |
| 文献调研员 | `math-literature-researcher` | 往届论文检索、方法库对齐、基线设定 | "参考什么模型"、"往届怎么解的" |
| 建模专家 | `math-modeler` | 题型识别、假设与符号、主/改进模型、灵敏度设计 | "建什么模型"、"假设怎么写" |
| 算法求解师 | `math-solver` | Python/MATLAB 双栈求解、仿真、规范图表、可复现 | "代码实现"、"数值结果"、"画图" |
| 可视化专家 | `math-visualizer` | 三线表、黑白矢量图、匿名题注、LaTeX 就绪导出 | "画图表"、"三线表"、"出图" |
| 论文主笔 | `math-writer` | 国赛结构、摘要单页含数值、LaTeX、三线表、附录程序 | "写国赛论文"、"摘要单页"、"LaTeX/查重" |
| 复现与查重守护 | `math-reproducibility` | 环境锁定、种子固定、一键复现、查重/匿名自查 | "复现脚本"、"查重风险"、"锁定环境" |
| 论文质检员 | `math-qa-reviewer` | 逻辑链、数值一致性、格式规范、提交清单终检 | "终检"、"数值对不上吗"、"提交前检查" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **A 完整国赛** | "拿到赛题、要全程托管" | Phase 0(lead 路线规划+data-analyst/literature **并行**)→1(modeler)→2(solver→visualizer **串行**)→3(writer)→4(reproducibility+qa **并行**) |
| **B 单题攻坚** | "只卡在某问/某步" | 卡选题→主理人；卡数据→data-analyst；卡文献→literature；卡建模→modeler；卡求解→solver；卡图表→visualizer；卡写作→writer；卡复现→reproducibility；卡终检→qa |
| **C 赛前特训** | "还没比赛，想练真题/补短板" | 指定年份真题跑通 Phase 0→1→2→3，Phase 4 自查打分 |

## 关键差异（国赛 vs 美赛）
- 摘要单独成页、不要求英文摘要
- 强调现实意义与机理建模
- 程序放附录
- 查重极严、匿名评阅

## 协作机制
- **技能调用协议**：每 Phase 前必扫 `skills/`，命中即用、严格按其执行
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可
- **思想纪律**：忠于原文、不绕圈、出错即停（2-3 轮无解即回传复核）
- **自检闸门**：`math-modeling-selfcheck` A 组开工前/B 组产出后，任一不过即停
- **一致性终审**：模型符号、求解数值、结论必须首尾一致
- **查重零容忍**：全程禁止复制往届/网文/教材

## 技能依赖
团队专用 skills 目录：`teams/math-modeling-team/skills/`
核心 skills：`math-modeling-guosai`（资料库）、`math-modeling-selfcheck`（自检）、题型/方法/模板/查重类 skill。

> **协作接口**：可对接 academic（建模论文写作/投稿）、visual（数据可视化图表）、content（建模科普/竞赛报告）；典型跨场景触发词：建模+论文、数据可视化、竞赛报告。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 完整国赛托管（Team-lead 为入口）
teams/math-modeling-team/agents/math-team-lead "帮我全程托管这个国赛赛题"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/math-modeling-team/agents/math-data-analyst "帮我清洗这份赛题数据并做EDA"
# teams/math-modeling-team/agents/math-literature-researcher "这个题型往届怎么解的"
# teams/math-modeling-team/agents/math-modeler "这个题型选什么模型"
# teams/math-modeling-team/agents/math-solver "帮我把模型落地跑出数值"
# teams/math-modeling-team/agents/math-visualizer "把结果画成国赛规范图表"
# teams/math-modeling-team/agents/math-writer "帮我按国赛格式写论文"
# teams/math-modeling-team/agents/math-reproducibility "生成一键复现脚本并做查重自查"
# teams/math-modeling-team/agents/math-qa-reviewer "提交前做终检"
```
