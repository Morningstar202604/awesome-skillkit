---
name: shot-recipe-designer
description: "Design a cinematic shot list from recipe cards: each shot gets a purpose, energy level, duration, camera move, and exit transition — 12 proven recipe cards (establishing shot, insert close-up, 2.5D parallax push, title card, match cut, reaction cutaway and more). Use when the user asks to 设计镜头 / 出镜头清单 / shot list / 运镜设计 / 转场设计 / 让片子有电影感 for a promo, short film, or product video. Do NOT use for writing dialogue or narration (use video-script-writer), nor for generating the video itself."
license: Apache-2.0
compatibility: Pure prompt-based design skill; no scripts, no API keys.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: video
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Shot Recipe Designer

用「镜头配方卡」组装镜头清单。每个镜头回答三个问题：**为什么存在（目的）、什么节奏（能量）、多长（时长）**——回答不了任何一个的镜头就该删。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 分镜 / 节拍表 | ✅ | storyboard-designer 的产出，或等价的场景描述 |
| 基调 | ❌ | cinematic / energetic / calm / playful；默认随内容推断 |
| 画幅 | ❌ | 默认 16:9 |

## 工作流

### 步骤 1：为每个节拍选配方

从 [shot-recipes.md](references/shot-recipes.md) 的 12 张卡里选。选卡顺序：先定**钩子镜头**和**收束镜头**（两端定生死），再给中间节拍配展开镜头。

预期：每个节拍恰好 1 张主卡；钩子节拍可叠加 1 张辅助卡。
若失败：某节拍两张卡都想要 → 拆成两个镜头，不要缝合。

### 步骤 2：按卡片公式实例化

每张卡给出参数公式（如视差推动的「前景层位移 1.2×、背景层 0.8×」）。照抄公式，把变量换成用户内容——**确定性优先，不要自由发挥运镜参数**。

### 步骤 3：标注转场链

镜头清单的最后一列填出场转场，规则：
- 同场景内部 → 硬切
- 时间跳跃 → 匹配剪辑（match cut）
- 情绪转换 → 叠化 ≤0.5s
- 全片最多 1 次转场特效（如胶片烧帧），克制是电影感的一部分

### 步骤 4：输出镜头清单

固定表格（列顺序不许变）：

```markdown
| # | 时长 | 配方卡 | 运镜 | 画面一句话 | 声音 | 出场转场 |
|---|------|--------|------|-----------|------|----------|
| 1 | 3s | establishing-wide | 缓推 | 雨夜街景霓虹 | 雨声渐入 | 硬切 |
```

预期：全片时长合计 = 节拍表总时长 ±10%。

## 十二张配方卡（速览，详见 references）

| 卡 | 用途 | 能量 | 时长 |
|----|------|------|------|
| establishing-wide | 开场定调 | 低 | 3-4s |
| hook-pop-in | 前 3 秒钩子 | 高 | 1-2s |
| insert-closeup | 强调细节 | 中 | 1-2s |
| parallax-push | 平面图变立体 | 中 | 3-4s |
| title-card | 标题/章节卡 | 低 | 2-3s |
| match-cut | 时空跳转 | 中 | 2-3s |
| reaction-cutaway | 情绪反应 | 中 | 1-2s |
| process-montage | 流程压缩 | 中高 | 3-5s |
| reveal-pan | 揭示全貌 | 低中 | 3-4s |
| beat-sync-cut | 卡点连切 | 高 | 0.5-1s×N |
| final-frame-hold | 收束定格 | 低 | 2s |
| cta-endcard | 行动号召尾板 | 中 | 2-3s |

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 全片高能镜头连排 | 想炫技 | 强制插入一张低能量卡（title-card / final-frame-hold）做呼吸 |
| 镜头时长合计超时长 | 卡没换算 | 按「时长合计=总时长±10%」重算，先砍中间 beat |
| 卡点切配不上 BGM | 无 BPM 信息 | 问用户要 BGM 或选「BGM 待定」并把 beat-sync-cut 标记为「渲染前定帧率再锁」 |
| 生成模型不支持该运镜 | 方言差异 | 降级为模型可执行的基础运镜（推/拉/固定），卡片参数保留在清单里供后期实现 |

## 交付标准

- 一张镜头清单表，7 列齐全，# 连号
- 每行配方卡名可在 references/shot-recipes.md 中找到原卡
- 时长合计误差 ≤10%

## 参考

- [shot-recipes.md](references/shot-recipes.md) —— 12 张完整配方卡（运镜参数公式 + 常见坑），选卡后必读对应原卡
- [sources-and-methodology.md](references/sources-and-methodology.md) —— 镜头卡片方法论的开源出处与致谢
