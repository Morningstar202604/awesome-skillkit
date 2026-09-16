# Sources & Methodology — memory-retriever

本技能的方法论蒸馏自 mem0 与 letta (MemGPT) 的公开实践，属于**方法论提炼（methodology distilled）**：只借鉴公开文档中描述的检索思想与注入模式，未复制任何源代码。

| 来源项目 | 许可 | 蒸馏了什么 | 署名方式 |
|---|---|---|---|
| mem0 | Apache-2.0 | 记忆检索以结构化条目（自然语言事实 + metadata）为单位返回，而非裸 embedding 片段；条目级置信度与来源可追溯 | 本技能注入块的 source/时间戳要素与 confidence 标注线即源于此；在上游 pack（memory-systems）与本文件中署名 |
| letta (MemGPT) | Apache-2.0 | 分层检索与上下文压力管理：按需从 archival 层检索注入，控制注入量以给工作记忆留空间；对话历史（recall）与知识记忆分离 | 本技能 token 预算硬截断与"记忆块边界标记"的设计即源于此；在上游 pack 与本文件中署名 |

## 蒸馏边界（诚实声明）

- hybrid retrieval 的融合公式与权重（0.4 semantic / 0.3 keyword / 0.2 recency / 0.1 confidence）、top-K、相关性下限均为本技能作者给出的经验值，非源自上述项目，可按业务校准。
- BM25 与向量召回为业界通用检索技术，不属于任何单一项目的专有方法论。
- 查询改写与指代消解为本技能作者补充的工程实践；keyword_only 降级路径为本技能作者设计的无向量库方案。
- 本技能为方法论蒸馏产物，与上述项目无隶属关系，不代表其官方观点。
