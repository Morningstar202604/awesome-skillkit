# 来源与方法论 / Sources and Methodology

本技能为 self-authored，方法论骨架提炼自以下公开材料（结构借鉴，无文本复制）：

| 来源 | 类型 | 借鉴内容 | 许可/署名 |
|------|------|----------|-----------|
| AIDA / PAS / FAB 直复营销框架（行业公版方法论） | 公版 | 框架选型表：受众决策阶段 ↔ 框架匹配 | 经典框架，无需授权 |
| [reef-copywriting](https://fast.io/resources/best-openclaw-skills-ai-product-description-ecommerce-copywriting)（OpenClaw 生态实测） | 🟡 第三方 | benefit-first 标题纪律；PAS 的"问题-激化-解决"用于痛点未觉醒受众；多内容类型（详情页/口播/海报）一套方法论 | 结构借鉴并署名 |
| [Copywriting（openclaw/skills 官方）](https://fast.io/resources/best-openclaw-skills-ai-product-description-ecommerce-copywriting) | 🟡 官方技能 | FAB 把技术规格翻译成客户利益的纪律；headline 公式；CTA 变体；**异议处理**（objection handling）独立成段 | 结构借鉴并署名 |
| [commerce-copywriting（modu-ai）](https://skills.rest/skill/commerce-copywriting) | 开源技能 | 渠道特定变体 + A/B 测试变体自动生成 + 上线前 AI 审查的流水线分工 | MIT 生态，结构借鉴并署名 |
| 中国广告法极限词纪律 | 法规 | "最/第一/国家级"禁用与可比较表述改写 | 合规要求，非借鉴 |

## 设计决策

1. **框架先行**：三框架选型表按"受众决策阶段"分流，比开源技能的"多框架并列"
   更可执行——先回答"受众卡在哪"再选枪。
2. **异议处理独立成段**：openclaw 官方技能的可取之处，实测中它是转化率与
   详情页停留时长的最大杠杆，值得强制。
3. **事实卫生前置**：与仓库"审计文化"同源——输入不干净（无事实）时拒绝动笔，
   而不是生成后清理。
