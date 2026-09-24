# Sources and Methodology

This skill is self-authored; its methodology skeleton is distilled from the following public materials (structural borrowing only, no text copied):

| Source | Type | What was borrowed | License/attribution |
|------|------|----------|-----------|
| [designskills](https://github.com/ArnavPuri/designskills)（ArnavPuri，MIT） | 开源技能库 | `design-context` 先行模式——品牌/受众/风格上下文作为所有下游技能的共享参数，保证系列一致性 | MIT，结构借鉴并署名 |
| [Anthropic canvas-design](https://github.com/anthropics/skills)（官方） | 🟢 官方 | "视觉哲学先行 → 画布执行"两阶段法；反 AI slop 纪律（极简文字、强视觉主导、杂志级构图） | 官方方法论引用并署名 |
| designskills 全家桶的分工视角 | 开源技能库 | 规格（context）→ 生成（prompt）→ 评估（critique）三段式链条划分 | MIT，结构借鉴并署名 |

## Design decisions

1. **规格单固定 7 字段**：purpose/platform/subject/style/palette/text/do-not——
   字段即可审计单元，比自由散文可验收。
2. **风格锚必须可判定**：吸收 canvas-design 的"哲学先行"，但强制改写为
   3-5 个可判定词——哲学描述给人看，可判定词给模型和审计脚本看。
3. **文字逐条列出并限字数**：图上文字是生成模型第一大翻车源，规格阶段就
   把它锁到最少。

## v2.0 调查来源（2026-09-21，领域暗知识补强）

SKILL.md v2.0 的"领域暗知识"四条均来自以下公开信源（多源交叉验证后引用，
弃用无出处的伪精确统计）：

| 暗知识条目 | 信源 | 采信内容 |
|------|------|----------|
| 1. 层级硬通货（强调一切=什么都没强调） | Robin Williams《The Non-Designer's Design Book》（CRAP 四原则）；IEEE ProComm《Elements of Visual Communication》（Melissa Clarkson）；Gestalt 心理学（Max Wertheimer 以来接近性/相似性/图底等定律）；Affinity Studio 设计博客（三档尺寸、眯眼测试） | CRAP 四原则、层级三档差距、亲密性成组、squint test |
| 2. 强调色稀缺性 | 60-30-10 法则（室内设计起源，Figma 官方资源库《Types of color palettes》收录；多家 UI 配色指南一致引用） | 60/30/10 配比、"最大胆的颜色应最稀有" |
| 3. 文字预算实证 | YouTube 创作者实证共识（0-5 词）；中文平台创作者经验（≤12 字）；WCAG 2.x AA（4.5:1，正文 16px 起）；澳洲政府 Accessibility Toolkit（45-75 字符行宽口径） | 文字上限、移动端缩略可读、对比度底线 |
| 4. 风格锚对竞品信息流 | filmit.io《Teal & Orange Explained》（"2012 成标准、2020 成俗套"演化弧线）；高创收创作者封面框架（feed-level contrast，多家创作者工具指南交叉印证） | 俗套风险、对照系纪律 |

**采信纪律**：只引有明确出处且多源一致的原则；单源精确百分比（如"提升 62%"类）
一律不采信，改用定性表述。

