# Video Production Team - 视频创作专家团

> 场景：从一条 brief 到交付一条节奏对、音画齐、合规可发布的成片——覆盖短视频/口播访谈/纪录片/动画/广告的全流程制作。

## 团队定位
- **输入**：视频 brief（目标平台、受众、时长、风格、必含信息点）、已有素材
- **输出**：过质检闸门、符合平台规格、音画同步、字幕合规可发布的成片 + 制作交接文档
- **核心价值**：14 人串行闭环、主理人全程把关风格统一与一致性、发布前必过质检闸门

## 成员架构（14 人）

| 角色 | Agent ID | 核心职责 | 典型触发 |
|------|----------|----------|----------|
| 制作总监 | `video-team-lead` | 片型判定、全流程编排、风格统一、终审、复盘 | 所有视频制作需求入口 |
| 编剧导演 | `video-scriptwriter-director` | 整体构思、脚本、导演意图、叙事弧线 | "写脚本"、"怎么构思" |
| 分镜师 | `video-storyboard-artist` | 分镜表、景别运镜、镜头语言、时长预估 | "画分镜"、"镜头怎么拍" |
| 短视频专家 | `video-short-form-expert` | 竖屏短视频/信息流钩子、完播结构、平台规格 | "做短视频"、"信息流广告" |
| 口播纪录片专家 | `video-interview-documentary-expert` | 口播稿、访谈提纲、纪录片结构、真实感 | "口播稿"、"访谈/纪录片怎么剪" |
| 动画动态设计 | `video-animation-motion-designer` | 二维/逐帧动画、MG 动态原型、动效节奏 | "做动画"、"动态设计" |
| 剪辑师 | `video-editor` | 粗剪精剪、节奏、转场、音画同步 | "怎么剪"、"节奏不对" |
| 动效包装 | `video-motion-graphics-designer` | 片头片尾、动效包装、字幕条、品牌模板 | "做包装"、"片头" |
| 音频设计 | `video-audio-designer` | 配乐、音效、人声处理、混音响度 | "配乐"、"人声不清楚" |
| 字幕专家 | `video-caption-subtitle-expert` | 字幕、双语、错别字、敏感词合规 | "加字幕"、"双语字幕" |
| 调色师 | `video-color-grader` | 一级校色、风格调色、肤色曝光统一 | "调色"、"风格化" |
| 特效合成 | `video-vfx-expert` | 抠像、跟踪、特效合成、画面修复 | "绿幕抠像"、"特效合成" |
| 数据复盘（只读） | `video-performance-analyst` | 完播/留存/互动数据复盘、优化建议 | "数据复盘"、"为什么没人看完" |
| 成片质检（只读） | `video-quality-reviewer` | 技术规格、音画质量、合规终检 | "成片质检"、"能发了吗" |

## Workflow 对照

| Workflow | 触发场景 | 执行流程 |
|----------|----------|----------|
| **W1 完整制作** | "给条 brief，全程托管出片" | Phase 0(lead+scriptwriter，按片型并行 short-form/interview)→1(storyboard)→2(制作/动画)→3(editor)→4(motion-graphics)→5(audio)→6(caption)→7(color+vfx)→8(quality-reviewer+performance-analyst 并行) |
| **W2 短视频快产** | "只要一条竖屏短视频，要快" | Phase 0(lead+short-form+scriptwriter 短脚本)→1(精简分镜)→3(快剪)→5(audio)→6(caption)→8(快检)，跳过非必要包装/调色 |
| **W3 质检复盘** | "已有成片，要质检/看数据" | quality-reviewer(只读)质检 →（有数据）performance-analyst(只读)复盘 → lead 汇总修改优先级 |

## 关键准则（全团必守）
- 前 3 秒定生死：开场必须有钩子，不铺垫空镜
- 节奏服务信息：有快慢呼吸，不匀速拖长
- 音画同呼吸：切点卡动作/停顿/重音，人声永远听得清
- 合规零容忍：敏感词、绝对化用语、未授权音乐发布前必扫
- 质检闸门：H 级问题（规格不符/音画错位/信息缺失/违规）一票否决

## 协作机制
- **技能调用协议**：每 Phase 前必扫 `skills/`，命中即用、严格按其执行
- **交接模板**：4 块（产出/决策/风险/重点），缺一不可
- **思想纪律**：忠于 brief、不绕圈、出错即停（2-3 轮无解即回传复核）
- **自检闸门**：开工前 + 产出后逐项过相关 skill 清单，任一不过即停
- **一致性终审**：脚本—分镜—剪辑—包装—音频—字幕—调色首尾咬合，主理人总控

## 技能依赖
团队专用 skills 目录：`teams/video-production-team/skills/`
核心 skills：`video-script-template`（脚本骨架）、`storyboard-guide`（分镜）、`short-video-structure-guide`（短视频结构）、`video-editing-guide`（剪辑）、`caption-and-subtitle-guide`（字幕）、`video-quality-checklist`（成片质检）。

> **协作接口**：可对接 content（脚本/口播文案/选题）、visual（封面/分镜视觉/字幕版式）；典型跨场景触发词：抖音视频、短视频带货、宣传片+文案、视频+封面设计。

## 入口调用
> Agent ID 为相对 agents 目录的路径（平台中立标识符）；在支持子 agent 调度的框架中按路径 ID 派发，团队成员由 Team-lead 内部编排，不作短名直调。
```text
# 完整视频制作托管（Team-lead 为入口）
teams/video-production-team/agents/video-team-lead "帮我从这条 brief 全程做一条短视频"

# 单点成员由 Team-lead 内部按 Workflow 派发（或在支持子 agent 的框架中按路径 ID 直派）
# teams/video-production-team/agents/video-scriptwriter-director "帮我写这条片子的脚本"
# teams/video-production-team/agents/video-storyboard-artist "把脚本画成分镜表"
# teams/video-production-team/agents/video-short-form-expert "这条竖屏短视频前3秒钩子怎么做"
# teams/video-production-team/agents/video-interview-documentary-expert "帮我写口播稿/访谈提纲"
# teams/video-production-team/agents/video-animation-motion-designer "做这个 MG 动态设计"
# teams/video-production-team/agents/video-editor "这段素材怎么剪节奏才对"
# teams/video-production-team/agents/video-motion-graphics-designer "做个片头和包装"
# teams/video-production-team/agents/video-audio-designer "配个乐并把人声处理清楚"
# teams/video-production-team/agents/video-caption-subtitle-expert "上字幕并查敏感词"
# teams/video-production-team/agents/video-color-grader "统一全片色调做风格调色"
# teams/video-production-team/agents/video-vfx-expert "绿幕抠像+背景合成"
# teams/video-production-team/agents/video-performance-analyst "分析这条的完播率找掉留点"
# teams/video-production-team/agents/video-quality-reviewer "成片发布前做终检"
```
