# Sources & Methodology — memory-manager

本技能的方法论蒸馏自 mem0 与 letta (MemGPT) 的公开实践，属于**方法论提炼（methodology distilled）**：只借鉴公开文档中描述的更新阶段决策与记忆自编辑思想，未复制任何源代码。

| Source project | License | What was distilled | Attribution |
|---|---|---|---|
| mem0 | Apache-2.0 | 两阶段记忆管线中的 update 阶段：新抽取的候选与现有记忆比对后，按 ADD / UPDATE / DELETE / NOOP 四种操作落库 | 本技能步骤 2 冲突消解决策表与步骤 3 四操作执行即源于此；在上游 pack（memory-systems）与本文件中署名 |
| letta (MemGPT) | Apache-2.0 | core memory 的 agent 自编辑模式：agent 改写自己的记忆块时对整块**重写而非追加**，防止上下文膨胀 | 本技能 UPDATE 操作的"重写不追加"原则与 changed_from 演进注记设计即源于此；在上游 pack 与本文件中署名 |

## Distillation boundary (honest disclaimer)

- TTL、使用频率衰减与主题压缩的具体数值（90 天、0.7、×0.8、10 条）为本技能作者给出的经验值，非源自上述项目，可按业务负载调整。
- 审计日志要求、GDPR 式删除权、disputed 标记为本技能作者补充的工程与合规约束，非 mem0 / letta 原文。
- This skill is a methodology distillation; it is not affiliated with the projects above and does not represent their official views.
