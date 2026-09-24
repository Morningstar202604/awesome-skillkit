# Sources & Methodology — memory-architect

本技能的方法论蒸馏自以下三个项目的公开实践，属于**方法论提炼（methodology distilled）**：只借鉴公开文档中描述的设计思想与分层概念，未复制任何源代码。

| Source project | License | What was distilled | Attribution |
|---|---|---|---|
| mem0 | Apache-2.0 | 记忆条目 = 自然语言事实 + 结构化 metadata（user_id、timestamp、run_id），而非裸 embedding；条目化存储与按用户隔离的思想 | 本技能 schema 模板的 user_id / source / confidence 字段设计即源于此；在上游 pack（memory-systems）与本文件中署名 |
| letta (MemGPT) | Apache-2.0 | 分层记忆：core memory（常驻上下文、agent 可自编辑）/ archival memory（持久库、按需检索）/ recall memory（对话历史索引）；memory pressure（上下文压力）概念 | 本技能"步骤 2 分层设计"的三层表与 core 层编辑权限讨论即源于此；在上游 pack 与本文件中署名 |
| Claude memory tool | 参照 Anthropic 官方文档条款 | 文件式记忆：MEMORY.md 索引 + 按主题拆分文件，会话开始载入、结束写回 | 本技能存储选型表中"纯文件"方案与会话收尾写回模式即源于此；在上游 pack 与本文件中署名 |

## Distillation boundary (honest disclaimer)

- This skill is a methodology distillation; it is not affiliated with the projects above and does not represent their official views.
- 三轴存储选型表与具体阈值（2000 条、2000 tokens 等）为本技能作者给出的经验值，非源自上述项目，可按实际负载调整。
- 原项目的具体实现细节（如 mem0 的向量索引参数、letta 的内存页调度）不在本技能范围内。
