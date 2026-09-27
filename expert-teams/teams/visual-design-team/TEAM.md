# Visual Design Team - 视觉设计专家团

> 场景：商业视觉设计全程托管——从设计需求简报拆解、风格定调、各品类设计产出到只读评审质检与落地交付。

## 团队定位
- **输入**：设计需求（用途/受众/尺寸/文案/品牌规范/参考素材）
- **输出**：风格统一、可商用、可落地（出血/分辨率/版权达标）的视觉设计方案 + 导出规格
- **核心价值**：14 人串行闭环、主理人全程把关风格一致性与版权合规

## 成员架构（14 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 设计总监 | `visual-team-lead` | 简报拆解、风格定调、品类路由、版权与一致性终审 | 所有视觉设计需求入口 |
| 品牌 VI 设计师 | `visual-brand-identity-designer` | 品牌/VI 体系、色彩字体系统、品牌手册 | "做品牌VI"、"品牌视觉规范" |
| 海报 KV 设计师 | `visual-poster-designer` | 海报/主视觉 KV/活动画面/大屏 | "做海报"、"主视觉"、"KV" |
| 插画师 | `visual-illustrator` | 插画/漫画/扁平风/角色场景 | "画插画"、"条漫"、"扁平配图" |
| 电商视觉设计师 | `visual-ecommerce-designer` | 主图/详情页/长图/活动页 | "电商主图"、"详情页"、"卖点图" |
| 社媒配图设计师 | `visual-social-media-designer` | 小红书/公众号封面/信息流 | "小红书封面"、"公众号头图" |
| 信息图设计师 | `visual-infographic-designer` | 信息图/数据可视化/流程图解 | "做信息图"、"数据可视化" |
| 字体排版专家 | `visual-typography-expert` | 字体/字号层级/版式网格 | "选什么字体"、"排版怎么排" |
| 色彩理论专家 | `visual-color-theory-expert` | 配色策略/品牌色/对比度 | "怎么配色"、"主色选什么" |
| Logo 设计师 | `visual-logo-designer` | Logo/标识/图标/安全区 | "做Logo"、"标识"、"图标" |
| 演示设计师 | `visual-presentation-designer` | PPT/Keynote/母版/图表美化 | "做PPT"、"幻灯片视觉" |
| 印刷物料设计师 | `visual-print-designer` | 印刷/包装/画册/线下落地 | "做名片"、"包装"、"印刷物料" |
| 设计评审质检员 | `visual-design-reviewer` | 只读评审/风格/版权/参数终检 | "挑毛病"、"交付前质检" |
| 素材管理管家 | `visual-asset-manager` | 素材版权/规格处理/归档打包 | "素材版权"、"整理素材" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 完整全案** | "要整套视觉/品牌活动视觉托管" | Phase 0(lead 简报拆解 + color/typography **并行**咨询)→1(品类设计师)→2(asset-manager)→3(reviewer 只读质检)→4(lead 汇编交付) |
| **W2 单品类设计** | "只要一张海报/一套主图/一篇社媒图" | lead 快拆 brief → 直达对应品类设计师 → 自检交付（要求高时追加 reviewer） |
| **W3 评审质检** | "已有稿子要挑错/交付前把关" | 直达 `visual-design-reviewer`（只读）→ 版权/规格问题转 `visual-asset-manager` |

## 关键差异（屏幕 vs 印刷）
- 屏幕件用 RGB、社媒/网页尺寸、安全区避让 UI
- 印刷件用 CMYK、出血 ≥3mm、分辨率 ≥300dpi、刀模与工艺
- 字体全程确认授权，素材全程确认可商用

## 协作机制
- **技能调用协议**：每 Phase 前必扫 `skills/`，命中即用、严格按其执行
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可
- **思想纪律**：忠于 brief、不绕圈、出错即停（2-3 轮对不上即回传复核）
- **自检闸门**：对应品类清单（电商自查/评审清单）开工前/产出后必过，任一不过即停
- **一致性终审**：配色/字体/版式跨物料必须首尾一致
- **版权零容忍**：全程禁止扒网图、未授权字体，素材必须可商用

## 技能依赖
团队专用 skills 目录：`teams/visual-design-team/skills/`
核心 skills：`design-brief-writer`（简报拆解）、`color-and-typography-guide`（配色字体速查）、`poster-and-key-visual-templates`（海报版式库）、`ecommerce-visual-checklist`（电商自查）、`image-generation-prompt-guide`（生图提示词）、`design-review-checklist`（评审清单）。

> **协作接口**：可对接 content（图文/小红书/公众号配图）、video（视频封面/分镜视觉/字幕版式）、fullstack（产品页/UI设计）、academic（论文图表）；典型跨场景触发词：小红书图文、视频封面、产品UI、论文配图。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 完整视觉全案托管（Team-lead 为入口）
teams/visual-design-team/agents/visual-team-lead "帮我全程托管这套活动视觉"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/visual-design-team/agents/visual-brand-identity-designer "帮我做品牌VI体系"
# teams/visual-design-team/agents/visual-poster-designer "帮我做活动主视觉海报"
# teams/visual-design-team/agents/visual-illustrator "帮我画一套扁平插画"
# teams/visual-design-team/agents/visual-ecommerce-designer "帮我做主图和详情页"
# teams/visual-design-team/agents/visual-social-media-designer "帮我做小红书封面"
# teams/visual-design-team/agents/visual-infographic-designer "帮我把数据做成信息图"
# teams/visual-design-team/agents/visual-typography-expert "这套版面字体怎么排"
# teams/visual-design-team/agents/visual-color-theory-expert "帮我定品牌配色"
# teams/visual-design-team/agents/visual-logo-designer "帮我设计Logo"
# teams/visual-design-team/agents/visual-presentation-designer "帮我美化这套PPT"
# teams/visual-design-team/agents/visual-print-designer "帮我做包装印刷稿"
# teams/visual-design-team/agents/visual-design-reviewer "交付前帮我质检这稿"
# teams/visual-design-team/agents/visual-asset-manager "核对素材版权并整理交付包"
```
