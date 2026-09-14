---
name: episode-publisher
description: "Package a rendered podcast episode for publishing: markdown shownotes (summary, guest/links, terminology table), timestamped chapter markers (podcasting 2.0 style), platform metadata (title formulas, episode numbering, cover spec) for Chinese platforms (Xiaoyuzhou/Ximalaya) and Apple Podcasts, plus the AI-content disclosure line. Reads the script and synthesis plan from upstream chain steps. Use when the user asks to 发播客 / shownotes / 章节标记 / 播客发布 / 小宇宙发布 / 节目元数据. Do NOT use for writing the script (podcast-producer), nor for synthesis/voice selection (tts-voice-director)."
license: Apache-2.0
compatibility: Pure prompt-based; no runtime dependencies.
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: audio
  pattern: single-task
  tier: standard
  verified-date: "2026-09-14"
---

# Episode Publisher

链条收口。把合成好的音频打包成**可发布件**：shownotes、章节标记、平台元数据、AI 披露声明。音频好了发布件拉胯 = 白做——小宇宙的转化一半在 shownotes。

## 输入清单

| 输入 | 必需 | 说明 |
|------|------|------|
| 脚本 | ✅ | podcast-producer 产出（有分段结构才能推时间戳） |
| 合成计划/音频 | ✅ | tts-voice-director 产出（段落时长用于章节估算） |
| 平台 | ❌ | 默认小宇宙 + Apple Podcasts 双规格 |

## 工作流

### 步骤 1：写 shownotes（固定结构）

```markdown
## 一句话摘要（≤40 字，钩子式）
## 本期要点（3-5 条，每条一句话）
## 提及资源（链接 + 一句话说明）
## 术语表（脚本里易读错的词 → 正确读音/释义）
## 时间线（见步骤 2）
## 制作说明
- 本期使用 AI 语音合成制作，内容经人工审校。
```

纪律：摘要写"这期让你明白什么"，不写"我们聊了聊"；术语表直接复用 podcast-producer 阶段记录的易错词；**AI 披露是硬要求**——多平台已要求合成内容标注，写死在模板里。

### 步骤 2：生成章节标记（podcasting 2.0 风格）

按脚本分段 + 合成计划里每段的实际时长推时间戳：

```text
00:00 开场
00:35 现象：工具从 3 个涨到 30 个
02:10 反直觉：演示与落地的差距
04:20 怎么做：分段流水线
06:00 收尾与预告
```

格式按 `HH:MM 章节名`；正片开始后的第一章节不早于 00:30（平台规范）。

### 步骤 3：平台元数据

| 字段 | 纪律 |
|------|------|
| 标题 | `[期号] 主题钩子`——期号放前便于排序；钩子 ≤20 字 |
| 副标题/一句话简介 | 与 shownotes 摘要同源，不另写 |
| 封面 | 3000x3000 方图（Apple 规范）；复用 visual-design-studio 链产出 |
| 分类 | 按平台分类表选一级；科技类默认「科技」+「教育」 |

### 步骤 4：交付与链条闭环

交付：shownotes.md + chapters.txt + 各平台元数据卡。**链条到此收口**——"选题 → 脚本 → 合成 → 发布件"四步走完，缺哪步回哪步。

## 失败处置表

| 现象 | 原因 | 处置 |
|------|------|------|
| 章节时间戳对不上 | 用了预估时长没回填实际值 | 合成后按实际音频时长重算一遍 |
| 小宇宙审核不过 | AI 内容未披露 / 封面违规字 | 检查披露行；封面去极限词 |
| shownotes 没人看 | 写成了大纲 | 每条要点带信息量，直接给结论 |
| 期数乱 | 手写期号 | 期号从节目配置读，不手填 |

## 参考

方法论出处与平台披露要求记录在 podcast-producer 的
[sources-and-methodology.md](../podcast-producer/references/sources-and-methodology.md)（同包内共享）。
