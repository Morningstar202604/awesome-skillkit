# 来源与方法论 / Sources and Methodology

本技能为 self-authored，方法论骨架提炼自以下公开材料（结构借鉴，无文本复制）：

| 来源 | 类型 | 借鉴内容 | 许可/署名 |
|------|------|----------|-----------|
| [designskills](https://github.com/ArnavPuri/designskills)（ArnavPuri，MIT） | 开源技能库 | `design-context` 先行模式——品牌/受众/风格上下文作为所有下游技能的共享参数，保证系列一致性 | MIT，结构借鉴并署名 |
| [Anthropic canvas-design](https://github.com/anthropics/skills)（官方） | 🟢 官方 | "视觉哲学先行 → 画布执行"两阶段法；反 AI slop 纪律（极简文字、强视觉主导、杂志级构图） | 官方方法论引用并署名 |
| designskills 全家桶的分工视角 | 开源技能库 | 规格（context）→ 生成（prompt）→ 评估（critique）三段式链条划分 | MIT，结构借鉴并署名 |

## 设计决策

1. **规格单固定 7 字段**：purpose/platform/subject/style/palette/text/do-not——
   字段即可审计单元，比自由散文可验收。
2. **风格锚必须可判定**：吸收 canvas-design 的"哲学先行"，但强制改写为
   3-5 个可判定词——哲学描述给人看，可判定词给模型和审计脚本看。
3. **文字逐条列出并限字数**：图上文字是生成模型第一大翻车源，规格阶段就
   把它锁到最少。
