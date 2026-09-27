# Education Training Team - 教育培训内容交付专家团

> 场景：教育培训全流程交付——从课程体系设计、课件撰写、出题、讲解、辅导、测评到学习路径规划与数据复盘，强质检、重落地、可自测。

## 团队定位
- **输入**：教学目标、学员对象画像、课时/周期、考核要求、已有素材
- **输出**：经质检门禁的课程体系、课件、题库、讲稿、测评与个性化学习路径，附难度梯度与自测答案
- **核心价值**：10 人分工、课程设计先行、课件/出题并行、qa-reviewer 质检收口，主理人只做拆解调度验收

## 成员架构（10 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 教育统筹 | `education-team-lead` | 任务拆解、教学目标对齐、角色分派、阶段质检 | 所有教育培训需求入口 |
| 课程设计师 | `education-curriculum-designer` | 课程体系、模块划分、难度梯度、教学目标 | "设计一门课"、"课程大纲" |
| 课件撰写 | `education-courseware-writer` | 讲义/PPT 文案/案例/图示文字 | "写课件"、"讲义怎么写" |
| 出题师 | `education-quiz-designer` | 填空/选择题库、大白话比喻解析、举一反三 | "出题"、"配练习题" |
| 讲解师 | `education-lecturer` | 讲稿、口播脚本、概念通俗讲解 | "怎么讲清楚这个知识点" |
| 辅导师 | `education-tutor` | 答疑、错题讲解、学习督促、个性化反馈 | "学生不懂"、"答疑" |
| 测评设计 | `education-assessment-designer` | 形成性/终结性测评、评分标准、及格线 | "出个考试"、"测评方案" |
| 学习路径规划 | `education-learning-path-planner` | 阶段目标、先后依赖、节奏安排、预估时长 | "怎么学"、"学习路线" |
| 教育数据分析师 | `education-data-analyst` | 学习数据复盘、薄弱点诊断、完成率分析 | "学习效果怎么样"、"数据分析" |
| 教育质检 | `education-qa-reviewer` | 知识正确性/难度梯度/答案一致性门禁（只读） | "内容质量把关" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 全流程** | "从零做一门课到可交付" | 拆解 → 课程设计（curriculum-designer 出体系）→ 课件+出题并行（courseware-writer + quiz-designer）→ 讲解（lecturer）→ 测评（assessment-designer）→ 质检门禁（qa-reviewer 清零后）→ 交付 |
| **W2 仅课程设计** | "只要课程体系/大纲" | 拆解 → curriculum-designer 出模块划分/难度梯度/教学目标 |
| **W3 仅出题+测评** | "只要题库和考试" | 拆解 → quiz-designer 出题（填空/选择+比喻解析+举一反三）→ assessment-designer 组测评 → qa-reviewer 核对答案正确性后收口 |

## 协作机制
- **小步提交**：按模块分批产出课件与题库，每批可独立质检
- **门禁规则（唯一口径）**：内容完成 → qa-reviewer 按知识正确性/难度梯度/答案一致三门禁评审 → **无错误后** → 主理人交付。涉及答案的题库必须经 qa-reviewer 核对答案无误。
- **驳回机制**：同一内容被驳回 2 次以上，停下来重查教学目标或知识点定义，而非重复派单
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可

## 纪律
- 主理人不亲自写课件/出题，只做拆解、调度、验收
- 知识内容以教材/权威来源为准，不脑补概念定义；拿不准标注 [待核实]
- 出题师必须体现"填空/选择 + 大白话比喻解析 + 举一反三"风格
- 质检结论以 qa-reviewer 回报为准，不脑补"应该没错"

> **协作接口**：可对接 academic-paper-team（学术课程）、data-analysis-team（数据类课程配套练习）、content-writing-team（课程营销文案）；典型跨场景触发词：课程设计、课件撰写、出题题库、学习路径、测评考试。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 全流程做课（Team-lead 为入口）
teams/education-training-team/agents/education-team-lead "帮我做一门 Python 入门课，从课程设计到题库全走一遍"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/education-training-team/agents/education-curriculum-designer "设计一门机器学习入门的课程体系"
# teams/education-training-team/agents/education-courseware-writer "写一份变量与数据类型的讲义"
# teams/education-training-team/agents/education-quiz-designer "给'循环'出 20 道填空选择题"
# teams/education-training-team/agents/education-lecturer "把'递归'讲成大白话"
# teams/education-training-team/agents/education-tutor "学生不懂什么是闭包，帮着答疑"
# teams/education-training-team/agents/education-assessment-designer "出一份期末测评方案"
# teams/education-training-team/agents/education-learning-path-planner "排一个 12 周自学路径"
# teams/education-training-team/agents/education-data-analyst "分析这份学习数据找薄弱点"
# teams/education-training-team/agents/education-qa-reviewer "对这批课件做知识正确性质检"
```
