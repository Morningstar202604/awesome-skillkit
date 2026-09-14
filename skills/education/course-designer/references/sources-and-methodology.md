# 来源与方法论 / Sources and Methodology

本技能为 self-authored，方法论骨架提炼自以下公开材料（结构借鉴，无文本复制）：

| 来源 | 类型 | 借鉴内容 | 许可/署名 |
|------|------|----------|-----------|
| [AI-Learning-Agent](https://github.com/Chittesh-ST/AI-Learning-Agent)（LangGraph 掌握式导师） | 开源项目 | checkpoint 分解 + 通过率门槛 + 失败触发费曼补救的循环；**禁选择题防蒙**的严格测验设计；评分 rubric 量化（0-20 分档） | 结构借鉴并署名 |
| [Feynman Learning Coach](https://lobehub.com/skills/jasonxzwen-skill-hub-feynman-learning-coach)（LobeHub 技能） | 开源技能 | **学习契约**（scope/level/target/constraints ≤3 问）；Foundations→Mechanism→Example→Transfer→Teach-back 路径；按 beginner/intermediate/advanced/exam 的深度控制表 | 结构借鉴并署名 |
| [授悟 FeynMind](https://forum.trae.cn/t/topic/70981/3)（TRAE 大赛作品，一线高中教师） | 🟡 实践案例 | "AI 扮演不太聪明的学生"的反向教学设计；知识覆盖状态可视化（主动/被动/未覆盖）；四维评估（覆盖率/准确性/连贯性/积极性） | 设计思想借鉴并署名 |
| [THU-MAIC/OpenMAIC feynman-learning](https://github.com/THU-MAIC/OpenMAIC) | 开源技能 | teach-back 与追问为核心；剥离术语；压力测试类比；迁移到新语境 | 结构借鉴并署名 |
| 掌握式学习（Mastery Learning，Bloom） | 教育学公版 | 以掌握为准而非以时间为准的通过门槛思想 | 经典理论 |

## 设计决策

1. **学习契约前置且 ≤3 问**：来自 Feynman Learning Coach 的最优实践——
   超过三个问题就是在拖延教学。
2. **checkpoint 可判定化**：把"理解"改写为"能解释/能做出/能通过"，
   与本仓"审计文化"同源——不可判定的目标无法验收。
3. **费曼循环独立成技能**（feynman-explainer）：补救教学是独立动作，
   与课程骨架（本技能）和习题（exercise-generator）解耦，链条更清晰。
