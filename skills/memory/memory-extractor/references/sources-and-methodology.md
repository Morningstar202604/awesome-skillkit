# Sources & Methodology — memory-extractor

本技能的方法论蒸馏自 mem0 的公开实践，属于**方法论提炼（methodology distilled）**：只借鉴公开文档中描述的抽取阶段流程与事实拆分原则，未复制任何源代码。

| 来源项目 | 许可 | 蒸馏了什么 | 署名方式 |
|---|---|---|---|
| mem0 | Apache-2.0 | 两阶段记忆管线中的 extraction 阶段：从对话中抽取候选事实，再交由更新阶段与现有记忆比对决定 ADD/UPDATE/DELETE/NOOP；细粒度事实原则——一条记忆 = 一个可独立成立的事实 | 本技能的"候选抽取 → 去重比对"两步结构与复合句拆分规则即源于此；在上游 pack（memory-systems）与本文件中署名 |

## 蒸馏边界（诚实声明）

- 本技能只覆盖 mem0 两阶段中的抽取阶段；比对后的落库决策（ADD/UPDATE/DELETE/NOOP）归上游 pack 中姊妹技能 memory-manager 完成，对应 mem0 的 update 阶段。
- 置信度打分数值（显式 0.9 / 推断 ≤ 0.7 / NO_DEDUP 上限 0.8）为本技能作者给出的经验值，非源自 mem0，可按业务校准。
- 敏感类别排除规则与 evidence_quote 可追溯性要求为本技能作者补充的工程约束，非 mem0 原文。
- 本技能为方法论蒸馏产物，与 mem0 无隶属关系，不代表其官方观点。
