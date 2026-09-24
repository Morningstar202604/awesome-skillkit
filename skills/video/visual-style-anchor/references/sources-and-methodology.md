# Methodology sources and acknowledgements

## Main sources

| Source | License | Methodology points borrowed |
|------|--------|------------------|
| [agentara/skills — video-storyboard](https://github.com/agentara/skills) | 见其仓库 | 角色身份约束（identity constraints）与角色设定资产（character sheet / turnaround / casting reference）作为生成前置输入的纪律 |
| 本仓 ai-baby-podcast（viral-entertainment 包）| Apache-2.0（本仓原创）| 角色卡七件套、锁定 seed/音色、每 10 条漂移审计、**永不从文字重生角色**（只许从已定稿参考图延伸）的实践，来自该技能已验证的 references/character-consistency.md，此处通用化 |
| 社区共识 | — | 「identity line 复制粘贴禁改写」「否定句禁用」「禁改清单」为多开源项目交叉验证的公共做法 |

## 通用化说明

本技能把 ai-baby-podcast 中「单一萌物角色」的专属纪律抽象为任意角色的通用
手册：去除了宝宝/萌物特定的形象公式，保留「描述固定、参考先行、漂移审计、
变体机制」四层骨架，并补充了声音一致性维度。

## v2.0 调查来源（2026-09-21，领域暗知识补强）

SKILL.md v2.0 的"领域暗知识"四条均来自以下公开信源（多源交叉验证后引用，
弃用无出处的伪精确统计）：

| 暗知识条目 | 信源 | 采信内容 |
|------|------|----------|
| 1. 青橙对比的物理机制与俗套化 | filmit.io《Teal & Orange Explained: Why Every Hollywood Movie Looks the Same》；Creative Comment《Beyond the Teal》；中文调色解析（色代码表博客）多源一致 | 肤色全人种落橙色区间、青为互补色造纵深；2007 工业化（数字摄影机 + Resolve LUT），2012 成标准，2020 成俗套；区分度来自题材与光线结构 |
| 2. 先校正后创作、留余量 | 调色师实操指南多源一致（weddingfilmphotography 调色指南、Airframe Media 调色教程） | 校正→匹配→创意三段序；LUT 透明度 50-70%（30-80% 区间口径）；只推暗部不动中间调；肤色饱和度设上限；"往肤色里推绿或品红会读作病态/做作"（weddingfilmphotography） |
| 3. 色彩温度字典 | 调色叙事通用词典（多源一致）；经典片例（《黑客帝国》单色绿、《月光男孩》邻近霓虹、《布达佩斯大饭店》粉彩） | 暖=怀旧/亲密，冷=距离/紧张；高饱和+黑场上浮=商业感，低饱和+压实黑场=电影感 |
| 4. 一致性比漂亮值钱 | 调色师共识（"跨镜头肤色不一致立刻露 amateur 底"）与角色一致性纪律同构 | 锚是合同不是参考；原样引用禁改写 |
| 5. 强调色稀缺性（SKILL.md 红线 5） | 60-30-10 法则（室内设计起源，Figma 官方资源库《Types of color palettes》收录） | 强调色唯一、只给焦点对象 |

**采信纪律**：只引有明确出处且多源一致的原则；单源精确百分比一律不采信，
改用定性表述。

