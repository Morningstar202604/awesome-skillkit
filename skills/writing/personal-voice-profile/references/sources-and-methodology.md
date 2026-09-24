# Sources & Methodology — personal-voice-profile

本技能属于**方法论蒸馏（methodology distilled）**：分析框架来自公开的风格计量与内容风格指南实践，字段设计与置信度约束为本技能作者的工程决策，未复制任何项目的源代码。

## Methodology sources

| Source | License | What was distilled | Attribution |
|---|---|---|---|
| 公开内容风格指南中的 voice 与 tone 区分（如 Mailchimp Content Style Guide 等免费在线指南的通行做法） | 免费公开指南，概念性引用 | 语气层分析框架：区分"人格基调"（voice）与"场景语气"（tone），本技能的 tonal 层按此组织；对读者称呼、感叹词习惯的观察维度亦源于此类指南 | 在本文件与 SKILL.md 语气层步骤中注明 |
| 风格计量学（stylometry）的通行思路：用可数特征刻画写作风格 | 学界通行概念，概念性引用 | 词汇层/句法层的量化口径：高频词、句长中位数与方差、标点频率；句长口径与 ai-trace-auditor 保持一致（有效字符数） | 在本文件声明为概念性借用，未采用其 authorship attribution 结论 |
| 网络写作社区的"作者指纹"讨论（口头禅、结构套路、开头结尾习惯的归纳实践） | 社区公开实践 | 结构层维度（开头/结尾/过渡套路）与 example_snippets 原文样本设计 | 在本文件声明为社区实践归纳 |

## Distillation boundary (honest disclaimer)

- 样本量下限（≥3 篇）与"每条结论必须附原文证据"的规则为本技能作者的工程约束，非源自上述来源； stylometry 领域对"最小样本量"并无与本场景直接对应的结论。
- 本技能只做**描述性画像**，不做作者身份鉴定（authorship identification）；不能用于判断某文本"是不是某人写的"——这一边界与红线 2、红线 3 配套。
- JSON 字段结构（lexical/syntactic/tonal/structural/example_snippets）为本技能自定义规格，与任何外部产品无兼容关系。
- 本技能为方法论蒸馏产物，与上述指南及社区无隶属关系，不代表其原作者观点。
