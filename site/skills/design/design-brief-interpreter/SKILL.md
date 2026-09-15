---
name: design-brief-interpreter
description: "Interpret a vague visual design request into a machine-checkable design spec: purpose, audience, platform + exact canvas size/ratio, composition, style anchor, color palette, text hierarchy, and text budget. This is the entry skill of the visual-design-studio chain — its output feeds image-prompt-engineer directly, and layout-spec-auditor verifies the final image against it. Use when the user asks to 做图 / 设计封面 / 海报 / 信息图 / 配图 / cover / poster / infographic / thumbnail / banner. Do NOT use for video frame prompts (video-prompt-engineer owns motion), nor for UI code generation."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: design
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Design Brief Interpreter

链条入口。把一句模糊的"帮我做张图"翻译成**设计规格单**——后面每个环节（prompt 工程、规格审计）都引用这份规格。没有规格单的生图就是抽卡：平台尺寸错一次重做一次，文字层级乱一次重做一次。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 粗需求 | ✅ | 用户原话："公众号需要一张讲 AI 视频的封面" |
| 平台/用途 | ✅（缺就问） | 决定画布尺寸与构图方向，不猜 |
| 品牌上下文 | ❌ | 有品牌色/字体/调性就记录，没有则给建议 |

## 工作流

### 步骤 1：三问定盘子（缺一就反问，不许编）

1. **给谁看、在哪看**——平台决定画布（公众号头图 2.35:1、小红书 3:4、B 站封面 16:9…）
2. **第一眼传达什么**——一句话主题，超出一句就是两张图的活
3. **文字要出现哪些**——标题/副题/署名逐条列出；图上的每个字都是翻车点，能砍则砍

### 步骤 2：产出规格单（固定 7 字段）

```markdown
## Design Spec
- purpose:    一句话用途与受众
- platform:   平台名 + 画布 W×H + 比例
- subject:    画面主体（写"画什么"，不写"表达什么"）
- style:      风格锚（3-5 个可判定的词：媒介质感 + 色彩情绪 + 构图法）
- palette:    主色 + 辅色 + 强调色（给色名/色值，不给"高级感"）
- text:       逐条列出图上文字（层级 + 字数上限）；无文字写 none
- do-not:     反向约束（不要什么元素/风格）
```

**风格锚纪律**（借鉴 Anthropic canvas-design 的"视觉哲学先行"）：先定 3-5 个可判定词再进 prompt——"杂志级极简、大留白、单一强调色"可审计，"好看、高级"不可审计。同系列物料必须复用同一风格锚，这是系列一致性的唯一锚点。

### 步骤 3：移交下游

- 直接说："规格单已就绪，继续调用 image-prompt-engineer 写 prompt，产出图后用 layout-spec-auditor 按本规格审计"——**链条自动展开，用户不需要再下指令**。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 用户说"随便设计一下" | 三问信息为零 | 给 2 个预设方向让用户选，不接受"随便" |
| 主题超过一句话 | 一次想做两张图 | 拆成多张规格单，各自走链 |
| 图上文字超过 12 字 | 想把文章塞进图 | 图文字只留钩子，正文回文章 |
| 品牌色说不清 | "蓝色那种" | 给 2-3 组具体色值让用户挑 |

## 参考

- [sources-and-methodology.md](references/sources-and-methodology.md) —— 方法论开源出处（design-context / canvas-design）
